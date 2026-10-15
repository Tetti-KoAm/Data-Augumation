from pathlib import Path
import json
import numpy as np,pandas as pd
P=Path(__file__).resolve().parent
NAMES={'bean':'豆（Dry Bean）','rice':'米（Rice）','raisin':'レーズン（Raisin）','occupancy':'室内在室（Occupancy）','grid':'電力網（Grid）'}
METHODS={'vime':'標準VIME','class_conditioned':'論文・クラス条件付き','proposed_copula':'提案・VIME copula'}
M=pd.read_csv(P/'metrics.csv'); assert len(M)==120 and (M.groupby(['dataset','method']).size()==8).all(); C=pd.read_csv(P/'controlled_semantics.csv'); E=json.loads((P/'environment.json').read_text()); T=json.loads((P/'timing.json').read_text())
lines=['# 論文条件を適用した公開5データ・3手法の比較','', '## この実験で比較したもの','', '提供された日本語要約PDF（Cui et al., arXiv:2404.17489）を確認し、原論文4.1節/Table 1と著者コードを照合した。**標準VIME、論文のクラス条件付き拡張＋対照学習、提案するVIME＋Gaussian copula**を、同じデータ分割で比較した。','', '今回は前学習500epoch、幅256・4層エンコーダ、ラベル率30%、著者の8seedを用いる。前回のラベル30件/100件・幅32・15epochとは別の実験であり、前回の数値と直接混ぜて比較しない。**ラベル30%は「ラベル30件」ではない。**','', '参照：[原論文](https://arxiv.org/html/2404.17489v1)、[著者コード](https://github.com/layer6ai-labs/Tabular-Class-Conditioned-SSL)。使用コミット：9ee368b647c6bc603cf2f2fed582804bca9b120d。提供PDFのSHA256はenvironment.jsonに保存。','', '置換値を採る条件は3通り。標準VIMEは同じ列から無条件、論文手法は同じ推定クラスの列から独立にサンプリング、提案copulaは残した特徴の値を条件として置換列を同時にサンプリングする。今回のcopulaはクラスで分けて推定する方式ではない。','', '## 条件の対応と変更点','', '|条件|今回の扱い|','|---|---|','|エンコーダ|3手法とも幅256・4層。論文手法は著者のモデル定義をそのまま読み込む|','|前学習|全手法500epoch。ただしVIMEはマスク推定＋復元、論文手法はInfoNCE|','|下流学習|論文は分類ヘッド100epoch。VIMEは100×ceil(ラベル数/256)回の更新（重複を許すランダム抽出での100epoch相当の提示予算）|','|ラベル率・反復|訓練の30%を一様ランダム選択。著者の8seed。全手法で同じ行を共有|','|ミニバッチ・最適化|batch256、Adam lr0.001、置換率0.4|','|疑似ラベル|論文手法のみ。10epochごとに既知ラベルで分類ヘッドを100epoch再学習、疑似ラベルを更新|','|訓練行数|前回の2000行上限を撤廃。通常は層化80/20|','|室内センサー|時系列の混入を避けて公式訓練/テスト分離を維持。論文の80/20とは異なる|','|豆の重複|同じ特徴値を持つ68行を分割前に除去（異なるラベルの衝突なし）。13,543行を使用|','|前処理|論文手法は訓練でfitしたStandardScaler。VIME2手法はsigmoid復元に合わせて訓練fitのMinMax|','|分類ヘッド|論文手法は著者の1隠れ層、VIME2手法は既存実装の2隠れ層。幅はいずれも256|','|マスク|論文は各行ceil(0.4×特徴数)列、VIME2手法は列ごとに確率0.4|','', 'VIME2手法は同じ設定・構造で、拡張器だけが異なる。論文手法との比較は、前処理・学習目的・分類ヘッド・計算量も異なる**手法全体の比較**であり、差のすべてを拡張器の差と解釈できない。論文の高相関/低相関マスクという追加アブレーションは今回は含めない。','', '論文手法では、初期疑似ラベル用の100epoch、前学習中50回×100epoch、最後の100epochの分類ヘッド学習を行う。各回で分類ヘッドを再初期化する著者コードの挙動も維持した。VIME2手法の自己教師学習・copula推定はラベルなし訓練のみ、論文手法の対照学習は全訓練特徴を利用する。','', '## データ別の行数','', '|データ|訓練|ラベルあり|ラベルなし|テスト|特徴数|クラス数|','|---|---:|---:|---:|---:|---:|---:|']
for name,title in NAMES.items():
 r=M[M.dataset==name].iloc[0]; lines.append(f"|{title}|{r.n_train}|{r.n_labeled}|{r.n_unlabeled}|{r.n_test}|{r.n_features}|{r.n_classes}|")
