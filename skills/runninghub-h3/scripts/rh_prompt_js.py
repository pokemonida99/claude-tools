#!/usr/bin/env python3
"""Turn an H3 prompt file into a JS snippet that fills the RunningHub prompt <textarea> (React-safe).

usage: python3 rh_prompt_js.py <prompt.txt> [audio_file_name_to_verify]
Paste the printed snippet into the Chrome javascript_tool (action javascript_exec).
It returns [prompt length on page, audio file name present?, switches, number inputs, ratio text]
so one call both fills and verifies the form. Refuses prompts >= 5000 chars (RunningHub limit).
"""
import json, sys

txt = open(sys.argv[1], encoding='utf-8').read()
audio = sys.argv[2] if len(sys.argv) > 2 else ''
if len(txt) >= 5000:
    sys.exit(f'prompt is {len(txt)} chars; RunningHub limit is 5000')
js = ("const ta=document.querySelector('textarea');"
      "Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype,'value').set.call(ta," + json.dumps(txt, ensure_ascii=False) + ");"
      "ta.dispatchEvent(new Event('input',{bubbles:true}));"
      "[ta.value.length, " + json.dumps(audio) + " ? document.body.innerText.includes(" + json.dumps(audio) + ") : null, "
      "[...document.querySelectorAll('[role=switch]')].map(b=>b.getAttribute('aria-checked')).join(','), "
      "[...document.querySelectorAll('input[type=number]')].map(i=>i.value).join(','), "
      "(document.body.innerText.match(/\\d+:\\d+ \\((Widescreen|Portrait Widescreen|Square)\\)/)||[])[0]]")
print(js)
print(f'\n// expected length: {len(txt)}', file=sys.stderr)
