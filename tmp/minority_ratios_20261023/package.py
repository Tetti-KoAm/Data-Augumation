from pathlib import Path
import json,zipfile
import pandas as pd
R=Path.cwd();E=R/'output/experiments/minority_ratios_20261023';O=R/'output/presentations/少数クラス割合比較_20261023';D=json.loads((E/'results/slide_data.json').read_text());M=pd.DataFrame(D['metrics'])
old=(R/'output/experiments/six_methods_20261023/README.md').read_text();defs=old.split('## 手法の定義')[1].split('## 結果：')[0]
s='''# テーブルデータにおけるデータ拡張：少数割合10%・20%・30%

## 問いと対象

全件に正解ラベルがある二値分類で、少数クラスを増やす６手法の挙動を比較します。ラベル付与率の比較ではありません。資料は課題の定義、手法の解説、公開データでの実験の順で構成しています。

実行：2026-10-23。UCIの米3810行7特徴、レーズン900行7特徴、電力網10000行12特徴を利用。電力網はシミュレーションで、連続ターゲットstabを入力から除き、stabfを分類します。

## 割合の調整と評価

元データをseed=11,23,37,51,67で層化70:30に分割。訓練候補からのみ抽出し、テストには触れません。比率間で拡張前の訓練総数を固定します。米・電力網は1100件（多数/少数が990/110、880/220、770/330）、レーズンは350件（315/35、280/70、245/105）。少数ラベルはCammeo、Besni、stable。同じseedの各比率でテスト集合を共通にし、各クラスの抽出は同じ乱数の並びの先頭から行います。少数が増えると多数は減るため、純粋な割合だけの因果効果ではありません。

６生成法とランダム複製は訓練クラス件数を1:1にするまで少数例を追加。拡張なしとクラス重み付けも対照にします。テストは元のクラス比率を保持。全てラベルあり、余った訓練候補は不使用。ハイパーパラメータ探索なし、閾値0.5、事前確率補正なし。分類器はStandardScaler+LogisticRegression(C=1,max_iter=2000)とHistGradientBoosting(max_iter=100,max_leaf_nodes=15,l2_regularization=1,early_stopping=False)。重み付け対照のみclass_weight=balanced。

５回は反復holdoutでテストが重なり、独立な5-fold CVではありません。平均±標本SDで探索的に比較し、有意差を主張しません。

## 手法の定義
'''+defs+'\n## Macro-F1（平均 ± 標本SD）\n\n'
names={'none':'拡張なし','duplicate':'複製','class_weight':'重み付け','shuffle':'シャッフル','copula':'コピュラ','smote':'SMOTE','copula_smote':'コピュラSMOTE','ctgan':'CTGAN','ctgan_copula':'CTGAN×コピュラ'}
for d in ['rice','raisin','grid']:
 for c in ['logistic','hist_boost']:
  s+=f'### {d} / {c}\n\n|手法|少数10%|少数20%|少数30%|\n|---|---|---|---|\n'
  for m,label in names.items():
   vals=[]
   for r in [.1,.2,.3]:
    a=M.query('dataset==@d and classifier==@c and method==@m and minority_fraction==@r and variant=="base"').macro_f1; vals.append(f'{a.mean():.4f} ± {a.std():.4f}')
   s+='|'+label+'|'+'|'.join(vals)+'|\n'
s+='''
## 診断と限界

全評価はmetrics.csv。quality.csvは生成行の既知制約、相関誤差、複製率などを記録。近傍ラベル一致は代理指標であり、生成行の真のクラスを確認した結果ではありません。電力関係はabs(p1+p2+p3+p4)>.01で違反。米・レーズンは離心率と軸長の整合、大小関係、面積と凸包面積を診断。関係の違反率と分類性能は別々の観点です。

保存データには既知制約の生成後修正を行ったrepair評価も含みますが、発表の主比較は修正なしのbaseです。修正後の違反率0は修正の定義上の結果。raw_generatedとgenerated（面積整数化）を保存し、修正済みの行はrepair関数で再構成できます。

人工的に作った割合、数値特徴、３データ、固定設定の結果です。米とレーズンは同系の形状特徴、電力網は模擬データ。カテゴリ混在・ラベルなし・実運用への有効性は未検証。共有されたScienceDirect論文の本文や新規性は引用していません。

## 再現方法

ZIPを展開したルートでPython3.12仮想環境を用意してください。

```
python -m venv .venv
.venv/bin/pip install -r output/experiments/minority_ratios_20261023/requirements-lock.txt
.venv/bin/python output/experiments/minority_ratios_20261023/run.py --out output/experiments/minority_ratios_20261023/rerun
```

デフォルト３データ×３割合×５seed×300epoch。--out省略時は保存済みresultsを再利用します。summarize.pyはresultsを集計・監査。環境や機器により浮動小数点結果が変わる場合があります。モデルpickleと仮想環境はZIPに含めません。各split.npzに訓練とテストの行番号・実データ、各generated.npzに生成行、loss.csvにGANの損失を保存。audit.jsonに確認項目があります。生成時間はCPU２並行ジョブの壁時計時間で、厳密な速度benchmarkではありません。

## 出典とライセンス

UCIの３データはCC BY 4.0。各公式ページに原著者の表示があります。データ名、DOI、以下の配布元とともに再利用時も表示してください。

- Rice Cammeo and Osmancik: https://archive.ics.uci.edu/dataset/545/rice+cammeo+and+osmancik DOI:10.24432/C5MW4Z
- Raisin: https://archive.ics.uci.edu/dataset/850/raisin DOI:10.24432/C5660T
- Electrical Grid Stability Simulated Data: https://archive.ics.uci.edu/dataset/471/electrical+grid+stability+simulated+data DOI:10.24432/C5PG66
- Chawla et al. (2002), SMOTE: https://www.cs.cmu.edu/afs/cs/project/jair/pub/volume16/chawla02a.pdf
- Xu et al. (2019), CTGAN: https://papers.nips.cc/paper/2019/hash/254ed7d2de3b23ab10936522dd547b78-Abstract.html
'''
(E/'README.md').write_text(s)
with zipfile.ZipFile(O/'少数割合10_20_30％_実験コードと全結果.zip','w',zipfile.ZIP_DEFLATED) as z:
 for n in ['run.py','summarize.py','requirements-lock.txt','README.md']:
  f=E/n;z.write(f,f.relative_to(R))
 for f in (E/'results').rglob('*'):
  if f.is_file() and f.suffix!='.pkl':z.write(f,f.relative_to(R))
 for meta in D['metadata']:
  if meta['seed']==11 and meta['minority_fraction']==.1:
   f=R/meta['file'];z.write(f,f.relative_to(R))
print('Packaged')
