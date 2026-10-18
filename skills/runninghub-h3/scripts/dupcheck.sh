#!/bin/zsh
# Repeated-frame ratio of a rendered video (YDIF < 2.5 between consecutive frames).
# Healthy: <= 5% (title cards / still moments). ~20%: 24->30 fps pulldown. 30-40%+: speed changes = visible "lag".
# usage: dupcheck.sh video.mp4 [start_s] [dur_s]
v=$1; ss=${2:-0}; t=${3:-99999}
ffmpeg -hide_banner -ss "$ss" -t "$t" -i "$v" -an -vf "scale=320:-1,signalstats,metadata=print:key=lavfi.signalstats.YDIF:file=-" -f null - 2>/dev/null \
 | grep YDIF | cut -d= -f2 | awk '{n++; if($1<2.5)d++} END{printf "repeated frames %d/%d = %.1f%%\n", d, n, 100*d/n}'