info=json.loads((P/'dataset_info.json').read_text())
sources={'bean':(602,'dry+bean'),'rice':(545,'rice+cammeo+and+osmancik'),'raisin':(850,'raisin'),'occupancy':(357,'occupancy+detection'),'grid':(471,'electrical+grid+stability+simulated+data')}
lines+=['','### 公開データの出典と全使用列','']
for name,title in NAMES.items():
 id,slug=sources[name]; lines.append(f"- [{title}（UCI {id}）](https://archive.ics.uci.edu/dataset/{id}/{slug})："+', '.join(info[name]['features'])+'。')
lines+=['','5データはUCIのCC BY 4.0公開データ。豆のAspectRationは元ARFFの列名表記で縦横比を意味する。入力列のアンダースコアは比較コードで省略している。電力網は実測ではなく公開シミュレーションデータ。','','### 今回の訓練行における相関','', '各seedの訓練特徴だけでPearson相関を計算し、その記述統計を8seedで平均した。|r|<0.1は低い標本相関の目安であり、独立性の検定ではない。意味制約に関与する変数には強い依存もある。','','|データ|平均絶対相関|低相関ペアの割合|','|---|---:|---:|']
for name,title in NAMES.items():
 c=info[name]['per_seed_correlation']; lines.append(f"|{title}|{np.mean([d['mean_abs_pearson'] for d in c]):.3f}|{np.mean([d['low_correlation_fraction'] for d in c])*100:.1f}%|")
lines+=['', '使用特徴量・データ出典は前回と同じ。豆/米/レーズンは粒の形状から品種を分類。室内は気温・相対湿度・照度・CO2・HumidityRatioから在室判定。電力網は反応時間tau1–4・電力p1–4・価格弾力性g1–4から安定判定。ID・日時・電力網のstab（ラベルを直接決める値）は除外した。','', '## 分類結果','', '平均 ± 標本標準偏差（8seed）。Accuracyを論文に合わせて主指標とし、ROC-AUCも併記する。AUCは多クラスmacro OVR。全seedを除外せず集計。','']
summary=[]
for metric,label,scale in [('accuracy','Accuracy（%）',100),('auc','ROC-AUC',1),('balanced_accuracy','Balanced accuracy',1),('macro_f1','Macro-F1',1)]:
 lines += ['### '+label,'','|データ|'+'|'.join(METHODS.values())+'|','|---|---:|---:|---:|']
 for name,title in NAMES.items():
  vals=[]
  for method in METHODS:
   v=M[(M.dataset==name)&(M.method==method)][metric]*scale; vals.append(f'{v.mean():.3f} ± {v.std():.3f}'); summary.append(dict(dataset=name,method=method,metric=metric,mean=float(v.mean()/scale),std=float(v.std()/scale)))
  lines.append('|'+title+'|'+'|'.join(vals)+'|')
 lines.append('')
constant=M[M.unique_probability_rows==1]
lines+=['全テスト行に同じ確率ベクトルを返した条件は'+str(len(constant))+'/120。該当条件はaudit.jsonに記録し、除外しない。','']
lines+=['## 同じseed間の対応差','','差は左の手法−右の手法。区間は8組の差を10,000回percentile bootstrapした探索的95%区間。反復holdoutは重複し、複数のデータ・手法を比較しているため、確証的な有意差とは扱わない。','','|データ|比較|Accuracy差（ポイント）と95%区間|AUC差と95%区間|AUC改善seed数|','|---|---|---|---|---:|']
paired=[]
for name,title in NAMES.items():
 for a,b in [('class_conditioned','vime'),('proposed_copula','vime'),('proposed_copula','class_conditioned')]:
  cells=[]; positive=0
  for metric,scale in [('accuracy',100),('auc',1)]:
   pv=M[M.dataset==name].pivot(index='seed',columns='method',values=metric); delta=(pv[a]-pv[b]).to_numpy(); rng=np.random.default_rng(20261015); bs=delta[rng.integers(0,len(delta),(10000,len(delta)))].mean(1); lo,hi=np.quantile(bs,[.025,.975]); positive=int((delta>0).sum())
   cells.append(f'{delta.mean()*scale:+.3f} [{lo*scale:+.3f}, {hi*scale:+.3f}]'); paired.append(dict(dataset=name,method_a=a,method_b=b,metric=metric,mean_difference=float(delta.mean()),ci_low=float(lo),ci_high=float(hi),positive_seeds=positive))
  lines.append(f'|{title}|{METHODS[a]} − {METHODS[b]}|'+'|'.join(cells)+f'|{positive}/8|')
