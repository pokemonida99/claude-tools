#!/bin/zsh
# 從成品影片抽圖拼成一張檢查圖:每條字幕的中間點各一張,另加幾個沒有字幕的時間點。
# 用法(在單集資料夾內):  check_frames.sh <成品影片> [輸出圖]
set -e
F="$1"; OUT="${2:-src/frames/check.jpg}"
rm -rf src/frames/_chk; mkdir -p src/frames/_chk
TIMES=($(python3 - <<'EOF'
import re
t = open('subs/frames.txt').read().split('\n')
cur = 0.0; mids = []; gaps = []
for i in range(0, len(t) - 1, 2):
    if not t[i + 1].startswith('duration'): break
    d = float(t[i + 1].split()[1])
    (gaps if 'blank' in t[i] else mids).append(cur + d / 2); cur += d
gaps = [g for g in gaps if g > 1][:: max(1, len(gaps) // 4)][:4]
print(' '.join('%.2f' % x for x in sorted(mids + gaps)))
EOF
))
i=0
for t in $TIMES; do
  ffmpeg -v error -y -ss $t -i "$F" -frames:v 1 -vf scale=480:270 src/frames/_chk/$(printf %03d $i).png; i=$((i+1))
done
COLS=5; ROWS=$(( (i + COLS - 1) / COLS ))
ffmpeg -v error -y -pattern_type glob -i 'src/frames/_chk/*.png' -vf "tile=${COLS}x${ROWS}" -frames:v 1 "$OUT"
echo "$i 張 → $OUT"
