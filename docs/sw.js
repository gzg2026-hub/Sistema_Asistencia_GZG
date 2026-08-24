// CACHE v4 - Fuerza limpieza total del cache anterior
const CACHE_NAME = 'gzg-pwa-v4.0.0';

self.addEventListener('install', (e) => {
  self.skipWaiting(); // Activar inmediatamente sin esperar
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    // Borrar TODOS los caches anteriores (v1, v2, v3, etc.)
    caches.keys().then(keys => {
      return Promise.all(keys.map(k => {
        console.log('[GZG SW] Eliminando cache viejo:', k);
        return caches.delete(k);
      }));
    }).then(() => self.clients.claim())
  );
});

// Sin cache - siempre ir a la red para obtener contenido fresco
self.addEventListener('fetch', (e) => {
  if (e.request.method !== 'GET') return;
  e.respondWith(fetch(e.request).catch(() => caches.match(e.request)));
});
