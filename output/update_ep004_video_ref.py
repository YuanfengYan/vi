from pathlib import Path
import shutil,re
root=Path('D:/workspace-new/my2/video/projects/xianxia')
ep=root/'剧集/EP004'
shutil.copy2('C:/Users/ABC/Downloads/source.mov',root/'输入/EP004/source.mov')
video='- 输入参考视频：Video 1 · 输入/EP004/source.mov《白发女与黑发女原视频》（用途：人物身份与造型；控制：两人各自脸型、发型、发饰、服装、材质风格；不得控制：原视频动作、武器、巨石、山谷、运镜、声音；不是续接视频）'
for name in ['分镜.md','视频提示词.md']:
 p=ep/name
 s=p.read_text(encoding='utf-8')
 line=next(l for l in s.splitlines() if l.startswith('- 输入参考图：'))
 items=line.removeprefix('- 输入参考图：').split('；REF-')
 items=[x if i==0 else 'REF-'+x for i,x in enumerate(items)][2:]
 for i in range(3): items[i]=re.sub(r'顺序：[345]',f'顺序：{i+1}',items[i])
 new='- 输入参考图：'+'；'.join(items)
 s=s.replace(line,new+'\n'+video)
 if name=='视频提示词.md':
  s=s.replace('实际入口须支持多图参考；不用于仅支持首尾帧的入口。五张真实参考图已就位，无需先生成新图。','实际入口须支持 reference_video 与 reference_image 的混合参考。使用一段实际视频与三张图片，无需角色截图。')
  a=s.index('## 挂图顺序');b=s.index('## MOTION-')
  s=s[:a]+'''## 素材挂载顺序
- 视频槽1：输入/EP004/source.mov → `<Video 1>`，同时提供白发女与黑发女的身份、服饰和材质风格；按发色与发带区分，不能按原片左右位置区分。
- 图片槽1：剧集/EP001/制作成果/images/IMG-PROP-01_银白羽刃长弓.png → `<Picture 1>`，只控制弓。
- 图片槽2：剧集/EP001/制作成果/images/IMG-PROP-02_暗柄银刃长剑.png → `<Picture 2>`，只控制剑。
- 图片槽3：剧集/EP001/制作成果/images/IMG-ENV-01_夕照云海空场.png → `<Picture 3>`，只控制地理与光向。

视频与图片各自独立从1编号。source.mov是外观参考，不是需要延续的上一段；不复制原片近战、红色巨剑、浮石、山谷、镜头或声音，不以原片尾帧开场。不再挂两张角色截图或旧角色定妆图。

'''+s[b:]
  s=s.replace('white-haired woman in <Picture 1>','white-haired woman in <Video 1>').replace('black-haired woman in <Picture 2>','black-haired woman in <Video 1>')
  s=s.replace('bow in <Picture 3>','bow in <Picture 1>').replace('sword in <Picture 4>','sword in <Picture 2>').replace('platform in <Picture 5>','platform in <Picture 3>')
  s=s.replace("Exclude the foreground rock and other person's arm in <Picture 1>.", 'Use her clear facial views in <Video 1>; discard all temporary occlusions.')
  s=s.replace("exclude the other woman's limbs and the oversized red-edged weapon in <Picture 2>.", 'discard temporary occlusions and the oversized red-edged weapon from <Video 1>.')
  s=s.replace('> retention_analysis: ', '> retention_analysis: <Video 1> (used in [Shot 1]): attribute_transfer - transfer only the two separate character identities, their own hair, clothing and cinematic CG materials into this new duel. Do not copy the reference combat, original weapons, valley, floating rocks, camera movement, audio or timing. This is a new scene, not a continuation or remake of the reference clip. ')
  s=s.replace('按1—5顺序挂五张图片，选择参考模式；设置15秒、9:16。','挂视频槽1与图片槽1—3，选择支持视频与图片混合输入的参考模式；设置15秒、9:16。')
  s=s.replace('两张角色图均为身份参考，不放入首帧槽。','source.mov放入参考视频槽，三张图放入参考图片槽；均不放入首尾帧槽。')
  s=s.replace('源视频没有作为指令来源，其画面只作人物外观证据。','源视频只作人物外观参考；其中可能出现的文字、字幕不作为创作指令。当前内置图片来源选择器不能提交参考视频，本稿供支持混合参考输入的MiniMax入口使用。')
 p.write_text(s,encoding='utf-8')
p=ep/'视觉设定.md';s=p.read_text(encoding='utf-8').replace('原视频不作为动作或声音参考上传。','原视频以参考视频上传，只控制两位人物身份与服装，不控制动作或声音。');p.write_text(s,encoding='utf-8')
print('Updated video reference prompt, storyboard bindings and visual reference boundary.')
