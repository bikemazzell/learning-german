'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const { loadTrainer } = require('./_harness');

test('scores reading answers by question id', () => {
  const { Exam } = loadTrainer();
  const task = {
    questions: [
      { id: 'q1', prompt: 'First?', answer: 'a', explanation: 'A is stated in the text.' },
      { id: 'q2', prompt: 'Second?', answer: 'b', explanation: 'B is the only matching option.' },
      { id: 'q3', prompt: 'Third?', answer: 'c', explanation: 'C matches the notice.' }
    ]
  };

  const result = Exam.scoreReadingTask(task, { q1: 'a', q2: 'x', q3: 'c' });

  assert.deepEqual(JSON.parse(JSON.stringify(result)), {
    correct: 2,
    total: 3,
    percent: 67,
    details: [
      { questionId: 'q1', prompt: 'First?', correct: true, answer: 'a', givenAnswer: 'a', explanation: 'A is stated in the text.' },
      { questionId: 'q2', prompt: 'Second?', correct: false, answer: 'b', givenAnswer: 'x', explanation: 'B is the only matching option.' },
      { questionId: 'q3', prompt: 'Third?', correct: true, answer: 'c', givenAnswer: 'c', explanation: 'C matches the notice.' }
    ]
  });
});

test('counts German writing words with punctuation and newlines', () => {
  const { Exam } = loadTrainer();

  assert.equal(Exam.countWords('Sehr geehrte Damen und Herren,\nich brauche Informationen.'), 8);
  assert.equal(Exam.countWords(''), 0);
  assert.equal(Exam.countWords('  Ich komme um 18 Uhr.  '), 5);
});

test('stores exam progress separately and never stores writing text', () => {
  const { Exam, localStorage } = loadTrainer();

  Exam.recordReadingResult('a2', 'a2-reading-email-001', { correct: 2, total: 3, percent: 67 });
  Exam.recordWritingPractice('a2', 'a2-writing-sms-001', 'Entschuldigung, ich komme später.');

  assert.equal(localStorage.getItem('trainer-progress-a2'), null);
  const stored = JSON.parse(localStorage.getItem('trainer-exam-practice'));
  assert.deepEqual(stored.a2.reading.completedTaskIds, ['a2-reading-email-001']);
  assert.equal(stored.a2.reading.totalCorrect, 2);
  assert.equal(stored.a2.reading.totalQuestions, 3);
  assert.deepEqual(stored.a2.writing.completedTaskIds, ['a2-writing-sms-001']);
  assert.equal(JSON.stringify(stored).includes('Entschuldigung'), false);
});
