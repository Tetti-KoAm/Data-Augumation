import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {Presentation,PresentationFile} from '@oai/artifact-tool';

const ROOT='/Users/kouta/Github/data augumation/Data-Augumation';
const DIR=ROOT+'/tmp/seminar_visual_20261022';
const SKILL='/Users/kouta/.codex/plugins/cache/openai-primary-runtime/presentations/26.1020.11127/skills/presentations';
const {applyPresentationChartFont}=await import(pathToFileURL(SKILL+'/container_tools/artifact_tool_utils.mjs').href);
const p=Presentation.create({slideSize:{width:1280,height:720}});
const C={navy:'#102B46',teal:'#167C80',orange:'#D96B35',ink:'#22384D',muted:'#647789',grid:'#DCE5EB',pale:'#EDF4F6',white:'#FFFFFF'};
const F='Hiragino Sans';
const sources={smote:'https://www.cs.cmu.edu/afs/cs/project/jair/pub/volume16/chawla02a.pdf',ctgan:'https://papers.nips.cc/paper/2019/hash/254ed7d2de3b23ab10936522dd547b78-Abstract.html',sdv:'https://docs.sdv.dev/sdgym/benchmarking/run/local',leak:'https://imbalanced-learn.org/0.14/common_pitfalls.html',shared:'https://www.sciencedirect.com/science/article/pii/S0925231226020369'};
const manifest=[];
function text(s,t,x,y,w,h,size=30,color=C.ink,bold=false,align='left'){
 const q=s.shapes.add({geometry:'textbox',position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});
 q.text=t;q.text.style={typeface:F,fontFamily:F,fontSize:size,color,bold,alignment:align};return q;
}
function add(title,section,notes,bridge,refs=[]){
 const s=p.slides.add();const n=p.slides.items.length;s.background.fill=C.white;
 text(s,title,64,42,1152,94,43,C.navy,true);
 text(s,section,68,674,1000,25,16,C.muted);
 text(s,String(n).padStart(2,'0'),1150,666,65,35,20,C.muted,false,'right');
 s.speakerNotes.text='説明\n'+notes+'\n\n次のスライドへのつなぎ\n'+bridge+'\n\n出典・位置づけ\n'+refs.map(r=>sources[r]??r).join('\n')+'\n本資料は研究計画。数値図は明記した説明例であり実験結果ではない。';
 manifest.push({number:n,title,section});return s;
}
function take(s,t){text(s,t,68,594,1144,59,29,C.teal,true);}
function label(s,t,x,y,w=500,color=C.muted){text(s,t,x,y,w,42,24,color,true);}
function table(s,v,widths,{x=68,y=175,w=1144,h=365,size=26}={}){
 let q=s.tables.add({rows:v.length,columns:v[0].length,left:x,top:y,width:w,height:h,values:v,columnWidths:widths});
 for(let r=0;r<v.length;r++)for(let c=0;c<v[0].length;c++){
  let z=q.getCell(r,c);z.fill=r===0?C.navy:r%2?C.pale:C.white;
  z.text.style={typeface:F,fontFamily:F,fontSize:size,bold:r===0,color:r===0?C.white:C.ink};
 }
 q.borders.assign({fill:C.grid,width:1,style:'solid'});
 q.cells.block({row:0,column:0,rowCount:v.length,columnCount:v[0].length}).assign({margins:{left:13,right:10,top:13,bottom:10}});
 return q;
}
function series(name,pts,color=C.teal,symbol='circle',size=10){return{name,xValues:pts.map(t=>t[0]),values:pts.map(t=>t[1]),fill:color,line:{fill:'none',width:0},marker:{symbol,size,fill:color}};}
function scatter(s,ss,{x=58,y=180,w=670,h=365,min=0,max=4,titleX='特徴 x₁',titleY='特徴 x₂',legend=true}={}){
 let a=s.charts.add('scatter',{position:{left:x,top:y,width:w,height:h},series:ss,scatterOptions:{style:'marker'},hasLegend:legend,legend:{position:'bottom',overlay:false,textStyle:{fontSize:20}},xAxis:{min,max,majorUnit:(max-min)/4,title:{text:titleX,textStyle:{fontSize:21}},textStyle:{fontSize:18},majorGridlines:{fill:C.grid,width:1},numberFormatCode:'0.0'},yAxis:{min,max,majorUnit:(max-min)/4,title:{text:titleY,textStyle:{fontSize:21}},textStyle:{fontSize:18},majorGridlines:{fill:C.grid,width:1},numberFormatCode:'0.0'},chartFill:C.white,plotAreaFill:C.white});
 applyPresentationChartFont(a,{fontFamily:F});
 text(s,'説明用の座標例（実験結果ではない）',x+18,y+h+5,w-32,26,16,C.muted);
 return a;
}
function twoReasons(s,leftTitle,leftBody,rightTitle,rightBody){
 text(s,'01',76,178,120,85,65,C.teal,true);text(s,leftTitle,76,280,510,58,35,C.navy,true);text(s,leftBody,76,360,510,160,29);
 text(s,'02',690,178,120,85,65,C.orange,true);text(s,rightTitle,690,280,510,58,35,C.navy,true);text(s,rightBody,690,360,510,160,29);
}
let s;

