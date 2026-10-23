"""Build SHA-256-verified offline HTML and full-package manifests; binary assets are reused."""
from pathlib import Path
import base64,hashlib,io,json,mimetypes,os,re,struct,zipfile,zlib
ROOT=Path(__file__).resolve().parents[2]
D=ROOT/'du/textbook/1hcl/unit4/peiyang-hao-xiguan'
SHARED=ROOT/'du/textbook/shared/lesson-v1'
OUT=ROOT.parent/'build/output';OUT.mkdir(parents=True,exist_ok=True)
BASE='https://huawentong-home.lyqlym2015.workers.dev/'
def sha(b):return hashlib.sha256(b).hexdigest()
def local(d,n):
 p=(d/n).resolve();assert p.is_file(),p;return p
byhash={};multipart={}
for p in list(D.rglob('*'))+list(SHARED.glob('*'))+[ROOT/'assets/huawentong-logo.png']:
 if p.is_file() and p.suffix in ['.png','.woff2','.pptx','.docx']:byhash[sha(p.read_bytes())]=p
def fp(d,p,encoding=None):
 b=p.read_bytes();r={'url':os.path.relpath(p,d),'bytes':len(b),'sha256':sha(b)}
 if encoding:r['encoding']=encoding
 return r

def resource(d,b,label='resource.bin',encoding=None):
 h=sha(b)
 if h in byhash:return [fp(d,byhash[h],encoding)]
 if h in multipart and not encoding:return [fp(d,p) for p in multipart[h]]
 target=d/'downloads/ipad-assets';target.mkdir(exist_ok=True);out=target/(h[:16]+(Path(label).suffix or '.bin'))
 if len(b)<=10*1024**2:out.write_bytes(b);byhash[h]=out;return [fp(d,out,encoding)]
 assert not encoding
 parts=[]
 for i,j in enumerate(range(0,len(b),10*1024**2)):
  p=out.with_name(out.stem+f'-{i+1:02d}.bin');p.write_bytes(b[j:j+10*1024**2]);parts.append(fp(d,p))
 return parts

def textparts(d,s):
 parts=[];pos=0
 for m in re.finditer(r'data:([^;"\s]+);base64,([A-Za-z0-9+/=]{80,})',s):
  if m.start(2)>pos:parts.append({'text':s[pos:m.start(2)]})
  parts+=resource(d,base64.b64decode(m[2]),'embedded'+(mimetypes.guess_extension(m[1]) or '.bin'),'base64');pos=m.end(2)
 if pos<len(s):parts.append({'text':s[pos:]})
 return parts

def bytesof(d,parts):
 out=[]
 for p in parts:
  if 'text' in p:out.append(p['text'].encode())
  elif 'base64' in p:out.append(base64.b64decode(p['base64']))
  else:
   b=local(d,p['url']).read_bytes();assert len(b)==p['bytes'] and sha(b)==p['sha256'];out.append(base64.b64encode(b) if p.get('encoding')=='base64' else b)
 return b''.join(out)

def dataurl(p):return 'data:'+(mimetypes.guess_type(p.name)[0] or 'application/octet-stream')+';base64,'+base64.b64encode(p.read_bytes()).decode()
def sanitise(s):return re.sub(r'<script[^>]*src="[^"]*(?:cloud[^/"?]*|package-v2)\.js[^"\s]*"[^>]*></script>','',s)
def inline(d,name='reading.html'):
 s=sanitise((d/name).read_text())
 def css(m):
  p=local(d,m[1].split('?')[0]);v=p.read_text()
  def url(u):
   n=u[1].strip('\'"');f=(p.parent/n).resolve()
   return 'url("'+dataurl(f)+'")' if not n.startswith(('data:','http:','https:')) and f.exists() else u[0]
  return '<style>'+re.sub(r'url\(([^)]+)\)',url,v)+'</style>'
 s=re.sub(r'<link[^>]*rel="stylesheet"[^>]*href="([^"]+)"[^>]*>',css,s)
 s=re.sub(r'<script[^>]*src="([^"]+)"[^>]*></script>',lambda m:'<script>'+local(d,m[1].split('?')[0]).read_text().replace('</script','<\\/script')+'</script>',s)
 assets={p.relative_to(d).as_posix():dataurl(p) for p in [d/n for n in (json.loads((d/'lesson.json').read_text()) if (d/'lesson.json').exists() else json.loads((d/'content.js').read_text().split('=',1)[1].strip().rstrip(';')))['panelImages']]}
 s=s.replace('<script>','<script>window.LESSON_ASSETS='+json.dumps(assets)+';</script><script>',1)
 def img(m):
  p=(d/m[1].split('?')[0]).resolve();return m[0].replace(m[1],dataurl(p)) if p.is_file() else m[0]
 s=re.sub(r'<img[^>]*src="([^"]+)"[^>]*>',img,s)
 def link(m):
  u=m[1]
  if u.startswith(('#','http:','https:','data:','mailto:')):return m[0]
  dest=(d/u.split('#')[0].split('?')[0]).resolve()
  return 'href="'+BASE+dest.relative_to(ROOT).as_posix()+('#'+u.split('#',1)[1] if '#' in u else '')+'"' if dest.is_relative_to(ROOT) else m[0]
 s=re.sub(r'href="([^"]+)"',link,s);s=s.replace('<main>','<main><p class="muted">离线版 · 关闭前请导出学习记录。</p>',1)
 assert not re.search(r'<script[^>]+src=',s)
 return s.encode()

