from pathlib import Path
import json,hashlib
R=Path('/workspace/scratch/6e755f6b886c');repo=R/'huawentong-home';O=repo/'du/textbook/2hcl/unit6/xinjiapo-yu-shijie'
for name,prefix in [('singapore-world.pptx','pptx'),('offline-learning.html','offline')]:
 data=(O/'downloads'/name).read_bytes();parts=[]
 for i,start in enumerate(range(0,len(data),6*1024*1024),1):
  b=data[start:start+6*1024*1024];fn=f'{prefix}-part-{i:02}.bin';(O/'downloads'/fn).write_bytes(b);parts.append(dict(file=fn,bytes=len(b),sha256=hashlib.sha256(b).hexdigest()))
 (O/'downloads'/f'{prefix}-manifest.json').write_text(json.dumps(dict(filename=name,bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),parts=parts),indent=2))
s=(O/'teacher.html').read_text().replace('<a class="btn" href="downloads/singapore-world.pptx" download>可编辑 PPT</a>','<button id="downloadPpt">可编辑 PPT</button>').replace('<a class="btn" href="downloads/offline-learning.html" download>离线互动学习单</a>','<button id="downloadOffline">离线互动学习单</button>');(O/'teacher.html').write_text(s)
s=(O/'pack.js').read_text();s=s.replace("document.getElementById('downloadPackage').onclick=async function()", "for(const [id,manifestName]of [['downloadPackage','package'],['downloadPpt','pptx'],['downloadOffline','offline']])document.getElementById(id).onclick=async function()").replace("fetch('downloads/package-manifest.json')","fetch('downloads/'+manifestName+'-manifest.json')").replace("{type:'application/zip'}","{type:manifestName==='offline'?'text/html;charset=utf-8':manifestName==='pptx'?'application/vnd.openxmlformats-officedocument.presentationml.presentation':'application/zip'}").replace('完整配套已准备好，请保存。','下载文件已准备好，请保存。');(O/'pack.js').write_text(s)
(O/'.gitignore').write_text('/downloads/singapore-world.pptx\n/downloads/offline-learning.html\n')
p=repo/'docs/xinjiapo-yu-shijie-unit6.md';p.write_text(p.read_text()+'\nPPT与独立HTML也提供分块合并下载，避免上传通道体积限制；实际下载后仍分别为单个.pptx及.html文件。\n')
m=[]
files=[repo/'index.html',p]+[f for f in O.rglob('*') if f.is_file() and f.name not in ['singapore-world.pptx','offline-learning.html']]
for f in files:
 b=f.read_bytes();m.append(dict(path=f.relative_to(repo).as_posix(),bytes=len(b),sha=hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()))
(R/'build/upload-files.json').write_text(json.dumps(m));print(json.dumps({'files':len(m),'totalBytes':sum(f['bytes'] for f in m)}))
