self.addEventListener('fetch', (event) => {
  // Základní service worker pro splnění podmínek instalace
  event.respondWith(fetch(event.request));
});