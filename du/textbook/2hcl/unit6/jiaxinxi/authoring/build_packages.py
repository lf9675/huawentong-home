from pathlib import Path
import base64,re,json,hashlib,zipfile,shutil
from fontTools.ttLib import TTFont
from fontTools import subset
ROOT=Path(__file__).resolve().parents[1];R=ROOT/'site/du/textbook/2hcl/unit6/jiaxinxi';H=ROOT/'site';B=ROOT/'build';D=R/'downloads'
base='https://huawentong-home.lyqlym2015.workers.dev/du/textbook/2hcl/unit6/jiaxinxi/'
def data(p,m):return 'data:'+m+';base64,'+base64.b64encode(p.read_bytes()).decode()
html=(R/'reading.html').read_text().replace('href="index.html"','href="'+base+'index.html"').replace('>主页</a>','>在线主页</a>').replace('href="../../../../../index.html#2/texts"','href="https://huawentong-home.lyqlym2015.workers.dev/index.html#2/texts"').replace('src="../../../../../assets/huawentong-logo.png"','src="'+data(H/'assets/huawentong-logo.png','image/png')+'"')
chars=''.join(p.read_text() for p in list(R.glob('*.html'))+list(R.glob('*.js'))+list((H/'du/textbook/shared/lesson-v1').glob('*.js')));fonts={}
for n,source in [('wenkai',Path('/root/.local/share/fonts/huawentong-wenkai.ttf')),('songti',Path('/root/.local/share/fonts/songti.ttf'))]:
 f=TTFont(source);s=subset.Subsetter();s.populate(text=chars);s.subset(f);f.flavor='woff';dest=B/(n+'-offline.woff');f.save(dest);fonts[n]=data(dest,'font/woff')
def css(m):
 p=(R/m.group(1).split('?')[0]).resolve();text=p.read_text()
 for n,url in fonts.items():text=re.sub(r"url\(['\"]?"+n+r"\.woff2['\"]?\)",'url('+url+')',text)
 return '<style>'+text+'</style>'
html=re.sub(r'<link rel="stylesheet" href="([^"]+)">',css,html)
assets={'comic'+str(i):data(R/f'assets/comic{i}.png','image/png') for i in range(1,6)}
html=html.replace('<script src="content.js', '<script>window.LESSON_ASSETS='+json.dumps(assets)+';</script><script src="content.js')
def script(m):return '<script>'+(R/m.group(1).split('?')[0]).resolve().read_text().replace('</script','<\\/script')+'</script>'
html=re.sub(r'<script src="([^"]+)"></script>',script,html)
html=html.replace('<button data-view="read">','<button id="fullComics">漫画整页</button><button data-view="read">')
html=html.replace('</body>', '<script>document.querySelector("#fullComics").onclick=()=>{const d=document.querySelector("#dialog"),c=document.querySelector("#dialogContent");c.innerHTML="<h2>原有漫画五页</h2>";for(const src of Object.values(window.LESSON_ASSETS)){const i=document.createElement("img");i.src=src;i.style.width="100%";c.append(i)}d.showModal()};</script></body>')
offline=B/'offline';offline.mkdir(exist_ok=True);(offline/'index.html').write_text(html)
(offline/'README.txt').write_text('别上假信息的当｜离线学生学习包\n解压后打开 index.html。全文、五页原漫画、互动题和词语本均已包含。在线主页需联网；设备语音是否可用取决于系统。\n记录保存在当前设备与浏览器。离线与在线记录分开；词语本可导出导入，作答记录可导出。主观题由教师核对。\n字体遵循附带的SIL Open Font License。\n')
with zipfile.ZipFile(D/'jiaxinxi-offline.zip','w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in offline.iterdir():z.write(p,p.name)
 for n in ['OFL-WenKai.txt','OFL-Noto.txt']:z.write(R/'assets'/n,n)
with zipfile.ZipFile(D/'fonts.zip','w',zipfile.ZIP_DEFLATED) as z:
 z.write('/root/.local/share/fonts/huawentong-wenkai.ttf','Huawentong-WenKai.ttf');z.write('/root/.local/share/fonts/songti.ttf','Noto-Serif-CJK-SC.ttf')
 for n in ['OFL-WenKai.txt','OFL-Noto.txt']:z.write(R/'assets'/n,n)
with zipfile.ZipFile(D/'source.zip','w',zipfile.ZIP_DEFLATED) as z:
 for p in (R/'authoring').glob('*'):
  if p.is_file():z.write(p,'authoring/'+p.name)
 for p in list(R.glob('*.js'))+list(R.glob('*.json'))+list(R.glob('*.html'))+list(R.glob('*.css')):z.write(p,p.name)
(R/'README.txt').write_text('别上假信息的当 教学配套\n中二高级华文 · 单元六 · 巩固课文 · 两课时\n\n教师：jiaxinxi.pptx 与 teacher-guide.docx。\n学生：解压 jiaxinxi-offline.zip，打开 index.html。\noriginal-comics 保留五页原漫画。\n本机编辑课件可安装 fonts.zip 中字体。在线投影无需安装。\n作答记录保存在当前设备与浏览器，可导出；主观题由教师核对。\n词语本按年级、单元、课文汇总，无账号云同步。\nsource.zip 供后续维护。\n教师资料：'+base+'teacher.html\n')
files=[('jiaxinxi.pptx','downloads/jiaxinxi.pptx'),('teacher-guide.docx','downloads/teacher-guide.docx'),('jiaxinxi-offline.zip','downloads/jiaxinxi-offline.zip'),('fonts.zip','downloads/fonts.zip'),('source.zip','downloads/source.zip'),('README.txt','README.txt')]+[(f'original-comics/comic{i}.png',f'assets/comic{i}.png') for i in range(1,6)]
full=B/'jiaxinxi-package.zip'
with zipfile.ZipFile(full,'w',zipfile.ZIP_STORED) as z:
 for name,src in files:z.write(R/src,name)
parts=[]
with zipfile.ZipFile(full) as z,full.open('rb') as f:
 for name,src in files:
  info=z.getinfo(name);f.seek(info.header_offset);header=f.read(30+len(info.filename.encode())+len(info.extra));bb=(R/src).read_bytes();parts.append(dict(file=src,name=name,bytes=len(bb),sha256=hashlib.sha256(bb).hexdigest(),header=base64.b64encode(header).decode()))
 f.seek(z.start_dir);tail=base64.b64encode(f.read()).decode()
for entry in parts:
 src=R/entry['file']
 if src.stat().st_size<=4*1024*1024:continue
 key={'jiaxinxi.pptx':'pptx','jiaxinxi-offline.zip':'offline','fonts.zip':'fonts'}.get(src.name)
 if not key:continue
 segments=[]
 with src.open('rb') as source:
  count=1
  while block:=source.read(4*1024*1024):
   name=f'{key}-{count:02}.bin';(D/name).write_bytes(block);segments.append(dict(file='downloads/'+name,bytes=len(block),sha256=hashlib.sha256(block).hexdigest()));count+=1
 entry['segments']=segments;(D/(key+'-manifest.json')).write_text(json.dumps(dict(filename=src.name,bytes=entry['bytes'],sha256=entry['sha256'],parts=segments),indent=2))
(D/'package-manifest.json').write_text(json.dumps(dict(filename='jiaxinxi-package.zip',bytes=full.stat().st_size,sha256=hashlib.sha256(full.read_bytes()).hexdigest(),parts=parts,tail=tail),indent=2))
print('Offline', (D/'jiaxinxi-offline.zip').stat().st_size,'Full',full.stat().st_size)
