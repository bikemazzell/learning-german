'use strict';

const test   = require('node:test');
const assert = require('node:assert/strict');
const { loadTrainer, loadLevel, flattenTopics } = require('./_harness');

/**
 * Full-catalog smoke test: for every topic in A1 and A2, simulate three
 * perfect sessions and verify the topic becomes mastered. This is the end-to-
 * end regression guard against template/KP-type drift that used to leave
 * learners permanently stuck (e.g. the Pronouns fill-blank bug).
 */
function simulateSession(deps, level, topic) {
  const { Progress, Engine, Exercises } = deps;
  const answerableTypes = new Set(['multiple-choice', 'fill-blank', 'translation']);

  for (const kp of topic.knowledge_points) {
    const state = Progress.getKPState(level, kp.id);
    const difficulty = state.correct_streak || 0;
    const ex = Exercises.generateExercise(
      kp, topic.exercise_templates, difficulty, topic.knowledge_points
    );
    assert.ok(ex, `exercise must be generated for ${topic.id}/${kp.id}`);

    if (answerableTypes.has(ex.type)) {
      assert.ok(
        typeof ex.correctAnswer === 'string' && ex.correctAnswer.length > 0,
        `Empty correctAnswer for ${topic.id}/${kp.id} at difficulty ${difficulty} (type ${ex.type})`
      );
      const result = Exercises.validateAnswer(ex, ex.correctAnswer);
      assert.equal(
        result.correct, true,
        `validateAnswer rejected the template's own correctAnswer for ${topic.id}/${kp.id}`
      );
    }

    Progress.updateKPState(level, kp.id, Engine.sm2Update(state, true));
  }
}

for (const levelId of ['a1', 'a2']) {
  const topics = flattenTopics(loadLevel(levelId));
  for (const topic of topics) {
    test(`${levelId.toUpperCase()} / ${topic.id}: reaches mastery in 3 perfect sessions`, () => {
      const deps = loadTrainer();
      simulateSession(deps, levelId, topic);
      simulateSession(deps, levelId, topic);
      simulateSession(deps, levelId, topic);

      const states = topic.knowledge_points.map(kp =>
        deps.Progress.getKPState(levelId, kp.id)
      );
      const score = deps.Engine.getTopicMasteryScore(states);
      assert.ok(
        score >= 0.85,
        `${topic.id} mastery score after 3 perfect sessions is ${score}`
      );
    });
  }
}
