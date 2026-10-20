from pathlib import Path
import json,html,re,shutil
R=Path(__file__).resolve().parents[2];D=R/'du/textbook/2hcl/unit1/wo-xiang-dui-ni-shuo';M=R/'du/textbook/2hcl/unit2/zhu-yang-ye-sheng-dong-wu';H=Path(__file__).parent
L=json.loads((H/'lesson.json').read_text());S=json.loads((D/'slides.json').read_text());E=html.escape;V=L['version'];shared='../../../shared/lesson-v1/'
flow=[['0—3分钟','短导入','用假设情境说一种关心家人的做法。'],['3—13分钟','国明 第一至二段','教师示范找烦恼，口头整理表格，再取证与核对建议。'],['13—24分钟','美华 第三至四段','师生共构烦恼与建议，留意条件和可能；口头评价建议。'],['24—35分钟','匿名 第五至六段','独立填写表格，并口头说明建议可能有效的理由。'],['35—40分钟','词语巩固','完成课本六个词语题，辨清委屈、内疚及窒息的语境义。'],['40—48分钟','开放回应','独立写3—4句，说明为什么，联系具体情境并自检。'],['48—50分钟','检查订正','订正错漏，按需要收藏词语、导出记录。']]
boundary='原文是三组网上求助与回应，按六条消息编号为六个教学段，段号仅用于课堂定位。保留发言者及各组时间，不把全文改排成时间顺序。国明的爸爸为何疲惫、美华是否提前告知、妈妈是否内疚、匿名同学是否成瘾及三人后来怎样做，原文均未确定。'
comic='复用全部三张原漫画，共24格，图片文件未改动。第一至六段依次对应第1—4、5—8、9—12、13—16、17—20、21—24格。第7—8、16、24格是建议情境，不是已经发生的结局；第15格的“也许”及第22格的“有些人的情况”须保留。漫画中的“苦恼／委屈”等概括不替代原文证据。'
def table(headers,rows):return '<table><thead><tr>'+''.join('<th>'+E(x)+'</th>' for x in headers)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+E(str(c))+'</td>' for c in row)+'</tr>' for row in rows)+'</tbody></table>'
def shell(title,body,script=''):
 return f'<!doctype html><html lang="zh-SG"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{E(title)} · 华文通</title><link rel="stylesheet" href="{shared}style.css?v={V}"><style>.concept b{{color:var(--red)}}.source-text,.text-full p{{white-space:pre-line}}.reading-links{{display:flex;gap:12px;flex-wrap:wrap}}</style></head><body><header class="site-header"><a href="../../../../../index.html"><img src="../../../../../assets/huawentong-logo.png" alt="华文通"></a><span>{L["label"]}</span></header><main>{body}</main>{script}</body></html>'
def panel(n):
 x,y,w,h=L['panelRects'][n-1];i=L['panelSheets'][n-1]
 return f'<div class="panel" style="aspect-ratio:{w}/{h}"><img src="assets/comic{i}.png" alt="原有漫画第{n}格" style="width:{1024/w*100}%;left:{-x/w*100}%;top:{-y/h*100}%"></div>'
s=(M/'reading.html').read_text().replace('助养野生动物','我想对你说').replace('单元二','单元一').replace('20261020-zy-1',V)
(D/'reading.html').write_text(s)
b='<p class="crumb"><a href="../../../../../index.html">华文通</a> / 中二 / 课文学习 / 单元一</p><section class="hero"><div><p class="eyebrow">生活空间 · 单元一第一篇 · 一课时</p><h1>我想对你说</h1><p class="lead">有些话，怎样让对方明白？</p><p>读懂三位同学的烦恼，理解辅导员的建议，再说出你的想法。</p><div class="actions"><a class="btn primary" href="reading.html">开始／继续</a><a class="btn" href="reading.html#words">个人词语本</a></div></div><div>'+panel(3)+'</div></section><div class="reading-links"><a class="btn" href="reading.html#paragraph-1">国明</a><a class="btn" href="reading.html#paragraph-3">美华</a><a class="btn" href="reading.html#paragraph-5">匿名同学</a></div><div class="actions"><a class="btn" href="../../../../ciyu/context-lab/index.html?unit=1#s2u1l1">词语预习</a><a class="btn" href="comics.html">漫画回读</a><a class="btn" href="reading.html#review">学习记录</a></div><div class="teacher-link"><a href="teacher.html">教师资料</a></div>'
(D/'index.html').write_text(shell(L['title'],b))
b='<p class="crumb"><a href="index.html">课文主页</a> / 漫画回读</p><h1>我想对你说</h1><p><a class="btn" href="reading.html">逐段阅读与词语积累</a></p>'
cn=['一','二','三','四','五','六']
for i,p in enumerate(L['paragraphs']):
 b+=f'<section class="workspace" style="margin-bottom:36px"><article class="paper"><h2>第{cn[i]}段</h2><p>{E(L["paragraphLabels"][i])}</p><p class="source-text">{E(p)}</p></article><aside class="paper"><h2>第{cn[i]}段</h2>'+''.join(panel(n) for n in L['panels'][i])+'</aside></section>'
