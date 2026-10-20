from pathlib import Path
import os,json,re,base64,hashlib,zipfile,shutil
W=Path(os.environ['ZM_BUILD_DIR']);R=Path(__file__).resolve().parents[2];O=R/'du/textbook/2hcl/unit4/zui-mei-de-zi-shi';S=R/'du/textbook/shared/lesson-v1';base='https://huawentong-home.lyqlym2015.workers.dev/';rel=O.relative_to(R).as_posix()+'/'
slides=json.loads((O/'slides.json').read_text());p=(R/'du/textbook/2hcl/unit3/shui-dou-qu-na-le/slides.html').read_text().replace('水都去哪儿了','最美的姿势').replace('water-lesson.pptx','zuimei-lesson.pptx').replace('单元三 · 一课时','单元四 · 两课时')
p=re.sub(r'const slides=.*?;\nconst \$',lambda m:'const slides='+json.dumps(slides,ensure_ascii=False).replace('</','<\\/')+';\nconst $',p,flags=re.S)
p=p.replace('<a href="downloads/zuimei-lesson.pptx" download>下载可编辑PPT</a>','<button data-pack="ppt">下载可编辑PPT</button>').replace('<nav aria-label="课件翻页">','<nav aria-label="分课入口"><a href="#1">第一课</a><a href="#20">第二课</a></nav><nav aria-label="课件翻页">').replace('</body>','<p id="packStatus" role="status"></p><script src="pack.js"></script></body>');(O/'slides.html').write_text(p)
readme='''最美的姿势｜中二高级华文 单元四 巩固阅读
两课时，每课按50分钟安排；位于《恐怖事件》之后。

学生：reading.html；10段原文、32格原漫画、10组12个步骤、词语本与闪卡。
教师：teacher.html；教学流程、答案、提示与人工评分建议。
在线投影：slides.html；39页，与PPT同版。第一课1—19页，第二课20—39页。
可编辑PPT：downloads/zuimei-lesson.pptx；原生文字可编辑，题目与答案分开。
教师DOCX：downloads/teacher-guide.docx；12页。
漫画：四张用户原图保持字节不变，段落与画格对应。取证以原文为准。
课本：七道旁注、仿句、关键句与主题、交友开放题均保留；教参补充讨论有独立标注。

每课两项文字作答。其余为点选、原句取证和口头讨论。
7个客观任务含8个选择检查；正确率按首次整项答对计算，不代表全课掌握程度。
主观题由教师按意义核对，不按字数或关键词自动评分。开放题必做并说明为什么。

记录：当前设备、当前浏览器本地保存，无账号同步及教师自动收件。检查页可导出首次作答、尝试、订正、身份及逐题记录。清理浏览器前先导出。
个人词语本：34项预设语境词，不强制收藏。自输未知词仍能建卡，标“释义待补充”。同域已接入课文按年级、单元、课文汇总；重置本课不删除词语本。

离线：独立HTML下载后打开；ZIP全部解压后打开“开始使用.html”。词语预习需要网络；朗读依赖设备语音。
PPT使用霞鹜文楷及思源宋体。未安装可能被替换，在线投影保留同版样式。
验证范围：内容与脚本、DOM模拟、PPT结构与逐页渲染、DOCX逐页渲染、资源和下载校验；未做实体iPad或原生PowerPoint实机测试。
'''
(O/'downloads/使用说明.txt').write_text(readme)
def data(p,mime):return 'data:'+mime+';base64,'+base64.b64encode(p.read_bytes()).decode()
s=(O/'reading.html').read_text()
def style(m):
 p=(O/m.group(1).split('?')[0]).resolve();css=p.read_text()
 for font in ['wenkai','songti']:css=css.replace('url('+font+'.woff2)','url('+data(S/(font+'.woff2'),'font/woff2')+')')
 return '<style>'+css+'</style>'
