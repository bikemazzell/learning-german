#!/usr/bin/env python3
"""
Goethe Institute Content Collector

Downloads and parses publicly available Goethe Institute exam materials
(word lists, practice exams) into structured JSON for the German trainer.

Sources:
  - Official Goethe Wortlisten (A1, A2) — PDF word lists
  - GitHub repos with pre-parsed Goethe data (TSV/CSV)
  - Goethe practice exam PDFs

Usage:
  python3 collect_goethe.py --level a1       # Collect A1 materials
  python3 collect_goethe.py --level a2       # Collect A2 materials
  python3 collect_goethe.py --level all      # Collect all levels
  python3 collect_goethe.py --source github  # Only GitHub repos (no PDF parsing)
  python3 collect_goethe.py --list-sources   # Show available sources

Requirements:
  pip install requests pdfplumber  (or: uv pip install requests pdfplumber)
"""

import argparse
import csv
import io
import json
import os
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

OUTPUT_DIR = Path(__file__).parent / "output"

SOURCES = {
    "goethe-wortliste-a1": {
        "url": "https://www.goethe.de/pro/relaunch/prf/de/A1_SD1_Wortliste_02.pdf",
        "type": "pdf",
        "level": "a1",
        "description": "Official Goethe A1 Start Deutsch 1 Wortliste (~650 words)",
    },
    "goethe-wortliste-a2": {
        "url": "https://www.goethe.de/pro/relaunch/prf/en/Goethe-Zertifikat_A2_Wortliste.pdf",
        "type": "pdf",
        "level": "a2",
        "description": "Official Goethe A2 Wortliste (~1300 words)",
    },
    "github-wordlist-tsv": {
        "url": "https://github.com/ilkermeliksitki/goethe-institute-wordlist",
        "api_base": "https://api.github.com/repos/ilkermeliksitki/goethe-institute-wordlist/contents",
        "type": "github-tsv",
        "levels": ["a1", "a2"],
        "description": "TSV word lists organized by level and letter (GitHub)",
    },
    "github-sprachomat-csv": {
        "url": "https://raw.githubusercontent.com/technologiestiftung/sprach-o-mat/main/data/dictionary_a1a2b1_onlystems.csv",
        "type": "csv",
        "levels": ["a1", "a2", "b1"],
        "description": "CSV vocabulary with level tags (GitHub sprach-o-mat)",
    },
    "github-a2-json": {
        "url": "https://raw.githubusercontent.com/langfield/A2_Wortliste_Goethe/master/models.json",
        "type": "json",
        "level": "a2",
        "description": "Structured A2 vocab with translations and audio (GitHub)",
    },
    "goethe-exam-a1-set1": {
        "url": "https://www.goethe.de/pro/relaunch/prf/de/A1_SD1_Modellsatz_Erwachsene.pdf",
        "type": "pdf-exam",
        "level": "a1",
        "description": "Official A1 practice exam set 1",
    },
    "goethe-exam-a2-set1": {
        "url": "https://www.goethe.de/pro/relaunch/prf/de/Goethe-Zertifikat_A2_Modellsatz_Erwachsene.pdf",
        "type": "pdf-exam",
        "level": "a2",
        "description": "Official A2 practice exam set 1",
    },
}

# ---------------------------------------------------------------------------
# Download helpers
# ---------------------------------------------------------------------------

def ensure_requests():
    try:
        import requests
        return requests
    except ImportError:
        print("ERROR: 'requests' package required. Install with:")
        print("  pip install requests")
        sys.exit(1)


def download_file(url, dest_path, description=""):
    requests = ensure_requests()
    if dest_path.exists():
        print(f"  [cached] {dest_path.name}")
        return dest_path

    print(f"  Downloading {description or url}...")
    resp = requests.get(url, timeout=60, headers={"User-Agent": "GoetheCollector/1.0"})
    resp.raise_for_status()
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    dest_path.write_bytes(resp.content)
    print(f"  [saved] {dest_path.name} ({len(resp.content)} bytes)")
    return dest_path


def download_text(url, description=""):
    requests = ensure_requests()
    print(f"  Fetching {description or url}...")
    resp = requests.get(url, timeout=30, headers={"User-Agent": "GoetheCollector/1.0"})
    resp.raise_for_status()
    return resp.text

