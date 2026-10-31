from pathlib import Path
import hashlib,json
root=Path(__file__).resolve().parent
manifest=json.loads((root/'ファイル一覧_SHA256.json').read_text(encoding='utf-8'))
errors=[]
for item in manifest['files']:
 f=root/item['path']
 if not f.is_file() or hashlib.sha256(f.read_bytes()).hexdigest()!=item['sha256']:errors.append(item['path'])
if errors:raise SystemExit('MISMATCH: '+str(errors))
print('OK:',len(manifest['files']),'files')