lines+=['','## 同じアンカー・同じマスクでの意味制約診断','','分類器のテスト成績とは別に、ラベルなし訓練から一様抽出した同じ最大1000行・同じceil(0.4×特徴数)列のマスクを使って生成器を比較した。列置換対照はラベルなし訓練全体から独立に値を採る。論文方式は、既知ラベルと最終疑似ラベルでアンカーと同じクラスに割り当てた訓練行から値を採る。copulaはラベルなし訓練で推定する。VIMEの学習中はBernoulliマスク・ミニバッチ内列シャッフルのため、この診断はVIMEの学習中の生成をそのまま再現するものではない。','', '|データ|元データ|独立列置換|論文の同クラス列置換|提案copula|','|---|---:|---:|---:|---:|']
for name,title in NAMES.items():
 vals=[C[(C.dataset==name)&(C.method==method)].violation_rate.mean()*100 for method in ['original','vime','class_conditioned','proposed_copula']]; lines.append('|'+title+'|'+'|'.join(f'{v:.1f}%' for v in vals)+'|')
lines+=['','違反の大きさも別に示す。形状は離心率の絶対誤差、室内はHumidityRatioの相対誤差、電力網は電力総和の絶対値。単位が異なるためデータを横断して平均しない。形状の面積逆転は上の違反率に含むが、この残差は離心率だけの指標である。','','|データ|独立列置換の平均残差|同クラス列置換の平均残差|copulaの平均残差|','|---|---:|---:|---:|']
for name,title in NAMES.items():
 vals=[C[(C.dataset==name)&(C.method==method)].mean_residual.mean() for method in ['vime','class_conditioned','proposed_copula']]; lines.append('|'+title+'|'+'|'.join(f'{v:.4f}' for v in vals)+'|')
lines+=['','違反の定義は前回と同じ。形状：短軸≤長軸、面積≤凸包面積+1、離心率とsqrt(1−(短軸/長軸)^2)の差≤0.01。電力網：|p1+p2+p3+p4|≤0.01。室内：標準気圧で気温・相対湿度から計算したHumidityRatioに対し相対誤差≤5%。式・許容差を結果に合わせて変更していない。これは評価した制約だけの違反率で、全意味制約やラベル保存を保証する指標ではない。面積など画素数の整数性は評価しておらず、copulaで小数になる問題も残る。','', '同じクラスに制限しても、各列を独立に混ぜれば、軸長と離心率、面積と凸包、気温・湿度と湿度比、電力収支が整合する保証はない。copulaにも厳密な式制約は実装していない。','', '### 論文方式で実際に生じた破綻例','', '最初のseed 614579で最初に違反した行を保存（説明用の架空値ではない）。全特徴値はclass_conditioned_examples.jsonに保存。']
examples=json.loads((P/'class_conditioned_examples.json').read_text())
for name,ex in examples.items():
 a=ex['original']; b=ex['class_conditioned']; lines+=['','**'+NAMES[name]+'**','']
 if name in ['bean','rice','raisin']:
  for title,d in [('元の行',a),('同クラス置換後',b)]:
   expected=np.sqrt(max(0,1-(d['MinorAxisLength']/d['MajorAxisLength'])**2)); lines.append(f"- {title}：長軸{d['MajorAxisLength']:.3f}、短軸{d['MinorAxisLength']:.3f}、離心率{d['Eccentricity']:.4f}（軸長からの計算値{expected:.4f}）、面積{d['Area']:.1f}、凸包面積{d['ConvexArea']:.1f}。")
  reasons=[]
  if b['Area']>b['ConvexArea']+1: reasons.append('物体を包む凸包が物体自身より小さい面積になっている')
  if b['MinorAxisLength']>b['MajorAxisLength']: reasons.append('短軸が長軸より長くなっている')
  if abs(b['Eccentricity']-np.sqrt(max(0,1-(b['MinorAxisLength']/b['MajorAxisLength'])**2)))>.01: reasons.append('軸長から決まる離心率と記録された離心率が一致しない')
  lines+=['','この行の矛盾：'+'。'.join(reasons)+'。']
 elif name=='grid':
  for title,d in [('元の行',a),('同クラス置換後',b)]: lines.append('- '+title+'：'+', '.join(f'{k}={d[k]:.4f}' for k in ['p1','p2','p3','p4'])+f"、総和{sum(d[k] for k in ['p1','p2','p3','p4']):.4f}。")
  lines+=['','置換後の電力総和が0から外れ、供給と消費が一致していない。']
 else:
  for title,d in [('元の行',a),('同クラス置換後',b)]: lines.append(f"- {title}：気温{d['Temperature']:.3f}℃、相対湿度{d['Humidity']:.3f}%、HumidityRatio={d['HumidityRatio']:.7f}。")
  pv=b['Humidity']/100*610.78*np.exp(17.2694*b['Temperature']/(b['Temperature']+237.3)); expected=.62198*pv/(101325-pv)
  lines+=['',f'この気温・相対湿度で期待されるHumidityRatioは約{expected:.7f}であり、置換値は約{abs(b["HumidityRatio"]-expected)/expected*100:.1f}%ずれる。']
 lines+=['','置換列：'+', '.join(ex['masked'])+'。']
