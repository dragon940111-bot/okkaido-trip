const { chromium } = require('playwright');
(async () => {
  const fs=require('fs'); const path=require('path');
  const frag=fs.readFileSync('site/hokkaido-trip.html','utf8');
  const doc='<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><style>:root{color-scheme:light;padding-top:env(safe-area-inset-top);padding-bottom:env(safe-area-inset-bottom)}body{margin:0;font:14px system-ui}img{max-width:100%}[hidden]{display:none!important}</style></head><body>'+frag+'</body></html>';
  fs.writeFileSync('site/_preview.html',doc);
  const b=await chromium.launch();
  for (const [w,h,scheme,name] of [[1280,900,'light','desk'],[390,844,'dark','mob']]) {
    const p=await b.newPage({viewport:{width:w,height:h},colorScheme:scheme});
    await p.goto('file://'+path.resolve('site/_preview.html')); await p.waitForTimeout(800);
    const sw=await p.evaluate(()=>[document.documentElement.scrollWidth,document.body.scrollWidth,innerWidth]);
    console.log(name,'scrollWidth',sw);
    await p.screenshot({path:`shot_${name}.png`,fullPage:false});
    for (const id of ['day3','day4','r-north','dropped']) { await p.evaluate(i=>{document.documentElement.style.scrollBehavior='auto';document.getElementById(i).scrollIntoView();},id); await p.waitForTimeout(400); await p.screenshot({path:`shot_${name}_${id}.png`}); }
  }
  await b.close();
})();
