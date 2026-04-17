'use strict';

const test   = require('node:test');
const assert = require('node:assert/strict');
const { loadTrainer, loadLevel, flattenTopics } = require('./_harness');

function simulatePerfectSession(deps, level, topicId) {
  const { Progress, Engine, Exercises } = deps;
  const topics = flattenTopics(loadLevel(level));
  const topic = topics.find(t => t.id === topicId);
  const kps = topic.knowledge_points;

  // For every KP in the topic: read state, simulate a correct answer, save.
  for (const kp of kps) {
    const state = Progress.getKPState(level, kp.id);
    const difficulty = state.correct_streak || 0;
    const ex = Exercises.generateExercise(kp, topic.exercise_templates, difficulty, kps);

    // We require the generated exercise to be answerable.
    const typesWithAnswer = new Set(['multiple-choice', 'fill-blank', 'translation']);
    assert.ok(ex, 'exercise must be generated');
    if (typesWithAnswer.has(ex.type)) {
      assert.ok(ex.correctAnswer && ex.correctAnswer.length > 0,
        `Broken exercise for ${kp.id} at difficulty ${difficulty} (type ${ex.type})`);
      const result = Exercises.validateAnswer(ex, ex.correctAnswer);
      assert.equal(result.correct, true, `Correct answer rejected for ${kp.id}`);
    }

    const newState = Engine.sm2Update(state, true);
    Progress.updateKPState(level, kp.id, newState);
  }
}

function topicMasteryScore(deps, level, topic) {
  const states = topic.knowledge_points.map(kp => deps.Progress.getKPState(level, kp.id));
  return deps.Engine.getTopicMasteryScore(states);
}

test('Pronouns topic reaches full mastery after 3 perfect sessions', () => {
  const deps = loadTrainer();
  const level = 'a1';
  const topic = flattenTopics(loadLevel(level)).find(t => t.id === 'a1-grammar-personal-pronouns');

  assert.equal(topicMasteryScore(deps, level, topic), 0, 'starts un-mastered');

  simulatePerfectSession(deps, level, topic.id);
  simulatePerfectSession(deps, level, topic.id);
  simulatePerfectSession(deps, level, topic.id);

  const score = topicMasteryScore(deps, level, topic);
  assert.ok(score >= 0.85,
    `after 3 perfect sessions Pronouns should be mastered, got ${score}`);
});

test('Recommender unblocks "sein" after Pronouns is mastered', () => {
  const deps = loadTrainer();
  const { Recommender } = deps;
  const level = 'a1';
  const topics = flattenTopics(loadLevel(level));

  // Before mastery, sein requires pronouns prereq.
  const before = Recommender.checkPrerequisites('a1-grammar-verb-sein', topics, level);
  assert.equal(before.met, false,
    'Expected sein prereq to be unmet before any practice');

  // Master pronouns.
  simulatePerfectSession(deps, level, 'a1-grammar-personal-pronouns');
  simulatePerfectSession(deps, level, 'a1-grammar-personal-pronouns');
  simulatePerfectSession(deps, level, 'a1-grammar-personal-pronouns');

  const after = Recommender.checkPrerequisites('a1-grammar-verb-sein', topics, level);
  assert.equal(after.met, true,
    'Expected sein prereq to be met once Pronouns is mastered');
});

test('Recommender advances to next new topic once in-progress topic reaches 80%', () => {
  // Scenario from bug report: Pronouns (88%) and sein (86%) are mastered,
  // haben is in progress at some level. Once haben reaches >= 80%, the
  // recommender should suggest the next new topic rather than staying on haben.
  const deps = loadTrainer();
  const { Recommender } = deps;
  const level = 'a1';
  const topics = flattenTopics(loadLevel(level));

  // Fully master Pronouns and sein so their dependents are unlocked.
  for (let i = 0; i < 3; i++) {
    simulatePerfectSession(deps, level, 'a1-grammar-personal-pronouns');
    simulatePerfectSession(deps, level, 'a1-grammar-verb-sein');
  }
  // Do two perfect sessions on haben — enough to push most KPs to mastered,
  // bringing the topic score above 80%.
  simulatePerfectSession(deps, level, 'a1-grammar-verb-haben');
  simulatePerfectSession(deps, level, 'a1-grammar-verb-haben');
  simulatePerfectSession(deps, level, 'a1-grammar-verb-haben');

  const habenTopic = topics.find(t => t.id === 'a1-grammar-verb-haben');
  const habenScore = topicMasteryScore(deps, level, habenTopic);
  assert.ok(habenScore >= 0.8,
    `haben should be >= 80% after 3 perfect sessions, got ${Math.round(habenScore * 100)}%`);

  const rec = Recommender.getRecommendation(topics, level);
  assert.notEqual(rec.topicId, 'a1-grammar-verb-haben',
    `Recommender should advance past haben (${Math.round(habenScore * 100)}%) to a new topic, got: ${rec.topicId}`);
  assert.ok(['new_topic', 'continue'].includes(rec.action),
    `Expected new_topic or continue action, got: ${rec.action}`);
});

test('Recommender continues lowest-mastery topic when multiple topics are in progress', () => {
  const deps = loadTrainer();
  const { Recommender } = deps;
  const level = 'a1';
  const topics = flattenTopics(loadLevel(level));

  // Unlock both sein and haben.
  for (let i = 0; i < 3; i++) simulatePerfectSession(deps, level, 'a1-grammar-personal-pronouns');

  // Give sein 3 sessions (interval_days reaches >=7 for most KPs → mastered)
  // and haben only 1 session (interval_days=1, not mastered).
  for (let i = 0; i < 3; i++) simulatePerfectSession(deps, level, 'a1-grammar-verb-sein');
  simulatePerfectSession(deps, level, 'a1-grammar-verb-haben');

  const seinScore  = topicMasteryScore(deps, level, topics.find(t => t.id === 'a1-grammar-verb-sein'));
  const habenScore = topicMasteryScore(deps, level, topics.find(t => t.id === 'a1-grammar-verb-haben'));

  // After 3 sessions sein should be mastered (>= 85%); haben should still be low.
  assert.ok(seinScore >= 0.85,
    `sein should be mastered after 3 perfect sessions, got ${Math.round(seinScore * 100)}%`);
  assert.ok(habenScore < 0.8,
    `haben should be below 80% after 1 session, got ${Math.round(habenScore * 100)}%`);

  // Now sein is 'mastered' (not 'learning'), so only haben is in-progress.
  const rec = Recommender.getRecommendation(topics, level);
  assert.equal(rec.topicId, 'a1-grammar-verb-haben',
    `Expected recommender to recommend the remaining in-progress topic (haben), got ${rec.topicId}`);
});