// 01. Cover
s=add('','', '全ラベル付きの不均衡分類を対象に、生成方法の仮定から失敗条件を説明し、原因に対応した改善案と評価を提案します。特定手法の優位性を示す実験結果ではありません。','まず研究全体の流れを示します。');
s.background.fill=C.navy;
text(s,'不均衡分類の\nデータ拡張',80,150,1120,185,65,C.white,true);
text(s,'なぜ生成が失敗し、どう改善するか',85,389,1110,65,36,'#BFDDE2');
text(s,'全ラベル付きデータを用いた研究計画',85,565,1100,50,25,'#BFDDE2');

// 02. Narrative
s=add('発表の流れ','背景', '全件にラベルがある連続値の二値分類から始めます。まず生成の必要性を検証できるように問題を分けます。次に六つの生成方法の仮定と限界を整理し、その原因に対応する改善を比較します。最後にどの評価が仮説を支持するかを示します。','最初に、不均衡だと何が起きるかを数値例で見ます。');
[['01','何が問題か','少数例不足と学習の偏り'],['02','なぜ失敗するか','生成方法が置く仮定'],['03','どう改善するか','原因に対応する制約'],['04','どう確かめるか','対照実験と評価指標']].forEach((r,i)=>{let y=175+i*98;text(s,r[0],76,y,85,65,42,C.teal,true);text(s,r[1],190,y+3,380,60,34,C.navy,true);text(s,r[2],650,y+8,550,55,28);});

// 03. Imbalance
s=add('Accuracyが高くても少数例を見逃しうる','背景', '説明例として多数950件、少数50件を置きます。全てを多数と予測すると950件が正しく、Accuracyは95%ですが少数Recallは0%です。これは学習器が必ずその解になるという意味ではなく、Accuracyだけでは目的を測れないことを示す計算です。','評価指標の問題に加えて、学習上の問題も二つに分けます。');
label(s,'説明例：クラスごとの件数',72,157,620);
let ch=s.charts.add('bar',{position:{left:62,top:215,width:660,height:320},categories:['多数クラス','少数クラス'],series:[{name:'件数',values:[950,50],fill:C.teal,points:[{idx:1,fill:C.orange}]}],barOptions:{direction:'bar',grouping:'clustered',gapWidth:95},hasLegend:false,xAxis:{min:0,max:1000,title:'件数',textStyle:{fontSize:19},majorGridlines:{fill:C.grid,width:1}},yAxis:{textStyle:{fontSize:24}},dataLabels:{showValue:true,position:'outEnd',textStyle:{fontSize:24,bold:true}},chartFill:C.white});applyPresentationChartFont(ch,{fontFamily:F});
label(s,'全件を多数と予測すると',790,191,410);
text(s,'95%',790,245,400,100,76,C.navy,true);text(s,'Accuracy',795,345,390,45,27);
text(s,'0%',790,410,400,100,76,C.orange,true);text(s,'少数クラスRecall',795,510,400,45,27);
take(s,'目的は、未知データの少数クラスを識別すること');

