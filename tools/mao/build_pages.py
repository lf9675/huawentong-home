from pathlib import Path
import json,html,re,shutil
ROOT=Path(__file__).resolve().parents[2];D=ROOT/'du/textbook/2hcl/unit2/mao';OLD=ROOT/'du/textbook/2hcl/unit1/fang-feng-zheng'
L=json.loads((Path(__file__).parent/'lesson.json').read_text());slides=json.loads((D/'slides.json').read_text());E=html.escape;V=L['version'];S='../../../shared/lesson-v1/'
def shell(title,body,script=''):
 return f'<!doctype html><html lang="zh-SG"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title} · 华文通</title><link rel="stylesheet" href="{S}style.css?v={V}"><style>.concept b{{color:var(--red)}}.reading-links{{display:flex;gap:10px;flex-wrap:wrap}}</style></head><body><header class="site-header"><a href="../../../../../index.html"><img src="../../../../../assets/huawentong-logo.png" alt="华文通"></a><span>{L["label"]}</span></header><main>{body}</main>{script}</body></html>'
def panel(n):
 x,y,w,h=L['panelRects'][n-1];sheet=L['panelSheets'][n-1]
 return f'<div class="panel" style="aspect-ratio:{w}/{h}"><img src="assets/comic{sheet}.png" alt="原有漫画第{n}格" style="width:{1024/w*100}%;left:{-x/w*100}%;top:{-y/h*100}%"></div>'
reading=(OLD/'reading.html').read_text().replace('放风筝','猫').replace('20261019-ffz-1',V).replace('单元一','单元二')
(D/'reading.html').write_text(reading)
body=f'<p class="crumb"><a href="../../../../../index.html">华文通</a> / 中二 / 课文学习 / 单元二</p><section class="hero"><div><p class="eyebrow">核心课文</p><h1>猫</h1><p class="lead">一次养猫经历，为什么让“我”至今愧疚？</p><p>按段落读课文，用原句说明自己的理解。</p><div class="actions"><a class="btn primary" href="reading.html">开始／继续</a><a class="btn" href="reading.html#words">词语本</a></div></div><div>{panel(3)}</div></section><section class="cards">'
for n,title,desc,p in [(1,'猫的形象与家人的态度','第一至四段：外形、动作、精神状态及家人的反应。',1),(2,'事实与判断','第五至九段：家人怎样作出判断，猫受到怎样的对待。',5),(3,'愧疚与回应','第十至十二段：发现错误、理解情感，再以猫的口吻回应。',10)]:
 body+=f'<article class="card"><h2>第{["","一","二","三"][n]}课</h2><h3>{title}</h3><p>{desc}</p><div class="reading-links"><a href="reading.html#paragraph-{p}">读文</a><a href="reading.html#lesson{n}">问题</a></div></article>'
body+='</section><div class="actions"><a class="btn" href="../../../../ciyu/context-lab/index.html?unit=2#s2u2l2">词语预习</a><a class="btn" href="comics.html">漫画回读</a><a class="btn" href="reading.html#review">学习记录</a></div><div class="teacher-link"><a href="teacher.html">教师资料</a></div>'
(D/'index.html').write_text(shell('猫',body))
body='<p class="crumb"><a href="index.html">课文主页</a> / 漫画回读</p><h1>猫</h1><p><a href="reading.html#read">逐段阅读与词语积累</a></p>'
body+=''.join(f'<img class="comic-full" src="assets/comic{i}.png" alt="猫 原有漫画第{i}张"><p><a class="btn" href="assets/comic{i}.png" download>下载原图{i}</a></p>' for i in range(1,5))
body+='<section class="text-full">'+''.join(f'<h3>第{i+1}段</h3><p>{E(p)}</p>' for i,p in enumerate(L['paragraphs']))+f'<p>{E(L["author"])}</p></section>'
(D/'comics.html').write_text(shell('猫 · 漫画回读',body))
flow=[['第一课','导入3分钟；第1—4段图文读文14分钟；随段问题28分钟；订正与词语5分钟。','第4段作用分析一题，其余取证、点选和口答。'],['第二课','第5—9段图文读文12分钟；随段问题与拟声词练习34分钟；订正4分钟。','第9段动作作用一题；拟声词填空口答。'],['第三课','第10—12段读文8分钟；随段问题13分钟；形象与情感12分钟；开放回应12分钟；检查订正5分钟。','形象与情感一题，开放回应一题。']]
boundary='“罪状证实”“一定是猫”是家人当时的认定，不能当成已查明事实。“好像”“似乎”“仿佛”“猜想”保留不确定性。第10段黑猫衔鸟使“我”意识到误判；第12段只确定自家的猫没有回来，死亡仍是猜想。教参对开放想象提到“死后”，本配套不把这个想象设定当作课文事实，也不要求学生原谅主人。'
comicNote='4张原漫画共32格，画面与文字不改动。逐段页面只调整显示范围。第17格含对话的图画位置可能使说话人不够清楚，课堂以第6段“张妈喊道”为准；第20格漫画概括为“气愤”，课文写妻子“很难过”，取证用原文。漫画中推测、情绪及人物外形不作为独立事实证据。'
def table(head,rows):return '<table><tr>'+''.join('<th>'+E(x)+'</th>' for x in head)+'</tr>'+''.join('<tr>'+''.join('<td>'+E(str(x))+'</td>' for x in row)+'</tr>' for row in rows)+'</table>'
body='<p class="crumb"><a href="index.html">课文主页</a> / 教师资料</p><h1>猫</h1><p>中二高级华文 · 单元二 · 核心课文 · 3课时，每课按50分钟安排。</p><div class="actions"><a class="btn primary" href="slides.html">在线投影</a><a class="btn" href="downloads/mao.pptx" download>可编辑PPT</a><a class="btn" href="downloads/teacher-guide.docx" download>教师流程与答案</a><button id="downloadPack">下载整套配套</button><button id="downloadOffline">独立互动HTML</button></div><p id="packStatus" role="status"></p><h2>教学目标</h2><ol>'+''.join('<li><p>'+E(o)+'</p></li>' for o in L['objectives'])+'</ol><h2>三课时流程</h2>'+table(['课次','时间与内容','自主输入'],flow)+'<p>共150分钟。按段落先后处理课本问题，10组内容拆为17个问题页。全文综合题放在读完第12段之后。可减少重复汇报，不删课本题、重点书写和必做开放回应。</p><h2>文本与图画的边界</h2><p>'+boundary+'</p><p>'+comicNote+'</p><h2>参考答案与讲评</h2>'
for i,t in enumerate(L['tasks'],1):
 body+=f'<details><summary>{i}. {E(t["title"])} · {E(t["source"])}</summary>'+''.join('<p class="question">'+E(q)+'</p>' for q in t['questions'])+f'<p class="model">{E(t.get("fullAnswer",t["answer"]))}</p><p>{E(t["explain"])}</p><p><b>课堂身份：</b>{E(t["role"])}　<b>易错点：</b>{E(t["reject"])}</p>'+''.join('<p><b>'+E(q)+'</b><br>'+E(a)+'</p>' for q,a in t.get('oral',[]))+''.join('<p>'+E(a)+'</p>' for a in t.get('alternatives',[]))+'</details>'