def zip_parts(d,files):
 parts=[];central=[];offset=0;seen=set()
 for n,b in files:
  assert n not in seen,n;seen.add(n);nb=n.encode();crc=zlib.crc32(b);size=len(b)
  h=struct.pack('<IHHHHHIIIHH',0x04034b50,20,0x800,0,0,0x5d56,crc,size,size,len(nb),0)+nb
  c=struct.pack('<IHHHHHHIIIHHHHHII',0x02014b50,20,20,0x800,0,0,0x5d56,crc,size,size,len(nb),0,0,0,0,0,offset)+nb
  parts.append({'base64':base64.b64encode(h).decode()});parts+=textparts(d,b.decode()) if Path(n).suffix in ('.html','.js','.css','.txt','.json','.md','.url') else resource(d,b,n);central.append(c);offset+=len(h)+size
 c=b''.join(central);end=struct.pack('<IHHHHIIH',0x06054b50,0,0,len(seen),len(seen),len(c),offset,0);parts.append({'base64':base64.b64encode(c+end).decode()});return parts

def save(d,p,name,mime,parts):
 raw=bytesof(d,parts);m={'format':'hwt-parts-v2','name':name,'mime':mime,'bytes':len(raw),'sha256':sha(raw),'parts':parts};p.write_text(json.dumps(m,ensure_ascii=False,separators=(',',':')));return raw


off=inline(D)
save(D,D/'downloads/offline-manifest.json','培养好习惯_离线学习.html','text/html;charset=utf-8',textparts(D,off.decode()))
(OUT/'habits-offline.html').write_bytes(off)
files=[('培养好习惯_离线学习.html',off),('使用说明.txt',(D/'使用说明.txt').read_bytes())]
for p in sorted(D.rglob('*')):
 if not p.is_file() or p.name.endswith('manifest.json') or 'ipad-assets' in p.parts:continue
 b=p.read_bytes();n='网页/'+p.relative_to(D).as_posix()
 if p.suffix=='.html':
  b=sanitise(b.decode()).replace('../../../shared/lesson-v1/','shared/').replace('../../../../../assets/','assets/').replace('../../../../../index.html#1/texts',BASE+'index.html#1/texts').replace('/bei/management/textbook/?lesson=s1u4l1',BASE+'bei/management/textbook/?lesson=s1u4l1').encode()
 if p.name=='teacher.html':
  b=re.sub(r'<button[^>]*id="(?:downloadPack|downloadOffline)"[^>]*>.*?</button>','',b.decode()).encode()
  b=b.replace(b'<p id="packStatus"',b'<p><a href="../'+ '培养好习惯_离线学习.html'.encode()+b'">'+ '打开离线学习页'.encode()+b'</a></p><p id="packStatus"')
 files.append((n,b))
V=ROOT/'du/ciyu/1hcl/unit4/peiyang-hao-xiguan'
vocab=inline(V,'index.html')
files.append(('词语巩固.html',vocab))
files=[(n,b.replace(b'../../../../ciyu/1hcl/unit4/peiyang-hao-xiguan/',b'../'+ '词语巩固.html'.encode())) if n.startswith('网页/') and n.endswith('.html') else (n,b) for n,b in files]
for p in sorted(SHARED.iterdir()):
 if p.is_file():files.append(('网页/shared/'+p.name,p.read_bytes()))
files.append(('网页/assets/huawentong-logo.png',(ROOT/'assets/huawentong-logo.png').read_bytes()))
for p in sorted((ROOT/'tools/habits').glob('*')):
 if p.is_file():files.append(('制作源文件/'+p.name,p.read_bytes()))
raw=save(D,D/'downloads/package-manifest.json','培养好习惯_完整教学配套.zip','application/zip',zip_parts(D,files))
(OUT/'habits-package.zip').write_bytes(raw)
z=zipfile.ZipFile(io.BytesIO(raw));assert z.testzip() is None
print(json.dumps({'offlineBytes':len(off),'packageBytes':len(raw),'files':len(files),'sha256':sha(raw)}))
