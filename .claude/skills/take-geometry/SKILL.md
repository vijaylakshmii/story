---
name: take-geometry
description: Stage 3 of the video edit pipeline. Use before placing any text, captions, cards or overlays on talking-head footage. Measures the speaker's face position per segment (MediaPipe) and computes safe zones so text never covers the face or platform UI. Writes geometry.json.
---

# Take geometry (stage 3)

**Rule: measure the face, keep text off it.** Never guess where the face is. Measure it on every segment, because people move between takes.

## Measure
```bash
pip install mediapipe opencv-python
```
For each segment in `edl.json`, sample frames at 5 fps and run MediaPipe Face Detection. Record a normalized bbox (0–1) for each sample, then take the **union over the segment** padded by 8%. Use the union, not the average, since the face moves.

## Platform UI safe zones (9:16, 1080×1920)
| Platform | Keep clear |
|---|---|
| Reels/TikTok | top 14% (header), bottom 22% (caption + buttons), right 12% (action rail) |
| YouTube Shorts | top 12%, bottom 20%, right 13% |

## Compute zones
- `face`: padded face union bbox.
- `text_safe`: the largest rectangle inside the platform safe area that doesn't intersect `face`. Usually the band above or below the face.
- `caption_y`: a vertical anchor for captions (stage 6). Choose the band below the face if it's at least 12% of height, otherwise the band above.
- If the face fills more than 55% of the frame height, flag `"reframe": true` and propose a crop or zoom-out (`crop`/`scale`) for that segment.

## Reframing horizontal → vertical
Crop the 9:16 window centered on the face center x (smoothed with a moving average over 1 s, so the framing doesn't jitter). Clamp it to the frame bounds.

## Output: `geometry.json`
```json
{"canvas":[1080,1920],"platform":"reels","segments":[{"beat":"B01","face":[0.31,0.22,0.69,0.55],"text_safe":[0.06,0.58,0.86,0.76],"caption_y":0.66,"reframe":false}]}
```
Every downstream skill that places pixels (`paper-drawer`, `split-screen`, `caption-align`) **must** read this file.

**Next:** `screen-capture` / `broll-select` / `genvideo`, as listed in the asset plan.
