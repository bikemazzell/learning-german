'use strict';

const test   = require('node:test');
const assert = require('node:assert/strict');
const fs     = require('node:fs');
const path   = require('node:path');
const { loadLevel, flattenTopics } = require('./_harness');

function loadTemplates() {
  const base = path.join(__dirname, '..', 'data', 'templates');
  const g = JSON.parse(fs.readFileSync(path.join(base, 'grammar.json'), 'utf8')).templates || [];
  const v = JSON.parse(fs.readFileSync(path.join(base, 'vocab.json'),   'utf8')).templates || [];
  const byId = {};
  for (const t of g.concat(v)) byId[t.id] = t;
  return byId;
}

test('every topic has at least one applicable template per KP type', () => {
  const templates = loadTemplates();

  for (const lvl of ['a1', 'a2']) {
    const topics = flattenTopics(loadLevel(lvl));
    for (const topic of topics) {
      const kpTypes = new Set(
        topic.knowledge_points.map(kp => kp.prompt_data && kp.prompt_data.type)
      );
      for (const kt of kpTypes) {
        const applicable = (topic.exercise_templates || [])
          .map(tid => templates[tid])
          .filter(t => t && (!t.applicable_kp_types || t.applicable_kp_types.indexOf(kt) !== -1));
        assert.ok(
          applicable.length > 0,
          `${lvl}/${topic.id}: no template applies to KP type "${kt}"`
        );
      }
    }
  }
});

test('every topic exercise_templates id resolves to a known template', () => {
  const templates = loadTemplates();

  for (const lvl of ['a1', 'a2']) {
    for (const topic of flattenTopics(loadLevel(lvl))) {
      for (const tid of topic.exercise_templates || []) {
        assert.ok(templates[tid],
          `${lvl}/${topic.id}: references unknown template "${tid}"`);
      }
    }
  }
});
