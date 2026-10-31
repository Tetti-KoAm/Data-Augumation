from pathlib import Path
import shutil,json,hashlib,zipfile
R=Path.cwd(); B=R/'output/handoff/テーブルデータ拡張_引き継ぎ_20261024'; E=R/'output/experiments/minority_ratios_20261023'; D=B/'output/experiments/minority_ratios_20261023'
D.mkdir(parents=True,exist_ok=True)
for name in ['run.py','summarize.py','requirements-lock.txt','README.md']:shutil.copy2(E/name,D/name)
shutil.copytree(E/'results',D/'results',dirs_exist_ok=True)
for did in ['545','850','471']:
 src=R/'output/experiments/public_semantics_20261015/data'/did;dst=B/'output/experiments/public_semantics_20261015/data'/did
 shutil.copytree(src,dst,dirs_exist_ok=True)
P=B/'資料';P.mkdir(exist_ok=True)
shutil.copy2(R/'output/presentations/少数クラス割合比較_20261023/テーブルデータにおけるデータ拡張_課題と６手法_少数10_20_30％比較_改訂版.pptx',P/'テーブルデータ拡張_内容確定版.pptx')
S=B/'presentation_source';S.mkdir(exist_ok=True)
s=(R/'tmp/minority_ratios_20261023/build.mjs').read_text()
s=s.replace("import {pathToFileURL} from 'node:url';","import {pathToFileURL,fileURLToPath} from 'node:url';")
s=s.replace("const ROOT='/Users/kouta/Github/data augumation/Data-Augumation';","const ROOT=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');")
s=s.replace("const DIR=ROOT+'/tmp/minority_ratios_20261023';","const DIR=ROOT+'/presentation_source/build_out';\nawait fs.mkdir(DIR,{recursive:true});")
s=s.replace("const SKILL='/Users/kouta/.codex/plugins/cache/openai-primary-runtime/presentations/26.1022.11436/skills/presentations';", "const SKILL=process.env.PRESENTATIONS_SKILL_DIR;\nif(!SKILL)throw new Error('PRESENTATIONS_SKILL_DIR に移行先の presentations スキルのパスを設定してください。');")
s=s.replace("const F='Hiragino Sans';","const F=process.env.SLIDE_FONT_FAMILY||'Hiragino Sans';")
(S/'build.mjs').write_text(s)
for f in ['manifest.json','chart-slides.json']:
 shutil.copy2(R/'tmp/minority_ratios_20261023'/f,S/f)
