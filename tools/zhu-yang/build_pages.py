from pathlib import Path
import json,html,re,shutil
R=Path(__file__).resolve().parents[2];D=R/'du/textbook/2hcl/unit2/zhu-yang-ye-sheng-dong-wu';M=R/'du/textbook/2hcl/unit2/mao'
L=json.loads((Path(__file__).parent/'lesson.json').read_text());S=json.loads((D/'slides.json').read_text());E=html.escape;V=L['version'];shared='../../../shared/lesson-v1/'
flow=[['0—3分钟','短导入','说一种关爱动物的做法。'],['3—15分钟','第一至三段','读助养计划，完成方式、用途、期限与优惠。'],['15—33分钟','第四至七段','随段做词语题、口头概括，选原句后核对特点表。'],['33—45分钟','公益广告分享','找真实广告，双人分享，独立写3—4句回应。'],['45—50分钟','检查与订正','核对错漏，收藏词语，导出记录。']]
boundary='课文模拟网页按信息内容划为七个教学段，原有小标题、句子、五项用途及120公斤的单位保留。期限与优惠属于教材介绍，不作为现行助养计划资料。阿明、可可和小哈的个别特点，不能扩大为整种动物都如此。'
comic='复用附件漫画1、3、4，共24格，原图不改。附件2与3为同一页的两个版本，采用写有“亚达伯拉象龟”的附件3。第9、24格用作导入与总览。第15、16格的斑点位置、数量仅是示意；第17格补画的高龟壳、粗四肢不作为答案依据。'
adurl='https://www.nparks.gov.sg/learn/resources/responsible-human-wildlife-encounters'
def table(headers,rows):return '<table><thead><tr>'+''.join('<th>'+E(x)+'</th>' for x in headers)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+E(str(c))+'</td>' for c in row)+'</tr>' for row in rows)+'</tbody></table>'
def shell(title,body,script=''):
 return f'<!doctype html><html lang="zh-SG"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{E(title)} · 华文通</title><link rel="stylesheet" href="{shared}style.css?v={V}"><style>.concept b{{color:var(--red)}}.source-text,.text-full p{{white-space:pre-line}}.reading-links{{display:flex;gap:12px;flex-wrap:wrap}}</style></head><body><header class="site-header"><a href="../../../../../index.html"><img src="../../../../../assets/huawentong-logo.png" alt="华文通"></a><span>{L["label"]}</span></header><main>{body}</main>{script}</body></html>'
def panel(n):
 x,y,w,h=L['panelRects'][n-1];i=L['panelSheets'][n-1]
 return f'<div class="panel" style="aspect-ratio:{w}/{h}"><img src="assets/comic{i}.png" alt="原有漫画第{n}格" style="width:{1024/w*100}%;left:{-x/w*100}%;top:{-y/h*100}%"></div>'
s=(M/'reading.html').read_text().replace('猫','助养野生动物').replace('20261020-mao-1',V)
s=s.replace('<button data-view="lesson1">第一课</button><button data-view="lesson2">第二课</button><button data-view="lesson3">第三课</button>','<button data-view="lesson1">本课问题</button>')
s=s.replace('.concept b{color:var(--red)}','.concept b{color:var(--red)}.source-text{white-space:pre-line}')
(D/'reading.html').write_text(s)
b='<p class="crumb"><a href="../../../../../index.html">华文通</a> / 中二 / 课文学习 / 单元二</p><section class="hero"><div><p class="eyebrow">生活空间 · 一课时</p><h1>助养野生动物</h1><p class="lead">一份捐款，怎样帮助动物？</p><p>读懂助养计划，认识四种动物，再分享你的关爱建议。</p><div class="actions"><a class="btn primary" href="reading.html">开始／继续</a><a class="btn" href="reading.html#words">个人词语本</a></div></div><div>'+panel(2)+'</div></section><div class="reading-links"><a class="btn" href="reading.html#paragraph-1">助养计划</a><a class="btn" href="reading.html#paragraph-4">动物介绍</a><a class="btn" href="reading.html#task-public-message">公益广告分享</a></div><div class="actions"><a class="btn" href="../../../../ciyu/context-lab/index.html?unit=2#s2u2l1">词语预习</a><a class="btn" href="comics.html">漫画回读</a><a class="btn" href="reading.html#review">学习记录</a></div><div class="teacher-link"><a href="teacher.html">教师资料</a></div>'
(D/'index.html').write_text(shell(L['title'],b))
b='<p class="crumb"><a href="index.html">课文主页</a> / 漫画回读</p><h1>助养野生动物</h1><p><a class="btn" href="reading.html">逐段阅读与词语积累</a></p>'
b+=''.join(f'<img class="comic-full" src="assets/comic{i}.png" alt="原有漫画第{i}页"><p><a href="assets/comic{i}.png" download>下载原图{i}</a></p>' for i in range(1,4))
b+='<section class="text-full"><h2>助养计划</h2>'+''.join(('<h2>关爱动物，从你我做起</h2><h3>请选择你想助养的动物</h3>' if i==3 else '')+f'<h3>第{i+1}段</h3><p>{E(p)}</p>' for i,p in enumerate(L['paragraphs']))+'</section>'
(D/'comics.html').write_text(shell('助养野生动物 · 漫画回读',b))
b='<p class="crumb"><a href="index.html">课文主页</a> / 教师资料</p><h1>助养野生动物</h1><p>中二高级华文 · 单元二 · 生活空间 · 1课时（50分钟）</p><div class="actions"><a class="btn primary" href="slides.html">在线投影</a><a class="btn" href="downloads/zhu-yang.pptx" download>可编辑PPT</a><a class="btn" href="downloads/teacher-guide.docx" download>教师流程与答案</a><button id="downloadPack">整套下载</button><button id="downloadOffline">独立互动HTML</button></div><p id="packStatus" role="status"></p><h2>教学目标</h2><ol>'+''.join('<li><p>'+E(x)+'</p></li>' for x in L['objectives'])+'</ol><h2>一课时流程</h2>'+table(['时间','环节','课堂操作'],flow)+'<p>8组任务。五个课本词语题分配到相应段落；四种动物特点表按教参2.2口头概括，网页记录原句依据。正式书面输入集中在公益广告来源和3—4句回应。</p><h2>课文与漫画核对</h2><p>'+boundary+'</p><p>'+comic+'</p><h2>逐题参考</h2>'
for i,t in enumerate(L['tasks'],1):
 b+=f'<details><summary>{i}. {E(t["title"])} · {E(t["source"])}</summary>'+''.join('<p class="question">'+E(q)+'</p>' for q in t['questions'])+f'<p class="model">{E(t["answer"])}</p><p>{E(t["explain"])}</p><p><b>答案点：</b>{E("；".join(t["points"]))}</p><p><b>易错：</b>{E(t["reject"])}</p><p><b>提示：</b>{E("；".join(t["hints"]))}</p></details>'
