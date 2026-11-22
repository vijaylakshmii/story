const { chromium } = require('playwright');
const FPS=30, N=+process.argv[2];
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1920}});
await p.goto('file://'+process.cwd()+'/overlay2_built.html');await p.evaluate(()=>document.fonts.ready);
for(let i=0;i<N;i++){await p.evaluate(t=>render(t),i/FPS);const buf=await p.screenshot({omitBackground:true,type:'png'});
 if(!process.stdout.write(buf)) await new Promise(r=>process.stdout.once('drain',r));
 if(i%300==0) process.stderr.write(`frame ${i}/${N}\n`);}
await b.close();})();