shutil.copytree(R/'tmp/minority_ratios_20261023',B/'資料/スライド画像',ignore=shutil.ignore_patterns('*'),dirs_exist_ok=True)
for f in (R/'tmp/minority_ratios_20261023').glob('slide-*.png'):shutil.copy2(f,B/'資料/スライド画像'/f.name)
(S/'README.md').write_text('''# スライドの編集元

build.mjs は31枚の内容確定版の編集元です。実験CSVに由来する slide_data.json を読み、PowerPointとPNGを生成します。元PCへの絶対パスは相対パスへ変更しています。完成PPTXは「資料」で直接編集できます。

再生成にはCodexのpresentationsスキルと付属の @oai/artifact-tool ランタイムが必要です。通常のPython実験環境とは別です。依存ランタイムはこのフォルダに含めていません。移行先のCodexでスキルを確認し、PRESENTATIONS_SKILL_DIR、Nodeの実行パス、node_modulesの解決先を設定してください。公開npmから取得できると仮定してインストールしないでください。

- PRESENTATIONS_SKILL_DIR：移行先のpresentationsスキルのフォルダ。
- SLIDE_FONT_FAMILY：利用可能な日本語フォント。省略時Hiragino Sans（Mac）。Windowsではインストール済みの日本語フォントを確認して変更。
- 生成先：presentation_source/build_out/candidate.pptx と各slide-XX.png。
- 生成後はそのPCのpresentationsスキルの手順で検証し、資料フォルダに別名で保存。

レイアウト参照PDFに合わせる修正では、まずPDFを表示し、title/body/tableの座標・フォント・色と余白を確認してこのソースを更新してください。モデルの再学習は不要です。
''')
(B/'README_最初に読んでください.md').write_text('''# 別のパソコンのCodexで続けるためのフォルダ

このフォルダ全体を移動し、Codexの作業フォルダとして開いてください。既存の実験結果は保存済みなので、資料を編集するだけなら再実験は不要です。

1. 「引き継ぎ説明.md」で目的・確定条件・残作業を確認。
2. 「資料」でPowerPointとスライド画像を確認。
3. 実験コード・実験結果は output/experiments/minority_ratios_20261023/。
4. 元データは output/experiments/public_semantics_20261015/data/。
5. スライドの再生成元は presentation_source/build.mjs。

会話履歴はこのフォルダに自動移行されません。移行先Codexに次の文を貼り付けてください。

> README_最初に読んでください.md と 引き継ぎ説明.md を読み、作業を続けてください。ゼミ資料「テーブルデータにおけるデータ拡張」です。課題の定義、６手法の説明、公開データによる実験比較の順に構成します。全件ラベル付きで、少数クラス割合10％・20％・30％を比較済みです。資料のレイアウトは参照PDFに合わせます。既存の実験結果を確認し、再実験が必要な変更か判断してから進めてください。

## 実験を再実行する場合

Python3.12を使い、このフォルダをカレントディレクトリにしてください。仮想環境は移行先で新しく作ります。元PCの .venv は含めていません。

macOS/Linux:
```
python3.12 -m venv .venv
.venv/bin/python -m pip install -r output/experiments/minority_ratios_20261023/requirements-lock.txt
.venv/bin/python output/experiments/minority_ratios_20261023/run.py --out output/experiments/minority_ratios_20261023/rerun
```

Windows PowerShell:
```
py -3.12 -m venv .venv
.\\.venv\\Scripts\\python.exe -m pip install -r output/experiments/minority_ratios_20261023/requirements-lock.txt
.\\.venv\\Scripts\\python.exe output/experiments/minority_ratios_20261023/run.py --out output/experiments/minority_ratios_20261023/rerun
```

保存済み results を残すため、再実行は別の --out を指定してください。summarize.py は現在 results を読む実装なので、新しい再実行結果を集計するときは読込先を変更してから実行してください。--outを省くと既存キャッシュを使い、再学習しない場合があります。設定を変える場合は必ず新しい出力先を使ってください。

PyTorch等の取得にはネット接続が必要です。OSや機器が違う場合は対応する依存パッケージと日本語フォントを確認してください。スライドの再生成には別途Codexのpresentationsランタイムが必要です。
''')
(B/'引き継ぎ説明.md').write_text('''# 引き継ぎ説明

## ユーザーが求めているもの

ゼミ発表用PowerPoint。タイトルは「テーブルデータにおけるデータ拡張」。内容の順序は以下で確定しています。

1. データ拡張の課題を定義し、「なぜ拡張するのか」「何を守る必要があるか」を説明。
2. シャッフル、コピュラ、SMOTE、コピュラSMOTE、CTGAN、CTGAN×コピュラを解説。
3. 公開データで実際に生成・分類し、結果を比較。理由と限界を考察。

全行に正解ラベルがあり、少数クラスの割合を10％・20％・30％にする意味です。ラベル付与率10〜30％の半教師あり実験ではありません。ユーザーは流れと「なぜ」、見やすさを重視しています。

## 最新の依頼

自分のPCのCodexで続きをするため、資料・コード・実験結果・引き継ぎを１つにまとめること。続いて2026-10-24に、参照PDF「10.05_齊藤光汰.pdf」のレイアウトを真似るよう依頼がありました。PDFの内容を研究内容に流用する指示ではなく、見た目の参照です。

## 実験の確定条件と結果

３公開データ（米、レーズン、模擬電力網）×３少数割合×５seed=45条件を実行済み。６生成法と３対照、２分類器、生成後修正の補助比較も含め全1350分類評価。主資料は修正なしのbaseを示します。

訓練前に層化70:30分割し、訓練側だけ抽出。米と電力網の訓練総数1100、レーズン350を固定。各割合でクラスごとの同じ乱数順の先頭を使用し、同seedのテストは共通です。生成後は1:1、テストは元のクラス比率を保持。

分類器はロジスティック回帰とHistGradientBoosting。固定閾値0.5、ハイパーパラメータ探索なし。CTGAN２法は300epoch。対照は拡張なし・ランダム複製・クラス重み付け。乱数11,23,37,51,67。

Macro-F1の平均と標本SDを資料に掲載。少数割合によって最高平均の手法が変わります。米のロジスティック回帰では拡張なし0.880→0.910→0.927。生成法の追加効果が小さくなる例です。一般的な優劣や有意差を主張しないでください。

Gridはシミュレーション。連続ターゲットstabを入力から除き、stabfを分類。stableを少数としています。米はCammeo、レーズンはBesni。元のRaisinは均衡データです。

## 実装の重要な定義

コピュラはGaussian copula、相関５％縮小。コピュラSMOTEは少数の経験順位を正規変換し、その空間で５近傍補間して逆変換。CTGAN×コピュラはクラス別経験順位変換後にCTGANを学習して少数用分布で逆変換する本プロジェクトの操作上の定義で、公式CopulaGANと同一ではありません。

CTGANの出力ラベル不一致は棄却しますが、真のラベルを保証しません。米・レーズンのArea/ConvexAreaは全手法で整数化。baseにはそれ以外の意味制約修正を含めません。

## データとファイル

- 資料/：内容確定版PowerPoint、31枚のPNG。追加のレイアウト反映版があればそちらを優先。
- presentation_source/：相対パス化したスライド生成JS。実験をやり直さずデザイン変更可能。
- output/experiments/minority_ratios_20261023/run.py：実験。
- summarize.py：保存済み配列と評価を確認し集計。
- requirements-lock.txt：Python依存の固定版。
- results/metrics.csv：1350件の評価。主比較はvariant=base。
- results/quality.csv：生成品質。timing.csv：時間。
- summary.csv：平均・SD。paired_differences.csv：複製との同seed差。
- slide_data.json：スライド用の値。protocol.json：設定と環境。
- datasets.json：出典・SHA256・各条件の件数。
- audit.json：整合性監査の結果。
- 条件別フォルダ：split.npz、生成NPZ、GAN損失CSV、生成メタデータ、モデルpickle、result.json。
- output/experiments/public_semantics_20261015/data/：元データ。run.pyの参照先なのでフォルダ構造を維持。

## 解釈上の注意

５回はテストが重なるholdoutで、独立5-fold CVではありません。比率を変えると少数・多数の観測件数も変化します。事前確率補正と閾値最適化なし。数値の二値分類３件の固定設定に限る結果です。品質制約を満たしても、真のクラスや分類の改善は保証されません。

共有されたScienceDirect論文 https://www.sciencedirect.com/science/article/pii/S0925231226020369 は本文未確認で、内容・回帰から分類への新規性を主張していません。

## 次のCodexへの作業方針

まず「レイアウト参照の状態.md」を確認してください。参照PDFが手元にある場合は全ページを表示し、配色、フォント、タイトル・本文位置、背景、余白、ページ番号、図表を確認してスライドを整えてください。実験の条件や数値はユーザーの追加指示がなければ維持。出典をノートに残し、全スライドをレンダリングして確認します。

既存の完成PPTXは編集可能。元スライド生成器の環境依存はpresentation_source/README.md参照。元PCのユーザー名に依存するパスを新しい環境にコピーしないでください。
''')
print(B)
