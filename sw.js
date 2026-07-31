const CACHE_NAME = 'visitas-v100-force-update-login';

self.addEventListener('install', (event) => {
  console.log('[ServiceWorker] Installing v100');
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  console.log('[ServiceWorker] Activating v100 - Purging old caches');
  event.waitUntil(
    caches.keys().then((keyList) => {
      return Promise.all(
        keyList.map((key) => {
          return caches.delete(key);
        })
      );
    }).then(() => self.clients.claim())
  );
});

// Network-First for everything to guarantee fresh code
self.addEventListener('fetch', (event) => {
  event.respondWith(
    fetch(event.request).catch(() => caches.match(event.request))
  );
});
