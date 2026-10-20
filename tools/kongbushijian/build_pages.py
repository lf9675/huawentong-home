from pathlib import Path
import json,re,html,shutil
R=Path(__file__).resolve().parents[2];W=R.parent;O=R/'du/textbook/2hcl/unit4/kongbushijian';L=json.loads((O/'lesson.json').read_text());B=json.loads((O/'teaching-brief.json').read_text());T=L['tasks'];V=L['version'];E=html.escape;rel=O.relative_to(R).as_posix()+'/'
shutil.copyfile(R/'du/textbook/2hcl/unit3/shou-ji-bei-diu-qi-zhi-hou/lesson.css',O/'lesson.css')
with (O/'lesson.css').open('a')as f:f.write('\n.panel{background:#fff}.source-text{line-height:2}.nav{flex-wrap:wrap}.cards{grid-template-columns:repeat(auto-fit,minmax(230px,1fr))}.concept{font-size:19px}.reference-nav{display:block;margin:10px 0}.lesson-card p{line-height:1.8}details summary{cursor:pointer;padding:10px 0}.answer-table{font-size:20px}.slide-links{display:flex;gap:12px;flex-wrap:wrap}')
def page(title,body,scripts=''):
 return '<!doctype html><html lang="zh-SG"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+E(title)+' · 华文通</title><link rel="stylesheet" href="../../../shared/lesson-v1/style.css?v='+V+'"><link rel="stylesheet" href="lesson.css?v='+V+'"></head><body><header class="site-header"><a href="../../../../../index.html#2/texts"><img src="../../../../../assets/huawentong-logo.png" alt="华文通"></a><span>'+L['label']+'</span></header>'+body+scripts+'</body></html>'
nav='<nav class="nav"><a class="btn" href="index.html">主页</a><button data-view="read">读文</button><button data-view="lesson1">第一课</button><button data-view="lesson2">第二课</button><button data-view="lesson3">第三课</button><button data-view="review">检查</button><button id="wordList">词语本</button></nav>'
body=nav+'<main><p id="saveState" class="muted" role="status"></p><div id="readTask" class="workspace"><article id="source" class="paper"></article><section id="activity" class="paper"></section></div><section id="review" class="paper" hidden></section><dialog id="dialog"><button id="dialogClose" class="dialog-close">关闭</button><div id="dialogContent"></div></dialog><dialog id="wordDialog"><button id="wordDialogClose" class="dialog-close">关闭</button><div id="wordDialogContent"></div></dialog></main>'
scripts=''.join('<script src="'+f+'?v='+V+'"></script>'for f in ['content.js','lexicon.js','../../../shared/lesson-v1/catalog.js','../../../shared/lesson-v1/wordbook.js','../../../shared/lesson-v1/app.js'])
(O/'reading.html').write_text(page('恐怖事件 · 互动学习',body,scripts))
x,y,w,h=L['panelRects'][0];pic=f'<div class="panel" style="aspect-ratio:{w}/{h}"><img src="assets/comic1.png" alt="原漫画第一格：我最讨厌蒋妍了" style="width:{1024/w*100}%;left:{-x/w*100}%;top:{-y/h*100}%"></div>'
body='<main><p class="crumb"><a href="../../../../../index.html#2/texts">中二 · 课文学习</a> / 单元四 / 核心课文</p><section class="hero"><div><h1>恐怖事件</h1><p class="lead">一次误会，<br>怎样改变了两人的关系？</p><div class="actions"><a class="btn primary" href="reading.html">开始／继续学习</a><a class="btn" href="../../../../ciyu/context-lab/index.html#s2u4l2">词语预习</a></div></div>'+pic+'</section><div class="cards">'+''.join('<section class="card lesson-card"><h2>'+title+'</h2><p>'+content+'</p><a class="btn" href="reading.html#lesson'+str(i+1)+'">进入'+title+'</a></section>'for i,(title,content)in enumerate([('第一课','第1—10段：矛盾、气氛与恐惧；找原句，说清作用。'),('第二课','第11—19段：交流与转变；解释关键句，理解主题。'),('第三课','内容与关系统整；感叹句；必做开放回应。')]))+'</div><p class="teacher-link"><a href="comics.html">完整图文回读</a>　<a href="reading.html#words">个人词语本与闪卡</a>　<a href="teacher.html">教师资料</a></p></main>'
(O/'index.html').write_text(page('恐怖事件',body))
# Full reading repeats the same paragraph-to-panel mapping without rewriting any image.
cn=['一','二','三','四','五','六','七','八','九','十','十一','十二','十三','十四','十五','十六','十七','十八','十九']
body='<main><nav class="actions"><a class="btn" href="index.html">主页</a><a class="btn" href="reading.html">互动学习单</a></nav><h1>恐怖事件 · 图文回读</h1>'
for i,p in enumerate(L['paragraphs']):
 pics=''
 for n in L['panels'][i]:
  x,y,w,h=L['panelRects'][n-1];pics+=f'<div class="panel" style="aspect-ratio:{w}/{h}"><img loading="lazy" src="assets/comic{L["panelSheets"][n-1]}.png" alt="原漫画第{n}格" style="width:{1024/w*100}%;left:{-x/w*100}%;top:{-y/h*100}%"></div>'
 body+='<section class="workspace paper"><article><h2>第'+cn[i]+'段</h2><p class="source-text">'+E(p)+'</p></article><div><h2>第'+cn[i]+'段</h2><div class="panel-list">'+pics+'</div></div></section>'