// 04. Causes
s=add('少数例不足と損失の偏りは別の問題','背景', '少数クラスの形や広がりを観測できない統計的な問題と、各行の平均損失のため多数側が強く寄与しうる問題を分けます。不均衡が必ず悪化を起こすわけではなく、クラス形状や学習器に依存します。比率だけでなく少数の絶対件数も重要です。','この二つを分けるため、生成しない対照も必要です。');
twoReasons(s,'観測の不足','クラスの広がりや\n複数の集団を推定しにくい','損失への寄与の偏り','多数側の誤りが\n学習を支配しうる');
take(s,'データを増やす目的を、問題ごとに切り分ける');

// 05. Baseline
s=add('生成しない対照で必要性を確かめる','背景', '重み付けは少数クラスの損失を重く扱い、ランダム過剰サンプリングは観測例を再利用します。最適化や正則化のため両者は完全には同じでありません。これらとの比較で新しい特徴値を生成する追加価値を調べます。','では、新しい特徴値を作る方法は何に依存するのでしょうか。');
table(s,[['対照','変えるもの','変わらないもの'],['拡張なし','元データで学習する','観測位置と件数'],['クラス重み付け','少数例の損失への重み','特徴空間の観測位置'],['ランダム複製','少数例が現れる回数','特徴空間の観測位置']],[305,420,419],{h:355});
take(s,'複製や重み付けを上回るかが、生成の追加価値を示す');

// 06. Assumption
s=add('合成データには未観測領域への仮定がある','背景', 'ここでは観測点がほぼ対角線に並ぶ説明例を置きます。近くの対角線上を補う生成は妥当かもしれませんが、全く離れた組み合わせも妥当とは限りません。合成例は新しい独立した実観測ではなく、観測データに基づく仮定です。','その仮定がどのように違うかを六つの方法で比較します。');
scatter(s,[series('観測例',[[.6,.7],[1,1],[1.5,1.6],[2.2,2.1],[3,3]]),series('補う候補',[[1.25,1.3],[2.6,2.6]],C.navy,'diamond',11),series('離れた候補',[[1,3],[3,1]],C.orange,'x',13)]);
label(s,'生成位置を決めるのは仮定',770,190,440,C.teal);
text(s,'観測点の間や周囲を\n同じクラスとみなす',770,250,440,100,33,C.navy,true);
text(s,'仮定が誤ると、\n誤った境界を学習しうる',770,407,440,110,29);
take(s,'クラスを指定するだけでは、ラベルの妥当性は保証できない');

// 07. Methods
s=add('６手法で異なる生成位置の決め方','生成方法', '全手法の目的を少数クラスの訓練行を増やすことに揃えます。列シャッフルはクラス内の各列を独立に再抽出します。コピュラSMOTEとCTGAN×コピュラは名称だけで実装を特定できないため、以降で今回の定義を示します。','最も単純な列シャッフルから、失敗の原因を見ます。');
table(s,[['手法','生成の基本操作'],['列シャッフル','同じクラスの列を独立に組み替える'],['Gaussian copula','周辺分布と依存を推定して生成する'],['SMOTE','同じクラスの近傍間を補間する'],['コピュラSMOTE','変換空間で補間し、元の尺度に戻す'],['CTGAN','ラベルを条件に分布を学習する'],['CTGAN×コピュラ','分布変換とGANを組み合わせる']],[365,779],{h:420,size:25});

