// Blacktemplar Bolter - Service Worker
// Cache de assets e suporte offline

const CACHE_NAME = 'blacktemplar-v1';

const ASSETS_TO_CACHE = [
  '/',
  '/static/style.css',
  '/static/app.js',
  '/static/icon.png'
];

// Instalação do Service Worker
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('✅ Cache aberto');
        return cache.addAll(ASSETS_TO_CACHE);
      })
  );
});

// Estratégia de cache: Network first, fallback para cache
self.addEventListener('fetch', (event) => {
  event.respondWith(
    fetch(event.request)
      .then((networkResponse) => {
        // Se a rede responder, devolver e atualizar cache
        if (shouldCache(event.request)) {
          const clone = networkResponse.clone();
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(event.request, clone);
          });
        }
        return networkResponse;
      })
      .catch(() => {
        // Se a rede falhar, tentar do cache
        return caches.match(event.request);
      })
  );
});

// Função para determinar se deve cachear um recurso
function shouldCache(request) {
  // Não fazer cache de APIs dinâmicas
  if (request.url.includes('/api/')) {
    return false;
  }
  
  // Cache para arquivos estáticos e HTML principal
  return request.method === 'GET' && 
         (request.url.includes('/static/') || 
          request.url.endsWith('/'));
}

// Limpeza de caches antigos
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME) {
            console.log('🧹 Limpando cache antigo:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
}); 