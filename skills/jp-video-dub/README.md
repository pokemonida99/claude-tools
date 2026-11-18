# jp-video-dub

外語影片 → 中文配音＋雙語字幕的 Claude Code skill。流程與技巧看 `SKILL.md`。

## 腳本（都在單集資料夾裡執行）

| 檔案 | 用途 |
|---|---|
| `scripts/prep.sh <網址或檔案>` | 下載、抽音軌、Demucs 分離、日文逐字稿、說話區段、畫面總覽圖 |
| `scripts/vad.py [門檻dB]` | 列出人聲軌的說話區段 |
| `scripts/el_js.py mute｜paste [句號…]` | 印出 ElevenLabs 頁面要執行的 JS（靜音、貼稿） |
| `scripts/align.py <take>` | 用 whisper 字詞時間把整段配音切回每一句 |
| `scripts/mix.py <名稱> <take> [句號=take…]` | 抽掉原旁白、把配音對回原時間、音量比照原旁白 |
| `scripts/verify.py <名稱>` | 用辨識驗證：背景無殘留原聲、成品對得上稿 |
| `scripts/subs.py <名稱> <檔名前綴>` | 產生中文在上、日文在下的字幕圖與 srt |
| `scripts/render.sh <名稱> <檔名前綴>` | 輸出字幕版、無字幕版、傳送版、聽檢檔 |
| `scripts/check_frames.sh <成品影片>` | 每條字幕抽一張拼成檢查圖 |

`templates/script.example.json` 是配音稿範例。

## 需要的東西

- `ffmpeg`、`whisper`（Homebrew）、`uv`（跑 Demucs 與 numpy 工具）、`yt-dlp`（預設 `~/claude-tools/ytdlp/bin/yt-dlp`，可用環境變數 `YTDLP` 換）
- `/opt/homebrew/bin/python3` 要有 Pillow（字幕用）
- macOS 內建字型：蘋方、ヒラギノ角ゴシック
- 使用者的 Chrome 已登入 ElevenLabs，並裝了 Claude in Chrome
