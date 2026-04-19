'use strict';

const fs = require('node:fs');
const path = require('node:path');
const test = require('node:test');
const assert = require('node:assert/strict');
const { loadLevel, flattenTopics } = require('./_harness');

const ROOT = path.join(__dirname, '..', '..');

function allKPs() {
  const out = [];
  for (const levelId of ['a1', 'a2']) {
    for (const topic of flattenTopics(loadLevel(levelId))) {
      for (const kp of topic.knowledge_points || []) {
        out.push({ levelId, topicId: topic.id, kp });
      }
    }
  }
  return out;
}

function label(item, field) {
  return `${item.levelId}/${item.topicId}/${item.kp.id}/${field}`;
}

function looksLikeGermanExample(text) {
  if (!text) return false;
  const s = String(text).trim();
  if (!/[.!?]$/.test(s)) return false;
  if (/\b(to|the|a|an|and|or|for|from|with|without|in|on|at)\b/i.test(s)) return false;
  return /^(ich|du|er|sie|wir|ihr|der|die|das|ein|eine|einen|einem|dem|den|mein|meine|wie|was|wo|wann|warum|bitte|sehr|heute|morgen|hier|dort|unter|seit|bei|mir)\b/i.test(s);
}

test('vocabulary English fields contain translations, not German example sentences', () => {
  const bad = [];
  for (const item of allKPs()) {
    const pd = item.kp.prompt_data || {};
    if (pd.type !== 'vocabulary') continue;
    if (looksLikeGermanExample(pd.english)) {
      bad.push(`${label(item, 'english')} = ${JSON.stringify(pd.english)}`);
    }
  }

  assert.deepEqual(bad, []);
});

test('catalog has no visible import TODOs or Goethe PDF metadata fragments', () => {
  const bad = [];
  const fragmentPattern = /TODO:|Goethe-Zertifikat|zugrunde|vorliegenden Wortschatz|Niveaustufe|schriftlichen Einwilligung|Modellsatz|2002\.|Erziehungs direktoren|Bedeu-/;

  for (const item of allKPs()) {
    const pd = item.kp.prompt_data || {};
    for (const [field, value] of Object.entries(pd)) {
      if (typeof value === 'string' && fragmentPattern.test(value)) {
        bad.push(`${label(item, field)} = ${JSON.stringify(value)}`);
      }
    }
  }

  assert.deepEqual(bad, []);
});

test('vocabulary example sentences are not English translation placeholders', () => {
  const bad = [];

  for (const item of allKPs()) {
    const pd = item.kp.prompt_data || {};
    if (pd.type !== 'vocabulary') continue;
    if (!pd.example_sentence) continue;
    if (String(pd.example_sentence).trim() === String(pd.english || '').trim()) {
      bad.push(`${label(item, 'example_sentence')} duplicates English translation`);
    }
  }

  assert.deepEqual(bad, []);
});

test('A1 food topic does not contain obvious work, travel, clothing, or body-part imports', () => {
  const food = flattenTopics(loadLevel('a1')).find(t => t.id === 'a1-vocab-food');
  assert.ok(food, 'A1 food topic exists');

  const misplaced = new Set([
    'a1-vocab-food-kp-arbeiten',
    'a1-vocab-food-kp-arbeitslos',
    'a1-vocab-food-kp-aussteigen',
    'a1-vocab-food-kp-arm',
    'a1-vocab-food-kp-bein',
    'a1-vocab-food-kp-bein---e',
    'a1-vocab-food-kp-kleidung'
  ]);

  assert.deepEqual(
    food.knowledge_points.filter(kp => misplaced.has(kp.id)).map(kp => kp.id),
    []
  );
});

test('A2 dative case includes plural article and plural noun ending coverage', () => {
  const dativeTopic = flattenTopics(loadLevel('a2')).find(t => t.id === 'a2-grammar-dative-case');
  assert.ok(dativeTopic, 'A2 dative case topic exists');

  const hasPluralArticle = dativeTopic.knowledge_points.some(kp => {
    const pd = kp.prompt_data || {};
    return pd.correct_form === 'den' && /plural/i.test(`${pd.english} ${pd.rule} ${kp.explanation}`);
  });
  const hasPluralNounEnding = dativeTopic.knowledge_points.some(kp => {
    const text = `${kp.prompt_data?.rule || ''} ${kp.prompt_data?.example_sentence || ''} ${kp.explanation || ''}`;
    return /\bKindern\b/.test(text) && /plural|n\b/i.test(text);
  });

  assert.equal(hasPluralArticle, true);
  assert.equal(hasPluralNounEnding, true);
});

test('A1 wir pronoun explanation is not overgeneralized to all verbs', () => {
  const pronouns = flattenTopics(loadLevel('a1')).find(t => t.id === 'a1-grammar-personal-pronouns');
  const wir = pronouns.knowledge_points.find(kp => kp.id === 'a1-gram-pronouns-kp-wir');

  assert.ok(wir);
  assert.doesNotMatch(wir.explanation, /always takes the same verb form as the infinitive/i);
  assert.match(wir.explanation, /regular present-tense verbs/i);
});

test('README content counts match the current catalog', () => {
  const readme = fs.readFileSync(path.join(ROOT, 'README.md'), 'utf8');
  const a1KPs = allKPs().filter(x => x.levelId === 'a1').length;
  const a2KPs = allKPs().filter(x => x.levelId === 'a2').length;
  const totalKPs = a1KPs + a2KPs;

  assert.match(readme, new RegExp(`Knowledge points \\| ${a1KPs} \\| ${a2KPs} \\| ${totalKPs} \\|`));
  assert.match(readme, new RegExp(`Knowledge graph\\*\\* with 55 topics and ${totalKPs} knowledge points`));
  assert.match(readme, new RegExp(`a1\\.json\\s+# A1 knowledge graph \\(30 topics, ${a1KPs} KPs\\)`));
  assert.match(readme, new RegExp(`a2\\.json\\s+# A2 knowledge graph \\(25 topics, ${a2KPs} KPs\\)`));
});