# ---------------------------------------------------------------------------
# PDF parsing
# ---------------------------------------------------------------------------

def parse_wortliste_pdf(pdf_path, level):
    """Parse a Goethe Wortliste PDF into structured vocabulary entries."""
    try:
        import pdfplumber
    except ImportError:
        print("WARNING: 'pdfplumber' not installed. Skipping PDF parsing.")
        print("  Install with: pip install pdfplumber")
        return []

    print(f"  Parsing {pdf_path.name}...")
    entries = []
    seen = set()

    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages):
            text = page.extract_text()
            if not text:
                continue
            # Parse lines looking for vocabulary entries
            # Goethe format varies but typically: word, article, plural, example
            entries.extend(_extract_vocab_from_text(text, level, seen))

    print(f"  Extracted {len(entries)} vocabulary entries from {pdf_path.name}")
    return entries


def _extract_vocab_from_text(text, level, seen):
    """Extract vocabulary entries from Wortliste text.

    Handles common patterns:
      - "der Apfel, Äpfel  apple"
      - "groß  big, tall"
      - "spielen  to play"
    """
    entries = []
    lines = text.split("\n")

    # Pattern: German word (possibly with article), comma, plural, spaces, meaning
    article_pattern = re.compile(
        r"^(der|die|das)\s+(\w[\wäöüß-]+)"
        r"(?:,\s*([\wäöüß-]+))?"  # optional plural
        r"(?:\s+(.+))?$",
        re.IGNORECASE,
    )

    # Pattern: word without article
    word_pattern = re.compile(
        r"^(\w[\wäöüß-]+)"
        r"(?:\s+(.+))?$",
    )

    for line in lines:
        line = line.strip()
        if not line or len(line) < 3:
            continue
        # Skip page numbers, headers, etc.
        if line.isdigit() or line.startswith("Seite") or line.startswith("Wortliste"):
            continue

        m = article_pattern.match(line)
        if m:
            article = m.group(1).lower()
            word = m.group(2)
            plural = m.group(3) or ""
            meaning = (m.group(4) or "").strip()

            key = f"{article} {word}".lower()
            if key in seen:
                continue
            seen.add(key)

            gender_map = {"der": "masculine", "die": "feminine", "das": "neuter"}
            entries.append({
                "german": f"{article} {word}",
                "english": meaning,
                "article": article,
                "gender": gender_map.get(article, ""),
                "plural": f"die {plural}" if plural else "",
                "type": "vocabulary",
                "level": level,
                "source": "goethe-wortliste",
            })
            continue

        # Try non-article word (verbs, adjectives, etc.)
        m2 = word_pattern.match(line)
        if m2:
            word = m2.group(1)
            meaning = (m2.group(2) or "").strip()
            if len(word) < 3 or word[0].isdigit():
                continue

            key = word.lower()
            if key in seen:
                continue
            seen.add(key)

            entries.append({
                "german": word,
                "english": meaning,
                "type": "vocabulary",
                "level": level,
                "source": "goethe-wortliste",
            })

    return entries


def parse_exam_pdf(pdf_path, level):
    """Parse a Goethe practice exam PDF — extract exercises and question types."""
    try:
        import pdfplumber
    except ImportError:
        print("WARNING: 'pdfplumber' not installed. Skipping exam parsing.")
        return []

    print(f"  Parsing exam: {pdf_path.name}...")
    exercises = []

    with pdfplumber.open(pdf_path) as pdf:
        full_text = ""
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                full_text += text + "\n---PAGE---\n"

    # Save raw text for manual review
    raw_path = pdf_path.with_suffix(".txt")
    raw_path.write_text(full_text, encoding="utf-8")
    print(f"  [saved] Raw text: {raw_path.name}")

    # Extract structured exercise patterns
    exercises = _extract_exercises_from_exam(full_text, level)
    print(f"  Extracted {len(exercises)} exercise items from {pdf_path.name}")
    return exercises


