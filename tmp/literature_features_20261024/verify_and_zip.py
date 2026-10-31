from pathlib import Path
import json,hashlib,zipfile,ast
from lxml import etree
R=Path.cwd();B=R/'output/handoff/テーブルデータ拡張_文献特徴量追加_20261024';old=R/'output/handoff/テーブルデータ拡張_引き継ぎ_20261024';T=R/'tmp/literature_features_20261024'
report=json.loads((T/'validation-literature-complete.json').read_text());assert report['packageIntegrity']['status']=='pass' and not report['presentationLayout']['warnings']
# Check that all previously generated experimental evidence is unchanged.
oldresults=old/'output/experiments/minority_ratios_20261023/results'
for f in oldresults.rglob('*'):
 if f.is_file():assert hashlib.sha256(f.read_bytes()).digest()==hashlib.sha256((B/f.relative_to(old)).read_bytes()).digest(),str(f)
for f in (B/'output/experiments/minority_ratios_20261023').glob('*.py'):ast.parse(f.read_text())
pptx=B/'資料/テーブルデータにおけるデータ拡張_文献と特徴量_完成版.pptx'
n={'a':'http://schemas.openxmlformats.org/drawingml/2006/main'}
with zipfile.ZipFile(pptx) as z:
 slides=[a for a in z.namelist() if a.startswith('ppt/slides/slide') and a.endswith('.xml')];assert len(slides)==40
 for i,ref in [(6,'[1]'),(7,'[2]'),(8,'[3]'),(9,'[4]'),(10,'[5]'),(11,'[6]')]:
  txt=''.join(etree.fromstring(z.read(f'ppt/slides/slide{i}.xml')).xpath('//a:t/text()',namespaces=n));assert ref in txt
 assert '16734' in (B/'output/experiments/minority_ratios_20261023/results/feature_examples.json').read_text()
files=[dict(path=str(f.relative_to(B)),bytes=f.stat().st_size,sha256=hashlib.sha256(f.read_bytes()).hexdigest()) for f in sorted(B.rglob('*')) if f.is_file() and f.name!='ファイル一覧_SHA256.json']
(B/'ファイル一覧_SHA256.json').write_text(json.dumps(dict(files=files),ensure_ascii=False,indent=2))
archive=B.with_suffix('.zip')
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
 for f in sorted(B.rglob('*')):
  if f.is_file():z.write(f,str(Path(B.name)/f.relative_to(B)))
with zipfile.ZipFile(archive) as z:assert z.testzip() is None
print(json.dumps(dict(pptx=str(pptx),archive=str(archive),files=len(files)+1,zip_bytes=archive.stat().st_size,experiment_evidence_unchanged=True),ensure_ascii=False))
