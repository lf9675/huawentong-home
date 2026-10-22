import zipfile,hashlib,lxml.etree as E,posixpath
from pathlib import Path
root=Path(__file__).resolve().parents[1]
z=zipfile.ZipFile(root/'build/ppt/candidate.pptx');files={n:z.read(n) for n in z.namelist()};by={};mapping={}
for n,b in files.items():
 if n.startswith('ppt/media/'):
  h=hashlib.sha256(b).hexdigest()
  if h in by:mapping[n]=by[h]
  else:by[h]=n
for n in list(files):
 if n.endswith('.rels'):
  r=E.fromstring(files[n]);changed=False;base=posixpath.dirname(posixpath.dirname(n))
  for el in r:
   full=posixpath.normpath(posixpath.join(base,el.get('Target',''))).lstrip('/')
   if full in mapping:el.set('Target','/'+mapping[full]);changed=True
  if changed:files[n]=E.tostring(r,xml_declaration=True,encoding='UTF-8',standalone=True)
for n in mapping:del files[n]
r=E.fromstring(files['[Content_Types].xml'])
for e in list(r):
 if e.get('PartName','').lstrip('/') in mapping:r.remove(e)
files['[Content_Types].xml']=E.tostring(r,xml_declaration=True,encoding='UTF-8',standalone=True)
with zipfile.ZipFile(root/'build/ppt/deduped.pptx','w',zipfile.ZIP_DEFLATED) as out:
 for n,b in files.items():out.writestr(n,b)
print('deduplicated',len(mapping),'media')
