#!/usr/bin/env python3
"""
Convert collected Goethe vocabulary into trainer knowledge graph format.

Takes the output from collect_goethe.py (vocabulary_a1.json, vocabulary_a2.json)
and generates/updates the trainer's data/levels/*.json files.

Usage:
  python3 convert_to_trainer.py --level a1 --dry-run     # Preview without writing
  python3 convert_to_trainer.py --level a1                # Update a1.json vocab topics
  python3 convert_to_trainer.py --level a2                # Update a2.json vocab topics
  python3 convert_to_trainer.py --compare a1              # Compare collected vs current

This script ONLY updates vocabulary topics (not grammar). Grammar topics require
manual/LLM curation since they involve conjugation patterns, rules, etc.
"""

import argparse
import json
import re
import sys
from pathlib import Path

COLLECTOR_OUTPUT = Path(__file__).parent / "output"
TRAINER_DATA = Path(__file__).parent.parent / "trainer" / "data" / "levels"

# Mapping from Goethe thematic categories to our topic IDs
# These are approximate — the collector doesn't always have clean categories
VOCAB_TOPIC_MAPPING_A1 = {
    "a1-vocab-greetings": [
        "hallo", "tschüss", "guten morgen", "guten tag", "guten abend",
        "auf wiedersehen", "bitte", "danke", "entschuldigung", "ja", "nein",
        "wie geht", "willkommen",
    ],
    "a1-vocab-family": [
        "mutter", "vater", "bruder", "schwester", "kind", "sohn", "tochter",
        "großmutter", "großvater", "eltern", "familie", "tante", "onkel",
        "mann", "frau",
    ],
    "a1-vocab-food": [
        "brot", "käse", "milch", "kaffee", "tee", "wasser", "bier", "wein",
        "apfel", "ei", "fleisch", "reis", "suppe", "kuchen", "zucker", "salz",
        "obst", "gemüse", "kartoffel", "tomate", "butter",
    ],
    "a1-vocab-home": [
        "küche", "wohnzimmer", "schlafzimmer", "badezimmer", "tisch", "stuhl",
        "bett", "sofa", "fenster", "tür", "lampe", "schrank", "wohnung", "haus",
        "zimmer", "garten",
    ],
    "a1-vocab-travel": [
        "auto", "bus", "zug", "flugzeug", "fahrrad", "straße", "bahnhof",
        "flughafen", "ticket", "fahrkarte", "haltestelle",
    ],
    "a1-vocab-professions": [
        "arzt", "ärztin", "lehrer", "lehrerin", "student", "koch", "ingenieur",
        "polizist", "verkäufer", "sekretär",
    ],
}

VOCAB_TOPIC_MAPPING_A2 = {
    "a2-vocab-health": [
        "kopf", "arm", "bein", "hand", "auge", "ohr", "nase", "mund",
        "krank", "gesund", "schmerz", "fieber", "arzt", "apotheke",
        "krankenhaus", "medikament",
    ],
    "a2-vocab-clothing": [
        "hemd", "hose", "kleid", "rock", "jacke", "mantel", "schuh",
        "socke", "mütze", "handschuh", "tasche",
    ],
    "a2-vocab-work": [
        "büro", "chef", "kollege", "firma", "gehalt", "bewerbung",
        "termin", "besprechung", "projekt", "arbeit",
    ],
}


def load_collected(level):
    """Load collected vocabulary for a level."""
    path = COLLECTOR_OUTPUT / f"vocabulary_{level}.json"
    if not path.exists():
        print(f"ERROR: {path} not found. Run collect_goethe.py first.")
        sys.exit(1)
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_trainer_data(level):
    """Load current trainer knowledge graph."""
    path = TRAINER_DATA / f"{level}.json"
    if not path.exists():
        print(f"ERROR: {path} not found.")
        sys.exit(1)
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def find_matching_topic(word, topic_mapping):
    """Find which topic a word belongs to based on keyword matching."""
    word_lower = re.sub(r"^(der|die|das|ein|eine)\s+", "", word.lower())
    for topic_id, keywords in topic_mapping.items():
        for kw in keywords:
            if kw in word_lower or word_lower in kw:
                return topic_id
    return None


