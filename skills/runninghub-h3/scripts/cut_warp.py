# Lip-sync without any speed change: every shot plays at exactly 1.0x; re-alignment happens only
# at the clip's own shot cuts by skipping (never repeating) footage. Uses the raw whisper anchors
# (audio/warp.py output) to find each shot's ideal offset. Places where H3 sang faster than the
# song cannot be fixed this way (no extra footage) -- those are reported and left for regeneration.
# Usage: python3 audio/cut_warp.py <raw warp.json> <clip dir> <out warp.json> [min_shot=0.6]
import json, os, subprocess, sys, statistics

raw_p, vdir, out_p = sys.argv[1:4]
MINSHOT = float(sys.argv[4]) if len(sys.argv) > 4 else 0.6

def cuts(path):
    r = subprocess.run(['ffmpeg', '-hide_banner', '-i', path, '-an', '-vf',
                        'scale=320:-1,scdet=threshold=12,metadata=print:key=lavfi.scd.time:file=-',
                        '-f', 'null', '-'], capture_output=True, text=True)
    return [float(l.split('=')[1]) for l in r.stdout.splitlines() if 'scd.time' in l]

def duration(path):
    return float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', path],
                                capture_output=True, text=True).stdout)

def build(A, edges, dur, D, k):
    """k in [0,1] scales how much footage we may skip (shrink if the clip would run out)."""
    segs, R, prev_o = [], 0.0, A[0][1] - A[0][0]
    for i in range(len(edges) - 1):
        a, b = edges[i], edges[i + 1]
        if i > 0 and R >= D: break
        offs = [c - r for r, c in A if a <= c < b]
        o = statistics.median(offs) if offs else prev_o
        # start inside this shot at its ideal offset (skipping its head); never before the cut
        s = min(a + k * max(0.0, (R + o) - a), b - MINSHOT) if i > 0 else a
        # how long this shot plays on the song timeline
        end_nat = R + (b - s)
        if i + 1 < len(edges) - 1:
            na, nb = edges[i + 1], edges[i + 2]
            noffs = [c - r for r, c in A if na <= c < nb]
            no = statistics.median(noffs) if noffs else o
            ideal_next = na - no          # song time where the next shot ideally starts
            Rn = min(end_nat, max(R + MINSHOT, ideal_next)) if k > 0 else end_nat
        else:
            Rn = max(end_nat, D)           # last shot runs to the end (may need footage past dur)
        segs.append((R, Rn, s))
        prev_o = s - R
        R = Rn
    return segs

def interp(x, xs, ys):
    if x <= xs[0]: return ys[0]
    for i in range(1, len(xs)):
        if x <= xs[i]: return ys[i-1] + (ys[i] - ys[i-1]) * (x - xs[i-1]) / max(1e-9, xs[i] - xs[i-1])
    return ys[-1]

out = {}
for name, A in json.load(open(raw_p)).items():
    path = os.path.join(vdir, name + '.mp4')
    dur, D = duration(path), A[-1][0]
    edges = [0.0] + [t for t in cuts(path) if 0.3 < t < dur - 0.3] + [dur]
    k = 1.0
    while True:
        segs = build(A, edges, dur, D, k)
        last_r0, last_r1, last_s = segs[-1]
        need = last_s + (D - last_r0)
        if need <= dur - 0.05 or k <= 0: break
        k = round(k - 0.1, 2)
    pts = []
    for r0, r1, s in segs:
        r1 = min(r1, D)
        pts += [[round(r0, 3), round(s, 3)], [round(r1 - 0.001, 3), round(s + (r1 - r0) - 0.001, 3)]]
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    errs = [(r, abs(interp(r, xs, ys) - c)) for r, c in A]
    bad = [f"{r:.1f}s" for r, e in errs if e > 0.4]
    skipped = sum(max(0, segs[i + 1][2] - (segs[i][2] + segs[i][1] - segs[i][0])) for i in range(len(segs) - 1))
    print(f"{name}: {len(edges)-2} cuts, skip {skipped:.2f}s, k={k}, mean err {statistics.mean(e for _, e in errs):.2f}s, "
          f"max {max(e for _, e in errs):.2f}s, >0.4s at {' '.join(bad) if bad else '-'}")
    out[name] = pts
json.dump(out, open(out_p, 'w'))
