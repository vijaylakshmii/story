#!/bin/bash
# Remove dead air from the finished render (video + audio together), mux, and measure.
set -e
cd "$(dirname "$0")"
K="0.36 14.10 14.40 34.15 34.40 85.633"
read a b c d e f <<< "$K"
ffmpeg -v error -y -i out/video_noaudio.mp4 -i sound/master.wav -filter_complex "\
[0:v]trim=$a:$b,setpts=PTS-STARTPTS[v1];[0:v]trim=$c:$d,setpts=PTS-STARTPTS[v2];[0:v]trim=$e:$f,setpts=PTS-STARTPTS[v3];\
[1:a]atrim=$a:$b,asetpts=PTS-STARTPTS,afade=t=in:d=0.01,afade=t=out:st=$(echo "$b-$a-0.01"|bc):d=0.01[a1];\
[1:a]atrim=$c:$d,asetpts=PTS-STARTPTS,afade=t=in:d=0.01,afade=t=out:st=$(echo "$d-$c-0.01"|bc):d=0.01[a2];\
[1:a]atrim=$e:$f,asetpts=PTS-STARTPTS,afade=t=in:d=0.01[a3];\
[v1][a1][v2][a2][v3][a3]concat=n=3:v=1:a=1[v][a]" -map "[v]" -map "[a]" \
 -c:v libx264 -preset medium -crf 17 -pix_fmt yuv420p -r 30 -c:a aac -b:a 320k -ar 48000 -movflags +faststart out/final.mp4
ffprobe -v error -show_entries format=duration:stream=codec_name,width,height,r_frame_rate -of compact out/final.mp4
ffmpeg -nostats -i out/final.mp4 -af ebur128=peak=true -f null - 2>&1 | grep -E "^\s+(I|Peak):"
