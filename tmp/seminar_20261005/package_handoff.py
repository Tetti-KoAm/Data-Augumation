from pathlib import Path
import shutil,json,hashlib,zipfile,py_compile,tempfile,subprocess,sys
PROJECT=Path.cwd()
BASE=PROJECT/'output/handoff'
PACK=BASE/'コピュラ研究_引き継ぎ_20261004'
PACK.mkdir(exist_ok=False)
ignore=shutil.ignore_patterns('__pycache__','*.pyc','.git','.DS_Store','.venv','venv')
shutil.copytree(PROJECT/'research-bench',PACK/'research-bench',ignore=ignore)
shutil.copytree(PROJECT/'output/presentations/比較実験',PACK/'output/presentations/比較実験',ignore=ignore)
shutil.copytree(PROJECT/'output/experiments/dependence_comparison',PACK/'output/experiments/dependence_comparison',ignore=ignore)
pres=PACK/'output/presentations'
for name in ['10.05_ゼミ発表_コピュラ進捗_流れ改善版_本編20枚.pptx','流れ改善版_発表ガイド.md']:
 shutil.copy2(PROJECT/'output/presentations'/name,pres/name)
ref=PACK/'参考資料';ref.mkdir()
shutil.copy2(Path('/Users/kouta/Library/CloudStorage/OneDrive-個人用/大学院/研究/10.05＿齊藤光汰.pptx'),ref/'10.05＿齊藤光汰_元資料.pptx')
# Minimal dependency set for the two-method comparisons. Keep full original locks too.
(PACK/'requirements.txt').write_text('numpy==2.5.3\nscipy==1.18.1\nscikit-learn==1.9.1\ntorch==2.14.1\nmatplotlib==3.11.2\n')
(PACK/'requirements-compatible.txt').write_text('numpy>=2.0,<3\nscipy>=1.12,<2\nscikit-learn>=1.4,<2\ntorch>=2.2,<3\nmatplotlib>=3.8,<4\n')
readme='''# 別のPCで研究を続けるための手順

## まず行うこと

1. ZIPを展開する。展開後の「コピュラ研究_引き継ぎ_20261004」フォルダ全体を保存する。
2. そのPCのCodexで、このフォルダをプロジェクトとして開く。
3. 下の文章を、新しいチャットの最初のメッセージに貼る。

```text
このフォルダの「研究引き継ぎ.md」を読み、研究の目的、私が理解できていること、スライドの制約、実装と実験結果、未解決の課題を引き継いでください。
次に「output/presentations/流れ改善版_発表ガイド.md」と「output/experiments/dependence_comparison/実験レポート.md」を読み、現在の状態を短く確認してください。
最初の4枚のスライドは変更しないでください。本編は20枚程度、補足は必要なだけという構成を維持してください。
実験の追加実行や資料の変更は、これから私が依頼する内容に沿って進めてください。
ファイルの場所は以前のPCの /Users/kouta/... ではなく、今開いているプロジェクトフォルダを基準に探してください。
```

会話の引き継ぎと、ファイルの受け渡しをこのフォルダにまとめた。Python環境を作らなくても、PowerPointと実験レポート・図は開ける。

## 入っているもの

- `研究引き継ぎ.md`：研究の目的、説明で大事にした流れ、実装、最新結果、次の課題。
- `output/presentations/`：本編20枚＋補足29枚の最新版と発表ガイド。
- `参考資料/`：最初の4枚を保持するための元のPowerPoint。
- `output/presentations/比較実験/`：Breast Cancer・Wineの比較、2変量の動作確認。
- `output/experiments/dependence_comparison/`：相関を制御した追加実験、結果、図、レポート、診断コード。
- `research-bench/src/`：VIME再実装と列置換・Gaussian copulaの実装。
- `research-bench/upstream/`：先行研究の参照コード。Git管理情報は除外し、元リビジョンの記録はUPSTREAM_VERSIONS.mdに保持。
- `ファイル一覧とSHA256.json`：受け渡したファイルの一覧とチェックサム。

追加の強相関実験は、PowerPointへまだ反映していない。最新の研究結果は「研究引き継ぎ.md」と追加実験レポートを優先する。

## 実験を再実行する場合

Python 3.12を用意し、展開したフォルダをターミナルの作業フォルダにする。仮想環境そのものはOS・PCに依存するため同梱していない。

macOS / Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python output/presentations/比較実験/run_experiment.py
python output/experiments/dependence_comparison/run_dependence_comparison.py
python output/experiments/dependence_comparison/check_baseline.py
python output/experiments/dependence_comparison/diagnose_seed37.py
python output/experiments/dependence_comparison/plot_results.py
python output/experiments/dependence_comparison/write_report.py
```

Windows PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe output/presentations/比較実験/run_experiment.py
.\.venv\Scripts\python.exe output/experiments/dependence_comparison/run_dependence_comparison.py
.\.venv\Scripts\python.exe output/experiments/dependence_comparison/check_baseline.py
.\.venv\Scripts\python.exe output/experiments/dependence_comparison/diagnose_seed37.py
.\.venv\Scripts\python.exe output/experiments/dependence_comparison/plot_results.py
.\.venv\Scripts\python.exe output/experiments/dependence_comparison/write_report.py
```

保存済みの結果を残すには、再実行用にフォルダのコピーを作ってから実行する。スクリプトは同じフォルダの結果ファイルを更新する。主実験は元のMacで既存データ比較が約8分半、追加実験が約10分だった。別のPCでの実行時間や数値の完全一致は保証しない。

固定バージョンがそのPCへインストールできない場合は、`requirements-compatible.txt`で互換範囲の環境を作り、実際のバージョンを記録する。この場合、元の実験環境と同一ではない。追加実験フォルダには元の環境の全pip freezeも保存してある。

上の手順は今回使った2手法の再実行用。`research-bench/scripts/quick_compare.py`の3手法比較や上流の原実装には、別途research-benchの依存関係が必要になる。
'''
(PACK/'README_最初に読む.md').write_text(readme)
handoff='''# コピュラ研究の引き継ぎ

作成：2026年10月4日。元のチャットで合意した研究の目的、説明上の要望、実装と結果をまとめた継続用の文書。会話の逐語録ではない。

## ユーザーの目的と発表の事情

齊藤光汰さんの大学院研究。10月5日の研究室ゼミで、前回の中間発表以降の進捗を教授と大学院2年生へ説明する。前回は問題設定を示し、「コピュラを使う予定」で終わった。今回の主目的は研究とコピュラを理解してもらうこと。実験結果は二の次だが、コードを動かした比較も示したい。

研究対象は表形式データの半教師あり学習とデータ拡張。独立に各列を置き換えると、列単体は妥当な値でも特徴の組合せが不自然になり得る。残す特徴を条件として置換する特徴を生成するため、コピュラを検討している。まず同じVIME実装内の置換器だけを変更して比較した。

特徴を条件にする方法は擬似ラベルを必要としないが、分類ラベルを保つことを保証しない。元資料にある確証バイアス等の問題設定は研究上の仮説を含むため、解決済みと書かない。

## スライドに関する必須条件

元のファイルは参考資料/10.05＿齊藤光汰_元資料.pptx。最初の4枚を一切変更しない。元の3・4枚目のデザインを参考にする。

現在の最新版はoutput/presentations/10.05_ゼミ発表_コピュラ進捗_流れ改善版_本編20枚.pptx。本編20枚（元の4枚を含む）、21〜49枚目が補足29枚。最初の4枚と依存パーツ44個の内容は元資料とバイト単位で同一。書き出した最初の4枚の画像も同一と確認した。ネイティブPowerPointアプリでの操作検証は行っていない。

ユーザーは「各スライドが単独で完結し、前後の流れが読み取れない」と指摘した。そのため、単に情報を減らすのではなく、前ページの疑問を次ページで答える構成へ変更した。各ページの上部に前ページからのつながり、下部に次の問いを置き、発表者ノートにもつなぎの言葉と説明・出典を書いた。

本編の流れ：

- 1〜4：前回の問題設定をそのまま保持。
- 5〜8：体重70kgが分かり、身長が未知の人をどう推測するか。近傍法、条件付き分布、値の分布と組合せの違い。
- 9〜12：累積確率の位置、位置の組、コピュラの定義、Sklarの定理。
- 13〜16：Gaussian copula、学習、条件付き生成、cmへ戻す数値例。
- 17〜20：VIMEへの接続、合成動作確認、Breast Cancer/Wine分類結果、課題。
- 21〜49：定義の細部、独立uv/同順位min、種類、潜在空間生成との違い、先行研究、実験条件、実装、文献。

重要：強相関の追加実験は最新版のPPTXにもまだ反映していない。スライド19の分類比較はBreast Cancer/Wineの前の結果。新しい実験を資料へ入れる場合は、研究の最新課題と結論も整合させる。本編の約20枚という希望と最初の4枚保持を維持する。

## ユーザーがつまずいた点と説明の方針

「周辺分布と依存を分けて表す」「累積確率で表した位置」「C(u,1)=u」「独立ならuv」「完全に同じ位置ならmin」の数式を理解しづらいと感じている。具体例を先にし、一つの例から数式へ進む。記号や変換を突然出さず、何のために導入するかを説明する。

直近の重要な疑問は「生の身長・体重を散布図に描き、似た体重の人から身長を推測するのと何が違うか」。回答は、目的は同じ条件付き推測・生成で、近傍法は近い実測行を使い、コピュラ法は全体から推定した同時モデルを条件付けるという違い。近傍法も有効な比較対象で、コピュラの一律の優位を主張しない。

確率位置への変換は、生の図で依存が見えないから行うのではない。周辺分布を共通の一様分布にして依存を表すため。狭義単調増加変換は順位を保つが距離や図形は変え得るため、生の散布図と一般に全く同じ図にはならない。

## 数学の核

Xは身長、Yは体重。F_X(x)=P(X≤x)、F_Y(y)=P(Y≤y)。位置U=F_X(X)、V=F_Y(Y)。周辺が連続なら各々Uniform(0,1)になるが、独立とは限らない。離散や有限経験分布では連続一様になる説明をそのまま当てはめない。

コピュラC(u,v)=P(U≤u,V≤v)は一様周辺を持つ同時CDF。散布点の集合や相関係数そのものとは区別する。C(u,1)=uはV≤1が必ず成立するため。独立ではP(U≤u)P(V≤v)=uv。同じ位置V=Uなら二つの条件がU≤min(u,v)となりC=min。

Sklar：H(x,y)=C(F_X(x),F_Y(y))。連続周辺ならCは一意。生成は位置の組を作り、X=F_X^{-1}(U)、Y=F_Y^{-1}(V)で戻す。

Gaussian copula：Z_j=Φ^{-1}(F_j(X_j))、Z~N(0,R)と仮定する。Φは標準正規CDF。元のXが多変量正規である必要はないが、変換後の依存がGaussianという仮定は必要。任意の非線形依存、U字関係、非対称の裾依存を表す保証はない。

2変量の例：体重70kgの位置v=.7、z_y=Φ^{-1}(.7)≈.524、ρ=.6。Z_x|Z_y=z_y~N(ρz_y,1−ρ²)、平均≈.315、標準偏差.8。ε~N(0,1)を引きz_x=.315+.8ε、u=Φ(z_x)、身長=F_X^{-1}(u)。説明用の身長周辺N(170,10²)ならε=-1,0,1で約165.2,173.2,181.2cm。3値の等確率選択ではない。

多変量は残す列Oと置換列Mに分け、μ=R_MO R_OO^{-1}z_O、Σ=R_MM−R_MO R_OO^{-1}R_OM。Mを同時に引き、生成列間の関係も考慮する。

種類：Gaussianは扱いやすい条件付き多変量生成。tは上下両側の裾依存。Claytonは通常形の正依存で下側、Gumbel/Joeは上側、Frankは漸近的な上下の裾依存係数0。Vineはペアを組み合わせる構成法。優劣は目的、標本数、真の関係、推定の安定性に依存する。Gaussianの非退化な相関では裾依存係数0だが、有限の端領域で無関係とは言わない。

## 現在の実装

research-bench/src/tabular_research/corruption.py：

- ColumnShuffleCorruptorは各列をバッチ内で独立に並べ替え、mask=Trueの値だけを置換。
- GaussianCopulaCorruptor.fitは訓練列の平均順位u=(r−.5)/nを逆正規変換し、潜在相関を推定。対角縮小0.05とjitter1e−6で安定化。
- 呼び出しはcopula(x,mask,rng)。各行の観測値を条件に、マスク列を多変量で同時生成。観測列は保持。全列マスクは無条件生成、マスクなしは変更なし。
- 逆変換は経験分位点の線形補間。未観測の値もあり得て、周辺を有限標本で厳密に完全保存とは言わない。
- 現在の対象は有限な連続数値。カテゴリや順序変数へのそのままの補間は不適切。クラス保持を保証しない。

research-bench/src/tabular_research/vime_torch.py：自己教師ありのマスクBCE＋復元MSE（重み2）、前学習後にエンコーダを固定し、ラベルありCE＋ラベルなし3viewのlogit分散による一貫性（重み1）で予測器を学習。これは原論文全設定の完全再現ではなくPyTorch再実装。fit時のcopula推定はラベルなし訓練のみ。

## 前の実験とスライドに載っている値

output/presentations/比較実験/。訓練80/20層化、訓練内ラベルあり30%、seed11,23,37,51,67。4層×32、前学習15epoch、半教師あり300反復、batch64、mask.4、CPU1thread。

Breast Cancer AUC：列置換0.970±0.012、copula0.973±0.017、平均差+.003、差区間[−.005,+.011]。Wine：.826±.068と.847±.130、差+.021、区間[−.079,+.109]。両区間0を含み、性能改善の実証ではない。再実行の全seed AUCは元の保存結果と一致した。

2変量の動作確認はρ=.8、2500行。元/列置換/copulaの相関.805/−.014/.761。推定と生成が同じデータなので汎化評価ではない。

## 最新の追加実験（このチャットで最後に実行）

ユーザーの仮説：「分類の差が小さいのは、特徴がすでに独立しているからではないか。もっと特徴間の関係があるデータで比較してほしい」。

まず既存データを検査。Breast Cancerの平均絶対Pearson相関.395、最大.998、相関絶対値.7超のペア16.1%。Wineは平均.305、最大.865、.7超2.6%。すべて独立という仮説は成り立たない。低い相関を独立の証拠にはしない。

output/experiments/dependence_comparison/に追加実験を保存。1000行・12列、X_j=√ρS+√(1−ρ)ε_j、Sとε_jは独立標準正規。各列の周辺は標準正規、異なる列の理論相関ρ。ρ=0,.5,.9で依存の強さを変える。

平均の課題：T=ΣX_j/√[12(1+11ρ)]。差の課題：T=(X_1−X_2)/√[2(1−ρ)]。y=1[T+.35η>0]。平均の課題を全ρ、差の課題をρ=.9で実施。どちらもTの分散を1にそろえた。各条件5回、反復ごとに新しい標本を生成、2手法は同じ標本・分割を共有。240ラベルあり、560ラベルなし、200テスト。学習設定は前の比較と同じ。計40fit、約606秒。

|条件|列置換AUC|copula AUC|
|---|---|---|
|独立・平均|.582±.080|.632±.097|
|相関.5・平均|.871±.207|.871±.208|
|相関.9・平均|.962±.013|.871±.208|
|相関.9・差|.492±.025|.499±.017|

相関.9・平均の差区間は約[−.271,−.00056]で負側。他の3条件は0を含む。5反復の探索的bootstrapであり、一律の統計的優位や劣位を断言しない。

相関.9・平均の置換後の平均絶対相関：元.898、列置換.340、copula.882。雑音を加える前の既知の分類境界をまたぐ割合：列11.0%、copula5.3%。関係保持にははっきり差があるが、分類効果は改善しなかった。

相関.9・差の課題：元相関.902、列置換.330、copula.886。境界変更率は26.2%と25.6%で近い。共通の相関を保っても、小さな差が決めるクラスの意味を保てるとは限らない。

真の条件平均からの残差二乗/真の条件分散は、正しく生成する場合の期待値1を基準に見る（0がよい指標ではない）。相関.9・平均では元1.037、列16.406、copula1.431。copulaにも推定・生成の誤差が残る。

線形診断：同じラベルあり行だけのStandardScaler＋LogisticRegression(C=10)は全4条件AUC約.96。課題自体は分類可能だが、モデル・目的関数が違うため置換器の直接対照ではない。

失敗の追加診断：相関.9・平均のseed37のcopula AUCは.5。同じ条件で再実行して一致。エンコーダ出力の座標標準偏差の平均≈6.3e−8、予測確率は全200行で同じ値。固定表現にロジスティック回帰を当ててもAUC.5。列置換側は出力標準偏差≈.137、AUC≈.950。表現がほぼ一定になったことは観測事実だが、なぜそうなったかはまだ特定していない。失敗反復を除外していない。

## 次の課題と避けるべき結論

関係の有無、生成による関係保持、クラスの意味の保持、分類の学習効果を分けて評価する。今回の結果から「コピュラで分類が良くなった」「全体の特徴相関が強ければ有利」「確証バイアスを解決済み」とは言わない。

候補は近傍から行をまとめて採る生成との比較、前学習表現が一定になる原因の診断、マスク率・一貫性強度・前学習予算の検証。調整は検証用データで行い、テストを見て有利な設定やseedだけを選ばない。Gaussianに合う合成データなので、非Gaussianの関係や実データへの一般化は別に評価する。

追加実験をスライドへ反映するなら「関係保持を確認したが、分類改善は未確認。表現の安定性と分類情報の保持が課題」という結論にそろえる。ユーザーは具体例と前後の流れを最重視する。

## 参照した主要文献

- Haugh, An Introduction to Copulas：https://www.columbia.edu/~mh2078/QRM/Copulas_MasterSlides.pdf
- Segers, Fundamentals of copulas：https://www.columbia.edu/~rf2283/Conference/1Fundamentals%20%281%29Seagers.pdf
- Schmidt, Copulas：https://people.math.ethz.ch/~embrecht/ftp/copulas.pdf
- Demarta & McNeil (2005), t copula：https://doi.org/10.1111/j.1751-5823.2005.tb00254.x
- Czado & Nagler (2022), Vine：https://www.annualreviews.org/content/journals/10.1146/annurev-statistics-040220-101153
- Zhao & Udell (2020), mixed-data Gaussian copula imputation：https://arxiv.org/abs/1910.12845
- Aas, Jullum & Løland (2021), dependent-feature Shapley：https://martinjullum.com/publication/aas-2021-explaining/aas-2021-explaining.pdf
- Yoon et al., VIME (2020)：https://papers.nips.cc/paper/2020/hash/7d97667a3e056acab9aaf653807b4a03-Abstract.html
- Cui et al. (2024), class-conditioned tabular SSL：https://arxiv.org/abs/2404.17489

資料の補足は混合型の欠損補完とSHAPの条件付き生成にも触れる。欠損補完・説明の結果を分類用拡張の効果の証拠にしない。クラス条件付き法の既存比較はランダム特徴マスク設定で、目的関数も異なる。コピュラの単独効果はまずVIME内の2手法差で見る。

## 別のPCのCodexへ

パスは展開したフォルダを基準に解決する。元の絶対パスは使わない。必要な実装と記録は同梱した。現行のPPTXは編集可能。資料を編集する際は、その環境のpresentations skillに従い、元ファイルに上書きせず別名で保存し、最初の4枚が同一か確認する。
'''
(PACK/'研究引き継ぎ.md').write_text(handoff)
files=[]
for path in sorted(PACK.rglob('*')):
 if path.is_file():files.append({'path':path.relative_to(PACK).as_posix(),'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
(PACK/'ファイル一覧とSHA256.json').write_text(json.dumps({'created':'2026-10-04','files':files},ensure_ascii=False,indent=2))
zip_path=BASE/(PACK.name+'.zip')
with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED) as z:
 for path in sorted(PACK.rglob('*')):
  if path.is_file():z.write(path,path.relative_to(BASE).as_posix())
with zipfile.ZipFile(zip_path) as z:assert z.testzip() is None
print(json.dumps({'folder':str(PACK),'zip':str(zip_path),'files':len(files)+1,'bytes':zip_path.stat().st_size},ensure_ascii=False))
