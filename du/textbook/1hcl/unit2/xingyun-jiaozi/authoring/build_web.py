from pathlib import Path
import json, html, shutil
R=Path(__file__).resolve().parents[1];O=R/'repo/du/textbook/1hcl/unit2/xingyun-jiaozi';B=R/'repo/du/textbook/1hcl/unit2/xinnian-fengsu';L=json.loads((O/'lesson.json').read_text());E=html.escape
V='20261022-jiaozi-1'
head=lambda title:f'<!doctype html><html lang="zh-SG"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="referrer" content="no-referrer"><title>{title} · 华文通</title><link rel="stylesheet" href="../../../shared/lesson-v1/style.css?v={V}"><link rel="stylesheet" href="lesson.css?v={V}"></head><body><header class="site-header"><a href="../../../../../index.html#1/texts"><img src="../../../../../assets/huawentong-logo.png" alt="华文通"></a><span>{L["label"]}</span></header>'
nav='<nav class="nav"><a class="btn" href="index.html">课文主页</a><a class="btn" href="reading.html">互动学习</a><a class="btn" href="comics.html">漫画回读</a><a class="btn" href="teacher.html">教师资料</a></nav>'
(O/'lesson.css').write_text((B/'lesson.css').read_text()+'''\n.thread-table{font-family:LessonKai,serif;font-size:20px}.thread-table th{width:58px}.thread-table td{line-height:1.8}.thread-word{color:#b21f32;font-weight:bold}.read-intro{margin-top:20px}.image-index{display:grid;grid-template-columns:repeat(4,1fr);gap:8px}.image-index img{width:100%}.hero .panel{max-width:540px}.mode-notes{max-width:900px;line-height:1.8}.resource-grid{grid-template-columns:repeat(2,1fr)}@media(max-width:760px){.resource-grid{grid-template-columns:1fr}.thread-table{font-size:18px}}\n''')
reader=(B/'reading.html').read_text().replace('世界各地的新年风俗','幸运饺子').replace('生活空间','巩固课文').replace('20261022-xinnian-1',V).replace('<button data-view="lesson1">本课问题</button>','<button data-view="lesson1">第一课</button><button data-view="lesson2">第二课</button>').replace('<script src="../../../shared/lesson-v1/summary-table.js?v='+V+'"></script>','').replace('</body>','<script src="lesson-support.js?v='+V+'"></script></body>')
(O/'reading.html').write_text(reader)
(O/'lesson-support.js').write_text('''(()=>{'use strict';
const L=window.LESSON,activity=document.querySelector('#activity'),source=document.querySelector('#source');
function enhance(){
 const select=document.querySelector('[data-field="thread"]');
 if(select&&!document.querySelector('#threadTable')){
  const section=document.createElement('section');section.id='threadTable';
  const h=document.createElement('h3');h.textContent='课本七行内容';section.append(h);
  const table=document.createElement('table');table.className='thread-table';
  for(const [p,text] of L.threadRows){const tr=document.createElement('tr'),th=document.createElement('th'),td=document.createElement('td');th.textContent='第'+p+'段';td.textContent=text;tr.append(th,td);table.append(tr)}section.append(table);
  const map=document.createElement('p');map.className='kai';map.id='threadMap';section.append(map);
  const label=select.previousElementSibling,choice=activity.querySelector('fieldset');
  if(choice)choice.before(section,label,select);else label.before(section);
  const sync=()=>{map.textContent='情节概括：包〔'+(select.value||'　　')+'〕 → 传〔'+(select.value||'　　')+'〕 → 吃到〔'+(select.value||'　　')+'〕。';};select.addEventListener('change',sync);sync();
 }
 if(document.querySelector('#p1')&&window.LessonEngine.state().position.view==='read'&&!document.querySelector('#firstOral')){
  const d=document.createElement('details');d.id='firstOral';d.className='read-intro';const s=document.createElement('summary');s.textContent='口头想一想';const p=document.createElement('p');p.textContent='中国北方人为什么喜欢在大年三十吃饺子？先说你的想法。';d.append(s,p);source.append(d);
 }
}
new MutationObserver(enhance).observe(activity,{childList:true});enhance();
})();''')
panel='<div class="panel" style="aspect-ratio:504/328"><img src="assets/comic1.png" alt="原有漫画第一格，一家人围坐包饺子" style="width:203.175%;left:-1.389%;top:-29.268%"></div>'
(O/'index.html').write_text(head('幸运饺子')+nav+f'''<main><section class="hero"><div><p class="eyebrow">中一高级华文 · 单元二 · 巩固</p><h1>幸运饺子</h1><p class="lead">一只饺子，为什么在家人之间传来传去？</p><div class="actions"><a class="btn primary" href="reading.html">开始／继续学习</a><a class="btn" href="teacher.html">教师资料</a></div></div>{panel}</section><section class="resource-grid"><a class="paper" href="reading.html#paragraph-1"><h2>第一课</h2><p>第1—5段：人物的动作和用意</p></a><a class="paper" href="reading.html#paragraph-6"><h2>第二课</h2><p>第6—8段：理解词句，归纳线索与主题</p></a><a class="paper" href="comics.html"><h2>漫画与全文回读</h2><p>四页原漫画 · 八段课文</p></a><a class="paper" href="reading.html#words"><h2>我的词语本</h2><p>收藏词语，翻卡复习</p></a></section><p>1—2课时。课堂节奏由老师安排。</p></main></body></html>''')
comics=head('幸运饺子 · 漫画回读')+nav+'<main><h1>漫画与全文回读</h1><p>四页原漫画按原顺序保留。点段号可回到逐段学习。</p>'
for n in range(1,5):comics+=f'<figure class="whole-comic"><img src="assets/comic{n}.png" alt="幸运饺子原漫画第{n}页" loading="lazy"><figcaption>原漫画第{n}页</figcaption></figure>'
for n,p in enumerate(L['paragraphs'],1):comics+=f'<section class="paper reread"><h2><a href="reading.html#paragraph-{n}">第{n}段</a></h2><p class="source-text">{E(p)}</p></section>'
(O/'comics.html').write_text(comics+'</main></body></html>')
flow=[('第一课','导入与自读','10','口头讨论第1段；自主读第1—5段，按需查词。'),('第一课','第2—3段','8','教师示范阻止做记号的推断；学生解释送给奶奶的心意。'),('第一课','第4段','8','共同比较眨眼与微笑，说明默契。'),('第一课','第5段','11','独立找两处行为，书面说明姑姑细心。'),('第一课','核对','3','订正并收藏不明白的词。'),('第二课','第6—8段自读','6','先读后练；不提前展示综合答案。'),('第二课','第6—7段','8','辨析成语语境、引号和家庭关系。'),('第二课','线索与主题','6','看课本七行，填线索，再判断中心。'),('第二课','必做开放回应','9','写理解、理由、课文依据、真实经历与回扣。'),('第二课','仿句','4','独立写一句，比较前后轻重关系。'),('第二课','资料比较','5','两人用提供的来源查同一方面，口头分享。'),('第二课','当堂检查','2','订正、整理词语、导出记录。')]
L['flow']=flow
teacher=head('幸运饺子 · 教师资料')+nav+'''<main class="teacher-page"><h1>教师资料</h1><p class="lead">幸运饺子 · 中一高级华文 · 单元二</p><div class="actions"><a class="btn primary" href="projection.html">在线投影</a><a class="btn" href="downloads/xingyun-jiaozi.pptx" download>可编辑PPT</a><a class="btn" href="downloads/teacher-guide.docx" download>教师流程与答案</a><button id="downloadPack">整套下载</button><a class="btn" href="downloads/offline.zip" download>离线学习包</a></div><p id="packStatus" role="status"></p><section class="paper"><h2>教学重点</h2><ol><li>依据人物动作与语言，说明转送饺子的用意。</li><li>解释“眨眨眼”“偷龙转凤”和引号在语境中的意思。</li><li>分清事物线索与主题，以课文和个人经历解释团聚的价值。</li></ol><p>建议分两课，每课40分钟。第一课只设一道书面题；第二课设开放回应与一句仿写。资料比较采用口头分享。</p><h2>一课时使用</h2><p>若学生已完成图文预读，可用50分钟：导入3分钟，逐段原题15分钟，人物证据7分钟，线索主题5分钟，开放题9分钟，仿句4分钟，资料比较5分钟，检查2分钟。保留全部课本题，减少重复展示与全班汇报，不另加课后任务。未预读且阅读困难的班级采用两课时。</p><h2>两课时流程</h2><table><tr><th>课次</th><th>环节</th><th>分钟</th><th>安排</th></tr>'''
teacher+=''.join('<tr>'+''.join('<td>'+E(c)+'</td>' for c in row)+'</tr>' for row in flow)+'</table></section>'
teacher+='''<section class="paper"><h2>导入与资料边界</h2><p>第1段教参问：中国北方人为什么喜欢在大年三十吃饺子？可从传统、团聚与美好祝愿理解。课文本身只明确“传统”和“喜悦”；象征团圆和好运的补充来自中国文化网，不能伪装成课文原句。</p><p>保留四页32格原漫画。对应：第1段1—2格，第2段3—8格，第3段9—14格，第4段15—18格，第5段19—21格，第6段22—25格，第7段26—31格，第8段32格。人物性别等画面细节不作为课文推断依据。第6段前不展示第7段结局作为答题提示。</p><p>课本巩固练习三题全部保留。人物题、换词题、成语题和家庭关系题来自旁注／教参；选择项是教学支架，不冒充课本选择题。课本第一题仿句排在读完第8段后；第二题线索主题在全文阅读后；第三题资料比较最后进行。</p></section>'''
for i,t in enumerate(L['tasks'],1):
 teacher+=f'<section class="paper answer-section"><h2>{i} · {E(t["title"])}</h2><p class="muted">{E(t["role"])}；{E(t["source"])}</p>'+''.join('<p class="question">'+E(q)+'</p>' for q in t['questions'])
 teacher+='<h3>文本证据与信息加工</h3><p>'+E('第'+str(t['focus'][0])+'段。'+('需回看第2段，并整合两处行为。' if t['id']=='careful' else '读完全篇后综合。' if t.get('scope')=='full' else '先定位人物动作或语言，再按题目加工。'))+'</p>'
 teacher+='<h3>参考答案</h3><p class="model">'+E(t['answer'])+'</p><h3>解释与接受范围</h3><p>'+E(t['explain'])+'</p><h3>常见失分</h3><p>'+E(t['reject'])+'</p><h3>参考评价</h3><p>'+E(t['scoreGuide'])+'</p><details><summary>分层提示与追问</summary><ol>'+''.join('<li>'+E(h)+'</li>' for h in t['hints'])+'</ol>'
 for q,a in t.get('oral',[]):teacher+='<p><b>'+E(q)+'</b><br>'+E(a)+'</p>'
 teacher+='</details></section>'
