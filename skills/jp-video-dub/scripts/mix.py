"""合成中文配音音軌。
用法: mix.py <輸出名> <take> [id=其他take ...]   例: mix.py james james_b 6=james_a
做法:
  背景 = 原音軌 − m(t)·人聲軌   (m 只在日文旁白時段為 1,其餘時間完全保留原音)
  配音 = 每句放在原句開始的時間點;句內有真正停頓的地方,分段對到原本分句的時間
  音量 = 每句比照原旁白該句的音量
"""
import json, sys, os
import numpy as np, soundfile as sf

out = sys.argv[1]; base = sys.argv[2]
over = dict(a.split('=') for a in sys.argv[3:])
script = json.load(open('script.json'))
orig, sr = sf.read('src/orig.wav')
voc, _ = sf.read('stems/htdemucs_ft/orig/vocals.wav')
n = min(len(orig), len(voc)); orig, voc = orig[:n], voc[:n]
H = int(sr * 0.01)

def active_rms(y):
    y = y.mean(1) if y.ndim > 1 else y
    fr = np.array([np.sqrt(np.mean(y[i:i + H] ** 2)) for i in range(0, len(y) - H, H)])
    a = fr[fr > 10 ** (-45 / 20)]
    return 20 * np.log10(np.sqrt(np.mean(a ** 2)) + 1e-9) if len(a) else -99

# ---- 背景:只在旁白時段抽掉人聲 ----
PRE, POST, RAMP = 0.35, 0.50, 0.15
wins = [[l['start'] - PRE, l['end'] + POST] for l in script]
merged = [wins[0]]
for a, b in wins[1:]:
    if a - merged[-1][1] < 0.8: merged[-1][1] = max(merged[-1][1], b)
    else: merged.append([a, b])
m = np.zeros(n)
t = np.arange(n) / sr
for a, b in merged:
    m = np.maximum(m, np.clip((t - (a - RAMP)) / RAMP, 0, 1) * np.clip(((b + RAMP) - t) / RAMP, 0, 1))
bed = orig - voc * m[:, None]

# ---- 配音 ----
dub = np.zeros(n)
report = []
for l in script:
    tk = over.get(str(l['id']), base)
    info = {i['id']: i for i in json.load(open(f'vo/cut/{tk}/info.json'))}[l['id']]
    y, sr2 = sf.read(f'vo/cut/{tk}/{l["id"]:02d}.wav'); assert sr2 == sr
    # 音量比照原旁白
    target = active_rms(voc[int(l['start'] * sr):int((l['end'] + 0.2) * sr)])
    gain = float(np.clip(target - info['arms'] + 1.0, -8, 14))
    y = y * 10 ** (gain / 20)
    # 句內分段:只在真的有停頓(< -38 dB)的地方切開
    parts = l['parts']
    cuts = [0] + [int(c['t'] * sr) if c['db'] < -38 else None for c in info['inner']] + [len(y)]
    chunks = []  # (目標開始時間, 片段)
    i = 0
    while i < len(parts):
        j = i + 1
        while cuts[j] is None: j += 1
        chunks.append((parts[i][0], y[cuts[i]:cuts[j]]))
        i = j
    # 由後往前算最晚可以開始的時間,確保整句不超出原時段太多
    nxt = next((x['start'] for x in script if x['start'] > l['start']), 1e9)
    limit = max(l['end'] + 0.35, min(nxt - 0.3, l['end'] + 1.5))
    latest = []
    for tgt, c in reversed(chunks):
        limit = limit - len(c) / sr; latest.append(limit)
    latest = latest[::-1]
    pos = -1e9; placed = []
    for (tgt, c), la in zip(chunks, latest):
        st = max(pos, min(tgt - 0.03, max(la, pos)))
        if not placed: st = min(tgt - 0.03, max(la, tgt - 0.03)) if la >= tgt - 0.03 else tgt - 0.03
        st = max(st, pos)
        c = c.copy(); f = int(0.006 * sr)
        if len(c) > 2 * f: c[:f] *= np.linspace(0, 1, f); c[-f:] *= np.linspace(1, 0, f)
        a = int(st * sr); dub[a:a + len(c)] += c[:max(0, n - a)]
        pos = st + len(c) / sr; placed.append((round(st, 2), round(pos, 2)))
    # 每個分句實際落在成品的時間(給字幕用)
    bnd = [0.0] + [c['t'] for c in info['inner']] + [len(y) / sr]
    cidx = [k for k, c in enumerate(cuts[:-1]) if c is not None]          # 每個片段從第幾個分句開始
    pp = []
    for k in range(len(parts)):
        ci = max(i for i, s0 in enumerate(cidx) if s0 <= k)
        off = placed[ci][0] - bnd[cidx[ci]]
        pp.append([round(off + bnd[k], 2), round(off + bnd[k + 1], 2)])
    report.append(dict(id=l['id'], take=tk, gain=round(gain, 1), placed=placed, parts_placed=pp, win=[l['start'], l['end']], zh=l['zh']))
    print('%2d %-8s gain %+5.1f dB  原 %.2f-%.2f  配 %s  %s' % (l['id'], tk, gain, l['start'], l['end'],
          ' '.join('%.2f-%.2f' % p for p in placed), '超出%.2fs' % (pos - l['end']) if pos > l['end'] + 0.3 else ''))

# 配音軟限幅
pk = np.abs(dub).max()
dub = np.tanh(dub / 0.85) * 0.85 if pk > 0.85 else dub
mix = bed + dub[:, None]
pk = np.abs(mix).max()
if pk > 0.97: mix *= 0.97 / pk
print('peak %.3f' % pk)
os.makedirs('out', exist_ok=True)
sf.write(f'out/{out}_mix.wav', mix, sr)
sf.write(f'out/{out}_dub_only.wav', dub, sr)
sf.write('out/bed.wav', bed, sr)
json.dump(report, open(f'out/{out}_report.json', 'w'), ensure_ascii=False, indent=1)
