# German Level Trainer

A mastery-based German language trainer modeled on [MathAcademy.com](https://www.mathacademy.com), targeting Goethe Institute A1 and A2 exam levels.

## What It Does

The trainer guides students through all grammar and vocabulary topics required for Goethe A1 and A2 certification using:

- **Knowledge graph** with 55 topics and 1398 knowledge points across two levels
- **SM-2 spaced repetition** per knowledge point, with adaptive review scheduling
- **Mastery-based progression** — topics are marked mastered when 85% of knowledge points reach mastery (7+ day interval, 85%+ accuracy)
- **Adaptive recommendations** — the system tells you what to study next based on due reviews, in-progress topics, and prerequisite dependencies
- **5 exercise types** — multiple choice, fill-in-the-blank, matching, translation, and sentence production
- **Exam Practice** — Goethe-style Lesen and Schreiben tasks with separate progress tracking
- **Difficulty progression** — easier exercise types first, harder ones as you improve on each knowledge point

## Content Coverage

| | A1 | A2 | Total |
|---|---|---|---|
| Grammar topics | 18 | 15 | 33 |
| Vocabulary topics | 12 | 10 | 22 |
| Knowledge points | 700 | 698 | 1398 |
| Exam reading tasks | 12 | 12 | 24 |
| Exam writing prompts | 12 | 12 | 24 |

**A1 Grammar:** Personal pronouns, sein/haben, nominative articles, present tense, negation, questions, possessives, accusative case, prepositions, adjectives, plurals, irregular verbs, modals, imperatives, numbers/time, word order, connectors.

**A1 Vocabulary:** Greetings, numbers, family, food & drink, daily routines, home & furniture, travel, hobbies, colors, days/months/seasons, shopping, professions.

**A2 Grammar:** Perfekt (haben/sein), irregular participles, dative case, dative/two-way prepositions, separable verbs, reflexive verbs, comparatives/superlatives, subordinate/temporal clauses, expanded modals, Futur I, adjective declension.

**A2 Vocabulary:** Health & body, weather, work & career, education, services, entertainment, clothing, emotions, German culture, directions.

## How It Works

### Session Flow

1. **Dashboard** shows your progress, review queue, and a recommended next topic
2. Click **Start Session** to get a mix of ~12 questions (60% new material, 30% reviews, 10% mastered-topic maintenance)
3. Answer questions with immediate feedback and explanations
4. **Session Summary** shows your accuracy and what to study next

### Mastery Model

- Each knowledge point tracks its own SM-2 state (ease factor, interval, next review date)
- A knowledge point is **mastered** when its review interval reaches 7+ days with 85%+ accuracy
- A topic is **mastered** when 85% of its knowledge points are mastered
- Mastered topics enter low-frequency review — they surface occasionally but don't dominate your sessions

### Prerequisites

Topics have soft prerequisites. The system recommends studying prerequisites first and shows warnings, but never locks you out of any topic.

### Exam Practice

The Exam Practice area covers the Goethe gaps that are not part of the grammar/vocabulary scheduler:

- **Lesen:** short original A1/A2 reading tasks with multiple-choice scoring and explanations
- **Schreiben:** original prompts with expected themes, word-count guidance, useful phrases, and self-review checklists
- **Progress:** reading scores and completed writing prompts are tracked separately from SM-2 progress
- **Privacy:** writing text is not stored; students can evaluate drafts with a teacher, tutor, or LLM

## Running

The app is a static HTML/CSS/JS site that loads data via `fetch()`, so it needs a local server:

```bash
cd trainer
python3 -m http.server 8765
# Open http://localhost:8765
```

Or use any static file server (e.g., `npx serve`, VS Code Live Server).

## Project Structure

```
learning-german/
├── trainer/                    # Main trainer application
│   ├── index.html             # SPA entry point
│   ├── css/styles.css         # Responsive dark/light mode styling
│   ├── js/
│   │   ├── app.js             # Main controller, routing, session lifecycle
│   │   ├── engine.js          # SM-2 algorithm, mastery calculations, session composition
│   │   ├── exam.js            # Exam practice loading, scoring, and progress
│   │   ├── recommender.js     # Prerequisite checking, adaptive topic recommendations
│   │   ├── exercises.js       # Exercise generation from templates, answer validation
│   │   ├── progress.js        # localStorage persistence, export/import
│   │   └── ui.js              # DOM rendering for all views
│   └── data/
│       ├── levels/
│       │   ├── a1.json        # A1 knowledge graph (30 topics, 700 KPs)
│       │   └── a2.json        # A2 knowledge graph (25 topics, 698 KPs)
│       ├── exam/
│       │   ├── a1.json        # A1 Lesen and Schreiben practice tasks
│       │   └── a2.json        # A2 Lesen and Schreiben practice tasks
│       └── templates/
│           ├── grammar.json   # Exercise templates for grammar topics
│           └── vocab.json     # Exercise templates for vocabulary topics
├── scripts/                    # Legacy CLI quizzes (Python)
├── quiz-app/                   # Legacy web quiz (vanilla JS)
├── source/                     # Learning materials and references
└── docs/
    └── superpowers/specs/     # Design spec
```

## Tech Stack

- **Vanilla HTML/CSS/JavaScript** — zero dependencies, no build step
- **localStorage** for progress persistence
- **JSON data files** for knowledge graphs and exercise templates
- **SM-2 algorithm** for spaced repetition scheduling

## Progress Data

Progress is stored in localStorage and can be exported/imported via the Settings page. Keys:
- `trainer-progress-a1` — A1 level progress
- `trainer-progress-a2` — A2 level progress
- `trainer-exam-practice` — separate A1/A2 Lesen and Schreiben practice progress

## Design

Full design spec at [`docs/superpowers/specs/2026-03-27-german-level-trainer-design.md`](docs/superpowers/specs/2026-03-27-german-level-trainer-design.md).