lines+=['','## 実装の検証・限界','','著者モデルは固定ソースから直接読み込み、InfoNCEのcosine計算だけを正規化行列の積に置換した。元の損失と勾配が数値的に一致することをverify.pyで確認。固定エンコーダの分類時は表現をキャッシュして同じ100epochのヘッド更新を実行。カテゴリ列を含むデータへの適用は今回検証していない。','', '著者コードではサンプラーが行順を変えた後も、既知ラベル位置のmaskは元の順のまま残る。今回は元行インデックスでラベル位置を管理する数値データ用adapterで修正した。未知ラベルはfitへの入力で-1にし、既知ラベル保持・同クラスドナー・非置換列の不変性を検証している。乱数の消費順や実装上の調整もあるため、著者main.pyの無変更実行による完全再現とは呼ばない。詳細はPROTOCOL.md。','', 'VIMEは本リポジトリのPyTorch再実装であり、公式コードをそのまま実行した結果ではない。今回の5データは「全特徴が無相関な5データ」ではない。形状3データは近縁の特徴設計であり、5つの独立した領域の証拠としては扱わない。前回の相関診断どおり、電力網では低相関ペアが多いが、形状などには強相関の派生量も含む。相関が小さいことと独立は同義ではない。','', '意味制約違反の減少、元ラベルの保存、分類性能の改善は別の論点である。物理式・幾何式が既知なら、派生量を再計算する制約付き生成も比較候補となる。Gaussian copulaの一般的な優位性をこの5件だけで主張しない。クラス条件と特徴の依存を同時に使う生成（クラス条件付きcopulaなど）は次の検討候補だが、今回の提案版には組み込んでいない。','', '## 再現と保存物','','`run.py` が主実験、`class_conditioned.py` が論文adapter、`verify.py` が一致・不変性検証、`controlled_semantics.py` が共通マスク診断、`audit.py` が保存結果の監査、`report.py` が本レポート。`metrics.csv` は全120学習、`paired_summary.csv` は対応差、`runs/データ_seed/` に分割・予測確率・正解・全学習曲線・各条件の結果を保存。','', f"Python {E['python']}、torch {E['torch']}、numpy {E['numpy']}、scikit-learn {E['sklearn']}。主実験は{E['workers']}プロセス、各CPU 1thread、経過時間{T['wall_seconds']/60:.1f}分。並列実行のため各手法の経過秒数の和と全体時間は一致しない。"]
# Explicit data-by-data interpretation based only on completed paired results.
interpret=['## データ別の読み方','']
for name,title in NAMES.items():
 means=M[M.dataset==name].groupby('method')[['accuracy','auc']].mean(); winner=means.auc.idxmax(); awinner=means.accuracy.idxmax(); da=means.loc['proposed_copula','auc']-means.loc['vime','auc']; dc=means.loc['proposed_copula','auc']-means.loc['class_conditioned','auc']
 interpret.append(f"- **{title}**：平均Accuracyが最大なのは{METHODS[awinner]}、平均AUCが最大なのは{METHODS[winner]}。提案版のAUC差は標準VIME比{da:+.3f}、論文手法比{dc:+.3f}。8seedの平均順位であり、後掲の対応差区間と各seedのばらつきも合わせて判断する。")
idx=lines.index('## 同じseed間の対応差'); lines[idx:idx]=interpret+['']
accuracy_leaders=M.groupby(['dataset','method']).accuracy.mean().unstack().idxmax(axis=1)
auc_leaders=M.groupby(['dataset','method']).auc.mean().unstack().idxmax(axis=1)
headline=['## 結果の要点','',f"平均Accuracyでは論文のクラス条件付き手法が{int((accuracy_leaders=='class_conditioned').sum())}/5データで最大だった。ただし平均順位はすべてのデータで有意な優位性を意味せず、対応差区間も確認する必要がある。",'', '平均AUCが最大の手法は、'+'、'.join(NAMES[n]+': '+METHODS[auc_leaders[n]] for n in NAMES)+'。','', 'copulaは共通マスク診断で幾何・湿度・電力収支の平均残差を減らしたが、分類性能の一貫した優位性は確認できなかった。意味制約の整合性と分類に役立つことは別々に評価すべき、という結果になった。','']
lines[2:2]=headline
(P/'比較レポート.md').write_text('\n'.join(lines)+'\n'); pd.DataFrame(summary).to_csv(P/'summary.csv',index=False); pd.DataFrame(paired).to_csv(P/'paired_summary.csv',index=False)
print(M.groupby(['dataset','method'])[['accuracy','auc']].mean().round(4).to_string())
