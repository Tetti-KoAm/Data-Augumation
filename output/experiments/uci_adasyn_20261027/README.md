# UCI二値分類・SMOTE/ADASYN比較（2026-10-27）

ゼミコメントに対応した実験用の新版です。既存 `minority_ratios_20261023` の生成・分類・意味制約診断を引き継ぎ、過去の5回分の結果は変更しません。

## 実験条件

- UCI Rice Cammeo and Osmancik（Cammeoを少数側）、Raisin（Besni）、Electrical Grid Stability Simulated Data（stable）の3データ。元の二値ラベルを使用。電力網の連続ターゲット `stab` は入力から除外。
- 元データを各seedで層化70:30に分割し、訓練側のみ少数割合を全体の10%・20%・30%へ調整。ラベル付与率ではありません。テストは元の割合を維持。
- 拡張前の訓練総数を割合間で固定（米・電力網1100、レーズン350）。クラス別の抽出順とテストを共有。少数増加に伴い多数は減ります。
- 10 seed: `11 23 37 51 67 79 97 113 131 149`。手法間で同じsplitを使用。反復holdoutであり、独立な10-fold CVではありません。
- 既存6生成法: 列シャッフル、Gaussian copula、SMOTE、コピュラSMOTE、CTGAN、CTGAN×コピュラ。
- 追加2生成法: ADASYN、コピュラADASYN。対照は拡張なし、ランダム複製、クラス重み付け。合計11条件。共通4生成法は共有するため、6手法のSMOTE版とADASYN置換版を同じ結果から比較できます。
- 分類器は標準化＋LogisticRegression、HistGradientBoosting。主比較は `variant=base`。`repair` は既存の代数制約修正を適用した補助比較。
- CTGANは既存と同じ300 epoch・CPU。小標本でも実行し、優位性を前提としません。今回はデータ数を変える独立実験は含みません。

## ADASYNの定義

通常版は実訓練全体で標準化して `imblearn.over_sampling.ADASYN(n_neighbors=5)` を適用し、逆変換します。
コピュラ版は少数クラスのみで経験周辺分布を学習し、その**共通の変換**を多数・少数の両方へ適用してADASYNを実行、少数周辺分布で逆変換します。多数側の範囲外値は変換端でクリップされます。この実験での操作上の定義であり、確立した同名手法の再現を意味しません。

ADASYNの局所配分の丸めにより、追加後のクラス件数が厳密な1:1にならない場合があります。実装の生成件数をそのまま使い、`timing.csv` の `requested_n_added` / `actual_n_added` と `metrics.csv` の `n_added` で確認できます。他の生成法は1:1に揃えます。米・レーズンの面積列は既存コードと同様に整数化します。

生成不能時はSMOTE等に置き換えず `failures.csv` に理由を記録。その条件の `n_success` が減り、未完了表示になります。単独成功回の標準偏差は未定義です。

公式仕様: [ADASYN](https://imbalanced-learn.org/stable/references/generated/imblearn.over_sampling.ADASYN.html)

## 実行

リポジトリルートでPython 3.12環境を使用してください。既存データは `output/experiments/public_semantics_20261015/data/{545,850,471}` を読みます。未取得の場合は既存 `download.py` で取得できます（他2データも取得されます）。

```bash
python3.12 -m venv .venv
.venv/bin/pip install -r output/experiments/uci_adasyn_20261027/requirements-lock.txt
.venv/bin/python output/experiments/public_semantics_20261015/download.py
.venv/bin/python output/experiments/uci_adasyn_20261027/run.py
.venv/bin/python output/experiments/uci_adasyn_20261027/verify.py
```

ダウンロード済みなら取得コマンドは不要です。デフォルトは3データ×3割合×10回=90ジョブ、各ジョブで11条件・2分類器を実行します。GAN学習は計180回です。実験終了時に平均・標準偏差を自動出力します。

```bash
# 短い全手法の動作確認（本実験の結果と混在させない）
.venv/bin/python output/experiments/uci_adasyn_20261027/run.py --datasets raisin --ratios .1 --seeds 11 23 --epochs 1 --out /tmp/uci_adasyn_smoke
# 中断した実験の再開は同じコマンド・同じoutを指定
# 出力先を指定して再集計・監査
.venv/bin/python output/experiments/uci_adasyn_20261027/summarize.py --out /tmp/uci_adasyn_smoke
.venv/bin/python output/experiments/uci_adasyn_20261027/verify.py --out /tmp/uci_adasyn_smoke
```

`--methods` で手法を絞れます。seed・手法・epoch等の設定が異なる結果の再利用を防ぐため、設定変更時は新しい `--out` を指定してください。既定 `results` は過去の実験出力と別です。中断時は完了ジョブと保存済み生成行から再開します。

## 出力

- `summary.csv`: データ×割合×分類器×手法×variantごとに各評価指標の `_mean` と `_std`（標本SD、ddof=1）、`n_success`、`n_expected`、`complete`。
- `summary.md`: 主比較のMacro-F1「平均 ± SD」と成功回数。未完了条件も表示。
- 指標: Macro-F1、balanced accuracy、少数クラスRecall/Precision、ROC-AUC、average precision（PR曲線の要約）。テストの不均衡率は変更しません。
- `metrics.csv` / `quality.csv` / `timing.csv`: 各回の性能・生成診断・時間。`failures.csv`: ADASYN生成失敗。
- `completion.json`: 完了ジョブ数・生成失敗数・全条件完了状態。`audit.json`: `verify.py` の監査結果。監査合格と全条件完了は別項目です。
- `protocol.json` / `datasets.json`: 実験設定・環境・元データSHA256・件数。各条件フォルダにsplit、生成行、GAN損失・モデルを保存。

平均のみで手法の優劣を断定せず、SDと成功回数を併記してください。成功回のみの平均も出しますが、10回そろわない条件は完了扱いにしません。データ数の違い、米とレーズンの特徴の類似、電力網がシミュレーションである点も解釈上の制約です。

## データ出典

いずれもUCI配布元の著者表示とCC BY 4.0に従って利用してください。

- [Rice Cammeo and Osmancik](https://archive.ics.uci.edu/dataset/545/rice+cammeo+and+osmancik) DOI:10.24432/C5MW4Z
- [Raisin](https://archive.ics.uci.edu/dataset/850/raisin) DOI:10.24432/C5660T
- [Electrical Grid Stability Simulated Data](https://archive.ics.uci.edu/dataset/471/electrical+grid+stability+simulated+data) DOI:10.24432/C5PG66

## 本実験の完了結果

全90ジョブ、GAN計180回×300 epochの本実験が完了し、全条件10回の結果を監査済みです。生成失敗0件。全手法の平均・標本SDは [比較レポート](results/comparison.md)、全指標は [summary.csv](results/summary.csv)、手法間の対応差は [paired_comparisons.csv](results/paired_comparisons.csv) を参照してください。
