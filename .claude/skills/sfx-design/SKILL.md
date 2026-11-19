---
name: sfx-design
description: Stage 7 of the video edit pipeline (sound). Use when adding sound effects to an edit. Places SFX according to what is moving on screen (cards, zooms, cuts, transitions, text pops), timed so the sound's peak lands on the motion's peak frame, then mixes them under the voice.
---

# Sound design (stage 7)

**Rule: SFX by what moves, on the peak.** Every sound needs a visible reason, and its loudest moment lands on the frame where the motion peaks.

## 1. List the motion events
Collect them from `edl.json` and the style overlays:
| Motion | SFX type |
|---|---|
| card / drawer slide in | soft whoosh or paper slide |
| zoom / punch-in | short whoosh or riser |
| hard cut to b-roll | subtle hit or click (not on every cut) |
| text / number pop | pop, tick, or keyboard tap |
| split-screen panel in | swoosh |
| reveal / punchline | impact plus a short tail |
Don't place SFX on a cut that has no visible motion. Silence is a valid choice.

## 2. Find the motion peak frame
- For an animation: the frame of maximum velocity, or the settle/overshoot frame. Use whichever reads as the "hit".
- For a cut: the cut frame itself.
- Measured motion: frame-difference energy (`ffmpeg -vf "select='gt(scene,0)',metadata=print"`, or numpy on frame diffs). The peak is the argmax inside the event window.

## 3. Find the SFX peak
For each SFX file, compute the time of maximum RMS (10 ms frames) → `sfx_peak`.
Place it at `start = motion_peak_time − sfx_peak`. That way the peak, not the start of the file, lands on the frame.

## 4. Mix
- SFX bus at roughly −18 to −24 LUFS short-term. Never compete with speech: sidechain-duck SFX by 6 dB when voice is present (`sidechaincompress`), or just keep the levels low.
- Don't repeat the identical sample back to back. Alternate 2–3 variants.
- Fade each SFX tail (`afade=t=out:d=0.08`).

## Output
`sound/sfx.json`: `[{"event":"B04 drawer in","file":"sound/sfx/whoosh_02.wav","motion_peak":18.47,"sfx_peak":0.12,"start":18.35,"gain_db":-14}]` and a mixed `sound/sfx_bus.wav` ready for render.
SFX sources: the user's library, or freely licensed packs (record the license).
