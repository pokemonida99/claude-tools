---
name: runninghub-h3
description: Generate AI video clips on RunningHub's MiniMax H3 app (multi-reference + audio lip-sync) by driving the user's Mac Chrome, then download, pick and assemble them without stutter. Use when a project needs H3 / RunningHub video generation, music-video or lip-sync clips, Topaz upscaling on RunningHub, or when the user mentions RunningHub, H3, 跑 RH, 生影片.
---

# RunningHub H3 影片生成流程

這份是做兩支 MV(《禮拜五下午》、《幽靈舞步》,2026-10)累積的經驗整理。新專案從「0. 開工前」開始照著做。腳本放在 `~/.claude/skills/runninghub-h3/scripts/`,說明見同資料夾的 README.md。

## 0. 開工前(先確認,不要猜)
- 用使用者指定那台 Mac 的 Chrome(Claude in Chrome)。連了多個瀏覽器時,先 `list_connected_browsers`,再 `select_browser` 選對的那台。
- 登入由使用者自己來,**密碼不代填**。Mac 的 Chrome 平常已經是登入狀態。
- 全站最多 **5 個排程**,H3 和 Topaz 放大共用。
- 角色:**不要拿真人照片當角色參考**。先用 GPT(codex)生原創三視圖(白底、同一版型),真人照只拿來看氛圍。
- 提示詞用 **h3-prompt-writing skill 的 Ref2VA 六段格式**:subject_definitions / summary / retention_analysis / detailed_description / overall_soundscape / non_diegetic_music。**整段必須少於 5000 字元**。

## 1. 應用與表單
H3:https://www.runninghub.ai/zh-tw/ai-detail/2084320751339032577
| 欄位 | 設定 |
|---|---|
| 參考圖1 / 參考圖2 | 角色 A / B 的三視圖(提示詞裡寫成 `<Picture 1>` / `<Picture 2>`) |
| 參考圖3 | 場景圖(例如錄音室)寫成 `<Picture 3>`。**不用的話一定要按 X 刪掉**:重新載入後這格會冒出預設的沙發圖 |
| 最高畫質參考 | **開** |
| 參考音訊1 | 這一段的歌曲切片(mp3,切點要在歌詞句子之間的空檔) |
| 提示詞 | 用 `scripts/rh_prompt_js.py` 產生 JS 填入(見第 3 節) |
| 提示詞優化 | 關。只有超過 15 秒時才開(開了最長 30 秒、比較慢,而且 H3 會改寫你的提示詞) |
| 比例 | 9:16 或 16:9 |
| 時長/秒 | 整數,不超過 15(優化開時不超過 30) |
| 像素/百萬 | 0.4 → 480p(畫面容易崩);0.8 → 672×1216;**1 → 1376×768(MV 用這個)** |
| 補幀開關 | **開**(輸出 36 fps,動作順很多) |
| 其他 | 取樣步數 8、LoRA 0.4,保持預設 |

**耗時參考**:0.8、5–8 秒約 4–8 分鐘;1、7–10 秒約 6–10 分鐘;1、16–23 秒且優化開約 12–20 分鐘。

## 2. H3 的特性(一定要知道)
1. **H3 會重新生成人聲,不會照抄上傳的音訊**(跟原曲的波形相似度只有約 0.05)。嘴型跟的是 H3 自己唱的版本。
   - 片段越長偏差越大:20 秒以上的片段可能差到 8 秒,還會漏句。
   - **提示詞不寫歌詞的話,H3 會自己編歌詞**(實測),嘴型更對不上。所以要寫歌詞:每個鏡頭用 `<d>[Chinese] 歌詞</d>` 標出,並寫明 `(S1)/(S2)` 誰唱。
   - **最準的做法是短片段**:5–10 秒,切點放在鏡頭邊界或句子之間。
2. **遠景人物會崩**:只拍胸上和臉部特寫,**Shot 1 直接寫 face close-up**(H3 習慣把第一鏡拍成中遠景),詳見 `templates/rules.md`「景別控制」。少寫手指動作,手容易崩。兩人同框每段最多一次。
   - **不要用綠幕**去背合成,場景圖直接當 `<Picture 3>` 烘進去。
3. **summary 只能寫這一段自己的內容**。寫整首歌的大綱的話,H3 會把別段的畫面拍進來(例如紙飛機出現兩次)。建議寫 "It contains ONLY the N shot(s) described below"。
4. 常用規則句(整理在 `templates/rules.md`):不回頭、不轉身(GPT 和 H3 做回眸都很恐怖)、表情自然不誇張、手指清晰、拿掉工作證之後不要再出現、防噴罩放側邊不擋嘴、Never wide shots。

## 3. 送單流程(每段 ×2)
1. `navigate` 到 H3 頁面(**每一輪都重新載入**,原因見第 5 節)→ 等 4 秒 → `find` 找出參考圖1/2/3、參考音訊1 的 file input,以及最高畫質參考、提示詞優化、時長、像素的 ref。
2. `file_upload` 上傳三視圖和音訊 → `left_click` 最高畫質參考(預設是關)→ 視需要點提示詞優化 → `form_input` 填時長和像素。
3. 提示詞:`python3 scripts/rh_prompt_js.py prompt.txt 音訊檔名.mp3`,把輸出貼進 `javascript_tool`。回傳的是 [頁面上的字數, 音訊在不在, 開關狀態, 數字欄位, 比例],跟 stderr 印的預期字數比對。
   - 同一輪換下一段時,不必重貼整段,用 JS 的 `v.replace(/\[Shot 1\][\s\S]*?\n\noverall_soundscape/, 新鏡頭+'\n\noverall_soundscape')` 換掉鏡頭,再換 summary 的秒數。
