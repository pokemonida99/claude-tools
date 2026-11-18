#!/bin/zsh
# 前置作業:下載(或用本機檔)→ 抽音軌 → Demucs 分離 → 日文逐字稿 → 說話區段 → 畫面總覽圖
# 用法(在新的單集資料夾內):  prep.sh <YouTube 網址 或 本機影片路徑>
set -e
SRC="$1"; [[ -z "$SRC" ]] && { echo "usage: prep.sh <url|file>"; exit 1; }
HERE="${0:A:h}"
YTDLP=${YTDLP:-$HOME/claude-tools/ytdlp/bin/yt-dlp}
mkdir -p src stems vo/raw vo/wh out/check subs src/frames

if [[ -f "$SRC" ]]; then
  cp "$SRC" src/src.mp4
else
  (cd src && "$YTDLP" --no-progress --no-playlist \
     -f "137+140/bv*[vcodec^=avc1][height<=1080]+ba[ext=m4a]/b" --merge-output-format mp4 \
     -o "src.%(ext)s" --write-auto-subs --sub-langs "ja.*,ja" --sub-format vtt "$SRC")
fi
ffprobe -v error -show_entries format=duration:stream=codec_name,width,height,r_frame_rate -of csv=p=0 src/src.mp4

echo "== 抽音軌"
ffmpeg -v error -y -i src/src.mp4 -vn -ac 2 -ar 44100 src/orig.wav

echo "== Demucs 分離人聲(CPU,約 1~2 分鐘)"
uvx --python 3.11 --with "torch==2.5.1" --with "torchaudio==2.5.1" --with soundfile --from demucs \
  demucs -d cpu -n htdemucs_ft --two-stems vocals -o stems src/orig.wav > stems/demucs.log 2>&1
ls stems/htdemucs_ft/orig/

echo "== 日文逐字稿(在人聲軌上跑)"
ffmpeg -v error -y -i stems/htdemucs_ft/orig/vocals.wav -ac 1 -ar 16000 src/vocals16k.wav
WOPT=(); [[ -n "$JA_PROMPT" ]] && WOPT=(--initial_prompt "$JA_PROMPT")
whisper src/vocals16k.wav --model medium --language ja --word_timestamps True --output_format json \
  --output_dir src --condition_on_previous_text False $WOPT > /dev/null 2>&1
python3 - <<'EOF'
import json
for s in json.load(open('src/vocals16k.json'))['segments']:
    print('%7.2f-%7.2f nsp=%.2f %s' % (s['start'], s['end'], s['no_speech_prob'], s['text']))
EOF

echo "== 說話區段(分句時間用這個)"
uvx --python 3.11 --with numpy --with soundfile python "$HERE/vad.py" -33

echo "== 畫面總覽圖 src/frames/sheet.jpg(每 9 秒一張,找片中標題字)"
ffmpeg -v error -y -i src/src.mp4 -vf "fps=1/9,scale=384:216,tile=6x5" -frames:v 1 src/frames/sheet.jpg
echo "done"
