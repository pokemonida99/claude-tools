---
name: jp-video-dub
description: 把日文（或其他外語）影片做成中文配音＋中日雙語字幕：Demucs 抽掉原旁白保留配樂音效、ElevenLabs 台灣音色配音（操作使用者 Mac 的 Chrome）、逐句對回原時間、音量比照原旁白、燒上「中文在上日文在下」字幕，輸出字幕版／無字幕版／30MB 傳送版。Use when the user gives a video file or YouTube link and asks for 中文配音、配音版、去原聲、換旁白、dub、中日字幕、雙語字幕、「這個也比照」前一支配音片，or mentions 新幹線戰士配音、ElevenLabs 配音、James 音色.
---

# 外語影片 → 中文配音＋雙語字幕

這份是做兩支《シンカリオン チェンジ ザ ワールド》宣傳片（L0、E4 Max 朱鷺號，2026-11）整理出來的流程。
腳本在 `~/.claude/skills/jp-video-dub/scripts/`（下面簡寫成 `$S`），**每支影片開一個資料夾，所有指令都在那個資料夾裡執行**。
一支 3～4 分鐘的片約 40～60 分鐘、ElevenLabs 約 600 點。

```bash
S=~/.claude/skills/jp-video-dub/scripts
PY="uvx --python 3.11 --with numpy --with soundfile python"
```

## 0. 開工前

- 使用者已定案的做法（沒另外交代就照這套）：
  - 音色 **ElevenLabs「James - Young, Friendly and Positive」＋ Eleven v4**
  - 字幕 **中文在上、日文在下**
  - 交付：字幕版、無字幕版、30MB 以下傳送版、srt、聽檢短檔
  - 成品複製到 `0720/雲端/<片名>中文配音/`，再備份到 Google 雲端硬碟 `03_影片創作/`（`~/Library/CloudStorage/GoogleDrive-*/我的雲端硬碟/`）
- ElevenLabs 沒有 API key，用**使用者 Mac 的 Chrome**（Claude in Chrome）操作已登入的網頁。
- 自己聽不到聲音：文字、時間、殘留原聲都用辨識驗證，**語氣與讀音一定交代使用者聽**。
- 不同系列的片先確認譯名；同系列沿用既有譯名（見第 4 節）。

## 1. 前置（一行跑完）

```bash
mkdir -p <專案>/epN-名稱 && cd <專案>/epN-名稱 && $S/prep.sh "<YouTube 網址或本機影片>"
```

`prep.sh` 會：下載 H.264 版本與自動日文字幕 → 抽 `src/orig.wav` → Demucs 分離 → 在人聲軌上跑 whisper 日文 → 列出說話區段 → 產生畫面總覽圖 `src/frames/sheet.jpg`。

要點：
- Demucs **一定 `-d cpu`**（Mac GPU 會報錯），並釘 Python 3.11＋torch／torchaudio 2.5.1。
- 人聲軌＋配樂軌相加等於原音，這是「只在說話時抽人聲」的基礎。
- 專有名詞多的片，先設 `JA_PROMPT="シンカリオン、…"` 再跑，whisper 會準一些。

## 2. 把日文稿弄對

三個來源互相對，不要只信一個：

1. `prep.sh` 印出的 whisper 結果（人聲軌）。
2. YouTube 自動字幕 `src/src.ja.vtt`。
3. 聽不清楚的段落**切 10～20 秒重跑**（原音與人聲軌各一次，`--temperature 0 --condition_on_previous_text False`）。

再加兩個檢查：
- **看畫面的標題字**：機體名、模式名、招式名通常有大字。打開 `sheet.jpg`，有字的時間點再放大抽圖。漏詞多半是這樣抓到的。
- **分句時間用說話區段（`vad.py`）**，比 whisper 的時間準。-25 dB 以下的零星小段通常是音效或叫聲，不是台詞。

whisper 在沒人說話的段落會幻聽（例如「ご視聴ありがとうございました」），`no_speech_prob` 高就不要信。
還是聽不準的詞：照最合理的寫，並**在回報裡明講哪個詞是推測的**。

## 3. 寫 `script.json`（唯一要手寫的檔）

範例：`templates/script.example.json`。

