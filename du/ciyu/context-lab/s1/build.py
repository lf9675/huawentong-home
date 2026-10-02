"""Build all Sec 1 lesson worksheets from reviewed, lesson-ordered source rows."""
from pathlib import Path
import json,html,re
P=Path(__file__).parent;C=P/'content';VERSION='20261002-s1-all-1'
lessons=json.loads((C/'lessons.json').read_text())
visuals={}
for line in (C/'visuals.tsv').read_text().splitlines():
 if not line or line.startswith('#'):continue
 w,*nodes=line.split('|');visuals[w]=[dict(zip(['icon','label'],n.split(':',1))) for n in nodes]
cores=[
'两肋插刀 来者不拒 直率 沉默寡言 冤枉','瞬间 狼狈 讥讽 赌气 手足无措','审案 拔刀相助 振振有词 心虚 哑口无言','哄堂大笑 离谱 叛逆 持之以恒 鸦雀无声',
'象征 风俗 辞旧迎新 预示 前夕','视讯 承诺 蒸腾 缺席 悦耳','饺子 剁肉 馅料 莫名其妙 偷龙转凤','天涯海角 分割 嚼 溢 盏',
'魅力 饱经风霜 融合 探索 娘惹','镶嵌 循环 映衬 松懈 领略','殖民地 投降 氧化 里程碑 发掘','擅长 紧凑 打道回府 不偏不倚 赞不绝口',
'一诺千金 言出必行 尴尬 维护 一帆风顺','赖床 滋味 催促 哀求 嗓子眼','何必 当铺 亏 慢条斯理 起航','徒劳无功 机械 蓬头垢面 气馁 梦寐以求',
'剩 偶尔 晋级 企业 橡皮擦','腾空而起 收拢 安然无恙 欺软怕硬 流连忘返','绞尽脑汁 华侨 由衷 独树一帜 挫折','传播 凸 熔化 陷入 飞跃',
'欣慰 攒钱 警惕 成就感 背井离乡','截至 延误 就绪 归功于 假以时日','新谣 琐事 朗朗上口 平凡 光芒','间隙 撤离 威胁 镇静 牺牲']
refs={
'华侨':['中国政府网：华侨、外籍华人的区分','https://www.gov.cn/fuwu/2012-11/15/content_2611992.htm'],
'新谣':['新加坡国家文物局 Roots：Xinyao','https://www.roots.gov.sg/ich-landing/ich/xinyao'],
'娘惹':['土生文化馆：Great Peranakans','https://www.nhb.gov.sg/peranakanmuseum/~/media/tpm/document/exhibitions/english%20gallery%20guide.pdf?la=en']}
for u in range(1,7):
 rows=[r.split('|') for r in (C/f'unit{u}.tsv').read_text().splitlines() if r and not r.startswith('#')];at=0
 for l in [x for x in lessons if x['unit']==u]:
  l['core']=cores[lessons.index(l)].split();l['words']=[];l['cloze']=[]
  for expected in l['vocab']:
   row=rows[at];at+=1;assert len(row)==8,row
   w,note,scene,correct,wrong1,wrong2,sentence,explain=row
   assert w==expected,(l['id'],expected,w)
   assert sentence.count('__')==1 and len({correct,wrong1,wrong2})==3,w
   assert max(len(scene),len(note),len(explain))<=100,w
   item=dict(word=w,note=note,scene=scene,question=f'这里的“{w}”是什么意思？',options=[correct,wrong1,wrong2],explain=explain,en='',core=w in l['core'],nodes=visuals.get(w,[]),sourceLabel='依据教师提供的课内词表编写；情境为教学新设，不是课文原句。',reference=refs.get(w))
   l['words'].append(item)
   accepted=['一诺千金','言出必行'] if w in ['一诺千金','言出必行'] else [w]
   l['cloze'].append(dict(word=w,sentence=sentence,hint=note,accepted=accepted))
  assert len(l['core'])==5 and set(l['core'])<=set(l['vocab'])
  l['groups']=[list(range(len(l['cloze'])))];l['grade']=1
 assert at==len(rows)
assert len(lessons)==24 and sum(len(l['words']) for l in lessons)==305
D=dict(version=VERSION,lessons=lessons)
(P/'concise-data.json').write_text(json.dumps(D,ensure_ascii=False,indent=2)+'\n')
e=html.escape
h=['<!doctype html><html lang="zh-Hans"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>中一全部课文词语 · 教师参考</title><style>body{max-width:960px;margin:auto;padding:24px;font:18px/1.7 system-ui}h1,h2,h3,summary{font-family:KaiTi,"Kaiti SC",serif}details{border-bottom:1px solid #ddd;padding:10px}summary{cursor:pointer}.note{color:#555}@media print{details>*{display:block}h2{break-before:page}a{color:inherit}}</style><a href="index.html">学生学习单</a><h1>中一全部课文词语 · 教师参考</h1><p>6单元、24课、305个课内词语条目；每词一道语境选择题及一道迁移填空。重复出现在不同课文的词分别保留。</p><p>初学用途：教师先简讲，再让学生点选、订正；每课先呈现5个重点词，其他词可展开。填空共用本课完整词库，每词使用一次，不分小词库。字词线索为简明释义、语义拆解或记忆提示，不冒充古文字字源。无需打字、不计时、不排名。</p><p>来源：用户《中一词语表.docx》；单元一至三词义另参考所提供上册课文。所有学习情境和填空均为教学创设，不声称是课文原句。中一下册全文未在本次本地资料中取得，不对它作引文或情节断言。</p><p>近义词判分：《培养好习惯》的“一诺千金／言出必行”在两道守信语境中都可接受，但全课每词仍只能用一次，不把自然的近义替换判错。其他题按题目限定及本课词库判断。</p><p>打印后备：本页列出完整情境、选项、解析及填空答案；教师可选题口头呈现或转写到黑板。手机和iPad端进度只保存在当前设备。</p>']
for l in lessons:
 h.append(f'<h2 id="{l["id"]}">单元{l["unit"]} · 第{l["lesson"]}课《{e(l["title"])}》</h2><p><a href="index.html#{l["id"]}">打开本课</a> · 共{len(l["words"])}词</p><p>重点词：{e("、".join(l["core"]))}</p>')
 for w in l['words']:
  h.append(f'<details><summary>{e(w["word"])}</summary><p>字义线索：{e(w["note"])}</p><p>学习情境：{e(w["scene"])}</p><p>{e(w["question"])}</p><p>选项（学生端打乱）：{e("／".join(w["options"]))}</p><p><b>答案：{e(w["options"][0])}</b><br>解析：{e(w["explain"])}</p>')
  if w['reference']:h.append(f'<p><a href="{e(w["reference"][1])}">{e(w["reference"][0])}</a></p>')
  h.append('</details>')
 h.append('<h3>全词库填空参考</h3><ol>')
 for q in l['cloze']:
  a='／'.join(q['accepted']);h.append('<li>'+e(q['sentence']).replace('__','<b>〔'+e(a)+'〕</b>')+'</li>')
 h.append('</ol>')
h.append('<script>window.addEventListener("beforeprint",()=>document.querySelectorAll("details").forEach(d=>d.open=true));</script></html>');(P/'teacher.html').write_text('\n'.join(h))
print(f'Built {len(lessons)} lessons / 305 context questions / 305 cloze items; {sum(bool(w["nodes"]) for l in lessons for w in l["words"])} relational diagrams plus custom SVG diagrams.')
