from pathlib import Path
import json,shutil,hashlib,zipfile
R=Path.cwd(); OLD=R/'output/handoff/テーブルデータ拡張_引き継ぎ_20261024';B=R/'output/handoff/テーブルデータ拡張_文献特徴量追加_20261024';T=R/'tmp/literature_features_20261024'
shutil.copytree(OLD,B,dirs_exist_ok=True)
# Keep previous slides explicitly in the old-version subfolder.
p=B/'資料/テーブルデータにおけるデータ拡張_参照レイアウト版_完成.pptx'
if p.exists():shutil.move(str(p),str(B/'資料/旧版'/p.name))
p=B/'資料/テーブルデータにおけるデータ拡張_文献と特徴量_追加版.pptx'
if p.exists():p.unlink()
for f in (B/'資料/スライド画像').glob('slide-*.png'):f.unlink()
for f in T.glob('slide-*.png'):shutil.copy2(f,B/'資料/スライド画像'/f.name)
E=B/'output/experiments/minority_ratios_20261023';shutil.copy2(R/'output/experiments/minority_ratios_20261023/diagnose_relationships.py',E/'diagnose_relationships.py');shutil.copy2(R/'output/experiments/minority_ratios_20261023/results/feature_examples.json',E/'results/feature_examples.json')
s=(T/'build.mjs').read_text().replace("import {pathToFileURL} from 'node:url';","import {pathToFileURL,fileURLToPath} from 'node:url';")
s=s.replace("const ROOT='/Users/kouta/Github/data augumation/Data-Augumation';", "const ROOT=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');")
s=s.replace("const DIR=ROOT+'/tmp/literature_features_20261024';", "const DIR=ROOT+'/presentation_source/build_out';\nawait fs.mkdir(DIR,{recursive:true});")
s=s.replace("const SKILL='/Users/kouta/.codex/plugins/cache/openai-primary-runtime/presentations/26.1022.11436/skills/presentations';", "const SKILL=process.env.PRESENTATIONS_SKILL_DIR;\nif(!SKILL)throw new Error('PRESENTATIONS_SKILL_DIR を移行先の presentations スキルの場所に設定してください。');")
s=s.replace("const F='Hiragino Sans';", "const F=process.env.SLIDE_FONT_FAMILY||'Hiragino Sans';")
(B/'presentation_source/build.mjs').write_text(s)
for name in ['manifest.json','chart-slides.json']:shutil.copy2(T/name,B/'presentation_source'/name)
p=B/'presentation_source/finalize.mjs';s=p.read_text().replace('requiredNativeChartOwnerSlides:[24]','requiredNativeChartOwnerSlides:[31]');p.write_text(s)
p=B/'presentation_source/README.md';s=p.read_text().replace('31枚','40枚');s+='\n2026-10-24追記：６手法の文献対応と特徴量・列関係の説明を追加。主結果の再実験なし。参照文献は「文献一覧と実装の対応.md」、特徴量の補足は「特徴量と列関係の補足.md」。\n';p.write_text(s)
for name in ['AGENTS.md','README_最初に読んでください.md','引き継ぎ説明.md','レイアウト参照の状態.md']:
 p=B/name;s=p.read_text().replace('テーブルデータにおけるデータ拡張_参照レイアウト版_完成.pptx','テーブルデータにおけるデータ拡張_文献と特徴量_発表版.pptx').replace('31枚','40枚');p.write_text(s)
