const { chromium } = require('playwright'); const path=require('path'); const fs=require('fs');
(async()=>{ const frag=fs.readFileSync('site/hokkaido-trip.html','utf8');
 fs.writeFileSync('site/_preview.html','<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><style>body{margin:0}img{max-width:100%}</style></head><body>'+frag+'</body></html>');
 const b=await chromium.launch(); const p=await b.newPage({viewport:{width:390,height:844}});
 await p.goto('file://'+path.resolve('site/_preview.html')); await p.waitForTimeout(500);
 const r=await p.evaluate(()=>{const W=innerWidth;const out=[];document.querySelectorAll('body *').forEach(e=>{const b=e.getBoundingClientRect();if(b.right>W+0.5&&!e.closest('.tblwrap')&&!e.closest('nav.jump ul'))out.push(e.tagName+'.'+e.className+' '+b.right.toFixed(1))});return [document.documentElement.scrollWidth,out.slice(0,10)]});
 console.log(JSON.stringify(r)); await b.close();})();
