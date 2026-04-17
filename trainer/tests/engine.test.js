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

test('getTopicProgressScore: returns 0 for untouched KPs', () => {
  const { Engine } = loadTrainer();
  const states = [
    { ease_factor: 2.5, interval_days: 0, next_review: null, correct_streak: 0, total_correct: 0, total_attempts: 0 },
    { ease_factor: 2.5, interval_days: 0, next_review: null, correct_streak: 0, total_correct: 0, total_attempts: 0 }
  ];
  assert.equal(Engine.getTopicProgressScore(states), 0);
});

test('getTopicProgressScore: gives partial credit for in-progress KPs', () => {
  const { Engine } = loadTrainer();
  // 1 KP with streak=1 (1/3 credit), 1 KP untouched (0 credit) → 1/6 ≈ 0.167
  const states = [
    { ease_factor: 2.5, interval_days: 1, next_review: null, correct_streak: 1, total_correct: 1, total_attempts: 1 },
    { ease_factor: 2.5, interval_days: 0, next_review: null, correct_streak: 0, total_correct: 0, total_attempts: 0 }
  ];
  const score = Engine.getTopicProgressScore(states);
  assert.ok(score > 0, 'in-progress topic should show non-zero progress');
  assert.ok(score < 1, 'in-progress topic should not show 100%');
  // streak=1 KP contributes 1/3, untouched contributes 0 → average = 1/6
  assert.equal(Math.round(score * 1000) / 1000, Math.round((1 / 6) * 1000) / 1000);
});

test('getTopicProgressScore: mastered KP contributes 1.0', () => {
  const { Engine } = loadTrainer();
  // Both KPs mastered (interval_days >= 7)
  const states = [
    { ease_factor: 2.5, interval_days: 15, next_review: '2099-01-01', correct_streak: 3, total_correct: 3, total_attempts: 3 },
    { ease_factor: 2.5, interval_days: 15, next_review: '2099-01-01', correct_streak: 3, total_correct: 3, total_attempts: 3 }
  ];
  assert.equal(Engine.getTopicProgressScore(states), 1);
});

test('getTopicProgressScore: matches getTopicMasteryScore when all KPs are mastered', () => {
  const { Engine } = loadTrainer();
  const states = [
    { ease_factor: 2.5, interval_days: 10, next_review: '2099-01-01', correct_streak: 3, total_correct: 3, total_attempts: 3 }
  ];
  assert.equal(Engine.getTopicProgressScore(states), Engine.getTopicMasteryScore(states));
});
