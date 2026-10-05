from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile
import subprocess,json,hashlib
project=Path.cwd();zpath=project/'output/handoff/コピュラ研究_引き継ぎ_20261004.zip';py=project/'tmp/seminar_20261005/experiment_env/bin/python'
with TemporaryDirectory(prefix='copula-handoff-',dir='/private/tmp') as tmp:
 with ZipFile(zpath) as z:z.extractall(tmp)
 root=Path(tmp)/'コピュラ研究_引き継ぎ_20261004'
 manifest=json.loads((root/'ファイル一覧とSHA256.json').read_text())
 for f in manifest['files']:assert hashlib.sha256((root/f['path']).read_bytes()).hexdigest()==f['sha256']
 p=root/'output/experiments/dependence_comparison/run_dependence_comparison.py'
 code="from pathlib import Path\np=Path("+repr(str(p))+ ")\nns={'__file__':str(p)}\nexec(compile(p.read_text().split('begin=time.time();runs=[]')[0],str(p),'exec'),ns)\nx,y=ns['make_data'](11,.9,'mean')\nq=ns['quality'](x[:700],x[800:],.9,'mean',11)\nassert all(q[m]['observed_unchanged'] for m in ['column_shuffle','gaussian_copula'])\nassert ns['project']==p.parents[3]\nprint('Relocated imports and conditional sampling passed.')"
 r=subprocess.run([str(py),'-c',code],cwd=tmp,text=True,capture_output=True)
 assert r.returncode==0,r.stderr;print(r.stdout.strip())
 with ZipFile(root/'参考資料/10.05＿齊藤光汰_元資料.pptx') as a,ZipFile(root/'output/presentations/10.05_ゼミ発表_コピュラ進捗_流れ改善版_本編20枚.pptx') as b:
  for i in range(1,5):assert a.read(f'ppt/slides/slide{i}.xml')==b.read(f'ppt/slides/slide{i}.xml')
 print('Verified',len(manifest['files']),'checksums and unchanged first 4 slides.')
