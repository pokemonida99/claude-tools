# claude-tools

Claude Code 用的工作流程工具，讓多台 Mac 可以同步使用：

| 內容 | 說明 |
|---|---|
| `skills/runninghub-h3/` | Claude Code skill：在 RunningHub 用 MiniMax H3 生成 AI 影片（多參考圖、音訊）、下載、選片、組片的完整流程與腳本 |
| `tools/gpt-image/gen.sh` | 用 GPT 生圖（透過 ChatGPT 桌面版內建的 codex 命令列工具，不需要 API key、不開瀏覽器） |

## 在一台新的 Mac 上安裝

1. 安裝 [ChatGPT 桌面版](https://chatgpt.com/download)，打開並登入 OpenAI 帳號（生圖用）。
2. 安裝 [Claude 桌面版](https://claude.ai/download)（使用 Claude Code），並在 Chrome 安裝 Claude in Chrome 擴充功能；在那台的 Chrome **自己登入 RunningHub**。
3. 下載這個 repo 並安裝：
   ```bash
   git clone https://github.com/pokemonida99/claude-tools.git ~/claude-tools
   ~/claude-tools/install.sh
   ```
   `install.sh` 會把 `skills/` 裡的 skill 連結到 `~/.claude/skills/`（原本若有同名資料夾，會先移到垃圾桶）。
4. 測試生圖：
   ```bash
   ~/claude-tools/tools/gpt-image/gen.sh test.png "a glowing jack-o'-lantern on a table"
   ```
   出現 `OK test.png` 就成功。
5. RunningHub 下載腳本需要你帳號的輸出網址前綴（每個帳號不同），設定一次即可：
   ```bash
   echo 'export RH_BASE=https://rh-hk-images.xiaoyaoyou.com/<你的帳號ID>/output' >> ~/.zshrc
   ```
   帳號 ID 的找法：在 RunningHub 個人中心任一支完成的影片，複製影片網址，去掉最後的檔名。

## 同步

- 拿到最新版：`cd ~/claude-tools && git pull`
- 改了 skill 要同步到其他台：`cd ~/claude-tools && git add -A && git commit -m "update" && git push`

因為 `~/.claude/skills/runninghub-h3` 是連結到這個資料夾，Claude 用的就是 repo 裡的最新內容。

## 注意

- 這個 repo 是公開的：**不要放密碼、token、帳號 ID 或個人資料**（`RH_BASE` 只放在自己電腦的 `~/.zshrc`）。
- Claude 的記憶（`~/.claude/projects/.../memory/`）不在這個 repo 裡，需要的話另外複製。
