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
        "wie geht", "willkommen", "grüß", "servus", "herzlich", "freut mich",
        "gute nacht",
    ],
    "a1-vocab-numbers": [
        "nummer", "zahl", "null", "eins", "zwei", "drei", "vier", "fünf",
        "sechs", "sieben", "acht", "neun", "zehn", "elf", "zwölf", "dreizehn",
        "vierzehn", "fünfzehn", "sechzehn", "siebzehn", "achtzehn", "neunzehn",
        "zwanzig", "dreißig", "vierzig", "fünfzig", "sechzig", "siebzig",
        "achtzig", "neunzig", "hundert", "tausend", "million", "postleitzahl",
        "hausnummer",
    ],
    "a1-vocab-family": [
        "mutter", "vater", "bruder", "schwester", "kind", "sohn", "tochter",
        "großmutter", "großvater", "eltern", "familie", "tante", "onkel",
        "mann", "frau", "oma", "opa", "baby", "geschwister", "cousin",
        "kusine", "neffe", "nichte", "enkel", "ehemann", "ehefrau",
        "schwiegermutter", "schwiegervater",
    ],
    "a1-vocab-food": [
        "brot", "käse", "milch", "kaffee", "tee", "wasser", "bier", "wein",
        "apfel", "ei", "fleisch", "reis", "suppe", "kuchen", "zucker", "salz",
        "obst", "gemüse", "kartoffel", "tomate", "butter", "fisch", "hähnchen",
        "nudel", "pizza", "schokolade", "marmelade", "joghurt", "saft",
        "limonade", "hunger", "durst", "restaurant", "speisekarte", "getränk",
        "gabel", "löffel", "teller", "tasse",
    ],
    "a1-vocab-daily-routines": [
        "aufstehen", "schlafen", "duschen", "waschen", "kochen", "aufräumen",
        "putzen", "anziehen", "ausziehen", "frühstücken", "arbeiten",
        "fernsehen", "spazieren", "einkaufen", "anfangen", "aufhören",
        "beginnen", "aufwachen", "einschlafen", "zähneputzen",
    ],
    "a1-vocab-home": [
        "küche", "wohnzimmer", "schlafzimmer", "badezimmer", "tisch", "stuhl",
        "bett", "sofa", "fenster", "tür", "lampe", "schrank", "wohnung", "haus",
        "zimmer", "garten", "balkon", "flur", "keller", "dach", "treppe",
        "garage", "toilette", "dusche", "spiegel", "regal", "teppich",
        "vorhang", "kühlschrank", "herd", "waschmaschine", "möbel", "sessel",
        "schlüssel", "etage", "stockwerk", "miete",
    ],
    "a1-vocab-travel": [
        "auto", "bus", "zug", "flugzeug", "fahrrad", "straße", "bahnhof",
        "flughafen", "ticket", "fahrkarte", "haltestelle", "abfahrt",
        "ankunft", "verspätung", "umsteigen", "gleis", "taxi", "reise",
        "koffer", "gepäck", "pass", "visum", "hotel", "rezeption",
        "abfahren", "ankommen", "fliegen", "fahren", "reisen",
    ],
    "a1-vocab-hobbies": [
        "sport", "musik", "spiel", "kino", "schwimm", "fußball", "tanz",
        "film", "buch", "lesen", "singen", "malen", "foto", "garten",
        "wandern", "rad", "joggen", "yoga", "kochen", "gitarre", "klavier",
        "konzert", "theater", "museum", "hobby", "freizeit", "beispiel",
        "buchstabe", "buchstabieren",
    ],
    "a1-vocab-colors": [
        "farbe", "rot", "blau", "grün", "gelb", "schwarz", "weiß", "braun",
        "grau", "orange", "rosa", "lila", "hell", "dunkel", "bunt",
    ],
    "a1-vocab-days-months": [
        "montag", "dienstag", "mittwoch", "donnerstag", "freitag", "samstag",
        "sonntag", "wochenende", "wochentag", "januar", "februar", "märz",
        "april", "mai", "juni", "juli", "august", "september", "oktober",
        "november", "dezember", "monat", "woche", "tag", "jahr", "frühling",
        "sommer", "herbst", "winter", "datum", "kalender", "feiertag",
        "geburtstag", "geburtsjahr", "gestern", "heute", "morgen", "vorgestern",
        "übermorgen", "uhr", "stunde", "minute", "sekunde", "zeit",
        "vormittag", "nachmittag", "mittag", "mitternacht",
    ],
    "a1-vocab-shopping": [
        "kaufen", "einkaufen", "verkaufen", "geschäft", "laden", "supermarkt",
        "markt", "preis", "geld", "euro", "cent", "bezahlen", "zahlen",
        "kosten", "teuer", "billig", "günstig", "kasse", "quittung",
        "sonderangebot", "größe", "kreditkarte", "karte",
    ],
    "a1-vocab-professions": [
        "arzt", "ärztin", "lehrer", "lehrerin", "student", "koch", "ingenieur",
        "polizist", "verkäufer", "sekretär", "beruf", "kellner", "mechaniker",
        "krankenschwester", "friseur", "bäcker", "metzger", "apotheker",
        "journalist", "programmierer", "architekt", "pilot", "fahrer",
        "hausfrau", "hausmann", "angestellte", "beamte", "chef",
    ],
}

