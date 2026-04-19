'use strict';

const fs = require('node:fs');
const path = require('node:path');
const test = require('node:test');
const assert = require('node:assert/strict');

const DATA_DIR = path.join(__dirname, '..', 'data', 'exam');

function loadExam(level) {
  return JSON.parse(fs.readFileSync(path.join(DATA_DIR, level + '.json'), 'utf8'));
}

function getSection(exam, skill) {
  return exam.sections.find(section => section.skill === skill);
}

function assertNonEmptyString(value, label) {
  assert.equal(typeof value, 'string', label);
  assert.ok(value.trim().length > 0, label);
}

for (const level of ['a1', 'a2']) {
  test(`${level.toUpperCase()} exam data has adult reading and writing sections`, () => {
    const exam = loadExam(level);

    assert.equal(exam.level, level.toUpperCase());
    assert.equal(exam.variant, 'adult');
    assert.ok(Array.isArray(exam.sections));

    const reading = getSection(exam, 'reading');
    const writing = getSection(exam, 'writing');
    assert.ok(reading, 'reading section exists');
    assert.ok(writing, 'writing section exists');

    assert.equal(reading.duration_minutes, level === 'a1' ? 25 : 30);
    assert.equal(writing.duration_minutes, level === 'a1' ? 20 : 30);
    assert.equal(reading.tasks.length, 12);
    assert.equal(writing.tasks.length, 12);
  });

  test(`${level.toUpperCase()} reading tasks are objectively answerable`, () => {
    const reading = getSection(loadExam(level), 'reading');
    const partIds = new Set(reading.tasks.map(task => task.part));

    for (const required of ['short-note', 'ad', 'sign', 'info-board']) {
      assert.ok(partIds.has(required), `missing reading part ${required}`);
    }

    for (const task of reading.tasks) {
      assertNonEmptyString(task.id, 'task.id');
      assertNonEmptyString(task.title, `${task.id}.title`);
      assertNonEmptyString(task.instruction, `${task.id}.instruction`);
      assertNonEmptyString(task.text, `${task.id}.text`);
      assert.ok(Array.isArray(task.questions) && task.questions.length >= 3, `${task.id}.questions`);

      for (const question of task.questions) {
        assertNonEmptyString(question.id, `${task.id}.question.id`);
        assertNonEmptyString(question.prompt, `${task.id}.${question.id}.prompt`);
        assert.ok(Array.isArray(question.options) && question.options.length === 3, `${task.id}.${question.id}.options`);
        assert.ok(question.options.includes(question.answer), `${task.id}.${question.id}.answer in options`);
        assertNonEmptyString(question.explanation, `${task.id}.${question.id}.explanation`);
      }
    }
  });

  test(`${level.toUpperCase()} writing tasks provide self-review guidance`, () => {
    const writing = getSection(loadExam(level), 'writing');
    const partIds = new Set(writing.tasks.map(task => task.part));
    const expectedParts = level === 'a1'
      ? ['form-fill', 'short-text']
      : ['sms', 'email'];

    for (const required of expectedParts) {
      assert.ok(partIds.has(required), `missing writing part ${required}`);
    }

    for (const task of writing.tasks) {
      assertNonEmptyString(task.id, 'task.id');
      assertNonEmptyString(task.title, `${task.id}.title`);
      assertNonEmptyString(task.situation, `${task.id}.situation`);
      assert.ok(Array.isArray(task.bullets) && task.bullets.length === 3, `${task.id}.bullets`);
      assert.ok(Array.isArray(task.requirements) && task.requirements.length >= 2, `${task.id}.requirements`);
      assert.ok(Array.isArray(task.useful_phrases) && task.useful_phrases.length >= 3, `${task.id}.useful_phrases`);
      assert.ok(Array.isArray(task.self_review) && task.self_review.length >= 3, `${task.id}.self_review`);
      assert.ok(task.word_count.min > 0, `${task.id}.word_count.min`);
      assert.ok(task.word_count.target >= task.word_count.min, `${task.id}.word_count.target`);
      assert.ok(task.word_count.max >= task.word_count.target, `${task.id}.word_count.max`);
    }
  });
}
