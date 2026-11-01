const { chromium } = require('playwright'); const fs=require('fs'); const path=require('path');
(async()=>{ const frag=fs.readFileSync('site/hokkaido-trip.html','utf8');
 fs.writeFileSync('site/_preview.html','<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><style>body{margin:0}img{max-width:100%}[hidden]{display:none!important}</style></head><body>'+frag+'</body></html>');
 const b=await chromium.launch();
 for (const [w,h,scheme,name] of [[1280,900,'light','desk'],[390,844,'dark','mob']]) {
  const p=await b.newPage({viewport:{width:w,height:h},colorScheme:scheme});
  const errs=[]; p.on('pageerror',e=>errs.push(String(e)));
  await p.goto('file://'+path.resolve('site/_preview.html')); await p.waitForTimeout(800);
  await p.evaluate(()=>{document.querySelector('#day2 details.dayd').open=true;}); await p.waitForTimeout(400);
  await p.locator('#day2 details.freed').screenshot({path:`s14_${name}_closed.png`});
  await p.evaluate(()=>{document.querySelector('#day2 details.freed').open=true;}); await p.waitForTimeout(300);
  await p.locator('#day2 details.freed').screenshot({path:`s14_${name}_open.png`});
  await p.evaluate(()=>document.querySelectorAll('details').forEach(d=>d.open=true)); await p.waitForTimeout(600);
  const ov=await p.evaluate(()=>{const W=innerWidth;const o=[];document.querySelectorAll('body *').forEach(e=>{const r=e.getBoundingClientRect();if(r.right>W+0.5&&!e.closest('.tblwrap')&&!e.closest('nav.jump ul')&&!e.closest('.phs'))o.push(e.tagName+'.'+e.className)});return [document.documentElement.scrollWidth,o.slice(0,6)]});
  const broken=await p.evaluate(()=>[...document.images].filter(i=>i.complete&&i.naturalWidth===0).length);
  console.log(name,JSON.stringify(ov),'broken',broken,'errors',JSON.stringify(errs));
 }
 await b.close(); fs.unlinkSync('site/_preview.html');})();
