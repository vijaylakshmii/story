---
name: broll-select
description: Stage 4 of the video edit pipeline (capture + assets). Use when the asset plan calls for BROLL visuals or a rough-cut segment is marked as a cutaway ("cover"). Finds, scores and trims b-roll that literally illustrates the spoken line, and places it on the exact word it supports.
---

# B-roll select (stage 4)

## Sources (in order of preference)
1. The user's own footage in `source/` or `assets/broll/`.
2. Free stock with clear licenses (Pexels, Pixabay). Record the URL and license.
3. Only if nothing real fits → `genvideo`.

## Selecting
For each `BROLL` beat or `cover` segment:
1. Pull the **concrete noun or verb** from the line. ("We **cut** the **footage**" → hands on an editing timeline.) Ignore abstract filler words.
2. For each candidate, extract 3 frames (`ffmpeg -ss … -frames:v 1`) and look at them. Reject footage that's off-topic, has visible watermarks or logos, contains readable text in a different language, or would read as a generic "stock" cliché.
3. Score candidates on literalness (1–5), motion that suits the pacing (1–5), and how well it crops to 9:16 (1–5). Pick the highest score.

## Placing
- Start the clip **on the keyword's first frame** (from `transcript/words.json`), not at the start of the sentence.
- Minimum 0.8 s and maximum 2.5 s per clip in short-form. Chain clips for longer covers.
- Choose the most active 2 s of the clip (the highest frame-difference energy).
- Crop to 9:16 around the subject. Keep it at 30 fps and match the color roughly (`eq=saturation=`).

## Output
`assets/broll/<beat>.mp4` plus a `cover` entry in `edl.json`: `{"beat":"B07","asset":"assets/broll/B07.mp4","at":23.41,"dur":1.6}`. Log the source and license in `plan/asset-plan.md`.