4. 參考圖3:不用的話,捲到最上面再往下 2 格,截圖找到參考圖3 右上角的 ⓧ(約在 x=388、y=161~283)點掉,再 zoom 確認那格是空的。
5. 比例:`scroll_to` 比例欄 → 用**座標**點下拉選單(約 408,342)→ 再點選項(16:9 約 290,552)→ zoom 確認。**用 ref 點選項會選錯成 1:1**。重新載入後預設通常是 9:16,記得再確認一次。
6. 立即執行按鈕約在 (366,644)。點一次,等 5 秒,再點一次(每段兩版)。
7. **確認真的有排進去**:點右側「歷史記錄」(1555,380),用 JS `(document.body.innerText.match(/生成中[^\n]*/g)||[]).join(' / ')` 數「生成中」有幾個,再點 (1240,355) 關掉面板。數量不對就重新載入、重填、重送。

## 4. 取件
1. 開 user-center 分頁 `https://www.runninghub.ai/zh-tw/user-center`,等 5 秒,用 JS 列出新的成品:
   ```js
   [Date.now()/1000|0, [...document.querySelectorAll('video')].map(v=>v.src||v.querySelector('source')?.src).filter(s=>s).map(s=>s.split('/').pop()).filter(s=>+s.split('_').pop().slice(0,10)>送單時的epoch)]
   ```
2. `scripts/rh_fetch.sh <資料夾> <檔名...>`:只下載 mp4,不下載 zip。腳本會印出長度,可以用長度分辨是哪一段(對照表在腳本裡)。
3. 同樣長度的片段分不出來時:`lipsync_anchors.py` 用每個候選段落試比對,matched chars 最多的就是那一段。

## 5. RunningHub 頁面的坑
- **只要有任務完成,這個頁面就會「按了執行卻沒送出」**:只看到追蹤請求,縮圖列也沒有轉圈。解法是每一輪都重新載入、重填。
- 重新載入後,參考圖3 會出現預設沙發圖、比例和時長也會重置。
- 剛上傳的參考圖要等幾秒才會顯示,截圖時看到預設圖不代表上傳失敗。
- 元素搜尋工具(find)有用量限制。必要時改用 `read_page filter=all` 找 `button type="file"` 的 ref。
- 隨機失敗(大約 5 次有 1 次,約 1 分半時發生):在歷史記錄按「重試」或重送。

## 6. 選片
- 每段兩版:用 ffmpeg 每秒抽一格拼成條(`fps=1,scale=220:-1,tile=10x1`)一起看。淘汰有轉身背對、臉被切、防噴罩擋嘴、同一人重複出現、遠景的版本。
- 對嘴量測:`lipsync_anchors.py clip.mp4 名稱 段落起點 長度 out.json timeline.json` 先取錨點,再 `cut_warp.py out.json 片段資料夾 cut.json`,會印出 mean/max err。**平均 ≤0.3 秒算合格**;差太多的就切成短段重做。

## 7. 組片(不能變速!)
- **片段一律 1.0 倍原速播放**。對嘴只能在原片的剪接點跳過一小段畫面來對齊(`cut_warp.py`),**絕對不要放慢或加快**。使用者一眼就會看出 lag(2026-10-13 的教訓:分段變速 0.6–1.6 倍造成 40% 重複格)。
- **輸出 fps 要跟原片一樣**:補幀開是 36 fps、關是 24 fps;fps 不一致會多出重複格。
- **H3 一支片段裡面自己有 2–3 個鏡頭**(約 2.6 秒、4.9 秒處切換)。剪輯時每個鏡頭只用一個連續畫面,不要跨過片段內部的切點,否則同人同景別換背景就是跳切;同一個角色不要連續兩鏡。
- render 頁面:canvas 搭配 `<video>`,`seekTo` 要對齊到片段 fps 的影格中心;用 puppeteer 一格一格匯出(參考 `templates/render/`)。同一支 `<video>` 不要在稍後的鏡頭跳秒重用,第一格會殘留舊畫面。
- 匯出後跑 `scripts/dupcheck.sh out.mp4`,重複格要在 5% 以下。
- 影片加了底片顆粒會很難壓縮。用 CRF 23 重新壓縮,3 分鐘 16:9 約 350–490 MB。

## 8. 放大(定案後才做)
Topaz:https://www.runninghub.ai/zh-tw/ai-detail/2100086280821784577,短邊 1080 就夠。**初稿不要放大**,只放大使用者確認要用的片段,放大後再重新剪接。

## 9. 交付與溝通
- 成品放專案指定的雲端資料夾。舊版移到 `~/.Trash`(不要 rm),先確認使用者同意刪除。
- 改變處理方法之前(尤其是會影響畫面順暢度或時間軸的),**先跟使用者說明原因再動手**。
- 每一輪送單之後,簡短回報目前在做什麼、排了幾個任務。
