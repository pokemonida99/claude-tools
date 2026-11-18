"""印出要在 ElevenLabs 文字轉語音頁面執行的 JavaScript。
用法(在單集資料夾內):
  python3 el_js.py mute            # 靜音掛鉤:每次進頁面先跑一次,生成完不會自動播出聲音
  python3 el_js.py paste           # 把 script.json 整份稿貼進編輯器(每句一行,句首帶語氣標記)
  python3 el_js.py paste 6 7       # 只貼第 6、7 句(補句用,連前一句一起生語氣才接得上)
同時把貼上的文字存成 vo/tts.txt。"""
import json, sys, os

MUTE = ("if(!window.__muteHook){window.__muteHook=1;const P=HTMLMediaElement.prototype.play;"
        "HTMLMediaElement.prototype.play=function(){this.muted=true;return P.apply(this,arguments)};"
        "new MutationObserver(()=>document.querySelectorAll('audio,video').forEach(a=>{a.muted=true}))"
        ".observe(document.body,{childList:true,subtree:true});}"
        "document.querySelectorAll('audio,video').forEach(a=>{a.muted=true;a.pause()});'muted'")

mode = sys.argv[1] if len(sys.argv) > 1 else 'paste'
if mode == 'mute':
    print(MUTE); sys.exit()
ids = set(map(int, sys.argv[2:]))
script = json.load(open('script.json'))
lines = [((l['tag'] + ' ') if l.get('tag') else '') + l['zh'] for l in script if not ids or l['id'] in ids]
text = '\n'.join(lines)
os.makedirs('vo', exist_ok=True)
open('vo/tts.txt', 'w').write(text + '\n')
print(MUTE.rsplit("'muted'", 1)[0] +
      "const text=" + json.dumps(text) + ";"
      "const pm=[...document.querySelectorAll('.ProseMirror')].find(e=>e.offsetParent);const ed=pm.editor;"
      "ed.commands.focus();ed.commands.selectAll();const dt=new DataTransfer();dt.setData('text/plain',text);"
      "pm.dispatchEvent(new ClipboardEvent('paste',{clipboardData:dt,bubbles:true,cancelable:true}));"
      "await new Promise(r=>setTimeout(r,800));ed.getText().length+' chars :: '+ed.getText().slice(-30)")
print('\n# %d 字元(約 %d 點,一次出兩版)' % (len(text), len(text)), file=sys.stderr)
