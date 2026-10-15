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

## 公開データ5件の追加比較（2026-10-15）

豆・米・レーズン・室内在室・電力網を対象に、分類性能と生成行の意味制約を別々に評価しています。

- [少数ラベル30件・100件の比較](output/experiments/public_semantics_20261015/実験レポート.md)：各5 seed、標準VIMEとcopula版、ラベルのみの参考対照。
- [論文の主要条件での3手法比較](output/experiments/paper_conditions_20261015/比較レポート.md)：ラベル率30%、各8 seed、幅256・前学習500 epoch。標準VIME、クラス条件付き対照学習、提案copulaを比較。
- [論文条件との対応・実装上の調整](output/experiments/paper_conditions_20261015/PROTOCOL.md)と[再現手順](output/experiments/paper_conditions_20261015/README.md)。

低相関の特徴ペアを含む候補の比較であり、全特徴が無相関な5データを確保した実験ではありません。
