"""Create verified resource manifests while preserving download formats and companion files."""
from pathlib import Path
import base64,hashlib,io,json,mimetypes,os,re,struct,subprocess,sys,zipfile,zlib
ROOT=Path(__file__).resolve().parents[2];SHARED=ROOT/'du/textbook/shared/lesson-v1';OUT=Path(sys.argv[1]);OUT.mkdir(parents=True,exist_ok=True)
BASE='https://huawentong-home.lyqlym2015.workers.dev/'
def sha(b):return hashlib.sha256(b).hexdigest()
def old(p):return json.loads(subprocess.check_output(['git','show','88d102f6d15c4c7cc8672d2f31d332b4d3a91eaa:'+p.relative_to(ROOT).as_posix()],cwd=ROOT))
def local(d,n):
 p=(d/n).resolve()
 if not p.is_file():p=(d/'downloads'/n).resolve()
 assert p.is_file(),p
 return p
tracked=subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().split('\0');byhash={};multipart={}
for name in tracked:
 p=ROOT/name
 if p.is_file() and p.suffix in ('.png','.webp','.woff2','.ttf','.otf','.pptx','.docx','.zip'):byhash.setdefault(sha(p.read_bytes()),p)
for p in ROOT.glob('du/textbook/*hcl/unit*/*/assets/panels/*.png'):byhash[sha(p.read_bytes())]=p
for p in ROOT.glob('du/textbook/*hcl/unit*/*/downloads/*manifest.json'):
 if 'offline' in p.name or 'package' in p.name:continue
 try:
  m=old(p);paths=[local(p.parent.parent,s.get('file',s.get('url'))) for s in m.get('parts',m.get('chunks',[]))];raw=b''.join(x.read_bytes() for x in paths)
  if sha(raw)==m.get('sha256'):multipart[sha(raw)]=paths
 except (AssertionError,KeyError,TypeError):pass

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
 assets={p.relative_to(d).as_posix():dataurl(p) for p in sorted((d/'assets/panels').glob('*.png'))}
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

def readparts(d,m):
 out=[]
 for p in m.get('parts',m.get('chunks',[])):
  if p.get('header'):out.append(base64.b64decode(p['header']))
  children=p.get('segments',p.get('chunks'))
  if children:out.extend(local(d,s.get('file',s.get('url'))).read_bytes() for s in children)
  else:out.append(local(d,p.get('file',p.get('url'))).read_bytes())
 if m.get('tail'):out.append(base64.b64decode(m['tail']))
 return b''.join(out)
def oldfiles(d,m):
 if m.get('entries'):return [(e['path'],readparts(d,{'parts':e['parts']}) if e.get('parts') else local(d,e['url']).read_bytes()) for e in m['entries']]
 if m.get('tail'):return [(p['name'],readparts(d,{'parts':p.get('segments',p.get('chunks')) or [dict(p,header='')]})) for p in m['parts']]
 z=zipfile.ZipFile(io.BytesIO(readparts(d,m)));assert z.testzip() is None;return [(n,z.read(n)) for n in z.namelist() if not n.endswith('/')]

def zip_parts(d,files):
 parts=[];central=[];offset=0;seen=set()
 for n,b in files:
  assert n not in seen,n;seen.add(n);nb=n.encode();crc=zlib.crc32(b);size=len(b)
  h=struct.pack('<IHHHHHIIIHH',0x04034b50,20,0x800,0,0,0x5d56,crc,size,size,len(nb),0)+nb
  c=struct.pack('<IHHHHHHIIIHHHHHII',0x02014b50,20,20,0x800,0,0,0x5d56,crc,size,size,len(nb),0,0,0,0,0,offset)+nb
  parts.append({'base64':base64.b64encode(h).decode()});parts+=textparts(d,b.decode()) if Path(n).suffix in ('.html','.js','.css','.txt','.json','.md','.url') else resource(d,b,n);central.append(c);offset+=len(h)+size
 c=b''.join(central);end=struct.pack('<IHHHHIIH',0x06054b50,0,0,len(seen),len(seen),len(c),offset,0);parts.append({'base64':base64.b64encode(c+end).decode()});return parts

