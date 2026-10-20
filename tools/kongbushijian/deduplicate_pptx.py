from pathlib import Path
import zipfile,hashlib,posixpath,xml.etree.ElementTree as ET
src=Path('ppt-build/candidate.pptx');dst=Path('ppt-build/candidate-dedup.pptx');ns='http://schemas.openxmlformats.org/package/2006/relationships';ET.register_namespace('',ns)
with zipfile.ZipFile(src)as z:
 byhash={};replace={}
 for n in z.namelist():
  if n.startswith('ppt/media/'):
   raw=z.read(n);h=hashlib.sha256(raw).hexdigest()
   if h in byhash:replace[n]=byhash[h]
   else:byhash[h]=n
 with zipfile.ZipFile(dst,'w',zipfile.ZIP_DEFLATED)as o:
  for i in z.infolist():
   if i.filename in replace:continue
   data=z.read(i.filename)
   if i.filename.endswith('.rels'):
    tree=ET.fromstring(data);changed=False
    owner=posixpath.dirname(posixpath.dirname(i.filename))
    for rel in tree:
     target=rel.get('Target','');absolute=posixpath.normpath(posixpath.join(owner,target)).lstrip('/')
     if absolute in replace:rel.set('Target',posixpath.relpath(replace[absolute],owner));changed=True
    if changed:data=ET.tostring(tree,encoding='utf-8',xml_declaration=True)
   o.writestr(i,data)
 print({'duplicate_media_removed':len(replace),'before':src.stat().st_size,'after':dst.stat().st_size})
with zipfile.ZipFile(src)as a,zipfile.ZipFile(dst)as b:
 for n in a.namelist():
  if n.startswith('ppt/slides/slide')and n.endswith('.xml'):assert a.read(n)==b.read(n)
 for n in b.namelist():
  if n.startswith('ppt/media/'):assert a.read(n)==b.read(n)
 print('Slide content and retained source-image bytes unchanged.')
