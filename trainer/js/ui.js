window.UI = (function () {

  var appEl;

  function init(el) {
    appEl = el;
  }

  function $(sel) { return appEl.querySelector(sel); }

  // ---------------------------------------------------------------------------
  // Dashboard
  // ---------------------------------------------------------------------------

  function renderDashboard(state) {
    var level = state.currentLevel;
    var allTopics = state.allTopics;
    var progress = state.progress;

    // Compute stats
    var grammarTopics = allTopics.filter(function (t) { return t._domain === 'grammar'; });
    var vocabTopics = allTopics.filter(function (t) { return t._domain === 'vocabulary'; });

    var grammarStats = domainStats(grammarTopics, progress, level);
    var vocabStats = domainStats(vocabTopics, progress, level);
    var totalMastered = grammarStats.mastered + vocabStats.mastered;
    var totalTopics = allTopics.length;

    // Recommendation
    var rec = Recommender.getRecommendation(allTopics, level);
    var dueCount = Recommender.getDueReviews(allTopics, level).length;

    var html = '';

    // Stats grid
    html += '<div class="stat-grid">';
    html += statCard(grammarStats.pct + '%', 'Grammar');
    html += statCard(vocabStats.pct + '%', 'Vocabulary');
    html += statCard(dueCount, 'Reviews Due');
    html += '</div>';

    // Recommendation card
    if (rec.action !== 'all_done') {
      var recTopic = Recommender.findTopic(allTopics, rec.topicId);
      var recName = recTopic ? recTopic.name : rec.topicName || 'Unknown';
      var actionLabel = rec.action === 'review' ? 'Review Session' :
                        rec.action === 'continue' ? 'Continue' : 'Start New Topic';
      html += '<div class="recommend-card">';
      html += '<div class="recommend-label">Recommended Next</div>';
      html += '<div class="recommend-title">' + esc(recName) + '</div>';
      html += '<div class="recommend-prereqs">' + esc(rec.reason) + '</div>';
      html += '<button class="btn btn-primary btn-block" data-action="start-session" data-topic="' + esc(rec.topicId) + '">' + actionLabel + '</button>';
      html += '</div>';
    } else {
      html += '<div class="card text-center"><div class="card-title">All topics mastered!</div>';
      html += '<div class="card-subtitle">Great work. Reviews will appear as they become due.</div></div>';
    }

    // Topic map — Grammar
    html += topicMapSection('Grammar', grammarTopics, progress, level);
    // Topic map — Vocabulary
    html += topicMapSection('Vocabulary', vocabTopics, progress, level);

    // Bottom nav
    html += '<div class="bottom-nav">';
    html += '<button class="btn btn-secondary" data-action="browse-topics">Browse Topics</button>';
    html += '<button class="btn btn-secondary" data-action="show-settings">Settings</button>';
    html += '</div>';

    appEl.innerHTML = html;
  }

  function domainStats(topics, progress, level) {
    var mastered = 0;
    for (var i = 0; i < topics.length; i++) {
      var kps = topics[i].knowledge_points || [];
      var states = kps.map(function (kp) { return Progress.getKPState(level, kp.id); });
      var score = Engine.getTopicMasteryScore(states);
      if (Engine.getTopicState(score) === 'mastered') mastered++;
    }
    var pct = topics.length > 0 ? Math.round((mastered / topics.length) * 100) : 0;
    return { mastered: mastered, total: topics.length, pct: pct };
  }

  function statCard(value, label) {
    return '<div class="stat-card"><div class="stat-value">' + value + '</div>' +
           '<div class="stat-label">' + esc(label) + '</div></div>';
  }

  function topicMapSection(title, topics, progress, level) {
    var html = '<div class="topic-map">';
    html += '<div class="topic-map-label">' + esc(title) + '</div>';
    html += '<div class="topic-grid">';
    for (var i = 0; i < topics.length; i++) {
      var t = topics[i];
      var kps = t.knowledge_points || [];
      var states = kps.map(function (kp) { return Progress.getKPState(level, kp.id); });
      var score = Engine.getTopicMasteryScore(states);
      var state = Engine.getTopicState(score);
      var pct = Math.round(score * 100);
      html += '<div class="topic-dot ' + state + '" data-action="view-topic" data-topic="' + esc(t.id) + '">';
      html += '<div class="topic-dot-name">' + esc(t.name) + '</div>';
      html += '<div class="topic-dot-pct">' + pct + '%</div>';
      html += '</div>';
    }
    html += '</div></div>';
    return html;
  }

  // ---------------------------------------------------------------------------
  // Topic Browser
  // ---------------------------------------------------------------------------

  function renderTopicBrowser(state) {
    var allTopics = state.allTopics;
    var level = state.currentLevel;

    var grammarTopics = allTopics.filter(function (t) { return t._domain === 'grammar'; });
    var vocabTopics = allTopics.filter(function (t) { return t._domain === 'vocabulary'; });

    var html = '<div class="section-header">';
    html += '<div class="section-title">Topics — ' + level.toUpperCase() + '</div>';
    html += '<button class="btn btn-sm btn-secondary" data-action="go-dashboard">Back</button>';
    html += '</div>';

    html += renderDomainList('Grammar', grammarTopics, level);
    html += renderDomainList('Vocabulary', vocabTopics, level);

    appEl.innerHTML = html;
  }

  function renderDomainList(domainName, topics, level) {
    var html = '<div class="domain-section">';
    html += '<div class="domain-header">' + esc(domainName) + '</div>';

    for (var i = 0; i < topics.length; i++) {
      var t = topics[i];
      var kps = t.knowledge_points || [];
      var states = kps.map(function (kp) { return Progress.getKPState(level, kp.id); });
      var score = Engine.getTopicMasteryScore(states);
      var tState = Engine.getTopicState(score);
      var pct = Math.round(score * 100);

      html += '<div class="topic-row" data-action="view-topic" data-topic="' + esc(t.id) + '">';
      html += '<div class="topic-status-dot ' + tState + '"></div>';
      html += '<div class="topic-info">';
      html += '<div class="topic-name">' + esc(t.name) + '</div>';
      html += '<div class="topic-meta">' + kps.length + ' items</div>';
      html += '</div>';
      html += '<div class="topic-mastery">' + pct + '%</div>';
      html += '</div>';
    }
    html += '</div>';
    return html;
  }

  // ---------------------------------------------------------------------------
  // Topic Detail
  // ---------------------------------------------------------------------------

  function renderTopicDetail(state, topicId) {
    var topic = Recommender.findTopic(state.allTopics, topicId);
    if (!topic) { renderDashboard(state); return; }

    var level = state.currentLevel;
    var kps = topic.knowledge_points || [];
    var states = kps.map(function (kp) { return Progress.getKPState(level, kp.id); });
    var score = Engine.getTopicMasteryScore(states);
    var tState = Engine.getTopicState(score);
    var pct = Math.round(score * 100);

    var prereqCheck = Recommender.checkPrerequisites(topicId, state.allTopics, level);

    var html = '<div class="section-header">';
    html += '<div class="section-title">' + esc(topic.name) + '</div>';
    html += '<button class="btn btn-sm btn-secondary" data-action="go-back">Back</button>';
    html += '</div>';

    html += '<div class="topic-detail">';
    html += '<div class="card-subtitle">' + esc(topic.description) + '</div>';

    // Progress bar
    html += '<div class="progress-bar"><div class="progress-fill ' + tState + '" style="width:' + pct + '%"></div></div>';
    html += '<div class="text-muted mb-16">' + pct + '% mastered &middot; ' + kps.length + ' knowledge points</div>';

    // Prerequisite warning
    if (!prereqCheck.met && prereqCheck.prereqs.length > 0) {
      var prereqNames = prereqCheck.prereqs.map(function (p) {
        return p.topicName + ' (' + Math.round(p.mastery * 100) + '%)';
      }).join(', ');
      html += '<div class="prereq-warning">Prerequisites not fully met: ' + esc(prereqNames) +
              '. You can still practice, but studying prerequisites first is recommended.</div>';
    }

    html += '<button class="btn btn-primary btn-block" data-action="start-session" data-topic="' + esc(topicId) + '">Practice This Topic</button>';
    html += '</div>';

    appEl.innerHTML = html;
  }

  // ---------------------------------------------------------------------------
  // Quiz Session
  // ---------------------------------------------------------------------------

  function renderQuizQuestion(session) {
    var idx = session.currentIndex;
    var total = session.queue.length;
    var item = session.queue[idx];
    var exercise = session.currentExercise;

    var pct = Math.round((idx / total) * 100);

    var html = '<div class="quiz-header">';
    html += '<div class="quiz-progress">';
    html += '<div class="quiz-progress-text">Question ' + (idx + 1) + ' of ' + total + '</div>';
    html += '<div class="progress-bar"><div class="progress-fill learning" style="width:' + pct + '%"></div></div>';
    html += '</div>';
    html += '<button class="btn btn-sm btn-secondary" data-action="end-session">End</button>';
    html += '</div>';

    html += '<div class="quiz-card">';
    html += '<div class="quiz-prompt">' + esc(exercise.prompt) + '</div>';

    switch (exercise.type) {
      case 'multiple-choice':
        html += renderMCOptions(exercise);
        break;
      case 'fill-blank':
        html += '<input class="answer-input" type="text" id="answer-input" placeholder="Type your answer..." autocomplete="off" autofocus>';
        html += '<button class="btn btn-primary btn-block mt-16" data-action="submit-answer" id="submit-btn">Check</button>';
        break;
      case 'translation':
        html += '<input class="answer-input" type="text" id="answer-input" placeholder="Type your translation..." autocomplete="off" autofocus>';
        html += '<button class="btn btn-primary btn-block mt-16" data-action="submit-answer" id="submit-btn">Check</button>';
        break;
      case 'sentence-production':
        html += '<input class="answer-input" type="text" id="answer-input" placeholder="Write a sentence..." autocomplete="off" autofocus>';
        html += '<button class="btn btn-primary btn-block mt-16" data-action="submit-answer" id="submit-btn">Check</button>';
        break;
      case 'matching':
        html += renderMatchingUI(exercise);
        break;
    }

    html += '<div id="feedback-area"></div>';
    html += '</div>';

    appEl.innerHTML = html;

    // Focus input
    var input = document.getElementById('answer-input');
    if (input) {
      setTimeout(function () { input.focus(); }, 50);
    }
  }

  function renderMCOptions(exercise) {
    var html = '<div class="mc-options">';
    var keys = ['1', '2', '3', '4'];
    for (var i = 0; i < exercise.options.length; i++) {
      html += '<button class="mc-option" data-action="select-mc" data-value="' + esc(exercise.options[i]) + '">';
      html += '<span class="mc-key">' + keys[i] + '</span>';
      html += '<span>' + esc(exercise.options[i]) + '</span>';
      html += '</button>';
    }
    html += '</div>';
    return html;
  }

  function renderMatchingUI(exercise) {
    var html = '<div class="matching-container">';
    html += '<div class="match-left">';
    for (var i = 0; i < exercise.leftItems.length; i++) {
      html += '<div class="match-item" data-action="select-match-left" data-index="' + i + '" data-value="' + esc(exercise.leftItems[i]) + '">' +
              esc(exercise.leftItems[i]) + '</div>';
    }
    html += '</div>';
    html += '<div class="match-right">';
    for (var j = 0; j < exercise.rightItems.length; j++) {
      html += '<div class="match-item" data-action="select-match-right" data-index="' + j + '" data-value="' + esc(exercise.rightItems[j]) + '">' +
              esc(exercise.rightItems[j]) + '</div>';
    }
    html += '</div>';
    html += '</div>';
    html += '<button class="btn btn-primary btn-block mt-16 hidden" data-action="submit-matching" id="submit-matching-btn">Check Matches</button>';
    return html;
  }

  function showFeedback(result, exercise) {
    var area = document.getElementById('feedback-area');
    if (!area) return;

    var cls = result.correct ? 'correct' : 'incorrect';
    var html = '<div class="feedback ' + cls + '">';
    html += '<strong>' + (result.correct ? 'Correct!' : 'Incorrect') + '</strong>';
    if (result.feedback && !result.correct) {
      html += '<div class="feedback-explanation">' + esc(result.feedback) + '</div>';
    }
    if (exercise.explanation && !result.correct) {
      html += '<div class="feedback-explanation">' + esc(exercise.explanation) + '</div>';
    }
    html += '</div>';
    html += '<button class="btn btn-primary btn-block mt-8" data-action="next-question">Next</button>';
    area.innerHTML = html;

    // Disable inputs
    var input = document.getElementById('answer-input');
    if (input) {
      input.disabled = true;
      input.classList.add(cls);
    }
    var submitBtn = document.getElementById('submit-btn');
    if (submitBtn) submitBtn.classList.add('hidden');

    // Highlight MC options
    if (exercise.type === 'multiple-choice') {
      var options = appEl.querySelectorAll('.mc-option');
      for (var i = 0; i < options.length; i++) {
        options[i].style.pointerEvents = 'none';
        if (options[i].getAttribute('data-value') === exercise.correctAnswer) {
          options[i].classList.add('correct');
        }
      }
    }
  }

  // ---------------------------------------------------------------------------
  // Session Summary
  // ---------------------------------------------------------------------------

  function renderSessionSummary(session, state) {
    var correct = session.results.filter(function (r) { return r.correct; }).length;
    var total = session.results.length;
    var accuracy = total > 0 ? Math.round((correct / total) * 100) : 0;

    var rec = Recommender.getRecommendation(state.allTopics, state.currentLevel);

    var html = '<div class="card">';
    html += '<div class="card-title text-center">Session Complete</div>';
    html += '<div class="summary-stat"><span class="summary-label">Accuracy</span><span class="summary-value">' + accuracy + '%</span></div>';
    html += '<div class="summary-stat"><span class="summary-label">Correct</span><span class="summary-value">' + correct + ' / ' + total + '</span></div>';
    html += '<div class="summary-stat"><span class="summary-label">Questions</span><span class="summary-value">' + total + '</span></div>';
    html += '</div>';

    // Next recommendation
    if (rec.action !== 'all_done') {
      var recTopic = Recommender.findTopic(state.allTopics, rec.topicId);
      html += '<div class="recommend-card">';
      html += '<div class="recommend-label">Up Next</div>';
      html += '<div class="recommend-title">' + esc(recTopic ? recTopic.name : '') + '</div>';
      html += '<button class="btn btn-primary btn-block" data-action="start-session" data-topic="' + esc(rec.topicId) + '">Continue Studying</button>';
      html += '</div>';
    }

    html += '<div class="bottom-nav">';
    html += '<button class="btn btn-secondary btn-block" data-action="go-dashboard">Back to Dashboard</button>';
    html += '</div>';

    appEl.innerHTML = html;
  }

  // ---------------------------------------------------------------------------
  // Settings view
  // ---------------------------------------------------------------------------

  function renderSettings(state) {
    var html = '<div class="section-header">';
    html += '<div class="section-title">Settings</div>';
    html += '<button class="btn btn-sm btn-secondary" data-action="go-dashboard">Back</button>';
    html += '</div>';

    html += '<div class="card">';
    html += '<div class="card-title">Progress Data</div>';
    html += '<div class="card-subtitle">Export or import your learning progress.</div>';
    html += '<div class="bottom-nav">';
    html += '<button class="btn btn-secondary" data-action="export-progress">Export JSON</button>';
    html += '<button class="btn btn-secondary" data-action="import-progress">Import JSON</button>';
    html += '</div>';
    html += '</div>';

    html += '<div class="card mt-16">';
    html += '<div class="card-title text-error">Reset Progress</div>';
    html += '<div class="card-subtitle">This cannot be undone.</div>';
    html += '<button class="btn btn-secondary" data-action="reset-level" data-level="' + esc(state.currentLevel) + '">Reset ' + state.currentLevel.toUpperCase() + ' Progress</button>';
    html += '</div>';

    appEl.innerHTML = html;
  }

  // ---------------------------------------------------------------------------
  // Utilities
  // ---------------------------------------------------------------------------

  function esc(str) {
    if (str === null || str === undefined) return '';
    var div = document.createElement('div');
    div.appendChild(document.createTextNode(String(str)));
    return div.innerHTML;
  }

  // ---------------------------------------------------------------------------
  // Public API
  // ---------------------------------------------------------------------------

  return {
    init: init,
    renderDashboard: renderDashboard,
    renderTopicBrowser: renderTopicBrowser,
    renderTopicDetail: renderTopicDetail,
    renderQuizQuestion: renderQuizQuestion,
    showFeedback: showFeedback,
    renderSessionSummary: renderSessionSummary,
    renderSettings: renderSettings,
    esc: esc
  };

})();
