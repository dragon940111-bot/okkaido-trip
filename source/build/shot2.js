const { chromium } = require('playwright'); const fs=require('fs'); const path=require('path');
(async()=>{ const frag=fs.readFileSync('site/hokkaido-trip.html','utf8');
 fs.writeFileSync('site/_preview.html','<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><style>body{margin:0}img{max-width:100%}[hidden]{display:none!important}</style></head><body>'+frag+'</body></html>');
 const b=await chromium.launch();
 for (const [w,h,scheme,name] of [[1280,900,'light','desk'],[390,844,'dark','mob']]) {
  const p=await b.newPage({viewport:{width:w,height:h},colorScheme:scheme});
  await p.goto('file://'+path.resolve('site/_preview.html')); await p.waitForTimeout(600);
  await p.evaluate(()=>{document.documentElement.style.scrollBehavior='auto'; document.querySelectorAll('#day3 details.alts')[0].open=true;});
  const ov=await p.evaluate(()=>{const W=innerWidth;const o=[];document.querySelectorAll('body *').forEach(e=>{const r=e.getBoundingClientRect();if(r.right>W+0.5&&!e.closest('.tblwrap')&&!e.closest('nav.jump ul'))o.push(e.tagName+'.'+e.className)});return [document.documentElement.scrollWidth,o.slice(0,6)]});
  console.log(name,JSON.stringify(ov));
  for (const sel of ['#day4 .it:nth-child(2)','#day1 details.alts']) { await p.evaluate(s=>document.querySelector(s).scrollIntoView(),sel); await p.waitForTimeout(300); await p.screenshot({path:`s2_${name}_${sel.replace(/[^a-z0-9]/gi,'')}.png`}); }
 }
 await b.close(); fs.unlinkSync('site/_preview.html');})();
