/**
 * Recommender — recommendation engine for the German language trainer.
 * Depends on: Progress (progress.js), Engine (engine.js)
 */
window.Recommender = (function () {
  "use strict";

  // ---- Helpers ----

  function findTopic(allTopics, topicId) {
    if (!allTopics || !topicId) return null;
    for (var i = 0; i < allTopics.length; i++) {
      if (allTopics[i].id === topicId) return allTopics[i];
    }
    return null;
  }

  /** Get mastery score for a topic by collecting KP states from Progress. */
  function topicMastery(topic, level) {
    var kps = topic.knowledge_points;
    if (!kps || !kps.length) return 0;
    var states = [];
    for (var i = 0; i < kps.length; i++) {
      states.push(Progress.getKPState(level, kps[i].id));
    }
    return Engine.getTopicMasteryScore(states);
  }

  /** Get topic state string ("new", "learning", "mastered"). */
  function topicState(topic, level) {
    var kps = topic.knowledge_points;
    if (!kps || !kps.length) return 'new';
    var states = [];
    for (var i = 0; i < kps.length; i++) {
      states.push(Progress.getKPState(level, kps[i].id));
    }
    return Engine.getTopicState(Engine.getTopicMasteryScore(states), states);
  }

  // ---- Public API ----

  /**
   * Returns all KPs that are past their next_review date, sorted most overdue first.
   * Only includes KPs that have been attempted at least once.
   */
  function getDueReviews(allTopics, level) {
    if (!allTopics || !allTopics.length) return [];

    var due = [];
    var now = Date.now();

    for (var t = 0; t < allTopics.length; t++) {
      var topic = allTopics[t];
      var kps = topic.knowledge_points;
      if (!kps || !kps.length) continue;

      for (var k = 0; k < kps.length; k++) {
        var kp = kps[k];
        var state = Progress.getKPState(level, kp.id);

        if (!state || !state.total_attempts || state.total_attempts === 0) continue;
        if (!Engine.isKPDue(state)) continue;

        var nextReview = state.next_review ? new Date(state.next_review).getTime() : 0;
        var overdueDays = Math.max(0, (now - nextReview) / (1000 * 60 * 60 * 24));

        due.push({
          kpId: kp.id,
          topicId: topic.id,
          kpData: kp,
          overdueDays: overdueDays
        });
      }
    }

    due.sort(function (a, b) {
      return b.overdueDays - a.overdueDays;
    });

    return due;
  }

  /**
   * Returns the most recently practiced topic in "learning" state.
   * Falls back to the first learning topic if no last-practiced info is available.
   */
  function getInProgressTopic(allTopics, level) {
    if (!allTopics || !allTopics.length) return null;

    // Collect all learning topics
    var learning = [];
    for (var i = 0; i < allTopics.length; i++) {
      if (topicState(allTopics[i], level) === "learning") {
        learning.push(allTopics[i]);
      }
    }

    if (learning.length === 0) return null;

    // Prefer the most recently practiced topic (if App is loaded)
    if (typeof App !== 'undefined' && App.getLastPracticedTopic) {
      var lastId = App.getLastPracticedTopic();
      if (lastId) {
        for (var j = 0; j < learning.length; j++) {
          if (learning[j].id === lastId) return learning[j];
        }
      }
    }

    return learning[0];
  }

  /**
   * Returns the highest priority unmastered topic whose prerequisites are met,
   * interleaving grammar and vocabulary when possible. Returns null if nothing
   * qualifies.
   */
  function getNextRecommendedTopic(allTopics, level) {
    if (!allTopics || !allTopics.length) return null;

    // Determine the category of the current in-progress topic (for interleaving).
    var inProgress = getInProgressTopic(allTopics, level);
    var lastCategory = null;
    if (inProgress) {
      lastCategory = (inProgress._domain || "").toLowerCase();
    }

    var candidates = [];

    for (var i = 0; i < allTopics.length; i++) {
      var topic = allTopics[i];
      var state = topicState(topic, level);

      // Only consider topics in "new" state (no KPs attempted yet).
      if (state !== "new") continue;

      // Check soft prerequisite gate (all prereqs >= 50% mastery).
      var prereqCheck = checkPrerequisites(topic.id, allTopics, level);
      if (!prereqCheck.met) continue;

      candidates.push(topic);
    }

    if (candidates.length === 0) return null;

    // If we have a last category, try to pick the opposite type first.
    if (lastCategory) {
      var preferred = [];
      var rest = [];

      for (var j = 0; j < candidates.length; j++) {
        var cat = (candidates[j]._domain || "").toLowerCase();
        if (cat && cat !== lastCategory) {
          preferred.push(candidates[j]);
        } else {
          rest.push(candidates[j]);
        }
      }

      if (preferred.length > 0) return preferred[0];
      if (rest.length > 0) return rest[0];
    }

    return candidates[0];
  }

  /**
   * Top-level recommendation.  Returns an action object describing what the
   * learner should do next.
   */
  function getRecommendation(allTopics, level) {
    var result = {
      action: "all_done",
      topicId: null,
      topicName: null,
      dueCount: 0,
      reason: ""
    };

    if (!allTopics || !allTopics.length) {
      result.reason = "No topics available.";
      return result;
    }

    var dueReviews = getDueReviews(allTopics, level);
    var inProgress = getInProgressTopic(allTopics, level);

    // Priority 1: Due reviews AND no in-progress topic.
    if (dueReviews.length > 0 && !inProgress) {
      // Find the topic with the most due KPs.
      var countByTopic = {};
      for (var i = 0; i < dueReviews.length; i++) {
        var tid = dueReviews[i].topicId;
        countByTopic[tid] = (countByTopic[tid] || 0) + 1;
      }

      var bestTopicId = null;
      var bestCount = 0;
      for (var id in countByTopic) {
        if (countByTopic.hasOwnProperty(id) && countByTopic[id] > bestCount) {
          bestCount = countByTopic[id];
          bestTopicId = id;
        }
      }

      var bestTopic = findTopic(allTopics, bestTopicId);
      result.action = "review";
      result.topicId = bestTopicId;
      result.topicName = bestTopic ? bestTopic.name : null;
      result.dueCount = dueReviews.length;
      result.reason = bestCount + " knowledge point(s) due for review in this topic.";
      return result;
    }

    // Priority 2: In-progress topic.
    if (inProgress) {
      result.action = "continue";
      result.topicId = inProgress.id;
      result.topicName = inProgress.name;
      result.dueCount = dueReviews.length;
      result.reason = "Continue learning this topic — it is already in progress.";
      return result;
    }

    // Priority 3: Next recommended new topic.
    var next = getNextRecommendedTopic(allTopics, level);
    if (next) {
      result.action = "new_topic";
      result.topicId = next.id;
      result.topicName = next.name;
      result.dueCount = dueReviews.length;
      result.reason = "Start a new topic — all prerequisites are met.";
      return result;
    }

    // Priority 4: All done.
    result.dueCount = dueReviews.length;
    result.reason = "All topics are mastered or no new topics have their prerequisites met.";
    return result;
  }

  /**
   * Check whether all prerequisites for a topic are met (>= 50% mastery).
   */
  function checkPrerequisites(topicId, allTopics, level) {
    var result = { met: true, prereqs: [] };

    var topic = findTopic(allTopics, topicId);
    if (!topic || !topic.prerequisites || topic.prerequisites.length === 0) {
      return result;
    }

    for (var i = 0; i < topic.prerequisites.length; i++) {
      var prereqId = topic.prerequisites[i];
      var prereqTopic = findTopic(allTopics, prereqId);
      var mastery = prereqTopic
        ? topicMastery(prereqTopic, level)
        : 0;

      var entry = {
        topicId: prereqId,
        topicName: prereqTopic ? prereqTopic.name : prereqId,
        mastery: mastery,
        required: 0.5
      };

      result.prereqs.push(entry);

      if (mastery < 0.5) {
        result.met = false;
      }
    }

    return result;
  }

  // ---- Expose public interface ----

  return {
    getDueReviews: getDueReviews,
    getInProgressTopic: getInProgressTopic,
    getNextRecommendedTopic: getNextRecommendedTopic,
    getRecommendation: getRecommendation,
    checkPrerequisites: checkPrerequisites,
    findTopic: findTopic
  };
})();
