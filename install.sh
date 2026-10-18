#!/bin/zsh
# Link this repo's skills into ~/.claude/skills so `git pull` updates them on every Mac.
# usage: ./install.sh      (run from the cloned repo)
cd "${0:A:h}"
mkdir -p ~/.claude/skills
for d in skills/*/; do
  n=${d:t}; dst=~/.claude/skills/$n
  if [[ -e $dst && ! -L $dst ]]; then mv "$dst" ~/.Trash/"$n.backup.$(date +%Y%m%d%H%M%S)"; echo "old $n moved to Trash"; fi
  ln -sfn "$PWD/skills/$n" "$dst" && echo "linked skill $n"
done
chmod +x tools/*/*.sh skills/*/scripts/*.sh 2>/dev/null
echo "GPT image tool: $PWD/tools/gpt-image/gen.sh"
