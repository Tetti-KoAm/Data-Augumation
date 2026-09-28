# コピュラの選び方と今回の実験手順

## 先に結論：どれが最適か

コピュラにデータや目的を問わない「最適な種類」はありません。周辺分布をどう表現するかと、特徴間依存をどう表現するかを分けて考え、最終的には下流タスクの検証データで選ぶ必要があります。コピュラ自体の尤度が高くても、分類に役立つ破損になるとは限りません。

今回の下流比較で試したコピュラはGaussian copulaだけです。比較対象は標準VIMEの列ごとの独立な置換です。5シードのmacro ROC-AUC平均ではGaussian copulaがBreast Cancerで+0.003、Wineで+0.021でしたが、いずれも対応差の95% bootstrap区間は0を含みました。従って「Gaussianが独立破損より確実に良い」とも、「他のコピュラより最適」とも結論できません。現在の推奨は、実装の単純さ・計算可能性・今回の小さな改善傾向を理由にGaussianを基準候補として維持し、t copulaを次の候補として検証することです。

## 候補となるコピュラ

| 種類 | 依存の表現 | 今回の表形式データでの見立て |
|---|---|---|
| 独立（積）コピュラ | 特徴間の依存を仮定しない | 現在の標準VIME破損に相当する比較基準。周辺分布は保ちやすいが、他特徴と整合する値にならない場合がある |
| Gaussian / normal | 潜在正規分布の相関行列で依存を表す。連続値・多次元で比較的扱いやすい | 今回実装済み。尾部依存は表せない。少数標本・多特徴では相関行列の正則化が重要 |
| Student-t | 潜在t分布の相関行列に自由度νを加える。両側の尾部依存を表現 | 外れ値・極端値が複数特徴で同時に現れる構造があれば候補。νの推定が増え、Gaussianより計算・推定が重くなる |
| Clayton | 下側尾部の依存が強い。標準形では交換可能（特徴ペアを入れ替えても同じ依存） | 「複数特徴が同時に低くなる」など明確な片側尾部構造向け。非対称・多様な依存がある多特徴データ全体には単独適用しにくい |
| Gumbel | 上側尾部の依存が強い。標準形は交換可能 | 「複数特徴が同時に高くなる」構造が明確な場合の候補 |
| Frank | 中央付近を含む依存を表し、Clayton/Gumbelのような尾部依存は持たない | 尾部より全体的な依存を調べる比較候補。ただし多次元で単一パラメータのArchimedean形は構造が制限される |
| Vine / pair-copula | 多変量依存を多数の二変量コピュラの積に分解し、ペアごとに異なる族を選べる | 最も柔軟だがパラメータ数・選択肢・計算量が増える。標本が少ないと過学習しやすく、今回のWine（訓練データ142件）では最初の候補にしにくい |

