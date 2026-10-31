from pathlib import Path
R=Path.cwd();B=R/'tmp/literature_features_20261024';s=(R/'tmp/layout_reference_20261024/build.mjs').read_text().replace('tmp/layout_reference_20261024','tmp/literature_features_20261024')
# Store verified primary references in notes; short citations remain visible.
a=s.index('const manifest=[];')
s=s[:a]+r'''
const literature={
 vime:{id:'1',short:'Yoon et al. (2020), VIME',full:'Yoon, J., Zhang, Y., Jordon, J., & van der Schaar, M. (2020). VIME: Extending the Success of Self- and Semi-supervised Learning to Tabular Domain. NeurIPS 33.',url:'https://papers.nips.cc/paper_files/paper/2020/hash/7d97667a3e056acab9aaf653807b4a03-Abstract.html'},
 sdv:{id:'2',short:'Patki et al. (2016), SDV',full:'Patki, N., Wedge, R., & Veeramachaneni, K. (2016). The Synthetic Data Vault. IEEE DSAA, 399–410. DOI:10.1109/DSAA.2016.49.',url:'https://doi.org/10.1109/DSAA.2016.49'},
 smote:{id:'3',short:'Chawla et al. (2002), SMOTE',full:'Chawla, N. V., Bowyer, K. W., Hall, L. O., & Kegelmeyer, W. P. (2002). SMOTE: Synthetic Minority Over-sampling Technique. JAIR 16, 321–357. DOI:10.1613/jair.953.',url:'https://www.cs.cmu.edu/afs/cs/project/jair/pub/volume16/chawla02a.pdf'},
 csmote:{id:'4',short:'Aich et al. (2025; v3: 2026), CopulaSMOTE',full:'Aich, A., et al. CopulaSMOTE: A Copula-Based Oversampling Approach for Imbalanced Classification in Diabetes Prediction. arXiv:2506.17326v3, 25 May 2026; initial submission 18 June 2025. Preprint. v3はtruncated vine copulaによる生成。本実験の順位正規化＋近傍補間とは異なる。',url:'https://arxiv.org/html/2506.17326v3'},
 ctgan:{id:'5',short:'Xu et al. (2019), CTGAN',full:'Xu, L., Skoularidou, M., Cuesta-Infante, A., & Veeramachaneni, K. (2019). Modeling Tabular data using Conditional GAN. NeurIPS 32.',url:'https://papers.nips.cc/paper/2019/hash/254ed7d2de3b23ab10936522dd547b78-Abstract.html'},
 cgan:{id:'6',short:'SDV, CopulaGANSynthesizer 公式文書',full:'DataCebo / SDV. CopulaGANSynthesizer. Official documentation, accessed 2026-10-24. 周辺分布の正規化後にCTGAN学習。単独の査読論文としては扱わない。本実験はクラス別経験分布変換を使うため公式実装の直接再現ではない。',url:'https://docs.sdv.dev/sdv/modeling/single-table-synthesizers/copulagansynthesizer.md'},
 gc:{id:'7',short:'SDV, GaussianCopulaSynthesizer 公式文書',full:'DataCebo / SDV. GaussianCopulaSynthesizer. Official documentation, accessed 2026-10-24. 本実験は経験周辺分布と相関５%縮小の自作実装。',url:'https://docs.sdv.dev/sdv/modeling/single-table-synthesizers/gaussiancopulasynthesizer'}
};
const featureRefs=['https://archive.ics.uci.edu/dataset/545/rice+cammeo+and+osmancik','https://archive.ics.uci.edu/dataset/850/raisin','https://archive.ics.uci.edu/dataset/471/electrical+grid+stability+simulated+data'];
const shapeRef='https://scikit-image.org/docs/stable/api/skimage.measure.html#skimage.measure.regionprops';
''' +s[a:]
# Main literature mapping after the six methods.
key="prose('公開データで確かめること'"
pos=s.index(key)
s=s[:pos]+r'''
s=add('先行研究と今回の実装の対応','先行研究','[1]のVIMEは全体の周辺分布から部分置換する自己・半教師あり手法。本実験は少数内で全列独立抽出する比較対照でありVIME全体ではない。[2,7]はGaussian copula合成の背景。[3]はSMOTE原著。[4]のv3はtruncated vine生成で、本実験の順位正規化＋SMOTE型補間と異なる。[6]は統計変換＋CTGANの公式文書で単独の査読論文ではない。','特徴量と列関係を確認してから実験結果を読みます。',Object.values(literature).map(x=>x.url));
notes(s,'論文の原著・関連研究・公式実装と、今回の操作上の定義を区別する');
tbl(s,[['手法','先行研究・参照元','今回の実装との関係'],['列シャッフル','[1] VIME (2020)','列別の再抽出という操作を参照'],['コピュラ','[2] SDV (2016)／[7] 公式文書','経験周辺分布＋相関５％縮小'],['SMOTE','[3] SMOTE (2002)','標準化後、k=5で補間'],['コピュラSMOTE','[4] CopulaSMOTE (v3, 2026)','同名研究はvine生成。本実験は変換＋補間'],['CTGAN','[5] CTGAN (2019)','公式ctganライブラリを使用'],['CTGAN×コピュラ','[5] CTGAN／[6] CopulaGAN公式文書','本実験はクラス別の経験分布変換']],[270,415,459],{y:180,h:400,size:24});
take(s,'混合手法の結果は、論文・公式実装を直接再現した結果ではない');
''' +s[pos:]
# Alias avoids a collision with the existing note(s,t) helper.
s=s.replace("notes(s,'論文の原著", "note(s,'論文の原著")
# Insert feature explanations immediately after the public dataset overview.
key="s=add('少数割合10％・20％・30％の作り方'"
pos=s.index(key)
s=s[:pos]+r'''
s=add('米・レーズンの７つの特徴量','特徴量と列間の関係','両データは同じ７種類の画像形状特徴。Riceファイルのunderscoreはコードで除去。Raisin公式サイトのVariables Tableは説明行にずれがあるためAdditional Variable Informationを参照。軸長は同等楕円の軸と解釈。','同じ粒から得る特徴なので、列の間に関係があります。',featureRefs.slice(0,2));
note(s,'各行は１粒。列は同じ画像から得た数値で、独立な属性ではない。');
tbl(s,[['列名（コード表記）','意味','型・尺度'],['Area','粒の領域に含まれる画素数','整数／画素'],['Perimeter','領域の輪郭の長さ','連続／画素の尺度'],['MajorAxisLength','形状を表す楕円の長軸長','連続／長さ'],['MinorAxisLength','形状を表す楕円の短軸長','連続／長さ'],['Eccentricity','楕円の離心率。丸さ・細長さ','連続／０以上１未満'],['ConvexArea','領域を囲む最小凸包の画素数','整数／画素'],['Extent','領域の面積 ÷ 外接矩形の面積','連続／０〜１']],[365,520,259],{y:178,h:390,size:24});
take(s,'米とレーズンでは、面積・軸長・離心率の整合性を確認できる');

s=add('形状特徴にある列間の関係','特徴量と列間の関係','長軸a、短軸b、離心率eは同じ２次モーメントを持つ楕円に由来しe=sqrt(1-(b/a)^2)。a>=b>0。Area<=ConvexArea。定義に基づく関係と、面積・周長などの統計的関係は区別する。Extentは外接矩形面積が元データに独立列としてなく、今回の診断は範囲だけを確認。','列を別々に組み替えると何が起きたかを示します。',[...featureRefs.slice(0,2),shapeRef]);
text(s,'面積の包含関係：Area ≤ ConvexArea',76,165,1125,65,36,C.ink,true);
text(s,'同じ楕円から求める関係：a ≥ b > 0\ne = √(1 − (b/a)²)',76,270,1125,120,36,C.ink,true);
text(s,'a：長軸長、b：短軸長、e：離心率\n面積・周長のような統計的な結び付きも、列別抽出で変わりうる',76,447,1125,110,28);
take(s,'各列の値が観測範囲内でも、１つの形状として成立しない場合がある');

s=add('列別抽出で実際に生じた面積の矛盾','保存済み生成データの診断','少数10%、seed11、列シャッフルの保存済み生成行。Area−ConvexAreaが最大の１行をデータごとに選択。Rice: zero-based row607, Area16734, ConvexArea12740。Raisin: row257, Area218459, ConvexArea56030。極端例を説明に使用し、発生頻度の代表値とはしない。','電力網では、電力の収支関係を確認します。',featureRefs.slice(0,2));
note(s,'少数10％・seed=11。面積の超過が最大の生成行を１件ずつ表示。');
tbl(s,[['データ','Area','ConvexArea','判定'],['米','16,734','12,740','粒の面積が凸包より大きい'],['レーズン','218,459','56,030','粒の面積が凸包より大きい']],[200,225,225,494],{y:200,h:240,size:27});
text(s,'各列は実際の少数クラスから取った値\nしかし組み合わせると、同じ粒の幾何学的な条件に反する',76,482,1125,90,30);
take(s,'値の範囲を守るだけでは、列どうしの整合性を守れない');

s=add('電力網の12特徴と分類ラベル','特徴量と列間の関係','UCI公式定義：tau1..4反応時間0.5..10s、p1..4公称電力、消費者p2..4負、生産者p1正。p1はabs(p2+p3+p4)で冗長。g1..4価格弾力性に比例する係数。UCIはp1をnon-predictiveと記載するが本比較は元の12特徴を全法で共通に使用。stab最大実部連続ターゲットを除外しstabfを分類。','電力の関係を壊した実例を見ます。',[featureRefs[2]]);
note(s,'４ノードのシミュレーション。添字１は生産者、２〜４は消費者。');
tbl(s,[['入力列','意味','範囲・関係'],['tau1〜tau4（４列）','参加者が制御に反応する時間','0.5〜10秒'],['p1〜p4（４列）','生産・消費の公称電力','p2〜p4は負、p1は正'],['g1〜g4（４列）','価格弾力性に比例する係数','0.05〜１（UCIの尺度）']],[350,420,374],{y:190,h:270,size:26});
text(s,'入力から除外：stab（安定性を表す連続ターゲット）\n分類ラベル：stabf（stable／unstable）。実験ではstableを少数化。',76,491,1125,90,27);
take(s,'p₁は他の電力列から決まる冗長な列。収支の等式を診断できる');

s=add('列別抽出で実際に崩れた電力収支','保存済み生成データの診断','少数10%、seed11、列シャッフル生成のzero-based row857。絶対収支残差最大の行。p1=5.58632954964135,p2=-1.00755712991671,p3=-.790205917054031,p4=-.656062390501308。合計3.1325041121693005。表示は小数３桁に丸め。UCIの負の消費符号よりp1=−(p2+p3+p4)。','列関係とラベルの問題を分けて考えます。',[featureRefs[2]]);
note(s,'少数10％・seed=11。収支の絶対誤差が最大の１行。表示は丸め。');
text(s,'必要な関係：p₁ = −(p₂+p₃+p₄)',76,177,1125,65,36,C.ink,true);
tbl(s,[['生産 p₁','消費 p₂','消費 p₃','消費 p₄'],['5.586','−1.008','−0.790','−0.656']],[286,286,286,286],{y:280,h:145,size:32});
text(s,'消費の合計から必要な生産量は約2.454\n生成された生産量は約5.586で、収支に約3.133のずれがある',76,472,1125,100,30);
take(s,'各列の値が妥当でも、元のシミュレーションの入力条件から外れる');

s=add('列関係の無視が学習に与えうる影響','課題と実験のつながり','違反頻度は保存済みquality.csvの列シャッフルbase、少数10%、５回平均。Rice77.75%、Raisin95.50%、Grid99.41%。形状は離心率差>.01 OR 短軸>長軸 OR Area>ConvexArea+1、Gridはabs収支>.01。データ間で違反条件が異なるため率の大小を直接比較しない。違反は真ラベルの誤りを直接測定したものではなく、ラベル維持の保証がないという課題。性能悪化は可能性であって必然ではない。','このため分類性能と生成品質を別々に比較します。',featureRefs);
tbl(s,[['データ','起こりうる不整合','列シャッフルの違反率'],['米','面積・軸長・離心率の整合が崩れる','77.8％'],['レーズン','同じ粒として成立しない組合せ','95.5％'],['電力網','生産と消費の収支が合わない','99.4％']],[245,600,299],{y:178,h:250,size:26});
text(s,'少数10％・５回平均。データごとに既知の関係を診断。\n不整合な行にも少数ラベルを付けると、誤った関連を学ぶ可能性がある。',76,469,1125,100,29);
take(s,'構造の不整合とラベルの誤りは同じ指標ではない。性能でも確かめる');
''' +s[pos:]
# Replace the sparse last bibliography slide with three complete reference slides.
a=s.index("s=add('参考文献と公開データの出典'")
b=s.index('await fs.writeFile(DIR',a)
s=s[:a]+r'''
s=add('参考文献１：シャッフル・コピュラ・SMOTE','参考文献','本文の[1][2][3][7]に対応。VIMEとSDVは関連研究で今回の全手順の再現ではない。','混合手法の文献を示します。',[literature.vime.url,literature.sdv.url,literature.smote.url,literature.gc.url]);
text(s,'[1] Yoon, J., et al. (2020). VIME: Extending the Success of\nSelf- and Semi-supervised Learning to Tabular Domain. NeurIPS 33.',76,158,1125,95,27,C.ink,true);
text(s,'[2] Patki, N., Wedge, R., & Veeramachaneni, K. (2016).\nThe Synthetic Data Vault. IEEE DSAA, 399–410.\nDOI: 10.1109/DSAA.2016.49',76,292,1125,120,27);
text(s,'[3] Chawla, N. V., et al. (2002).\nSMOTE: Synthetic Minority Over-sampling Technique.\nJAIR, 16, 321–357. DOI: 10.1613/jair.953',76,461,1125,120,27);
text(s,'[7] GaussianCopulaSynthesizer（SDV公式文書）。URLはノート・文献一覧。',76,616,1125,40,21,C.muted);

s=add('参考文献２：CopulaSMOTE・CTGAN','参考文献','[4] arXivプレプリント。初稿2025-06-18、参照版v3 2026-05-25。v3はtruncated vine copulaで、本実験の変換＋補間ではない。[5]CTGAN原著。','公式実装とデータの出典を示します。',[literature.csmote.url,literature.ctgan.url]);
text(s,'[4] Aich, A., et al. (2025; v3: 2026).\nCopulaSMOTE: A Copula-Based Oversampling Approach\nfor Imbalanced Classification in Diabetes Prediction.\narXiv:2506.17326v3（プレプリント）',76,164,1125,170,28,C.ink,true);
text(s,'[5] Xu, L., Skoularidou, M., Cuesta-Infante, A.,\n& Veeramachaneni, K. (2019).\nModeling Tabular data using Conditional GAN. NeurIPS 32.',76,411,1125,135,28);
take(s,'[4]は今回のコピュラSMOTEの直接再現元として扱わない');

s=add('参考文献３：公式実装と特徴量の出典','参考文献','[6]は論文ではなく公式文書。CTGAN×copulaの組合せの参考であり本比較のクラス別経験分布変換とは違う。UCI各ページAdditional Variable Information、形状の定義はregionprops公式文書を照合。全URLと参照日は文献一覧MD。','以上です。',[literature.cgan.url,literature.gc.url,...featureRefs,shapeRef]);
text(s,'[6] DataCebo / SDV. CopulaGANSynthesizer（公式文書）\n[7] DataCebo / SDV. GaussianCopulaSynthesizer（公式文書）',76,158,1125,100,27,C.ink,true);
text(s,'UCI Rice：DOI 10.24432/C5MW4Z\nUCI Raisin：DOI 10.24432/C5660T\nUCI Electrical Grid Stability：DOI 10.24432/C5PG66',76,314,1125,145,28);
text(s,'特徴量の定義：各UCI配布ページと scikit-image regionprops\n公式文書の参照日：2026年10月24日\n全URLと、今回の実装との差は同梱の文献一覧に記載。',76,516,1125,120,26);

// Add a short, visible source attribution on each method slide.
const methodCitations=[['列シャッフル：',[literature.vime],'関連研究：'],['コピュラ：',[literature.sdv,literature.gc],'関連研究・実装：'],['SMOTE：',[literature.smote],'原著：'],['コピュラSMOTE：',[literature.csmote],'同名の関連研究：'],['CTGAN：',[literature.ctgan],'原著：'],['CTGAN×コピュラ：',[literature.ctgan,literature.cgan],'参考：']];
for(let i=0;i<manifest.length;i++)for(const [prefix,refs,lead] of methodCitations){if(manifest[i].title.startsWith(prefix)){text(p.slides.items[i],lead+refs.map(r=>'['+r.id+'] '+r.short).join(' ／ '),76,109,1125,27,18,C.muted);p.slides.items[i].speakerNotes.text+='\n\n文献と今回の実装の対応\n'+refs.map(r=>r.full+'\n'+r.url).join('\n\n');}}
''' +s[b:]
(B/'build.mjs').write_text(s)
# New output folder preserves the previous transferable folder unchanged.
O=R/'output/handoff/テーブルデータ拡張_文献特徴量追加_20261024';(O/'資料').mkdir(parents=True,exist_ok=True)
f=(R/'tmp/layout_reference_20261024/finalize.mjs').read_text().replace('tmp/layout_reference_20261024','tmp/literature_features_20261024').replace('output/handoff/テーブルデータ拡張_引き継ぎ_20261024/資料/テーブルデータにおけるデータ拡張_参照レイアウト版_完成.pptx','output/handoff/テーブルデータ拡張_文献特徴量追加_20261024/資料/テーブルデータにおけるデータ拡張_文献と特徴量_追加版.pptx').replace('validation-layout-final.json','validation-literature.json').replace('requiredNativeChartOwnerSlides:[24]','requiredNativeChartOwnerSlides:[31]')
(B/'finalize.mjs').write_text(f)
