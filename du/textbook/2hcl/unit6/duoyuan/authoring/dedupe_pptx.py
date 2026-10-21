from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import hashlib,sys,posixpath
from lxml import etree
p=Path(sys.argv[1]);q=p.with_suffix('.deduped.pptx')
with ZipFile(p) as z:
    mapping={};seen={}
    for n in z.namelist():
        if n.startswith('ppt/media/'):
            h=hashlib.sha256(z.read(n)).hexdigest()
            if h in seen:mapping[n]=seen[h]
            else:seen[h]=n
    with ZipFile(q,'w',ZIP_DEFLATED,compresslevel=6) as w:
        for n in z.namelist():
            if n in mapping:continue
            data=z.read(n)
            if n.endswith('.rels'):
                tree=etree.fromstring(data)
                parent=posixpath.dirname(posixpath.dirname(n))
                for r in tree:
                    target=r.get('Target','')
                    actual=posixpath.normpath(posixpath.join(parent,target)).lstrip('/')
                    if actual in mapping:r.set('Target',posixpath.relpath(mapping[actual],parent))
                data=etree.tostring(tree,xml_declaration=True,encoding='UTF-8',standalone=True)
            w.writestr(n,data)
q.replace(p)
print('Deduplicated',len(mapping),'media:',p.stat().st_size)
