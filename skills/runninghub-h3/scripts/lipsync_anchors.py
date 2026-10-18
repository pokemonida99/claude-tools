"""Lip-sync fix: H3 re-sings the uploaded audio with its own timing, and the mouths follow that.
For each clip, align its own vocal (whisper char times) to the song's lyric char times and write a
monotonic piecewise-linear map song_rel_time -> clip_time (web/<dir>/warp.json). The render page then plays
the clip at that mapped time, so the mouth lands on the original song.
usage: python3 lipsync_anchors.py <clip.mp4> <name> <song_start> <dur> <out_json> [timeline.json]
timeline.json = {"lines":[{"text":"...","t":[char times in song seconds, null for non-CJK]}]} (whisper-aligned lyrics of the song)
Output: appends {name: [[song_rel, clip_t], ...]} to out_json and prints how many lyric chars matched
(few matches = H3 sang other words / wrong segment)."""
import sys, json, subprocess, difflib, os, tempfile
clip, name, t0, dur, outp = sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4]), sys.argv[5]
cjk = lambda c: '一' <= c <= '鿿' or '가' <= c <= '힣'
# song chars inside the window
TL = json.load(open(sys.argv[6] if len(sys.argv) > 6 else 'web/timeline_full.json'))
song = [(c, t - t0) for L in TL['lines'] for c, t in zip(L['text'], L['t']) if t is not None and cjk(c) and t0 - 0.2 <= t < t0 + dur]
# clip chars from whisper on the clip's own audio
tmp = tempfile.mkdtemp()
wav = os.path.join(tmp, 'a.wav')
subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', clip, '-vn', '-ac', '1', '-ar', '16000', wav], check=True)
prompt = ''.join(c for c, _ in song)[:200]
subprocess.run(['whisper', wav, '--model', 'medium', '--language', 'zh', '--word_timestamps', 'True', '--output_format', 'json',
                '--output_dir', tmp, '--initial_prompt', prompt], check=True, capture_output=True)
W = json.load(open(os.path.join(tmp, 'a.json')))
cl = []
for s in W['segments']:
    for w in s['words']:
        txt = w['word'].strip(); n = len(txt)
        for k, ch in enumerate(txt):
            if cjk(ch): cl.append((ch, w['start'] + (w['end'] - w['start']) * k / max(n, 1)))
# align char sequences (exact char matches only)
sm = difflib.SequenceMatcher(a=[c for c, _ in song], b=[c for c, _ in cl], autojunk=False)
pairs = []
for a, b, n in sm.get_matching_blocks():
    for i in range(n): pairs.append((song[a + i][1], cl[b + i][1]))
# keep a monotonic, plausible subset (local speed 0.6x..1.6x)
pairs.sort(); keep = [(0.0, max(0.0, pairs[0][1] - pairs[0][0]) if pairs else 0.0)]
for s, c in pairs:
    ps, pc = keep[-1]
    if s - ps < 0.15: continue
    r = (c - pc) / (s - ps)
    if 0.6 <= r <= 1.6: keep.append((s, c))
last_s, last_c = keep[-1]
keep.append((dur, min(last_c + (dur - last_s), 999)))
print(name, f'{len(pairs)} matched chars, {len(keep)} anchors;', ' '.join(f'{s:.2f}->{c:.2f}' for s, c in keep))
data = json.load(open(outp)) if os.path.exists(outp) else {}
data[name] = keep
json.dump(data, open(outp, 'w'))
