# German Level Trainer — Design Spec

## Context

The existing project has CLI and web quizzes for German articles (652 nouns), dative verbs (36), and irregular verbs (97), all using SM-2 spaced repetition. The goal is to build a new, separate system modeled on MathAcademy.com that provides structured, level-based training aligned with Goethe Institute exam levels.

**Problem:** Current quizzes are topic-isolated with no sense of progression, prerequisite relationships, or adaptive recommendations. A student can't answer "am I ready for the A1 exam?" or "what should I study next?"

**Solution:** A mastery-based trainer with a knowledge graph, adaptive recommendations, and spaced repetition that guides students through all grammar and vocabulary topics required for a given Goethe level.

## Scope

- **Levels:** A1 and A2 (extensible to B1+ later)
- **Skill areas:** Grammar and vocabulary only (no reading comprehension, listening, writing, or speaking)
- **Platform:** Enhanced vanilla HTML/CSS/JS web app, localStorage for progress, no backend
- **Existing quizzes:** Untouched. New system lives in `trainer/` directory. Fresh start.

## Architecture: Topic Tree + Enhanced SM-2

### Data Model

Four layers:

```
Level (A1, A2)
  └── Domain (Grammar, Vocabulary)
        └── Topic
              ├── id: string (e.g., "a1-grammar-nominative-articles")
              ├── name: string
              ├── description: string
              ├── prerequisites: string[] (topic IDs, soft — recommendations, not locks)
              ├── mastery_threshold: number (default 0.85)
              ├── exercise_templates: ExerciseTemplate[]
              └── knowledge_points: KnowledgePoint[]
                    ├── id: string
                    ├── prompt_data: object (see KP Data Shapes below)
                    └── explanation: string
```

**KP Data Shapes by domain:**

Grammar KP (e.g., verb conjugation):
```json
{
  "type": "conjugation",
  "verb": "spielen",
  "pronoun": "ich",
  "correct_form": "spiele",
  "tense": "present",
  "example_sentence": "Ich spiele Fußball."
}
```

