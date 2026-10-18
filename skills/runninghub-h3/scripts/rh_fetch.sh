#!/bin/zsh
# Download finished RunningHub outputs (mp4 only, never zip) and print duration / size so you can
# tell which task each file is (durations differ per requested length: 5s->5.17, 7s->7.29, 8s->8.0,
# 9s->9.42, 10s->10.13, 13s->13.67, 14s->14.38, 15s->15.08, 16s->16.5, 21s->21.46, 22s->22.17, 23s->23.58, 30s->~30).
# usage: rh_fetch.sh <out_dir> <MiniMaxH3_xxx.mp4 or name without .mp4> ...
# Get the names with the JS snippet "list new outputs" in SKILL.md (user-center page).
# RH_BASE = your account's output URL prefix (per account). Find it once: on the user-center page, copy any finished
# video's src and drop the file name, e.g. export RH_BASE=https://rh-hk-images.xiaoyaoyou.com/<your-id>/output
BASE=${RH_BASE:?set RH_BASE to your RunningHub output URL prefix (see comment above)}
out=$1; shift
mkdir -p "$out"
for n in "$@"; do
  f=${n%.mp4}.mp4
  curl -s -o "$out/$f" "$BASE/$f" || { echo "FAIL $f"; continue; }
  info=$(ffprobe -v error -select_streams v:0 -show_entries stream=width,height -show_entries format=duration -of csv=p=0 "$out/$f" | tr '\n' ' ')
  echo "$f  $info"
done
