from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1];O=R/'repo/du/textbook/1hcl/unit3/xingyao-changi';D=O/'downloads';data=(D/'xingyao-changi.pptx').read_bytes();parts=[]
for i,start in enumerate(range(0,len(data),5*1024*1024),1):
 b=data[start:start+5*1024*1024];name=f'pptx-part-{i:02}.bin';(D/name).write_bytes(b);parts.append(dict(url='downloads/'+name,bytes=len(b),sha256=hashlib.sha256(b).hexdigest()))
(D/'pptx-manifest.json').write_text(json.dumps(dict(filename='魅力四射_星耀樟宜.pptx',bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),parts=parts),ensure_ascii=False,indent=2))
(O/'.gitignore').write_text('/downloads/xingyao-changi.pptx\n')
p=O/'teacher.html';p.write_text(p.read_text().replace('<a class="btn" href="downloads/xingyao-changi.pptx" download>可编辑PPT</a>','<button id="downloadPpt">可编辑PPT</button>'))
(O/'pack.js').write_text((R/'build/pack.js').read_text())