p=B/'引き継ぎ説明.md';s=p.read_text()+'''
## 2026-10-24 文献・特徴量の追記

ユーザー依頼により６手法の原著・関連研究・公式文書を対応付け、各手法スライド、ノート、３枚の文献一覧に追加。米・レーズンの７特徴、電力網の12特徴、列関係の式、独立抽出で生じた実例と違反率を追加しました。計40枚。内容順と参照PDFのレイアウトを維持。

重要：Aich et al. の同名CopulaSMOTEのv3（2026）はtruncated vineによる生成であり、今回の順位正規化＋SMOTE型補間と違います。今回の手法を論文の直接再現と書かないこと。CTGAN×コピュラも公式CopulaGANと同一ではありません。VIMEは関連する部分置換操作の参照で、今回VIME全体を実験したものではありません。

具体例は既存の少数10%、seed11、shuffle生成行から選んだ最大違反例。米のArea16734/ConvexArea12740、レーズン218459/56030。Gridはp1=5.58632954964135、消費合計=-2.453825437472049、残差3.1325041121693005。頻度の代表例ではありません。diagnose_relationships.pyで再抽出し、results/feature_examples.jsonへ保存できます。分類実験の再学習や数値変更はしていません。

新しい結果表やグラフの再作成時は、この追加版ソースを使ってください。ネイティブグラフの所有スライドは31。旧版は資料/旧版に保存しています。
''';p.write_text(s)
(B/'文献一覧と実装の対応.md').write_text('''# 文献一覧と今回の実装の対応

確認日：2026-10-24。原著・関連研究・公式文書を区別しています。今回の比較結果を、参照論文の直接再現結果と一律に表現しないでください。

| 今回の手法 | 参照 | 対応と相違 |
|---|---|---|
| 列シャッフル | [1] VIME | 各列の経験周辺分布から値を再抽出する操作が関連。VIMEは部分置換を使う自己・半教師ありフレームワーク。今回は少数クラス内で全列を独立再抽出する対照。VIMEの再現ではない。 |
| Gaussian copula | [2] SDV、[7] GaussianCopula公式文書 | 分布に基づく合成の関連研究。今回は経験周辺分布と相関５％縮小の自作実装で、SDVライブラリをそのまま使っていない。 |
| SMOTE | [3] SMOTE原著 | 少数の近傍間を線形補間。今回は訓練内標準化、k=5。 |
| コピュラSMOTE | [4] CopulaSMOTE | 同名の先行研究だが、参照したv3はtruncated vine copulaから生成。今回は順位を正規化して近傍補間するため、同一アルゴリズムではない。 |
| CTGAN | [5] CTGAN原著 | 公式ctgan0.11.0を使用。構成・epochは本実験の固定設定。 |
| CTGAN×コピュラ | [5] CTGAN、[6] CopulaGAN公式文書 | 周辺分布変換＋CTGANの組合せが関連。今回はクラス別の経験分布変換で、公式CopulaGANの直接再現ではない。 |

## [1] VIME：列別の置換に関連する研究

Yoon, J., Zhang, Y., Jordon, J., & van der Schaar, M. (2020). **VIME: Extending the Success of Self- and Semi-supervised Learning to Tabular Domain.** Advances in Neural Information Processing Systems 33.

- 原著：https://papers.nips.cc/paper_files/paper/2020/hash/7d97667a3e056acab9aaf653807b4a03-Abstract.html
- 本文：https://papers.nips.cc/paper_files/paper/2020/file/7d97667a3e056acab9aaf653807b4a03-Paper.pdf
- 操作の根拠：第4.1節、式(3)。マスクされた特徴値をその列の経験周辺分布から再抽出する。

## [2] Synthetic Data Vault：分布に基づく合成の関連研究

Patki, N., Wedge, R., & Veeramachaneni, K. (2016). **The Synthetic Data Vault.** 2016 IEEE International Conference on Data Science and Advanced Analytics (DSAA), 399–410. DOI: **10.1109/DSAA.2016.49**.

- 出版元：https://doi.org/10.1109/DSAA.2016.49
- 著者・実装の引用情報：https://github.com/sdv-dev/SDV
- Gaussian copulaを使う現在の公式実装の説明は[7]。今回の相関縮小や経験分布の設定は本実験の定義。

## [3] SMOTE：原著

Chawla, N. V., Bowyer, K. W., Hall, L. O., & Kegelmeyer, W. P. (2002). **SMOTE: Synthetic Minority Over-sampling Technique.** Journal of Artificial Intelligence Research, 16, 321–357. DOI: **10.1613/jair.953**.

- 本文：https://www.cs.cmu.edu/afs/cs/project/jair/pub/volume16/chawla02a.pdf
- 論文での比較結果を、今回の３データで得られる結果と同一視しない。

## [4] CopulaSMOTE：同名の関連研究

Aich, A., et al. **CopulaSMOTE: A Copula-Based Oversampling Approach for Imbalanced Classification in Diabetes Prediction.** arXiv:2506.17326. 初稿2025-06-18。今回参照した版は **v3（2026-05-25）**、プレプリント。

- 版固定の本文：https://arxiv.org/html/2506.17326v3
- 書誌情報：https://arxiv.org/abs/2506.17326
- DOI：https://doi.org/10.48550/arXiv.2506.17326
- v3の第3節は、少数クラスの順位変換、truncated vineの推定とサンプリング、経験逆CDFによる逆変換。
- 今回の順位正規化＋近傍補間とは異なる。同名であることだけを根拠に論文再現と記述しない。

## [5] CTGAN：原著

Xu, L., Skoularidou, M., Cuesta-Infante, A., & Veeramachaneni, K. (2019). **Modeling Tabular data using Conditional GAN.** Advances in Neural Information Processing Systems 32.

- 原著：https://papers.nips.cc/paper/2019/hash/254ed7d2de3b23ab10936522dd547b78-Abstract.html
- 公式実装：https://github.com/sdv-dev/CTGAN

## [6] CopulaGAN：公式実装の参考文書

DataCebo / Synthetic Data Vault. **CopulaGANSynthesizer.** Official documentation. 参照日2026-10-24。

- https://docs.sdv.dev/sdv/modeling/single-table-synthesizers/copulagansynthesizer.md
- 学習部分のTechnical Details：列の周辺分布を正規化してからCTGANを学習。
- FAQの引用案内はCTGAN原著[5]を示す。ここでは独立の査読済みCopulaGAN論文があると仮定せず、文書として引用する。

## [7] Gaussian copula：公式実装の参考文書

DataCebo / Synthetic Data Vault. **GaussianCopulaSynthesizer.** Official documentation. 参照日2026-10-24。

- https://docs.sdv.dev/sdv/modeling/single-table-synthesizers/gaussiancopulasynthesizer

## 特徴量とデータの一次資料

- Rice (Cammeo and Osmancik), UCI. DOI:10.24432/C5MW4Z。https://archive.ics.uci.edu/dataset/545/rice+cammeo+and+osmancik
- Raisin, UCI. DOI:10.24432/C5660T。https://archive.ics.uci.edu/dataset/850/raisin
- Electrical Grid Stability Simulated Data, UCI. DOI:10.24432/C5PG66。https://archive.ics.uci.edu/dataset/471/electrical+grid+stability+simulated+data
- scikit-image公式 regionprops：https://scikit-image.org/docs/stable/api/skimage.measure.html#skimage.measure.regionprops

Raisin公式ページではVariables Tableの一部の説明がずれているため、Additional Variable Informationの定義と列名を照合しています。上記データはCC BY 4.0。元論文の導入情報は各UCIページにあります。共有されたScienceDirect論文の本文は未確認のままで、内容・新規性の根拠として引用していません。
''')
(B/'特徴量と列関係の補足.md').write_text('''# 特徴量と、列関係を無視したときに起こること

## 米とレーズン

いずれも１粒の画像から７形状特徴を抽出します。コードではRiceの列名のアンダースコアを除いています。

|列|意味|
|---|---|
|Area|領域内の画素数|
|Perimeter|輪郭の長さ|
|MajorAxisLength|形状を表す楕円の長軸長|
|MinorAxisLength|同じ楕円の短軸長|
|Eccentricity|楕円の離心率|
|ConvexArea|領域を囲む最小凸包の画素数|
|Extent|領域面積を外接矩形面積で割った比率|

定義に基づきArea<=ConvexArea、a>=b>0、e=sqrt(1-(b/a)^2)が必要です。Extentは0〜1。外接矩形面積は独立した入力列として保存されていないため、ExtentとAreaの完全な関係をこのデータだけで検証したとは主張しません。面積と周長などの統計的な依存も、列を別々に動かすと変わる可能性があります。

独立抽出ではそれぞれの列の値が観測済みでも、同じ粒の特徴として矛盾することがあります。既存生成行の少数10%・seed11で、Area-ConvexAreaが最大の行は次の通りでした。

|データ|生成行（0始まり）|Area|ConvexArea|
|---|---|---|---|
|米|607|16734|12740|
|レーズン|257|218459|56030|

これは最大違反を選んだ説明例であり、頻度や代表値を示すサンプルではありません。

## 電力網

４ノードのシミュレーション。tau1..4は反応時間、p1..4は公称電力、g1..4は価格弾力性に比例する係数。１は生産者、２〜４は消費者です。消費p2..4は負なのでp1=−(p2+p3+p4)。UCIはp1を冗長なnon-predictive列と記載していますが、今回の比較は12列に共通して適用し、p1も列間整合性の診断対象にしています。

連続ターゲットstabは入力から除外し、stable/unstableを表すstabfを分類。stableを実験上の少数クラスとしています。

独立抽出で収支の絶対誤差が最大の生成行（少数10%、seed11、0始まり857）では、p1=5.58632954964135、p2=-1.00755712991671、p3=-0.790205917054031、p4=-0.656062390501308。必要なp1は約2.453825で、収支残差は約3.132504です。各値が元の範囲内でも、元シミュレーションの入力条件に一致しません。

## 頻度と学習への意味

少数10%、列シャッフル、５回平均の既知関係違反率は米77.8%、レーズン95.5%、電力網99.4%。形状は離心率差>0.01、短軸>長軸、Area>ConvexArea+1のいずれか、電力網は絶対収支残差>0.01で判定。元の少数訓練行の違反率は０です。データごとに条件の厳しさが違うので、率をデータ間の品質順位として直接比較しないでください。

不整合な行に少数ラベルをそのまま与えると、不自然な関連を分類器が学ぶ可能性があります。ただし違反率は合成行の真のラベル誤りを測った指標ではありません。また、違反したら必ず分類性能が悪化するわけではありません。したがって生成品質と未使用データの分類性能を別に確認します。

追加の再学習はしていません。diagnose_relationships.pyは保存済みNPZ/CSVから上記例と率を抽出し、results/feature_examples.jsonに記録します。出典と今回の解釈は「文献一覧と実装の対応.md」を参照。
''')
print('Bundle content prepared')
