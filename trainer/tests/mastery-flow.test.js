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
