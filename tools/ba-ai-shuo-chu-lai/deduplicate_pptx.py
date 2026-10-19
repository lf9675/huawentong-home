"""Losslessly share identical embedded images; all text, positions and crops stay native."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import hashlib, posixpath, sys
from lxml import etree
path=Path(sys.argv[1]);temp=path.with_suffix('.dedup.pptx')
with ZipFile(path) as z:
    canonical={};duplicates={}
    for n in z.namelist():
        if n.startswith('ppt/media/'):
            sha=hashlib.sha256(z.read(n)).hexdigest()
            if sha in canonical:duplicates[n]=canonical[sha]
            else:canonical[sha]=n
    with ZipFile(temp,'w',ZIP_DEFLATED,compresslevel=6) as out:
        for info in z.infolist():
            if info.filename in duplicates:continue
            data=z.read(info.filename)
            if info.filename.endswith('.rels'):
                doc=etree.fromstring(data);base=posixpath.dirname(posixpath.dirname(info.filename))
                for rel in doc:
                    if rel.get('TargetMode')=='External':continue
                    target=posixpath.normpath(posixpath.join(base,rel.get('Target',''))).lstrip('/')
                    if target in duplicates:rel.set('Target',posixpath.relpath(duplicates[target],base))
                data=etree.tostring(doc,xml_declaration=True,encoding='UTF-8',standalone=True)
            out.writestr(info,data)
temp.replace(path)
print(f'Deduplicated {len(duplicates)} identical images; {path.stat().st_size} bytes')
