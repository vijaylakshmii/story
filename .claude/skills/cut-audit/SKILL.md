---
name: cut-audit
description: Stage 2 of the video edit pipeline. Use after a rough cut exists (edl.json / rough.mp4) to verify every cut by measuring the actual audio waveform, not the transcript. Catches clipped word onsets, chopped tails, breaths, clicks/pops and loudness jumps at cut points, then fixes the EDL.
---

# Cut audit (stage 2 ★, the stage most people skip)

**Rule: check the audio, not the transcript.** WhisperX word boundaries are routinely 30–100 ms off. A cut that looks clean in text can still chop a consonant.

## For every cut point in `edl.json`
Extract a window around each boundary at 48 kHz mono and analyze it in Python (numpy plus `ffmpeg -f f32le` piping):
```bash
ffmpeg -ss <t-0.25> -t 0.5 -i <src> -vn -ac 1 -ar 48000 -f f32le - > win.raw
```

Run these checks (10 ms RMS frames):
1. **Clipped onset:** at the `in` point, energy in the first 20 ms is already above −35 dBFS → the cut starts mid-sound. Move `in` earlier to the nearest frame below −45 dBFS (search back as far as 150 ms).
2. **Chopped tail:** at the `out` point, energy is still above −35 dBFS → a word or its decay is cut off. Move `out` later until the level falls below −45 dBFS (up to 250 ms), stopping before the next word.
3. **Breath/noise:** a 150–500 ms broadband hump (spectral flatness above 0.3) right after `in` or before `out` → trim it out or duck it by −12 dB.
4. **Click/pop:** a sample discontinuity at the join (abs jump > 0.2) → snap the cut to a zero crossing (±2 ms) and add an `afade` of 5 ms on both sides.
5. **Level jump:** short-term loudness differs by more than 3 LU across the join (`ffmpeg ... -af ebur128`) → note it for a per-segment gain in render-ops, or apply `volume=` on the segment.
6. **Room tone mismatch:** the noise floor differs by more than 6 dB between takes → flag it, and lay a continuous room-tone bed under the cut.

## Listen too
Measurement catches most problems, not all of them. Render a 1.5 s clip around each cut (`cut_<n>.wav`). Re-transcribe each clip with whisperx and confirm that the first and last words are fully recognized. A dropped or garbled word means the cut is bad.

## Output
- Updated `edl.json` (each change noted in a `"audit"` field).
- `review/cut-audit.md`: a table of cut #, timecode, issue, fix applied.
- Re-assembled `rough.mp4`.

**Next:** `take-geometry`.
