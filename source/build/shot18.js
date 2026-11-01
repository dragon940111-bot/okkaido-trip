const { chromium } = require('playwright'); const fs=require('fs'); const path=require('path');
(async()=>{ const frag=fs.readFileSync('site/hokkaido-trip.html','utf8');
 fs.writeFileSync('site/_preview.html','<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><style>body{margin:0}img{max-width:100%}[hidden]{display:none!important}</style></head><body>'+frag+'</body></html>');
 const b=await chromium.launch(); const p=await b.newPage({viewport:{width:1280,height:900}});
 await p.goto('file://'+path.resolve('site/_preview.html')); await p.waitForTimeout(800);
 await p.evaluate(()=>{document.querySelectorAll('#swap details').forEach((d,i)=>{d.open=(i>=5);}); document.querySelectorAll('img').forEach(i=>i.loading='eager');}); await p.waitForTimeout(1500);
 await p.locator('#swap').screenshot({path:'rv/v17_swap.png'});
 await b.close(); fs.unlinkSync('site/_preview.html');})();
