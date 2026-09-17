/* Service worker do Lucro Artesanato.

   Faz DUAS coisas, e só elas:
     1. habilita o prompt nativo de "instalar app";
     2. faz os apps abrirem OFFLINE depois da primeira visita.

   O que ele NÃO faz, de propósito (regra dura do Vini, 17/09/2026):
   NÃO guarda nível de acesso, nem no cache, nem em lugar nenhum. A liberação é
   pelo CAMINHO do link que a compradora recebeu, e só. Sem backend, sem
   localStorage, sem query string.

   Estratégia: rede primeiro, cache como reserva. Assim ela sempre recebe a versão
   nova quando tem internet, e continua funcionando sem ela.

   AO MEXER EM QUALQUER APP, SUBA A VERSÃO DO CACHE. Sem isso a tela mostra o
   arquivo antigo e parece que a correção não pegou. */
const CACHE = 'lucroartesanato-v1';

const ARQS = [
  'hub.html',
  'manifest.webmanifest',
  'favicon-96.png', 'favicon-180.png', 'icone-192.png', 'icone-512.png',
  /* Cada pasta serve o menu E os apps: é isso que mantém a chave no caminho de
     toda página, pro ícone nascer liberado no Compartilhar do Safari. */
  'p/', 'pc/', 'pk/', 'tudo/'
];

self.addEventListener('install', (e) => {
  e.waitUntil(
    caches.open(CACHE)
      .then(c => Promise.allSettled(ARQS.map(a => c.add(a))))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys()
      .then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (e) => {
  const req = e.request;
  if (req.method !== 'GET') return;
  if (new URL(req.url).origin !== self.location.origin) return;

  e.respondWith(
    fetch(req)
      .then(res => {
        if (res && res.ok) {
          const copia = res.clone();
          caches.open(CACHE).then(c => c.put(req, copia)).catch(() => {});
        }
        return res;
      })
      .catch(async () => {
        /* Sem rede: devolve o que houver no cache.
           ignoreSearch pra achar a página mesmo com query string diferente —
           a query não carrega acesso nenhum aqui, então isso é seguro. */
        const c = await caches.open(CACHE);
        return (await c.match(req)) ||
               (await c.match(req, { ignoreSearch: true })) ||
               Response.error();
      })
  );
});
