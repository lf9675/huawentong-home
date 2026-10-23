from pathlib import Path
import json,html,shutil,re
R=Path(__file__).resolve().parents[1];O=R/'repo/du/textbook/1hcl/unit3/xingyao-changi';B=R/'repo/du/textbook/1hcl/unit2/xingyun-jiaozi';L=json.loads((O/'lesson.json').read_text());E=html.escape;V='20261022-changi-1'
head=lambda title:f'<!doctype html><html lang="zh-SG"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="referrer" content="no-referrer"><title>{title} · 华文通</title><link rel="stylesheet" href="../../../shared/lesson-v1/style.css?v={V}"><link rel="stylesheet" href="lesson.css?v={V}"></head><body><header class="site-header"><a href="../../../../../index.html#1/texts"><img src="../../../../../assets/huawentong-logo.png" alt="华文通"></a><span>{L["label"]}</span></header>'
nav='<nav class="nav"><a class="btn" href="index.html">课文主页</a><a class="btn" href="reading.html">互动学习</a><a class="btn" href="comics.html">漫画回读</a><a class="btn" href="teacher.html">教师资料</a></nav>'
css=(B/'lesson.css').read_text().split('.thread-table')[0]+'''\n.resource-grid{grid-template-columns:repeat(3,1fr)}.hero .panel{max-width:560px}.hero h1{font-size:48px}.answer-table,.answer-table tbody,.answer-table tr,.answer-table td,.answer-table th{display:block;width:100%;box-sizing:border-box}.answer-table thead{display:none}.answer-table tbody th{background:#edf5fa}.answer-table td:before{content:attr(data-label);display:block;font-family:LessonSong,serif;font-size:17px;margin-bottom:7px;color:#526e82}.answer-table select{height:auto;min-height:48px;white-space:normal}.own-summary{font-size:18px;table-layout:auto}.own-summary td,.own-summary th{min-width:100px}.summary-scroll{overflow-x:auto}.summary-scroll table{min-width:720px}.word-family-example{font-family:LessonKai,serif;font-size:22px;line-height:1.8}.wide-note{max-width:920px;line-height:1.8}.teacher-page h3{margin-bottom:4px}.teacher-page .paper>p{line-height:1.8}.hero .panel img{max-width:none}@media(max-width:800px){.resource-grid{grid-template-columns:1fr}.hero h1{font-size:36px}}\n'''
(O/'lesson.css').write_text(css)
s=(B/'reading.html').read_text().replace('幸运饺子',L['title']).replace('单元二 · 巩固课文','单元三 · 核心课文').replace('20261022-jiaozi-1',V).replace('<button data-view="lesson2">第二课</button>','<button data-view="lesson2">第二课</button><button data-view="lesson3">第三课</button>')
(O/'reading.html').write_text(s)
(O/'lesson-support.js').write_text('''(()=>{'use strict';
 const L=window.LESSON,host=document.querySelector('#source');
 function draw(){const id=location.hash.replace('#task-','');
 if(['ending','recommend'].includes(id)&&!document.querySelector('#ownSummary')){
 const wrap=document.createElement('section');wrap.id='ownSummary';const h=document.createElement('h3');h.textContent='我的五方面统整表';wrap.append(h);const note=document.createElement('p');note.className='guide';note.textContent='这是你前面填的答案。点说明对象，可以回去订正。';wrap.append(note);
 const scroll=document.createElement('div');scroll.className='summary-scroll';const table=document.createElement('table');table.className='own-summary';const thead=document.createElement('thead'),tr=document.createElement('tr');['说明对象',...L.summaryColumns.map(c=>c.label)].forEach(v=>{const th=document.createElement('th');th.textContent=v;tr.append(th)});thead.append(tr);table.append(thead);const body=document.createElement('tbody');const state=window.LessonEngine.state();for(const row of L.summaryItems){const tr=document.createElement('tr'),th=document.createElement('th'),a=document.createElement('a');a.href='#task-'+row.id;a.textContent=row.name;th.append(a);tr.append(th);for(const c of L.summaryColumns){const td=document.createElement('td');td.textContent=state.answers[row.id]?.fields?.[c.key]||'未填写';tr.append(td)}body.append(tr)}table.append(body);scroll.append(table);wrap.append(scroll);host.append(wrap);
 }
 if(id==='word-families'&&!document.querySelector('#wordExamples')){const existing=host.querySelector('.source-paragraph');if(existing)existing.hidden=true;const e=document.createElement('section');e.id='wordExamples';const h=document.createElement('h3');h.textContent='课本例子';e.append(h);for(const [w,words] of [['木','树木、灌木、草木、木材、木柴'],['桥','天悬桥、波浪桥、木桥、铁桥、吊桥'],['顶','屋顶、房顶、山顶、楼顶、头顶'],['习','学习、练习、补习、预习、复习']]){const p=document.createElement('p');p.className='word-family-example';p.textContent=w+'：'+words;e.append(p)}host.append(e);}
 }
 new MutationObserver(draw).observe(host,{childList:true});draw();
})();''')
panel='<div class="panel" style="aspect-ratio:511/365"><img src="assets/comic1.png" alt="教师提供的星耀樟宜漫画第一格" style="width:200.39%;left:-1.174%;top:-21.37%"></div>'
vocab='/du/ciyu/context-lab/s1/index.html?unit=3#s1u3l2'
(O/'index.html').write_text(head(L['title'])+nav+f'''<main><section class="hero"><div><p class="eyebrow">中一高级华文 · 单元三 · 核心</p><h1>魅力四射<br>星耀樟宜</h1><p class="lead">数字和例子，怎样让特点更清楚？</p><div class="actions"><a class="btn primary" href="reading.html">开始／继续学习</a><a class="btn" href="teacher.html">教师资料</a></div></div>{panel}</section><section class="resource-grid"><a class="paper" href="reading.html#paragraph-1"><h2>第一课</h2><p>第1—3段<br>小标题、外形与雨漩涡</p></a><a class="paper" href="reading.html#paragraph-4"><h2>第二课</h2><p>第4—7段<br>用数字与例子读懂特点</p></a><a class="paper" href="reading.html#lesson3"><h2>第三课</h2><p>词语串串串<br>推荐三个地方，说明理由</p></a><a class="paper" href="comics.html"><h2>漫画与全文回读</h2><p>五页原漫画 · 七段课文</p></a><a class="paper" href="reading.html#words"><h2>我的词语本</h2><p>收藏不懂的词，翻卡复习</p></a><a class="paper" href="{vocab}"><h2>已有词语学习单</h2><p>本课词义与语境练习</p></a></section><p>2—3课时。教师可按班级节奏安排。</p></main></body></html>''')
comic=head(L['title']+' · 漫画回读')+nav+'<main><h1>漫画与全文回读</h1><p>五页原漫画完整保留。数字与事实按课文介绍理解。</p>'
for i in range(1,6):comic+=f'<figure class="whole-comic"><img src="assets/comic{i}.png" alt="星耀樟宜原漫画第{i}页" loading="lazy"><figcaption>原漫画第{i}页</figcaption></figure>'
for i,p in enumerate(L['paragraphs'],1):comic+=f'<section class="paper reread"><h2><a href="reading.html#paragraph-{i}">第{i}段 · {E(L["paragraphLabels"][i-1])}</a></h2><p class="source-text">{E(p)}</p></section>'
(O/'comics.html').write_text(comic+'</main></body></html>')
teacher=head(L['title']+' · 教师资料')+nav+'''<main class="teacher-page"><h1>教师资料</h1><p class="lead">魅力四射 星耀樟宜 · 中一高级华文 · 单元三</p><div class="actions"><a class="btn primary" href="projection.html">在线投影</a><a class="btn" href="downloads/xingyao-changi.pptx" download>可编辑PPT</a><a class="btn" href="downloads/teacher-guide.docx" download>教师流程与答案</a><button id="downloadPack">整套下载</button><button id="downloadOffline">离线学习包</button></div><p id="packStatus" role="status"></p><section class="paper"><h2>教学目标</h2><ol>'''+''.join('<li>'+E(x)+'</li>' for x in L['objectives'])+'</ol><h2>三课时流程</h2><p>建议三课各40分钟，共120分钟。课堂时间用于安排节奏，不设置倒计时。</p><table><tr><th>课次</th><th>环节</th><th>分钟</th><th>安排</th></tr>'
teacher+=''.join('<tr>'+''.join('<td>'+E(c)+'</td>' for c in row)+'</tr>' for row in L['flow'])+'</table><h2>两课时安排</h2><p>'+E(L['twoLessonFlow'])+'</p></section>'
teacher+='<section class="paper"><h2>教材与图文对应</h2><table><tr><th>段号</th><th>内容</th><th>原漫画格号</th></tr>'
for i,p in enumerate(L['paragraphs']):teacher+=f'<tr><td>{i+1}</td><td>{E(L["paragraphIdeas"][i])}</td><td>{L["panels"][i][0]}—{L["panels"][i][-1]}</td></tr>'
teacher+='</table>'+''.join('<p>'+E(x)+'</p>' for x in L['boundaries'])+'</section>'
for i,t in enumerate(L['tasks'],1):
 teacher+=f'<section class="paper answer-section"><h2>{E(t["title"])}</h2><p>{E(t["role"])} · {E(t["source"])}</p>'+''.join('<p class="question">'+E(q)+'</p>' for q in t['questions'])
 teacher+='<h3>目标与定位</h3><p>'+E(t['target'])+' 第'+E('、'.join(map(str,t['focus'])))+'段。'+('读完全篇后回看前文。' if t.get('scope')=='full' else '')+'</p>'
 teacher+='<h3>参考答案</h3><p class="model">'+E(t['answer'])+'</p><h3>证据与解释</h3><p>'+E(t['explain'])+'</p><h3>接受范围与常见失分</h3><p>'+E(t['reject'])+'</p><h3>参考评价</h3><p>'+E(t['scoreGuide'])+'</p><details><summary>分层提示与选项解析</summary><ol>'+''.join('<li>'+E(h)+'</li>' for h in t['hints'])+'</ol>'
 for c in t['checks']:
  teacher+='<h4>'+E(c['question'])+'</h4>'+''.join('<p>'+chr(65+j)+'. '+E(c['options'][j])+'：'+E(x)+'</p>' for j,x in enumerate(c['why']))
 for q,a in t.get('oral',[]):teacher+='<p><b>'+E(q)+'</b><br>'+E(a)+'</p>'
 teacher+='</details></section>'
