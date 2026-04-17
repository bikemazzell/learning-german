window.Exercises = (function () {

  var grammarTemplates = [];
  var vocabTemplates = [];

  // ---------------------------------------------------------------------------
  // Template loading
  // ---------------------------------------------------------------------------

  function loadTemplates(basePath) {
    basePath = basePath || 'data/templates';
    return Promise.all([
      fetch(basePath + '/grammar.json').then(function (r) { return r.json(); }),
      fetch(basePath + '/vocab.json').then(function (r) { return r.json(); })
    ]).then(function (results) {
      grammarTemplates = results[0].templates || [];
      vocabTemplates = results[1].templates || [];
    });
  }

  function getAllTemplates() {
    return grammarTemplates.concat(vocabTemplates);
  }

  function findTemplate(templateId) {
    var all = getAllTemplates();
    for (var i = 0; i < all.length; i++) {
      if (all[i].id === templateId) return all[i];
    }
    return null;
  }

  // ---------------------------------------------------------------------------
  // Levenshtein distance
  // ---------------------------------------------------------------------------

  function levenshtein(a, b) {
    if (a.length === 0) return b.length;
    if (b.length === 0) return a.length;

    var matrix = [];
    for (var i = 0; i <= b.length; i++) matrix[i] = [i];
    for (var j = 0; j <= a.length; j++) matrix[0][j] = j;

    for (i = 1; i <= b.length; i++) {
      for (j = 1; j <= a.length; j++) {
        var cost = b.charAt(i - 1) === a.charAt(j - 1) ? 0 : 1;
        matrix[i][j] = Math.min(
          matrix[i - 1][j] + 1,
          matrix[i][j - 1] + 1,
          matrix[i - 1][j - 1] + cost
        );
      }
    }
    return matrix[b.length][a.length];
  }

  // ---------------------------------------------------------------------------
  // Helpers
  // ---------------------------------------------------------------------------

  function shuffle(arr) {
    var a = arr.slice();
    for (var i = a.length - 1; i > 0; i--) {
      var j = Math.floor(Math.random() * (i + 1));
      var tmp = a[i]; a[i] = a[j]; a[j] = tmp;
    }
    return a;
  }

  function normalize(str) {
    return (str || '').trim().toLowerCase()
      .replace(/[,;]/g, ' ')       // treat comma/semicolon as word separator before stripping
      .replace(/[.!?:'"()]/g, '')  // remove remaining punctuation
      .replace(/\s+/g, ' ')        // collapse any run of spaces
      .trim();
  }

  /** Extract the bare word from "der Tisch" -> "Tisch", "das Buch" -> "Buch" */
  function stripArticle(str) {
    return (str || '').replace(/^(der|die|das|ein|eine|einen|einem|einer)\s+/i, '');
  }

  /** Split multi-form answers like "sie/Sie" or "er/sie/es" into individual forms. */
  function splitForms(str) {
    if (!str) return [];
    var parts = String(str).split(/\s*\/\s*/);
    var out = [];
    for (var i = 0; i < parts.length; i++) {
      var p = parts[i].trim();
      if (p && out.indexOf(p) === -1) out.push(p);
    }
    return out;
  }

  function escapeRegex(str) {
    return String(str).replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  }

  /**
   * Blank out the target word in the example sentence, handling multi-form
   * answers (e.g. "sie/Sie", "er/sie/es") by trying each form plus stripped
   * articles. Returns { sentence, matchedForm } so callers can display the
   * specific form that was blanked.
   */
  function blankSentenceDetailed(sentence, targetWord) {
    if (!sentence || !targetWord) return { sentence: sentence || '', matchedForm: null };

    var candidates = [];
    function push(x) {
      if (x && candidates.indexOf(x) === -1) candidates.push(x);
    }
    push(targetWord);
    var forms = splitForms(targetWord);
    for (var i = 0; i < forms.length; i++) {
      push(forms[i]);
      var bare = stripArticle(forms[i]);
      if (bare) push(bare);
    }
    push(stripArticle(targetWord));

    for (var j = 0; j < candidates.length; j++) {
      var c = candidates[j];
      var re = new RegExp('\\b' + escapeRegex(c) + '\\b');
      var m = sentence.match(re);
      if (m) {
        return { sentence: sentence.replace(re, '______'), matchedForm: m[0] };
      }
      // Case-insensitive fallback if case-sensitive didn't hit.
      var reI = new RegExp('\\b' + escapeRegex(c) + '\\b', 'i');
      var mI = sentence.match(reI);
      if (mI) {
        return { sentence: sentence.replace(reI, '______'), matchedForm: mI[0] };
      }
    }
    return { sentence: sentence + ' (______)', matchedForm: null };
  }

  /** Backwards-compatible helper returning only the blanked sentence string. */
  function makeBlankedSentence(sentence, targetWord) {
    return blankSentenceDetailed(sentence, targetWord).sentence;
  }

  /**
   * Can `template` (a fill-blank template) produce an inline blank for `kpData`?
   * Many grammar-rule KPs store a descriptive `correct_form` (e.g. "-e",
   * "Bist du...?", "zu") that does not occur verbatim in `example_sentence`.
   * For those, fill-blank would emit a trailing "(______)" fallback; the
   * engine filters them out and picks another exercise type instead.
   */
  function canFillBlankInline(kpData, template) {
    var pd = kpData && kpData.prompt_data;
    if (!pd || !pd.example_sentence) return false;
    var answerField = (template && template.answer_field) || 'correct_form';
    var raw = resolveField(pd, answerField);
    if (!raw) raw = fallbackAnswer(pd);
    if (!raw) return false;
    return blankSentenceDetailed(pd.example_sentence, raw).matchedForm != null;
  }

  // ---------------------------------------------------------------------------
  // Exercise type: determine from difficulty
  // ---------------------------------------------------------------------------

  function getExerciseType(difficulty, availableTemplateTypes) {
    var types;
    if (difficulty <= 1) {
      types = ['multiple-choice'];
    } else if (difficulty <= 3) {
      types = ['fill-blank', 'multiple-choice'];
    } else {
      types = ['translation', 'sentence-production', 'fill-blank'];
    }
    // Filter to available types
    for (var i = 0; i < types.length; i++) {
      if (availableTemplateTypes.indexOf(types[i]) !== -1) return types[i];
    }
    // Fallback
    return availableTemplateTypes[0] || 'multiple-choice';
  }

  // ---------------------------------------------------------------------------
  // Generate exercise (main entry point)
  // ---------------------------------------------------------------------------

  /**
   * @param {Object} kpData       The knowledge point's prompt_data + id + explanation
   * @param {Array}  templateIds  Array of template IDs applicable to this topic
   * @param {number} difficulty   0-5+ based on correct_streak from KP state
   * @param {Array}  allKPsInTopic All KPs in the same topic (for distractors)
   * @returns {Object} exercise instance
   */
  function generateExercise(kpData, templateIds, difficulty, allKPsInTopic) {
    var kpType = (kpData && kpData.prompt_data && kpData.prompt_data.type) || null;

    // Collect all templates declared on the topic.
    var allForTopic = [];
    for (var i = 0; i < templateIds.length; i++) {
      var t = findTemplate(templateIds[i]);
      if (t) allForTopic.push(t);
    }

    // Filter to templates actually applicable to THIS KP's type. A missing
    // `applicable_kp_types` on a template means "any", matching legacy behaviour.
    var templates = [];
    for (i = 0; i < allForTopic.length; i++) {
      var tpl = allForTopic[i];
      if (!tpl.applicable_kp_types || !kpType ||
          tpl.applicable_kp_types.indexOf(kpType) !== -1) {
        templates.push(tpl);
      }
    }

    // Last-resort fallback: if filtering left nothing (e.g. data drift), use
    // the unfiltered set so we still produce some exercise rather than crash.
    if (templates.length === 0) templates = allForTopic;

    // Further filter: drop fill-blank templates that cannot produce an inline
    // blank for THIS KP (e.g. correct_form is a rule description like "-e" or
    // "Bist du...?"). Without this, getExerciseType would pick fill-blank and
    // generateFillBlank would emit a trailing "(______)" fallback. Keep at
    // least one template overall so the engine can still pick something.
    var filteredByBlankability = [];
    for (i = 0; i < templates.length; i++) {
      if (templates[i].type === 'fill-blank' && !canFillBlankInline(kpData, templates[i])) {
        continue;
      }
      filteredByBlankability.push(templates[i]);
    }
    if (filteredByBlankability.length > 0) templates = filteredByBlankability;

    // Get available types from these templates
    var availableTypes = [];
    for (i = 0; i < templates.length; i++) {
      if (availableTypes.indexOf(templates[i].type) === -1) {
        availableTypes.push(templates[i].type);
      }
    }

    var chosenType = getExerciseType(difficulty, availableTypes);

    // Pick a template matching the chosen type
    var matching = [];
    for (i = 0; i < templates.length; i++) {
      if (templates[i].type === chosenType) matching.push(templates[i]);
    }
    var template = matching[Math.floor(Math.random() * matching.length)];

    if (!template) {
      // Ultimate fallback: MC from first available template
      template = templates[0] || { type: 'multiple-choice', id: 'fallback' };
    }

    switch (template.type) {
      case 'multiple-choice': return generateMultipleChoice(kpData, template, allKPsInTopic);
      case 'fill-blank':      return generateFillBlank(kpData, template);
      case 'matching':        return generateMatching(allKPsInTopic, template);
      case 'translation':     return generateTranslation(kpData, template);
      case 'sentence-production': return generateSentenceProduction(kpData, template);
      default:                return generateMultipleChoice(kpData, template, allKPsInTopic);
    }
  }

  // ---------------------------------------------------------------------------
  // Multiple Choice
  // ---------------------------------------------------------------------------

  function generateMultipleChoice(kpData, template, allKPsInTopic) {
    var pd = kpData.prompt_data;
    var answerField = template.answer_field || 'german';
    var correctAnswer = resolveField(pd, answerField);
    if (!correctAnswer) correctAnswer = fallbackAnswer(pd);
    var prompt = fillPromptTemplate(template.prompt_template, pd);

    // Build distractors
    var distractors = [];
    if (template.distractor_strategy === 'same-field-wrong-value' && template.distractor_pool) {
      // Use pool, exclude correct answer
      for (var i = 0; i < template.distractor_pool.length; i++) {
        if (template.distractor_pool[i] !== correctAnswer) {
          distractors.push(template.distractor_pool[i]);
        }
      }
    } else {
      // random-from-topic or same-paradigm: pick from other KPs
      var others = (allKPsInTopic || []).filter(function (kp) {
        return kp.id !== kpData.id;
      });
      others = shuffle(others);
      var count = (template.distractor_count || 3);
      for (var j = 0; j < others.length && distractors.length < count; j++) {
        var val = resolveField(others[j].prompt_data, answerField);
        if (val && val !== correctAnswer && distractors.indexOf(val) === -1) {
          distractors.push(val);
        }
      }
    }

    // Pad if needed
    while (distractors.length < 2) {
      distractors.push('—');
    }

    // Trim to 3 max distractors
    distractors = distractors.slice(0, 3);

    // Build options and shuffle
    var options = [correctAnswer].concat(distractors);
    options = shuffle(options);

    return {
      type: 'multiple-choice',
      prompt: prompt,
      options: options,
      correctAnswer: correctAnswer,
      contextHint: pd.article_label ? pd.article_label + ' article' : '',
      explanation: kpData.explanation || '',
      kpId: kpData.id
    };
  }

  // ---------------------------------------------------------------------------
  // Fill in the Blank
  // ---------------------------------------------------------------------------

  function generateFillBlank(kpData, template) {
    var pd = kpData.prompt_data;
    var answerField = template.answer_field || 'correct_form';
    var rawAnswer = resolveField(pd, answerField);
    if (!rawAnswer) rawAnswer = fallbackAnswer(pd);

    // Collect every acceptable form up front so multi-form answers
    // (e.g. "sie/Sie", "er/sie/es") are handled consistently.
    var accept = [];
    function addAccept(x) {
      if (x && accept.indexOf(x) === -1) accept.push(x);
    }
    addAccept(rawAnswer);
    var forms = splitForms(rawAnswer);
    for (var i = 0; i < forms.length; i++) addAccept(forms[i]);

    var prompt;
    // Default displayed answer is the raw field; if we blank inside a
    // sentence, prefer the exact form found there so the hint shown on
    // failure matches what the blank required.
    var displayAnswer = rawAnswer;
    if (pd.example_sentence && rawAnswer) {
      var blanked = blankSentenceDetailed(pd.example_sentence, rawAnswer);
      prompt = blanked.sentence;
      if (blanked.matchedForm) {
        displayAnswer = blanked.matchedForm;
        addAccept(blanked.matchedForm);
      }
    } else {
      prompt = fillPromptTemplate(template.prompt_template || 'Fill in: ______', pd);
    }

    // Build context hint:
    // - Conjugation KPs: pronoun label (e.g. "sie = they") + "verb only"
    // - Article vocabulary KPs: "noun only" (article is already visible in sentence)
    // - ALL vocabulary KPs: prepend English translation so the learner knows
    //   which word to fill in (without it "Das ______ ist alt." is unsolvable).
    var fillContextHint = pd.pronoun_label || '';
    if (pd.type === 'conjugation' && !fillContextHint) {
      fillContextHint = 'verb only';
    } else if (pd.type === 'conjugation' && fillContextHint) {
      fillContextHint = fillContextHint + ' — verb only';
    }
    if (pd.article_label) {
      fillContextHint = fillContextHint ? fillContextHint + ' — noun only' : 'noun only';
    }
    if (pd.type === 'vocabulary' && pd.english) {
      // Prepend English so the exercise reads: "Das ______ ist alt." / "the house — noun only"
      fillContextHint = pd.english + (fillContextHint ? ' — ' + fillContextHint : '');
    }
    if (pd.type === 'conjugation' && pd.verb) {
      // Prepend the infinitive so the learner knows which verb to conjugate.
      // Without it "Sie ______ Obst im Supermarkt." is unsolvable — any verb fits.
      fillContextHint = pd.verb + (fillContextHint ? ' — ' + fillContextHint : '');
    }

    return {
      type: 'fill-blank',
      prompt: prompt,
      correctAnswer: displayAnswer,
      acceptAlternatives: accept,
      hint: template.hint || '',
      contextHint: fillContextHint,
      explanation: kpData.explanation || '',
      kpId: kpData.id
    };
  }

  // ---------------------------------------------------------------------------
  // Matching
  // ---------------------------------------------------------------------------

  function generateMatching(allKPsInTopic, template) {
    var leftField = template.left_field || 'german';
    var rightField = template.right_field || 'english';
    var pairCount = Math.min(template.pair_count || 5, (allKPsInTopic || []).length);

    var selected = shuffle(allKPsInTopic || []).slice(0, pairCount);

    var pairs = selected.map(function (kp) {
      return {
        left: resolveField(kp.prompt_data, leftField),
        right: resolveField(kp.prompt_data, rightField),
        kpId: kp.id
      };
    });

    // Shuffled right side for the UI
    var rightSideShuffled = shuffle(pairs.map(function (p) { return p.right; }));

    return {
      type: 'matching',
      pairs: pairs,
      leftItems: pairs.map(function (p) { return p.left; }),
      rightItems: rightSideShuffled,
      explanation: 'Match each German term with its English translation.',
      kpId: pairs.length > 0 ? pairs[0].kpId : null
    };
  }

  // ---------------------------------------------------------------------------
  // Translation
  // ---------------------------------------------------------------------------

  function generateTranslation(kpData, template) {
    var pd = kpData.prompt_data;
    var direction = template.direction || 'en-to-de';
    var prompt, correctAnswer;
    var accept = [];
    function addAlt(x) {
      if (x && accept.indexOf(x) === -1) accept.push(x);
    }

    if (direction === 'en-to-de') {
      prompt = fillPromptTemplate(template.prompt_template || "Translate to German: '{english}'", pd);

      var baseAnswer = pd.german || pd.correct_form || fallbackAnswer(pd) || '';

      // For conjugation KPs the correct_form is only the inflected verb
      // (e.g. "hast"). The learner may also write the full phrase "du hast" —
      // both are accepted, but we display the verb alone and label it
      // "(verb only)" so the expectation is clear before answering.
      var transContextHint = '';
      if (pd.type === 'conjugation' && pd.pronoun && pd.correct_form) {
        var pronounForms = splitForms(pd.pronoun);   // handles "er/sie/es"
        // Displayed answer: bare verb only — pronoun+verb also accepted.
        correctAnswer = pd.correct_form;
        addAlt(pd.correct_form);
        addAlt(baseAnswer);
        for (var pi = 0; pi < pronounForms.length; pi++) {
          addAlt(pronounForms[pi] + ' ' + pd.correct_form);
        }
        transContextHint = 'verb only — pronoun optional';
      } else {
        correctAnswer = baseAnswer;
        addAlt(correctAnswer);
        addAlt(stripArticle(correctAnswer));
        // Article-type vocabulary KPs: show definite/indefinite label.
        if (pd.article_label) {
          transContextHint = pd.article_label + ' article';
        }
        // Grammar-rule KPs with a comma-separated correct_form (e.g. pattern
        // examples like "einundzwanzig, zweiunddreißig, dreiundvierzig"):
        // accept any individual example form as a correct answer so the learner
        // can demonstrate the pattern without having to recall one specific form.
        if (pd.type === 'grammar-rule' && pd.correct_form) {
          var cfForms = pd.correct_form.split(/\s*,\s*/);
          for (var cfi = 0; cfi < cfForms.length; cfi++) {
            addAlt(cfForms[cfi]);
          }
        }
      }
    } else {
      prompt = fillPromptTemplate(template.prompt_template || "Translate to English: '{german}'", pd);
      correctAnswer = pd.english || '';
      addAlt(correctAnswer);
    }

    return {
      type: 'translation',
      prompt: prompt,
      correctAnswer: correctAnswer,
      acceptAlternatives: accept,
      contextHint: transContextHint || '',
      direction: direction,
      explanation: kpData.explanation || '',
      kpId: kpData.id
    };
  }

  // ---------------------------------------------------------------------------
  // Sentence Production
  // ---------------------------------------------------------------------------

  function generateSentenceProduction(kpData, template) {
    var pd = kpData.prompt_data;

    // Build scenario from data
    var scenario;
    if (pd.type === 'conjugation') {
      scenario = "Use '" + pd.verb + "' with '" + pd.pronoun + "' in a sentence.";
    } else if (pd.type === 'vocabulary') {
      scenario = "Write a sentence using '" + (stripArticle(pd.german) || pd.german) + "'.";
    } else {
      scenario = "Write a sentence using '" + (pd.german || '') + "'.";
    }

    // Required keywords for validation
    var requiredKeywords = [];
    if (pd.correct_form) requiredKeywords.push(pd.correct_form);
    else if (pd.german) requiredKeywords.push(stripArticle(pd.german));
    if (pd.pronoun) requiredKeywords.push(pd.pronoun);

    // Example answer
    var exampleAnswer = pd.example_sentence || '';

    return {
      type: 'sentence-production',
      prompt: scenario,
      requiredKeywords: requiredKeywords,
      exampleAnswer: exampleAnswer,
      explanation: kpData.explanation || '',
      kpId: kpData.id
    };
  }

  // ---------------------------------------------------------------------------
  // Answer Validation
  // ---------------------------------------------------------------------------

  function validateAnswer(exercise, userAnswer) {
    switch (exercise.type) {
      case 'multiple-choice':
        return validateMultipleChoice(exercise, userAnswer);
      case 'fill-blank':
        return validateFillBlank(exercise, userAnswer);
      case 'matching':
        return validateMatching(exercise, userAnswer);
      case 'translation':
        return validateTranslation(exercise, userAnswer);
      case 'sentence-production':
        return validateSentenceProduction(exercise, userAnswer);
      default:
        return { correct: false, feedback: 'Unknown exercise type.' };
    }
  }

  function validateMultipleChoice(exercise, selected) {
    var correct = selected === exercise.correctAnswer;
    return {
      correct: correct,
      correctAnswer: exercise.correctAnswer,
      feedback: correct ? 'Correct!' : 'The correct answer is: ' + exercise.correctAnswer
    };
  }

  function validateFillBlank(exercise, userAnswer) {
    var normalized = normalize(userAnswer);
    var candidates = [exercise.correctAnswer].concat(exercise.acceptAlternatives || []);
    var correct = false;
    for (var i = 0; i < candidates.length; i++) {
      var exp = normalize(candidates[i]);
      if (!exp) continue;
      if (normalized === exp || levenshtein(normalized, exp) <= 1) {
        correct = true;
        break;
      }
    }
    return {
      correct: correct,
      correctAnswer: exercise.correctAnswer,
      feedback: correct ? 'Correct!' : 'The correct answer is: ' + exercise.correctAnswer
    };
  }

  function validateMatching(exercise, userPairs) {
    // userPairs is an object: { leftItem: rightItem, ... }
    var allCorrect = true;
    var results = [];
    for (var i = 0; i < exercise.pairs.length; i++) {
      var pair = exercise.pairs[i];
      var userRight = userPairs[pair.left];
      var correct = userRight === pair.right;
      if (!correct) allCorrect = false;
      results.push({ left: pair.left, right: pair.right, userRight: userRight, correct: correct });
    }
    return {
      correct: allCorrect,
      pairResults: results,
      feedback: allCorrect ? 'All matched correctly!' : 'Some pairs were incorrect.'
    };
  }

  function validateTranslation(exercise, userAnswer) {
    var normalized = normalize(userAnswer);
    var correct = false;

    // Check main answer
    if (normalized === normalize(exercise.correctAnswer)) {
      correct = true;
    }
    // Check alternatives
    if (!correct && exercise.acceptAlternatives) {
      for (var i = 0; i < exercise.acceptAlternatives.length; i++) {
        if (normalized === normalize(exercise.acceptAlternatives[i])) {
          correct = true;
          break;
        }
        if (levenshtein(normalized, normalize(exercise.acceptAlternatives[i])) <= 1) {
          correct = true;
          break;
        }
      }
    }
    // Typo tolerance on main answer
    if (!correct && levenshtein(normalized, normalize(exercise.correctAnswer)) <= 1) {
      correct = true;
    }

    return {
      correct: correct,
      correctAnswer: exercise.correctAnswer,
      feedback: correct ? 'Correct!' : 'The correct answer is: ' + exercise.correctAnswer
    };
  }

  function validateSentenceProduction(exercise, userAnswer) {
    var normalized = normalize(userAnswer);
    var missingKeywords = [];

    for (var i = 0; i < exercise.requiredKeywords.length; i++) {
      var keyword = normalize(exercise.requiredKeywords[i]);
      // Check if keyword appears in the answer (with typo tolerance)
      var found = false;
      var words = normalized.split(' ');
      for (var j = 0; j < words.length; j++) {
        if (words[j] === keyword || levenshtein(words[j], keyword) <= 1) {
          found = true;
          break;
        }
      }
      if (!found) {
        missingKeywords.push(exercise.requiredKeywords[i]);
      }
    }

    var correct = missingKeywords.length === 0 && normalized.length > 0;
    var feedback;
    if (correct) {
      feedback = 'Good sentence!';
    } else if (normalized.length === 0) {
      feedback = 'Please write a sentence.';
    } else {
      feedback = 'Missing: ' + missingKeywords.join(', ') + '. Example: ' + exercise.exampleAnswer;
    }

    return {
      correct: correct,
      correctAnswer: exercise.exampleAnswer,
      missingKeywords: missingKeywords,
      feedback: feedback
    };
  }

  // ---------------------------------------------------------------------------
  // Template string helpers
  // ---------------------------------------------------------------------------

  function fillPromptTemplate(template, data) {
    if (!template) return '';
    return template.replace(/\{(\w+)\}/g, function (match, key) {
      if (key === 'german_no_article') return stripArticle(data.german || '');
      if (key === 'example_sentence_with_blank') {
        var answer = data.correct_form || stripArticle(data.german || '');
        return makeBlankedSentence(data.example_sentence || '', answer);
      }
      // If the key isn't present in the KP's prompt_data, drop the placeholder
      // rather than leaking `{key}` into the UI. Template filtering in
      // `generateExercise` should prevent most mismatches, but this guards
      // against data drift.
      return data[key] !== undefined ? data[key] : '';
    });
  }

  function resolveField(data, field) {
    if (!data || !field) return '';
    // Handle special computed fields
    if (field === 'german_word') return stripArticle(data.german || '');
    return data[field] !== undefined ? String(data[field]) : '';
  }

  /** Best-effort answer when a template's declared `answer_field` is missing
   *  on a KP. Picks the first non-empty common field. */
  function fallbackAnswer(pd) {
    if (!pd) return '';
    return pd.correct_form
        || stripArticle(pd.german || '')
        || pd.german
        || pd.english
        || '';
  }

  // ---------------------------------------------------------------------------
  // Public API
  // ---------------------------------------------------------------------------

  // Test seam: allow synchronous template injection (used by the Node test harness).
  function __setTemplates(grammar, vocab) {
    grammarTemplates = grammar || [];
    vocabTemplates = vocab || [];
  }

  return {
    loadTemplates: loadTemplates,
    generateExercise: generateExercise,
    generateMultipleChoice: generateMultipleChoice,
    generateFillBlank: generateFillBlank,
    generateMatching: generateMatching,
    generateTranslation: generateTranslation,
    generateSentenceProduction: generateSentenceProduction,
    validateAnswer: validateAnswer,
    levenshtein: levenshtein,
    __setTemplates: __setTemplates
  };

})();
