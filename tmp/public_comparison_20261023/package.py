from pathlib import Path
import json,zipfile
import pandas as pd
R=Path.cwd(); E=R/'output/experiments/six_methods_20261023'; O=R/'output/presentations/公開データ比較_20261023'; data=json.loads((E/'results/slide_data.json').read_text()); M=pd.read_csv(E/'results/metrics.csv'); Q=pd.read_csv(E/'results/quality.csv')
report='''# テーブルデータにおけるデータ拡張：公開データ比較

実行日：2026-10-23。実験結果を示す資料であり、最適化した全手法の一般的な順位を確定する比較ではありません。

## 実験設計

UCIの米（3,810行・7特徴）、レーズン（900行・7特徴）、模擬電力網（10,000行・12特徴）を使用。すべて数値の二値分類です。電力網の連続ターゲット stab は入力から除き、stabf を分類します。

元データを層化70:30で分割した後、訓練側だけ多数上限1,000件、少数は多数の1/10（切捨て）を選びます。米と電力網は1,000:100、レーズンは315:31。残りの訓練候補は使いません。少数ラベルはCammeo、Besni、stableです。元のRaisinは均衡データです。テストは元のクラス比率を保ちます。seed=11,23,37,51,67を全手法で共有し、６生成法は追加後1:1に揃えます。

全変換と学習は訓練内で実施。対照は拡張なし、ランダム複製、クラス重み付け。標準化＋ロジスティック回帰とHistGradientBoostingClassifierを使用。分類閾値0.5、ハイパーパラメータ探索なし。主指標はMacro-F1。５回はテストが重なる反復holdoutであり、独立な5-fold CVではありません。平均と標本SDを報告し、有意差を主張しません。

## 手法の定義

- 列シャッフル：少数クラスの各列を独立に復元抽出。
- Gaussian copula：少数クラスの経験順位を正規化し、相関R=0.95R推定+0.05Iで多変量正規生成後、経験分布で逆変換。
- SMOTE：実訓練データで標準化し、k=5の少数近傍を補間、逆変換。
- コピュラSMOTE：少数クラスの経験順位を正規化し、変換空間の５近傍で線形補間、逆変換。今回の操作上の定義。
- CTGAN：全訓練行とカテゴリラベルを学習し、少数条件で生成。生成されたラベルが少数と異なる行は再抽出。真のクラスを保証する判定ではありません。
- CTGAN×コピュラ：クラス別に経験順位を正規化しCTGANを学習。少数条件で生成した行を少数分布で逆変換。今回の操作上の定義であり、公式CopulaGANと同一ではありません。

GAN２法はctgan0.11.0、300epochs、embedding128、generator/discriminator=(128,128)、batch200、pac10、CPU。copulaのPSD固有値下限1e-8。全生成法で米/レーズンのAreaとConvexAreaは整数化します。その他の制約修正はbaseには含めません。

## 結果：Macro-F1（平均 ± 標本SD）

'''
for d in data['datasets']:
 report+='### '+d+'\n\n|手法|Logistic|Boost|\n|---|---|---|\n'
 for method in data['methods']:
  vals=[]
  for c in ['logistic','hist_boost']:
   a=M.query('dataset==@d and method==@method and classifier==@c and variant=="base"').macro_f1
   vals.append(f'{a.mean():.4f} ± {a.std():.4f}')
  report+='|'+data['method_names'][method]+'|'+'|'.join(vals)+'|\n'
report+='''
## 読み取りと制約

分類器とデータにより順位が変わりました。米とレーズンではロジスティック回帰のクラス重み付けも強い対照です。Boostでは３データともコピュラが最高平均でしたが、固定設定での探索的結果です。GANがすべての条件で勝つことは確認できませんでした。

特徴間の既知関係の違反率は分類性能と一致しません。米/レーズンでは軸長と離心率、軸長の大小、面積と凸包面積、電力網では電力の収支を確認しました。米/レーズンは許容誤差0.01（面積は1）、電力網はabs(p1+p2+p3+p4)>0.01で違反とします。指標はデータ間で厳しさが異なるので、手法を同じデータ内で比較します。

生成後の補助輪として、米/レーズンは正値化・軸長の大小修正・離心率再計算・凸包面積>=面積・Extent範囲制限、電力網はp1=−(p2+p3+p4)を行いました。違反率０は修正の定義上の結果です。分類性能は改善する場合と悪化する場合があり、ラベルの正しさはこの修正で保証されません。修正前後の全値はrepair_differences.csvにあります。

本比較は人工的な10:1、数値特徴、少数100/31件、固定予算と閾値に限られます。米・レーズンは似た形状特徴、電力網はシミュレーションです。訓練とテストの事前確率の差を補正していません。ラベルなし・カテゴリ混在・実運用の有効性は未検証。共有されたScienceDirect論文の本文は未確認で、論文内容や新規性を主張していません。

## データ・原著

UCIの３データはCC BY 4.0。各公式ページの著者表示を参照してください。

- Rice Cammeo and Osmancik: https://archive.ics.uci.edu/dataset/545/rice+cammeo+and+osmancik DOI:10.24432/C5MW4Z
- Raisin: https://archive.ics.uci.edu/dataset/850/raisin DOI:10.24432/C5660T
- Electrical Grid Stability Simulated Data: https://archive.ics.uci.edu/dataset/471/electrical+grid+stability+simulated+data DOI:10.24432/C5PG66
- Chawla et al. (2002), SMOTE: https://www.cs.cmu.edu/afs/cs/project/jair/pub/volume16/chawla02a.pdf
- Xu et al. (2019), CTGAN: https://papers.nips.cc/paper/2019/hash/254ed7d2de3b23ab10936522dd547b78-Abstract.html

## 再現方法

Python3.12で仮想環境を作成し、requirements-lock.txtをインストールしてください。Torch等が大きいため時間を要します。ZIPを展開したルートで次を実行します。run.pyはファイル自身から３階層上をデータのルートとします。

```
python -m venv .venv
.venv/bin/pip install -r output/experiments/six_methods_20261023/requirements-lock.txt
.venv/bin/python output/experiments/six_methods_20261023/run.py --out output/experiments/six_methods_20261023/rerun
```

デフォルトは３データ×５seed×300epoch。--outを省略すると保存済みresultsを再利用します。summarize.pyはresultsを集計・監査します。浮動小数点・Torch実装や機器差により完全一致しない場合があります。

CSV: metrics（全450分類評価）、quality（生成診断）、timing（生成時間）、paired_differences（対照との差）、repair_differences（修正前後）。NPZ: train/test分割と生成行。protocol.jsonに設定とライブラリバージョン、datasets.jsonに元データのSHA256。GAN損失は各*_loss.csv。モデルpickleと仮想環境はZIPに含めません。生成時間はCPU２並行ジョブでの壁時計時間で、単独実行速度の厳密な比較ではありません。
'''
(E/'README.md').write_text(report)
with zipfile.ZipFile(O/'公開データ比較_実験コードと全結果.zip','w',zipfile.ZIP_DEFLATED) as z:
 for n in ['run.py','summarize.py','requirements-lock.txt','README.md']:
  f=E/n;z.write(f,f.relative_to(R))
 for f in (E/'results').rglob('*'):
  if f.is_file() and f.suffix!='.pkl':z.write(f,f.relative_to(R))
 for meta in data['metadata'][::5]:
  f=R/meta['file'];z.write(f,f.relative_to(R))
print('report and ZIP ready')