def _extract_exercises_from_exam(text, level):
    """Extract exercise patterns from exam text.

    Looks for:
    - Richtig/Falsch (True/False) sections
    - Multiple choice (a/b/c) sections
    - Fill-in-blank patterns
    """
    exercises = []

    # Find Richtig/Falsch patterns
    rf_pattern = re.compile(r"(richtig|falsch)", re.IGNORECASE)
    # Find multiple choice patterns (a) ... b) ... c) ...)
    mc_pattern = re.compile(r"\b([abc])\)\s+(.+?)(?=\b[abc]\)|$)", re.IGNORECASE)

    sections = text.split("---PAGE---")
    for i, section in enumerate(sections):
        # Detect exercise sections (Lesen, Hören, etc.)
        if re.search(r"(Lesen|Hören|Schreiben)", section):
            exercises.append({
                "page": i + 1,
                "type": "exam-section",
                "content_preview": section[:500].strip(),
                "level": level,
                "source": "goethe-exam",
            })

    return exercises

# ---------------------------------------------------------------------------
# GitHub TSV parser
# ---------------------------------------------------------------------------

def collect_github_tsv(level):
    """Download TSV word lists from ilkermeliksitki/goethe-institute-wordlist."""
    requests = ensure_requests()
    entries = []
    base = SOURCES["github-wordlist-tsv"]["api_base"]

    print(f"  Fetching GitHub TSV index for {level}...")
    try:
        resp = requests.get(
            f"{base}/{level}",
            timeout=30,
            headers={"User-Agent": "GoetheCollector/1.0"},
        )
        resp.raise_for_status()
        files = resp.json()
    except Exception as e:
        print(f"  WARNING: Could not fetch GitHub TSV index: {e}")
        return entries

    for f in files:
        if not f["name"].endswith(".tsv"):
            continue
        print(f"    Fetching {f['name']}...")
        try:
            content = requests.get(
                f["download_url"],
                timeout=30,
                headers={"User-Agent": "GoetheCollector/1.0"},
            ).text
        except Exception as e:
            print(f"    WARNING: Failed to download {f['name']}: {e}")
            continue

        reader = csv.reader(io.StringIO(content), delimiter="\t")
        for row in reader:
            if not row or len(row) < 1:
                continue
            word = row[0].strip()
            if not word or word.startswith("#"):
                continue

            entries.append({
                "german": word,
                "english": row[1].strip() if len(row) > 1 else "",
                "type": "vocabulary",
                "level": level,
                "source": "github-tsv",
            })

    print(f"  Collected {len(entries)} entries from GitHub TSV")
    return entries

# ---------------------------------------------------------------------------
# CSV parser (sprach-o-mat)
# ---------------------------------------------------------------------------

def collect_sprachomat_csv(levels):
    """Download and parse sprach-o-mat CSV vocabulary."""
    url = SOURCES["github-sprachomat-csv"]["url"]
    entries = []

    try:
        content = download_text(url, "sprach-o-mat CSV")
    except Exception as e:
        print(f"  WARNING: Could not fetch sprach-o-mat CSV: {e}")
        return entries

    reader = csv.DictReader(io.StringIO(content))
    for row in reader:
        row_level = (row.get("Level", "") or "").strip().lower()
        if row_level not in levels:
            continue
        stem = (row.get("Stem", "") or "").strip()
        if not stem:
            continue

        entries.append({
            "german": stem,
            "english": "",
            "type": "vocabulary",
            "level": row_level,
            "source": "sprachomat",
        })

    print(f"  Collected {len(entries)} entries from sprach-o-mat")
    return entries

# ---------------------------------------------------------------------------
# Merge and deduplicate
# ---------------------------------------------------------------------------

def merge_entries(all_entries):
    """Merge entries from multiple sources, preferring richer data."""
    merged = {}
    for entry in all_entries:
        key = entry["german"].lower().strip()
        if key in merged:
            # Keep the entry with more data
            existing = merged[key]
            if not existing.get("english") and entry.get("english"):
                existing["english"] = entry["english"]
            if not existing.get("article") and entry.get("article"):
                existing["article"] = entry["article"]
                existing["gender"] = entry.get("gender", "")
            if not existing.get("plural") and entry.get("plural"):
                existing["plural"] = entry["plural"]
            # Track all sources
            sources = existing.get("sources", [existing.get("source", "")])
            if entry.get("source") not in sources:
                sources.append(entry["source"])
            existing["sources"] = sources
        else:
            merged[key] = entry.copy()
    return list(merged.values())

# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def save_output(data, filename):
    """Save collected data as JSON."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTPUT_DIR / filename
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"\n[output] {path} ({len(data)} entries)")
    return path

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def collect_level(level, source_filter=None):
    """Collect all available data for a given level."""
    print(f"\n{'='*60}")
    print(f"Collecting {level.upper()} materials")
    print(f"{'='*60}")

    all_entries = []
    exam_data = []
    downloads_dir = OUTPUT_DIR / "downloads"
    downloads_dir.mkdir(parents=True, exist_ok=True)

    # 1. GitHub TSV (fast, no PDF parsing needed)
    if source_filter in (None, "github"):
        print(f"\n[source] GitHub TSV word lists")
        all_entries.extend(collect_github_tsv(level))

    # 2. Sprach-o-mat CSV
    if source_filter in (None, "github"):
        print(f"\n[source] Sprach-o-mat CSV")
        all_entries.extend(collect_sprachomat_csv([level]))

    # 3. Official Wortliste PDF
    wortliste_key = f"goethe-wortliste-{level}"
    if wortliste_key in SOURCES and source_filter in (None, "pdf"):
        src = SOURCES[wortliste_key]
        print(f"\n[source] {src['description']}")
        pdf_path = downloads_dir / f"wortliste_{level}.pdf"
        try:
            download_file(src["url"], pdf_path, src["description"])
            all_entries.extend(parse_wortliste_pdf(pdf_path, level))
        except Exception as e:
            print(f"  WARNING: Failed to process Wortliste PDF: {e}")

    # 4. Practice exam PDFs
    exam_key = f"goethe-exam-{level}-set1"
    if exam_key in SOURCES and source_filter in (None, "pdf", "exam"):
        src = SOURCES[exam_key]
        print(f"\n[source] {src['description']}")
        pdf_path = downloads_dir / f"exam_{level}_set1.pdf"
        try:
            download_file(src["url"], pdf_path, src["description"])
            exam_data.extend(parse_exam_pdf(pdf_path, level))
        except Exception as e:
            print(f"  WARNING: Failed to process exam PDF: {e}")

    # Merge and deduplicate vocabulary
    merged = merge_entries(all_entries)

    # Sort by German word
    merged.sort(key=lambda e: e["german"].lower())

    # Save outputs
    save_output(merged, f"vocabulary_{level}.json")
    if exam_data:
        save_output(exam_data, f"exam_exercises_{level}.json")

    # Print summary
    print(f"\n--- {level.upper()} Summary ---")
    print(f"  Total unique vocabulary entries: {len(merged)}")
    with_english = sum(1 for e in merged if e.get("english"))
    with_article = sum(1 for e in merged if e.get("article"))
    print(f"  With English translation: {with_english}")
    print(f"  With article/gender: {with_article}")
    print(f"  Exam exercise items: {len(exam_data)}")

    return merged


def list_sources():
    """Print all available sources."""
    print("\nAvailable sources:\n")
    for key, src in SOURCES.items():
        levels = src.get("level", src.get("levels", "?"))
        print(f"  {key}")
        print(f"    {src['description']}")
        print(f"    Level(s): {levels}")
        print(f"    Type: {src['type']}")
        print(f"    URL: {src['url']}")
        print()


def main():
    parser = argparse.ArgumentParser(
        description="Collect Goethe Institute exam materials for the German trainer"
    )
    parser.add_argument(
        "--level", choices=["a1", "a2", "all"], default="all",
        help="Which level to collect (default: all)"
    )
    parser.add_argument(
        "--source", choices=["github", "pdf", "exam"],
        help="Only collect from specific source type"
    )
    parser.add_argument(
        "--list-sources", action="store_true",
        help="List all available sources and exit"
    )
    parser.add_argument(
        "--output-dir", type=str,
        help="Custom output directory (default: collector/output/)"
    )

    args = parser.parse_args()

    if args.list_sources:
        list_sources()
        return

    global OUTPUT_DIR
    if args.output_dir:
        OUTPUT_DIR = Path(args.output_dir)

    levels = ["a1", "a2"] if args.level == "all" else [args.level]

    for level in levels:
        collect_level(level, args.source)

    print(f"\n{'='*60}")
    print("Collection complete. Output in: " + str(OUTPUT_DIR))
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
