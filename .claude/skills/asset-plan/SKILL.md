---
name: asset-plan
description: Stage 0 of the video edit pipeline. Use before any cutting starts, when the user hands over a script, transcript, or raw footage for a video/reel/short. Classifies every visual the video needs and fact-checks every claim made in it, producing plan/asset-plan.md.
---

# Asset plan (stage 0 ★, the stage most people skip)

**Rule: classify every visual, fact-check every claim.** Nothing gets cut until the plan exists.

## Inputs
- Script, outline, or transcript (if there's only footage, run a quick `whisperx` pass first; see `shortform-cutaway`).
- Raw footage in `work/<project>/source/`.

## Steps
1. **Split the script into beats**, one beat per sentence or idea. Number them `B01, B02, …`.
2. **Classify the visual for every beat.** Give each beat exactly one primary type:
   - `A-ROLL`: talking head, nothing else.
   - `SCREEN`: screen recording → `screen-capture`
   - `BROLL`: stock or own footage that illustrates the line → `broll-select`
   - `GEN`: AI-generated clip (only when nothing real exists) → `genvideo`
   - `CARD`: text/demo card, stat, quote, or document → style kit (`paper-drawer`, etc.)
   - `SPLIT`: two things compared side by side → `split-screen`
   Add the source if one is known (file path, URL, or "needs capture").
3. **Fact-check every claim.** Pull out every factual statement (numbers, dates, names, "X is the first/only/biggest", quotes, product features). For each one:
   - Verify it with a web search or a primary source. Record the source URL.
   - Mark it `✅ verified`, `⚠️ needs softening` (and give a suggested rewording), or `❌ wrong` (and give the correction).
   - Never mark a claim verified from memory alone.
4. **List the gaps:** assets that don't exist yet, claims that need a re-record.

## Output: `plan/asset-plan.md`
```markdown
# Asset plan: <project>
| Beat | Line (short) | Visual | Source / action | Claims |
|------|--------------|--------|-----------------|--------|
| B01 | "Most editors skip…" | A-ROLL | source/take1.mp4 | — |
| B02 | "WhisperX is 70x realtime" | CARD | stat card | C1 |

## Claims
- C1 "WhisperX is 70x realtime" — ✅ verified — <url>

## Gaps / blockers
- B05 needs a screen capture of the settings page
```

**Next:** if any claim is `❌`, stop and flag it to the user. Otherwise go to `shortform-cutaway`.
