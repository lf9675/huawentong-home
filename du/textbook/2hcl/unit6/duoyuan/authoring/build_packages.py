from pathlib import Path
import base64,re,json,hashlib,zipfile,shutil
from fontTools.ttLib import TTFont
from fontTools import subset
R=Path(__file__).resolve().parents[1];H=R.parents[4];B=H.parent/'build';D=R/'downloads'
base='https://huawentong-home.lyqlym2015.workers.dev/du/textbook/2hcl/unit6/duoyuan/'
def data(p,m):return 'data:'+m+';base64,'+base64.b64encode(p.read_bytes()).decode()
html=(R/'reading.html').read_text()
# A single self-contained student file; all learning code, fonts and original images are embedded.
html=html.replace('href="index.html"','href="'+base+'index.html"').replace('>主页</a>','>在线主页</a>')
html=html.replace('href="../../../../../index.html#2/texts"','href="https://huawentong-home.lyqlym2015.workers.dev/index.html#2/texts"')
html=html.replace('src="../../../../../assets/huawentong-logo.png"','src="'+data(H/'assets/huawentong-logo.png','image/png')+'"')
chars=''.join(p.read_text() for p in list(R.glob('*.html'))+list(R.glob('*.js'))+list((H/'du/textbook/shared/lesson-v1').glob('*.js')))
fonts={}
for n,source in [('wenkai',B/'huawentong-wenkai.ttf'),('songti',Path('/root/.local/share/fonts/songti.ttf'))]:
 f=TTFont(source);s=subset.Subsetter();s.populate(text=chars);s.subset(f);f.flavor='woff';dest=B/(n+'-offline.woff');f.save(dest);fonts[n]=data(dest,'font/woff')
def css(m):
 p=(R/m.group(1).split('?')[0]).resolve();text=p.read_text()
 for n,url in fonts.items():text=re.sub(r"url\(['\"]?"+n+r"\.woff2['\"]?\)",'url('+url+')',text)
 text=text.replace('url(assets/rare.woff)','url('+data(R/'assets/rare.woff','font/woff')+')')
 return '<style>'+text+'</style>'
