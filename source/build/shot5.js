const { chromium } = require('playwright'); const fs=require('fs'); const path=require('path');
(async()=>{ const frag=fs.readFileSync('site/hokkaido-trip.html','utf8');
 fs.writeFileSync('site/_preview.html','<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><style>body{margin:0}img{max-width:100%}[hidden]{display:none!important}</style></head><body>'+frag+'</body></html>');
 const b=await chromium.launch();
 for (const [w,h,scheme,name] of [[1280,900,'light','desk'],[390,844,'dark','mob']]) {
  const p=await b.newPage({viewport:{width:w,height:h},colorScheme:scheme});
  await p.goto('file://'+path.resolve('site/_preview.html')); await p.waitForTimeout(800);
  await p.evaluate(()=>{document.documentElement.style.scrollBehavior='auto'; document.querySelectorAll('img').forEach(i=>i.loading='eager');});
  await p.waitForTimeout(800);
  const ov=await p.evaluate(()=>{const W=innerWidth;const o=[];document.querySelectorAll('body *').forEach(e=>{const r=e.getBoundingClientRect();if(r.right>W+0.5&&!e.closest('.tblwrap')&&!e.closest('nav.jump ul')&&!e.closest('.phs'))o.push(e.tagName+'.'+e.className)});return [document.documentElement.scrollWidth,o.slice(0,6)]});
  const broken=await p.evaluate(()=>[...document.images].filter(i=>i.complete&&i.naturalWidth===0).map(i=>i.getAttribute('src')).slice(0,10));
  console.log(name,JSON.stringify(ov),'broken',JSON.stringify(broken));
  const shots=[['#day1 .it:nth-child(5)','d1lunch'],['#day2 .it:last-child','d2late'],['#day4 .it:last-child','d4sushi'],['#regions .rguide','rguide'],['#r-south','south'],['#dropped','dropped'],['#booking','booking']];
  for (const [sel,tag] of shots) { await p.evaluate(s=>{const e=document.querySelector(s); if(e) e.scrollIntoView();},sel); await p.waitForTimeout(400); await p.screenshot({path:`s4_${name}_${tag}.png`}); }
 }
 await b.close(); fs.unlinkSync('site/_preview.html');})();
