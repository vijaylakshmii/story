# Video editing pipeline skills

Every edit runs these stages in this order. Each stage is a skill. Stages marked ★ are the ones most people skip, so don't skip them.

| # | Stage | Skill(s) | Rule |
|---|-------|----------|------|
| 0 ★ | Asset plan | `asset-plan` | Classify every visual, fact-check every claim |
| 1 | Rough cut | `shortform-cutaway` | WhisperX words, the clean take of each line |
| 2 ★ | Cut audit | `cut-audit` | Check the audio, not the transcript |
| 3 | Take geometry | `take-geometry` | Measure the face, keep text off it |
| 4 | Capture + assets | `screen-capture` · `broll-select` · `genvideo` | Screens, b-roll, demo cards, generated clips |
| 5 | Style | `split-screen` · `paper-drawer` · … | The format skill + your motion-graphics kit |
| 6 | Captions | `caption-align` | On the exact frame of each word |
| 7 | Sound | `sfx-design` | SFX by what moves, on the peak |
| 8 | Render | `render-ops` | −14 LUFS, measured on the final file |
| 9 ★ | Review gate | `reel-review` | A different model watches it first |

## Shared project layout

All skills read and write the same working folder, so the stages chain together:

```
work/<project>/
  source/              raw footage (never modified)
  plan/asset-plan.md   stage 0
  transcript/words.json  stage 1 (WhisperX word timestamps)
  edl.json             stage 1–2 edit decision list
  rough.mp4            stage 1–2 assembled rough cut
  geometry.json        stage 3 face boxes + safe text zones
  assets/              stage 4 (screens/, broll/, gen/, cards/)
  style/               stage 5 format renders / overlays
  captions/captions.ass  stage 6
  sound/sfx.json       stage 7 (+ sound/sfx/ library)
  out/final.mp4        stage 8
  review/review.md     stage 9
```

**Frame rate:** use 30 fps unless the source is something else. All timing is stored in seconds (float) and converted to frames as `round(t * fps)`.

**Tools:** `ffmpeg`/`ffprobe` (required), Python 3, `whisperx` (`pip install whisperx`), `mediapipe` and `opencv-python` (for take-geometry).
