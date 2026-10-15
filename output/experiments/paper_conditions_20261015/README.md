# 論文条件でのVIME・クラス条件付き対照学習・提案copula比較

主成果物は `比較レポート.md`。実験条件と論文との差は `PROTOCOL.md`、全seed成績は `metrics.csv`、対応差は `paired_summary.csv`、共通マスクでの制約違反は `controlled_semantics.csv` を参照。

既存の `../public_semantics_20261015/data/` と同フォルダの `fast_copula.py` を再利用する。データがなければ前回フォルダのdownload.pyでUCI公式データを取得する。

リポジトリルートから、requirements.txtを導入したPython 3.12環境で実行：

```sh
output/experiments/public_semantics_20261015/.venv312/bin/python output/experiments/paper_conditions_20261015/verify.py
output/experiments/public_semantics_20261015/.venv312/bin/python output/experiments/paper_conditions_20261015/run.py --workers 4
output/experiments/public_semantics_20261015/.venv312/bin/python output/experiments/paper_conditions_20261015/controlled_semantics.py
output/experiments/public_semantics_20261015/.venv312/bin/python output/experiments/paper_conditions_20261015/audit.py
output/experiments/public_semantics_20261015/.venv312/bin/python output/experiments/paper_conditions_20261015/dataset_info.py
output/experiments/public_semantics_20261015/.venv312/bin/python output/experiments/paper_conditions_20261015/report.py
```

各runはデータとseed別のフォルダに結果を保存する。既存の学習結果と診断結果がそろっていればrun.pyはその条件を再学習せず再開できる。`--collect-only` は完了した各条件をmetrics.csvへ集計する。

これは著者main.pyの完全な再実行ではない。著者モデルを読み込み、損失の等価な高速化と既知ラベル行の対応を維持する修正を行った数値データ向けadapter。VIMEと論文の対照学習では目的関数・前処理・分類ヘッド・ラベルの使い方が異なる。詳細はPROTOCOL.md。

出典：Cui et al. (2024), Tabular Data Contrastive Learning via Class-Conditioned and Feature-Correlation Based Augmentation, arXiv:2404.17489。著者ソースはresearch-bench/upstream/Tabular-Class-Conditioned-SSL/に固定済み。
