from pathlib import Path
import json,numpy as np,pandas as pd
P=Path(__file__).resolve().parent
names={'bean':'Dry Bean（豆）','rice':'Rice（米）','raisin':'Raisin（レーズン）','occupancy':'Occupancy（室内在室）','grid':'Electrical Grid（電力網）'}
ids={'bean':602,'rice':545,'raisin':850,'occupancy':357,'grid':471}
slugs={'bean':'dry+bean','rice':'rice+cammeo+and+osmancik','raisin':'raisin','occupancy':'occupancy+detection','grid':'electrical+grid+stability+simulated+data'}
desc={
'bean':'豆7品種の分類。面積・周長・長短軸・離心率・凸包面積に加え、縦横比、等価直径、外接矩形充填率、凸包充填率、円形度、コンパクトさ、4種類の形状係数を使う。形状の基本量と派生量を別々に置換すると、同じ豆として両立しない寸法になる。',
'rice':'米2品種Cammeo/Osmancikの分類。面積、周長、長軸、短軸、離心率、凸包面積、外接矩形充填率を使う。軸長と離心率は同じ粒の形から計算されるので、各列が実在範囲内でも組合せは不正になり得る。',
'raisin':'レーズン2品種Kecimen/Besniの分類。面積、長軸、短軸、離心率、凸包面積、外接矩形充填率、周長を使う。同じ形状の幾何量を列単位で混ぜる問題を、米とは異なる粒形状・標本数で検証する。形状3件は関連するデータ群であり、独立した3領域の証拠とは扱わない。',
'occupancy':'室内の在室/不在分類。気温、相対湿度、照度、CO2、湿度比HumidityRatio（水蒸気と空気の質量比）を使う。HumidityRatioは気温と相対湿度から導出された量なので、独立置換すると同じ空気の状態として両立しなくなる。ID・日時は使わない。',
'grid':'4ノード電力網シミュレーションの安定/不安定分類。各参加者4名の反応時間tau1–4、電力p1–4、価格弾力性係数g1–4の12特徴を使う。p1は供給、p2–4は消費でp1=abs(p2+p3+p4)。独立置換すると電力収支が崩れる。stabはラベルを決める値なので入力から除外。実測データではなく公開シミュレーションデータである。'}
m=pd.read_csv(P/'metrics.csv'); s=pd.read_csv(P/'semantics.csv'); meta=json.loads((P/'metadata.json').read_text()); env=json.loads((P/'environment.json').read_text())
lines=['# 公開テーブル5データの少数ラベル実験','', '## 結論の範囲','', '本実験は「低相関の特徴ペアを含む公開データで、ランダムな列置換が意味制約を破るか」を測定した。**全特徴間が無相関で、しかも非線形依存だけを持つ5データを確保した実験ではない。** 無相関と独立は異なる。下の相関表から候補の適合性を判断してほしい。意味制約に関与する変数に相関がある例も含み、低相関ペアがある事実だけで、そのペアが意味破綻の原因だとはいえない。','', '提案手法は既存実装のGaussian copula条件付き置換。残した特徴に条件付けて生成する動機はあるが、厳密な幾何式・物理式を守る仕組みはなく、非単調な依存も一般には表現できない。「提案手法だから意味的に正しい」とは仮定していない。','', '## 共通条件','', '各データでラベル30件/100件、seed=11,23,37,51,67の5反復。訓練最大2000行、残りをラベルなしとして使用。通常は層化80/20のholdout、Occupancyだけは公式訓練8143行から最大2000行を抽出し、公式テスト2ファイル計12417行で評価。訓練とテストの行インデックスに重複なし。重複内容のレコードは事前除去せず、audit.jsonに一致件数を別記。MinMaxは訓練のみ、copulaはラベルなし訓練のみでfitした。','', 'copulaの周辺変換だけをバッチ化した実験用アダプタを使用し、元実装と同じ出力になることをverify_fast.pyで確認した。VIME列置換とcopula版は同じ分類器・学習予算（幅32×4層、前学習15epoch、半教師300反復、batch64、置換率0.4、3view、整合性重み1、復元重み2）。少数ラベルのみのロジスティック回帰も参考対照に含む。ハイパーパラメータをデータ別に最適化した比較ではない。各反復の分割はnpzで保存。','', '## 相関と候補の適合性','', '訓練データだけで計算。|r|<0.1を低い標本Pearson相関の目安として使用。平均値は5seed。具体的ペアはseed11。','', '|データ|総行数|特徴数|平均絶対相関|低相関ペアの割合|最も低相関のペア（r）|','|---|---:|---:|---:|---:|---|']
for name in names:
 z=meta[name]; cs=z['train_correlation']; a,b,r=cs[0]['lowest_pairs'][0]
 lines.append(f"|{names[name]}|{20560 if name=='occupancy' else z['n']}|{len(z['features'])}|{np.mean([c['mean_abs'] for c in cs]):.3f}|{np.mean([c['fraction_abs_below_point1'] for c in cs])*100:.1f}%|{a} / {b} ({r:.3f})|")
