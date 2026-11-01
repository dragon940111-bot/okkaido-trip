const { chromium } = require('playwright'); const fs=require('fs'); const path=require('path');
(async()=>{ const frag=fs.readFileSync('site/hokkaido-trip.html','utf8');
 fs.writeFileSync('site/_preview.html','<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><style>body{margin:0}img{max-width:100%}[hidden]{display:none!important}</style></head><body>'+frag+'</body></html>');
 const b=await chromium.launch();
 for (const [w,h,scheme,name] of [[1280,900,'light','desk'],[390,844,'dark','mob']]) {
  const p=await b.newPage({viewport:{width:w,height:h},colorScheme:scheme});
  await p.goto('file://'+path.resolve('site/_preview.html')); await p.waitForTimeout(800);
  await p.locator('#detail').screenshot({path:`s12_${name}_head.png`});
  await p.evaluate(()=>{document.querySelector('#day1 details.dayd').open=true;}); await p.waitForTimeout(500);
  await p.locator('#day1 .it').filter({hasText:'1985'}).first().locator('details.alts').screenshot({path:`s12_${name}_alts.png`});
  const ov=await p.evaluate(()=>{const W=innerWidth;const o=[];document.querySelectorAll('body *').forEach(e=>{const r=e.getBoundingClientRect();if(r.right>W+0.5&&!e.closest('.tblwrap')&&!e.closest('nav.jump ul')&&!e.closest('.phs'))o.push(e.tagName+'.'+e.className)});return [document.documentElement.scrollWidth,o.slice(0,6)]});
  console.log(name,JSON.stringify(ov));
 }
 await b.close(); fs.unlinkSync('site/_preview.html');})();