b+='<h2>完整漫画原图</h2>'+''.join(f'<img class="comic-full" src="assets/comic{i}.png" alt="完整原漫画第{i}张"><p><a href="assets/comic{i}.png" download>下载原图{i}</a></p>' for i in range(1,4))
(D/'comics.html').write_text(shell('我想对你说 · 漫画回读',b))
b='<p class="crumb"><a href="index.html">课文主页</a> / 教师资料</p><h1>我想对你说</h1><p>中二高级华文 · 单元一 · 生活空间 · 1课时（按50分钟安排）</p><div class="actions"><a class="btn primary" href="slides.html">在线投影</a><a class="btn" href="downloads/wo-xiang.pptx" download>可编辑PPT</a><a class="btn" href="downloads/teacher-guide.docx" download>教师流程与答案</a><button id="downloadPack">整套下载</button><button id="downloadOffline">独立互动HTML</button></div><p id="packStatus" role="status"></p><h2>教学目标</h2><ol>'+''.join('<li><p>'+E(x)+'</p></li>' for x in L['objectives'])+'</ol><h2>一课时流程</h2>'+table(['时间','环节','课堂操作'],flow)+'<p>8组任务，28页课件。六条消息依序阅读；课本表格拆到相应对话。国明先示范，美华共同整理，两行可口述并按需记录；匿名一行独立填写，最后完成必做开放回应。共两项主要书面任务。</p><h2>课文与漫画核对</h2><p>'+boundary+'</p><p>'+comic+'</p><h2>逐题参考</h2>'
for i,t in enumerate(L['tasks'],1):
 b+=f'<details><summary>{i}. {E(t["title"])} · {E(t["source"])}</summary>'+''.join('<p class="question">'+E(q)+'</p>' for q in t['questions'])+f'<p class="model">{E(t["answer"])}</p><p>{E(t["explain"])}</p><p><b>答案点：</b>{E("；".join(t["points"]))}</p><p><b>易错：</b>{E(t["reject"])}</p><p><b>提示：</b>{E("；".join(t["hints"]))}</p></details>'
b+='<h2>课本三人表格参考</h2>'+table(['同学','烦恼','辅导员的建议'],[['国明','爸爸疲惫、不开心；想安慰又怕打扰，不知怎样做。','直接表达关心，可写卡片打气或拥抱爸爸。'],['美华','做小组作业晚归，受妈妈责备，解释被当成顶嘴。','体谅妈妈担心，找机会和她好好沟通。'],['匿名','每天只准玩半小时游戏且被监督，觉得不自由、不被理解。','从爸爸角度思考，理解他对学习及家人关系的顾虑。']])
b+='<h2>开放表达</h2><p>保留课本“你想对父母或辅导员说些什么”。学生说明为什么，并联系具体情境。可以写愿意分享的真实经历，也可明确写假设；不要强迫公开私人经历。允许合理表达不同意见，教师评价表达与逻辑，不以是否顺从父母决定得分。</p><p>课本与教参未提供分值或完整标准答案。这里为课堂参考：词语6分；匿名表格4分；开放回应4分，各意义点独立给分，总计14分（如教师需要）。网页不自动给主观题分数，也不将口头共构当成独立掌握。</p><h2>记录与使用</h2><p>课堂发学生互动页直达链接。原句可连续加入、复制粘贴和编辑；首次错误先提示，5秒后可重试。表格与开放回应保存首次回答和订正。检查页可填姓名、班级、学号并导出逐题CSV、完整JSON或文字记录。</p><p>记录只保存在同设备、同浏览器，不自动发给老师、不上传Google Sheet。词语本按年级、单元、课文汇总站内个人收藏，已知词带释义与原句；未知词可建立待补释义卡。清理浏览器前先导出。离线文件与线上记录不自动互通。</p><p>教师资料公开，链接本身不是权限保护。整套下载包含离线学生HTML、课件、教师方案、原图与离线投影。当前未安排新短文、延迟小测或课后打卡。</p>'
(D/'teacher.html').write_text(shell('我想对你说 · 教师资料',b,'<script src="pack.js"></script>'))
shutil.copyfile(M/'pack.js',D/'pack.js')
old=(M/'slides.html').read_text();script=old[old.index('<script>'):old.rindex('</script>')+9];script=re.sub(r'const SLIDES=.*?;let ',lambda _:'const SLIDES='+json.dumps(S,ensure_ascii=False)+';let ',script,count=1)
b='<p class="crumb"><a href="teacher.html">教师资料</a> / 在线投影</p><div class="toolbar"><select id="slideSelect" aria-label="选择课件页"></select></div><section class="projector" id="projector"><img id="slideImage" alt="课件"><div class="toolbar"><button id="prev">上一页</button><button id="next">下一页</button><button id="full">全屏</button><span class="slide-label" id="slideLabel"></span></div></section><details class="slide-notes"><summary>教师提示</summary><p id="notes"></p></details>'
(D/'slides.html').write_text(shell('我想对你说 · 在线投影',b,script))
p=R/'index.html';s=p.read_text();m=re.search(r'const DATA=(.*?);\n',s);data=json.loads(m[1]);unit=next(u for u in data['2']['texts'] if u['title']=='单元一');url='du/textbook/2hcl/unit1/wo-xiang-dui-ni-shuo/index.html'
unit['items']=[x for x in unit['items'] if x['url']!=url]
unit['items'].insert(0,dict(title='生活空间 · 我想对你说',url=url,note='一课时 · 亲子沟通 · 烦恼与建议 · 开放表达'))
p.write_text(s[:m.start(1)]+json.dumps(data,ensure_ascii=False,separators=(',',':'))+s[m.end(1):])
(H/'teaching_meta.json').write_text(json.dumps(dict(flow=flow,boundary=boundary,comic=comic),ensure_ascii=False,indent=2))
print('Built six lesson pages and first-position unit-one entry')