lines+=['','## 分類結果（ROC-AUC）','','平均 ± 標本標準偏差。多クラスはmacro OVR。差は同一seedでcopula−列置換。5回の差が正だった回数も示す。テストが重なる反復であり、少数seedの探索結果として読む。','','|データ|ラベル数|ラベルのみLogistic|VIME列置換|提案copula|平均差|改善seed数|','|---|---:|---:|---:|---:|---:|---:|']
summary=[]
for name in names:
 for n in [30,100]:
  sub=m[(m.dataset==name)&(m.n_labels==n)]; vals=[]
  for method in ['supervised_logistic','vime_shuffle','vime_copula']:
   v=sub[sub.method==method].auc; vals.append(f'{v.mean():.3f} ± {v.std():.3f}')
  pv=sub.pivot(index='seed',columns='method',values='auc'); delta=pv.vime_copula-pv.vime_shuffle
  lines.append(f'|{names[name]}|{n}|'+ '|'.join(vals)+f'|{delta.mean():+.3f}|{sum(delta>0)}/5|')
  summary.append(dict(dataset=name,n_labels=n,delta_auc_mean=delta.mean(),delta_auc_sd=delta.std(),positive_seeds=int(sum(delta>0))))
lines+=['','Balanced accuracyとMacro-F1、全seedの値はmetrics.csvに保存。Logisticはモデル構造が異なる参考比較で、copulaの効果を直接分離する対照はVIME列置換。','','## 意味制約の違反率','','生成診断では、ラベルなし訓練の最大1000行をアンカーとし、列置換とcopulaに同じマスクを適用。表は5seed×2ラベル条件の10診断の平均であり、独立した10実験という意味ではない。残した特徴は保存されるが、元ラベルを保つ保証は評価できていない。','','|データ|元データ|列置換|提案copula|','|---|---:|---:|---:|']
for name in names:
 vals=[s[(s.dataset==name)&(s.method==method)].violation_rate.mean()*100 for method in ['original','shuffle','copula']]; lines.append(f'|{names[name]}|'+ '|'.join(f'{v:.1f}%' for v in vals)+'|')
lines+=['','形状：短軸≤長軸、面積≤凸包面積+1、離心率eとsqrt(1−(短軸/長軸)^2)の差≤0.01。電力網：|p1+p2+p3+p4|≤0.01。室内：標準気圧101325 Pa、飽和水蒸気圧610.78 exp(17.2694T/(T+237.3))、HumidityRatio=0.62198 pv/(101325−pv)に対し相対誤差≤5%。許容差は実行前に固定。これはすべての意味的破綻を網羅する指標ではない。画素数の整数性も未評価。','','## 各データの説明と実際の破綻例','','以下はseed11・ラベル30件条件で、列置換が実際に生成した最初の違反行。架空の説明用数値ではない。全特徴値と置換列はmetadata.jsonに保存。']
for name in names:
 z=meta[name]; ex=z['example']; a=ex['original']; b=ex['augmented']
 lines+=['',f'### {names[name]}','',desc[name], '',f"出典：[UCI Dataset {ids[name]}](https://archive.ics.uci.edu/dataset/{ids[name]}/{slugs[name]})。UCI公開データはCC BY 4.0。",'', '使用列：'+', '.join(z['features'])+'。','']
 if name in ['bean','rice','raisin']:
  for label,d in [('元の行',a),('置換後',b)]:
   e=np.sqrt(max(0,1-(d['MinorAxisLength']/d['MajorAxisLength'])**2)); lines.append(f"- {label}：長軸={d['MajorAxisLength']:.3f}、短軸={d['MinorAxisLength']:.3f}、記録された離心率={d['Eccentricity']:.4f}、軸長から求めた離心率={e:.4f}、面積={d['Area']:.1f}、凸包面積={d['ConvexArea']:.1f}。")
  reasons=[]
  if b['Area']>b['ConvexArea']+1: reasons.append('物体を包む凸包の面積が物体自身の面積より小さくなっている')
  if abs(b['Eccentricity']-np.sqrt(max(0,1-(b['MinorAxisLength']/b['MajorAxisLength'])**2)))>.01: reasons.append('記録された離心率が軸長から決まる離心率と一致しない')
  lines+=['','この行の破綻：'+'。'.join(reasons)+'。']
  lines+=['','同じ形状の軸と離心率・面積を同時に説明できるかを検証した。提案手法が観測された他列を条件として使うことは合理的だが、Gaussian copulaには式の厳密な保証がない。']
 elif name=='grid':
  for label,d in [('元の行',a),('置換後',b)]: lines.append(f"- {label}："+', '.join(f'{k}={d[k]:.4f}' for k in ['p1','p2','p3','p4'])+f"、電力総和={sum(d[k] for k in ['p1','p2','p3','p4']):.4f}。")
  lines+=['','置換後は供給と消費の総和が0から外れ、元データの電力収支条件を満たさない。']
  lines+=['','供給と消費が同時に成り立つ生成を目指して条件付き生成を適用した。ただし正則化や周辺分布の逆変換により収支式は自動的には守られない。p1は冗長量なので、実用上は生成後にp1を再計算する別案もある。']
 else:
  for label,d in [('元の行',a),('置換後',b)]: lines.append(f"- {label}：気温={d['Temperature']:.3f}℃、相対湿度={d['Humidity']:.3f}%、HumidityRatio={d['HumidityRatio']:.7f}。")
  pv=b['Humidity']/100*610.78*np.exp(17.2694*b['Temperature']/(b['Temperature']+237.3)); expected=.62198*pv/(101325-pv)
  lines+=['',f'この気温・相対湿度から期待されるHumidityRatioは約{expected:.7f}で、置換値は約{abs(b["HumidityRatio"]-expected)/expected*100:.1f}%ずれている。']
  lines+=['','同じ空気状態の派生量を保つ目的で条件付き生成を適用した。物理式を知っている場合、生成後にHumidityRatioを再計算する対照も今後必要。']
 lines+=['','実際に置換した列：'+', '.join(ex['masked'])+'。']
