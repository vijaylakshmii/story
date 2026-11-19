---
name: genvideo
description: Stage 4 of the video edit pipeline (capture + assets). Use when the asset plan calls for a GEN visual, i.e. a shot that can't be filmed, captured or found as b-roll. Writes tight prompts for an AI video generator, generates short clips, and conforms them to the edit (fps, size, duration).
---

# Generated video (stage 4)

**Use this last.** Real footage → screen capture → b-roll → *then* generation. Never generate something that pretends to be a real event, a real person, or real evidence for a claim.

## Prompting
One shot per prompt. Structure the prompt as:
`[subject] [action] in [setting], [camera move], [lens/framing], [lighting], [style], vertical 9:16, no text`
- Describe motion explicitly ("slow push-in", "static tripod").
- Always add "no text, no logos, no watermark". Generators garble text, so add any text later in the style stage.
- Keep it to 3–5 s and cut it down to the best 1–2 s.

## Generating
Use whatever generator is connected in this session (look for a video-generation MCP tool, such as the vidIQ `generate_video` or Canva `create-video` tools), or one the user has an API key for. If none is available, deliver the prompts in `assets/gen/prompts.md` for the user to run.

## Conform
```bash
ffmpeg -i raw.mp4 -vf "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30" \
  -t <dur> -c:v libx264 -crf 18 -an assets/gen/<beat>.mp4
```
Look at 3 frames before you use a clip. Reject warped hands or faces, morphing objects, and garbled text.

## Output
`assets/gen/<beat>.mp4`, with the prompt and tool recorded in `plan/asset-plan.md`. Label the beat `GEN` so the review gate knows it's synthetic.