// 08. Shuffle
s=add('列シャッフルは組み合わせを壊しうる','生成方法', '説明用に少数クラスがx2=x1を満たすとします。(1,1),(3,3)から各列を独立に選ぶと(1,3),(3,1)が生まれます。列の値は観測済みでも組み合わせは関係を満たしません。これは仕組みの例で、実データの完全な制約とは区別します。','依存を壊す問題に対して、依存を一緒にモデル化するのがコピュラです。');
scatter(s,[series('元の行',[[1,1],[3,3]],C.teal,'circle',13),series('組み替えた行',[[1,3],[3,1]],C.orange,'x',15)]);
label(s,'説明例：必要な関係',770,180,440);
text(s,'x₂ = x₁',770,238,440,70,48,C.navy,true);
text(s,'(1,1) と (3,3) は満たす\n(1,3) と (3,1) は外れる',770,339,440,115,29);
text(s,'各列の値が正しくても、\n組み合わせは妥当とは限らない',770,487,440,80,27,C.orange);
take(s,'依存する列を一緒に動かすことが改善候補になる');

// 09. Copula
s=add('コピュラは特徴間の依存を一緒に扱う','生成方法', 'Gaussian copulaではクラスごとにu_j=F_j(x_j)、z_j=Φ⁻¹(u_j)へ変換し、変換後の相関を推定します。多変量正規から生成した値を逆変換して戻します。図は依存を保つ生成の狙いを説明する座標例で、実際のコピュラ学習結果ではありません。','ただし、依存を推定するにも十分な例数が必要です。');
scatter(s,[series('観測例',[[.6,.7],[1,1],[1.5,1.6],[2.2,2.1],[3,3]]),series('依存に沿う候補',[[.85,.9],[1.3,1.2],[1.8,1.95],[2.6,2.6]],C.navy,'diamond',10)]);
[['01','各列を正規空間へ変換'],['02','変換後の相関から生成'],['03','逆変換で元の尺度へ戻す']].forEach((r,i)=>{text(s,r[0],770,192+i*110,70,54,34,C.teal,true);text(s,r[1],850,195+i*110,355,85,27);});
take(s,'少数例では相関推定が揺れるため、正則化を検討する');

// 10. SMOTE
const islands=[[.6,1],[.85,1.15],[1,.8],[3,1],[3.15,1.2],[3.4,.8]];
const majority=[[1.75,.8],[1.9,1.3],[2.1,1],[2.25,1.4]];
s=add('SMOTEは近傍の線分も同じクラスとみなす','生成方法', 'SMOTEはxnew=xi+λ(xj−xi),0≤λ≤1で少数クラス内の近傍を補間します。図は少数クラスが二つの集団に分かれ、選んだ近傍が集団をまたぐ説明例です。十分近くに同じ集団の点があれば、必ず橋を作るわけではありません。標準化と近傍数の影響を確認します。','補間を行う距離の空間を変えた案がコピュラSMOTEです。',['smote']);
scatter(s,[series('少数例',islands),series('多数例',majority,C.muted,'square',9),series('集団間の補間',[[1.3,1],[1.7,1],[2.1,1],[2.5,1],[2.8,1]],C.orange,'x',12)]);
label(s,'補間の式',770,183,440);
text(s,'x_new = x_i\n+ λ(x_j − x_i)',770,240,440,120,35,C.navy,true);
text(s,'0 ≤ λ ≤ 1',770,366,440,45,25,C.muted);
text(s,'近傍が別の集団に届くと、\n多数側の領域へ入りうる',770,423,440,110,29);
take(s,'近傍数や集団内補間を、原因に対応する改善案として調べる');

// 11. CopulaSMOTE
s=add('コピュラSMOTEは補間する空間を変える','生成方法', '本発表の操作上の定義です。クラス内でGaussian copulaの周辺変換を行い、正規空間でSMOTEして逆変換します。周辺分布の歪みを調整する仮説ですが、特徴が独立になるわけではなく、複数集団や非凸形状も解決するとは限りません。既存の特定手法と同一とは主張しません。','より柔軟な分布を直接学ぶ候補としてCTGANを比較します。');
table(s,[['段階','操作','検討する理由'],['1','各列を正規空間へ変換','周辺分布の歪みを調整する'],['2','変換空間でSMOTE','距離と補間の意味を変える'],['3','元の尺度へ逆変換','生成行として分類に使う']],[135,480,529],{h:320,size:28});
text(s,'仮説',76,540,120,45,27,C.teal,true);text(s,'変換後の近さは、分類上も妥当か',220,536,970,55,32,C.navy,true);

