from pathlib import Path
import os
import json,re,base64,hashlib,zipfile
W=Path(os.environ.get('XQ_BUILD_DIR','/tmp/huawentong-xinqing-build'));W.mkdir(parents=True,exist_ok=True);R=Path(__file__).resolve().parents[2];O=R/'du/textbook/2hcl/unit4/xin-qing-shou-zhang';S=R/'du/textbook/shared/lesson-v1';base='https://huawentong-home.lyqlym2015.workers.dev/';rel=O.relative_to(R).as_posix()+'/'
slides=json.loads((O/'slides.json').read_text());p=(R/'du/textbook/2hcl/unit3/shui-dou-qu-na-le/slides.html').read_text();p=p.replace('水都去哪儿了','心情手账').replace('water-lesson.pptx','mood-journal-lesson.pptx').replace('单元三 · 一课时','单元四 · 一课时');p=re.sub(r'const slides=.*?;\nconst \$',lambda m:'const slides='+json.dumps(slides,ensure_ascii=False).replace('</','<\\/')+';\nconst $',p,flags=re.S);p=p.replace('<a href="downloads/mood-journal-lesson.pptx" download>下载可编辑PPT</a>','<button data-pack="ppt">下载可编辑PPT</button>');p=p.replace('</body>','<p id="packStatus" role="status"></p><script src="pack.js"></script></body>');(O/'slides.html').write_text(p)
(O/'downloads/使用说明.txt').write_text('心情手账｜中二高级华文 单元四 生活空间\n1课时，按50分钟安排；位于单元四最前面。\n\n学生：reading.html；四则手账共24格原漫画，9个顺序任务，个人词语本与闪卡。\n教师：teacher.html；教学流程、答案、人工评分建议、教材与漫画核对。\n在线投影：slides.html；29页，与PPT同版，题目与答案分开。\n可编辑PPT：downloads/mood-journal-lesson.pptx；文字与四张表格可编辑。\n教师DOCX：downloads/teacher-guide.docx；共9页。\n漫画：用户提供四张原图，原文件未改动。答题以课文原句为准。\n\n题目：保留全部课本题；表格按日期逐行点选。教参人物分析自主作答，课本开放题必做并说明理由。答案是根据原文拟定的教学参考，附件未提供官方答案。\n\n保存：同设备、同浏览器本地保存，未接入账号同步及教师自动收件。可导出首次作答、尝试、订正与逐题记录。个人词语本按年级、单元、课文分类，保留各出处，支持编辑、导入导出与闪卡。未知词建卡标释义待补充；重置本课不删词语本。\n\n离线：独立HTML下载后打开即可；ZIP先全部解压，再打开“开始使用.html”。平台词语预习需要网络，朗读依赖设备语音。PPT使用霞鹜文楷与思源宋体，未安装可能替换；在线投影为同版图片。\n\n检验：内容、原图字节、资源链接、离线资源、PPT/DOCX渲染和DOM交互校验。未做实体iPad或原生PowerPoint实机测试。\n')
def data(p,mime):return 'data:'+mime+';base64,'+base64.b64encode(p.read_bytes()).decode()
s=(O/'reading.html').read_text()
def style(m):
 p=(O/m.group(1).split('?')[0]).resolve();css=p.read_text()
 for font in ['wenkai','songti']:css=css.replace('url('+font+'.woff2)','url('+data(S/(font+'.woff2'),'font/woff2')+')')
 return '<style>'+css+'</style>'
s=re.sub(r'<link rel="stylesheet" href="([^"]+)">',style,s)
s=s.replace('../../../../../assets/huawentong-logo.png',data(R/'assets/huawentong-logo.png','image/png')).replace('href="../../../../../index.html','href="'+base+'index.html').replace('href="index.html"','href="'+base+rel+'index.html"')
def script(m):return '<script>'+(O/m.group(1).split('?')[0]).resolve().read_text().replace('</script','<\\/script')+'</script>'
s=re.sub(r'<script src="([^"]+)"></script>',script,s)
images={f'comic{i}':data(O/f'assets/comic{i}.png','image/png')for i in range(1,5)}

