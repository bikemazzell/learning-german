'use strict';

const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const test = require('node:test');
const assert = require('node:assert/strict');

const TRAINER_DIR = path.join(__dirname, '..');

function makeDocument(elementsById) {
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
    },
    getElementById(id) {
      return elementsById[id] || null;
    }
  };
}

function makeClassList() {
  const classes = new Set();
  return {
    add(name) { classes.add(name); },
    contains(name) { return classes.has(name); }
  };
}

function makeOption(value) {
  return {
    style: {},
    classList: makeClassList(),
    getAttribute(name) {
      return name === 'data-value' ? value : null;
    }
  };
}

function loadUI(appEl, elementsById) {
  const sandbox = {
    window: {},
    document: makeDocument(elementsById),
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
  return sandbox.UI;
}

test('multiple-choice feedback marks the selected wrong option separately from the correct answer', () => {
  const feedbackArea = { innerHTML: '' };
  const options = [
    makeOption('fünf'),
    makeOption('hundert'),
    makeOption('einsteigen'),
    makeOption('die Postleitzahl')
  ];
  const appEl = {
    querySelector() { return null; },
    querySelectorAll(selector) {
      return selector === '.mc-option' ? options : [];
    }
  };

  const UI = loadUI(appEl, {
    'feedback-area': feedbackArea,
    'answer-input': null,
    'submit-btn': null
  });

  UI.showFeedback(
    {
      correct: false,
      selectedAnswer: 'hundert',
      correctAnswer: 'fünf',
      feedback: 'The correct answer is: fünf'
    },
    {
      type: 'multiple-choice',
      correctAnswer: 'fünf',
      explanation: ''
    }
  );

  assert.match(feedbackArea.innerHTML, /Incorrect/);
  assert.equal(options[0].classList.contains('correct'), true);
  assert.equal(options[1].classList.contains('incorrect'), true);
});