s=re.sub(r'<link rel="stylesheet" href="([^"]+)">',style,s).replace('../../../../../assets/huawentong-logo.png',data(R/'assets/huawentong-logo.png','image/png')).replace('href="../../../../../index.html','href="'+base+'index.html').replace('href="index.html"','href="'+base+rel+'index.html"')
def script(m):return '<script>'+(O/m.group(1).split('?')[0]).resolve().read_text().replace('</script','<\\/script')+'</script>'
s=re.sub(r'<script src="([^"]+)"></script>',script,s)
images={f'comic{i}':data(O/f'assets/comic{i}.png','image/png')for i in range(1,5)}
s=s.replace('<script>window.LESSON','<script>window.LESSON_ASSETS='+json.dumps(images)+';</script><script>window.LESSON',1)
OFF=W/'output/zuimei-offline.html';OFF.write_text(s)
def publish(src,prefix,name,mime):
 raw=src.read_bytes()
 for p in (O/'downloads').glob(prefix+'.*'):p.unlink()
 chunks=[raw]if len(raw)<8*1024**2 else[raw[i:i+3*1024**2]for i in range(0,len(raw),3*1024**2)];parts=[]
 for i,c in enumerate(chunks):
  fn=prefix+({'text/html':'.html','application/zip':'.zip'}.get(mime,'.pptx'))if len(chunks)==1 else f'{prefix}.part{i+1:02}.bin';(O/'downloads'/fn).write_bytes(c);parts.append(dict(file=fn,bytes=len(c),sha256=hashlib.sha256(c).hexdigest()))
 m=dict(name=name,mime=mime,bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),parts=parts);(O/'downloads'/f'{prefix}-manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2));return m
PPT=W/'output/zuimei-lesson.pptx';of=publish(OFF,'offline','最美的姿势-离线学习单.html','text/html');pm=publish(PPT,'ppt','最美的姿势-可编辑课件.pptx','application/vnd.openxmlformats-officedocument.presentationml.presentation')
ZIP=W/'output/zuimei-package.zip'
with zipfile.ZipFile(ZIP,'w',zipfile.ZIP_DEFLATED)as z:
 for p in sorted(O.rglob('*')):
  if not p.is_file()or p.name.startswith(('.', 'package.','offline.','package-','offline-','ppt.','ppt-')):continue
  if p.suffix=='.html':
   h=p.read_text().replace('<button data-pack="ppt">可编辑PPT</button>','<a class="btn" href="downloads/zuimei-lesson.pptx" download>可编辑PPT</a>').replace('<button data-pack="ppt">下载可编辑PPT</button>','<a href="downloads/zuimei-lesson.pptx" download>下载可编辑PPT</a>').replace('href="../../../../../index.html','href="'+base+'index.html').replace('href="../../../../ciyu/','href="'+base+'du/ciyu/')
   h=h.replace('<button data-pack="offline">独立离线学习单</button>','<a class="btn" href="../../../../../最美的姿势-离线学习单.html">独立离线学习单</a>').replace('<button data-pack="package">整套下载</button>','').replace('<script src="pack.js"></script>','')
   z.writestr(p.relative_to(R).as_posix(),h)
  else:z.write(p,p.relative_to(R).as_posix())
 z.write(PPT,rel+'downloads/zuimei-lesson.pptx')
 for name in ['app.js','wordbook.js','catalog.js','style.css','wenkai.woff2','songti.woff2']:
  p=S/name;z.write(p,p.relative_to(R).as_posix())
 p=R/'assets/huawentong-logo.png';z.write(p,p.relative_to(R).as_posix());z.write(OFF,'最美的姿势-离线学习单.html')
 z.writestr('开始使用.html','<!doctype html><html lang="zh-SG"><meta charset="utf-8"><title>最美的姿势</title><body style="font:24px/2 system-ui;padding:40px"><h1>最美的姿势</h1><p><a href="最美的姿势-离线学习单.html">打开互动学习单</a></p><p><a href="'+rel+'teacher.html">教师资料、课件与图文回读</a></p><p>整套解压后使用；平台词语预习需要网络。</p></body></html>')
pk=publish(ZIP,'package','最美的姿势-完整教学配套.zip','application/zip');print({'offline':of['bytes'],'ppt':pm['bytes'],'package':pk['bytes'],'parts':[len(of['parts']),len(pm['parts']),len(pk['parts'])]})
