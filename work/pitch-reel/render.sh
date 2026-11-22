#!/bin/bash
set -e
cd "$(dirname "$0")/style"
N=$(ffprobe -v error -count_frames -select_streams v -show_entries stream=nb_read_frames -of csv=p=0 ../base.mp4)
node render_full.js $N | ffmpeg -v error -y -i ../base.mp4 -f image2pipe -framerate 30 -c:v png -i - \
  -filter_complex "[0:v][1:v]overlay=0:0:format=auto,format=yuv420p[v]" -map "[v]" -c:v libx264 -preset medium -crf 17 -r 30 ../out/video_noaudio.mp4
echo DONE
