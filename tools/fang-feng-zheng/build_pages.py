from pathlib import Path
import json,html,re,shutil
ROOT=Path(__file__).resolve().parents[2]; D=ROOT/'du/textbook/2hcl/unit1/fang-feng-zheng'; OLD=D.parent/'ba-ai-shuo-chu-lai'
L=json.loads((Path(__file__).parent/'lesson.json').read_text()); slides=json.loads((D/'slides.json').read_text());E=html.escape;V=L['version'];S='../../../shared/lesson-v1/'
def shell(title,body,script=''):
    return f'<!doctype html><html lang="zh-SG"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title} · 华文通</title><link rel="stylesheet" href="{S}style.css?v={V}"><style>.concept b{{color:var(--red)}}.reading-links{{display:flex;gap:10px;flex-wrap:wrap}}</style></head><body><header class="site-header"><a href="../../../../../index.html"><img src="../../../../../assets/huawentong-logo.png" alt="华文通"></a><span>中二高级华文 · 单元一</span></header><main>{body}</main>{script}</body></html>'
def panel(n):
    x,y,w,h=L['panelRects'][n-1]
    return f'<div class="panel" style="aspect-ratio:{w}/{h}"><img src="assets/comic{(n-1)//10+1}.png" alt="原有漫画第{n}格" style="width:{1024/w*100}%;left:{-x/w*100}%;top:{-y/h*100}%"></div>'
reading=(OLD/'reading.html').read_text().replace('把爱说出来','放风筝').replace('20261019-2',V).replace('</head>','<style>.concept b{color:var(--red)}</style></head>')
(D/'reading.html').write_text(reading)
body=f'''<p class="crumb"><a href="../../../../../index.html">华文通</a> / 中二 / 课文学习 / 单元一</p><section class="hero"><div><p class="eyebrow">巩固课文</p><h1>放风筝</h1><p class="lead">一次海边出游，怎样改变“我”的想法？</p><p>按段落读懂课文，用原句说明想法。</p><div class="actions"><a class="btn primary" href="reading.html">开始／继续</a><a class="btn" href="reading.html#words">词语本</a></div></div><div>{panel(18)}</div></section><section class="cards">'''
for n,title,desc,p in [(1,'晚归与冷战','第一至九段：冲突的起因、父母反应与“我”的心情。',1),(2,'海边的变化','第十至十四段：从妈妈的行动、爸爸的话理解爱与引导，再练习扩写。',10),(3,'比较与回应','全文人物比较，以及自由与管教的开放回应。',14)]:
    body+=f'<article class="card"><h2>第{["","一","二","三"][n]}课</h2><h3>{title}</h3><p>{desc}</p><div class="reading-links"><a href="reading.html#paragraph-{p}">读文</a><a href="reading.html#lesson{n}">问题</a></div></article>'
body+='</section><div class="actions"><a class="btn" href="../../../../ciyu/context-lab/index.html?unit=1#s2u1l3">词语预习</a><a class="btn" href="comics.html">漫画回读</a><a class="btn" href="reading.html#review">学习记录</a></div><div class="teacher-link"><a href="teacher.html">教师资料</a></div>'
(D/'index.html').write_text(shell('放风筝',body))
body='<p class="crumb"><a href="index.html">课文主页</a> / 漫画回读</p><h1>放风筝</h1><p><a href="reading.html#read">逐段阅读与词语积累</a></p>'
body+=''.join(f'<img class="comic-full" src="assets/comic{i}.png" alt="放风筝原有漫画第{i}张"><p><a class="btn" href="assets/comic{i}.png" download>下载原图{i}</a></p>' for i in range(1,4))
body+='<section class="text-full">'+''.join(f'<h3>第{i+1}段</h3><p>{E(p)}</p>' for i,p in enumerate(L['paragraphs']))+f'<p>{E(L["author"])}</p></section>'
(D/'comics.html').write_text(shell('放风筝 · 漫画回读',body))
flow3=[['第一课','导入3分钟；第1—3段读文与问题24分钟；第4—9段读文与问题18分钟；订正、词语5分钟。','第3段描写作用短答；其余点选、取证与口答。'],['第二课','复习3分钟；第10—11段12分钟；第12—14段20分钟；扩写句子10分钟；订正5分钟。','第12段原因短答、课本扩写一句。'],['第三课','回顾5分钟；人物比较18分钟；开放回应17分钟；自检、订正和词语10分钟。','人物比较、开放回应独立书写。']]
flow2=[['第一课','导入3分钟；第1—3段20分钟；第4—9段12分钟；第10—11段10分钟；订正5分钟。','保留第3段短答，其他用点选、取证和口答。'],['第二课','第12—14段12分钟；扩写示范与学生口头扩写5分钟；人物比较13分钟；开放回应15分钟；订正5分钟。','第12段改口头共构；人物比较与开放回应保留独立书写。']]
def table(head,rows):return '<table><tr>'+''.join('<th>'+E(x)+'</th>' for x in head)+'</tr>'+''.join('<tr>'+''.join('<td>'+E(str(x))+'</td>' for x in row)+'</tr>' for row in rows)+'</table>'
boundary='第1段尚未交代静音模式，第3段才核对原因。“不讲理”是“我”当时的想法。“想和好”“希望改善关系”属于结合行为的合理推断。第11段主要运用比喻，也有拟人色彩，不作排他的单选判分。结尾只写醒悟，没有明确写出道歉或冷战正式结束。理解父母苦心，不等于所有管教都正确。'
body='''<p class="crumb"><a href="index.html">课文主页</a> / 教师资料</p><h1>放风筝</h1><p>中二高级华文 · 单元一 · 2—3课时，每课按50分钟安排。</p><div class="actions"><a class="btn primary" href="slides.html">在线投影</a><a class="btn" href="downloads/fang-feng-zheng.pptx" download>可编辑PPT</a><a class="btn" href="downloads/teacher-guide.docx" download>教师流程与答案</a><button id="downloadPack">下载整套配套</button><button id="downloadOffline">独立互动HTML</button></div><p id="packStatus" role="status"></p><h2>教学目标</h2><ol>'''+''.join('<li><p>'+E(x)+'</p></li>' for x in L['objectives'])+'</ol><h2>三课时完整安排</h2>'+table(['课次','课堂流程','自主输入'],flow3)+'<h2>两课时安排</h2>'+table(['课次','课堂流程','自主输入'],flow2)+'<p>两课时适合教师集中讲解、减少全班重复汇报。若每课只有40分钟，采用三课时。各方案均保留原题、人物自主概括及必做开放回应，不另加新短文或课后一周小测。</p><h2>文本与图画的边界</h2><p>'+boundary+'</p><p>第14格原漫画横跨第8、9段，按两段显示同一完整格，保留原图台词。漫画中的人物外形与地点细节是插画呈现，答题以课文为依据。</p><h2>参考答案与讲评</h2>'
for i,t in enumerate(L['tasks']):
    body+=f'<details><summary>{i+1}. {E(t["title"])} · {E(t["source"])}</summary>'+''.join('<p class="question">'+E(q)+'</p>' for q in t['questions'])+f'<p class="model">{E(t["answer"])}</p><p>{E(t["explain"])}</p><p><b>易错点：</b>{E(t["reject"])}</p>'+''.join('<p><b>'+E(q)+'</b><br>'+E(a)+'</p>' for q,a in t.get('oral',[]))+''.join('<p>'+E(a)+'</p>' for a in t.get('alternatives',[]))+'</details>'
