const { chromium } = require('playwright'); const fs=require('fs'); const path=require('path');
(async()=>{ const frag=fs.readFileSync('site/hokkaido-trip.html','utf8');
 fs.writeFileSync('site/_preview.html','<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><style>body{margin:0}img{max-width:100%}[hidden]{display:none!important}</style></head><body>'+frag+'</body></html>');
 const b=await chromium.launch();
 for (const [w,h,scheme,name] of [[1280,900,'light','desk'],[390,844,'light','mob']]) {
  const p=await b.newPage({viewport:{width:w,height:h},colorScheme:scheme});
  await p.goto('file://'+path.resolve('site/_preview.html')); await p.waitForTimeout(800);
  await p.evaluate(()=>{document.querySelectorAll('img').forEach(i=>i.loading='eager'); document.querySelector('nav.jump').style.position='static';}); await p.waitForTimeout(1500);
  await p.screenshot({path:`rv/${name}_full.png`, fullPage:true});
  // day1 opened
  await p.evaluate(()=>{document.querySelector('#day1 details.dayd').open=true;}); await p.waitForTimeout(800);
  await p.locator('#day1').screenshot({path:`rv/${name}_day1.png`});
 }
 await b.close(); fs.unlinkSync('site/_preview.html');})();
