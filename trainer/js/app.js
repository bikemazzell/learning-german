window.App = (function () {

  // ---------------------------------------------------------------------------
  // State
  // ---------------------------------------------------------------------------

  var state = {
    currentLevel: 'a1',
    levels: {},          // { a1: { level, domains }, a2: ... }
    allTopics: [],       // flat array of topics for current level (with _domain tag)
    progress: null,      // Progress data for current level
    currentView: 'dashboard',
    previousView: null,
    session: null        // active quiz session
  };

  // ---------------------------------------------------------------------------
  // Init
  // ---------------------------------------------------------------------------

  function init() {
    UI.init(document.getElementById('app'));

    Promise.all([
      fetch('data/levels/a1.json').then(function (r) { return r.json(); }),
      fetch('data/levels/a2.json').then(function (r) { return r.json(); }),
      Exercises.loadTemplates('data/templates')
    ]).then(function (results) {
      state.levels.a1 = results[0];
      state.levels.a2 = results[1];
      setLevel(state.currentLevel);
      renderLevelTabs();
      setupEventDelegation();
      navigate('dashboard');
    }).catch(function (err) {
      document.getElementById('app').innerHTML =
        '<div class="card text-center"><div class="card-title text-error">Failed to load data</div>' +
        '<div class="card-subtitle">' + UI.esc(err.message) + '</div></div>';
    });
  }

  // ---------------------------------------------------------------------------
  // Level management
  // ---------------------------------------------------------------------------

  function setLevel(level) {
    state.currentLevel = level;
    state.progress = Progress.loadProgress(level);
    state.allTopics = flattenTopics(state.levels[level]);
  }

  function flattenTopics(levelData) {
    var topics = [];
    if (!levelData || !levelData.domains) return topics;
    for (var i = 0; i < levelData.domains.length; i++) {
      var domain = levelData.domains[i];
      var domainTopics = domain.topics || [];
      for (var j = 0; j < domainTopics.length; j++) {
        var t = domainTopics[j];
        t._domain = domain.id;
        t._domainName = domain.name;
        topics.push(t);
      }
    }
    return topics;
  }

  function renderLevelTabs() {
    var tabsEl = document.getElementById('level-tabs');
    if (!tabsEl) return;
    var levels = Object.keys(state.levels);
    var html = '';
    for (var i = 0; i < levels.length; i++) {
      var l = levels[i];
      var active = l === state.currentLevel ? ' active' : '';
      html += '<button class="level-tab' + active + '" data-action="switch-level" data-level="' + l + '">' + l.toUpperCase() + '</button>';
    }
    tabsEl.innerHTML = html;
  }

  // ---------------------------------------------------------------------------
  // Navigation
  // ---------------------------------------------------------------------------

  function navigate(view, params) {
    state.previousView = state.currentView;
    state.currentView = view;
    window.location.hash = view;

    switch (view) {
      case 'dashboard':
        UI.renderDashboard(state);
        break;
      case 'topics':
        UI.renderTopicBrowser(state);
        break;
      case 'topic-detail':
        UI.renderTopicDetail(state, params);
        break;
      case 'quiz':
        UI.renderQuizQuestion(state.session);
        break;
      case 'summary':
        UI.renderSessionSummary(state.session, state);
        break;
      case 'settings':
        UI.renderSettings(state);
        break;
      default:
        UI.renderDashboard(state);
    }
  }

  // ---------------------------------------------------------------------------
  // Session lifecycle
  // ---------------------------------------------------------------------------

  function startSession(topicId) {
    var queue = Engine.composeSession(state.allTopics, state.progress, topicId, 12);

    if (queue.length === 0) {
      navigate('dashboard');
      return;
    }

    state.session = {
      topicId: topicId,
      queue: queue,
      currentIndex: 0,
      currentExercise: null,
      results: [],
      matchState: { selectedLeft: null, pairs: {} }
    };

    generateCurrentExercise();
    navigate('quiz');
  }

  function generateCurrentExercise() {
    var session = state.session;
    var item = session.queue[session.currentIndex];
    var topic = Recommender.findTopic(state.allTopics, item.topicId);
    var kpState = Progress.getKPState(state.currentLevel, item.kpId);
    var difficulty = kpState.correct_streak || 0;
    var templateIds = topic ? topic.exercise_templates : [];
    var allKPs = topic ? topic.knowledge_points : [];

    var kpDataFull = {
      id: item.kpData.id,
      prompt_data: item.kpData.prompt_data,
      explanation: item.kpData.explanation
    };

    session.currentExercise = Exercises.generateExercise(kpDataFull, templateIds, difficulty, allKPs);
  }

  function submitAnswer(userAnswer) {
    var session = state.session;
    var exercise = session.currentExercise;
    var result = Exercises.validateAnswer(exercise, userAnswer);

    // Update SM-2 state
    var item = session.queue[session.currentIndex];
    var kpState = Progress.getKPState(state.currentLevel, item.kpId);
    var newState = Engine.sm2Update(kpState, result.correct);
    Progress.updateKPState(state.currentLevel, item.kpId, newState);
    state.progress = Progress.loadProgress(state.currentLevel);

    session.results.push({
      kpId: item.kpId,
      correct: result.correct,
      exercise: exercise.type
    });

    UI.showFeedback(result, exercise);
  }

  function nextQuestion() {
    var session = state.session;
    session.currentIndex++;

    if (session.currentIndex >= session.queue.length) {
      navigate('summary');
      return;
    }

    session.matchState = { selectedLeft: null, pairs: {} };
    generateCurrentExercise();
    navigate('quiz');
  }

  // ---------------------------------------------------------------------------
  // Matching exercise state
  // ---------------------------------------------------------------------------

  function handleMatchLeft(value) {
    state.session.matchState.selectedLeft = value;
    // Highlight selected
    var items = document.querySelectorAll('[data-action="select-match-left"]');
    for (var i = 0; i < items.length; i++) {
      items[i].classList.toggle('selected', items[i].getAttribute('data-value') === value);
    }
  }

  function handleMatchRight(value) {
    var ms = state.session.matchState;
    if (!ms.selectedLeft) return;

    ms.pairs[ms.selectedLeft] = value;

    // Mark both as matched
    var leftItems = document.querySelectorAll('[data-action="select-match-left"]');
    var rightItems = document.querySelectorAll('[data-action="select-match-right"]');

    for (var i = 0; i < leftItems.length; i++) {
      if (leftItems[i].getAttribute('data-value') === ms.selectedLeft) {
        leftItems[i].classList.add('matched');
        leftItems[i].classList.remove('selected');
      }
    }
    for (var j = 0; j < rightItems.length; j++) {
      if (rightItems[j].getAttribute('data-value') === value) {
        rightItems[j].classList.add('matched');
      }
    }

    ms.selectedLeft = null;

    // Check if all pairs made
    var exercise = state.session.currentExercise;
    if (Object.keys(ms.pairs).length >= exercise.leftItems.length) {
      var submitBtn = document.getElementById('submit-matching-btn');
      if (submitBtn) submitBtn.classList.remove('hidden');
    }
  }

  function submitMatching() {
    var exercise = state.session.currentExercise;
    submitAnswer(state.session.matchState.pairs);
  }

  // ---------------------------------------------------------------------------
  // Event delegation
  // ---------------------------------------------------------------------------

  function setupEventDelegation() {
    document.addEventListener('click', function (e) {
      var target = e.target.closest('[data-action]');
      if (!target) return;

      var action = target.getAttribute('data-action');

      switch (action) {
        case 'switch-level':
          var level = target.getAttribute('data-level');
          setLevel(level);
          renderLevelTabs();
          navigate('dashboard');
          break;

        case 'start-session':
          var topicId = target.getAttribute('data-topic');
          startSession(topicId);
          break;

        case 'go-dashboard':
          navigate('dashboard');
          break;

        case 'browse-topics':
          navigate('topics');
          break;

        case 'view-topic':
          var tid = target.getAttribute('data-topic');
          navigate('topic-detail', tid);
          break;

        case 'go-back':
          if (state.previousView === 'topics') {
            navigate('topics');
          } else {
            navigate('dashboard');
          }
          break;

        case 'select-mc':
          var val = target.getAttribute('data-value');
          submitAnswer(val);
          break;

        case 'submit-answer':
          var input = document.getElementById('answer-input');
          if (input && input.value.trim()) {
            submitAnswer(input.value.trim());
          }
          break;

        case 'select-match-left':
          handleMatchLeft(target.getAttribute('data-value'));
          break;

        case 'select-match-right':
          handleMatchRight(target.getAttribute('data-value'));
          break;

        case 'submit-matching':
          submitMatching();
          break;

        case 'next-question':
          nextQuestion();
          break;

        case 'end-session':
          navigate('summary');
          break;

        case 'show-settings':
          navigate('settings');
          break;

        case 'export-progress':
          exportProgress();
          break;

        case 'import-progress':
          importProgress();
          break;

        case 'reset-level':
          var rl = target.getAttribute('data-level');
          if (confirm('Reset all progress for ' + rl.toUpperCase() + '? This cannot be undone.')) {
            Progress.resetLevel(rl);
            state.progress = Progress.loadProgress(state.currentLevel);
            navigate('dashboard');
          }
          break;
      }
    });

    // Keyboard support
    document.addEventListener('keydown', function (e) {
      if (state.currentView !== 'quiz' || !state.session) return;
      var exercise = state.session.currentExercise;
      if (!exercise) return;

      // Enter to submit text input
      if (e.key === 'Enter') {
        var feedbackArea = document.getElementById('feedback-area');
        if (feedbackArea && feedbackArea.innerHTML) {
          // Feedback is showing — advance
          nextQuestion();
          return;
        }
        var input = document.getElementById('answer-input');
        if (input && input.value.trim() && !input.disabled) {
          submitAnswer(input.value.trim());
        }
      }

      // Number keys for MC
      if (exercise.type === 'multiple-choice') {
        var feedbackShowing = document.getElementById('feedback-area');
        if (feedbackShowing && feedbackShowing.innerHTML) return;
        var num = parseInt(e.key);
        if (num >= 1 && num <= exercise.options.length) {
          submitAnswer(exercise.options[num - 1]);
        }
      }
    });
  }

  // ---------------------------------------------------------------------------
  // Export / Import
  // ---------------------------------------------------------------------------

  function exportProgress() {
    var data = Progress.exportProgress();
    var blob = new Blob([data], { type: 'application/json' });
    var url = URL.createObjectURL(blob);
    var a = document.createElement('a');
    a.href = url;
    a.download = 'german-trainer-progress.json';
    a.click();
    URL.revokeObjectURL(url);
  }

  function importProgress() {
    var input = document.createElement('input');
    input.type = 'file';
    input.accept = '.json';
    input.onchange = function (e) {
      var file = e.target.files[0];
      if (!file) return;
      var reader = new FileReader();
      reader.onload = function (ev) {
        try {
          Progress.importProgress(ev.target.result);
          state.progress = Progress.loadProgress(state.currentLevel);
          navigate('dashboard');
        } catch (err) {
          alert('Import failed: ' + err.message);
        }
      };
      reader.readAsText(file);
    };
    input.click();
  }

  // ---------------------------------------------------------------------------
  // Public API
  // ---------------------------------------------------------------------------

  return {
    init: init,
    state: state
  };

})();

// Boot
document.addEventListener('DOMContentLoaded', App.init);
