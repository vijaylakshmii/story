---
name: screen-capture
description: Stage 4 of the video edit pipeline (capture + assets). Use when the asset plan calls for SCREEN visuals, i.e. recording a website, app, terminal or UI demo, or cleaning up an existing screen recording (crop, zoom-to-action, cursor, speed-up) for vertical short-form video.
---

# Screen capture (stage 4)

## Recording web UIs (headless, reproducible)
Use Playwright with video recording. A scripted capture is repeatable and doesn't contain stray clicks:
```js
const { chromium } = require('playwright');
const browser = await chromium.launch();
const ctx = await browser.newContext({ viewport:{width:1080,height:1350}, deviceScaleFactor:2,
  recordVideo:{ dir:'assets/screens/', size:{width:1080,height:1350} }});
const page = await ctx.newPage();
await page.goto(url); await page.waitForTimeout(800);
// scripted actions with deliberate pauses (600–900 ms) between them
await ctx.close(); await browser.close();
```
For desktop apps, ask the user for a recording (OBS: 60 fps, CRF 18, hide notifications).

## Clean-up rules
- **Crop to the action.** Viewers on a phone can't read a full desktop. Crop so UI text is at least 28 px tall on the 1080-wide canvas.
- **Zoom-to-action:** a smooth `zoompan` or crop keyframe toward each click target, 0.4 s ease-in-out, holding 0.6 s before the click.
- **Speed:** cut the dead time. Speed up typing and loading (`setpts=0.5*PTS`) but keep the result moment at 1×.
- **Cursor:** enlarge it or add a highlight ring if it's hard to see, and hide it when idle.
- **Privacy:** blur emails, tokens, account names (`boxblur` on a region) before anything else.
- Match the duration to the beat length in `edl.json` (trim, or hold the last frame).

## Output
`assets/screens/<beat>.mp4` at 30 fps, H.264, with the beat id in the filename. Mark the beat as filled in `plan/asset-plan.md`.