teacher+='''<section class="paper"><h2>学习记录与课堂收件</h2><p>普通入口保存同设备、同浏览器的首次答案、尝试与订正，可填写姓名、班级、学号，导出JSON、CSV或文字记录。清除浏览器资料前先导出。本课重置不删除个人词语本。</p><p>使用现有<a href="/bei/management/textbook/">课文课堂看板</a>创建任务并发放学生专属链接后，可沿用平台收件功能；普通链接与离线包不会自动发送给教师。开放题仍需教师覆核。</p><p>客观任务6组，共8个选择判断和1个线索点选；另有1处原文证据校验。首次全部答对率按已提交客观任务的组数计算，不等于逐项得分，也不代表独立掌握。姑姑细心、开放回应和仿句为3道书面题；资料比较为口头任务。</p><p>个人词语本按年级、单元、课文汇总已收藏的词，39条预设语境释义不自动全部加入。未知词仍可建卡并补释义。离线页面与在线页面的本地记录分开。</p><p>教师页与下载材料公开包含答案。在线投影与PPT页序一致，课件文字可编辑；如本机缺少字体，可安装整套包里的字体，或直接使用在线投影。</p><h2>比较题资料来源</h2>'''
teacher+=''.join(f'<p><a href="{E(s["url"])}" target="_blank" rel="noopener">{E(s["label"])}</a></p>' for s in L['sources'])+'<p>资料于2026年10月22日核对。仅比较常见习俗，不概括每个家庭的做法。</p></section></main><script src="pack.js"></script></body></html>'
(O/'teacher.html').write_text(teacher)
proj=(B/'projection.html').read_text().replace('世界各地的新年风俗','幸运饺子').replace('20261022-xinnian-1',V).replace('生活空间','巩固课文')
proj=proj.replace('<button data-lesson="1">本课</button>','<button data-lesson="1">第一课</button><button data-lesson="2">第二课</button>')
(O/'projection.html').write_text(proj);shutil.copy(B/'projection.js',O/'projection.js')
(O/'pack.js').write_text('''document.querySelector('#downloadPack').onclick=async()=>{const b=document.querySelector('#downloadPack'),s=document.querySelector('#packStatus');b.disabled=true;try{const m=await(await fetch('downloads/package-manifest.json')).json(),parts=[];for(let i=0;i<m.parts.length;i++){s.textContent='正在准备下载 '+(i+1)+' / '+m.parts.length;const r=await fetch(m.parts[i].path);if(!r.ok)throw Error('下载失败');const a=await r.arrayBuffer();if(a.byteLength!==m.parts[i].bytes)throw Error('文件不完整');parts.push(a)}const blob=new Blob(parts,{type:'application/zip'});if(blob.size!==m.bytes)throw Error('大小不一致');const bytes=await blob.arrayBuffer(),hash=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes))).map(n=>n.toString(16).padStart(2,'0')).join('');if(hash!==m.sha256)throw Error('校验失败');const u=URL.createObjectURL(blob),a=document.createElement('a');a.href=u;a.download='幸运饺子_完整教学配套.zip';a.click();setTimeout(()=>URL.revokeObjectURL(u),60000);s.textContent='下载已开始。'}catch(e){s.textContent='下载未完成，请刷新重试或先分别下载课件和教师文件。'}finally{b.disabled=false}};''')
(O/'lesson.json').write_text(json.dumps(L,ensure_ascii=False,indent=2))
(O/'README.txt').write_text('幸运饺子｜中一高级华文｜单元二｜巩固\n先打开index.html或reading.html。教师资料见teacher.html；可编辑课件和教师答案在downloads。\n1—2课时；原漫画四页保留。作答与词语本保存在当前浏览器，及时导出。离线不自动收件。\n在线投影需打开本地HTTP服务，或使用正式站点。直接打开文件可用reading.html和PPT。\n')
print('web built')
