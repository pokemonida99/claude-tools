#!/bin/zsh
# Generate one image with GPT through the codex CLI (no browser, no API key: it uses your ChatGPT login).
# usage: gen.sh <out.png> "<prompt>" [reference images...]
#   e.g. gen.sh sheet.png "A character reference sheet ..." ref1.jpg ref2.jpg
# codex: the copy bundled inside ChatGPT.app is used if present, else `codex` on PATH (npm i -g @openai/codex).
# Run at most 2 at a time in parallel, more gets HTTP 429.
out=$1; prompt=$2; shift 2
CODEX=/Applications/ChatGPT.app/Contents/Resources/codex-cli/bin/codex
[[ -x $CODEX ]] || CODEX=$(command -v codex) || { echo "codex not found: install ChatGPT.app or npm i -g @openai/codex"; exit 1; }
args=()
for r in "$@"; do args+=(-i "$r"); done
# the prompt must come before -i, otherwise codex swallows it as an image path
$CODEX exec --skip-git-repo-check \
  "Generate one image with your image generation tool: $prompt. Do not run any shell commands." "${args[@]}" > "${out%.png}.log" 2>&1 </dev/null
sid=$(grep -m1 'session id:' "${out%.png}.log" | awk '{print $3}')
img=$(ls -t ~/.codex/generated_images/$sid/*.png 2>/dev/null | head -1)
if [[ -n "$img" ]]; then cp "$img" "$out"; echo "OK $out"; else echo "FAIL $out"; tail -5 "${out%.png}.log"; fi
