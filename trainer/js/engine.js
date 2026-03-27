window.Engine = (function () {

  // ---------------------------------------------------------------------------
  // Helpers
  // ---------------------------------------------------------------------------

  function todayISO() {
    return new Date().toISOString().slice(0, 10);
  }

  function addDays(isoDate, days) {
    var d = new Date(isoDate + 'T00:00:00');
    d.setDate(d.getDate() + days);
    return d.toISOString().slice(0, 10);
  }

  /** Fisher-Yates shuffle (in place). */
  function shuffle(arr) {
    for (var i = arr.length - 1; i > 0; i--) {
      var j = Math.floor(Math.random() * (i + 1));
      var tmp = arr[i];
      arr[i] = arr[j];
      arr[j] = tmp;
    }
    return arr;
  }

  // ---------------------------------------------------------------------------
  // SM-2 core
  // ---------------------------------------------------------------------------

  /**
   * Pure SM-2 update. Returns a NEW state object; never mutates `kpState`.
   *
   * Quality mapping:
   *   correct  -> q = 5
   *   incorrect -> q = 1
   */
  function sm2Update(kpState, wasCorrect) {
    var s = {
      ease_factor:    kpState.ease_factor,
      interval_days:  kpState.interval_days,
      next_review:    kpState.next_review,
      correct_streak: kpState.correct_streak,
      total_correct:  kpState.total_correct,
      total_attempts: kpState.total_attempts
    };

    if (wasCorrect) {
      // SM-2 quality = 5 (perfect response)
      var q = 5;
      // EF' = EF + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
      s.ease_factor = Math.max(1.3,
        s.ease_factor + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
      );

      if (s.correct_streak === 0) {
        s.interval_days = 1;
      } else if (s.correct_streak === 1) {
        s.interval_days = 6;
      } else {
        s.interval_days = Math.round(s.interval_days * s.ease_factor);
      }

      s.correct_streak += 1;
      s.total_correct  += 1;
    } else {
      // SM-2 quality = 1 (complete blackout)
      s.ease_factor   = Math.max(1.3, s.ease_factor - 0.2);
      s.interval_days = 1;
      s.correct_streak = 0;
    }

    s.total_attempts += 1;
    s.next_review = addDays(todayISO(), s.interval_days);

    return s;
  }

  // ---------------------------------------------------------------------------
  // Mastery helpers
  // ---------------------------------------------------------------------------

  function isKPMastered(kpState) {
    return kpState.interval_days >= 7
      && kpState.total_attempts > 0
      && (kpState.total_correct / kpState.total_attempts) >= 0.85;
  }

  function isKPDue(kpState) {
    return kpState.next_review === null || kpState.next_review <= todayISO();
  }

  /**
   * Fraction (0-1) of KPs that are mastered.
   * @param {Array} kpStates  Array of individual KP state objects.
   */
  function getTopicMasteryScore(kpStates) {
    if (!kpStates || kpStates.length === 0) return 0;
    var mastered = 0;
    for (var i = 0; i < kpStates.length; i++) {
      if (isKPMastered(kpStates[i])) mastered++;
    }
    return mastered / kpStates.length;
  }

  /**
   * @param {number} masteryScore  Fraction of mastered KPs.
   * @param {Array}  [kpStates]    Optional array of KP states to check if any were attempted.
   */
  function getTopicState(masteryScore, kpStates) {
    if (masteryScore >= 0.85) return 'mastered';
    if (masteryScore > 0)     return 'learning';
    // Score is 0 — check if any KP was actually attempted
    if (kpStates) {
      for (var i = 0; i < kpStates.length; i++) {
        if (kpStates[i].total_attempts > 0) return 'learning';
      }
    }
    return 'new';
  }

  // ---------------------------------------------------------------------------
  // Session composition
  // ---------------------------------------------------------------------------

  /**
   * Build a study session queue.
   *
   * @param {Array}  allTopics          Flat array of topic objects, each with
   *                                    a `knowledge_points` array.
   * @param {Object} allProgress        Progress object from Progress.loadProgress().
   * @param {string} recommendedTopicId Topic to prioritise.
   * @param {number} [sessionSize=12]   Total items in the session.
   * @returns {Array} Array of { kpId, topicId, kpData }.
   */
  function composeSession(allTopics, allProgress, recommendedTopicId, sessionSize) {
    sessionSize = sessionSize || 12;

    var targetNew    = Math.round(sessionSize * 0.6);
    var targetReview = Math.round(sessionSize * 0.3);
    var targetNear   = sessionSize - targetNew - targetReview;

    var today = todayISO();
    var seen  = {};     // kpId -> true, to prevent duplicates

    // Categorise every KP across all topics
    var newLearning = [];   // new/learning KPs from the recommended topic
    var dueReviews  = [];   // due KPs from any topic
    var nearMastered = [];  // mastered KPs near review from any topic

    for (var t = 0; t < allTopics.length; t++) {
      var topic = allTopics[t];
      var kps   = topic.knowledge_points || [];

      for (var k = 0; k < kps.length; k++) {
        var kp    = kps[k];
        var kpId  = kp.id;
        var state = (allProgress.kpStates && allProgress.kpStates[kpId])
          ? allProgress.kpStates[kpId]
          : { ease_factor: 2.5, interval_days: 0, next_review: null,
              correct_streak: 0, total_correct: 0, total_attempts: 0 };

        var item = { kpId: kpId, topicId: topic.id, kpData: kp };

        if (isKPMastered(state)) {
          // Near review: next_review within 2 days or already due
          if (state.next_review && state.next_review <= addDays(today, 2)) {
            nearMastered.push(item);
          }
        } else if (isKPDue(state)) {
          if (state.total_attempts > 0) {
            // Previously seen but not mastered and due -> review
            dueReviews.push(item);
          } else if (topic.id === recommendedTopicId) {
            // Never attempted, from recommended topic -> new/learning
            newLearning.push(item);
          }
        } else {
          // Not due yet, but if it's from the recommended topic and still
          // learning, include as candidate for the new/learning bucket.
          if (topic.id === recommendedTopicId && !isKPMastered(state)) {
            newLearning.push(item);
          }
        }
      }
    }

    // Shuffle each pool for variety
    shuffle(newLearning);
    shuffle(dueReviews);
    shuffle(nearMastered);

    var session = [];

    // Fill from primary buckets
    fillFrom(session, newLearning, targetNew, seen);
    fillFrom(session, dueReviews, targetReview, seen);
    fillFrom(session, nearMastered, targetNear, seen);

    // Back-fill remaining slots from whichever pools still have items
    var remaining = sessionSize - session.length;
    if (remaining > 0) fillFrom(session, newLearning, remaining, seen);
    remaining = sessionSize - session.length;
    if (remaining > 0) fillFrom(session, dueReviews, remaining, seen);
    remaining = sessionSize - session.length;
    if (remaining > 0) fillFrom(session, nearMastered, remaining, seen);

    return session;
  }

  /**
   * Take up to `count` unique items from `pool` and push them into `target`.
   */
  function fillFrom(target, pool, count, seen) {
    var added = 0;
    for (var i = 0; i < pool.length && added < count; i++) {
      if (seen[pool[i].kpId]) continue;
      seen[pool[i].kpId] = true;
      target.push(pool[i]);
      added++;
    }
  }

  // ---------------------------------------------------------------------------
  // Public API
  // ---------------------------------------------------------------------------

  return {
    todayISO:             todayISO,
    addDays:              addDays,
    sm2Update:            sm2Update,
    isKPMastered:         isKPMastered,
    isKPDue:              isKPDue,
    getTopicMasteryScore: getTopicMasteryScore,
    getTopicState:        getTopicState,
    composeSession:       composeSession
  };

})();
