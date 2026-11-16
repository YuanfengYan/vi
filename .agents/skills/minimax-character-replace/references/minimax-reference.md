# MiniMax 混合参考与人物替换正文

## 核对来源与入口

核对日期：2026-11-04。以下官方资料用于核实格式和能力，不代表所有网页、第三方服务或同名型号都提供相同输入：

- [MiniMax官方H3仓库](https://github.com/MiniMax-AI/MiniMax-H3)：区分FL2VA首尾帧与Ref2VA混合参考；当前公开说明中，后者可以接收视频及图片。
- [官方full-reference提示词指南](https://github.com/MiniMax-AI/MiniMax-H3/blob/main/skills/h3-prompt-writing/references/ref-en.txt)：参考标签、编辑任务、六字段与音轨关系。

执行本任务前，查看目标型号及实际入口的当前官方说明，确认：支持编辑来源视频并同时挂人物图片；素材数量、原片长度、输出时长、画幅和音轨复用可用。优先使用官方仓库、官方平台文档，不用第三方同名页面代替能力证明。平台入口的限制可能小于模型规格，不能由“支持MiniMax”推断“支持混合参考”。不确定时标明尚未核实，询问具体入口，不编造API字段。

这不是原生非生成式逐像素编辑工具；“保留”是提示词要求，实际保真程度只能在产物中验证。不要向用户承诺画面、动作或音轨逐像素/逐采样一致。

## 标签与正文结构

- 图片依挂图顺序使用`<Picture 1>`、`<Picture 2>`，视频依视频顺序使用`<Video 1>`。两类分别从1编号，不共用序号。
- `<Subject N>`定义要转移的人物；其定义中引用提供外观的图片。不要把同一人重新定义为另一个主体。
- 编辑任务的`summary`以`[video editing + reference generation]`标明关系，明确视频是待编辑底片，图片提供替换身份；不是延续视频，也不是只提取动作生成新场景。
- 六字段依次为`subject_definitions`、`summary`、`retention_analysis`、`detailed_description`、`overall_soundscape`、`non_diegetic_music`；字段和值均用英文，原片对白及画面文字保留原语言。
- 原片多镜头时遵循实际镜序和切点，逐镜说明有变化的可见人物、交互和遮挡；不能把整个多镜头视频伪写成一镜到底。只在核实切点时写具体时间，缺少依据时补看素材，不捏造时间戳。

## 按本次素材改写的六字段骨架

下面是编写模板，不是可直接交付的最终提示词。把尖括号素材标签保留；所有大括号项必须用本次看过的素材事实替换，删去不存在的人物、声层和指令。单人任务只保留一个映射；多人任务按需扩展。

```text
subject_definitions:
<Video 1> is the footage being edited, supplying its existing scene, performances, objects, effects and camera timeline.
<Subject 1> is the person in <Picture 1>, identified by {observed face, hair, clothing and accessories}.
<Subject 2> is the person in <Picture 2>, identified by {observed face, hair, clothing and accessories}.

summary:
[video editing + reference generation] Edit <Video 1> by replacing {unambiguous original person A} with <Subject 1> and {unambiguous original person B} with <Subject 2>. Change {confirmed appearance scope} while following the source events and photography.

retention_analysis:
<Video 1>: partially_preserved - replace only the selected character appearance. Retain other people, actions, held objects, setting, effects, camera path, cuts, framing and timing.
<Subject 1>: attribute_transfer - apply {confirmed appearance attributes} to source person A, without transferring the picture's pose, display objects or background.
<Subject 2>: attribute_transfer - apply {confirmed appearance attributes} to source person B, without transferring the picture's pose, display objects or background.

detailed_description:
Follow the source sequence and its existing composition and lighting. {Describe the observed source shots, action and interactions in order, binding the corresponding replacement subject at each appearance.} Track each assigned identity through crossings, turns, cuts and occlusion. Retain the source performers' gaze, expressive intent, trajectories, balance, hand contacts and weapon grips. Fit the replacement appearance to that performance, with hair and garments reacting to the source motion. Keep uncovered background and unselected people as in the source; leave character-free views character-free. Retain existing in-scene writing and overlays. Add no new captions, logos, action or props. Use the original event times and correctly displayed orientation and framing.

overall_soundscape:
{Use the selected source-audio route below; describe only the actual ambience/physical sound layers.}

non_diegetic_music:
{Retain the original score if present under the selected audio route; otherwise N/A.}
```

不要机械保留上面模板的全身衣物条款。用户只换脸时，把转移属性收窄为面部身份，明确原片头发、服装、饰品和身体保持；只换脸并不自动包含头发。

若用户要求只替换外观而原视频已有说话，保持原表演、口型与原音频时序，不因为换成新人物就添加或翻译台词。没有逐字核实的原台词不转录进正文。

## 原声的两条实际路径

按执行入口选一条，不混写已经执行和计划执行：

1. **已确认可复用音轨**：把真正启用或挂载的音轨定义为`<Audio 1>`，并说明是原视频的同步声音；`summary`加入`audio reuse`。完整音轨直接复用时，在`retention_analysis`使用`fully_copy`，按实际声层在两个声音字段引用该标签。不另加同一音轨已包含的音效或音乐。
2. **不能复用或尚未确认**：不凭视频文件带声音就虚构`<Audio 1>`。说明保留原声音的交付目标；中文操作说明记录“成片阶段沿用原音轨，当前入口的精确音频复制未确认”。两个声音字段按已观察声层说明无需新录、新增音效或配乐；不把此路径写成`fully_copy`已生效，也不声称已完成合成。

原视频没有音轨时，`overall_soundscape`要求保持无声，`non_diegetic_music`写`N/A`。原音轨存在音乐时，不使用会抹掉原曲的全局禁配乐指令。

## 格式和时长限制

记录源视频的实测长度与正确显示的宽高/方向，不只读取未应用旋转信息的编码宽高。必要时核对播放器显示或解码后帧。

若源片为10.64秒而入口只允许整数秒，不能擅自改成11秒并停帧，也不能缩至10秒。说明差异，提出保留原速后补尾并裁回、经用户选择的分段编辑、或换用兼容入口等适用方案；用户选定之前，完整提示词只能标为草稿。分段也会影响接缝与参考长度，不能承诺无缝。

## 验收用例

用以下请求回读技能输出，检查决策与素材绑定，不以关键词出现次数代替行为验收：

| 请求/情况 | 必须得到的结果 |
|---|---|
| source.mov白发女→项目弓手、黑发女→项目剑士 | 视频保留原场景与战斗，两张图提供目标外观；不新编龙凤对攻 |
| 仅替换画面中戴眼镜的人 | 只绑定该人，其他角色与背景保留 |
| 两人在不同镜头交换左右位置 | 同一原人物始终对应同一图片，不按左右改绑 |
| 人物图含弓、剑或灰背景 | 只提取请求的外观；原片持物保留，不加入图片道具或背景 |
| “只换脸，衣服和头发保持” | 转移属性只包含脸，正文不要求转移整套造型 |
| 原片横屏，项目默认竖屏 | 保留原片显示画幅；项目全局配置不变 |
| 原片10.64秒，入口仅整数秒 | 明示不兼容并等待方案选择，不擅自补尾/裁切/变速 |
| 视频/必要图片不可读 | 报具体缺口，不生成标为就绪的最终提示词 |
| 多张人物图映射不明确 | 只询问缺失对应，不自行按发色或文件顺序猜测 |
| 仅支持首帧的MiniMax入口 | 说明不支持所需混合参考，不伪装为支持视频编辑 |
| 视频有声音但音轨复制未确认 | 无虚构Audio槽，无已复制成功声明，说明后期沿用原音轨 |
