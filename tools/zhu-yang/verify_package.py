"""Verify release files, native document structure, original art and homepage scope."""
from pathlib import Path
from html.parser import HTMLParser
from io import BytesIO
import hashlib, json, re, zipfile, subprocess

R = Path(__file__).resolve().parents[2]
D = R / 'du/textbook/2hcl/unit2/zhu-yang-ye-sheng-dong-wu'

class Links(HTMLParser):
    def handle_starttag(self, tag, attrs):
        for k, v in attrs:
            if k in ('href', 'src') and v and not v.startswith(('http:', 'https:', 'data:', '#', 'blob:')):
                p = (self.file.parent / v.split('?')[0].split('#')[0]).resolve()
                assert p.is_file(), (self.file.name, v)

for f in D.glob('*.html'):
    parser = Links(); parser.file = f; parser.feed(f.read_text())
for f in [*D.glob('*.js'), R/'du/textbook/shared/lesson-v1/app.js', R/'du/textbook/shared/lesson-v1/catalog.js']:
    subprocess.run(['node', '--check', str(f)], check=True)

for name in ['package', 'offline']:
    m = json.loads((D/f'downloads/{name}-manifest.json').read_text()); chunks = []
    for part in m['parts']:
        b = (D/'downloads'/part['file']).read_bytes()
        assert len(b) == part['bytes'] and len(b) <= 10*1024**2
        assert hashlib.sha256(b).hexdigest() == part['sha256']
        chunks.append(b)
    raw = b''.join(chunks)
    assert len(raw) == m['bytes'] and hashlib.sha256(raw).hexdigest() == m['sha256']
    if name == 'offline':
        s = raw.decode()
        assert '<script src=' not in s and '<link rel="stylesheet"' not in s
        assert 'window.LESSON_ASSETS=' in s and '2hcl-u2-zhu-yang-ye-sheng-dong-wu' in s
        assert 'first_summary' in s and '本段问题' in s
    else:
        with zipfile.ZipFile(BytesIO(raw)) as z:
            assert z.testzip() is None
            assert z.read('可编辑课件.pptx') == (D/'downloads/zhu-yang.pptx').read_bytes()
            assert z.read('教师流程与答案.docx') == (D/'downloads/teacher-guide.docx').read_bytes()
            assert len([n for n in z.namelist() if n.startswith('slides/')]) == 32

with zipfile.ZipFile(D/'downloads/zhu-yang.pptx') as z:
    slides = [n for n in z.namelist() if re.fullmatch(r'ppt/slides/slide\d+.xml', n)]
    assert len(slides) == 32
    for n in slides:
        s = z.read(n).decode()
        assert '<a:t>' in s and all(int(x) >= 3000 for x in re.findall(r'\bsz="(\d+)"', s))
with zipfile.ZipFile(D/'downloads/teacher-guide.docx') as z:
    assert z.testzip() is None and 'word/document.xml' in z.namelist()
assert len(list((D/'slides').glob('*.png'))) == 32
projector = json.loads(re.search(r'const SLIDES=(.*?);let ', (D/'slides.html').read_text())[1])
assert len(projector) == 32
assert projector == json.loads((D/'slides.json').read_text())

lesson = json.loads((R/'tools/zhu-yang/lesson.json').read_text())
assert len(lesson['paragraphs']) == 7 and len(lesson['tasks']) == 8
assert len([t for t in lesson['tasks'] if t.get('summaryRow')]) == 4
assert sum(len(t.get('blanks', [])) for t in lesson['tasks']) == 5
for x, y, w, h in lesson['panelRects']:
    assert min(x, y, w, h) > 0 and x+w <= 1024 and y+h <= 1536
original_hashes = [
    '817708c8f2ba4a4cd874528e56d264d3cfbdd1af2f30005f83473e9875f35018',
    '24fd52fbd0cf132d5e54bd3c5ccd66a04b620af9cc36ca4530c63207b18248be',
    '24fbebee0f71362c068693621ebf34366e940d31243f8a4181cf50bb46593a7f',
]
for i, expected in enumerate(original_hashes, 1):
    assert hashlib.sha256((D/f'assets/comic{i}.png').read_bytes()).hexdigest() == expected
prior = subprocess.check_output(['git', 'show', '95be7342f7a2971fc7ab355b02f5b2ea9cae3432:index.html'], cwd=R, text=True)
def data(s): return json.loads(re.search(r'const DATA=(.*?);\n', s)[1])
a, b = data(prior), data((R/'index.html').read_text())
unit = next(u for u in b['2']['texts'] if u['title'] == '单元二')
assert unit['items'][0]['url'] == 'du/textbook/2hcl/unit2/zhu-yang-ye-sheng-dong-wu/index.html'
unit['items'].pop(0)
assert a == b
print('PASS: relative links, JavaScript syntax, 32 native-text slides >=30pt, matching projector, DOCX, unchanged original comics, full ZIP/offline chunk integrity, isolated homepage addition.')
