---
name: render-ops
description: Stage 8 of the video edit pipeline. Use when exporting the final video. Combines video, captions, voice, SFX and music, normalizes loudness to −14 LUFS integrated (true peak ≤ −1 dBTP) and then MEASURES the final rendered file to prove it, plus checks codec, fps, resolution and platform specs.
---

# Render (stage 8)

**Rule: −14 LUFS, measured on the final file.** Normalizing the mix isn't enough. Encoding changes levels, so measure what you actually ship.

## Targets
| Spec | Value |
|---|---|
| Loudness | −14 LUFS integrated (±0.5), true peak ≤ −1.0 dBTP |
| Video | H.264 High, yuv420p, 1080×1920, 30 fps (CFR), CRF 18 or ~12–16 Mbps |
| Audio | AAC-LC 320 kbps, 48 kHz, stereo |
| Container | MP4 with `-movflags +faststart` |

## 1. Mix
Voice is primary. Music sits −18 to −22 dB under voice (sidechain-ducked), and SFX comes from `sound/sfx_bus.wav`.

## 2. Two-pass loudnorm
```bash
# pass 1: measure
ffmpeg -i mix.wav -af loudnorm=I=-14:TP=-1.0:LRA=11:print_format=json -f null - 2> ln.txt
# pass 2: apply with the measured values
ffmpeg -i captioned.mp4 -i mix.wav -map 0:v -map 1:a \
  -af "loudnorm=I=-14:TP=-1.0:LRA=11:measured_I=..:measured_TP=..:measured_LRA=..:measured_thresh=..:offset=..:linear=true,aresample=48000" \
  -c:v libx264 -profile:v high -pix_fmt yuv420p -r 30 -crf 18 -c:a aac -b:a 320k -movflags +faststart out/final.mp4
```

## 3. Measure the final file (required)
```bash
ffmpeg -i out/final.mp4 -af ebur128=peak=true -f null - 2>&1 | tail -12
ffprobe -v error -show_entries stream=codec_name,width,height,r_frame_rate,pix_fmt,sample_rate -of compact out/final.mp4
```
- Integrated loudness must read −14.0 ±0.5 LUFS and the true peak must be ≤ −1.0 dBTP. If not, adjust and re-render. Don't just report a miss.
- Confirm the resolution, fps, pix_fmt and that A/V durations match within 1 frame.
- Write the measured numbers to `out/render-report.md`.

**Next:** `reel-review`. Nothing gets posted before the review gate.
