from pathlib import Path
import os,json,re,base64,hashlib,zipfile
R=Path(__file__).resolve().parents[2];W=Path(os.environ.get('HWT_BUILD_WORKSPACE',R.parent));O=R/'du/textbook/2hcl/unit3/shou-ji-bei-diu-qi-zhi-hou';S=R/'du/textbook/shared/lesson-v1';base='https://huawentong-home.lyqlym2015.workers.dev/';rel=O.relative_to(R).as_posix()+'/'
slides=json.loads((O/'slides.json').read_text());p=(R/'du/textbook/2hcl/unit3/shui-dou-qu-na-le/slides.html').read_text();p=p.replace('水都去哪儿了','手机被丢弃之后').replace('water-lesson.pptx','phone-lesson.pptx').replace('单元三 · 一课时','单元三 · 两课时');p=re.sub(r'const slides=.*?;\nconst \$',lambda m:'const slides='+json.dumps(slides,ensure_ascii=False).replace('</','<\\/')+';\nconst $',p,flags=re.S);p=p.replace('<nav aria-label="课件翻页">','<nav aria-label="课件翻页"><a href="#1">第一课</a><a href="#18">第二课</a>');(O/'slides.html').write_text(p)
(O/'downloads/使用说明.txt').write_text('''手机被丢弃之后｜中二高级华文 单元三 阅读巩固
两课时，每课按50分钟安排，可依实际课长调整。

学生：reading.html，逐段图文、11步互动、每课两项书写、个人词语本与闪卡。
教师：teacher.html，流程、全部已提供问题的答案、评分建议及下载。
在线投影：slides.html；36页。第一课1—17，第二课18—36。
可编辑PPT：downloads/phone-lesson.pptx；饼状图及数据可编辑。折线图没有逐年原始数据，保留原绘图区，不编造精确数列。
教师DOCX：downloads/teacher-guide.docx。
漫画：使用附件四张原图，共32格，按9段对应。

离线：下载独立HTML后打开即可；整套ZIP先解压，再打开“开始使用.html”。外部平台和词语预习入口仍需网络。朗读取决于设备语音包。PPT使用霞鹜文楷及思源宋体，未安装时可能字体替换；在线投影已渲染为图片。

资料：保留教材原有年份，不当成2026年现况。已提供旁注、教参引导及三道巩固练习均已对应。课本正式题名为“手机被丢弃之后”，原文件及旧词语目录的“以后”作为同一课文识别。第3段“几乎会翻一番”照录；精确计算7400÷4440约为1.67，增加约67%，另作讲评说明。

保存：当前设备、当前浏览器保存，无教师自动收件及账号云同步。检查页可导出JSON、CSV及文字记录；词语本另有导入导出。清浏览器前先备份。主观回答由教师核对，不自动判分。重置本课保留个人词语本。
验证：完成页面DOM行为与资源校验；未做实体iPad、原生PowerPoint打开测试。
''')
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
for name in ['textbook-composition.png','textbook-trend.png']:images['assets/'+name]=data(O/'assets'/name,'image/png')
s=s.replace('<script>window.LESSON','<script>window.LESSON_ASSETS='+json.dumps(images)+';</script><script>window.LESSON',1)
OFF=W/'phone-offline.html';OFF.write_text(s)
def publish(src,prefix,name,mime):
 raw=src.read_bytes()
 for p in (O/'downloads').glob(prefix+'.*'):p.unlink()
 chunks=[raw]if len(raw)<24*1024**2 else[raw[i:i+3*1024**2]for i in range(0,len(raw),3*1024**2)];parts=[]
 for i,c in enumerate(chunks):
  fn=prefix+('.html'if mime=='text/html'else'.zip')if len(chunks)==1 else f'{prefix}.part{i+1:02}.bin';(O/'downloads'/fn).write_bytes(c);parts.append(dict(file=fn,bytes=len(c),sha256=hashlib.sha256(c).hexdigest()))
 m=dict(name=name,mime=mime,bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),parts=parts);(O/'downloads'/f'{prefix}-manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2));return m
of=publish(OFF,'offline','手机被丢弃之后-离线学习单.html','text/html')
ZIP=W/'phone-package.zip'
with zipfile.ZipFile(ZIP,'w',zipfile.ZIP_DEFLATED)as z:
 for p in sorted(O.rglob('*')):
  if not p.is_file()or p.name.startswith(('.', 'package.','offline.','package-','offline-')):continue
  if p.suffix=='.html':
   h=p.read_text().replace('href="../../../../../index.html','href="'+base+'index.html').replace('href="../../../../ciyu/','href="'+base+'du/ciyu/')
   if p.name=='teacher.html':h=h.replace('<button data-pack="offline">独立离线学习单</button>','<a class="btn" href="../../../../../手机被丢弃之后-离线学习单.html">独立离线学习单</a>').replace('<button data-pack="package">整套下载</button>','').replace('<script src="pack.js"></script>','')
   z.writestr(p.relative_to(R).as_posix(),h)
  else:z.write(p,p.relative_to(R).as_posix())
 for name in ['app.js','wordbook.js','catalog.js','style.css','wenkai.woff2','songti.woff2']:p=S/name;z.write(p,p.relative_to(R).as_posix())
 p=R/'assets/huawentong-logo.png';z.write(p,p.relative_to(R).as_posix());z.write(OFF,'手机被丢弃之后-离线学习单.html')
 z.writestr('开始使用.html','<!doctype html><html lang="zh-SG"><meta charset="utf-8"><title>手机被丢弃之后</title><body style="font:24px/2 system-ui;padding:40px"><h1>手机被丢弃之后</h1><p><a href="手机被丢弃之后-离线学习单.html">打开互动学习单</a></p><p><a href="'+rel+'teacher.html">教师资料、课件与图文回读</a></p><p>外部资料和平台词语预习需要网络。解压整套文件后使用。</p></body></html>')
pk=publish(ZIP,'package','手机被丢弃之后-完整教学配套.zip','application/zip');print({'offline':of['bytes'],'package':pk['bytes'],'parts':[len(of['parts']),len(pk['parts'])]})
