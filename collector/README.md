# Goethe Content Collector

Tools for gathering and processing Goethe Institute exam materials into structured data for the German trainer.

## Pipeline

```
collect_goethe.py  →  output/*.json  →  convert_to_trainer.py  →  trainer/data/levels/*.json
     (gather)          (raw data)          (transform)              (trainer-ready)
```

## Quick Start

```bash
# Install dependencies
pip install requests pdfplumber

# Collect A1 materials (GitHub sources only, no PDF parsing)
python3 collect_goethe.py --level a1 --source github

# Collect everything (including PDF word lists and exam papers)
python3 collect_goethe.py --level all

# Compare collected data against current trainer content
python3 convert_to_trainer.py --level a1 --compare

# Preview enrichment (no file changes)
python3 convert_to_trainer.py --level a1 --dry-run

# Apply enrichment to trainer data
python3 convert_to_trainer.py --level a1
```

## Sources

| Source | Type | Content | Requires |
|--------|------|---------|----------|
| GitHub TSV wordlist | TSV | A1/A2 vocab by letter | `requests` |
| Sprach-o-mat CSV | CSV | A1/A2/B1 word stems | `requests` |
| Goethe Wortliste PDFs | PDF | Official ~650 (A1) / ~1300 (A2) words | `requests`, `pdfplumber` |
| Goethe practice exams | PDF | Exam exercises (Lesen, Hören, etc.) | `requests`, `pdfplumber` |

## Output

- `output/vocabulary_a1.json` — Merged, deduplicated A1 vocabulary
- `output/vocabulary_a2.json` — Merged, deduplicated A2 vocabulary
- `output/exam_exercises_a1.json` — Extracted exam exercise patterns
- `output/downloads/` — Cached PDF downloads

## Notes

- Grammar topics are NOT auto-generated. They require manual or LLM-assisted curation.
- The converter only enriches existing vocab topics — it doesn't create new topics.
- KPs added from collected data have empty `example_sentence` fields that need filling.
- Run `--compare` first to see what's missing before applying changes.
