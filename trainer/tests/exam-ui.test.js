'use strict';

const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const test = require('node:test');
const assert = require('node:assert/strict');

const TRAINER_DIR = path.join(__dirname, '..');

function makeDocument() {
  return {
    createElement() {
      return {
        _text: '',
        appendChild(node) { this._text += node.text; },
        get innerHTML() {
          return this._text
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;');
        }
      };
    },
    createTextNode(text) {
      return { text: String(text) };
    }
  };
}

function loadUI() {
  const appEl = { innerHTML: '', querySelector() { return null; } };
  const sandbox = {
    window: {},
    document: makeDocument(),
    Progress: {
      getKPState() {
        return { interval_days: 0, total_attempts: 0, correct_streak: 0 };
      }
    },
    Engine: {
      getTopicMasteryScore() { return 0; },
      getTopicState() { return 'new'; },
      getTopicProgressScore() { return 0; }
    },
    Recommender: {
      getRecommendation() { return { action: 'all_done' }; },
      getDueReviews() { return []; },
      findTopic() { return null; },
      checkPrerequisites() { return { met: true, prereqs: [] }; }
    }
  };
  sandbox.window = sandbox;
  vm.runInNewContext(fs.readFileSync(path.join(TRAINER_DIR, 'js', 'ui.js'), 'utf8'), sandbox);
  sandbox.UI.init(appEl);
  return { UI: sandbox.UI, appEl };
}

test('index loads exam module before app boot code', () => {
  const html = fs.readFileSync(path.join(TRAINER_DIR, 'index.html'), 'utf8');
  assert.ok(html.indexOf('js/exam.js') > -1, 'exam.js script is included');
  assert.ok(html.indexOf('js/exam.js') < html.indexOf('js/app.js'), 'exam.js loads before app.js');
});

test('service worker precaches exam practice assets', () => {
  const sw = fs.readFileSync(path.join(TRAINER_DIR, 'sw.js'), 'utf8');

  assert.match(sw, /js\/exam\.js/);
  assert.match(sw, /data\/exam\/a1\.json/);
  assert.match(sw, /data\/exam\/a2\.json/);
});

test('dashboard includes an Exam Practice entry point', () => {
  const { UI, appEl } = loadUI();
  UI.renderDashboard({
    currentLevel: 'a1',
    allTopics: [],
    progress: {},
    examData: {},
    examProgress: {}
  });

  assert.match(appEl.innerHTML, /Exam Practice/);
  assert.match(appEl.innerHTML, /data-action="show-exam"/);
});

test('dashboard shows exam skills as first-class sections', () => {
  const { UI, appEl } = loadUI();
  UI.renderDashboard({
    currentLevel: 'a1',
    allTopics: [],
    progress: {},
    examData: {
      a1: {
        sections: [
          { skill: 'reading', name: 'Lesen', duration_minutes: 25, tasks: [{ id: 'r1' }, { id: 'r2' }] },
          { skill: 'writing', name: 'Schreiben', duration_minutes: 20, tasks: [{ id: 'w1' }] }
        ]
      }
    },
    examProgress: { a1: { reading: { completedTaskIds: ['r1'] }, writing: { completedTaskIds: [] } } }
  });

  assert.match(appEl.innerHTML, /Exam Practice/);
  assert.match(appEl.innerHTML, /Lesen/);
  assert.match(appEl.innerHTML, /Schreiben/);
  assert.match(appEl.innerHTML, /data-action="view-exam-section"/);
});

test('exam overview renders reading and writing sections', () => {
  const { UI, appEl } = loadUI();
  UI.renderExamOverview({
    currentLevel: 'a2',
    examData: {
      a2: {
        sections: [
          { id: 'a2-reading', skill: 'reading', name: 'Lesen', duration_minutes: 30, tasks: [{ id: 'r1' }] },
          { id: 'a2-writing', skill: 'writing', name: 'Schreiben', duration_minutes: 30, tasks: [{ id: 'w1' }] }
        ]
      }
    },
    examProgress: { a2: { reading: { completedTaskIds: [] }, writing: { completedTaskIds: [] } } }
  });

  assert.match(appEl.innerHTML, /Lesen/);
  assert.match(appEl.innerHTML, /Schreiben/);
  assert.match(appEl.innerHTML, /data-action="view-exam-section"/);
});

test('reading task view renders answer options and score action', () => {
  const { UI, appEl } = loadUI();
  UI.renderExamReadingTask({
    id: 'reading-1',
    title: 'Test Lesen',
    instruction: 'Lesen Sie.',
    text: 'Kurzer Text.',
    questions: [
      { id: 'q1', prompt: 'Frage?', options: ['a', 'b', 'c'], answer: 'a', explanation: 'x' }
    ]
  });

  assert.match(appEl.innerHTML, /Kurzer Text/);
  assert.match(appEl.innerHTML, /name="exam-q-q1"/);
  assert.match(appEl.innerHTML, /data-action="submit-exam-reading"/);
});

test('writing task view renders word guidance and self-review checklist', () => {
  const { UI, appEl } = loadUI();
  UI.renderExamWritingTask({
    id: 'writing-1',
    title: 'Test Schreiben',
    situation: 'Schreiben Sie eine E-Mail.',
    word_count: { min: 30, target: 35, max: 40 },
    bullets: ['Punkt 1', 'Punkt 2', 'Punkt 3'],
    requirements: ['Anrede', 'Gruß'],
    useful_phrases: ['Sehr geehrte Damen und Herren,', 'Mit freundlichen Grüßen', 'Bitte ...'],
    self_review: ['Alle Punkte?', 'Wortzahl?', 'Gruß?']
  });

  assert.match(appEl.innerHTML, /30-40 Wörter/);
  assert.match(appEl.innerHTML, /<textarea/);
  assert.match(appEl.innerHTML, /data-action="mark-exam-writing"/);
  assert.match(appEl.innerHTML, /Alle Punkte/);
});
