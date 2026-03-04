# Plan: Reorganize German Irregular Verbs for Optimal Memorization

## Overview

Reorganize the 82 irregular verbs in `irregular-perfect.md` using cognitive science principles to maximize memorization effectiveness.

## Key Insights from Research

1. **Mnemonic effectiveness varies**: Inka/barrel/Saudi are strong (concrete nouns, clear vowel shifts); anaconda/wind are weak
2. **Anaconda is problematic**: A→A shows no vowel change - rename to "SPHINX" (mysterious, needs special attention)
3. **Large groups need sub-grouping**: Polo (19 verbs) and lasso (15 verbs) should be split by semantic meaning
4. **Frequency matters**: Common verbs first within each group
5. **Interleaving beats blocking**: Similar patterns (Polo o-o, lasso a-o) should NOT be learned back-to-back
6. **Inseparable prefix note**: Verbs with be-, emp-, ent-, er-, ge-, miss-, ver-, zer- prefixes don't add "ge-" in perfect

## Proposed Organization Structure

### Primary: 8 Mnemonic Groups with Color Codes

| Mnemonic | Pattern | Color | Verbs | Phase |
|----------|---------|-------|-------|-------|
| INKA | I → A | Red | 10 | 1 |
| BARREL | A → E | Green | 8 | 1 |
| SAUDI | A → U | Gold | 9 | 1 |
| USA | U → A | Blue | 7 | 2 |
| LASSO | A → O | Orange | 15 | 2 |
| POLO | O → O | Teal | 19 | 3 |
| WIND | I → IE | Sky Blue | 6 | 4 |
| ANACONDA | Mixed | Purple | 8 | 4 |

### Secondary: Semantic Sub-groups for Large Categories

**POLO (19 verbs) split into:**
- Movement: ziehen, fliegen, schieben, biegen, fliehen
- Liquids/Temp: schließen, fließen, gießen, schmelzen, frieren
- Sensory/Abstract: bieten, genießen, heben, riechen, wiegen, lügen, verlieren
- Forceful: schießen, saufen

**LASSO (15 verbs) split into:**
- Communication: sprechen, treffen, empfehlen
- Physical: nehmen, helfen, kommen, werfen, brechen
- Life/Competition: beginnen, gewinnen, schwimmen, sterben
- Taking: stehlen, stechen

**ANACONDA (8 verbs) split into:**
- "-enn-" verbs: kennen, nennen, brennen, rennen (all follow e→a pattern)
- Consonant change: denken, bringen (both have -achte/-acht)
- True irregulars: stehen, tun (memorize individually)

### Tertiary: Frequency Ordering

Within each group/sub-group, order by frequency:
- ★★★ = Essential (gehen, sehen, nehmen, fahren, etc.)
- ★★☆ = Common (schlafen, trinken, werfen, etc.)
- ★☆☆ = Less common (braten, graben, stinken, etc.)

---

## Automation: Study/Testing App

### Data Format for Parsing

The markdown tables can be parsed into structured data:

```python
# Example verb data structure
verb = {
    "infinitive": "sprechen",
    "mnemonic": "lasso",
    "pattern": "a-o",
    "praeteritum": "sprach",
    "perfect": "gesprochen",
    "english": "to speak",
    "frequency": 3,  # ★★★ = 3, ★★☆ = 2, ★☆☆ = 1
    "phase": 2,
    "semantic_group": "communication",
    "has_ge_prefix": True  # False for ver-, be-, ge-, emp- verbs
}
```

### Quiz Modes

1. **Infinitive → Forms**: Given infinitive, produce praeteritum and/or perfect
2. **Forms → Infinitive**: Given conjugated form, identify the infinitive
3. **English → German**: Translation with conjugation
4. **Mnemonic Drill**: Given mnemonic, recall all verbs in that group
5. **Pattern Recognition**: Given a verb, identify its mnemonic pattern
6. **Fill-in-the-blank**: Complete sentences with correct form

### Simple CLI App Structure

```
learning-german/
├── irregular-perfect.md      # Source data (reorganized)
├── verbs.json                # Parsed verb data
├── quiz.py                   # Quiz script
└── progress.json             # Track user progress (spaced repetition)
```

### Key Features

1. **Parse markdown** → Extract verb tables into JSON
2. **Spaced repetition**: Track correct/incorrect, adjust review intervals
3. **Phase-based progression**: Unlock phases as mastery increases
4. **Mnemonic hints**: Show mnemonic when stuck
5. **Statistics**: Track accuracy by mnemonic group, identify weak areas

### Example Quiz Flow

```
$ python quiz.py

Mode: [1] Praeteritum [2] Perfect [3] Both [4] Mnemonic drill
> 1

Phase: [1] Strong [2] Moderate [3] O-Pattern [4] Special [a] All
> 1

---
What is the Praeteritum of "gehen"? (INKA: i→a)
> ging
✓ Correct!

What is the Praeteritum of "trinken"? (SAUDI: a→u)
> trunk
✗ Incorrect. Answer: trank (remember: SAUDI = a→u, not u!)

Score: 1/2 (50%)
```

### Tech Options

- **Python CLI**: Simple, quick to build with `argparse` or `click`
- **Web app**: React/Vue frontend, localStorage for progress
- **Anki export**: Generate `.apkg` file for existing spaced repetition
- **Terminal UI**: `rich` or `textual` for colorful CLI experience