// 12. CTGAN
s=add('CTGANの柔軟さにも少数例の制約がある','生成方法', 'CTGANはmode-specific normalizationや条件付き生成、training-by-samplingなどを用います。ラベルをカテゴリ列として含め、少数クラスを条件に生成します。条件指定のAPIは実装に応じて確認します。少数条件のデータが乏しければ、過適合やモードの偏りを起こす可能性を検証する必要があります。','コピュラとの併用は、その学習の負担を減らせるかという追加仮説です。',['ctgan']);
label(s,'学習時',76,181,510,C.teal);text(s,'特徴 x とラベル y',76,243,510,70,40,C.navy,true);text(s,'連続値・カテゴリを含む\nテーブルの分布を学ぶ',76,351,510,115,30);
label(s,'生成時',690,181,510,C.orange);text(s,'y = 少数クラス',690,243,510,70,40,C.navy,true);text(s,'その条件の合成行を得る\n重複・偏り・多様性を確認する',690,351,510,115,30);
take(s,'複雑なモデルでも、観測していない分布を必ず回復できるとは限らない');

// 13. Combination
s=add('CTGAN×コピュラで追加効果を確かめる','生成方法', '独自案は列ごとの分布変換、CTGANでの学習と生成、逆変換と定義します。SDVにはCopulaGANという既存実装があるため、それと独自案を区別します。CTGAN内部の正規化との重複、変換の推定誤差を確認します。二つを組み合わせるだけで改善するとは断定しません。','手法名ではなく、各手法の仮定と失敗をまとめます。',['sdv']);
table(s,[['比較','確認すること'],['CTGAN単独','基準となる性能・生成品質・実行時間'],['分布変換＋CTGANの独自案','変換による学習負担の軽減があるか'],['既存CopulaGAN','独自案との仕様・処理順の違い']],[500,644],{h:330,size:27});
take(s,'変換の利点と、変換誤差・内部正規化との重複を切り分ける');

// 14. method summary
s=add('手法の仮定が失敗条件を決める','生成方法', 'これまでの説明を仮定と失敗の対応でまとめます。Gaussian copulaはモデル表現の限界と推定誤差、SMOTEは補間する領域の仮定、GANは有限標本と学習の安定性が論点です。これらは検証対象であり、特定データで悪化すると決めつけるものではありません。','この原因に対応する補助輪を一つずつ検証します。');
table(s,[['手法群','主な仮定','確認する失敗'],['列シャッフル','列を独立に選べる','特徴の関係が壊れる'],['Gaussian copula','正規空間の依存で近似できる','相関推定やモデルが合わない'],['SMOTE系','近傍間を同じクラスとみなす','集団間や境界に生成する'],['GAN系','観測例から分布を学べる','過適合・生成の偏り']],[280,445,419],{h:385,size:26});
take(s,'比較の中心は、どの構造でどの仮定が崩れるか');

// 15. Cause remedy
s=add('改善案は失敗の原因から導く','改善案', 'クラス内生成は基本定義として共通に入れます。さらに局所化や正則化、生成量の制限、生成後の意味制約検査を追加します。最初から全てを使うと寄与を特定できません。改善前後を同じ分割と採択後の生成件数で比較します。生成量は推定誤差自体を解消するものではありません。','まず、正則化が必要になる理由を特徴数で見ます。');
table(s,[['原因候補','改善候補','副作用'],['依存推定が揺れる','相関を正則化','真の依存も弱まる'],['生成範囲が広い','集団内に限定','小集団の例数が減る'],['合成例の影響が強い','追加件数を抑える','誤った生成は残る'],['意味制約に違反する','生成後に検査','採択後の分布が変わる']],[385,350,409],{h:390,size:26});
take(s,'対策は一つずつ加え、効果と副作用を測る');

