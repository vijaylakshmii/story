---
name: watch
description: Watch a local video file. Use when the user asks to watch, look at, review, describe, summarize or time-code a video file (mp4, mov, webm, mkv…) on disk, or when another skill (e.g. reel-review, cut-audit) needs to "see" a video. Extracts frames with ffmpeg, transcribes the audio, then views the frames and returns a timestamped breakdown.
argument-hint: <path/to/video> [focus, e.g. "hook" or "captions"]
---

# /watch: watch a local video

You can't play a video directly, so you watch it by **looking at frames** (Read tool on PNGs) and **reading a transcript** of the audio, both lined up on the same timeline.

## 0. Setup
- The input is a local file path. If the user gave none, look for uploads or `work/*/out/*.mp4` and ask if it's ambiguous.
- Work folder: `<scratchpad>/watch/<video-basename>/` (keep it out of the repo).

## 1. Probe
```bash
ffprobe -v error -show_entries format=duration:stream=codec_type,width,height,r_frame_rate -of compact "$VIDEO"
```
Note the duration, resolution, fps and whether there's an audio stream.

## 2. Extract frames
Pick a sampling rate based on duration, so you look at ~30–60 frames total:
| Duration | Rate |
|---|---|
| ≤ 60 s | 1 fps (plus every 0.5 s for the first 3 s, which is the hook) |
| 1–5 min | 1 frame / 3 s |
| > 5 min | 1 frame / 10 s, plus scene changes |

```bash
ffmpeg -v error -i "$VIDEO" -vf "fps=1,scale=540:-2" -q:v 3 frames/f_%04d.jpg
# scene-change frames (catches cuts the fixed rate misses)
ffmpeg -v error -i "$VIDEO" -vf "select='gt(scene,0.3)',showinfo,scale=540:-2" -vsync vfr frames/s_%04d.jpg 2> scenes.log
grep -o 'pts_time:[0-9.]*' scenes.log | cut -d: -f2 > scene_times.txt
```
For a quick overview, also make contact sheets (`fps=1,scale=270:-2,tile=5x4`), and read those first.

Frame `f_NNNN.jpg` sits at time `(NNNN-1)/fps` seconds.

## 3. Transcribe the audio
Skip this if there's no audio stream.
```bash
ffmpeg -v error -i "$VIDEO" -vn -ac 1 -ar 16000 audio.wav
```
- Preferred: `whisperx audio.wav --model large-v3 --output_format json` (word timestamps).
- Fallback: `whisper audio.wav --model small --word_timestamps True --output_format json` (`pip install openai-whisper`).
- If neither installs, still measure the audio: `ffmpeg -i audio.wav -af silencedetect=n=-35dB:d=0.4 -f null -` (speech vs silence) and `ebur128` (loudness). Say that there's no transcript.

## 4. Watch
Open the frames with the Read tool, the contact sheets first, then the individual frames at the hook, at every scene change, and wherever the transcript suggests something happens. Actually look at them. Don't describe frames you haven't opened.

## 5. Report
Lead with a 2–3 sentence summary, then:

```markdown
**File:** name · 0:42 · 1080×1920 · 30 fps · audio yes

| Time | What's on screen | What's said | Notes |
|------|------------------|-------------|-------|
| 0:00–0:02 | Close-up face, text "STOP DOING THIS" | "Most editors…" | hook |
| 0:02 | cut → screen recording | … | |
```
Then add the notes relevant to the user's focus, if they gave one:
- **Hook** (first 3 s): is there a clear reason to keep watching?
- **Cuts / pacing:** cut count, average shot length, dead air over 0.4 s (from silencedetect).
- **On-screen text:** legible? Covering the face or platform UI?
- **Captions vs speech:** mismatches.
- **Audio:** integrated loudness and silence gaps.

Always give exact timestamps, so the user (or the next pipeline skill) can jump straight to them.

## Limits (say these when they matter)
- You only saw sampled frames, so motion between samples (fast animations, flashes) can be missed. Sample more densely around a moment if asked.
- You hear the audio only through the transcript and measurements. Music, tone and SFX are inferred, not heard.