- 一「句」＝原片兩次明顯停頓之間的一整段；`start` 是第一個分句開始、`end` 是最後一個分句結束。
- `parts` 是句內依原片小停頓切的分句：`[開始秒, 配音唸的中文, 日文原文, 字幕顯示的中文(可省), 選項(可省)]`
  - 日文欄給 `""` → 這個分句的字幕併入上一條（「變形！」＋「新幹線戰士！」）。
  - 選項寫 `"top"` → 這條字幕放畫面上方（片中有大標題字時）。
- `zh`＝各分句配音文字接起來；`ja`＝日文接起來；`tag`＝句首語氣標記。

## 4. 翻譯與配音稿的技巧

- **字數預算**：每秒 4.3～5 個字。超過就精簡用詞；句子後面有空檔可以放寬（混音會往後延伸最多 1.5 秒）。
- **寫給 TTS 唸的字**：`L0`→`L零`、`E4`→`E四`、`500`→`五百`、`0系`→`零系`。字幕要顯示一般寫法就填第 4 欄。
- **英文片假名的專有名詞保留英文**（Great、Full Max、Guard Buster、Big Wave Buster）：v4 中英夾雜唸得自然，也對得上畫面標題。
- **避開多音字**，能換字就換（「朝未來」→「向未來」）。辨識抓不到讀音錯。
- **每個分句要能單獨成立**，順序對得上原句；畫面常在某個詞出現時切鏡頭。
- **不要自己加原片沒說的資訊**（原片說「他們」就翻「他們」，不補敵方名稱）。
- **語氣標記**：`[dramatic, energetic narrator]`、`[building excitement]`、`[excited]`、`[shouting]`、`[energetic narrator]`。v4 不會把標記唸出來。
- 新幹線戰士系列譯名：シンカリオン＝新幹線戰士（官方名「新幹線變形機器人」太長，喊招塞不下）；とき＝朱鷺號；チェンジ！＝變形！

## 5. 選音色（換系列、換角色時才需要）

- **先量原旁白音高、看是誰在講，再選**。不要預設「宣傳片＝低沉男旁白」——新幹線戰士的旁白是少年主角（旁白 175～220 Hz、喊招 470 Hz）。
- 音色庫搜尋 `Taiwan`，網址加 `&gender=male`／`female`；看描述、年齡、用途。
- 用同樣三四句（旁白一句、激動一句、喊招一句）試配兩三個候選，每次約 130 點。
- 第一次給使用者兩個音色的完整版讓他挑；定案後不用再做對照版。
- 使用者指定過的音色：少年旁白用「James - Young, Friendly and Positive」；女聲、可愛角色用「Ellen - Sweet」（使用者說「Elle sweet」就是它）。使用者直接指定音色時不用做對照版。
- 短劇式的片（多個角色輪流講話）目前都用同一個音色配，靠每句的語氣標記分出通報、喊招、撒嬌；交付時要說明這一點。

## 6. ElevenLabs 生成

頁面：`https://elevenlabs.io/app/speech-synthesis/text-to-speech`

1. **先靜音**：`python3 $S/el_js.py mute` 印出的 JS 用 javascript_tool 執行（生成完會自動播放；換頁要重掛）。
2. 選音色：點右側「聲音」→ 挑選器切到**「探索」分頁** → 搜尋名稱 → 滑鼠移到該列按「使用」。音色庫的聲音不用先加到「我的音色」。
3. 模型選 **Eleven v4**，其他設定用預設。
4. 貼稿：`python3 $S/el_js.py paste` 印出的 JS 拿去執行（編輯器是 ProseMirror，鍵盤貼上無效）。**整份稿一次貼、每句一行**，語氣前後才一致。貼完截圖確認標記有變色。
5. 按「生成語音」（用 find 找按鈕的 ref，位置會變），約 15～20 秒，一次出兩版。
6. 兩版都按下載。檔案在 `~/Downloads/ElevenLabs_<時間>_<音色>_….mp3` 與 `… (1).mp3`，搬成 `vo/raw/james_a.mp3`、`james_b.mp3`。
7. 補單句：`el_js.py paste 6 7`，連前一句一起生，存成另一個 take（例如 `james_p1`），混音時用 `7=james_p1` 換上。
8. 做完關掉自己開的分頁。

