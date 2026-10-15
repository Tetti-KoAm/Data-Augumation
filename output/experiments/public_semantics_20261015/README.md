# 公開データ・意味制約・少数ラベル比較（2026-10-15）

主な成果物は `実験レポート.md`。`metrics.csv` はデータ・ラベル数・seed・手法別の分類成績、`semantics.csv` は生成行の制約違反、`metadata.json` は特徴名・相関・具体的な破綻例、`paired_summary.csv` は対応差の集計。`PROTOCOL.md` に設定と実行上の調整を記録。

リポジトリルートで再現：

```sh
python3.12 -m venv output/experiments/public_semantics_20261015/.venv312
output/experiments/public_semantics_20261015/.venv312/bin/python -m pip install -r output/experiments/public_semantics_20261015/requirements.txt
output/experiments/public_semantics_20261015/.venv312/bin/python output/experiments/public_semantics_20261015/download.py
output/experiments/public_semantics_20261015/.venv312/bin/python output/experiments/public_semantics_20261015/verify_fast.py
output/experiments/public_semantics_20261015/.venv312/bin/python output/experiments/public_semantics_20261015/run.py
output/experiments/public_semantics_20261015/.venv312/bin/python output/experiments/public_semantics_20261015/diagnose.py
output/experiments/public_semantics_20261015/.venv312/bin/python output/experiments/public_semantics_20261015/report.py
```

データ出典（UCI、CC BY 4.0）：

- Dry Bean (2020): https://doi.org/10.24432/C50S4B
- Rice (Cammeo and Osmancik) (2019): https://doi.org/10.24432/C5MW4Z
- Çinar, İ., Koklu, M., & Tasdemir, S. (2020), Raisin: https://doi.org/10.24432/C5660T
- Candanedo, L. (2016), Occupancy Detection: https://doi.org/10.24432/C5X01N
- Arzamasov, V. (2018), Electrical Grid Stability Simulated Data: https://doi.org/10.24432/C5PG66

「全列が無相関な5データ」を確保したという主張ではない。選定の限界、Gaussian copulaの表現力と制約保持の限界、分類結果の不安定さをレポートに記載する。
