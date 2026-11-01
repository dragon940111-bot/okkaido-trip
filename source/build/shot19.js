const { chromium } = require('playwright'); const fs=require('fs'); const path=require('path');
(async()=>{ const frag=fs.readFileSync('site/hokkaido-trip.html','utf8');
 fs.writeFileSync('site/_preview.html','<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><style>body{margin:0}img{max-width:100%}[hidden]{display:none!important}</style></head><body>'+frag+'</body></html>');
 const b=await chromium.launch();
 for (const [w,h,scheme,name] of [[1280,900,'light','desk'],[390,844,'dark','mob']]) {
  const p=await b.newPage({viewport:{width:w,height:h},colorScheme:scheme});
  const errs=[]; p.on('pageerror',e=>errs.push(String(e)));
  await p.goto('file://'+path.resolve('site/_preview.html')); await p.waitForTimeout(800);
  await p.evaluate(()=>{document.querySelectorAll('img').forEach(i=>i.loading='eager');}); await p.waitForTimeout(1000);
  await p.screenshot({path:`rv/v18_${name}_top.png`, clip:{x:0,y:0,width:w,height:Math.min(1900, 99999)}, fullPage:true});
  await p.evaluate(()=>{document.querySelector('#day2 details.dayd').open=true;}); await p.waitForTimeout(1200);
  const y=await p.evaluate(()=>document.querySelector('#day2 .routes').getBoundingClientRect().top+scrollY);
  await p.evaluate(y=>scrollTo(0,y-200),y); await p.waitForTimeout(600);
  await p.screenshot({path:`rv/v18_${name}_day2a.png`});
  const y2=await p.evaluate(()=>[...document.querySelectorAll('#day2 .card.act')].pop().getBoundingClientRect().top+scrollY);
  await p.evaluate(y=>scrollTo(0,y-80),y2); await p.waitForTimeout(800);
  await p.screenshot({path:`rv/v18_${name}_day2b.png`});
  await p.locator('#day2 .scenlink').first().click(); await p.waitForTimeout(900);
  const sc=await p.evaluate(()=>[document.querySelector('#scen-A details').open, Math.round(document.querySelector('#scen-A').getBoundingClientRect().top)]);
  await p.evaluate(()=>document.querySelectorAll('details').forEach(d=>d.open=true)); await p.waitForTimeout(600);
  const ov=await p.evaluate(()=>{const W=innerWidth;const o=[];document.querySelectorAll('body *').forEach(e=>{const r=e.getBoundingClientRect();if(r.right>W+0.5&&!e.closest('.tblwrap')&&!e.closest('nav.jump ul')&&!e.closest('.phs'))o.push(e.tagName+'.'+e.className)});return [document.documentElement.scrollWidth,o.slice(0,6)]});
  const broken=await p.evaluate(()=>[...document.images].filter(i=>i.complete&&i.naturalWidth===0).map(i=>i.getAttribute('src')).slice(0,5));
  console.log(name,'scenA open/top',JSON.stringify(sc),JSON.stringify(ov),'broken',JSON.stringify(broken),'errors',JSON.stringify(errs));
 }
 await b.close(); fs.unlinkSync('site/_preview.html');})();
