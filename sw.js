// 버전 76b173903a
const C='hk-trip';
self.addEventListener('install',e=>{self.skipWaiting();e.waitUntil(caches.open(C).then(c=>c.addAll(['./','index.html','manifest.webmanifest','icon-192.png','icon-512.png'])));});
self.addEventListener('activate',e=>e.waitUntil(self.clients.claim()));
async function fresh(req){const c=await caches.open(C);const old=await c.match('index.html');
  try{const ctl=new AbortController();const t=setTimeout(()=>ctl.abort(),8000);
    const r=await fetch('index.html',{cache:'no-store',signal:ctl.signal});clearTimeout(t);
    if(r.ok){const et=r.headers.get('etag')||r.headers.get('last-modified')||'';const oe=old?(old.headers.get('etag')||old.headers.get('last-modified')||''):'';
      await c.put('index.html',r.clone());
      if(old&&et&&et!==oe){(await self.clients.matchAll()).forEach(cl=>cl.postMessage({type:'updated'}));}
      return r;}
  }catch(e){}
  return old||Response.error();}
self.addEventListener('fetch',e=>{const u=new URL(e.request.url);
  if(e.request.mode==='navigate'||u.pathname.endsWith('/index.html')||u.pathname.endsWith('/')){e.respondWith(fresh(e.request));return;}
  if(u.origin===location.origin){e.respondWith(caches.match(e.request).then(r=>r||fetch(e.request)));}
});