// 16. Regularization
s=add('特徴が増えるほど相関の推定量も増える','改善案', 'd特徴にはd(d−1)/2個の相関係数があります。10,30,50特徴なら45,435,1225個です。少数クラスの例数が同じでも推定する量は増えます。正則化Rλ=(1−λ)Rhat+λIで縮める候補を検証します。ただしGaussian copulaの表現能力の限界を正則化だけでは解決できません。','生成範囲を制限する改善は、別の失敗に対応します。');
label(s,'推定する相関係数の数：d(d−1)/2',72,166,670);
ch=s.charts.add('bar',{position:{left:60,top:228,width:650,height:320},categories:['10特徴','30特徴','50特徴'],series:[{name:'相関係数の数',values:[45,435,1225],fill:C.teal}],barOptions:{direction:'column',gapWidth:100},hasLegend:false,xAxis:{textStyle:{fontSize:23}},yAxis:{min:0,max:1400,majorGridlines:{fill:C.grid,width:1},textStyle:{fontSize:18}},dataLabels:{showValue:true,position:'outEnd',textStyle:{fontSize:23,bold:true}},chartFill:C.white});applyPresentationChartFont(ch,{fontFamily:F});
text(s,'少数例数が同じでも、\n推定は難しくなる',770,224,430,110,34,C.navy,true);
text(s,'正則化で揺れを抑える\n強さは検証データで選ぶ',770,407,430,100,29);
take(s,'正則化は安定性と依存の再現のトレードオフを持つ');

// 17. local comparison
s=add('集団内補間は誤った橋を減らす候補','改善案', '左右は同じ観測座標を用いた対照の説明図です。左は集団間の近傍を選んだ場合、右は集団内に限定した場合です。右は橋が少ない一方、集団の推定や少数例の分割による不安定性が残ります。これはSMOTEの実測結果ではありません。','範囲を制御しても、誤った生成行を増やしすぎる問題は残ります。');
label(s,'集団間に補間した説明例',76,156,540,C.orange);label(s,'集団内に限定した説明例',690,156,540,C.teal);
scatter(s,[series('少数例',islands),series('多数例',majority,C.muted,'square',8),series('合成例',[[1.4,1],[1.8,1],[2.2,1],[2.6,1]],C.orange,'x',11)],{x:53,y:215,w:570,h:335});
scatter(s,[series('少数例',islands),series('多数例',majority,C.muted,'square',8),series('合成例',[[.75,1.05],[.9,.9],[3.1,1.1],[3.25,1]],C.orange,'x',11)],{x:661,y:215,w:570,h:335});
take(s,'局所化しすぎると、推定に使える例が減る');

// 18. quantity
s=add('生成量は誤った例の影響も増やす','改善案', '説明例として少数クラスの実例が20件あり、追加倍率0,1,3で合成0,20,60件を追加します。グラフは少数ラベルを付ける訓練行だけの内訳で、多数クラスは含みません。行を等重みで学習する場合に合成行の寄与が増えることを示します。最適な生成量は検証で選びます。','件数だけでなく、生成後に除外するルールにも副作用があります。');
label(s,'説明例：少数ラベルの訓練行の内訳',72,156,690);
ch=s.charts.add('bar',{position:{left:60,top:225,width:675,height:325},categories:['追加0倍','追加1倍','追加3倍'],series:[{name:'元の少数実例',values:[20,20,20],fill:C.teal},{name:'合成行',values:[0,20,60],fill:C.orange}],barOptions:{direction:'column',grouping:'stacked',gapWidth:100,overlap:100},hasLegend:true,legend:{position:'bottom',overlay:false,textStyle:{fontSize:21}},xAxis:{textStyle:{fontSize:23}},yAxis:{min:0,max:80,title:'件数',textStyle:{fontSize:18},majorGridlines:{fill:C.grid,width:1}},chartFill:C.white});applyPresentationChartFont(ch,{fontFamily:F});
text(s,'実例20件は固定',790,220,420,60,34,C.navy,true);text(s,'増えるのは\n推定した分布からの行',790,310,420,100,30);
text(s,'妥当なら助けになる\n誤りがあれば影響も増える',790,455,420,90,27,C.orange);
take(s,'候補生成数・採択数・実行時間を別々に記録する');

