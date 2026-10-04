from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
from lxml import etree as E
import re,copy,json
root=Path(__file__).parent;p=root/'candidate.pptx'
A='http://schemas.openxmlformats.org/drawingml/2006/main'
# Native editable PowerPoint text runs: conventional subscript and exponent positioning.
pat=re.compile(r'_(ν,R|M\|O|MO|OO|MM|OM|R|ν|d|M|O)\b|\^\(([^()]*)\)')
changed=[]
with ZipFile(p) as z:parts={n:z.read(n) for n in z.namelist()}
for name in parts:
 if not re.match(r'ppt/slides/slide1\d{2}\.xml$',name):continue
 doc=E.fromstring(parts[name]);count=0
 for run in list(doc.findall('.//{'+A+'}r')):
  text=run.find('{'+A+'}t')
  if text is None or not pat.search(text.text or ''):continue
  original=text.text;parent=run.getparent();index=parent.index(run);style=run.find('{'+A+'}rPr');previous=0;newruns=[]
  def create(value,baseline=None):
   r=E.Element('{'+A+'}r');rp=copy.deepcopy(style) if style is not None else E.Element('{'+A+'}rPr')
   if baseline is not None:
    rp.set('baseline',str(baseline))
    if rp.get('sz'):rp.set('sz',str(round(int(rp.get('sz'))*.72)))
   r.append(rp);t=E.SubElement(r,'{'+A+'}t');t.text=value;t.set('{http://www.w3.org/XML/1998/namespace}space','preserve');return r
  for m in pat.finditer(original):
   if m.start()>previous:newruns.append(create(original[previous:m.start()]))
   newruns.append(create(m.group(1) or m.group(2),-25000 if m.group(1) else 30000));previous=m.end()
  if previous<len(original):newruns.append(create(original[previous:]))
  parent.remove(run)
  for k,r in enumerate(newruns):parent.insert(index+k,r)
  count+=1
 if count:
  parts[name]=E.tostring(doc,xml_declaration=True,encoding='UTF-8',standalone=True);changed.append({'part':name,'runs':count})
with ZipFile(p,'w',ZIP_DEFLATED) as z:
 for n,data in parts.items():z.writestr(n,data)
(root/'math_typesetting.json').write_text(json.dumps(changed,indent=2));print('native math runs typeset',sum(x['runs'] for x in changed))
