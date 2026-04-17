'use strict';

const test   = require('node:test');
const assert = require('node:assert/strict');
const { loadTrainer } = require('./_harness');

test('SM-2: 3 consecutive corrects reach interval >= 7 (mastered)', () => {
  const { Engine } = loadTrainer();

  let s = {
    ease_factor: 2.5, interval_days: 0, next_review: null,
    correct_streak: 0, total_correct: 0, total_attempts: 0
  };
  s = Engine.sm2Update(s, true);
  assert.equal(s.correct_streak, 1);
  assert.equal(s.interval_days, 1);

  s = Engine.sm2Update(s, true);
  assert.equal(s.correct_streak, 2);
  assert.equal(s.interval_days, 6);

  s = Engine.sm2Update(s, true);
  assert.equal(s.correct_streak, 3);
  assert.ok(s.interval_days >= 7, 'interval should cross mastery threshold after 3rd correct');
  assert.ok(Engine.isKPMastered(s), 'KP should be classified mastered');
});

test('SM-2: incorrect resets streak and interval', () => {
  const { Engine } = loadTrainer();
  let s = {
    ease_factor: 2.5, interval_days: 6, next_review: '2099-01-01',
    correct_streak: 2, total_correct: 2, total_attempts: 2
  };
  s = Engine.sm2Update(s, false);
  assert.equal(s.correct_streak, 0);
  assert.equal(s.interval_days, 1);
  assert.ok(s.ease_factor >= 1.3);
});

test('getTopicState: returns "learning" when some KPs attempted but none mastered', () => {
  const { Engine } = loadTrainer();
  const states = [
    { ease_factor: 2.5, interval_days: 1, next_review: null, correct_streak: 1, total_correct: 1, total_attempts: 1 },
    { ease_factor: 2.5, interval_days: 0, next_review: null, correct_streak: 0, total_correct: 0, total_attempts: 0 }
  ];
  assert.equal(Engine.getTopicState(Engine.getTopicMasteryScore(states), states), 'learning');
});
