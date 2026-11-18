"""驗證:只取旁白時段,(1)背景軌用日文辨識應該聽不出話 (2)原音對照應該聽得出 (3)成品用中文辨識應該對得上稿。
用法(在單集資料夾內): python3 ../tools/verify.py <mix 名稱>"""
import json, subprocess, sys
name = sys.argv[1]
s = json.load(open('script.json'))
def cut(src, dst):
    parts = ''.join('[0:a]atrim=%.2f:%.2f,asetpts=PTS-STARTPTS[a%d];' % (l['start'] - 0.2, l['end'] + 0.6, i) for i, l in enumerate(s))
    cat = ''.join('[a%d]' % i for i in range(len(s))) + 'concat=n=%d:v=0:a=1[o]' % len(s)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', src, '-filter_complex', parts + cat, '-map', '[o]', '-ar', '16000', '-ac', '1', dst], check=True)
def asr(f, lang, prompt=None):
    cmd = ['whisper', f, '--model', 'medium', '--language', lang, '--output_format', 'json', '--output_dir', 'out/check', '--condition_on_previous_text', 'False']
    if prompt: cmd += ['--initial_prompt', prompt]
    subprocess.run(cmd, capture_output=True)
    d = json.load(open(f.replace('.wav', '.json')))
    return ' '.join('%s(nsp %.2f)' % (x['text'].strip(), x['no_speech_prob']) if lang == 'ja' else x['text'].strip() for x in d['segments'])
import os; os.makedirs('out/check', exist_ok=True)
cut('out/bed.wav', 'out/check/bed_win.wav'); cut('src/orig.wav', 'out/check/orig_win.wav'); cut(f'out/{name}_mix.wav', f'out/check/{name}_win.wav')
print('【背景軌｜日文辨識】', asr('out/check/bed_win.wav', 'ja'))
print('【原音對照｜日文辨識】', asr('out/check/orig_win.wav', 'ja')[:300], '…')
print('【成品｜中文辨識】', asr(f'out/check/{name}_win.wav', 'zh', '以下是繁體中文旁白。' + s[0]['zh']))
print('【配音稿】', ''.join(l['zh'] for l in s))
