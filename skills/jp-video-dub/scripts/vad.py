"""列出人聲軌的說話區段(給分句時間用)。在單集資料夾內執行。"""
import numpy as np, soundfile as sf, sys
v, sr = sf.read('stems/htdemucs_ft/orig/vocals.wav'); v = v.mean(1)
th = float(sys.argv[1]) if len(sys.argv) > 1 else -33
h = int(sr * 0.02); n = len(v) // h
r = np.array([20 * np.log10(np.sqrt(np.mean(v[i*h:(i+1)*h] ** 2)) + 1e-9) for i in range(n)])
on = r > th; segs = []; i = 0
while i < n:
    if on[i]:
        j = i
        while j < n and (on[j] or on[j:j + 10].any()): j += 1      # 0.2 秒內的空隙視為同一段
        if (j - i) * 0.02 >= 0.25: segs.append((i * 0.02, j * 0.02, r[i:j].max()))
        i = j
    else: i += 1
for a, b, p in segs: print('%7.2f-%7.2f (%.2fs) peak %.0f dB' % (a, b, b - a, p))