費用：每字元 1 點（標記也算），生成前後看左下角剩餘點數，回報用了多少。

## 7. 切句 → 混音 → 驗證 → 字幕

```bash
for t in james_a james_b; do whisper vo/raw/$t.mp3 --model medium --language zh --word_timestamps True --output_format json --output_dir vo/wh --initial_prompt "以下是繁體中文旁白：<幾個專有名詞>" >/dev/null 2>&1; ${=PY} $S/align.py $t; done
```

`align.py` 每句印出：`dur`／`win`（配音長度／原句長度）、`cov`（對到的字比例，低於 0.7 要懷疑）、`cuts`（句內停頓音量，低於 -38 dB 才會分開擺）。
挑喊招音量較足、整體較平均的那版當主版。

```bash
${=PY} $S/mix.py james james_b            # 個別句子換版：後面加 7=james_p1
python3 $S/verify.py james
/opt/homebrew/bin/python3 $S/subs.py james <檔名前綴>
```

- **混音**：背景＝原音 − 遮罩×人聲軌，遮罩只在旁白時段為 1，其他時間原音不動。配音每個分句放在原分句的開始時間，放不下往後延伸，**不提早、不變速**。每句音量比照原旁白那一句＋1 dB。
- **驗證**（只取旁白時段）：背景軌用日文辨識應該聽不出話；原音對照應該每句都聽得出；成品用中文辨識應該對得上稿。成品響度與原片差 0.5 LUFS 以內。
  - 不要對整支配樂軌跑 whisper，會卡十幾分鐘。
  - whisper 把少見詞聽成同音字（擊穿→集穿）不算錯；整句不見或多字才要查。
- **字幕**：時間跟中文配音走；1080p 自動等比放大；`subs.py` 用 PIL，要用 `/opt/homebrew/bin/python3`。

## 8. 輸出與檢查

```bash
$S/render.sh james <檔名前綴>
$S/check_frames.sh "out/<檔名前綴>_中文配音_中日字幕.mp4"
```

- `render.sh` 出三支影片＋聽檢檔。來源是 H.264 時無字幕版直接複製畫面；傳送版自動算流量壓到 28MB 內。
- `check_frames.sh` 把每條字幕各抽一張拼成 `src/frames/check.jpg`，**一定打開看**：
  - 字幕有沒有蓋到片中標題字、片尾 logo → 有就在該分句加 `"top"`，重跑 `subs.py` 與 `render.sh`。
  - 中日文有沒有對錯行、字有沒有超出畫面。
- 複製成品到 `雲端/` 與 Google 雲端硬碟，回報時列出檔案與大小。

## 9. 回報時要講清楚

- 我聽不到，哪些是辨識驗過的、哪些要請使用者聽。
- 哪個日文詞是推測的、譯名怎麼選、哪幾句為了時間有精簡。
- ElevenLabs 用了幾點、剩幾點。
- 成品放在哪（本機、雲端硬碟）。

## 踩過的坑

| 狀況 | 解法 |
|---|---|
| Demucs 一開始就報 MPS 錯 | `-d cpu` |
| whisper 跑很久不結束 | 不要丟整支配樂軌，只取旁白時段 |
| 逐字稿中段整段不見 | 在人聲軌上跑、切小段重跑 |
| 機體名漏了一個詞 | 對畫面標題字 |
| 字幕蓋到片中大標題 | 該分句加 `"top"` |
| 音色選太成熟 | 先量原旁白音高 |
| zsh 迴圈裡 `$PY` 沒被拆成多個字 | 用 `${=PY}` |
| yt-dlp 進度列塞滿輸出 | `--no-progress` |
| zsh 腳本裡把變數取名 `PROMPT` 就報錯 | `PROMPT` 是 zsh 的特殊變數，換別的名字 |
| 第二次下載 Chrome 卡「允許多個下載」 | 檔案其實在 `~/Downloads/.com.google.Chrome.*` 暫存檔，可直接複製 |

改了流程或腳本，要改這個 skill（`~/claude-tools/skills/jp-video-dub/`），不要只改專案裡的複本。
