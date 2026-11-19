---
name: split-screen
description: Stage 5 of the video edit pipeline (style). Use for SPLIT beats or any comparison (before/after, A vs B, speaker + screen, reaction). Composes two or more sources into a vertical 9:16 layout with ffmpeg, respecting the face and safe zones from geometry.json.
---

# Split screen (stage 5 style format)

## Layouts (1080×1920)
| Layout | Use for | Geometry |
|---|---|---|
| `stack` | speaker + screen, A vs B | top 1080×960 / bottom 1080×960 |
| `stack-60` | demo is the focus | screen 1080×1150 top, face 1080×770 bottom |
| `side` | quick visual compare | two 540×1920 columns (only for simple visuals) |
| `pip` | screen with speaker commentary | full screen + 360×360 rounded face, corner kept out of UI safe zones |

## Rules
- Crop the face panel using `geometry.json`. Center the face in its panel with headroom of about 12% of the panel height.
- Put a 6 px divider (brand color or `#111`) between panels.
- Labels ("BEFORE" / "AFTER") go inside the panel, top-left, and never over a face.
- Both panels must stay in sync. Trim both sources to the same duration.
- Animate in: the second panel slides in over 8 frames with ease-out. Hard-cut out.

## ffmpeg (stack)
```bash
ffmpeg -i top.mp4 -i bottom.mp4 -filter_complex \
 "[0:v]scale=1080:960:force_original_aspect_ratio=increase,crop=1080:960[t];\
  [1:v]scale=1080:960:force_original_aspect_ratio=increase,crop=1080:960[b];\
  [t][b]vstack,drawbox=y=957:w=1080:h=6:color=0x111111:t=fill,fps=30[v]" \
 -map "[v]" -map 0:a? -c:v libx264 -crf 18 style/<beat>_split.mp4
```

## Output
`style/<beat>_split.mp4`. Update the `edl.json` segment with `"style":"style/<beat>_split.mp4"`.
