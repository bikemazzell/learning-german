var CACHE = 'german-trainer-v1';
var ASSETS = [
  './',
  'index.html',
  'css/styles.css',
  'js/app.js',
  'js/engine.js',
  'js/exercises.js',
  'js/progress.js',
  'js/recommender.js',
  'js/ui.js',
  'data/levels/a1.json',
  'data/levels/a2.json',
  'data/templates/grammar.json',
  'data/templates/vocab.json',
  'manifest.json'
];

self.addEventListener('install', function (e) {
  e.waitUntil(
    caches.open(CACHE).then(function (cache) {
      return cache.addAll(ASSETS);
    })
  );
  self.skipWaiting();
});

self.addEventListener('activate', function (e) {
  e.waitUntil(
    caches.keys().then(function (keys) {
      return Promise.all(
        keys.filter(function (k) { return k !== CACHE; })
            .map(function (k) { return caches.delete(k); })
      );
    })
  );
  self.clients.claim();
});

self.addEventListener('fetch', function (e) {
  e.respondWith(
    fetch(e.request).then(function (response) {
      var clone = response.clone();
      caches.open(CACHE).then(function (cache) {
        cache.put(e.request, clone);
      });
      return response;
    }).catch(function () {
      return caches.match(e.request);
    })
  );
});