// 19. filter
s=add('生成後の検査にも異なる目的がある','改善案', '物理的な値域や既知の関係の違反と、分類器の信頼度の低さは別です。自信のない例を全て捨てると、本物の難しい境界点も失い、既存モデルの偏りを強めます。ルールは事前に定義するか検証で決めます。採択率と多様性、Recallを同時に確認します。','改善が効く理由を確かめるには、原因を分けた実験が必要です。');
table(s,[['検査','除く対象','注意点'],['意味制約','値域・整数・既知の関係への違反','事前に妥当なルールを定義する'],['信頼度','分類器が自信を持てない例','本物の難例まで除きうる']],[245,450,449],{h:285,size:26});
text(s,'採択率',84,510,330,55,36,C.teal,true);text(s,'多様性',480,510,330,55,36,C.teal,true);text(s,'少数Recall',855,510,350,55,36,C.teal,true);
take(s,'制約違反が減るだけで、分類が良くなるとは限らない');

// 20. hypotheses
s=add('人工データで失敗の原因を切り分ける','実験計画', '人工データでは依存、複数集団、重なりを別々に操作します。真の生成分布から独立したテスト標本を得る設計にします。重なり領域ではラベルが一意に決まらないため、真の事後確率を使う診断を検討します。人工データの結論は実データで再確認します。','比較手順でも、手法以外の差を揃える必要があります。');
table(s,[['変える構造','仮説','対応する改善'],['特徴間の依存','独立生成は関係を壊しやすい','関連列を一緒に生成'],['少数側の複数集団','集団間補間は橋を作りうる','集団内に補間を限定'],['クラスの重なり','除外が難例を失わせうる','採択条件と量を調整']],[350,460,334],{h:345,size:26});
take(s,'一度に変える構造を絞り、仮説と診断指標を先に決める');

// 21. protocol
s=add('分割・生成・評価を混ぜない比較手順','実験計画', 'まず訓練、検証、テストに分けます。正規化と生成器と分類器の適合は訓練のみ、生成量や正則化、採択閾値、分類閾値は検証で選びます。交差検証ならfoldごとに適合をやり直します。分類器と設定探索予算を揃え、同じ分割で複数seedを比較します。初期はロジスティック回帰と木モデルを候補にします。','目的の達成と仕組みの診断を別々の指標で評価します。',['leak']);
table(s,[['データ','役割','使う処理'],['訓練','モデルを適合','前処理・生成器・分類器の学習'],['検証','設定を選択','生成量・正則化・採択条件・閾値'],['テスト','選択後に最終評価','元の評価分布で性能を測定']],[210,300,634],{h:330,size:27});
take(s,'同じ分割・分類器・探索予算で、対照群と改善前後を比較する');

// 22. metrics
s=add('分類性能は目的、生成品質は仕組みを測る','実験計画', 'macro F1は各クラスF1の平均、balanced accuracyは各クラスRecallの平均です。少数クラスを陽性にしたPrecision,Recall,PR-AUCも併記し、PR-AUCの実装定義を固定します。品質には意味制約、分布のずれ、多様性、重複、採択率を含めます。実データの近傍一致率は真のラベルではなく代理指標です。','最後に、どの結果なら改善案を支持できるかをまとめます。');
table(s,[['評価','主な指標','確かめること'],['分類性能','macro F1・balanced accuracy','未知の実例を識別できるか'],['少数側の挙動','Recall・Precision・PR-AUC','見逃しと誤検知のバランス'],['生成品質','制約違反・多様性・重複','想定した失敗が減ったか'],['安定性と負担','seedごとの差・実行時間','効果が安定し、実用的か']],[240,465,439],{h:370,size:26});
take(s,'品質と性能が同時に改善しても、条件を変えて再確認する');