def compare_collected_vs_current(level):
    """Compare collected Goethe data against current trainer content."""
    collected = load_collected(level)
    trainer = load_trainer_data(level)

    # Get all current vocab KP german words
    current_words = set()
    for domain in trainer["domains"]:
        if domain["id"] != "vocabulary":
            continue
        for topic in domain["topics"]:
            for kp in topic["knowledge_points"]:
                pd = kp["prompt_data"]
                german = pd.get("german", "").lower()
                current_words.add(german)
                # Also add without article
                bare = re.sub(r"^(der|die|das|ein|eine)\s+", "", german)
                current_words.add(bare)

    # Collected words with translations
    collected_with_english = [e for e in collected if e.get("english")]

    # Find words in collected but not in trainer
    missing = []
    for entry in collected_with_english:
        german = entry["german"].lower()
        bare = re.sub(r"^(der|die|das|ein|eine)\s+", "", german)
        if german not in current_words and bare not in current_words:
            missing.append(entry)

    print(f"\n--- {level.upper()} Comparison ---")
    print(f"  Collected entries (total): {len(collected)}")
    print(f"  Collected with English: {len(collected_with_english)}")
    print(f"  Current trainer vocab words: {len(current_words)}")
    print(f"  Missing from trainer: {len(missing)}")

    if missing:
        print(f"\n  Sample missing words (first 30):")
        for entry in missing[:30]:
            print(f"    {entry['german']:30s} — {entry.get('english', '?')}")

    return missing


def enrich_topic_kps(topic, collected_entries, level):
    """Add new KPs to a topic from collected entries."""
    existing_ids = {kp["id"] for kp in topic["knowledge_points"]}
    existing_words = set()
    for kp in topic["knowledge_points"]:
        german = kp["prompt_data"].get("german", "").lower()
        existing_words.add(german)
        bare = re.sub(r"^(der|die|das|ein|eine)\s+", "", german)
        existing_words.add(bare)

    added = 0
    for entry in collected_entries:
        german = entry["german"].lower()
        bare = re.sub(r"^(der|die|das|ein|eine)\s+", "", german)
        if german in existing_words or bare in existing_words:
            continue

        # Generate KP
        kp_id = f"{level}-vocab-{topic['id'].split('-')[-1]}-kp-{_slug(bare)}"
        if kp_id in existing_ids:
            continue

        prompt_data = {
            "type": "vocabulary",
            "german": entry["german"],
            "english": entry.get("english", ""),
        }
        if entry.get("article"):
            prompt_data["article"] = entry["article"]
            prompt_data["gender"] = entry.get("gender", "")
        if entry.get("plural"):
            prompt_data["plural"] = entry["plural"]
        prompt_data["example_sentence"] = ""  # Needs manual/LLM filling

        topic["knowledge_points"].append({
            "id": kp_id,
            "prompt_data": prompt_data,
            "explanation": f"From Goethe {level.upper()} word list.",
        })
        existing_ids.add(kp_id)
        existing_words.add(german)
        added += 1

    return added


def _slug(text):
    """Create a URL-safe slug from text."""
    return re.sub(r"[^a-z0-9]", "-", text.lower()).strip("-")[:30]


def main():
    parser = argparse.ArgumentParser(description="Convert collected Goethe data to trainer format")
    parser.add_argument("--level", choices=["a1", "a2"], required=True)
    parser.add_argument("--compare", action="store_true", help="Compare collected vs current (no changes)")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without writing")

    args = parser.parse_args()

    if args.compare:
        compare_collected_vs_current(args.level)
        return

    # Load data
    collected = load_collected(args.level)
    topic_mapping = VOCAB_TOPIC_MAPPING_A1 if args.level == "a1" else VOCAB_TOPIC_MAPPING_A2
    trainer = load_trainer_data(args.level)

    # Categorize collected entries by topic
    categorized = {}
    uncategorized = []
    for entry in collected:
        if not entry.get("english"):
            continue
        topic_id = find_matching_topic(entry["german"], topic_mapping)
        if topic_id:
            categorized.setdefault(topic_id, []).append(entry)
        else:
            uncategorized.append(entry)

    print(f"\nCategorized {sum(len(v) for v in categorized.values())} entries across {len(categorized)} topics")
    print(f"Uncategorized: {len(uncategorized)} entries")

    # Enrich each matching topic
    total_added = 0
    for domain in trainer["domains"]:
        if domain["id"] != "vocabulary":
            continue
        for topic in domain["topics"]:
            entries = categorized.get(topic["id"], [])
            if entries:
                added = enrich_topic_kps(topic, entries, args.level)
                if added:
                    print(f"  {topic['name']}: +{added} KPs")
                    total_added += added

    print(f"\nTotal new KPs added: {total_added}")

    if args.dry_run:
        print("\n[dry-run] No files written.")
        return

    if total_added > 0:
        out_path = TRAINER_DATA / f"{args.level}.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(trainer, f, indent=2, ensure_ascii=False)
        print(f"\n[written] {out_path}")
    else:
        print("\nNo new entries to add.")


if __name__ == "__main__":
    main()
