---
name: reel-review
description: Stage 9 of the video edit pipeline, the review gate. Use after render-ops, before anything is published. A different model than the one that made the edit watches the final file and reviews it (hook, pacing, captions vs audio, text over face, claims, audio, specs) and returns pass/fail with timestamped notes.
---

# Review gate (stage 9 ★, the stage most people skip)

**Rule: a different model watches it first.** The model that made the edit is blind to its own mistakes, so the reviewer must be a separate model with fresh context.

## How to get a different model
In order of preference:
1. A video-capable model or tool connected in this session that can watch the actual file (for example, a video-review MCP tool).
2. A subagent with a **different model** than the editing session (use the Agent tool with a `model` override, such as `sonnet` when the editor is Opus). Give it **only** the review packet below, not the edit history.
3. If neither is possible, tell the user that the gate wasn't independent.

## Build the review packet (`review/packet/`)
The reviewer gets only what a viewer would get:
- Frames: 2 fps contact sheets (`ffmpeg -vf "fps=2,scale=270:-1,tile=6x5" review/packet/sheet_%02d.png`), plus a full-res frame at every cut.
- A fresh transcript of `out/final.mp4` (re-run whisperx, so the reviewer doesn't reuse the edit's own transcript).
- `out/render-report.md` (loudness and specs) and the claims list from `plan/asset-plan.md`.

## Reviewer checklist (pass to the reviewer verbatim)
1. **Hook:** do the first 1.5 s give a clear reason to keep watching? Is there visual change within 2 s?
2. **Pacing:** any dead air over 0.4 s, or a static shot over 3 s?
3. **Cuts:** any audible chopped words, pops or breaths (check against the transcript)?
4. **Geometry:** does any text, caption or card overlap the face or the platform UI zones?
5. **Captions:** do they match the spoken words? Any spelling or name errors?
6. **Claims:** is every on-screen and spoken claim in the verified list? Is any synthetic (GEN) footage presented as real?
7. **Sound:** is every SFX motivated by visible motion? Is the voice always intelligible?
8. **Specs:** is the measured loudness −14 ±0.5 LUFS with TP ≤ −1 dBTP? 1080×1920 at 30 fps?
9. **Ending:** does it land cleanly, with no cut-off last word or abrupt black?

## Output: `review/review.md`
`VERDICT: PASS | FAIL`, followed by a table of timecode, severity (blocker/fix/nit), issue and suggested fix.
**Any blocker means FAIL.** Send the video back to the stage that owns the problem, re-render, and review again.
