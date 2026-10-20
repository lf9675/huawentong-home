from pathlib import Path
import json,re,base64,hashlib,zipfile
R=Path(__file__).resolve().parents[2];W=R.parent;O=R/'du/textbook/2hcl/unit4/kongbushijian';S=R/'du/textbook/shared/lesson-v1';base='https://huawentong-home.lyqlym2015.workers.dev/';rel=O.relative_to(R).as_posix()+'/'
slides=json.loads((O/'slides.json').read_text());p=(R/'du/textbook/2hcl/unit3/shui-dou-qu-na-le/slides.html').read_text();p=p.replace('水都去哪儿了','恐怖事件').replace('water-lesson.pptx','horror-lesson.pptx').replace('单元三 · 一课时','单元四 · 2—3课时');p=re.sub(r'const slides=.*?;\nconst \$',lambda m:'const slides='+json.dumps(slides,ensure_ascii=False).replace('</','<\\/')+';\nconst $',p,flags=re.S);p=p.replace('<nav aria-label="课件翻页">','<nav aria-label="课件翻页"><a href="#1">第一课</a><a href="#19">第二课</a><a href="#36">第三课</a>');(O/'slides.html').write_text(p)
(O/'downloads/使用说明.txt').write_text('恐怖事件｜中二高级华文 单元四 核心课文\n2—3课时；三课时每课按50分钟安排，两课时精简方案见教师资料。\n\n学生：reading.html，19段图文，10组任务分为19步，个人词语本与闪卡。\n教师：teacher.html，流程、答案、评分建议、教材核对及旧题整合说明。\n在线投影：slides.html；46页，第一课1—18，第二课19—35，第三课36—46。\n可编辑PPT：downloads/horror-lesson.pptx；文字与两页统整表格可编辑。\n教师DOCX：downloads/teacher-guide.docx，共16页。\n漫画：五张原图共40格，按19段对应。原图片文件未改动，取证以课本原文为准。\n\n旧版：原网址的一份24题练习被两个入口重复引用，已整合并替换，移除重复课前预习入口。修正“讨厌鬼双关”“互相道歉”等错误，没有保留另一套重复练习。\n\n保存：同设备、同浏览器本地保存，未接入账号同步及教师自动收件。导出首次作答、尝试、订正和逐题记录。个人词语本支持已接入同域课文的分类、各出处、编辑、导入导出与闪卡。未知词建卡标释义待补充；重置本课不删词语本。\n\n离线：独立HTML下载后打开即可；ZIP先全部解压，再打开“开始使用.html”。外部平台词语预习需要网络；朗读依赖设备语音。PPT使用霞鹜文楷与思源宋体，未安装可能替换；在线投影为同版图片。\n\n检验：内容、原图字节、资源链接、离线资源、PPT/DOCX渲染和DOM交互校验。未做实体iPad或原生PowerPoint实机测试。\n')
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
images={f'comic{i}':data(O/f'assets/comic{i}.png','image/png')for i in range(1,6)}

s=s.replace('<script>window.LESSON','<script>window.LESSON_ASSETS='+json.dumps(images)+';</script><script>window.LESSON',1)
OFF=W/'horror-offline.html';OFF.write_text(s)
def publish(src,prefix,name,mime):
 raw=src.read_bytes()
 for p in (O/'downloads').glob(prefix+'.*'):p.unlink()
 chunks=[raw]if len(raw)<24*1024**2 else[raw[i:i+3*1024**2]for i in range(0,len(raw),3*1024**2)];parts=[]
 for i,c in enumerate(chunks):
  fn=prefix+('.html'if mime=='text/html'else'.zip')if len(chunks)==1 else f'{prefix}.part{i+1:02}.bin';(O/'downloads'/fn).write_bytes(c);parts.append(dict(file=fn,bytes=len(c),sha256=hashlib.sha256(c).hexdigest()))
 m=dict(name=name,mime=mime,bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),parts=parts);(O/'downloads'/f'{prefix}-manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2));return m
of=publish(OFF,'offline','恐怖事件-离线学习单.html','text/html')
ZIP=W/'horror-package.zip'
with zipfile.ZipFile(ZIP,'w',zipfile.ZIP_DEFLATED)as z:
 for p in sorted(O.rglob('*')):
  if not p.is_file()or p.name.startswith(('.', 'package.','offline.','package-','offline-')):continue
  if p.suffix=='.html':
   h=p.read_text().replace('href="../../../../../index.html','href="'+base+'index.html').replace('href="../../../../ciyu/','href="'+base+'du/ciyu/')
   if p.name=='teacher.html':h=h.replace('<button data-pack="offline">独立离线学习单</button>','<a class="btn" href="../../../../../恐怖事件-离线学习单.html">独立离线学习单</a>').replace('<button data-pack="package">整套下载</button>','').replace('<script src="pack.js"></script>','')
   z.writestr(p.relative_to(R).as_posix(),h)
  else:z.write(p,p.relative_to(R).as_posix())
 for name in ['app.js','wordbook.js','catalog.js','style.css','wenkai.woff2','songti.woff2']:p=S/name;z.write(p,p.relative_to(R).as_posix())
 p=R/'assets/huawentong-logo.png';z.write(p,p.relative_to(R).as_posix());z.write(OFF,'恐怖事件-离线学习单.html')
 z.writestr('开始使用.html','<!doctype html><html lang="zh-SG"><meta charset="utf-8"><title>恐怖事件</title><body style="font:24px/2 system-ui;padding:40px"><h1>恐怖事件</h1><p><a href="恐怖事件-离线学习单.html">打开互动学习单</a></p><p><a href="'+rel+'teacher.html">教师资料、课件与图文回读</a></p><p>外部资料和平台词语预习需要网络。解压整套文件后使用。</p></body></html>')
pk=publish(ZIP,'package','恐怖事件-完整教学配套.zip','application/zip');print({'offline':of['bytes'],'package':pk['bytes'],'parts':[len(of['parts']),len(pk['parts'])]})