diagnoses=json.loads((P/'low_auc_diagnosis.json').read_text())
lines+=['','## 低AUCの反復の追加診断（結果確認後）','','AUC<0.55だったVIME条件を保存した分割・同じ設定で再学習し、AUCの再現を確認した。条件の除外や設定の再調整はしていない。下表の予測種類数は、テスト行に対する確率ベクトルのユニーク行数。1なら全行に同じ予測を出したことを表す。','','|データ|seed|ラベル数|手法|AUC|予測種類数|','|---|---:|---:|---|---:|---:|']
for d in diagnoses:
 lines.append(f"|{names[d['dataset']]}|{d['seed']}|{d['n_labels']}|{d['method']}|{d['original_auc']:.3f}|{d['unique_probability_rows']}|")
lines+=['','豆30件の列置換はほぼ一定、豆100件のcopulaと米30件の列置換は完全に同じ予測になった。これらが平均差に大きく影響するため、豆・米の平均AUC差を安定した優劣とは扱わない。電力網の低AUC条件は予測が変動しており、同じ原因と断定できない。元特徴でのLogisticがより高いAUCを出していることから、今回のVIMEの学習設定・表現・整合性制約の検討が必要。エンコーダ出力のばらつきなどはlow_auc_diagnosis.jsonに保存。','','分割監査では、豆のテスト2723行中2〜6行で、訓練に同一の特徴値を持つレコードがあった。行番号は異なるが元データの重複内容によるもので、スコアが楽観的になる可能性がある。他の通常分割3データでは一致なし。Occupancyは公式分割を使用。豆は重複をグループとして分割する追加確認が必要。']
lines+=['','## 研究上の解釈','','この5件から「完全に無相関なデータに提案法が効く」とは結論できない。形状3件には強相関な派生量も含む。電力網では多くの特徴ペアの相関が弱くても、電力収支に関与する特徴には依存がある。低相関・非線形依存に対する本格的な検証には、依存そのものを持つ変数集合の選定、非線形依存の診断、Gaussian以外の条件付き生成器との比較が必要。','','また、意味制約の違反が減っても分類AUCが上がるとは限らない。派生量は生成後に再計算するだけで整合性を回復できる場合があり、それを行う制約付きベースラインとの比較なしに提案法の必要性は主張しない。VIME原論文の全実験再現でもない。','','## 再現','','専用環境：Python '+env['python']+'、torch '+env['torch']+'、numpy '+env['numpy']+'、scipy '+env['scipy']+'、scikit-learn '+env['sklearn']+'。実行時間 '+f"{env['seconds']/60:.1f}"+' 分。','','リポジトリルートで `.venv312/bin/python`（この実験フォルダ内）から `run.py`、その後 `report.py` を実行。requirements.txtに環境を固定。データ元URLとSHA256、全分割、全反復結果を保存。']
(P/'実験レポート.md').write_text('\n'.join(lines)+'\n'); pd.DataFrame(summary).to_csv(P/'paired_summary.csv',index=False)
print('\n'.join(lines[:65]))
