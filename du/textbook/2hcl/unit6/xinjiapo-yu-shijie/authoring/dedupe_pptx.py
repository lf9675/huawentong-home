import zipfile,hashlib,sys,pathlib,posixpath,xml.etree.ElementTree as E
p=pathlib.Path(sys.argv[1]);z=zipfile.ZipFile(p);d={n:z.read(n) for n in z.namelist()};seen={};ren={}
for n,b in list(d.items()):
 if n.startswith('ppt/media/'):
  key=hashlib.sha256(b).digest()
  if key in seen:ren[n]=seen[key];del d[n]
  else:seen[key]=n
ns='{http://schemas.openxmlformats.org/package/2006/relationships}'
for n,b in list(d.items()):
 if not n.endswith('.rels'):continue
 tree=E.fromstring(b);base=posixpath.dirname(posixpath.dirname(n));changed=False
 for el in tree:
  target=el.get('Target','');resolved=posixpath.normpath(posixpath.join(base,target)).lstrip('/')
  if resolved in ren:el.set('Target',posixpath.relpath(ren[resolved],base));changed=True
 if changed:
  E.register_namespace('',ns[1:-1]);d[n]=E.tostring(tree,encoding='utf-8',xml_declaration=True)
# Remove duplicate-media content-type overrides if any.
ct=E.fromstring(d['[Content_Types].xml'])
for el in list(ct):
 if el.get('PartName','').lstrip('/') in ren:ct.remove(el)
E.register_namespace('','http://schemas.openxmlformats.org/package/2006/content-types')
d['[Content_Types].xml']=E.tostring(ct,encoding='utf-8',xml_declaration=True)
z.close()
with zipfile.ZipFile(p,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as out:
 for n,b in d.items():out.writestr(n,b)
print('deduplicated',len(ren),'identical media;',p.stat().st_size,'bytes')
