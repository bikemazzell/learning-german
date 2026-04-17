window.Progress = (function () {
  var STORAGE_PREFIX = 'trainer-progress-';

  var DEFAULT_KP_STATE = {
    ease_factor: 2.5,
    interval_days: 0,
    next_review: null,
    correct_streak: 0,
    total_correct: 0,
    total_attempts: 0
  };

  // In-memory cache: { level: progressObject }
  var cache = {};

  function storageKey(level) {
    return STORAGE_PREFIX + level;
  }

  function emptyProgress() {
    return { kpStates: {}, lastUpdated: null };
  }

  function loadProgress(level) {
    if (cache[level]) return cache[level];
    try {
      var raw = localStorage.getItem(storageKey(level));
      if (!raw) {
        cache[level] = emptyProgress();
        return cache[level];
      }
      var parsed = JSON.parse(raw);
      if (!parsed || typeof parsed.kpStates !== 'object') {
        cache[level] = emptyProgress();
        return cache[level];
      }
      cache[level] = parsed;
      return cache[level];
    } catch (e) {
      cache[level] = emptyProgress();
      return cache[level];
    }
  }

  function saveProgress(level, data) {
    data.lastUpdated = new Date().toISOString();
    cache[level] = data;
    try {
      localStorage.setItem(storageKey(level), JSON.stringify(data));
    } catch (e) {
      // storage full or unavailable
    }
  }

  function getKPState(level, kpId) {
    var progress = loadProgress(level);
    var state = progress.kpStates[kpId];
    if (!state) {
      // Return a fresh default (copy so caller can't mutate the template)
      return {
        ease_factor: 2.5,
        interval_days: 0,
        next_review: null,
        correct_streak: 0,
        total_correct: 0,
        total_attempts: 0
      };
    }
    // Return a shallow copy so caller can't corrupt cache
    return {
      ease_factor: state.ease_factor,
      interval_days: state.interval_days,
      next_review: state.next_review,
      correct_streak: state.correct_streak,
      total_correct: state.total_correct,
      total_attempts: state.total_attempts
    };
  }

  function updateKPState(level, kpId, newState) {
    var progress = loadProgress(level);
    var current = progress.kpStates[kpId] || {
      ease_factor: 2.5, interval_days: 0, next_review: null,
      correct_streak: 0, total_correct: 0, total_attempts: 0
    };
    for (var key in newState) {
      if (newState.hasOwnProperty(key)) {
        current[key] = newState[key];
      }
    }
    progress.kpStates[kpId] = current;
    saveProgress(level, progress);
  }

  function getTopicProgress(level, topicId, knowledgePoints) {
    var progress = loadProgress(level);
    var total = knowledgePoints.length;
    var attempted = 0;
    var mastered = 0;
    var totalCorrect = 0;
    var totalAttempts = 0;

    for (var i = 0; i < knowledgePoints.length; i++) {
      var state = progress.kpStates[knowledgePoints[i].id];
      if (!state) continue;
      if (state.total_attempts > 0) attempted++;
      if (state.interval_days >= 7 && state.total_attempts > 0) mastered++;
      totalCorrect += state.total_correct || 0;
      totalAttempts += state.total_attempts || 0;
    }

    return {
      total: total,
      attempted: attempted,
      mastered: mastered,
      accuracy: totalAttempts > 0 ? totalCorrect / totalAttempts : 0
    };
  }

  function exportProgress() {
    var all = {};
    try {
      for (var i = 0; i < localStorage.length; i++) {
        var key = localStorage.key(i);
        if (key.indexOf(STORAGE_PREFIX) === 0) {
          var level = key.substring(STORAGE_PREFIX.length);
          all[level] = JSON.parse(localStorage.getItem(key));
        }
      }
    } catch (e) {
      // ignore read errors
    }
    return JSON.stringify(all);
  }

  function importProgress(jsonString) {
    var data;
    try {
      data = JSON.parse(jsonString);
    } catch (e) {
      return false;
    }
    if (!data || typeof data !== 'object') return false;

    try {
      for (var level in data) {
        if (!data.hasOwnProperty(level)) continue;
        var entry = data[level];
        if (!entry || typeof entry.kpStates !== 'object') continue;
        localStorage.setItem(storageKey(level), JSON.stringify(entry));
        cache[level] = entry; // update cache
      }
    } catch (e) {
      return false;
    }
    return true;
  }

  function resetTopic(level, topicId, knowledgePoints) {
    var progress = loadProgress(level);
    for (var i = 0; i < knowledgePoints.length; i++) {
      delete progress.kpStates[knowledgePoints[i].id];
    }
    saveProgress(level, progress);
  }

  function resetLevel(level) {
    delete cache[level];
    try {
      localStorage.removeItem(storageKey(level));
    } catch (e) {
      // ignore removal errors
    }
  }

  /** Force reload from localStorage (useful after external changes). */
  function invalidateCache(level) {
    if (level) {
      delete cache[level];
    } else {
      cache = {};
    }
  }

  return {
    loadProgress: loadProgress,
    saveProgress: saveProgress,
    getKPState: getKPState,
    updateKPState: updateKPState,
    getTopicProgress: getTopicProgress,
    exportProgress: exportProgress,
    importProgress: importProgress,
    resetTopic: resetTopic,
    resetLevel: resetLevel,
    invalidateCache: invalidateCache
  };
})();