def adapt(d,n,b,off):
 if n=='source.zip':
  z=zipfile.ZipFile(io.BytesIO(b));buf=io.BytesIO()
  with zipfile.ZipFile(buf,'w',zipfile.ZIP_DEFLATED) as out:
   for f in z.namelist():
    if not f.endswith('/'):out.writestr(f,adapt(d,f,z.read(f),off))
  return buf.getvalue()
 if n.endswith('.html') and len(b)>500000:
  if '词语' in n or 'vocab' in n:return inline(d,'vocabulary.html') if (d/'vocabulary.html').exists() else b
  if any(x in n for x in ['学习','阅读','offline']) or n=='index.html':return off
 candidates=[ROOT/n,d/n]
 if n.startswith('shared/'):candidates.insert(0,SHARED/Path(n).name)
 for p in candidates:
  if p.is_file() and p.suffix in ('.js','.css','.html','.json','.txt','.md') and 'authoring' not in p.parts:
   raw=p.read_bytes();return sanitise(raw.decode()).encode() if p.suffix=='.html' else raw
 return b

def save(d,p,name,mime,parts):
 raw=bytesof(d,parts);m={'format':'hwt-parts-v2','name':name,'mime':mime,'bytes':len(raw),'sha256':sha(raw),'parts':parts};p.write_text(json.dumps(m,ensure_ascii=False,separators=(',',':')));return raw

reports=[]
for reading in sorted(ROOT.glob('du/textbook/*hcl/unit*/*/reading.html')):
 d=reading.parent;slug=d.name
 if len(sys.argv)>2 and slug not in sys.argv[2:]:continue
 off=inline(d);(OUT/(slug+'.html')).write_bytes(off)
 for p in (d/'downloads/offline').glob('*.html'):
  s=sanitise((d/p.name).read_text()).replace('../../../shared/lesson-v1/','shared/').replace('../../../../../assets/','assets/').replace('../../../../../index.html#1/texts','index.html');s=re.sub(r'<script[^>]*src="pack\.js[^\"]*"[^>]*></script>','',s);p.write_text(s)
 mp=d/'downloads/offline-manifest.json';offzip=None
 if mp.exists():
  m=old(mp);name=m.get('name',m.get('filename'));iszip=name.endswith('.zip')
  if not iszip:parts=textparts(d,off.decode())
  else:
   files=oldfiles(d,m)
   if m.get('entries'):files +=[(p.relative_to(d).as_posix(),p.read_bytes()) for p in sorted((d/'assets/panels').glob('*.png'))]
   else:files=[(n,off if n=='index.html' else b) for n,b in files]
   parts=zip_parts(d,files)
  raw=save(d,mp,name,'application/zip' if iszip else 'text/html;charset=utf-8',parts);(OUT/(slug+'-offline'+('.zip' if iszip else '.html'))).write_bytes(raw)
  if iszip:offzip=raw
 pp=d/'downloads/package-manifest.json';pp=pp if pp.exists() else d/'downloads/resource-pack.json';m=old(pp);files=oldfiles(d,m);updated=[]
 for n,b in files:
  if n.endswith('-offline.zip') and offzip is not None:b=offzip
  elif not m.get('entries'):b=adapt(d,n,b,off)
  updated.append((n,b))
 prefix=d.relative_to(ROOT).as_posix()+'/' if any(n.startswith(d.relative_to(ROOT).as_posix()+'/') for n,_ in updated) else ''
 if any(n==prefix+'content.js' for n,_ in updated):
  names={n for n,_ in updated}
  for p in sorted((d/'assets/panels').glob('*.png')):
   n=prefix+p.relative_to(d).as_posix()
   if n not in names:updated.append((n,p.read_bytes()))
 parts=zip_parts(d,updated);raw=save(d,pp,m.get('name',m.get('filename','团圆饭_完整教学资源包.zip')),'application/zip',parts);z=zipfile.ZipFile(io.BytesIO(raw));assert z.testzip() is None;(OUT/(slug+'-package.zip')).write_bytes(raw)
 reports.append({'lesson':slug,'offlineBytes':len(off),'packageBytes':len(raw),'files':len(updated)});print(slug,len(off),len(raw),len(updated),flush=True)
(OUT/'report.json').write_text(json.dumps(reports,ensure_ascii=False,indent=2))
