'use strict';

const test   = require('node:test');
const assert = require('node:assert/strict');
const { loadTrainer, loadLevel, flattenTopics } = require('./_harness');

// Stabilise Math.random so we deterministically exercise every template path.
function withSeed(seed, fn) {
  const orig = Math.random;
  let s = seed;
  Math.random = () => {
    // LCG — numerically unimportant, just deterministic.
    s = (s * 1664525 + 1013904223) >>> 0;
    return s / 0x100000000;
  };
  try { return fn(); } finally { Math.random = orig; }
}

const PLACEHOLDER_RE = /\{[a-zA-Z_][a-zA-Z0-9_]*\}/;

function findTopic(level, topicId) {
  const topics = flattenTopics(level);
  return topics.find(t => t.id === topicId);
}

test('generateExercise: no prompt ever contains an unresolved {placeholder}', () => {
  const { Exercises } = loadTrainer();
  const levels = [loadLevel('a1'), loadLevel('a2')];

  for (const level of levels) {
    for (const topic of flattenTopics(level)) {
      const kps = topic.knowledge_points || [];
      for (const kp of kps) {
        for (let difficulty = 0; difficulty <= 5; difficulty++) {
          // Try several random seeds to shake out template choices.
          for (let seed = 1; seed <= 5; seed++) {
            const ex = withSeed(seed, () =>
              Exercises.generateExercise(kp, topic.exercise_templates, difficulty, kps)
            );
            if (ex && typeof ex.prompt === 'string') {
              assert.ok(
                !PLACEHOLDER_RE.test(ex.prompt),
                `Unresolved placeholder in ${topic.id}/${kp.id} ` +
                `(type=${kp.prompt_data.type}, difficulty=${difficulty}): "${ex.prompt}"`
              );
            }
          }
        }
      }
    }
  }
});

test('generateExercise: answerable exercises always have a non-empty correctAnswer', () => {
  const { Exercises } = loadTrainer();
  const levels = [loadLevel('a1'), loadLevel('a2')];
  const typesRequiringAnswer = new Set(['multiple-choice', 'fill-blank', 'translation']);

  for (const level of levels) {
    for (const topic of flattenTopics(level)) {
      const kps = topic.knowledge_points || [];
      for (const kp of kps) {
        for (let difficulty = 0; difficulty <= 5; difficulty++) {
          for (let seed = 1; seed <= 5; seed++) {
            const ex = withSeed(seed, () =>
              Exercises.generateExercise(kp, topic.exercise_templates, difficulty, kps)
            );
            if (!ex || !typesRequiringAnswer.has(ex.type)) continue;
            assert.ok(
              typeof ex.correctAnswer === 'string' && ex.correctAnswer.length > 0,
              `Empty correctAnswer in ${topic.id}/${kp.id} type=${ex.type} ` +
              `kpType=${kp.prompt_data.type} difficulty=${difficulty}`
            );
          }
        }
      }
    }
  }
});

test('Pronouns topic: fill-blank and translation for pronoun KPs have usable prompts+answers', () => {
  const { Exercises } = loadTrainer();
  const a1 = loadLevel('a1');
  const pronouns = findTopic(a1, 'a1-grammar-personal-pronouns');
  assert.ok(pronouns, 'pronouns topic must exist');

  for (const kp of pronouns.knowledge_points) {
    // Difficulty 2 picks fill-blank in current engine logic.
    const ex = withSeed(7, () =>
      Exercises.generateExercise(kp, pronouns.exercise_templates, 2, pronouns.knowledge_points)
    );
    assert.ok(ex.prompt && !PLACEHOLDER_RE.test(ex.prompt),
      `Bad prompt for pronoun KP ${kp.id}: "${ex.prompt}"`);
    if (ex.type === 'fill-blank' || ex.type === 'translation' || ex.type === 'multiple-choice') {
      assert.ok(ex.correctAnswer && ex.correctAnswer.length > 0,
        `Empty correctAnswer for pronoun KP ${kp.id} (type=${ex.type})`);
    }
  }
});

test('Grammar-rule KPs in sein topic never pick the conjugation template', () => {
  const { Exercises } = loadTrainer();
  const a1 = loadLevel('a1');
  const sein = findTopic(a1, 'a1-grammar-verb-sein');
  const grammarRuleKPs = sein.knowledge_points.filter(kp => kp.prompt_data.type === 'grammar-rule');
  assert.ok(grammarRuleKPs.length > 0, 'test precondition: grammar-rule KPs exist in sein');

  for (const kp of grammarRuleKPs) {
    for (let difficulty = 0; difficulty <= 5; difficulty++) {
      for (let seed = 1; seed <= 10; seed++) {
        const ex = withSeed(seed, () =>
          Exercises.generateExercise(kp, sein.exercise_templates, difficulty, sein.knowledge_points)
        );
        assert.ok(!PLACEHOLDER_RE.test(ex.prompt || ''),
          `Grammar-rule KP ${kp.id} produced unresolved placeholder: "${ex.prompt}"`);
      }
    }
  }
});
