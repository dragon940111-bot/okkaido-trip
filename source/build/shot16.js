const { chromium } = require('playwright'); const fs=require('fs'); const path=require('path');
(async()=>{ const frag=fs.readFileSync('site/hokkaido-trip.html','utf8');
 fs.writeFileSync('site/_preview.html','<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><style>body{margin:0}img{max-width:100%}[hidden]{display:none!important}</style></head><body>'+frag+'</body></html>');
 const b=await chromium.launch();
 for (const [w,h,scheme,name] of [[1280,900,'light','desk'],[390,844,'dark','mob']]) {
  const p=await b.newPage({viewport:{width:w,height:h},colorScheme:scheme});
  const errs=[]; p.on('pageerror',e=>errs.push(String(e)));
  await p.goto('file://'+path.resolve('site/_preview.html')); await p.waitForTimeout(800);
  await p.locator('header.top').screenshot({path:`rv/v15_${name}_top.png`});
  await p.locator('details.script > summary').click(); await p.waitForTimeout(200);
  const chk=await p.evaluate(()=>[document.querySelector('#bk9').checked, document.querySelector('details.script').open]);
  await p.locator('#booking').screenshot({path:`rv/v15_${name}_book.png`});
  await p.locator('#swap').screenshot({path:`rv/v15_${name}_swap.png`});
  await p.locator('#regions .warnbox').screenshot({path:`rv/v15_${name}_warn.png`});
  await p.evaluate(()=>{document.querySelector('#day1 details.dayd').open=true;}); await p.waitForTimeout(500);
  const it=p.locator('#day1 .it.k-move').nth(2); await it.scrollIntoViewIfNeeded();
  await p.evaluate(()=>{const e=document.querySelectorAll('#day1 .it.k-move')[2]; scrollTo(0,e.getBoundingClientRect().top+scrollY-300);}); await p.waitForTimeout(400);
  await p.screenshot({path:`rv/v15_${name}_moves.png`});
  await p.evaluate(()=>document.querySelectorAll('details').forEach(d=>d.open=true)); await p.waitForTimeout(500);
  const ov=await p.evaluate(()=>{const W=innerWidth;const o=[];document.querySelectorAll('body *').forEach(e=>{const r=e.getBoundingClientRect();if(r.right>W+0.5&&!e.closest('.tblwrap')&&!e.closest('nav.jump ul')&&!e.closest('.phs'))o.push(e.tagName+'.'+e.className)});return [document.documentElement.scrollWidth,o.slice(0,6)]});
  console.log(name,'checkbox/scriptOpen',JSON.stringify(chk),JSON.stringify(ov),'errors',JSON.stringify(errs));
 }
 await b.close(); fs.unlinkSync('site/_preview.html');})();
