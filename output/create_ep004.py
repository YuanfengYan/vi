from pathlib import Path
import subprocess,sys

root=Path('projects/xianxia')
ep=root/'剧集/EP004'
ep.mkdir(parents=True,exist_ok=False)
def save(name,text):
    (ep/name).write_text(text,encoding='utf-8')
    r=subprocess.run([sys.executable,'.agents/skills/short-drama/scripts/creator_markdown_check.py',str(ep),'--project-root',str(root),'--partial'],capture_output=True,text=True,encoding='utf-8')
    print(name,r.stdout,r.stderr)

save('剧本.md','''# EP004 银发引凤 · 玄剑凝龙

独立弓剑对决新集，不接EP003徒手收势。将原白衣弓手替换为source.mov中的白发女，将原黑衣剑士替换为其中的黑发女；保留弓剑与龙凤对攻。建议15秒、9:16、无对白，单个连续镜头。视频只提供人物外观，不照搬其中的巨剑近战。

## EP004-SC001 外 · 夕照云海石台 · 黄昏

白发女站在石台左侧，银白长发与米白金饰衣裙被风吹起，左手握银羽长弓。右侧黑发女系着红色发带，米色露肩长袖衣装随风摆动，双手持暗柄银刃长剑，目光越过弓身盯住对手。

白发女向右助跑两步，蹬地完成一次后翻。她在悬空中伸出左腿，以左脚前端抵住下弓臂坚实内侧，左手由弓柄换到弦上，与右手一同向左拉弦；右膝屈起。弦间银光聚成一箭。双手同时松弦，白箭向右脱弦，连续展开成一只白凤凰。白发女借余势落回左侧，左手重新接稳弓柄。

[SFX] 脚步、衣摆掠风、弓弦绷紧，随后一声清脆放弦。

黑发女不退，双手将长剑举向右后上方，前脚踏稳，转腰向左前下方斜斩。紫黑弧形剑气离开剑刃，在她前方汇聚黑气；弧刃前端先凝成龙首，黑鳞与龙角随后显现，身躯沿剑气方向生长为一条无翼东方黑龙。黑发女握住实体长剑，停在斩后姿态。

[SFX] 踏步、剑刃破风，黑气汇聚的低鸣随龙首成形渐强。

白凤自左向右，黑龙自右向左，在石台中央上空相撞。银白羽光与紫黑鳞光形成清晰界面，一道透明压力环推开近雾，再推开远处云缘。白发女在左下、黑发女在右下，各守原来落点，分别握弓与剑。龙凤轮廓仍然分明，力量相持，胜负未定。

[SFX] 接触时一次低沉冲击，继以持续风压与能量碎响。

[连续性] 两位成年女性始终身份独立；米白金饰长发弓手在左、红发带黑发剑手在右。白凤与黑龙各只有一只，均由各自攻击转化；不是额外召唤。无对白、旁白、字幕或配乐。
''')
save('视觉设定.md','''# EP004 视觉设定

外观证据：输入/EP004/视频角色原帧.png，提取自用户提供的 source.mov 约4秒处。两张身份参考是该原帧的裁切，不是新生成定妆图。原帧中有遮挡；背面及鞋履细节未被此帧充分证明，不新增具体花纹设定。

## 人物 · 白发女
- 画面代称：white-haired archer
- 识别锚点：成年女性，银白长直发、侧分额发、纤细脸型；米白衣裙、古金色颈胸装饰与腰饰、暗色臂部装饰。保留参考中的面部与材质风格。
- 本集状态：替代原白衣弓手，使用银羽长弓；不继承旧角色羽冠、紫晶耳坠与银白羽衣。
- 参考：输入/EP004/白发女身份参考.png。

## 人物 · 黑发女
- 画面代称：black-haired swordswoman
- 识别锚点：成年女性，长黑发后束、额前碎发、红色发带与暗色结饰、金属耳饰；米色露肩长袖衣装、棕色束腰。不是黑衣角色。
- 本集状态：替代原黑衣剑士，使用暗柄银刃长剑；不继承旧角色栗棕短发、宽檐帽、黑紫战衣与披风，也不携带原视频的巨型红刃武器。
- 参考：输入/EP004/黑发女身份参考.png。裁切中混入的白发女手臂与原视频武器不属于该角色身份。

## 地点 · 夕照云海石台
- 画面代称：sunset cloud-sea platform
- 识别锚点：灰褐石台，草边，橙色云海与蓝灰天空，左后暖夕阳。复用EP001空场图；只保持地面与光向，扩展足够的对战距离。

## 道具 · 银羽长弓
- 画面代称：silver feather bow
- 识别锚点：银白反曲弓、层叠羽刃弓臂、单根清晰弓弦；参考图内文字与背景不进入视频。只有一支能量箭。

## 道具 · 暗柄银刃长剑
- 画面代称：dark-handled silver sword
- 识别锚点：银色直刃、暗色握柄、尖锐金属护手；实体兵器与脱体剑气分层，长剑始终由黑发女握住。

## 效果 · 白凤与黑龙
- 画面代称：phoenix and dragon
- 识别锚点：白凤为银白羽翼、冠羽与长尾翎；黑龙为无翼东方龙、黑曜鳞、紫色鳞缝。箭化凤、剑气凝龙，身体轮廓连续生长，各仅一只。接触后保留两种轮廓与中间折射界面。

## 参考边界
人物参考只锁身份与可见服饰，不锁原视频的姿势、武器、山谷、巨石、红色特效或近战动作。兵器图只锁兵器；空场图只锁地理光向。原视频不作为动作或声音参考上传。
''')
refs='；'.join([
'REF-EP004-WHITE（顺序：1）· 输入/EP004/白发女身份参考.png《白发女身份参考》（用途：身份；控制：脸型、银白长发、米白金饰衣装；不得控制：遮挡、构图、动作、原视频武器和场景）',
'REF-EP004-BLACK（顺序：2）· 输入/EP004/黑发女身份参考.png《黑发女身份参考》（用途：身份；控制：脸型、长黑发、红色发带、米色露肩衣装；不得控制：他人肢体、原视频武器、动作、场景）',
'REF-EP004-BOW（顺序：3）· 剧集/EP001/制作成果/images/IMG-PROP-01_银白羽刃长弓.png《银羽长弓》（用途：造型状态；控制：羽刃弓臂、握柄、单弦；不得控制：文字、背景、摆放姿态、独立实体箭）',
'REF-EP004-SWORD（顺序：4）· 剧集/EP001/制作成果/images/IMG-PROP-02_暗柄银刃长剑.png《暗柄银刃长剑》（用途：造型状态；控制：银刃、暗柄、护手形制；不得控制：背景、摆放姿态）',
'REF-EP004-ENV（顺序：5）· 剧集/EP001/制作成果/images/IMG-ENV-01_夕照云海空场.png《夕照云海石台》（用途：地理；控制：石台、云海、草边、左后夕阳；不得控制：空镜构图、人物站位、人物身份）'])
start='白发女在左侧双脚着地，左手持弓、右手自由；黑发女在右侧双手持剑于腰侧，相距约二十米。'
end='白发女落回左下握弓，黑发女右下握剑，中央上空一凤一龙接触相持；胜负未定。'
chain='站立对峙 → 后翻脚抵弓、双手拉弦 → 一次释放、箭化白凤、落地接弓 → 黑发女举剑斜斩、剑气离剑凝龙 → 龙凤接触、压力环外扩'
anchor='The white-haired archer stays on the left with the silver feather bow; the black-haired swordswoman stays on the right with the dark-handled silver sword, on a sunset cloud-sea platform with warm backlight from the left.'
save('分镜.md',f'''# EP004 分镜

单镜15秒、9:16，连续侧面摄影，不切镜、不使用逐切关键帧容器。完整保留人物替换与弓剑化龙凤的核心动作；不沿用旧10秒版多次切镜。独立新集，与EP003没有续接关系。

## 场景站位
石台中线为固定锚点；白发女在中线左侧、黑发女在右侧，互相面对。摄影机始终在对战轴线南侧。石台足够宽，两人开场相距约二十米。运动与摄影允许拉开空间，双方不交换左右。

## SHOT-EP004-001 · 银发引凤玄剑凝龙
- 时长：15s
- 来源：EP004-SC001全场。
- 职责：由白发女先攻、黑发女反击，完成龙凤对撞的当集回报。
- 景别/机位：南侧双人全景，后半向后升高为大全景。
- 运镜：先小幅侧跟白发女，黑发女反击时平稳向右滑移，最后缓慢拉远升高，把龙凤接触点留在中央；无切镜、无越轴。
- 图片提示词项：无
- 输入参考图：{refs}
- 视觉依据：《视觉设定.md》·人物「白发女」「黑发女」（控制：身份与服装）；地点「夕照云海石台」（控制：光向与地面）；道具「银羽长弓」「暗柄银刃长剑」（控制：武器形制）；效果「白凤与黑龙」（控制：数量、形态和转化）。
- 起点：{start}
- 唯一动作：双方完成一轮弓剑化兽攻防。
- 状态链：{chain}
- 终点：{end}
- 声音：全程高空风；放弦、破风与接触声对应动作；无对白、旁白、配乐。无口语估时需求。

### 冻结关键帧提示词
> {anchor} Both adult women face each other across roughly twenty metres of stone. The white-haired archer stands with both feet grounded, holding the bow in her left hand, right hand free. The black-haired swordswoman holds the sword at waist level with both hands. Wide side view, complete bodies and weapons visible, open sky above the central gap, detailed cinematic fantasy CG with realistic materials. No arrow in flight, phoenix, dragon or impact yet. No captions or text overlays.
''')
save('视频提示词.md',f'''# EP004 银发引凤 · 玄剑凝龙｜MiniMax H3 参考生

沿用项目已接受的 minimax-h3 / full-reference 档案，英文六字段，15秒，9:16。实际入口须支持多图参考；不用于仅支持首尾帧的入口。五张真实参考图已就位，无需先生成新图。本次仅写提示词，未调用视频生产。

## 挂图顺序
1. 输入/EP004/白发女身份参考.png：视频中的白发女，替换旧弓手身份与服饰。
2. 输入/EP004/黑发女身份参考.png：视频中的黑发女，替换旧剑士身份与服饰。
3. 剧集/EP001/制作成果/images/IMG-PROP-01_银白羽刃长弓.png：只取弓。
4. 剧集/EP001/制作成果/images/IMG-PROP-02_暗柄银刃长剑.png：只取剑。
5. 剧集/EP001/制作成果/images/IMG-ENV-01_夕照云海空场.png：只取地形、云海和光向。

不用上传source.mov，也不用旧人物定妆图、旧海报、旧双人动作图，以免混入旧脸、宽檐帽、羽冠或原视频巨剑。人物裁切保留部分遮挡，正文已限定只提取角色身份与服饰；完整背面与鞋履仍需生成结果核对。

## MOTION-EP004-001 · 银发引凤玄剑凝龙
- 分镜：SHOT-EP004-001
- 时长：15s
- 生成方式：图生视频
- 输入参考图：{refs}
- 静态视觉锚点：{anchor}
- 起始帧：{start}
- 状态链：{chain}
- 终点：{end}

### 可复制提示词
> subject_definitions: <Subject 1> is the adult white-haired woman in <Picture 1>, now the archer, with the same face, long silver-white hair, ivory dress, antique-gold neck and bodice ornaments and dark arm accents. <Subject 2> is the adult black-haired woman in <Picture 2>, now the swordswoman, with the same face, tied-back long black hair, red hair ribbons, metal earrings, beige off-shoulder sleeves and brown waist layers. <Subject 3> is only the silver feather bow in <Picture 3>, with feather-bladed recurved limbs and one string. <Subject 4> is the dark-handled silver straight sword in <Picture 4>. <Subject 5> is the sunset cloud-sea platform in <Picture 5>.
>
> summary: One continuous fifteen-second cinematic fantasy duel. The white-haired archer launches a single arrow that becomes a white phoenix; the black-haired swordswoman answers with one detached sword-energy arc that becomes a black eastern dragon. They collide above the platform between the two women, ending in unresolved pressure exchange.
>
> retention_analysis: <Subject 1> (appears in [Shot 1]): fully_preserved - keep her facial identity, silver-white hair and visible ivory-and-gold clothing; her pose is newly choreographed. Exclude the foreground rock and other person's arm in <Picture 1>. <Subject 2> (appears in [Shot 1]): fully_preserved - keep her face, long black hair, red ribbons and beige clothing; exclude the other woman's limbs and the oversized red-edged weapon in <Picture 2>. Neither woman acquires the old archer's feather crown or the old swordswoman's wide-brim hat and black-purple costume. <Subject 3> (appears in [Shot 1]): partially_preserved - bow design and string only, without the reference lettering, background or separate display arrow. <Subject 4> (appears in [Shot 1]): fully_preserved - blade, hilt and guard geometry, with choreography determining orientation. <Subject 5> (appears in [Shot 1]): partially_preserved - stone surface, grass edges, cloud sea and left-back sunset; expand the fighting space and reframe for two women. No source-image pose, occlusion, lettering or composition is an opening frame.
>
> detailed_description: [Shot 1] {anchor} One continuous 9:16 side-view take, camera on the south side of the duel axis throughout. Both complete bodies and weapons are readable, roughly twenty metres apart, open sky above the central gap. Use the reference women's cinematic CG facial rendering with detailed skin, hair and fabric materials. At 0–1 seconds both women stand grounded; the archer holds her bow in her left hand, right hand free, and the swordswoman holds her sword at her waist with both hands. At 1–2.5 seconds the archer takes two running steps to the right, pushes off and completes one backward somersault. The camera rises slightly without rolling. At 2.5–4 seconds she extends her left leg to the right, pressing the front of her left foot against the strong inner lower bow limb, about two fifths of the bow height up from its lower tip. Her right knee stays bent. Her left hand visibly releases the grip and joins her right hand on the middle of the string; both hands pull left as the left leg pushes right, forming a readable taut string triangle. One slender silver-white energy arrow gathers above her supporting foot. At 4–5.5 seconds both hands release together once; the arrow leaves toward the right. Its point becomes a phoenix head and crest, its shaft continuously opens into a feathered chest and two wings, its tail becomes long white tail feathers. Only one arrow transforms into one phoenix, with no leftover arrow. The archer drops her left foot away from the bow, catches the grip again with her left hand and lands on the left side of the platform. The phoenix advances through the spacious central gap. At 5.5–7 seconds the black-haired swordswoman raises her sword with both hands above and behind her right shoulder, keeping her gaze leftward. The camera smoothly slides right while keeping the phoenix in the left part of the wide frame. At 7–9 seconds she plants the front foot, rotates hips and shoulders and makes one broad diagonal slash from upper right to lower left. A purple-black energy crescent separates from the physical blade and moves left. The solid silver sword stays in her hands. At 9–11 seconds dark vapor spirals into this travelling crescent; its leading edge forms a dragon muzzle, horns and obsidian scales, followed by one wingless eastern dragon body with fine violet light between scales. No dragon exists before this transformation. The camera gradually cranes backward and upward, keeping both creatures distinct and approaching each other. At 11–12 seconds the white phoenix from the left and the black dragon from the right make actual contact above the central stone gap. At 12–15 seconds hold their opposed silhouettes around a small silver-white and violet-black refractive interface; a transparent pressure ring pushes the nearest mist outward and then the farther cloud edges. One brief camera recoil occurs at contact, followed by stable wide framing. The archer remains grounded in the lower-left with her bow; the swordswoman remains in the lower-right holding her sword after the slash. Each creature reads about five times its woman's projected height, with complete readable feather and dragon silhouettes and no whiteout. The ending remains an active stalemate. Two women, one bow, one sword, one phoenix and one dragon only. Do not generate subtitles, captions or dialogue text overlays at any time. No reference-image lettering, logos, grid layouts or watermarks.
>
> overall_soundscape: Continuous high-altitude wind from 0–15 seconds. Footfalls and cloth rush at 1–2.5 seconds; bow tension at 2.5–4 seconds; a single string snap at 4 seconds followed by arrow whistle developing into feather rush at 4–5.5 seconds; landing scuff and grip contact at 5.5 seconds. Metal movement and sleeve rustle at 5.5–7 seconds, one planted step and accelerating sword swish at 7–9 seconds, gathering vapor hiss at 9–11 seconds. One low impact at actual creature contact around 11 seconds, followed by displaced-air roar and fine silver-violet crackle to 15 seconds. No dialogue or narration.
>
> non_diegetic_music: N/A

## 提交说明
按1—5顺序挂五张图片，选择参考模式；设置15秒、9:16。六字段引用块从subject_definitions到non_diegetic_music整段作为一次任务提交，不拆成六条。两张角色图均为身份参考，不放入首帧槽。生成后核对双手换握、足抵弓、兵器未变形、箭与剑气各仅一次、人物未混脸；实际输出尚未验证。

方言依据：[MiniMax官方H3仓库](https://github.com/MiniMax-AI/MiniMax-H3)，本地项目既有H3参考模式档案。源视频没有作为指令来源，其画面只作人物外观证据。
''')
