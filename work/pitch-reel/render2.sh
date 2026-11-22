#!/bin/bash
# Full render v2: base2 + overlay (frame-by-frame) + face-tracked bubbles, then audio + dead-air trim.
set -e
cd "$(dirname "$0")"
python3 -c "
s=open('style/overlay2.html').read().replace('__CAPS__',open('style/captions.json').read()).replace('__TL__',open('style/timeline2.json').read()); open('style/overlay2_built.html','w').write(s)"
N=$(ffprobe -v error -count_frames -select_streams v -show_entries stream=nb_read_frames -of csv=p=0 base2.mp4)
B=$(python3 -c "
import json;E=json.load(open('edl2.json'))
print(' '.join(f\"{b['t']}:{b['d']}\" for b in E['bubbles']))")
read b0 b1 b2 <<< "$B"
t0=${b0%%:*}; t1=${b1%%:*}; t2=${b2%%:*}
d0=${b0##*:}; d1=${b1##*:}; d2=${b2##*:}
cd style && sed 's/overlay_built.html/overlay2_built.html/' render_full.js > render_full2.js && cd ..
(cd style && node render_full2.js $N) | ffmpeg -v error -y -i base2.mp4 -f image2pipe -framerate 30 -c:v png -i - \
  -filter_complex "[0:v][1:v]overlay=0:0:format=auto,format=yuv420p[v]" -map "[v]" -frames:v $N -c:v libx264 -preset medium -crf 17 -r 30 out/video_noaudio2.mp4
echo RENDERED
