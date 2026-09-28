# Data-Augumation

テーブルデータ拡張の研究用リポジトリです。VIMEの列内シャッフルを
Gaussian copulaによる条件付きサンプリングへ置き換える実験と、関連する
中間発表資料・調査記録を保存しています。

## 構成

- [`research-bench/`](research-bench/): 実験コード、固定した先行研究実装、実験結果
- [`docs/WORK_LOG_2026-09-24.md`](docs/WORK_LOG_2026-09-24.md): これまでの作業内容、結果、注意点、次の課題
- [`docs/artifacts/`](docs/artifacts/): 中間発表の元スライドとレビューPDF
- [`scripts/generate_research_review_pdf.py`](scripts/generate_research_review_pdf.py): レビューPDFの生成コード

## 実験の再現

```bash
cd research-bench
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-lock.txt
scripts/run_quick_compare.sh --epochs 15 --vime-iterations 300
```

実験条件と解釈は
[`research-bench/results/EXPERIMENT_DETAILED_JA.md`](research-bench/results/EXPERIMENT_DETAILED_JA.md)、
要約は
[`research-bench/results/REPORT_JA.md`](research-bench/results/REPORT_JA.md)
を参照してください。