body+='<h2>课本统整表</h2>'+table(['事情','对猫的描写','人的感受或反应'],[['猫被收养','毛色花白、没有光泽、瘦小；不活泼，一副忧郁的样子。','大家都不太喜欢它。'],['家里买了鸟','常跳到桌上，仰头凝望鸟笼；被赶走后又回来。','妻子提醒张妈留心猫，张妈把猫赶走。'],['死了一只鸟','趴在露台晒太阳，神态安详，嘴里好像在吃什么。','“我”怒气冲天，拿木棒追过去狠狠地打猫。']])
body+='''<h2>课堂操作与记录</h2><p>先点“读文”，一次一段；再进入该课问题。左边点原句，右边“加入原句”，可连续加入多句，重复原句不重复添加。题目答案在学生提交或口头讨论后才展开。客观题首次答错先给提示，5秒后可订正；主观题由教师核对，不用字数或关键词假装评分。</p><p>“检查”页填写姓名、班级、学号，导出完整JSON、逐题CSV或文字记录。首次回答与订正分别保存。口头共构题不计自动正确率。课堂建议分值见教师方案，均不是官方考试分值。</p><p>记录保存在同一设备、同一浏览器，没有账号云同步、自动发送教师或Google Sheet上传。清除浏览器前先导出。个人词语本与本站已接入的课文共用，按年级、单元、课文筛选；未知词仍建卡并标“释义待补充”。重置本课保留词语本。离线版与在线版记录不会自动互通。</p><p>课件原生文字可编辑，漫画是原图。下载整包后先解压，可用独立HTML学习及离线投影。本教师页公开含答案，请向学生发互动学习直达链接。没有另加新短文、课后一周小测、个人排行榜或速度奖励。</p>'''
(D/'teacher.html').write_text(shell('猫 · 教师资料',body,'<script src="pack.js"></script>'))
old=(OLD/'slides.html').read_text();controls=old[old.index('<script>const SLIDES='):];start=controls.index(';const $=');controls='<script>const SLIDES='+json.dumps(slides,ensure_ascii=False)+controls[start:];controls=controls[:controls.rfind('</body>')]
bounds={n:next(i+1 for i,s in enumerate(slides) if s['lesson']==n) for n in (1,2,3)}
body='<p class="crumb"><a href="teacher.html">教师资料</a> / 在线投影</p><div class="toolbar">'+''.join(f'<a class="btn" href="#{bounds[n]}">第{["","一","二","三"][n]}课</a>' for n in (1,2,3))+'''<select id="slideSelect" aria-label="选择课件页"></select></div><section class="projector" id="projector"><img id="slideImage" alt="课件"><div class="toolbar"><button id="prev">上一页</button><button id="next">下一页</button><button id="full">全屏</button><span class="slide-label" id="slideLabel"></span></div></section><details class="slide-notes"><summary>教师提示</summary><p id="notes"></p></details>'''
(D/'slides.html').write_text(shell('猫 · 在线投影',body,controls));shutil.copyfile(OLD/'pack.js',D/'pack.js')
(Path(__file__).parent/'teaching_meta.json').write_text(json.dumps(dict(flow=flow,boundary=boundary,comicNote=comicNote),ensure_ascii=False,indent=2))
print('Generated reading, homepage, teacher, comics and projector pages')
