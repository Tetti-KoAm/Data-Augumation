"""Preserve source slides 1-4 and all dependencies without reserialization.
Append Artifact Tool-authored slides under a namespaced package path.
"""
from pathlib import Path,PurePosixPath
from zipfile import ZipFile,ZIP_DEFLATED
from lxml import etree as E
import posixpath,hashlib,json
ROOT=Path(__file__).parent
source=Path('/Users/kouta/Library/CloudStorage/OneDrive-個人用/大学院/研究/10.05＿齊藤光汰.pptx')
NS={'p':'http://schemas.openxmlformats.org/presentationml/2006/main','r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships','pr':'http://schemas.openxmlformats.org/package/2006/relationships','ct':'http://schemas.openxmlformats.org/package/2006/content-types'}
with ZipFile(source) as a,ZipFile(ROOT/'new_slides.pptx') as b:
 parts={n:a.read(n) for n in a.namelist()};new={n:b.read(n) for n in b.namelist()}
 mapping={n:'ppt/copula/'+n[4:] for n in new if n.startswith('ppt/') and n not in ['ppt/presentation.xml','ppt/_rels/presentation.xml.rels']}
 for old in list(mapping):
  if old.startswith('ppt/slides/slide') and old.endswith('.xml'):
   i=int(old.rsplit('slide',1)[1][:-4]);mapping[old]=f'ppt/slides/slide{100+i}.xml'
  elif old.startswith('ppt/slides/_rels/slide') and old.endswith('.xml.rels'):
   i=int(old.rsplit('slide',1)[1][:-9]);mapping[old]=f'ppt/slides/_rels/slide{100+i}.xml.rels'
 def ser(root):return E.tostring(root,xml_declaration=True,encoding='UTF-8',standalone=True)
 # Rename all added parts and repair relative links based on source and target owners.
 for old,mapped in mapping.items():
  data=new[old]
  if old.endswith('.rels'):
   root=E.fromstring(data)
   owner=posixpath.join(posixpath.dirname(posixpath.dirname(old)),posixpath.basename(old)[:-5])
   mapped_owner=mapping.get(owner,'ppt/copula/presentation.xml')
   for rel in root:
    if rel.get('TargetMode')=='External':continue
    target=rel.get('Target');absolute=posixpath.normpath(posixpath.join(posixpath.dirname(owner),target)) if not target.startswith('/') else target[1:]
    target_new=mapping.get(absolute)
    if absolute=='ppt/presentation.xml':target_new='ppt/presentation.xml'
    if target_new is None:raise ValueError((old,absolute))
    rel.set('Target',posixpath.relpath(target_new,posixpath.dirname(mapped_owner)))
   data=ser(root)
  parts[mapped]=data
 pres=E.fromstring(parts['ppt/presentation.xml']);rels=E.fromstring(parts['ppt/_rels/presentation.xml.rels']);npres=E.fromstring(new['ppt/presentation.xml']);nrels=E.fromstring(new['ppt/_rels/presentation.xml.rels']);newrel={r.get('Id'):r for r in nrels}
 sids=pres.find('p:sldIdLst',NS)
 for child in list(sids)[4:]:sids.remove(child)
 # Remove presentation links to the discarded source slides; orphan parts don't affect preservation.
 first_ids={c.get('{'+NS['r']+'}id') for c in sids}
 for rel in list(rels):
  if rel.get('Type').endswith('/slide') and rel.get('Id') not in first_ids:rels.remove(rel)
 rid_map={}
 for j,r in enumerate(nrels):
  target=r.get('Target')[1:] if r.get('Target').startswith('/') else posixpath.normpath(posixpath.join('ppt',r.get('Target')))
  if target not in mapping:continue
  rid='rIdCopula'+str(j+1);rid_map[r.get('Id')]=rid
  rel=E.SubElement(rels,'{'+NS['pr']+'}Relationship',Id=rid,Type=r.get('Type'),Target=posixpath.relpath(mapping[target],'ppt'))
 for j,child in enumerate(npres.find('p:sldIdLst',NS)):
  E.SubElement(sids,'{'+NS['p']+'}sldId',id=str(1000+j),attrib={'{'+NS['r']+'}id':rid_map[child.get('{'+NS['r']+'}id')]})
 for tag in ['sldMasterIdLst','notesMasterIdLst']:
  original=pres.find('p:'+tag,NS);nl=npres.find('p:'+tag,NS)
  if nl is None:continue
  if original is None:
   original=E.Element('{'+NS['p']+'}'+tag);pres.insert(1 if tag=='sldMasterIdLst' else 2,original)
  for j,c in enumerate(nl):
   cc=E.fromstring(E.tostring(c));cc.set('{'+NS['r']+'}id',rid_map[c.get('{'+NS['r']+'}id')]);
   if cc.get('id') is not None:cc.set('id',str(2147485000+j))
   original.append(cc)
 # Drop source sections/custom shows that may reference no-longer-listed slides.
 for name in ['custShowLst','extLst']:
  x=pres.find('p:'+name,NS)
  if x is not None:pres.remove(x)
 parts['ppt/presentation.xml']=ser(pres);parts['ppt/_rels/presentation.xml.rels']=ser(rels)
 ct=E.fromstring(parts['[Content_Types].xml']);nct=E.fromstring(new['[Content_Types].xml']);existing={c.get('Extension') for c in ct if c.tag.endswith('Default')}
 for c in nct:
  if c.tag.endswith('Override'):
   old=c.get('PartName')[1:]
   if old in mapping:E.SubElement(ct,c.tag,PartName='/'+mapping[old],ContentType=c.get('ContentType'))
  elif c.get('Extension') not in existing:ct.append(c);existing.add(c.get('Extension'))
 parts['[Content_Types].xml']=ser(ct)
 # Keep only reachable parts to avoid carrying discarded source slide content.
 roots=['_rels/.rels','[Content_Types].xml'];visited=set(roots);queue=['']
 while queue:
  owner=queue.pop();relpath='_rels/.rels' if owner=='' else posixpath.join(posixpath.dirname(owner),'_rels',posixpath.basename(owner)+'.rels')
  if relpath not in parts:continue
  visited.add(relpath)
  for rel in E.fromstring(parts[relpath]):
   if rel.get('TargetMode')=='External':continue
   target=rel.get('Target');absolute=posixpath.normpath(posixpath.join(posixpath.dirname(owner),target)) if not target.startswith('/') else target[1:]
   if absolute not in visited:visited.add(absolute);queue.append(absolute)
 parts={n:v for n,v in parts.items() if n in visited}
 ct=E.fromstring(parts['[Content_Types].xml'])
 for c in list(ct):
  if c.tag.endswith('Override') and c.get('PartName')[1:] not in parts:ct.remove(c)
 parts['[Content_Types].xml']=ser(ct)
 # Exact preservation of slide files and every dependency reachable from them.
 preserved=set();queue=[f'ppt/slides/slide{i}.xml' for i in range(1,5)]
 while queue:
  owner=queue.pop()
  if owner in preserved:continue
  preserved.add(owner);relpath=posixpath.join(posixpath.dirname(owner),'_rels',posixpath.basename(owner)+'.rels')
  if relpath not in a.namelist():continue
  preserved.add(relpath)
  for rel in E.fromstring(a.read(relpath)):
   if rel.get('TargetMode')=='External':continue
   target=posixpath.normpath(posixpath.join(posixpath.dirname(owner),rel.get('Target')))
   if target in a.namelist() and target!='ppt/presentation.xml':queue.append(target)
 for n in preserved:
  assert n in parts and parts[n]==a.read(n),f'Changed original dependency {n}'
 dest=ROOT/'candidate.pptx'
 with ZipFile(dest,'w',ZIP_DEFLATED) as z:
  for n,v in parts.items():z.writestr(n,v)
 (ROOT/'preservation.json').write_text(json.dumps({'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'preserved_first_slides':4,'byte_identical_dependencies':len(preserved),'total_slides':len(sids)},indent=2))
 print('merged',len(sids),'slides; byte-identical original dependencies',len(preserved))
