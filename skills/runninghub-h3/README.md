# runninghub-h3 skill：說明

在 RunningHub 用 MiniMax H3 生成 AI 影片（多參考圖加音訊對嘴），再組成不會 lag 的成品。
Claude 依照 `SKILL.md` 執行，這份說明寫給人看。

## 怎麼開始一個新專案
跟 Claude 說「用 RunningHub H3 做 ○○ 的影片／MV」，這個 skill 就會被套用。開工前先準備：
1. **角色三視圖**：用 GPT 生成的原創三視圖，不要用真人照片。
2. **歌曲與歌詞**：用 whisper 對齊出每個字的時間，做成 `timeline.json`。
   - 格式：`{"lines":[{"text":"...","t":[每個字在歌曲中的秒數]}]}`
   - 做法:demucs 分離人聲 → whisper(medium、`--word_timestamps`)取每個字的時間,歌詞以原稿為準。
3. **切音訊**：照「鏡頭邊界或句子之間的空檔」切成 5–10 秒的 mp3。
4. **提示詞**：用 h3-prompt-writing skill 的 Ref2VA 格式寫，套 `templates/rules.md` 的規則段落，每段必須少於 5000 字元。

## 檔案
| 檔案 | 用途 |
|---|---|
| `SKILL.md` | 完整操作流程：表單、送單、取件、RunningHub 頁面的坑、選片、組片、放大、交付 |
| `scripts/rh_prompt_js.py` | 把 prompt.txt 轉成填表用的 JS（React 安全寫法），一次完成填入和驗證 |
| `scripts/rh_fetch.sh` | 下載成品 mp4（不下載 zip），印出長度和解析度，方便分辨是哪一段 |
| `scripts/lipsync_anchors.py` | 用 whisper 比對片段實際唱的字和原曲歌詞的時間，輸出錨點，也能用來辨識片段屬於哪一段 |
| `scripts/cut_warp.py` | 原速對嘴：每個鏡頭都 1.0 倍播放，只在剪接點跳過畫面來對齊；會印出平均和最大誤差 |
| `scripts/dupcheck.sh` | 計算成品的重複格比例（≤5% 正常；30% 以上就是 lag） |
| `templates/rules.md` | 提示詞骨架、實測有效的規則段落、踩過的雷 |
| `templates/make_chunks_example.py` | 把長片段依鏡頭切成短段重新生成的範例（prompt 加音訊） |
| `templates/render/` | canvas 加 `<video>` 的渲染頁 `studio.html`（含 seekTo、warp），以及 puppeteer 匯出 `export.mjs` |

## 三條最重要的教訓
1. **H3 會自己重唱**：短片段加上寫明歌詞最準；不寫歌詞的話 H3 會自己編歌詞。
2. **組片絕對不能變速**：一律原速、跟原片同 fps（補幀開 36、關 24），對齊只在剪接點做。
3. **每次有任務完成就重新載入頁面再送單**，送出後到「歷史記錄」數一下「生成中」的數量。