b+='<h2>课本动物特点表</h2>'+table(['动物','概括主要特点'],[[n,L['tasks'][i]['answer'].replace('词语：敏捷、穿梭。','').replace('词语：馋。','').replace('词语：摔跤。','')] for i,n in [(3,'红毛猩猩'),(4,'非洲企鹅'),(5,'亚达伯拉象龟'),(6,'马来熊')]])
b+=f'<h2>公益广告分享</h2><p>保留“上网搜一搜，找一个关爱动物的公益广告，和同学分享”。<a href="{adurl}" target="_blank" rel="noopener">NParks官方公益海报入口</a>可作起点：下载海报第3页“Wildlife and Us”。学生也可自行选择真实广告。建议先由同桌各说一句，再独立写回应；课堂不实际捐款、不上传作品。</p><h2>记录与课堂使用</h2><p>教师发reading.html学生直达链接。每段读完可点“本段问题”；题目左边为对应原文，证据可多句累加、复制粘贴和修改。错后5秒可重试，首次答案保留。自动正确率只统计取证、词语和点选，不代表口头概括或开放题已由系统评分。</p><p>记录保存在同一设备、同一浏览器。可导出逐题CSV、完整JSON或文字记录；不会自动发给老师或上传Google Sheet。词语本沿用站内共享格式，按年级、单元、课文汇总。清理浏览器前先导出；离线文件与在线页不自动互通。</p><p>本站教师材料公开，教师链接不代表权限保护。无网时使用整包中的独立学生HTML与离线投影；外部公益海报请课前打开备用。</p>'
(D/'teacher.html').write_text(shell('助养野生动物 · 教师资料',b,'<script src="pack.js"></script>'))
shutil.copyfile(M/'pack.js',D/'pack.js')
old=(M/'slides.html').read_text();script=old[old.index('<script>'):old.rindex('</script>')+9];script=re.sub(r'const SLIDES=.*?;let ',lambda _: 'const SLIDES='+json.dumps(S,ensure_ascii=False)+';let ',script,count=1)
b='<p class="crumb"><a href="teacher.html">教师资料</a> / 在线投影</p><div class="toolbar"><select id="slideSelect" aria-label="选择课件页"></select></div><section class="projector" id="projector"><img id="slideImage" alt="课件"><div class="toolbar"><button id="prev">上一页</button><button id="next">下一页</button><button id="full">全屏</button><span class="slide-label" id="slideLabel"></span></div></section><details class="slide-notes"><summary>教师提示</summary><p id="notes"></p></details>'
(D/'slides.html').write_text(shell('助养野生动物 · 在线投影',b,script))
# One catalogue insertion; unrelated units are retained.
p=R/'index.html';s=p.read_text();m=re.search(r'const DATA=(.*?);\n',s);data=json.loads(m[1]);unit=next(u for u in data['2']['texts'] if u['title']=='单元二');url='du/textbook/2hcl/unit2/zhu-yang-ye-sheng-dong-wu/index.html'
if not any(x['url']==url for x in unit['items']):unit['items'].insert(0,dict(title='生活空间 · 助养野生动物',url=url,note='一课时 · 助养信息 · 动物特点 · 公益广告分享'))
p.write_text(s[:m.start(1)]+json.dumps(data,ensure_ascii=False,separators=(',',':'))+s[m.end(1):])
(Path(__file__).parent/'teaching_meta.json').write_text(json.dumps(dict(flow=flow,boundary=boundary,comic=comic,adurl=adurl),ensure_ascii=False,indent=2))
print('Built homepage, reading, teacher, comics and projector pages.')
