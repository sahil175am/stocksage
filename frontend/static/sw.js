/**
 * StockSage Service Worker
 * Provides offline fallback and caches static assets.
 * Network-first for API calls, cache-first for static assets.
 */

const CACHE_VERSION = 'stocksage-v1';
const STATIC_CACHE  = `${CACHE_VERSION}-static`;
const API_CACHE     = `${CACHE_VERSION}-api`;

const STATIC_ASSETS = [
  '/',
  '/static/css/main.css',
  '/static/js/main.js',
  '/static/manifest.json',
  'https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Barlow:wght@300;400;500;600;700&family=Barlow+Condensed:wght@400;600;700&display=swap',
  'https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js',
];

const OFFLINE_PAGE = '/static/offline.html';

// ── Install: cache static assets ──
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(STATIC_CACHE).then(cache => {
      return cache.addAll(STATIC_ASSETS).catch(err => {
        console.warn('[SW] Some static assets could not be cached:', err);
      });
    })
  );
  self.skipWaiting();
});

// ── Activate: remove old caches ──
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(
        keys.filter(k => k.startsWith('stocksage-') && k !== STATIC_CACHE && k !== API_CACHE)
            .map(k => caches.delete(k))
      )
    )
  );
  self.clients.claim();
});

// ── Fetch strategy ──
self.addEventListener('fetch', event => {
  const { request } = event;
  const url = new URL(request.url);

  // Skip non-GET and cross-origin (except fonts/CDN)
  if (request.method !== 'GET') return;

  // API calls: network-first, no cache fallback (always fresh)
  if (url.pathname.startsWith('/stock/api/') ||
      url.pathname.startsWith('/news/api/')  ||
      url.pathname.startsWith('/compare/api/') ||
      url.pathname.startsWith('/profile/alerts/')) {
    event.respondWith(
      fetch(request).catch(() =>
        new Response(JSON.stringify({ error: 'You appear to be offline.' }),
          { headers: { 'Content-Type': 'application/json' } })
      )
    );
    return;
  }

  // Static assets: cache-first
  if (url.pathname.startsWith('/static/') || url.hostname !== location.hostname) {
    event.respondWith(
      caches.match(request).then(cached => cached || fetch(request).then(resp => {
        if (resp && resp.status === 200) {
          const clone = resp.clone();
          caches.open(STATIC_CACHE).then(c => c.put(request, clone));
        }
        return resp;
      }))
    );
    return;
  }

  // HTML pages: network-first with offline fallback
  event.respondWith(
    fetch(request).catch(() =>
      caches.match(request).then(cached => cached ||
        new Response(
          `<!DOCTYPE html><html><head><meta charset="UTF-8"><title>Offline — StockSage</title>
          <style>body{background:#080c10;color:#e2e8f0;font-family:monospace;display:flex;align-items:center;justify-content:center;height:100vh;margin:0;flex-direction:column;gap:1rem}
          h1{color:#00ff88;letter-spacing:3px}p{color:#94a3b8}</style></head>
          <body><h1>◈ STOCKSAGE</h1><p>You appear to be offline.</p><p>Please check your connection and try again.</p></body></html>`,
          { headers: { 'Content-Type': 'text/html' } }
        )
      )
    )
  );
});
