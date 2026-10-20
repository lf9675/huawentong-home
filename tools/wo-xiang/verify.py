"""Check source preservation, published resource completeness and package integrity."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
from xml.etree import ElementTree as ET
import hashlib, json, re, subprocess, zipfile
R=Path(__file__).resolve().parents[2]
D=R/'du/textbook/2hcl/unit1/wo-xiang-dui-ni-shuo'
sha=lambda b:hashlib.sha256(b).hexdigest()
class Links(HTMLParser):
    def __init__(self): super().__init__();self.links=[]
    def handle_starttag(self,tag,attrs):
        for k,v in attrs:
            if k in ('href','src') and v:self.links.append(v)
for p in D.glob('*.html'):
    doc=Links();doc.feed(p.read_text())
    for u in doc.links:
        q=urlsplit(u)
        if q.scheme or q.netloc or not q.path:continue
        assert (p.parent/unquote(q.path)).resolve().exists(),(p.name,u)
for i in range(1,4):
    original=R.parent/'upload'/f'我想对你说-{i}(2).png'
    if original.exists():assert sha(original.read_bytes())==sha((D/f'assets/comic{i}.png').read_bytes())
for name in ['package','offline']:
    m=json.loads((D/f'downloads/{name}-manifest.json').read_text())
    raw=b''
    for part in m['parts']:
        b=(D/'downloads'/part['file']).read_bytes()
        assert len(b)==part['bytes'] and sha(b)==part['sha256']
        raw+=b
    assert len(raw)==m['bytes'] and sha(raw)==m['sha256']
    if name=='offline':
        page=raw.decode();assert '<script src=' not in page
        assert 'window.LESSON_ASSETS=' in page and 'answerTable' in page
        assert 'data:font/woff2;base64,' in page
    else:
        import io
        with zipfile.ZipFile(io.BytesIO(raw)) as z:
            assert z.testzip() is None
            assert len([x for x in z.namelist() if x.startswith('slides/')])==28
            assert z.read('可编辑课件.pptx')==(D/'downloads/wo-xiang.pptx').read_bytes()
            assert z.read('教师流程与答案.docx')==(D/'downloads/teacher-guide.docx').read_bytes()
for p in D.rglob('*'):
    if p.is_file():assert p.stat().st_size<25*1024**2,(p,p.stat().st_size)
ns={'a':'http://schemas.openxmlformats.org/drawingml/2006/main'}
with zipfile.ZipFile(D/'downloads/wo-xiang.pptx') as z:
    paths=[p for p in z.namelist() if re.fullmatch(r'ppt/slides/slide\d+.xml',p)]
    assert len(paths)==28
    sizes=[];texts=[]
    for p in paths:
        root=ET.fromstring(z.read(p));sizes.extend(int(n.get('sz')) for n in root.iter() if n.get('sz'))
        texts.extend(n.text or '' for n in root.findall('.//a:t',ns))
    assert min(sizes)>=2800,min(sizes)
    assert ET.fromstring(z.read('ppt/slides/slide18.xml')).find('.//a:tbl',ns) is not None
    assert '我想对你说' in texts
with zipfile.ZipFile(D/'downloads/teacher-guide.docx') as z:assert z.testzip() is None
data=lambda s:json.loads(re.search(r'const DATA=(.*?);\n',s)[1])
before=data(subprocess.check_output(['git','show','53082d191c59972e118776f3ed1924a79f9c67d0:index.html'],cwd=R,text=True))
after=data((R/'index.html').read_text())
unit=next(u for u in after['2']['texts'] if u['title']=='单元一')
assert unit['items'][0]['url']=='du/textbook/2hcl/unit1/wo-xiang-dui-ni-shuo/index.html'
assert unit['items'][0]['title']=='生活空间 · 我想对你说'
unit['items'].pop(0);assert after==before,'Unrelated homepage entries changed'
print('PASS: all local resource links, original comics, offline/ZIP checksums and contents, 25 MiB asset limit, 28 editable slides (minimum 30 pt), native table, DOCX archive, unit-one first entry and unrelated homepage data.')