body+='''<h2>学习记录与使用</h2><p>请发学生互动链接；本教师页公开含答案。学习答案保存在同一设备、同一浏览器，保留首次回答、订正及提示使用，支持JSON、逐题CSV和文字导出。主观题由教师核对，不按字数或关键词自动评分。没有自动发送教师或接入Google Sheet。</p><p>个人词语本与华文通已接入的课文共用，按年级、单元、课文筛选。已收录词带入语境释义和真实例句；未收录词也能收藏，标为释义待补。重置本课不删除词语本。清除浏览器会丢失本地记录，换设备前先导出。离线版与在线版记录不会自动互通。</p><p>三张原漫画完整保留；课件原生文字、图形可编辑，漫画仍是图片。在线投影与PPT页序一致。课本用“外貌描写”归类表情和汗珠，课堂沿用其口径，可进一步说明神态。分值仅供教师课堂参考，不是官方评分。</p><p class="footer-note">依据本次上传的14段课文、巩固练习、3张教参截图与3张漫画。设备朗读使用浏览器语音。未做真实iPad或原生PowerPoint实测。</p>'''
(D/'teacher.html').write_text(shell('放风筝 · 教师资料',body,'<script src="pack.js"></script>'))
# Reuse the already accepted projector controls, replacing only lesson content and page bounds.
old=(OLD/'slides.html').read_text();controls=old[old.index('<script>const SLIDES='):]
start=controls.index(';const $=')
controls='<script>const SLIDES='+json.dumps(slides,ensure_ascii=False)+controls[start:]
controls=controls[:controls.rfind('</body>')]
bounds={n:next(i+1 for i,s in enumerate(slides) if s['lesson']==n) for n in (1,2,3)}
body='<p class="crumb"><a href="teacher.html">教师资料</a> / 在线投影</p><div class="toolbar">'+''.join(f'<a class="btn" href="#{bounds[n]}">第{["","一","二","三"][n]}课</a>' for n in (1,2,3))+'''<select id="slideSelect" aria-label="选择课件页"></select></div><section class="projector" id="projector"><img id="slideImage" alt="课件"><div class="toolbar"><button id="prev">上一页</button><button id="next">下一页</button><button id="full">全屏</button><span class="slide-label" id="slideLabel"></span></div></section><details class="slide-notes"><summary>教师提示</summary><p id="notes"></p></details>'''
(D/'slides.html').write_text(shell('放风筝 · 在线投影',body,controls))
shutil.copyfile(OLD/'pack.js',D/'pack.js')
# Only add the requested lesson in the existing unit; all other entries remain byte-for-byte.
p=ROOT/'index.html';s=p.read_text();old='{"title":"核心课文 · 把爱说出来","url":"du/textbook/2hcl/unit1/ba-ai-shuo-chu-lai/index.html","note":"逐段图文 · 人物比较 · 开放回应 · 词语本与闪卡"}'
new='{"title":"巩固课文 · 放风筝","url":"du/textbook/2hcl/unit1/fang-feng-zheng/index.html","note":"逐段图文 · 父母比较 · 扩写句子 · 自由与管教"}'
if new not in s:
    assert s.count(old)==1;s=s.replace(old,old+','+new);p.write_text(s)
(Path(__file__).parent/'teaching_meta.json').write_text(json.dumps({'flow3':flow3,'flow2':flow2,'boundary':boundary},ensure_ascii=False,indent=2))
print('Pages generated and unit-one navigation added.')
