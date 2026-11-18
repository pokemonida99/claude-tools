#!/bin/zsh
# 輸出三個版本:中日字幕版、無字幕版、30MB 以下傳送版,再加一支「只有配音段落」的聽檢檔。
# 用法(在單集資料夾內,先跑過 mix.py、verify.py、subs.py):  render.sh <mix 名稱> <檔名前綴>
# 測試時可加 T=8 只輸出前 8 秒。
set -e
MIX="$1"; N="$2"; [[ -z "$N" ]] && { echo "usage: render.sh <mix> <prefix>"; exit 1; }
DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 out/${MIX}_mix.wav)
LEN=${T:-$DUR}
VC=$(ffprobe -v error -select_streams v:0 -show_entries stream=codec_name -of csv=p=0 src/src.mp4)
H=$(ffprobe -v error -select_streams v:0 -show_entries stream=height -of csv=p=0 src/src.mp4)
CRF=23; [[ $H -ge 1080 ]] && CRF=22

echo "== 字幕版"
ffmpeg -v error -y -i src/src.mp4 -f concat -safe 0 -i subs/frames.txt -i out/${MIX}_mix.wav \
  -filter_complex "[0:v][1:v]overlay=0:0:eof_action=pass[v]" -map "[v]" -map 2:a:0 \
  -c:v libx264 -preset medium -crf $CRF -pix_fmt yuv420p -c:a aac -b:a 192k -movflags +faststart -t $LEN \
  "out/${N}_中文配音_中日字幕.mp4"

echo "== 無字幕版"
if [[ "$VC" == "h264" ]]; then VOPT=(-c:v copy); else VOPT=(-c:v libx264 -preset medium -crf $CRF -pix_fmt yuv420p); fi
ffmpeg -v error -y -i src/src.mp4 -i out/${MIX}_mix.wav -map 0:v:0 -map 1:a:0 $VOPT \
  -c:a aac -b:a 192k -movflags +faststart -t $LEN "out/${N}_中文配音_無字幕.mp4"

echo "== 傳送版(目標 28MB 以內)"
VB=$(python3 -c "print(min(2500, max(300, int(28*8*1024/$LEN - 128 - 40))))")
ffmpeg -v error -y -i "out/${N}_中文配音_中日字幕.mp4" -vf scale=-2:540 -c:v libx264 -preset slow \
  -b:v ${VB}k -maxrate $((VB*3/2))k -bufsize $((VB*3))k -pix_fmt yuv420p -c:a aac -b:a 128k -movflags +faststart \
  "out/${N}_中文配音_中日字幕_傳送版.mp4"

[[ -f out/check/${MIX}_win.wav ]] && ffmpeg -v error -y -i out/check/${MIX}_win.wav -c:a aac -b:a 128k "out/聽檢_只有配音段落_${N}.m4a"
ls -la out/*.mp4 out/*.m4a 2>/dev/null