s=s.replace('<script>window.LESSON','<script>window.LESSON_ASSETS='+json.dumps(images)+';</script><script>window.LESSON',1)
OFF=W/'mood-journal-offline.html';OFF.write_text(s)
def publish(src,prefix,name,mime):
 raw=src.read_bytes()
 for p in (O/'downloads').glob(prefix+'.*'):p.unlink()
 chunks=[raw]if len(raw)<8*1024**2 else[raw[i:i+3*1024**2]for i in range(0,len(raw),3*1024**2)];parts=[]
 for i,c in enumerate(chunks):
  fn=prefix+('.html'if mime=='text/html'else'.zip')if len(chunks)==1 else f'{prefix}.part{i+1:02}.bin';(O/'downloads'/fn).write_bytes(c);parts.append(dict(file=fn,bytes=len(c),sha256=hashlib.sha256(c).hexdigest()))
 m=dict(name=name,mime=mime,bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),parts=parts);(O/'downloads'/f'{prefix}-manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2));return m
of=publish(OFF,'offline','心情手账-离线学习单.html','text/html')
PPT=O/'downloads/mood-journal-lesson.pptx'
if not PPT.exists():PPT=W/'output/mood-journal-lesson-release.pptx'
ppt=publish(PPT,'ppt','心情手账-可编辑课件.pptx','application/vnd.openxmlformats-officedocument.presentationml.presentation')
ZIP=W/'mood-journal-package.zip'
with zipfile.ZipFile(ZIP,'w',zipfile.ZIP_DEFLATED)as z:
 for p in sorted(O.rglob('*')):
  if not p.is_file()or p.name=='mood-journal-lesson.pptx'or p.name.startswith(('.', 'package.','offline.','package-','offline-','ppt.','ppt-')):continue
  if p.suffix=='.html':
   h=p.read_text().replace('<button data-pack="ppt">可编辑PPT</button>','<a class="btn" href="downloads/mood-journal-lesson.pptx" download>可编辑PPT</a>').replace('<button data-pack="ppt">下载可编辑PPT</button>','<a href="downloads/mood-journal-lesson.pptx" download>下载可编辑PPT</a>').replace('href="../../../../../index.html','href="'+base+'index.html').replace('href="../../../../ciyu/','href="'+base+'du/ciyu/')
   if p.name=='teacher.html':h=h.replace('<button data-pack="offline">独立离线学习单</button>','<a class="btn" href="../../../../../心情手账-离线学习单.html">独立离线学习单</a>').replace('<button data-pack="package">整套下载</button>','').replace('<script src="pack.js"></script>','')
   z.writestr(p.relative_to(R).as_posix(),h)
  else:z.write(p,p.relative_to(R).as_posix())
 z.write(PPT,(O.relative_to(R)/'downloads/mood-journal-lesson.pptx').as_posix())
 for name in ['app.js','wordbook.js','catalog.js','style.css','wenkai.woff2','songti.woff2']:p=S/name;z.write(p,p.relative_to(R).as_posix())
 p=R/'assets/huawentong-logo.png';z.write(p,p.relative_to(R).as_posix());z.write(OFF,'心情手账-离线学习单.html')
 z.writestr('开始使用.html','<!doctype html><html lang="zh-SG"><meta charset="utf-8"><title>心情手账</title><body style="font:24px/2 system-ui;padding:40px"><h1>心情手账</h1><p><a href="心情手账-离线学习单.html">打开互动学习单</a></p><p><a href="'+rel+'teacher.html">教师资料、课件与图文回读</a></p><p>外部资料和平台词语预习需要网络。解压整套文件后使用。</p></body></html>')
pk=publish(ZIP,'package','心情手账-完整教学配套.zip','application/zip');print({'offline':of['bytes'],'package':pk['bytes'],'parts':[len(of['parts']),len(pk['parts'])]})

if (O/'downloads/mood-journal-lesson.pptx').exists():(O/'downloads/mood-journal-lesson.pptx').unlink()
