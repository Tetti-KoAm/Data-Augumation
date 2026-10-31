from pathlib import Path
import json,hashlib,zipfile,csv
R=Path.cwd();B=R/'output/handoff/テーブルデータ拡張_ROS比較_20261026';T=R/'tmp/ros_comparison_20261026';old=R/'output/handoff/テーブルデータ拡張_文献特徴量追加_20261024'
v=json.loads((T/'validation-ros-final.json').read_text());assert v['packageIntegrity']['status']=='pass' and not v['presentationLayout']['warnings'],v['presentationLayout']['warnings']
# Preserve previous experiments; ROS re-evaluation is stored separately.
for f in (old/'output/experiments/minority_ratios_20261023/results').rglob('*'):
 if f.is_file():assert hashlib.sha256(f.read_bytes()).digest()==hashlib.sha256((B/f.relative_to(old)).read_bytes()).digest(),str(f)
E=B/'output/experiments/minority_ratios_20261023/results'
assert json.loads((E/'ros_audit.json').read_text())['classifier_rechecks']==90
assert len(list(csv.DictReader((E/'ros_recheck.csv').open())))==90
assert len(list(csv.DictReader((E/'augmentation_vs_ros.csv').open())))==108
assert len(list((B/'資料/スライド画像').glob('slide-*.png')))==44
p=B/'資料/テーブルデータにおけるデータ拡張_ROS比較版.pptx'
if p.exists():p.unlink()
for p in B.rglob('*.md'):
 s=p.read_text().replace('所有スライドは31','所有スライドは35').replace('グラフの所有スライドは31','グラフの所有スライドは35');p.write_text(s)
files=[dict(path=str(f.relative_to(B)),bytes=f.stat().st_size,sha256=hashlib.sha256(f.read_bytes()).hexdigest()) for f in sorted(B.rglob('*')) if f.is_file() and f.name!='ファイル一覧_SHA256.json']
(B/'ファイル一覧_SHA256.json').write_text(json.dumps(dict(files=files),ensure_ascii=False,indent=2))
archive=B.with_suffix('.zip')
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
 for f in sorted(B.rglob('*')):
  if f.is_file():z.write(f,str(Path(B.name)/f.relative_to(B)))
with zipfile.ZipFile(archive) as z:assert z.testzip() is None
print(json.dumps(dict(archive=str(archive),bytes=archive.stat().st_size,files=len(files)+1,ros_rechecks=90,delta_comparisons=108),ensure_ascii=False))
