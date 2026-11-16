from pathlib import Path
root=Path('D:/workspace-new/my2/video/projects/xianxia')
ep=root/'剧集/EP004'
refs='REF-EP004-ARCHER（顺序：1）· 剧集/EP001/制作成果/images/IMG-CHAR-01_银白羽饰弓手.png《银白羽饰弓手》（用途：身份；控制：脸型、银白长发、羽冠、耳坠、白银羽衣、鞋履；不得控制：站姿、灰背景、动作、兵器）；REF-EP004-SWORDSWOMAN（顺序：2）· 剧集/EP001/制作成果/images/IMG-CHAR-02_黑紫宽檐帽剑士.png《黑紫宽檐帽剑士》（用途：身份；控制：脸型、栗棕发、金纹宽檐帽、黑紫战衣、手套、披风、靴子；不得控制：站姿、灰背景、动作、兵器）'
video='Video 1 · 输入/EP004/source.mov《待替换人物的原视频》（控制：场景、动作、武器、特效、构图、运镜、剪接、节奏、声音；替换：原白发女与原黑发女的身份和服饰）'
anchor='Replace the original white-haired woman in <Video 1> with the silver-white feather-clad woman from <Picture 1>, and replace the original black-haired woman in <Video 1> with the dark-purple wide-brim-hat woman from <Picture 2>.'
(ep/'剧本.md').write_text('''# EP004 原片人物替换

本集为source.mov的人物替换版本。以用户最新澄清为准：原视频白发女→项目银白羽饰弓手；原视频黑发女→项目黑紫宽檐帽剑士。只更换人物身份与服饰，不新编弓剑对决，不增加弓箭、龙凤或夕照云海场景。

## EP004-SC001 外 · 原视频山谷战场 · 原片光态

逐时刻沿用source.mov的原片动作、人物运动轨迹、接触关系、兵器、浮石、场景、摄影与剪接。银白羽饰弓手扮演原白发女，黑紫宽檐帽剑士扮演原黑发女，分别完整承接其表演和身体动作。两位新人物的头发、服饰、帽饰与披风随原片加速度自然运动，保留原片遮挡与受力关系。

[连续性] 角色称谓仅标识图片中的人物，不要求弓手拿弓或剑士改持项目长剑。原片武器与红色效果保持，原人物身份不再混回。人物离开画面时保留原片空景。

[SFX] 保留原片声音及其同步时点。
''',encoding='utf-8')
(ep/'视觉设定.md').write_text('''# EP004 视觉设定

## 人物 · 银白羽饰弓手
- 画面代称：silver-white feather-clad woman
- 识别锚点：以项目IMG-CHAR-01图片为准，成年女性，银白长发、银色枝叶羽冠、紫晶耳坠、白银羽饰衣裙、银白鞋履。
- 本集状态：替换source.mov原白发女，完整承接原人物动作和原片兵器状态；不新增弓箭。

## 人物 · 黑紫宽檐帽剑士
- 画面代称：dark-purple wide-brim-hat woman
- 识别锚点：以项目IMG-CHAR-02图片为准，成年女性，栗棕发、金纹靛紫宽檐帽、黑紫战衣、护臂手套、破边披风、黑紫靴。
- 本集状态：替换source.mov原黑发女，完整承接原人物动作和原片兵器状态；不改为项目独立长剑。

## 地点 · 原视频山谷战场
- 画面代称：original valley battlefield
- 识别锚点：完全依据source.mov的山崖、谷地、巨石、浮石、尘土、原片光照与色调。画幅和旋转方向以播放器正确显示的原视频为准，不套项目默认9:16。

## 参考边界
source.mov为编辑底片与动作摄影依据，两张项目人物图片只负责身份及全身服饰，不控制动作、构图、背景和道具。原视频10.64秒，包含音轨；原片声音保留，不添加配音或配乐。
''',encoding='utf-8')
common=f'''- 时长：11s
- 输入参考图：{refs}
- 输入参考视频：{video}
'''
(ep/'分镜.md').write_text(f'''# EP004 原片人物替换 · 分镜依据

按原视频逐帧对应，不重新拆镜或改变原剪接。source.mov实测10.64秒；若生成设置只接受整数秒，设11秒，0—10.64秒维持原速原时点，余下0.36秒停留原片终帧，交付时裁回10.64秒。画幅与方向均沿用原片正确显示结果。

## SHOT-EP004-001 · 原片双人身份替换
{common}- 来源：EP004-SC001与source.mov全片。
- 职责：仅替换两个人物的身份、头发和全身服饰。
- 景别/机位：逐时刻照原视频。
- 运镜：逐时刻照原视频，原片有剪接就保留剪接，不新设连续镜头。
- 图片提示词项：无
- 视觉依据：《视觉设定.md》·人物「银白羽饰弓手」（控制：身份服饰）；人物「黑紫宽檐帽剑士」（控制：身份服饰）；地点「原视频山谷战场」（控制：全部原片环境）。
- 起点：原视频首帧，将入画的原人物替换为对应项目人物。
- 唯一动作：逐帧重演原片人物动作，仅替换外观。
- 终点：原视频尾帧，人物在场与否、位置及遮挡均以原片为准。
- 声音：保留原音轨与同步，不新增声音。

### 冻结关键帧提示词
> Match the correctly oriented first frame of <Video 1> in framing, camera, lighting, environment, visible action, props and occlusions. {anchor} Replace only a character visible in this first frame; do not insert an absent character. Character reference backgrounds and static poses do not transfer.
''',encoding='utf-8')
(ep/'视频提示词.md').write_text(f'''# EP004 原视频人物替换｜MiniMax H3

本版替代此前龙凤对决稿。编辑目标：保留source.mov，只更换人物身份与全身服饰。

## 挂载素材
- 视频1：输入/EP004/source.mov → `<Video 1>`，原片底片，控制场景、表演、摄影与特效。
- 图片1：剧集/EP001/制作成果/images/IMG-CHAR-01_银白羽饰弓手.png → `<Picture 1>`，替换原白发女。
- 图片2：剧集/EP001/制作成果/images/IMG-CHAR-02_黑紫宽檐帽剑士.png → `<Picture 2>`，替换原黑发女。

使用支持视频加图片混合参考的MiniMax H3入口。视频与图片分别编号。不挂弓、长剑、云海、龙凤或原视频角色截图。

## MOTION-EP004-001 · 原片双人身份替换
- 分镜：SHOT-EP004-001
- 时长：11s
- 生成方式：图生视频
- 输入参考图：{refs}
- 输入参考视频：{video}
- 静态视觉锚点：{anchor}
- 起始帧：原视频首帧，只替换入画人物。
- 状态链：原片首帧 → 逐帧沿用动作、接触、遮挡、摄影与特效，仅替换人物外观 → 原片尾帧。
- 终点：原视频尾帧，不增加收势或新人物；余下0.36秒保持尾帧。

### 可复制提示词
> subject_definitions: <Video 1> is the source footage to edit, not merely an inspiration or motion example. <Subject 1> is the adult silver-white feather-clad woman in <Picture 1>, with her exact facial identity, long silver-white hair, silver leaf-and-feather crown, purple crystal earrings, white-silver feathered dress and matching footwear. <Subject 2> is the adult dark-purple wide-brim-hat woman in <Picture 2>, with her exact facial identity, chestnut hair, gold-trimmed indigo-purple wide-brim hat, black-purple fitted outfit, gloves, bracers, ragged purple cloak and boots.
>
> summary: Perform character replacement on <Video 1>. Replace its original white-haired woman with <Subject 1> and its original black-haired woman with <Subject 2>. Keep the original scene, combat, physical weapons, effects, camera work, cuts and timing.
>
> retention_analysis: <Video 1>: partially_preserved - preserve all non-character content, original action timing, spatial trajectories, body mechanics, hand contacts, grips, weapons, rocks, debris, red energy effects, background, lighting, depth of field, motion blur, camera paths, cuts, framing and original sound. Replace only the two women's identities, hair, accessories, clothing and footwear. <Picture 1>: attribute_transfer - transfer <Subject 1>'s complete character appearance to the source white-haired woman's tracked body, retaining the source performance rather than the reference pose. <Picture 2>: attribute_transfer - transfer <Subject 2>'s complete character appearance to the source black-haired woman's tracked body, retaining the source performance rather than the reference pose. Neither image contributes its grey studio background, static stance or new props. Track the two source identities through changing screen positions and occlusions; never swap their assigned replacements.
>
> detailed_description: {anchor} Edit the entire source sequence in temporal correspondence with <Video 1>. At every visible moment, preserve the source actor's position, scale, facing, gaze, expression intent, pose, acceleration, jump path, balance, hand placement, grip and interaction with the other actor and all objects. Retarget these performances to the two replacement characters. Preserve the original valley and cliffs, original physical weapon geometry and red blade effects, floating rocks, dust and all other source effects exactly in their existing roles. Let the new hair, feathered dress, hat and cloak react naturally to the source body motion, wind, inertia and collisions; preserve their reference designs without changing the choreography. Maintain correct occlusion in front of and behind rocks, weapons and the other character; hands remain attached to their original contacts and grips. Keep character appearance temporally consistent in wide views, close views, fast motion and partial occlusion. During source shots or ending frames with no characters visible, reproduce the original environment without inserting anyone. The labels archer and swordswoman identify the image characters only: do not introduce a bow, arrows, new sword, phoenix, dragon, cloud-sea platform or any additional action. Preserve the source framing, aspect ratio, display orientation, shot order, camera moves, zooms, cuts and event times. Keep the original 10.64-second action at its original speed from 0 to 10.64 seconds; if an 11-second output is required, hold only the final frame from 10.64 to 11 seconds. Do not stretch or retime the combat. No new subtitles, captions, dialogue overlays, logos or watermarks.
>
> overall_soundscape: Preserve the original source audio and its event synchronization. Do not add dialogue, narration, sound effects or a new music layer. If the execution interface cannot copy source audio, retain the original audio track for the final replacement render instead of inventing a new soundtrack.
>
> non_diegetic_music: Preserve only music already present in the source audio, if any; add no new music.

## 使用说明
将六字段正文整段提交一次，挂一段视频和两张人物图。原片时长实测10.64秒；入口若仅支持整数秒，设置11秒，保持前10.64秒原速，最后0.36秒停帧，成片裁回10.64秒。画幅、旋转方向以原片正确播放结果为准，不套项目默认竖屏。原声精确保留可在成片阶段直接沿用原音轨。

这是提示词与素材绑定，尚未生成或验证替换效果。当前内置图片来源选择器不支持提交参考视频，需在支持混合参考的入口挂载。
''',encoding='utf-8')
print('EP004 corrected: source video is the base; project character images replace the two women.')
