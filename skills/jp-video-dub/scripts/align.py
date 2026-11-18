"""把一整段 TTS 依 whisper 字詞時間切回 script.json 的每一句。
用法: align.py <take名>      (SCRIPT=其他稿.json 可換稿)
輸出 vo/cut/<take>/NN.wav（去頭尾靜音的一整句）與 info.json（句內可分開擺放的停頓點）。"""
import json, sys, re, difflib, subprocess, os
import numpy as np, soundfile as sf

take = sys.argv[1]
script = json.load(open(os.environ.get('SCRIPT', 'script.json')))
wh = json.load(open(f'vo/wh/{take}.json'))
wav = f'vo/raw/{take}.wav'
if not os.path.exists(wav):
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f'vo/raw/{take}.mp3', '-ar', '44100', '-ac', '1', wav], check=True)
x, sr = sf.read(wav)
norm = lambda s: re.sub(r'[^\w]', '', s.lower()).replace('500', '五百').translate(str.maketrans('0123456789', '零一二三四五六七八九'))

chars, ct = [], []
for s in wh['segments']:
    for w in s['words']:
        t = norm(w['word'])
        for k, c in enumerate(t):
            d = (w['end'] - w['start']) / len(t)
            chars.append(c); ct.append((w['start'] + d * k, w['start'] + d * (k + 1)))
hyp = ''.join(chars)

# 以「分句」為單位對齊
units = []  # (line_idx, part_idx, text)
for li, l in enumerate(script):
    for pi, p in enumerate(l.get('parts', [[l['start'], l['zh']]])):
        units.append((li, pi, norm(p[1])))
ref = ''.join(u[2] for u in units)
r2h = {}
for a, b, n in difflib.SequenceMatcher(None, ref, hyp, autojunk=False).get_matching_blocks():
    for k in range(n): r2h[a + k] = b + k

H = int(sr * 0.01)
db = np.array([20 * np.log10(np.sqrt(np.mean(x[i:i + H] ** 2)) + 1e-9) for i in range(0, len(x) - H, H)])

def quiet(t0, t1):
    """t0..t1 之間最安靜的 50ms 的中心與其音量"""
    a, b = max(0, int(t0 / 0.01)), min(len(db) - 5, int(t1 / 0.01) + 1)
    if b <= a: return (t0 + t1) / 2, 0.0
    sm = np.array([db[i:i + 5].mean() for i in range(a, b)])
    k = int(np.argmin(sm))
    return (a + k + 2.5) * 0.01, float(sm[k])

pos, spans = 0, []
for li, pi, t in units:
    idx = [r2h[i] for i in range(pos, pos + len(t)) if i in r2h]; pos += len(t)
    spans.append((ct[idx[0]][0], ct[idx[-1]][1], len(idx) / len(t)))

cuts = []  # 每個單位之間的切點 (time, dB)
for i in range(len(units) - 1):
    cuts.append(quiet(spans[i][1] - 0.12, spans[i + 1][0] + 0.12))
bounds = [(0.0, -99)] + cuts + [(len(x) / sr, -99)]

os.makedirs(f'vo/cut/{take}', exist_ok=True)
info = []
for li, l in enumerate(script):
    us = [i for i, u in enumerate(units) if u[0] == li]
    lo, hi = bounds[us[0]][0], bounds[us[-1] + 1][0]
    seg = x[int(lo * sr):int(hi * sr)]
    d = 20 * np.log10(np.abs(seg) + 1e-9); act = np.where(d > -40)[0]
    a, b = max(0, act[0] - int(0.03 * sr)), min(len(seg), act[-1] + int(0.10 * sr))
    seg = seg[a:b]
    t0 = lo + a / sr
    # 淡入淡出避免喀聲
    f = int(0.008 * sr); seg = seg.copy(); seg[:f] *= np.linspace(0, 1, f); seg[-f:] *= np.linspace(1, 0, f)
    sf.write(f'vo/cut/{take}/{l["id"]:02d}.wav', seg, sr)
    inner = [dict(t=round(bounds[u][0] - t0, 3), db=round(bounds[u][1], 1)) for u in us[1:]]
    cov = min(spans[u][2] for u in us)
    dur = len(seg) / sr; win = l['end'] - l['start']
    fr = np.array([np.sqrt(np.mean(seg[i:i + H] ** 2)) for i in range(0, len(seg) - H, H)])
    arms = 20 * np.log10(np.sqrt(np.mean(fr[fr > 10 ** (-45 / 20)] ** 2)) + 1e-9)
    info.append(dict(id=l['id'], dur=round(dur, 3), win=round(win, 2), cov=round(cov, 2), inner=inner, arms=round(float(arms), 1)))
    print('%2d dur %.2f win %.2f %s%+.2f cov %.2f rms %.1f  cuts %s  %s' % (
        l['id'], dur, win, 'OVER ' if dur > win + 0.15 else '', dur - win, cov, arms,
        ' '.join('%.2f@%.0fdB' % (c['t'], c['db']) for c in inner), l['zh'][:12]))
json.dump(info, open(f'vo/cut/{take}/info.json', 'w'), ensure_ascii=False, indent=1)
