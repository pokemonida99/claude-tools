# H3 Ref2VA prompt skeleton + rule blocks that worked (禮拜五下午 MV)

Fill `{…}`. Keep the whole prompt < 5000 chars (aim 3,300–4,600). Shot times are relative to the clip start,
and should sit on lyric-line starts of the uploaded audio slice.

```
subject_definitions:
<Subject 1> is {A: who + "from the multi-angle reference sheet <Picture 1>: same face, hair…, outfit…"}.
<Subject 2> is {B …<Picture 2>…}.
<Subject 3> is {scene from <Picture 3>, only if a scene ref is uploaded}.
<Audio 1> is the song excerpt used as the complete soundtrack; <Subject 1> (S1) and <Subject 2> (S2) lip-sync its vocals exactly.

summary:
[reference generation + audio reuse] A {N}-second, {k}-shot {9:16 vertical|16:9} {music-video excerpt|one-take studio recording performance} set in {place}. It contains ONLY the {k} shot(s) described below. The singing follows <Audio 1> word for word and cuts follow the timestamps below.

retention_analysis:
<Subject 1> (appears across the shots): fully_preserved - face, hairstyle and outfit follow the reference sheet.
<Subject 2> (appears across the shots): fully_preserved - face, hairstyle and outfit follow the reference sheet.
<Audio 1>: fully_copy - the excerpt is the complete soundtrack, unchanged in timing; the lip-sync follows it exactly.

detailed_description:
The target video is a photorealistic, cinematic {ratio} {K-pop music video|studio-session video} with {light}, Kodak Portra film tones and shallow depth of field. {RULE BLOCKS}
[Shot 1] {composition, who, action, camera}; <Subject 1> (S1) lip-syncs <d>[Chinese] {lyric}</d>.
[Shot 2] At 00:0{t}, the shot cuts to: {…}; <Subject 2> (S2) lip-syncs <d>[Korean] {lyric}</d>.

overall_soundscape:
No extra sound effects; <Audio 1> carries the whole soundtrack.

non_diegetic_music:
<Audio 1> is reused as the complete score, unchanged.
```

## Rule blocks (paste the ones that apply)
- **Framing**: Framing is mostly SINGLE-PERSON close-ups: each shot shows one woman alone in a chest-up or tight close-up, or a detail close-up of her hands, skirt hem, calves or sneakers; at most one short two-shot per sequence. Never wide full-body shots.
- **Gimbal camera**: Camera work feels like an operator holding a gimbal stabilizer: smooth slow orbit moves circling 30 to 90 degrees around the singer while staying locked on her face, gentle push-ins, soft floating handheld drift.
- **Natural faces**: Expressions are natural, relaxed and happy, never exaggerated. Hands and fingers stay crisp. Faces and bodies stay toward the camera with natural anatomy; nobody turns around.
- **Continuity example**: Neither woman wears an ID badge or lanyard. (or: "<Subject 1> wears an ID badge only in Shots 1-3; after she removes it…")
- **Sheet background**: The studio background of the reference sheets is not used.
- **Lip-sync**: Mouth shapes must match each syllable of <Audio 1> exactly at its timing; the singer starts and stops singing exactly when the vocal starts and stops.
- **Studio mics**: Each pop filter is angled off to the side of the microphone, never between the lips and the camera: the singing mouth and lips stay fully visible and unobstructed in every frame.
- **Studio take**: This is a live one-take studio performance: both women stand at the two condenser microphones of <Subject 3>, each wearing closed-back studio headphones, and sing for real. … Each shot shows ONE singer alone unless a two-shot is stated.

## Don'ts (learned)
- Don't omit lyrics hoping H3 follows the audio — it invents its own words.
- Don't put the whole-song synopsis in a short chunk's summary — H3 shoots other chunks' scenes.
- Don't write "she lip-syncs" without the (S1)/(S2) tag; plural subjects take "lip-sync"/"sing".
- Ice cream / food: each person has her own. Crying coworker: "glistening eyes, small sad pout", not sobbing.
- Earphones produced broken cables (3 earbuds on one wire) — avoid; use a selfie or other prop.

## 景別控制（2026-10-15 實測）
- 寫「waist-up」H3 會給大腿以上中景，臉偏小；寫「knee-up」幾乎一定變全身。全身時臉會崩。
- 規則段落用：「Framing is TIGHT: medium close-ups from the chest up and face close-ups only; head and shoulders fill most of the frame and the face is at least one third of the frame height; never show the waist, hips, legs or full body, never a wide or medium-wide shot, never a small figure.」
- **最有效的是 Shot 1 就寫 face close-up**：H3 傾向把第一個鏡頭拍成定場中遠景；第一鏡是臉部特寫時，整支都會維持近景（小葵 N_pump3 兩支全段皆近景）。
- 提示詞的規則段落不要寫沒出現的道具範例（例：寫了「a slim wand」，沒拿魔杖的角色手上也會多一根棍子）。
- 背景圖本身是「大門＋台階」這類有地面延伸的建築時，即使 Shot 1 寫臉部特寫，H3 仍可能先拍一段全身（N_pump4 前 2.6 秒）。要近景就挑背景是牆面、燭光、霧這類沒有地面的場景。