VOCAB_TOPIC_MAPPING_A2 = {
    "a2-vocab-health": [
        "kopf", "arm", "bein", "hand", "auge", "ohr", "nase", "mund",
        "krank", "gesund", "schmerz", "fieber", "arzt", "apotheke",
        "krankenhaus", "medikament", "zahn", "bauch", "rücken", "finger",
        "fuß", "hals", "herz", "körper", "blut", "husten", "schnupfen",
        "erkältung", "verletzt", "rezept", "tablette", "salbe", "pflaster",
        "untersuchung", "allergie", "operation", "notfall", "rettung",
        "krankenwagen", "diät", "vitamin",
    ],
    "a2-vocab-weather": [
        "wetter", "regen", "sonne", "schnee", "wind", "wolke", "sturm",
        "nebel", "temperatur", "grad", "kalt", "warm", "heiß", "kühl",
        "sonnig", "regnerisch", "bewölkt", "windig", "gewitter", "eis",
        "trocken", "feucht", "klima", "vorhersage",
    ],
    "a2-vocab-clothing": [
        "hemd", "hose", "kleid", "rock", "jacke", "mantel", "schuh",
        "socke", "mütze", "handschuh", "tasche", "pullover", "t-shirt",
        "bluse", "anzug", "krawatte", "gürtel", "stiefel", "schal",
        "brille", "schmuck", "ring", "uhr", "mode", "größe", "passen",
        "anprobieren", "umziehen",
    ],
    "a2-vocab-work": [
        "büro", "chef", "kollege", "firma", "gehalt", "bewerbung",
        "termin", "besprechung", "projekt", "arbeit", "stelle", "beruf",
        "karriere", "lebenslauf", "vertrag", "kündigung", "urlaub",
        "überstunde", "teilzeit", "vollzeit", "praktikum", "erfahrung",
        "abteilung", "meeting", "konferenz", "geschäftsführer",
    ],
    "a2-vocab-education": [
        "schule", "klasse", "prüfung", "unterricht", "lernen", "kurs",
        "note", "studium", "universität", "hausaufgabe", "zeugnis",
        "lehrer", "schüler", "student", "fach", "mathematik", "deutsch",
        "englisch", "gymnasium", "grundschule", "ausbildung", "diplom",
        "semester", "vorlesung", "bibliothek", "kennenlernen",
    ],
    "a2-vocab-services": [
        "bank", "post", "polizei", "amt", "behörde", "friseur", "werkstatt",
        "versicherung", "rathaus", "bürger", "formular", "antrag",
        "ausweis", "führerschein", "anmeldung", "abmeldung", "konto",
        "überweisung", "postkarte", "postleitzahl", "brief", "paket",
        "stempel", "poster",
    ],
    "a2-vocab-entertainment": [
        "fernsehen", "zeitung", "internet", "radio", "computer", "konzert",
        "theater", "programm", "nachricht", "zeitschrift", "film", "kino",
        "musik", "buch", "spiel", "serie", "sendung", "kanal", "online",
        "handy", "telefon", "app", "video", "lied", "band", "festival",
        "ticket", "eintrittskarte", "veranstaltung",
    ],
    "a2-vocab-emotions": [
        "freude", "angst", "traurig", "glücklich", "zufrieden", "ärger",
        "nervös", "freundlich", "nett", "lieb", "böse", "stolz", "müde",
        "lustig", "langweilig", "gern", "lieber", "lieblings", "verlieb",
        "einsam", "aufgeregt", "überrascht", "enttäuscht", "wütend",
        "hoffnung", "sorge", "lachen", "weinen", "fühlen", "lieben",
        "hassen", "mögen", "beliebt",
    ],
    "a2-vocab-culture": [
        "weihnacht", "ostern", "fest", "feier", "tradition", "kultur",
        "kirche", "feiertag", "karneval", "silvester", "neujahr",
        "oktoberfest", "brauch", "religion", "festival",
    ],
    "a2-vocab-directions": [
        "links", "rechts", "geradeaus", "ecke", "kreuzung",
        "richtung", "norden", "süden", "osten", "westen", "gegenüber",
        "nebenan", "daneben", "oben", "unten", "draußen", "drinnen",
        "hinten", "vorne", "entfernung", "kilometer", "navigation",
        "stadtplan", "landkarte", "wegbeschreibung", "ampel",
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