body+='<details class="paper"><summary>查看五张完整原图</summary>'+''.join(f'<img class="comic-full" loading="lazy" src="assets/comic{i}.png" alt="原漫画第{i}页">'for i in range(1,6))+'</details></main>'
(O/'comics.html').write_text(page('恐怖事件 · 图文回读',body))
body='<main><nav class="actions"><a class="btn" href="index.html">课文主页</a><a class="btn" href="reading.html">学生学习单</a></nav><h1>教师资料</h1><section class="paper"><h2>2—3课时 · 从原文理解关系变化</h2><p>19个自然段，10组任务拆成19个随段小步骤。三课时方案循序展开；两课时方案减少重复汇报，将部分语言练习改为口头处理。</p><div class="actions"><a class="btn primary" href="slides.html">在线投影</a><a class="btn" href="downloads/horror-lesson.pptx" download>可编辑PPT</a><a class="btn" href="downloads/teacher-guide.docx" download>教师流程与答案</a><button data-pack="offline">独立离线学习单</button><button data-pack="package">整套下载</button></div><p id="packStatus" role="status"></p><p><a href="downloads/使用说明.txt">使用说明</a>　<a href="comics.html">完整图文回读</a></p></section><section class="paper"><h2>教学目标</h2>'+''.join('<p>'+E(g)+'</p>'for g in B['goals'])+'<h2>三课时安排</h2>'+''.join('<h3>'+r[0]+' '+r[1]+'</h3><p>'+E(r[2])+'</p>'for r in B['schedule'])+'<h3>两课时安排</h3><p>'+E(B['twoLesson'])+'</p><p>课时按每课50分钟规划，可依实际课长调整。</p></section><section class="paper"><h2>教材核对与旧练习整合</h2>'+''.join('<p>'+E(s)+'</p>'for s in B['sourceBoundary'])+'</section>'
for t in T:
 body+='<details class="paper"><summary>'+E(t['title'])+'</summary>'+''.join('<p class="question">'+E(q)+'</p>'for q in t['questions'])+'<p>来源：'+E(t['source'])+'<br>课堂身份：'+E(t['role'])+'</p><h3>参考答案</h3><p class="model">'+E(t['answer'])+'</p><h3>证据与加工</h3><p>'+E(t['explain'])+'</p><details><summary>原文依据</summary>'+''.join('<p class="source-text">'+E(p)+'</p>'for p in t['evidenceText'])+'</details><p>答案点：'+E('；'.join(t['points']))+'</p><p>提示：'+E(' → '.join(t['hints']))+'</p><p>常见失分：'+E(t['reject'])+'</p><p>'+E(t['scoreGuide'])+'</p>'+''.join('<p>'+E(a)+'</p>'for a in t.get('alternatives',[]))+''.join('<details><summary>'+E(q)+'</summary><p>'+E(a)+'</p></details>'for q,a in t.get('oral',[]))+'</details>'
body+='<section class="paper"><h2>记录与使用</h2><p>作答、首次答案、尝试、订正与姓名班级学号保存在当前设备、当前浏览器。检查页可导出完整JSON、逐题CSV及文字记录。主观题由教师核对，不自动判分；没有教师自动收件或账号云同步。</p><p>词语本汇总已接入的同域课文收藏，按年级、单元、课文分类，支持自输词、编辑、闪卡和导入导出。重置本课不删除词语本。</p><p>教师资料是公开页面。设备朗读不是人工录音。</p></section></main>'
(O/'teacher.html').write_text(page('恐怖事件 · 教师资料',body,'<script src="pack.js"></script>'))
shutil.copyfile(R/'du/textbook/2hcl/unit3/shui-dou-qu-na-le/pack.js',O/'pack.js')
# Preserve unrelated platform items. Both former entries pointed to exactly this route.
p=R/'index.html';s=p.read_text();m=re.search(r'const DATA=(.*?);\s*',s);data=json.loads(m.group(1));u=next(u for u in data['2']['texts']if u['title']=='单元四')
u['items']=[x for x in u['items']if 'kongbushijian' not in x['url']];u['items'].insert(0,dict(title='核心课文 · 恐怖事件',url=rel+'index.html',note='2—3课时 · 逐段图文 · 关系变化 · 关键句与主题 · 教师资料'))
for block in data['2']['texts']:
 if block is not u:block['items']=[x for x in block['items']if 'kongbushijian'not in x['url']]
data['2']['texts']=[x for x in data['2']['texts']if x['items']or x['title']!='课前预习']
s=s[:m.start(1)]+json.dumps(data,ensure_ascii=False,separators=(',',':'))+s[m.end(1):];p.write_text(s)
print('Web pages ready')
