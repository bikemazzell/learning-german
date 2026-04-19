window.Exam = (function () {
  'use strict';

  var STORAGE_KEY = 'trainer-exam-practice';

  function loadExamData(basePath) {
    basePath = basePath || 'data/exam';
    return Promise.all([
      fetch(basePath + '/a1.json').then(function (r) { return r.json(); }),
      fetch(basePath + '/a2.json').then(function (r) { return r.json(); })
    ]).then(function (results) {
      return { a1: results[0], a2: results[1] };
    });
  }

  function emptyProgress() {
    return {
      a1: emptyLevelProgress(),
      a2: emptyLevelProgress()
    };
  }

  function emptyLevelProgress() {
    return {
      reading: { completedTaskIds: [], totalCorrect: 0, totalQuestions: 0 },
      writing: { completedTaskIds: [] }
    };
  }

  function normalizeLevel(level) {
    return String(level || '').toLowerCase();
  }

  function loadProgress() {
    try {
      var raw = localStorage.getItem(STORAGE_KEY);
      if (!raw) return emptyProgress();
      var parsed = JSON.parse(raw);
      var progress = emptyProgress();
      for (var level in progress) {
        if (!progress.hasOwnProperty(level)) continue;
        if (!parsed[level]) continue;
        if (parsed[level].reading) {
          progress[level].reading.completedTaskIds = parsed[level].reading.completedTaskIds || [];
          progress[level].reading.totalCorrect = parsed[level].reading.totalCorrect || 0;
          progress[level].reading.totalQuestions = parsed[level].reading.totalQuestions || 0;
        }
        if (parsed[level].writing) {
          progress[level].writing.completedTaskIds = parsed[level].writing.completedTaskIds || [];
        }
      }
      return progress;
    } catch (e) {
      return emptyProgress();
    }
  }

  function saveProgress(progress) {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(progress));
    } catch (e) {
      // Ignore storage failures; the practice UI can still work in-memory.
    }
  }

  function uniquePush(arr, value) {
    if (arr.indexOf(value) === -1) arr.push(value);
  }

  function scoreReadingTask(task, answersByQuestionId) {
    var questions = task.questions || [];
    var details = [];
    var correct = 0;

    for (var i = 0; i < questions.length; i++) {
      var q = questions[i];
      var userAnswer = answersByQuestionId ? answersByQuestionId[q.id] : undefined;
      var isCorrect = userAnswer === q.answer;
      if (isCorrect) correct++;
      details.push({
        questionId: q.id,
        prompt: q.prompt,
        correct: isCorrect,
        answer: q.answer,
        givenAnswer: userAnswer,
        explanation: q.explanation
      });
    }

    return {
      correct: correct,
      total: questions.length,
      percent: questions.length ? Math.round((correct / questions.length) * 100) : 0,
      details: details
    };
  }

  function countWords(text) {
    var trimmed = String(text || '').trim();
    if (!trimmed) return 0;
    return trimmed.split(/\s+/).filter(Boolean).length;
  }

  function recordReadingResult(level, taskId, result) {
    var levelKey = normalizeLevel(level);
    var progress = loadProgress();
    if (!progress[levelKey]) progress[levelKey] = emptyLevelProgress();
    uniquePush(progress[levelKey].reading.completedTaskIds, taskId);
    progress[levelKey].reading.totalCorrect += result.correct || 0;
    progress[levelKey].reading.totalQuestions += result.total || 0;
    saveProgress(progress);
    return progress[levelKey].reading;
  }

  function recordWritingPractice(level, taskId) {
    var levelKey = normalizeLevel(level);
    var progress = loadProgress();
    if (!progress[levelKey]) progress[levelKey] = emptyLevelProgress();
    uniquePush(progress[levelKey].writing.completedTaskIds, taskId);
    saveProgress(progress);
    return progress[levelKey].writing;
  }

  function findSection(examLevel, skill) {
    var sections = examLevel && examLevel.sections ? examLevel.sections : [];
    for (var i = 0; i < sections.length; i++) {
      if (sections[i].skill === skill) return sections[i];
    }
    return null;
  }

  function findTask(examLevel, skill, taskId) {
    var section = findSection(examLevel, skill);
    var tasks = section && section.tasks ? section.tasks : [];
    for (var i = 0; i < tasks.length; i++) {
      if (tasks[i].id === taskId) return tasks[i];
    }
    return null;
  }

  return {
    loadExamData: loadExamData,
    loadProgress: loadProgress,
    scoreReadingTask: scoreReadingTask,
    countWords: countWords,
    recordReadingResult: recordReadingResult,
    recordWritingPractice: recordWritingPractice,
    findSection: findSection,
    findTask: findTask
  };
})();