// 23. closing
s=add('失敗条件と改善効果の対応を明らかにする','実験計画', '今回目指す主張は、この構造ではこの仮定が崩れ、その対策で対応する失敗と分類誤りが減る、という条件付きの知見です。まず単純手法と対照群、次に複合手法、最後に実データで確認します。ゼミでは優先する構造と複合手法の定義を相談します。研究の新規性は共有論文と関連研究の内容確認後に位置づけます。','本編はここまでです。補足は定義、既存実装、半教師ありへの接続と出典です。');
text(s,'この構造で、この仮定が崩れる',76,188,1120,70,42,C.navy,true);
text(s,'原因に対応する対策で、\n失敗と分類誤りが減るかを検証する',76,295,1120,120,38,C.teal,true);
text(s,'実施順：単純手法と対照群、複合手法、実データ',80,469,1120,60,28);
take(s,'ゼミで相談：優先する失敗条件と、複合手法の具体的な定義');

// 24. definitions appendix
s=add('補足：複合手法は処理を固定して比較する','補足', '名称だけでは一意に定まらないので操作を定義します。独自案と既存実装の一致は仕様とソースで確認が必要です。変換は訓練データ内で適合し、カテゴリ列の扱いも記録します。少数クラス条件を指定してもラベルの意味は保証されません。','次は既存のVIME実験との違いです。',['sdv']);
table(s,[['方法','今回の扱い'],['コピュラSMOTE','クラス内の周辺変換、正規空間SMOTE、逆変換'],['CTGAN×コピュラの独自案','列の分布変換、CTGAN学習・生成、逆変換'],['既存CopulaGAN','独自案と区別し、仕様・内部処理を確認']],[390,754],{h:350,size:27});
take(s,'分類や半教師ありへの拡張だけで、新規性が成立するとは断定しない');

// 25. VIME and SSL appendix
s=add('補足：半教師ありへ進むための基準','補足', 'リポジトリの既存実装はVIMEの破損器を列シャッフルから条件付きGaussian copulaへ置換するもので、今回は少数クラスの訓練行を増やす過剰サンプリングです。学習目的が異なるので結果を流用しません。ラベルなしへの展開では最初にランダムにラベルを隠し、次にクラス別欠損率を変えます。疑似ラベルを使う場合は誤りの増幅を別に診断します。','最後に参考資料の確認状況を示します。');
table(s,[['段階','確認すること'],['全件ラベル付き','生成器そのものの失敗条件を特定する'],['一部のラベルをランダムに隠す','ラベル率の効果を比較する'],['クラス別のラベル欠損率を変える','観測の偏りを追加して比較する']],[445,699],{h:325,size:27});
take(s,'既存VIMEの入力破損と、今回の過剰サンプリングは評価を分ける');

// 26. references
s=add('参考文献と共有論文の確認状況','補足', 'SMOTE,CTGANの原著とSDV,imbalanced-learnの公式文書を参照しています。URLはこのノートに記載します。共有論文は本文を取得できておらず、回帰を対象とするか、分類・半教師ありへの拡張が新規かは未確認です。論文内容を推測して紹介していません。','以上です。',['smote','ctgan','sdv','leak','shared']);
text(s,'Chawla et al. (2002)\nSMOTE: Synthetic Minority Over-sampling Technique',76,168,1130,95,29,C.navy,true);
text(s,'Xu et al. (2019)\nModeling Tabular Data using Conditional GAN',76,294,1130,95,29,C.navy,true);
text(s,'SDV ／ imbalanced-learn 公式ドキュメント',76,433,1130,58,27);
text(s,'共有論文：本文未確認。今回の資料では内容を引用していない',76,541,1130,60,26,C.orange);

await fs.writeFile(DIR+'/manifest.json',JSON.stringify(manifest,null,2));
await (await PresentationFile.exportPptx(p)).save(DIR+'/candidate.pptx');
for(let i=0;i<p.slides.items.length;i++){
 const b=await p.export({slide:p.slides.items[i],format:'png',scale:1});
 await fs.writeFile(DIR+'/slide-'+String(i+1).padStart(2,'0')+'.png',new Uint8Array(await b.arrayBuffer()));
}
console.log(JSON.stringify({slides:p.slides.items.length,candidate:DIR+'/candidate.pptx'}));
