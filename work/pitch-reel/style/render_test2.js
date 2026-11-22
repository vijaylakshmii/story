const { chromium } = require('playwright');
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1920}});
await p.goto('file://'+process.cwd()+'/overlay2_built.html');await p.evaluate(()=>document.fonts.ready);
for(const t of process.argv.slice(2)){await p.evaluate(t=>render(+t),t);await p.screenshot({path:`/tmp/claude-0/-home-user-story/12afa795-050c-5329-99ca-6f019a2a2d82/scratchpad/ov_${t}.png`,omitBackground:true});}
await b.close();})();
