"""通用版:依 script.json 與混音報告做中日雙語字幕(中文在上、日文在下)。
用法(在單集資料夾內): python3 ../tools/subs2.py <mix 名稱> [輸出檔名前綴]
script.json 每個分句 parts = [開始秒, 配音唸的中文, 日文原文, 字幕顯示的中文(可省), 選項(可省)]
  日文給 "" 表示併入上一條字幕;選項含 "top" 表示這條放畫面上方(避開片中標題字)。"""
import json, sys, os, glob, subprocess
from PIL import Image, ImageDraw, ImageFont
name = sys.argv[1]; prefix = sys.argv[2] if len(sys.argv) > 2 else name
PF = glob.glob('/System/Library/AssetsV2/com_apple_MobileAsset_Font*/*/AssetData/PingFang.ttc')[0]
JP = '/System/Library/Fonts/ヒラギノ角ゴシック W5.ttc'
src = 'src/src.mp4'
W, H = map(int, subprocess.check_output(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height', '-of', 'csv=p=0', src]).decode().strip().split(','))
DUR = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', src]).decode())
k = H / 720
def face(path, want, size):
    for i in range(40):
        try: f = ImageFont.truetype(path, size, index=i)
        except Exception: break
        if f.getname() == want: return f
    raise SystemExit('font not found')
fz = face(PF, ('PingFang TC', 'Semibold'), round(38 * k)); fj = ImageFont.truetype(JP, round(26 * k))
script = json.load(open('script.json'))
rep = {r['id']: r for r in json.load(open(f'out/{name}_report.json'))}
cues = []
for l in script:
    pp = rep[l['id']]['parts_placed']
    for i, p in enumerate(l['parts']):
        ja = p[2] if len(p) > 2 else ''
        zh = p[3] if len(p) > 3 and p[3] else p[1]
        opt = p[4] if len(p) > 4 else ''
        if ja == '' and cues and i > 0:                       # 併入上一條
            cues[-1][1] = pp[i][1]; cues[-1][2] += zh; continue
        cues.append([pp[i][0], pp[i][1], zh, ja, 'top' in opt, l['end']])
    cues[-1][1] = max(cues[-1][1], l['end'])                 # 句尾至少撐到原句結束
for c in cues: c[1] += 0.15
for i in range(len(cues) - 1):
    if cues[i][1] > cues[i + 1][0] or cues[i + 1][0] - cues[i][1] < 0.25: cues[i][1] = cues[i + 1][0]
os.makedirs('subs', exist_ok=True)
for f in glob.glob('subs/*.png'): os.remove(f)
def text(d, s, font, y, fill, stroke):
    w = d.textlength(s, font=font); assert w < W - 80 * k, s
    d.text(((W - w) / 2, y), s, font=font, fill=fill, stroke_width=round(stroke * k), stroke_fill=(0, 0, 0, 255))
Image.new('RGBA', (W, H), (0, 0, 0, 0)).save('subs/blank.png')
lines = []; t = 0.0
for i, (st, en, z, j, top, _) in enumerate(cues):
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    y0 = (34 if top else 588) * k
    text(d, z, fz, y0, (255, 255, 255, 255), 4); text(d, j, fj, y0 + 54 * k, (245, 245, 245, 255), 3)
    im.save(f'subs/{i:03d}.png')
    if st > t + 0.001: lines += ["file 'blank.png'", f'duration {st - t:.3f}']
    lines += [f"file '{i:03d}.png'", f'duration {en - st:.3f}']; t = en
lines += ["file 'blank.png'", f'duration {max(0.1, DUR - t):.3f}', "file 'blank.png'"]
open('subs/frames.txt', 'w').write('\n'.join(lines) + '\n')
ts = lambda x: '%02d:%02d:%02d,%03d' % (x // 3600, x % 3600 // 60, x % 60, round(x % 1 * 1000))
open(f'out/{prefix}_中日雙語.srt', 'w').write(''.join(f'{i+1}\n{ts(c[0])} --> {ts(c[1])}\n{c[2]}\n{c[3]}\n\n' for i, c in enumerate(cues)))
for c in cues: print('%7.2f-%7.2f %s %s ｜ %s' % (c[0], c[1], '↑' if c[4] else ' ', c[2], c[3]))
