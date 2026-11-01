const { chromium } = require('playwright'); const fs=require('fs'); const path=require('path');
(async()=>{ const frag=fs.readFileSync('site/hokkaido-trip.html','utf8');
 fs.writeFileSync('site/_preview.html','<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><style>body{margin:0}img{max-width:100%}[hidden]{display:none!important}</style></head><body>'+frag+'</body></html>');
 const b=await chromium.launch();
 for (const [w,h,scheme,name] of [[1280,900,'light','desk'],[390,844,'dark','mob']]) {
  const p=await b.newPage({viewport:{width:w,height:h},colorScheme:scheme});
  const errs=[]; p.on('pageerror',e=>errs.push(String(e)));
  await p.goto('file://'+path.resolve('site/_preview.html')); await p.waitForTimeout(800);
  const top=await p.evaluate(()=>document.querySelector('.wrap .foldbar').getBoundingClientRect().top+scrollY);
  await p.evaluate(y=>scrollTo(0,y-70),top); await p.waitForTimeout(300);
  await p.screenshot({path:`s10_${name}_days.png`});
  await p.locator('#eatlist details.eld.n1 > summary').click(); await p.waitForTimeout(300);
  await p.locator('#eatlist details.eld.n1').screenshot({path:`s10_${name}_el1.png`});
  await p.locator('nav.jump a[href="#day2"]').click(); await p.waitForTimeout(500);
  const st=await p.evaluate(()=>[document.querySelector('#day2 details').open, document.querySelector('#day1 details').open, Math.round(document.querySelector('#day2').getBoundingClientRect().top)]);
  await p.locator('nav.jump a[href="#regions"]').click(); await p.waitForTimeout(400);
  await p.evaluate(()=>{const e=document.querySelector('#regions .foldbar'); scrollTo(0,e.getBoundingClientRect().top+scrollY-70);}); await p.waitForTimeout(300);
  await p.screenshot({path:`s10_${name}_regions.png`});
  await p.locator('#regions .rnav a').first().click(); await p.waitForTimeout(400);
  const rg=await p.evaluate(()=>document.querySelector('#regions .region details').open);
  await p.locator('#regions .foldbar button[data-fold="open"]').click();
  const allo=await p.evaluate(()=>[...document.querySelectorAll('details.regd')].every(d=>d.open));
  await p.evaluate(()=>document.querySelectorAll('details').forEach(d=>d.open=true)); await p.waitForTimeout(500);
  const ov=await p.evaluate(()=>{const W=innerWidth;const o=[];document.querySelectorAll('body *').forEach(e=>{const r=e.getBoundingClientRect();if(r.right>W+0.5&&!e.closest('.tblwrap')&&!e.closest('nav.jump ul')&&!e.closest('.phs'))o.push(e.tagName+'.'+e.className)});return [document.documentElement.scrollWidth,o.slice(0,6)]});
  console.log(name,'day2open/day1open/top',JSON.stringify(st),'regionOpenByNav',rg,'allOpen',allo,JSON.stringify(ov),'errors',JSON.stringify(errs));
 }
 await b.close(); fs.unlinkSync('site/_preview.html');})();
