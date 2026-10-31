from pathlib import Path
import shutil,json
R=Path.cwd();OLD=R/'output/handoff/テーブルデータ拡張_文献特徴量追加_20261024';B=R/'output/handoff/テーブルデータ拡張_ROS比較_20261026';T=R/'tmp/ros_comparison_20261026';E=R/'output/experiments/minority_ratios_20261023'
shutil.copytree(OLD,B,dirs_exist_ok=True)
p=B/'資料/テーブルデータにおけるデータ拡張_文献と特徴量_完成版.pptx'
if p.exists():shutil.move(str(p),str(B/'資料/旧版'/p.name))
for f in (B/'資料/スライド画像').glob('slide-*.png'):f.unlink()
for f in T.glob('slide-*.png'):shutil.copy2(f,B/'資料/スライド画像'/f.name)
D=B/'output/experiments/minority_ratios_20261023'
for name in ['ros_recheck.csv','ros_audit.json','augmentation_vs_ros.csv']:shutil.copy2(E/'results'/name,D/'results'/name)
shutil.copy2(T/'recheck_ros.py',D/'recheck_ros.py');shutil.copy2(E/'ROS比較の説明.md',D/'ROS比較の説明.md');shutil.copy2(E/'ROS比較の説明.md',B/'ROS比較の説明.md')
s=(T/'build.mjs').read_text().replace("import {pathToFileURL} from 'node:url';","import {pathToFileURL,fileURLToPath} from 'node:url';").replace("const ROOT='/Users/kouta/Github/data augumation/Data-Augumation';","const ROOT=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');").replace("const DIR=ROOT+'/tmp/ros_comparison_20261026';","const DIR=ROOT+'/presentation_source/build_out';\nawait fs.mkdir(DIR,{recursive:true});").replace("const SKILL='/Users/kouta/.codex/plugins/cache/openai-primary-runtime/presentations/26.1025.11240/skills/presentations';","const SKILL=process.env.PRESENTATIONS_SKILL_DIR;\nif(!SKILL)throw new Error('PRESENTATIONS_SKILL_DIR を移行先の presentations スキルの場所に設定してください。');").replace("const F='Hiragino Sans';","const F=process.env.SLIDE_FONT_FAMILY||'Hiragino Sans';")
(B/'presentation_source/build.mjs').write_text(s)
for name in ['manifest.json','chart-slides.json']:shutil.copy2(T/name,B/'presentation_source'/name)
p=B/'presentation_source/finalize.mjs';s=p.read_text().replace('requiredNativeChartOwnerSlides:[31]','requiredNativeChartOwnerSlides:[35]');p.write_text(s)
for name in ['AGENTS.md','README_最初に読んでください.md','引き継ぎ説明.md','レイアウト参照の状態.md','presentation_source/README.md']:
 p=B/name;s=p.read_text().replace('テーブルデータにおけるデータ拡張_文献と特徴量_完成版.pptx','テーブルデータにおけるデータ拡張_ROS比較_完成版.pptx').replace('40枚','44枚');p.write_text(s)
p=B/'引き継ぎ説明.md';s=p.read_text()+'''
## 2026-10-26 ROS比較の明示

ユーザーの希望：６手法に加えて単純複製のオーバーサンプリングを比較し、新しい行を生成する追加効果を見たい。

従来のランダム複製（内部ID duplicate）はすでにROSの操作です。名称を「ROS（単純複製）」に統一し、ROSの説明１枚と６生成法−ROSの差３枚を追加。絶対性能表・電力網の折れ線・品質表にもROSを明示。計44枚、グラフの所有スライドは35。３データ、少数10/20/30%、５seed、２分類器の条件は維持。

保存済みの45条件で追加行が元の少数訓練行と完全一致し1:1になることを確認し、90件の分類学習・評価を再実行。６評価指標が元のduplicate結果と1e-12以内で一致。GANなどの再学習は不要なので行っていません。新たな10番目の手法としてROSを二重に数えないでください。

recheck_ros.pyが再確認用。結果はros_recheck.csv、監査はros_audit.json、対応seedでの生成法−ROSの差はaugmentation_vs_ros.csv。ROS比較の説明.mdに平均差±標本SDを掲載。主資料の差表は平均のみで、小差の有意性は主張しません。

ROSは広義のデータ拡張・オーバーサンプリングの一種です。ここでは少数行の学習頻度を増やす効果と、新しい特徴ベクトルを生成する効果を切り分けて説明します。
''';p.write_text(s)
p=B/'AGENTS.md';p.write_text(p.read_text()+'\nROS比較を明示済み。内部ID duplicate=ROSで同じ方式。ROSを別の10番目の方式として二重計上しないこと。ROS比較の説明.mdも参照。\n')
p=B/'文献一覧と実装の対応.md';p.write_text(p.read_text()+'''\n## [8] 単純複製によるROS\n\nim​​balanced-learn. **RandomOverSampler.** 公式文書、2026-10-26確認。\n\nhttps://imbalanced-learn.org/stable/references/generated/imblearn.over_sampling.RandomOverSampler.html\n\n少数行のランダムな復元抽出。今回の既存duplicateはノイズなしの同じ操作で、NumPyで実装。公式クラスと同一乱数列の実装再現とは主張しない。ROSも広義にはデータ拡張であり、SMOTEなどもオーバーサンプリング手法に含む。\n''')
p=D/'README.md';p.write_text(p.read_text().replace('|複製|','|ROS（単純複製）|')+'\n2026-10-26：duplicateはROSの操作。ROS比較の説明.mdに６生成法との差、ros_recheck.csvに90件の再評価を保存。元の1350件の評価と、この90件の再現確認を独立な1440件の実験条件として集計しないこと。\n')
p=B/'README_最初に読んでください.md';p.write_text(p.read_text()+'\n最新の追加点：ROS（単純複製）との比較。「ROS比較の説明.md」に、既存のランダム複製との関係、再確認結果、６生成法からの性能差を記載。\n')
print('Prepared handoff folder')
