---
name: paper-drawer
description: Stage 5 of the video edit pipeline (style). Motion-graphics format for CARD beats: a paper-textured card (note, document, stat, quote, source screenshot) slides out from the frame edge like a drawer, holds while the line is spoken, then slides back. Use to show facts, sources, quotes or key numbers over talking-head footage.
---

# Paper drawer (stage 5 style format)

> This skill was written from the pipeline diagram alone, without the original. The format: a paper card slides in like a drawer to show a fact, stat, quote or source, then slides away. Adjust the timings and look to match your own motion-graphics kit.

## The look
- A card on an off-white paper texture (`#F4F1EA`), with a subtle grain (noise at 4%), a 2 px warm-gray border, and a soft drop shadow (blur 24, 25% black, offset y 8).
- Typography: a bold grotesk headline (64–88 px), a mono label (28 px, accent orange `#D9734E`) for "SOURCE" / "STAT", and serif italics for quotes.
- Card width: 86% of the canvas. Height: fits the content, never above 40% of the frame.
- One idea per card, 12 words max. For a fact card, show the source domain on the card (from the `asset-plan` claim).

## Placement
- Read `geometry.json` and put the card inside `text_safe`. It must never overlap the face box.
- The drawer slides from the edge **nearest** the safe zone (bottom band → slides up from the bottom, top band → slides down from the top).

## Motion (30 fps)
| Phase | Frames | Easing |
|---|---|---|
| Slide in | 9 | ease-out cubic, overshoot 3% then settle 3f |
| Hold | until the last word of the line + 6f | slight 1° tilt drift |
| Slide out | 7 | ease-in cubic |
The slide-in starts **on the first frame of the keyword** (from `words.json`).

## Build
Preferred: render the card as a transparent PNG/WebM with Remotion or HTML + Playwright, then overlay it with ffmpeg:
```bash
ffmpeg -i rough.mp4 -i style/B04_card.png -filter_complex \
 "[0:v][1:v]overlay=x=(W-w)/2:y='if(lt(t,T0),H,if(lt(t,T0+0.3),H-(H-Y)*(1-pow(1-(t-T0)/0.3,3)),Y))':enable='between(t,T0,T1)'" ...
```
(Replace T0, T1 and Y with the keyword time, the end time and the target y. Add the slide-out the same way.)
Keep the drawer whoosh timing in `sound/sfx.json` (`sfx-design` will place the SFX on the slide's motion peak).

## Output
`style/<beat>_card.png` (or `.webm`) plus overlay timing in `edl.json`: `{"overlay":"style/B04_card.png","in":18.20,"out":20.75,"anim":"paper-drawer","edge":"bottom"}`.
