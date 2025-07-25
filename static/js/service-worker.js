const CACHE_NAME = 'e-sante-v1';
const ASSETS = [
  '/static/dist/tailwind.css',
  '/static/images/login-bg.jpg',
  '/static/js/app.js'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(ASSETS))
  );
});

self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request)
      .then(response => response || fetch(event.request))
  );
});