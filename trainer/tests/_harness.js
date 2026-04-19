/**
 * Minimal harness to load the browser IIFE modules under Node for testing.
 * Each module attaches itself to `window.<Name>`; we shim `window` and a tiny
 * `localStorage`, then `vm.runInThisContext` the source so it installs onto
 * our shared globals.
 */
'use strict';

const fs   = require('fs');
const path = require('path');
const vm   = require('vm');

const TRAINER_DIR = path.join(__dirname, '..');
const JS_DIR      = path.join(TRAINER_DIR, 'js');
const DATA_DIR    = path.join(TRAINER_DIR, 'data');

function makeLocalStorage() {
  const store = {};
  return {
    _store: store,
    getItem(k)      { return Object.prototype.hasOwnProperty.call(store, k) ? store[k] : null; },
    setItem(k, v)   { store[k] = String(v); },
    removeItem(k)   { delete store[k]; },
    clear()         { for (const k of Object.keys(store)) delete store[k]; },
    key(i)          { return Object.keys(store)[i] || null; },
    get length()    { return Object.keys(store).length; }
  };
}

function loadTrainer() {
  const ls  = makeLocalStorage();

  // Shared sandbox so all IIFE files see the same `window`/`localStorage`.
  // Use a Proxy-window whose assignments propagate to the context globals so
  // bare references like `Progress` (used in recommender.js) resolve the same
  // way they do in the browser, where `window.Foo = ...` also creates a global.
  const sandbox = {
    localStorage: ls,
    Math, Date, JSON, Object, Array, String, Number, Boolean,
    console, setTimeout, clearTimeout, isNaN, parseInt, parseFloat
  };
  const ctx = vm.createContext(sandbox);
  // Build `window` proxy AFTER ctx exists, so it can write back into the sandbox.
  const win = new Proxy({}, {
    set(_t, key, value) { sandbox[key] = value; return true; },
    get(_t, key)        { return sandbox[key]; },
    has(_t, key)        { return key in sandbox; }
  });
  sandbox.window = win;

  const files = ['progress.js', 'engine.js', 'recommender.js', 'exercises.js', 'exam.js'];
  for (const f of files) {
    const code = fs.readFileSync(path.join(JS_DIR, f), 'utf8');
    vm.runInContext(code, ctx, { filename: f });
  }

  // Load template JSON synchronously and inject into Exercises without using fetch.
  const grammar = JSON.parse(fs.readFileSync(path.join(DATA_DIR, 'templates/grammar.json'), 'utf8'));
  const vocab   = JSON.parse(fs.readFileSync(path.join(DATA_DIR, 'templates/vocab.json'),   'utf8'));

  // Monkey-patch loadTemplates to resolve synchronously from injected JSON.
  const origLoad = win.Exercises.loadTemplates;
  win.Exercises.loadTemplates = function () {
    // Re-run the original internals by re-evaluating the array assignment.
    // Simpler: set a global fetch for this one call.
    return Promise.resolve();
  };
  // Populate template stores by re-running exercises.js bootstrap with our data.
  // The original closure is inaccessible — instead, call a small shim exposed
  // by our modified exercises.js (see `__setTemplates` added for tests).
  if (typeof win.Exercises.__setTemplates === 'function') {
    win.Exercises.__setTemplates(grammar.templates || [], vocab.templates || []);
  } else {
    throw new Error('Exercises.__setTemplates missing — add a test hook to exercises.js.');
  }

  return {
    window: win,
    localStorage: ls,
    Progress:    sandbox.Progress,
    Engine:      sandbox.Engine,
    Recommender: sandbox.Recommender,
    Exercises:   sandbox.Exercises,
    Exam:        sandbox.Exam
  };
}

function loadLevel(levelId) {
  return JSON.parse(
    fs.readFileSync(path.join(DATA_DIR, 'levels', levelId + '.json'), 'utf8')
  );
}

function flattenTopics(levelData) {
  const out = [];
  for (const d of levelData.domains || []) {
    for (const t of d.topics || []) {
      t._domain = d.id;
      t._domainName = d.name;
      out.push(t);
    }
  }
  return out;
}

module.exports = { loadTrainer, loadLevel, flattenTopics };
