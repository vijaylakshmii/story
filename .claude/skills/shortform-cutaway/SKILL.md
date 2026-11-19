---
name: shortform-cutaway
description: Stage 1 of the video edit pipeline, the rough cut. Use when cutting raw talking-head footage (often multiple takes) into a tight short-form video. Transcribes with WhisperX word timestamps, picks the clean take of each scripted line, and builds an edit decision list (edl.json) plus rough.mp4.
---

# Rough cut (stage 1)

**Rule: WhisperX words, the clean take of each line.**

## 1. Transcribe with word timestamps
```bash
pip install whisperx   # once
ffmpeg -i source/take.mp4 -vn -ac 1 -ar 16000 transcript/take.wav
whisperx transcript/take.wav --model large-v3 --align_model WAV2VEC2_ASR_LARGE_LV60K_960H \
  --output_format json --output_dir transcript/ --compute_type int8
```
Merge every take into `transcript/words.json`: `[{src, word, start, end, score}]`.
Use the aligned **word** times, never segment times.

## 2. Find every take of every line
- Match each script beat (from `plan/asset-plan.md`) against the transcript using fuzzy matching on normalized words (lowercase, punctuation stripped).
- A line is usually said several times. Collect all candidates.

## 3. Pick the clean take
Score each candidate and keep the best one:
- Word match against the script (fewer missing or extra words wins).
- No filler (`um`, `uh`, `like`, restarts, repeated words).
- Mean WhisperX `score` (alignment confidence). Low scores often mean a mumble.
- Later takes win ties, because speakers usually improve.
Once a take is chosen, never splice words from different takes inside a single line unless the user asks.

## 4. Set cut points
- `in` = first word `start` − 0.08 s, `out` = last word `end` + 0.12 s (pad, then let `cut-audit` refine).
- Remove gaps longer than 0.35 s between lines (short-form pacing).
- For a cutaway (B-roll or screen over the speaker's audio), mark the segment `"cover": "B07"` so stage 4 can fill it. This hides jump cuts.

## 5. Write `edl.json` and assemble
```json
{"fps":30,"segments":[{"beat":"B01","src":"source/take3.mp4","in":12.48,"out":15.91,"cover":null}]}
```
Assemble with one ffmpeg concat (trim and atrim per segment, then `concat=n=N:v=1:a=1`). Re-encode, don't stream-copy, so cuts land frame-accurately:
```bash
ffmpeg -i source/take3.mp4 -filter_complex "[0:v]trim=12.48:15.91,setpts=PTS-STARTPTS[v0];[0:a]atrim=12.48:15.91,asetpts=PTS-STARTPTS[a0];...;[v0][a0][v1][a1]concat=n=2:v=1:a=1[v][a]" \
  -map "[v]" -map "[a]" -c:v libx264 -crf 18 -r 30 -c:a aac -ar 48000 rough.mp4
```

**Next:** `cut-audit`. The transcript says the cut is clean, but the audio might not be.
