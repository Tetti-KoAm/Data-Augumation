from pathlib import Path
import shutil,json,hashlib,zipfile,ast
R=Path.cwd();B=R/'output/handoff/テーブルデータ拡張_引き継ぎ_20261024';S=B/'presentation_source';P=B/'資料';ref=B/'レイアウト参照';ref.mkdir(exist_ok=True)
shutil.copy2(R/'tmp/layout_reference_20261024/reference.pdf',ref/'10.05_齊藤光汰.pdf')
old=P/'旧版';old.mkdir(exist_ok=True);shutil.move(str(P/'テーブルデータ拡張_内容確定版.pptx'),str(old/'テーブルデータ拡張_旧レイアウト.pptx'))
f=P/'テーブルデータにおけるデータ拡張_参照レイアウト版.pptx'
if f.exists():f.unlink()
for f in (R/'tmp/layout_reference_20261024').glob('slide-*.png'):shutil.copy2(f,P/'スライド画像'/f.name)
s=(R/'tmp/layout_reference_20261024/build.mjs').read_text().replace("import {pathToFileURL} from 'node:url';","import {pathToFileURL,fileURLToPath} from 'node:url';")
s=s.replace("const ROOT='/Users/kouta/Github/data augumation/Data-Augumation';", "const ROOT=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');")
s=s.replace("const DIR=ROOT+'/tmp/layout_reference_20261024';", "const DIR=ROOT+'/presentation_source/build_out';\nawait fs.mkdir(DIR,{recursive:true});")
s=s.replace("const SKILL='/Users/kouta/.codex/plugins/cache/openai-primary-runtime/presentations/26.1022.11436/skills/presentations';", "const SKILL=process.env.PRESENTATIONS_SKILL_DIR;\nif(!SKILL)throw new Error('PRESENTATIONS_SKILL_DIR を移行先の presentations スキルの場所に設定してください。');")
s=s.replace("const F='Hiragino Sans';", "const F=process.env.SLIDE_FONT_FAMILY||'Hiragino Sans';")
(S/'build.mjs').write_text(s)
for name in ['manifest.json','chart-slides.json']:shutil.copy2(R/'tmp/layout_reference_20261024'/name,S/name)
(S/'finalize.mjs').write_text('''import path from 'node:path';
import fs from 'node:fs/promises';
import {fileURLToPath,pathToFileURL} from 'node:url';
const ROOT=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const S=process.env.PRESENTATIONS_SKILL_DIR;
if(!S||!process.env.RUNTIME_PYTHON)throw new Error('PRESENTATIONS_SKILL_DIR と RUNTIME_PYTHON を設定してください。');
process.env.RUNTIME_NODE ||= process.execPath;
const D=ROOT+'/presentation_source/build_out';
const {finalizePresentation}=await import(pathToFileURL(path.join(S,'container_tools/artifact_tool_utils.mjs')).href);
const suffix=new Date().toISOString().replace(/[:.]/g,'-');
const result=await finalizePresentation({workspaceDir:ROOT,candidatePath:D+'/candidate.pptx',finalPath:ROOT+'/資料/テーブルデータ拡張_更新_'+suffix+'.pptx',pythonExecutable:process.env.RUNTIME_PYTHON,integrityValidatorPath:S+'/container_tools/inspect_presentation_package_integrity.py',layoutValidatorPath:S+'/container_tools/inspect_presentation_layout_geometry.py',layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-bullet-geometry','--validate-heading-fit'],fontPolicy:{basis:'design',families:[process.env.SLIDE_FONT_FAMILY||'Hiragino Sans']},requiredNativeChartOwnerSlides:[24],materializeLiteralChartWorkbooks:true,nativeChartTargetApplication:'powerpoint',verifyArtifactToolImport:true,receiptPath:D+'/validation-'+suffix+'.json'});
console.log(JSON.stringify(result));
''')
p=S/'README.md';t=p.read_text();t=t.replace('31枚の内容確定版の編集元','31枚の参照レイアウト反映版の編集元');t+='\nfinalize.mjsは検証・完成ファイル出力用。移行先スキルの実装説明に従い、RUNTIME_PYTHON、RUNTIME_NODE_MODULES、RUNTIME_BIN_DIRなどの実行環境も設定してください。Node本体やライブラリを手作業でコピーする必要はありません。\n';p.write_text(t)
(B/'レイアウト参照の状態.md').write_text('''# レイアウト参照の反映状況

2026-10-24にユーザー指定PDFの全22ページを確認し、31枚の資料にレイアウトを反映済みです。最新は「資料/テーブルデータにおけるデータ拡張_参照レイアウト版_完成.pptx」です。

反映：白背景、中央揃えの大きい見出し、見出し下の細い横線、薄緑の表見出しと緑文字、白・薄灰の表行、下部の薄緑要点帯、左下の節名と右下ページ番号。表紙もPDFに合わせた中央配置。実験条件・結果は維持しています。

PDFは見た目の参考としてのみ使用しました。PDFにある半教師あり設定や別データ・結果は今回の実験に転用していません。

参照は16:9、PDFのページサイズ960×540pt。新資料も16:9、編集キャンバス1280×720です。PDFにはMS GothicとYuGothic-Lightが含まれますが、今回の出力環境ではHiragino Sansを使っています。完全に同一フォントではありません。PDFは画像として貼らず、テキスト・表・グラフを編集可能なPowerPointとして再構築しています。

参照PDFは「レイアウト参照/10.05_齊藤光汰.pdf」に同梱。元PDFには一部ページ番号の並びが前後する箇所がありますが、新資料は1〜31で連番です。

今後修正する場合は、この反映版とpresentation_source/build.mjsを使ってください。資料/旧版は変更前の内容確定版で、通常は参照不要です。
''')
p=B/'引き継ぎ説明.md';t=p.read_text().replace('追加のレイアウト反映版があればそちらを優先。','最新は参照レイアウト版_完成.pptx。旧版は資料/旧版に保存。');t+='\n## 2026-10-24 完了追記\n\n指定PDFの全ページ確認とレイアウト反映を完了。最新PowerPoint・31枚PNG・編集元JSを更新済み。実験結果の変更や再学習はしていません。フォルダ内の実験コード・CSV・NPZ・モデルは保存済み結果と同一。次の作業は、ユーザーの追加修正に合わせた内容・見せ方の調整です。\n';p.write_text(t)
p=B/'README_最初に読んでください.md';t=p.read_text().replace('2. 「資料」でPowerPointとスライド画像を確認。','2. 「資料/テーブルデータにおけるデータ拡張_参照レイアウト版_完成.pptx」とスライド画像を確認。');t=t.replace('資料のレイアウトは参照PDFに合わせます。','資料のレイアウトは同梱の参照PDFに合わせて反映済みです。');p.write_text(t)
(B/'AGENTS.md').write_text('''# 作業の引き継ぎ

まず README_最初に読んでください.md、引き継ぎ説明.md、レイアウト参照の状態.md を読んでください。
最新資料は 資料/テーブルデータにおけるデータ拡張_参照レイアウト版_完成.pptx、編集元は presentation_source/build.mjs です。
全件ラベル付きで少数クラス割合10%、20%、30%を比較した条件を維持してください。ラベル付与率の意味ではありません。
既存結果を利用できる変更では再学習は不要です。実験設定を変更する場合は元のresultsを残し別の出力先を使ってください。
''')
# Portable verification command without experiment dependencies.
(B/'verify_bundle.py').write_text('''from pathlib import Path
import hashlib,json
root=Path(__file__).resolve().parent
manifest=json.loads((root/'ファイル一覧_SHA256.json').read_text(encoding='utf-8'))
errors=[]
for item in manifest['files']:
 f=root/item['path']
 if not f.is_file() or hashlib.sha256(f.read_bytes()).hexdigest()!=item['sha256']:errors.append(item['path'])
if errors:raise SystemExit('MISMATCH: '+str(errors))
print('OK:',len(manifest['files']),'files')
''')
for f in [B/'verify_bundle.py',B/'output/experiments/minority_ratios_20261023/run.py',B/'output/experiments/minority_ratios_20261023/summarize.py']:ast.parse(f.read_text())
files=[]
for f in sorted(B.rglob('*')):
 if f.is_file() and f.name!='ファイル一覧_SHA256.json':files.append(dict(path=str(f.relative_to(B)),bytes=f.stat().st_size,sha256=hashlib.sha256(f.read_bytes()).hexdigest()))
(B/'ファイル一覧_SHA256.json').write_text(json.dumps(dict(files=files),ensure_ascii=False,indent=2))
archive=B.with_suffix('.zip')
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
 for f in sorted(B.rglob('*')):
  if f.is_file():z.write(f,str(Path(B.name)/f.relative_to(B)))
with zipfile.ZipFile(archive) as z:assert z.testzip() is None
print(json.dumps(dict(folder=str(B),archive=str(archive),files=len(files)+1,zip_bytes=archive.stat().st_size),ensure_ascii=False))
