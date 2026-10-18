# Short-chunk re-generation for MV v3 clips whose lip-sync drifted (H3 re-sings long clips with its own timing).
# Splits a full3 clip at its own shot boundaries into chunks (<=10 s), re-times the shots inside each chunk,
# and cuts the matching song audio -> h3/full3s/<Cxx><a|b|c>.txt + audio/seg/<Cxx><a|b|c>.mp3.
# Run from h3/:  python3 make_full3_short.py
import math, os, subprocess
src = open('make_full3.py').read().split('def ts(t)')[0]
exec(src)                                     # A, B, RULES, CLIPS, FIXES, sing(), S1/S2/BOTH
def ts(t): m, s = divmod(t, 60); return f"{int(m):02d}:{s:06.3f}"

SEG_START = {'C01': 0.00, 'C02': 20.36, 'C03': 35.70, 'C04': 57.90, 'C05': 79.36, 'C06': 95.36,
             'C07': 110.50, 'C08': 124.50, 'C09': 139.45, 'C10': 151.16, 'C11': 165.04}
CHUNKS = {'C04': [0.0, 6.5, 15.0, 22.0], 'C11': [0.0, 6.3, 13.0, 23.0]}   # boundaries = existing shot times
MAXLEN = 10.0
os.makedirs('full3s', exist_ok=True)
for name, dur, setting, light, summ, shots in CLIPS:
    if name not in CHUNKS: continue
    edges = CHUNKS[name]
    for ci in range(len(edges) - 1):
        c0, c1 = edges[ci], edges[ci + 1]
        assert c1 - c0 <= MAXLEN + 1e-6
        sub = [(t - c0, txt) for t, txt in shots if c0 - 1e-6 <= t < c1 - 1e-6]
        assert sub and abs(sub[0][0]) < 1e-6, (name, ci)
        cid = name + 'abc'[ci]
        L = round(c1 - c0, 2); secs = math.ceil(L)
        body = "\n".join(("[Shot 1] " if i == 0 else f"[Shot {i+1}] At {ts(t)}, the shot cuts to: ") + txt for i, (t, txt) in enumerate(sub))
        s2 = summ.replace('Xiao Lan', '<Subject 1>').replace('Xiao Huang', '<Subject 2>')
        txt = ("subject_definitions:\n<Subject 1> is " + A + ".\n<Subject 2> is " + B + ".\n"
          f"<Audio 1> is the song excerpt used as the complete soundtrack; <Subject 1> (S1) and <Subject 2> (S2) lip-sync its vocals and dance to its beat.\n\n"
          f"summary:\n[reference generation + audio reuse] A {secs}-second, {len(sub)}-shot 16:9 music-video excerpt set in {setting}. It contains ONLY the {len(sub)} shot(s) described below, nothing else. The singing follows <Audio 1> word for word and cuts follow the timestamps below.\n\n"
          "retention_analysis:\n<Subject 1> (appears across the shots): fully_preserved - face, hairstyle and outfit follow the reference sheet.\n"
          "<Subject 2> (appears across the shots): fully_preserved - face, hairstyle and outfit follow the reference sheet.\n"
          "<Audio 1>: fully_copy - the excerpt is the complete soundtrack, unchanged in timing; the lip-sync follows it exactly.\n\n"
          f"detailed_description:\nThe target video is a photorealistic, cinematic 16:9 K-pop music video with {light}, Kodak Portra film tones and shallow depth of field. {RULES} "
          "Mouth shapes must match each syllable of <Audio 1> exactly at its timing; the singer starts and stops singing exactly when the vocal starts and stops.\n" + body + "\n\n"
          "overall_soundscape:\nNo extra sound effects; <Audio 1> carries the whole soundtrack.\n\nnon_diegetic_music:\n<Audio 1> is reused as the complete score, unchanged.\n")
        for a, b in FIXES: txt = txt.replace(a, b)
        assert len(txt) < 5000 and '  ' not in txt, (cid, len(txt))
        open(f'full3s/{cid}.txt', 'w').write(txt)
        st = SEG_START[name] + c0
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{st:.3f}', '-t', f'{secs:.3f}', '-i', '../web/song.mp3',
                        '-c:a', 'libmp3lame', '-b:a', '192k', f'../audio/seg/{cid}.mp3'], check=True)
        print(f"{cid}: song {st:.2f}+{L}s (gen {secs}s), {len(sub)} shots, {len(txt)} chars")
