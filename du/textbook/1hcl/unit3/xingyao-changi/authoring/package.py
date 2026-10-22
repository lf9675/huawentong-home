from pathlib import Path
import json,re,hashlib,shutil,zipfile,os,runpy
R=Path(__file__).resolve().parents[1]; O=R/'repo/du/textbook/1hcl/unit3/xingyao-changi'; S=R/'repo/du/textbook/shared/lesson-v1'
runpy.run_path(str(R/'build/prepare_publish.py'))
D=O/'downloads'; offline=D/'offline'; offline.mkdir(exist_ok=True)
def adapt(s):
 s=s.replace('../../../shared/lesson-v1/','shared/').replace('../../../../../assets/','assets/').replace('../../../../../index.html#1/texts','index.html')
 s=s.replace('href="/du/ciyu/', 'href="https://huawentong-home.lyqlym2015.workers.dev/du/ciyu/')
 s=re.sub(r'<script[^>]*src="shared/cloud[^\"]*"[^>]*></script>','',s)
 return s
for f in ['reading.html','index.html','comics.html']:
 s=adapt((O/f).read_text());s=re.sub(r'<a[^>]+href="teacher.html"[^>]*>教师资料</a>','',s);(offline/f).write_text(s)
# Teacher copy works within full package and advertises the downloaded local files.
s=adapt((O/'teacher.html').read_text()).replace('<button id="downloadPpt">可编辑PPT</button>','<a class="btn" href="downloads/xingyao-changi.pptx" download>可编辑PPT</a>');s=re.sub(r'<button id="downloadPack">.*?</button>','',s);s=s.replace('<a class="btn" href="downloads/offline.zip" download>离线学习包</a>','');s=s.replace('<button id="downloadOffline">离线学习包</button>','');s=s.replace('<script src="pack.js"></script>','');(offline/'teacher.html').write_text(s)
(O/'projection.html').write_text((O/'projection.html').read_text().replace('<button data-lesson="1">第一课</button><button data-lesson="2">第二课</button>','').replace('<button id="prev">','<button data-lesson="1">第一课</button><button data-lesson="2">第二课</button><button id="prev">'))
(offline/'projection.html').write_text(adapt((O/'projection.html').read_text()))
A=O/'authoring';A.mkdir(exist_ok=True)
for name in ['build_content.py','build_web.py','create_slides.mjs','create_docx.py','dedupe_ppt.py','finalize_ppt.mjs','prepare_publish.py','pack.js','package.py']:
 shutil.copy(R/'build'/name,A/name)
(A/'MAINTENANCE.txt').write_text('维护说明\n课文、任务和段落配图矩形见 lesson.json；content.js 为同一数据的浏览器版本。词语释义见 lexicon.js。\n网页调用 shared/lesson-v1 既有引擎；保留本课状态与跨课词语本键名。\nPPT 文字与图形可在 PowerPoint 编辑。create_slides.mjs 使用 @oai/artifact-tool；路径需按实际项目调整。文档脚本使用 python-docx。\n配图由教师提供，保持原图；课件仅通过图片框裁切展示各格，不改动原文件。\n修改后同步在线投影、PPT、教师答案和下载清单。\n')
def entry(src,dst):
 p=(O/src).resolve();b=p.read_bytes();e=dict(url=src,path=dst,bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
 if src=='downloads/xingyao-changi.pptx':e['parts']=json.loads((D/'pptx-manifest.json').read_text())['parts']
 return e
base=[entry('downloads/offline/'+f,f) for f in ['reading.html','index.html','comics.html']]
base += [entry(f,f) for f in ['lesson.css','lesson-support.js','content.js','lexicon.js','README.txt']]
base += [entry('assets/comic'+str(i)+'.png','assets/comic'+str(i)+'.png') for i in range(1,6)]
base += [entry('../../../shared/lesson-v1/'+f,'shared/'+f) for f in ['app.js','wordbook.js','catalog.js','identity.js','style.css','wenkai.woff2','songti.woff2']]
base += [entry('../../../../../assets/huawentong-logo.png','assets/huawentong-logo.png')]
full=base+[entry('downloads/offline/'+f,f) for f in ['teacher.html','projection.html']]+[entry(f,f) for f in ['projection.js','lesson.json','downloads/xingyao-changi.pptx','downloads/teacher-guide.docx']]
full += [entry('../../unit2/xinnian-fengsu/downloads/fonts.zip','fonts.zip')]
full += [entry(str(p.relative_to(O)),str(p.relative_to(O))) for folder in ['slides','authoring'] for p in sorted((O/folder).iterdir()) if p.is_file()]
for name,entries in [('offline',base),('package',full)]:
 (D/(name+'-manifest.json')).write_text(json.dumps(dict(filename='魅力四射_星耀樟宜_'+('离线学习包' if name=='offline' else '完整教学配套')+'.zip',entries=entries),ensure_ascii=False,indent=2))
 with zipfile.ZipFile(R/'build'/(name+'-check.zip'),'w',zipfile.ZIP_STORED) as z:
  for e in entries:z.write((O/e['url']).resolve(),e['path'])
 with zipfile.ZipFile(R/'build'/(name+'-check.zip')) as z:assert z.testzip() is None
 print(name,len(entries),sum(e['bytes'] for e in entries))
 if name=='offline':
  target=R/'build/offline';shutil.rmtree(target,ignore_errors=True)
  with zipfile.ZipFile(R/'build'/(name+'-check.zip')) as z:z.extractall(target)
s=(O/'teacher.html').read_text().replace('<a class="btn" href="downloads/offline.zip" download>离线学习包</a>','<button id="downloadOffline">离线学习包</button>');(O/'teacher.html').write_text(s)