Gaussianは尾部依存を持たず、Student-tは対称な尾部依存を持ちます。ClaytonとGumbelは異なる片側尾部を重点的に表し、vineは異なる二変量構造を組み合わせます。[t copulaの性質に関するDemarta & McNeilの論文](https://doi.org/10.1111/j.1751-5823.2005.tb00254.x)、[vine構成の原著論文](https://core.ac.uk/download/pdf/12162901.pdf)、[Gaussian copulaの尾部依存に関する解説論文](https://arxiv.org/abs/1607.04736)を参照してください。

今回のBreast Cancerは30特徴・訓練455件（うちラベルなし319件）、Wineは13特徴・訓練142件（うちラベルなし100件）です。特徴数に対してWineは特に標本数が少なく、vineのような柔軟なモデルをいきなり選ぶより、低自由度のGaussianとt copulaを先に比べるのが現実的です。ただし、分布の形だけで結論を出してはいけません。特徴破損がクラス境界をまたぐ可能性があるためです。

### 「最適」を今後どう判定するか

1. Gaussian、Student-t（例えばνを2, 4, 8, 16で比較）、必要性がデータ診断で見えた場合のみClayton/Gumbelや縮約vineを候補にする。
2. 内側の訓練・検証分割だけで周辺分布と依存構造をfitする。テストデータはモデル選択に使わない。
3. コピュラ密度の検証対数尤度や、観測特徴を条件にしたholdout特徴の対数尤度で「分布への当てはまり」を診断する。
4. 最終目的は分類なので、内側のラベル付き検証データで macro ROC-AUC などを測り、下流性能が最良の族・パラメータを選ぶ。対数尤度が最良でも下流性能が最良とは限らない。
5. 選択を固定してから、未使用の外側テスト分割で一度だけ評価する。複数データセット・複数シードで順位が再現するか確認する。

このnestedな選択を行っていない今回の結果から言えるのは、「固定設定のGaussian VIMEと標準VIMEの比較」までです。

## 今回実施した実験：データから評価まで

実行スクリプトは [`quick_compare.py`](../scripts/quick_compare.py)、VIME実装は [`vime_torch.py`](../src/tabular_research/vime_torch.py)、破損実装は [`corruption.py`](../src/tabular_research/corruption.py) です。生の各試行結果は [`repeated_compare.json`](repeated_compare.json) にあります。

1. **データ取得**：scikit-learn内蔵のBreast Cancer Wisconsin（569×30、2クラス）とWine（178×13、3クラス）を使いました。どちらも今回のcopula実装が要求する有限な連続数値特徴です。カテゴリ特徴や欠損値の実験ではありません。
2. **外側分割**：シード11, 23, 37, 51, 67ごとに、目的変数で層化した80%訓練・20%テスト分割を作りました。全手法に同じ分割を渡します。
3. **ラベルを隠す**：訓練分割内でさらに層化し、30%だけをラベル付きにします。残り70%はVIMEの自己教師あり段階・一貫性学習・クラス条件付き学習の入力特徴に使用し、目的変数は渡しません。Breast Cancerでは各試行で455訓練（136ラベル付き、319ラベルなし）・114テスト、Wineでは142訓練（42ラベル付き、100ラベルなし）・36テストです。
4. **前処理**：MinMaxScalerを訓練特徴だけでfitし、訓練とテストを[0, 1]範囲に変換します。外側テストの統計量は前処理に使いません。
5. **標準VIME**：列ごとに独立した訓練値を置換する破損を使用します。マスク推定＋特徴再構成でエンコーダを事前学習し、エンコーダを固定して、ラベル付き交差エントロピーと未ラベルデータの複数破損ビュー間の予測一貫性を学習します。
6. **Gaussian Copula VIME**：VIMEの損失・ネットワーク・データ分割は同じにし、置換値の生成だけを条件付きGaussian copulaに差し替えます。この二手法の差が、今回の比較で最も直接的に破損方法の差を表します。
7. **先行研究2**：変更していない固定コミットの公式コードから`ClassCorruptSampler`、モデルと学習関数を呼びます。ラベル付きデータからブートストラップ分類器を学習し、その予測で未ラベル行に疑似クラスを割り当て、同じクラスと推定された行から破損元をサンプルします。この手法は損失・学習戦略自体もVIMEと異なるため、Gaussian copulaだけの比較ではありません。
8. **評価と集計**：テストデータでmacro ROC-AUC（主指標）、balanced accuracy、macro F1、accuracyを計算。5シードの平均・標準偏差と、同じシード内での標準VIMEとの差を求めました。差の95%区間は5個のシード差を10,000回再標本化するpercentile bootstrapです。外側分割が重複するため、確証的有意差検定ではなく探索的なばらつき表示として扱います。

## Gaussian copulaの実装フロー

`VIMEClassifier.fit(x_labeled, y_labeled, x_unlabeled)`から始まります。`pretrain(x_unlabeled)`でcopulaを**ラベルなし訓練特徴だけ**にfitし、特徴ごとの経験分布と依存行列を作ります。

1. 各特徴を順位に変換し、`u=(rank−0.5)/n`で(0,1)に入れます。順位は同値を平均順位で扱い、両端は数値安定性のためクリップします。
2. `z=Φ⁻¹(u)`で潜在正規尺度に変換し、各特徴ペアの相関から相関行列Rを推定します。
3. `R ← (1−λ)R + λI`で正則化し、正定値になるようjitterを加えます。今回の値はλ=0.05、jitter=1e-6です。
4. 行ごとに置換対象Mと観測対象Oに分けます。Gaussian条件付き分布は次の通りです。

   `Z_M | Z_O=z_O ~ Normal(R_MO R_OO⁻¹ z_O, R_MM − R_MO R_OO⁻¹ R_OM)`

5. 条件付き分布から値を引き、各列の経験逆CDF（訓練データの経験分位点）で元の尺度に戻します。これにより単変量の周辺分布を経験的に保ちつつ、観測特徴と整合する依存を残そうとします。
6. 条件付き共分散から乱数を生成する際はCholesky分解を用います。特異に近いときはjitterを追加します。

これは連続値向けのGaussian copulaであり、カテゴリ値を扱う混合コピュラではありません。さらに、条件付き生成が実際のクラスを維持する保証はありません。

## 主要パラメータ

| パラメータ | 今回値 | 意味 |
|---|---:|---|
| 外側テスト割合 | 0.20 | 1試行ごとの層化訓練/テスト比 |
| 訓練内ラベル割合 | 0.30 | 訓練分割中でラベルを使える割合 |
| seeds | 11, 23, 37, 51, 67 | 分割・初期値・サンプル順の再現用 |
| mask corruption probability | 0.40 | 各特徴を破損対象にするBernoulli確率 |
| Gaussian shrinkage | 0.05 | 相関推定を単位行列側に縮約する割合 |
| Gaussian jitter | 1e-6 | 行列計算の数値安定化 |
| self-supervised epochs | 15 | VIMEのマスク推定・再構成の学習回数 |
| reconstruction weight | 2.0 | 再構成MSEに掛ける係数 |
| augmented views | 3 | 一貫性損失で比較する破損ビュー数 |
| consistency weight | 1.0 | 予測一貫性損失の係数 |
| VIME semi iterations | 300 | ラベル損失＋一貫性損失の更新回数 |
| batch size | 64 | 更新ごとのラベル・未ラベルサンプル上限 |
| encoder | 4層、幅32、dropout 0 | 三手法間で共通とした表現部 |
| predictor hidden width | 32 | VIME分類予測器の隠れ幅 |
| optimizer | pretrain: RMSprop / predictor: Adam | predictor学習率は実装既定値1e-3 |
| class-conditioned refresh | 10 epochs | 疑似ラベル・クラスサンプラー更新間隔 |

公式クラス条件付きコードにも同じbatch size・15 contrastive epochs・15 supervised epochs・corruption rate 0.4を設定しました。VIMEのsemi iterationsと公式手法のepochsは同じ単位ではないため、「同じ計算更新回数」ではありません。加えて公式法では10 epochごとに追加の教師あり学習と疑似ラベル更新があります。結果はあくまで今回の固定設定に対する比較です。

## コードの呼び出し順

1. `scripts/run_quick_compare.sh`が仮想環境Python、PyTorch同梱ライブラリ、`PYTHONPATH`を設定します。
2. `scripts/quick_compare.py:main()`が各データセット・シードを順に処理し、JSONを保存します。
3. `run_one()`が外側分割、ラベル付き/未ラベル分割、train-only scaling、ネットワーク設定を作ります。
4. `VIMEClassifier.fit()`が事前学習と半教師あり学習を行います。破損器を注入するため、通常置換とGaussian copulaを同じ処理系で比較できます。
5. 同じ`run_one()`内で公式クラス条件付き法を実行し、同じ外側testに対する予測を得ます。
6. `score()`が指標を計算し、`summarize()`が平均・標準偏差・中央値・シード対応差とbootstrap区間を作ります。

参考となる実装箇所：[`quick_compare.py`](../scripts/quick_compare.py)の`run_one()`/`score()`/`summarize()`、[`vime_torch.py`](../src/tabular_research/vime_torch.py)の`pretrain()`/`fit()`、[`corruption.py`](../src/tabular_research/corruption.py)の`GaussianCopulaCorruptor.fit()`/`sample_conditional()`。

## 実行環境と再現方法

今回の実験環境はmacOS 26.3.1 arm64、Python 3.13.12、PyTorch 2.14.0、NumPy 2.5.3、SciPy 1.18.1、pandas 3.0.6、scikit-learn 1.9.1です。依存パッケージの固定一覧は[`requirements-lock.txt`](../requirements-lock.txt)にあります。CPUで実行し、各手法の開始時にPython/NumPy/PyTorch seedを同じ値にリセットします。公式repoのimportがXGBoost/OpenMPを読むため、ランチャーはPyTorchの`lib`を`DYLD_LIBRARY_PATH`に加えます。OpenBLAS/OMPスレッド数の既定値は各1です。

再現するにはこのプロジェクトディレクトリで次を実行します。

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-lock.txt
scripts/run_quick_compare.sh --epochs 15 --vime-iterations 300
```

デフォルトで上記2データセット・5シードが走り、`results/repeated_compare.json`が更新されます。標準出力にOpenMLディレクトリの権限警告が出る環境がありますが、この実験はOpenMLからデータを取得せずscikit-learn内蔵データのみを使うため、実行自体には影響しません。

最後に大切な限界です。5シード・2データセット・固定15 epochの結果を研究上の確定結論とすることはできません。クラス条件付き手法はVIMEと学習目的も異なるため、Copulaと通常破損の差だけを比較したいときはVIME同士を主比較にしてください。コピュラ族を本当に選定する次段階では、内側validationでGaussianとStudent-tを選び、選択後に外側testで評価する設計が必要です。