teacher+='''<section class="paper"><h2>完整统整表参考</h2><table><tr><th>说明对象</th><th>特点</th><th>说明依据</th><th>方法</th></tr>'''
for t in L['tasks']:
 if 'answerTable' in t:teacher+='<tr><td>'+E(t['answerTable']['name'])+'</td>'+''.join('<td>'+E(f['correct'])+'</td>' for f in t['answerTable']['fields'])+'</tr>'
teacher+='''</table><p>第4段还须补充灌木超过10万株、两棵橄榄树超过100岁；第5段还须补充蹦跳网长250米和腾空而起的感觉。表格是概括，不替代完整原文。</p></section><section class="paper"><h2>课堂记录与使用</h2><p>本课共有10组任务：7组客观任务、3组需教师核对的任务（作用短答、词语串串串、推荐）。客观部分含8个四选一判断、15个表格点选，以及1个多句证据框。首次全部答对率以客观任务组为单位，不是逐小题总分，也不代表独立掌握。</p><p>教师先示范，学生再完成。第一次错误只给提示，5秒后允许重试；再次错误后可看讲解。首次答案、尝试与订正分别保留。主观题不按字数或关键词自动评分。</p><p>姓名、班级、学号可在页面上方填写；检查页可下载完整备份、逐题CSV和文字记录。普通入口保存在同设备、同浏览器，清除资料前请先导出。重置本课不删除个人词语本。</p><p>使用现有<a href="/bei/management/textbook/">课文课堂看板</a>选择本课并创建班级任务，发放学生专属链接后，可使用平台收件。普通链接与离线包不会自动发送给教师；开放题仍需教师覆核。</p><p>44条预设词语释义按原文语境准备，学生收藏的词跨课文汇总。学生也能自输词语；未收录词标“释义待补充”，可自行编辑。</p><p>教师页与下载包公开包含答案。PPT文字可编辑；本机如缺字体，可使用包内字体或在线投影。图像中的漫画文字保持教师提供的原样。</p></section></main><script src="pack.js"></script></body></html>'''
(O/'teacher.html').write_text(teacher)
s=(B/'projection.html').read_text().replace('单元二 · 巩固课文','单元三 · 核心课文').replace('20261022-jiaozi-1',V).replace('<button data-lesson="2">第二课</button>','<button data-lesson="2">第二课</button><button data-lesson="3">第三课</button>')
(O/'projection.html').write_text(s)
for f in ['projection.js','pack.js']:shutil.copy(B/f,O/f)
(O/'README.txt').write_text('魅力四射 星耀樟宜｜中一高级华文｜单元三｜核心课文\n学生：打开 reading.html；教师：打开 teacher.html。\n建议三课各40分钟；两课各50分钟的安排见教师资料。\n五页40格原漫画保留，七段逐段阅读。课文日期、数字与“目前”等依教材理解。\n可编辑PPT、教师DOCX在downloads。离线学生页可直接打开；在线投影需本地HTTP服务或使用正式网址。\n普通入口及离线作答保存在当前浏览器，请及时导出。离线不自动收件。\n')
print('web built')

(O/'lesson.css').write_text((O/'lesson.css').read_text()+'\n.workspace>.paper{min-width:0}.summary-scroll{width:100%;max-width:100%}\n')