Vocabulary KP (e.g., food item):
```json
{
  "type": "vocabulary",
  "german": "der Apfel",
  "english": "the apple",
  "article": "der",
  "gender": "masculine",
  "plural": "die Äpfel",
  "example_sentence": "Ich esse einen Apfel."
}
```
```

### Knowledge Graph Structure

**A1 Grammar topics (~18 topics):**
- Personal pronouns → Verb sein → Verb haben
- Nominative articles (definite + indefinite)
- Present tense regular verbs (requires: pronouns, articles)
- Basic question formation (W-questions)
- Negation (nicht/kein)
- Possessive adjectives
- Accusative case (requires: nominative articles, present tense)
- Accusative prepositions
- Basic adjectives in nominative
- Plural forms
- Irregular present tense verbs (stem changes)
- Modal verbs (können, mögen, wollen)
- Imperatives
- Numbers and time expressions
- Basic prepositions (mit, von, zu)
- Word order in statements
- Word order in questions
- Sentence connectors (und, aber, oder)

**A1 Vocabulary topics (~12 topics):**
- Greetings and basics
- Numbers 0-100
- Family members
- Food and drink
- Daily routines
- Home and furniture
- Travel and transport
- Hobbies and leisure
- Colors and descriptions
- Days, months, seasons
- Shopping and commerce
- Professions

**A2 Grammar topics (~15 topics):**
- Perfekt tense (haben + sein auxiliaries)
- Past participle formation (regular)
- Past participle formation (irregular)
- Dative case
- Dative prepositions
- Two-way prepositions (Wechselpräpositionen)
- Separable verbs
- Reflexive verbs
- Comparative adjectives
- Superlative adjectives
- Subordinate clauses (weil, dass)
- Temporal clauses (wenn, während)
- Expanded modal verbs (dürfen, sollen, müssen)
- Futur I (werden + infinitive)
- Adjective declension with dative

**A2 Vocabulary topics (~10 topics):**
- Health and body parts
- Weather and seasons (expanded)
- Work and career
- Education and school
- Services and establishments
- Entertainment and media
- Clothing
- Emotions and personality
- German culture and traditions
- Directions and location (expanded)

**Total: ~55 topics across A1+A2**

### Exercise Templates

**5 exercise types (4 core + 1 production):**

1. **Multiple Choice** — Select correct answer from 3-4 options
   - Used for: article selection, verb conjugation, vocabulary meaning, grammar rules
   - Distractors: generated from same paradigm (wrong gender, wrong conjugation, etc.)

2. **Fill in the Blank** — Type the missing word in a sentence
   - Used for: verb conjugation in context, article usage, preposition selection
   - Accepts minor typo tolerance

3. **Matching** — Connect 4-6 pairs (German ↔ English, or prompt ↔ answer)
   - Used for: vocabulary bulk practice, pronoun-verb pairing
   - Drag-and-drop or click-to-pair UI

4. **Translation** — Translate a word or short phrase
   - Used for: vocabulary (both directions), short grammar constructions
   - Accepts reasonable synonyms

5. **Sentence Production** — Given a scenario/prompt, write a full German sentence
   - Used for: grammar synthesis, mastery-gate exercises
   - Example: "Say that you have a sister" → "Ich habe eine Schwester"
   - Validation: each sentence production exercise defines required keywords (e.g., ["habe", "Schwester"]) and optional structural patterns (e.g., verb in position 2). Answer must contain all required keywords. Case-insensitive, minor typo tolerance via Levenshtein distance ≤ 1.

**Template definition format:**
```json
{
  "type": "multiple-choice",
  "prompt_template": "What is the article for '{noun}'?",
  "answer_key": "article",
  "distractor_strategy": "same-field-wrong-value",
  "distractor_pool": ["der", "die", "das"]
}
```

**Exercise difficulty progression per KP:**
- First encounter: Multiple choice (easiest)
- After 1-2 correct: Fill in the blank
- After 3+ correct: Translation or sentence production (hardest)

### Mastery & Spaced Repetition

**Per-knowledge-point SM-2 state:**
```json
{
  "kp_id": "a1-gram-articles-kp-tisch",
  "ease_factor": 2.5,
  "interval_days": 1,
  "next_review": "2026-03-28",
  "correct_streak": 0,
  "total_correct": 0,
  "total_attempts": 0
}
```

**Topic mastery:**
- KP is "mastered" when: interval ≥ 7 days AND accuracy ≥ 85%
- Topic mastery score = % of KPs at mastered status
- Topic states: **New** (0% started) → **Learning** (< 85% KPs mastered) → **Mastered** (≥ 85%)

**Session composition (default 10-15 questions):**
- ~60% new/learning material from recommended topic
- ~30% due reviews across all topics
- ~10% occasional review of mastered KPs approaching review date

### Recommendation Engine

Priority order for "what to study next":

1. **Due reviews** — KPs past their `next_review` date. Always come first.
2. **Continue in-progress topic** — If a topic is in Learning state, continue it.
3. **Next recommended topic** — Highest priority unmastered topic where:
   - All prerequisites are at ≥ 50% mastery (soft gate)
   - Same level as current focus (A1 before A2)
   - Grammar and vocabulary interleaved (not all grammar then all vocab)

### Progress Persistence

- **localStorage** keyed by level: `trainer-progress-a1`, `trainer-progress-a2`
- **Export/Import:** JSON download/upload for backup
- **Reset:** Per-topic or full level reset

## UI Structure

### Pages/Views

1. **Dashboard** (landing page)
   - Level selector (A1 / A2 tabs)
   - Overall progress: grammar mastery %, vocab mastery %, total topics mastered
   - Review queue count
   - Recommended next topic with "Start" button
   - Topic map: visual grid showing all topics with mastery state (new/learning/mastered)

2. **Topic Browser**
   - Full topic tree organized by domain
   - Each topic shows: name, mastery %, prerequisite status, KP count
   - Click to start practicing any topic (soft prereq warning if not met)

3. **Quiz Session**
   - Question display with exercise type UI
   - Answer input (buttons for MC, text input for fill-blank/translation, drag for matching)
   - Immediate feedback: correct/incorrect + explanation
   - Progress bar: questions completed / session total
   - "End session" button

4. **Session Summary**
   - Accuracy breakdown
   - KPs progressed / newly mastered
   - Topics advanced
   - Next recommendation

### Responsive Design
- Mobile-friendly (quiz sessions especially)
- Touch-friendly targets for matching exercises

## File Structure

```
trainer/
├── index.html              # SPA entry point
├── css/
│   └── styles.css          # All styling
├── js/
│   ├── app.js              # Main controller, view routing, initialization
│   ├── engine.js           # SM-2 algorithm, mastery calculations, session composer
│   ├── recommender.js      # Prerequisite checking, topic recommendation logic
│   ├── exercises.js        # Exercise template engine, question generation, validation
│   ├── progress.js         # localStorage CRUD, export/import, reset
│   └── ui.js               # DOM rendering: dashboard, topic browser, quiz, summary
└── data/
    ├── levels/
    │   ├── a1.json          # A1 knowledge graph (all topics, KPs, prereqs)
    │   └── a2.json          # A2 knowledge graph
    └── templates/
        ├── grammar.json     # Exercise templates for grammar topic types
        └── vocab.json       # Exercise templates for vocabulary topic types
```

## Data Generation Workflow

1. Use Claude to generate A1 knowledge graph JSON (topics, KPs, prereqs, exercise config)
2. Review, refine, and correct the generated data
3. Repeat for A2
4. Exercise templates are defined per topic type (not per topic) — reusable

## Verification Plan

1. **Data integrity:** Validate JSON schema — no broken prereq references, all KPs have required fields
2. **SM-2 correctness:** Unit-test the engine with known sequences (correct/incorrect/mixed) and verify intervals match SM-2 spec
3. **Recommendation sanity:** Walk through a simulated student journey — verify topics are recommended in sensible order
4. **Exercise generation:** For each topic, generate 10 exercises and verify they're valid (correct answers exist, distractors are wrong)
5. **Full flow test:** Start as new student, complete one topic to mastery, verify dashboard updates, recommendations change, and reviews schedule correctly
6. **localStorage persistence:** Refresh page, verify progress survives. Export, clear, import, verify restoration.
7. **Edge cases:** Empty state (new student), all topics mastered, single KP topic, topic with many prereqs
