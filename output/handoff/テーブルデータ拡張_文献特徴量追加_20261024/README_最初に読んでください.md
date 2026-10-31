# 別のパソコンのCodexで続けるためのフォルダ

このフォルダ全体を移動し、Codexの作業フォルダとして開いてください。既存の実験結果は保存済みなので、資料を編集するだけなら再実験は不要です。

1. 「引き継ぎ説明.md」で目的・確定条件・残作業を確認。
2. 「資料/テーブルデータにおけるデータ拡張_文献と特徴量_完成版.pptx」とスライド画像を確認。
3. 実験コード・実験結果は output/experiments/minority_ratios_20261023/。
4. 元データは output/experiments/public_semantics_20261015/data/。
5. スライドの再生成元は presentation_source/build.mjs。

会話履歴はこのフォルダに自動移行されません。移行先Codexに次の文を貼り付けてください。

> README_最初に読んでください.md と 引き継ぎ説明.md を読み、作業を続けてください。ゼミ資料「テーブルデータにおけるデータ拡張」です。課題の定義、６手法の説明、公開データによる実験比較の順に構成します。全件ラベル付きで、少数クラス割合10％・20％・30％を比較済みです。資料のレイアウトは同梱の参照PDFに合わせて反映済みです。既存の実験結果を確認し、再実験が必要な変更か判断してから進めてください。

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
.\.venv\Scripts\python.exe -m pip install -r output/experiments/minority_ratios_20261023/requirements-lock.txt
.\.venv\Scripts\python.exe output/experiments/minority_ratios_20261023/run.py --out output/experiments/minority_ratios_20261023/rerun
```

保存済み results を残すため、再実行は別の --out を指定してください。summarize.py は現在 results を読む実装なので、新しい再実行結果を集計するときは読込先を変更してから実行してください。--outを省くと既存キャッシュを使い、再学習しない場合があります。設定を変える場合は必ず新しい出力先を使ってください。

PyTorch等の取得にはネット接続が必要です。OSや機器が違う場合は対応する依存パッケージと日本語フォントを確認してください。スライドの再生成には別途Codexのpresentationsランタイムが必要です。
