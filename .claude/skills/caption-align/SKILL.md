---
name: caption-align
description: Stage 6 of the video edit pipeline. Use when adding captions/subtitles to a cut video. Re-aligns words against the final edited audio so every caption word appears on the exact frame it is spoken, groups words into short-form chunks, places them using geometry.json, and burns them in via ASS subtitles.
---

# Captions (stage 6)

**Rule: on the exact frame of each word.** Captions that run ahead or behind by even 3 frames feel wrong.

## 1. Align against the final cut
Don't reuse the source-timeline timestamps, because the cuts moved everything. Re-run WhisperX alignment on the **edited** audio:
```bash
ffmpeg -i rough.mp4 -vn -ac 1 -ar 16000 captions/edit.wav
whisperx captions/edit.wav --model large-v3 --output_format json --output_dir captions/
```
Correct the recognized words against the script (spelling, names, numbers) and keep WhisperX's timing.

## 2. Snap to frames
`frame_in = round(start*fps)`, `frame_out = round(end*fps)`. A word becomes visible on `frame_in` and stays until the next word's `frame_in`, or until `frame_out` + 4f at the end of a phrase.

## 3. Chunk
- 1–3 words per chunk (short form), never splitting across a sentence boundary or a cut.
- Break on punctuation and natural pauses (gaps over 0.25 s).
- Highlight the active word (karaoke style: an accent color or a scale of 1.08) using ASS `\k` tags or per-word events.

## 4. Place
- Read `geometry.json` → `caption_y` for each segment. Captions must never cover the face, and must stay inside the platform-safe area.
- Font: bold sans at 72–84 px on a 1080-wide canvas, white with a 6 px black outline, or a semi-opaque box. Max line width 80% of the canvas.

## 5. Write ASS and burn
Write `captions/captions.ass` (PlayResX 1080, PlayResY 1920, per-segment `\pos(540,y)`), then:
```bash
ffmpeg -i rough.mp4 -vf "ass=captions/captions.ass" -c:v libx264 -crf 18 -c:a copy captioned.mp4
```

## Verify
Spot-check 5 random words: extract the frame at `frame_in` and the one before it, and confirm the word appears exactly on `frame_in`.