html=re.sub(r'<link rel="stylesheet" href="([^"]+)">',css,html)
assets={'comic'+str(i):data(R/f'assets/comic{i}.png','image/png') for i in range(1,6)}
html=html.replace('<script src="content.js', '<script>window.LESSON_ASSETS='+json.dumps(assets)+';</script><script src="content.js')
def script(m):return '<script>'+(R/m.group(1).split('?')[0]).resolve().read_text().replace('</script','<\\/script')+'</script>'
html=re.sub(r'<script src="([^"]+)"></script>',script,html)
html=html.replace('<button data-view="read">','<button id="fullComics">漫画整页</button><button data-view="read">')
html=html.replace('</body>', '<script>document.querySelector("#fullComics").onclick=()=>{const d=document.querySelector("#dialog"),c=document.querySelector("#dialogContent");c.innerHTML="<h2>原有漫画五页</h2>";for(const src of Object.values(window.LESSON_ASSETS)){const i=document.createElement("img");i.src=src;i.style.width="100%";c.append(i)}d.showModal()};</script></body>')
offline=B/'offline';offline.mkdir(exist_ok=True);(offline/'index.html').write_text(html)
readme='多元而开放的新加坡｜离线学生学习包\n解压后打开 index.html。原文、五页原漫画、互动题、词语本均已包含。\n打开“漫画整页”可看五页原漫画；“在线主页”需要联网。\n记录保存在当前设备与浏览器。在线与离线记录分开；词语本可导出导入，作答记录可导出留存。主观题由教师核对。\n字体遵循附带的SIL Open Font License。\n'
(offline/'README.txt').write_text(readme)
with zipfile.ZipFile(D/'duoyuan-offline.zip','w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in offline.iterdir():z.write(p,p.name)
 z.write(R/'assets/OFL-WenKai.txt','OFL-WenKai.txt');z.write(B/'noto-font/package/LICENSE','OFL-Noto.txt')
# Assemble the full ZIP from files that are already served; avoid duplicate large assets.
with zipfile.ZipFile(D/'fonts.zip','w',zipfile.ZIP_DEFLATED) as z:
 z.write(B/'huawentong-wenkai.ttf','Huawentong-WenKai.ttf');z.write('/root/.local/share/fonts/songti.ttf','Noto-Serif-CJK-SC.ttf')
 z.write(R/'assets/OFL-WenKai.txt','OFL-WenKai.txt');z.write(B/'noto-font/package/LICENSE','OFL-Noto.txt')
with zipfile.ZipFile(D/'source.zip','w',zipfile.ZIP_DEFLATED) as z:
 for p in (R/'authoring').glob('*'):
  if p.is_file():z.write(p,'authoring/'+p.name)
 for p in list(R.glob('*.js'))+list(R.glob('*.json')):z.write(p,p.name)
(R/'README.txt').write_text('多元而开放的新加坡 教学配套\n中二高级华文 · 单元六 · 核心课文\n\n教师：duoyuan.pptx与teacher-guide.docx。\n学生：解压duoyuan-offline.zip，打开其中index.html。\noriginal-comics保留五页原漫画。\n本机编辑课件并保持相同字形时，可安装fonts.zip中的字体；在线投影无需安装。\n作答记录保存于同设备同浏览器，可导出；主观题由教师核对。词语本按年级、单元与课文汇总。\nsource.zip供后续维护。\n在线教师资料：'+base+'teacher.html\n')
files=[('duoyuan.pptx','downloads/duoyuan.pptx'),('teacher-guide.docx','downloads/teacher-guide.docx'),('duoyuan-offline.zip','downloads/duoyuan-offline.zip'),('fonts.zip','downloads/fonts.zip'),('source.zip','downloads/source.zip'),('README.txt','README.txt')]+[(f'original-comics/comic{i}.png',f'assets/comic{i}.png') for i in range(1,6)]
full=B/'duoyuan-package.zip'
with zipfile.ZipFile(full,'w',zipfile.ZIP_STORED) as z:
 for name,src in files:z.write(R/src,name)
parts=[]
with zipfile.ZipFile(full) as z,full.open('rb') as f:
 for name,src in files:
  info=z.getinfo(name);f.seek(info.header_offset);header=f.read(30+len(info.filename.encode())+len(info.extra));data_bytes=(R/src).read_bytes()
  parts.append(dict(file=src,name=name,bytes=len(data_bytes),sha256=hashlib.sha256(data_bytes).hexdigest(),header=base64.b64encode(header).decode()))
 f.seek(z.start_dir);tail=base64.b64encode(f.read()).decode()
# Each hosted binary stays small enough for the publishing connector and static host.
for entry in parts:
 src=R/entry['file']
 if src.stat().st_size<=4*1024*1024:continue
 key={'duoyuan.pptx':'pptx','duoyuan-offline.zip':'offline','fonts.zip':'fonts'}.get(src.name)
 if not key:continue
 segments=[]
 with src.open('rb') as source:
  count=1
  while block:=source.read(4*1024*1024):
   name=f'{key}-{count:02}.bin';(D/name).write_bytes(block);segments.append(dict(file='downloads/'+name,bytes=len(block),sha256=hashlib.sha256(block).hexdigest()));count+=1
 entry['segments']=segments
 (D/(key+'-manifest.json')).write_text(json.dumps(dict(filename=src.name,bytes=entry['bytes'],sha256=entry['sha256'],parts=segments),indent=2))
(D/'package-manifest.json').write_text(json.dumps(dict(filename='duoyuan-package.zip',bytes=full.stat().st_size,sha256=hashlib.sha256(full.read_bytes()).hexdigest(),parts=parts,tail=tail),indent=2))
for p in D.glob('package-*.bin'):p.unlink()
assert (D/'duoyuan.pptx').stat().st_size<25*1024*1024
assert (D/'duoyuan-offline.zip').stat().st_size<25*1024*1024
print('Offline',(D/'duoyuan-offline.zip').stat().st_size,'Full',full.stat().st_size,'source parts',len(parts))
