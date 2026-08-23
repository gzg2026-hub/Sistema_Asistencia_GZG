const CACHE_NAME = 'gzg-asistencia-v1.0.2';
const STATIC_ASSETS = [
  '/',
  '/manifest.json',
  '/assets/gzg_logo.png',
  '/assets/gzg_logo_transparent.png'
];

// Instalación del Service Worker
self.addEventListener('install', (event) => {
  self.skipWaiting();
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      console.log('[PWA GZG] Precaching static assets');
      return cache.addAll(STATIC_ASSETS).catch((err) => {
        console.warn('[PWA GZG] Some static assets failed to cache:', err);
      });
    })
  );
});

// Activación del Service Worker y limpieza de versiones antiguas
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cache) => {
          if (cache !== CACHE_NAME) {
            console.log('[PWA GZG] Removing old cache:', cache);
            return caches.delete(cache);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

// Intercepción de peticiones (Network-First con Fallback a Caché para datos, Cache-First para imágenes)
self.addEventListener('fetch', (event) => {
  const request = event.request;

  // Solo interceptar peticiones GET
  if (request.method !== 'GET') return;

  // Estrategia Cache First para imágenes y recursos estáticos
  if (request.url.includes('/assets/') || request.url.includes('.png') || request.url.includes('.ico')) {
    event.respondWith(
      caches.match(request).then((cachedResponse) => {
        if (cachedResponse) return cachedResponse;
        return fetch(request).then((networkResponse) => {
          if (networkResponse && networkResponse.status === 200) {
            const responseClone = networkResponse.clone();
            caches.open(CACHE_NAME).then((cache) => cache.put(request, responseClone));
          }
          return networkResponse;
        });
      })
    );
    return;
  }

  // Estrategia Network First para navegación y datos del dashboard
  event.respondWith(
    fetch(request)
      .then((networkResponse) => {
        if (networkResponse && networkResponse.status === 200) {
          const responseClone = networkResponse.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(request, responseClone));
        }
        return networkResponse;
      })
      .catch(() => {
        return caches.match(request).then((cachedResponse) => {
          if (cachedResponse) return cachedResponse;
          // Fallback offline si la red no está disponible
          if (request.headers.get('accept').includes('text/html')) {
            return new Response(
              `<!DOCTYPE html>
              <html lang="es">
              <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>GZG Minerales - Modo Offline</title>
                <style>
                  body { background-color: #121418; color: #FFFFFF; font-family: sans-serif; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; margin: 0; text-align: center; padding: 20px; }
                  .card { background: #1D212A; border: 1px solid #2A2F3D; border-radius: 16px; padding: 30px; max-width: 400px; }
                  h2 { color: #F58220; margin-bottom: 10px; }
                  p { color: #9A9EA7; font-size: 14px; line-height: 1.5; }
                  button { background: linear-gradient(135deg, #F58220 0%, #D35400 100%); color: white; border: none; padding: 12px 24px; border-radius: 8px; font-weight: bold; cursor: pointer; margin-top: 15px; }
                </style>
              </head>
              <body>
                <div class="card">
                  <h2>⚠️ Modo Offline</h2>
                  <p>No se pudo conectar con el servidor en mina. Los datos cacheados se mostrarán automáticamente al restablecer señal.</p>
                  <button onclick="window.location.reload()">Reintentar Conexión</button>
                </div>
              </body>
              </html>`,
              { headers: { 'Content-Type': 'text/html' } }
            );
          }
        });
      })
  );
});
