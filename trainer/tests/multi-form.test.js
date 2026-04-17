'use strict';

const test   = require('node:test');
const assert = require('node:assert/strict');
const { loadTrainer, loadLevel, flattenTopics } = require('./_harness');

function withSeed(seed, fn) {
  const orig = Math.random;
  let s = seed;
  Math.random = () => { s = (s * 1664525 + 1013904223) >>> 0; return s / 0x100000000; };
  try { return fn(); } finally { Math.random = orig; }
}

function findKP(level, topicId, kpId) {
  const topic = flattenTopics(loadLevel(level)).find(t => t.id === topicId);
  return { topic, kp: topic.knowledge_points.find(k => k.id === kpId) };
}

test('fill-blank on "sie/Sie" pronoun blanks the form inside the sentence (not appended)', () => {
  const { Exercises } = loadTrainer();
  const { topic, kp } = findKP('a1', 'a1-grammar-personal-pronouns', 'a1-gram-pronouns-kp-sie-they');
  // Force fill-blank by using difficulty 2 (and the only applicable fill-blank
  // template for pronouns is fill-blank-pronoun now).
  let ex;
  for (let seed = 1; seed <= 10 && (!ex || ex.type !== 'fill-blank'); seed++) {
    ex = withSeed(seed, () =>
      Exercises.generateExercise(kp, topic.exercise_templates, 2, topic.knowledge_points));
  }
  assert.equal(ex.type, 'fill-blank', 'expected a fill-blank exercise for this run');
  assert.ok(ex.prompt.indexOf('______') !== -1, 'prompt must contain a blank');
  assert.ok(!/\(______\)\s*$/.test(ex.prompt),
    `blank must not be appended at the end — got "${ex.prompt}"`);
  assert.ok(ex.prompt.indexOf('kommen aus Deutschland') !== -1,
    `expected example sentence to be present — got "${ex.prompt}"`);
});

test('fill-blank on "sie/Sie" accepts either "Sie" or "sie" (form actually in the sentence)', () => {
  const { Exercises } = loadTrainer();
  const { topic, kp } = findKP('a1', 'a1-grammar-personal-pronouns', 'a1-gram-pronouns-kp-sie-they');
  let ex;
  for (let seed = 1; seed <= 10 && (!ex || ex.type !== 'fill-blank'); seed++) {
    ex = withSeed(seed, () =>
      Exercises.generateExercise(kp, topic.exercise_templates, 2, topic.knowledge_points));
  }
  assert.equal(ex.type, 'fill-blank');

  const sie   = Exercises.validateAnswer(ex, 'Sie');
  const sieLC = Exercises.validateAnswer(ex, 'sie');
  const full  = Exercises.validateAnswer(ex, 'sie/Sie');
  assert.equal(sie.correct,   true, '"Sie" should be accepted');
  assert.equal(sieLC.correct, true, '"sie" should be accepted');
  assert.equal(full.correct,  true, '"sie/Sie" should be accepted');
});

test('fill-blank displayed correctAnswer is the form that actually appears in the sentence', () => {
  const { Exercises } = loadTrainer();
  const { topic, kp } = findKP('a1', 'a1-grammar-personal-pronouns', 'a1-gram-pronouns-kp-sie-they');
  let ex;
  for (let seed = 1; seed <= 10 && (!ex || ex.type !== 'fill-blank'); seed++) {
    ex = withSeed(seed, () =>
      Exercises.generateExercise(kp, topic.exercise_templates, 2, topic.knowledge_points));
  }
  assert.equal(ex.type, 'fill-blank');
  assert.equal(ex.correctAnswer, 'Sie',
    `expected the displayed correctAnswer to be "Sie" (the form in the sentence), got "${ex.correctAnswer}"`);
});

test('catalog-wide: fill-blank prompts never have a trailing "(______)" appended', () => {
  const { Exercises } = loadTrainer();
  for (const level of ['a1', 'a2']) {
    for (const topic of flattenTopics(loadLevel(level))) {
      for (const kp of topic.knowledge_points) {
        if (!kp.prompt_data || !kp.prompt_data.example_sentence) continue;
        for (let difficulty = 0; difficulty <= 5; difficulty++) {
          for (let seed = 1; seed <= 3; seed++) {
            const ex = withSeed(seed, () =>
              Exercises.generateExercise(kp, topic.exercise_templates, difficulty, topic.knowledge_points));
            if (ex.type !== 'fill-blank') continue;
            assert.ok(!/\(______\)\s*$/.test(ex.prompt),
              `Trailing blank in ${topic.id}/${kp.id}: "${ex.prompt}"`);
          }
        }
      }
    }
  }
});
