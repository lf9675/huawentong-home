from pathlib import Path
from html.parser import HTMLParser
import hashlib,json,re,zipfile,subprocess
R=Path(__file__).resolve().parents[2];D=R/'du/textbook/2hcl/unit2/mao'
class Links(HTMLParser):
 def handle_starttag(self,tag,attrs):
  for k,v in attrs:
   if k in ('href','src') and v and not v.startswith(('http:','https:','data:','#','blob:')):
    p=(self.file.parent/v.split('?')[0].split('#')[0]).resolve()
    assert p.is_file(),(self.file.name,v)
for f in D.glob('*.html'):
 a=Links();a.file=f;a.feed(f.read_text())
for name in ['package','offline']:
 m=json.loads((D/f'downloads/{name}-manifest.json').read_text());chunks=[]
 for part in m['parts']:
  b=(D/'downloads'/part['file']).read_bytes();assert len(b)==part['bytes'];assert hashlib.sha256(b).hexdigest()==part['sha256'];assert len(b)<=10*1024**2;chunks.append(b)
 raw=b''.join(chunks);assert len(raw)==m['bytes'];assert hashlib.sha256(raw).hexdigest()==m['sha256']
 if name=='offline':
  s=raw.decode();assert '<script src=' not in s and '<link rel="stylesheet"' not in s;assert 'window.LESSON_ASSETS=' in s;assert '2hcl-u2-mao' in s
with zipfile.ZipFile(D/'downloads/mao.pptx') as z:
 slides=[n for n in z.namelist() if re.fullmatch(r'ppt/slides/slide\d+.xml',n)];assert len(slides)==53
 for n in slides:
  s=z.read(n).decode();assert '<a:t>' in s;assert all(int(a)>=3000 for a in re.findall(r'\bsz="(\d+)"',s))
with zipfile.ZipFile(D/'downloads/teacher-guide.docx') as z:assert 'word/document.xml' in z.namelist()
assert len(list((D/'slides').glob('*.png')))==53
L=json.loads((R/'tools/mao/lesson.json').read_text());assert len(L['paragraphs'])==12 and len(L['tasks'])==17
for x,y,w,h in L['panelRects']:assert min(x,y,w,h)>0 and x+w<=1024 and y+h<=1536
for i in range(1,5):assert (D/f'assets/comic{i}.png').read_bytes()==(R.parent/f'upload/猫-{i}.png').read_bytes()
prior=subprocess.check_output(['git','show','HEAD:index.html'],cwd=R,text=True);current=(R/'index.html').read_text()
def data(s):return json.loads(re.search(r'const DATA=(.*?);\n',s)[1])
a,b=data(prior),data(current);units=b['2']['texts'];new=next(u for u in units if u['title']=='单元二');assert new['items'][0]['url']=='du/textbook/2hcl/unit2/mao/index.html';units.remove(new);assert a==b
print('PASS: local links, 53 native-text PPT slides (>=30pt), 53 projector images, DOCX, original comics, checked multipart offline/ZIP downloads, isolated homepage insertion.')
