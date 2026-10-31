import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {Presentation,PresentationFile} from '@oai/artifact-tool';

const ROOT='/Users/kouta/Github/data augumation/Data-Augumation';
const DIR=ROOT+'/tmp/six_methods_main_20261022';
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
let s,ch;


// Cover
s=add('','','全件ラベル付きでクラスの件数が偏るデータを対象に、六つの生成方法の挙動を確認し、問題点と原因を整理したうえで改善案を考える研究計画です。ラベルなしデータの扱いや論文紹介は今回の中心にしません。','まず今回の条件と目的を明確にします。');
s.background.fill=C.navy;
text(s,'テーブルデータにおける\nデータ拡張',80,150,1120,185,60,C.white,true);
text(s,'全ラベル付き・不均衡データでの６手法の挙動と改善案',85,389,1110,90,30,'#BFDDE2');
text(s,'問題点を整理し、原因に対応する補助輪を検証する',85,565,1100,50,25,'#BFDDE2');


// Scope
s=add('今回の条件と、確かめたいこと','対象と目的','今回は全サンプルに正解ラベルが付いているが、多数クラスと少数クラスの件数が偏っている条件です。偏りはクラス比として扱い、まず二値分類と連続数値の特徴に限定します。どの手法がどんな点を作るかを調べ、問題を発見してから対策を加えます。性能向上は未検証です。','この条件で比較する六つの方法を示します。');
label(s,'対象',76,173,1100,C.teal);
text(s,'すべてラベル付き\nクラスの件数に偏りがある',76,235,1100,128,43,C.navy,true);
label(s,'目的',76,408,1100,C.orange);
text(s,'６手法の挙動を確認し、\n問題の原因と改善案を対応させる',76,461,1100,105,34,C.ink,true);
take(s,'最初は連続数値の二値分類で、同じ条件の比較を作る');

// 07. Methods
s=add('６手法で異なる生成位置の決め方','生成方法', '全手法の目的を少数クラスの訓練行を増やすことに揃えます。列シャッフルはクラス内の各列を独立に再抽出します。コピュラSMOTEとCTGAN×コピュラは名称だけで実装を特定できないため、以降で今回の定義を示します。','最も単純な列シャッフルから、失敗の原因を見ます。');
table(s,[['手法','生成の基本操作'],['列シャッフル','同じクラスの列を独立に組み替える'],['Gaussian copula','周辺分布と依存を推定して生成する'],['SMOTE','同じクラスの近傍間を補間する'],['コピュラSMOTE','変換空間で補間し、元の尺度に戻す'],['CTGAN','ラベルを条件に分布を学習する'],['CTGAN×コピュラ','分布変換とGANを組み合わせる']],[365,779],{h:420,size:25});



// Behavior axes
s=add('挙動は生成位置と分類への影響で確認する','対象と目的','生成して動いたことだけを成功としません。生成点の場所、特徴間関係の維持、ラベルの妥当性、多様性や重複、分類性能を確認します。人工データでは真の生成分布を使って診断し、実データでは意味制約や近傍を代理にします。代理指標だけで正しいラベルを断定しません。','各手法について、挙動、問題、改善の順に説明します。');
table(s,[['見るもの','確認する挙動'],['生成位置','元のクラスから外れていないか'],['特徴間の関係','組み合わせや意味制約を壊していないか'],['多様性・重複','同じ例や同じ領域に偏っていないか'],['分類性能','少数例の識別が改善したか']],[345,799],{h:375,size:28});
take(s,'各手法を「確認する挙動・問題の原因・改善案」の順で整理する');

// 08. Shuffle
s=add('列シャッフルは組み合わせを壊しうる','生成方法', '説明用に少数クラスがx2=x1を満たすとします。(1,1),(3,3)から各列を独立に選ぶと(1,3),(3,1)が生まれます。列の値は観測済みでも組み合わせは関係を満たしません。これは仕組みの例で、実データの完全な制約とは区別します。','まず、関連列をまとめて動かす補助輪を考えます。');
scatter(s,[series('元の行',[[1,1],[3,3]],C.teal,'circle',13),series('組み替えた行',[[1,3],[3,1]],C.orange,'x',15)]);
label(s,'説明例：必要な関係',770,180,440);
text(s,'x₂ = x₁',770,238,440,70,48,C.navy,true);
text(s,'(1,1) と (3,3) は満たす\n(1,3) と (3,1) は外れる',770,339,440,115,29);
text(s,'各列の値が正しくても、\n組み合わせは妥当とは限らない',770,487,440,80,27,C.orange);
take(s,'依存する列を一緒に動かすことが改善候補になる');



// Shuffle guard
s=add('シャッフルの補助輪：関連する列を一緒に動かす','改善案 1／6','関連する列の値を同じ行から取れば、その列グループ内の関係を保持できます。三列の例ではx2=x1を必要な関係と仮定し、x1,x2をまとめて選び、x3を別に抽出します。グループの決定は訓練データや既知の知識に基づきます。グループ間の依存は依然壊れるため、完全な解決ではありません。','次は依存をモデルとして学ぶGaussian copulaです。');
table(s,[['処理','生成例','関係 x₂ = x₁'],['元の行','(1,1,10)、(3,3,20)','元の２行は満たす'],['列ごとに独立抽出','(1,3,20)','満たさない'],['x₁・x₂をまとめて抽出','(1,1,20)','グループ内は保つ']],[355,420,369],{h:345,size:27});
take(s,'グループ内の関係は保てても、グループ間の依存は残る課題');

// 09. Copula
s=add('コピュラは特徴間の依存を一緒に扱う','生成方法', 'Gaussian copulaではクラスごとにu_j=F_j(x_j)、z_j=Φ⁻¹(u_j)へ変換し、変換後の相関を推定します。多変量正規から生成した値を逆変換して戻します。図は依存を保つ生成の狙いを説明する座標例で、実際のコピュラ学習結果ではありません。','ただし、依存を推定するにも十分な例数が必要です。');
scatter(s,[series('観測例',[[.6,.7],[1,1],[1.5,1.6],[2.2,2.1],[3,3]]),series('依存に沿う候補',[[.85,.9],[1.3,1.2],[1.8,1.95],[2.6,2.6]],C.navy,'diamond',10)]);
[['01','各列を正規空間へ変換'],['02','変換後の相関から生成'],['03','逆変換で元の尺度へ戻す']].forEach((r,i)=>{text(s,r[0],770,192+i*110,70,54,34,C.teal,true);text(s,r[1],850,195+i*110,355,85,27);});
take(s,'少数例では相関推定が揺れるため、正則化を検討する');


// 16. Regularization
s=add('コピュラの補助輪：相関推定を正則化する','改善案', 'd特徴にはd(d−1)/2個の相関係数があります。10,30,50特徴なら45,435,1225個です。少数クラスの例数が同じでも推定する量は増えます。正則化Rλ=(1−λ)Rhat+λIで縮める候補を検証します。ただしGaussian copulaの表現能力の限界を正則化だけでは解決できません。','次は近傍間を補間するSMOTEです。');
label(s,'推定する相関係数の数：d(d−1)/2',72,166,670);
ch=s.charts.add('bar',{position:{left:60,top:228,width:650,height:320},categories:['10特徴','30特徴','50特徴'],series:[{name:'相関係数の数',values:[45,435,1225],fill:C.teal}],barOptions:{direction:'column',gapWidth:100},hasLegend:false,xAxis:{textStyle:{fontSize:23}},yAxis:{min:0,max:1400,majorGridlines:{fill:C.grid,width:1},textStyle:{fontSize:18}},dataLabels:{showValue:true,position:'outEnd',textStyle:{fontSize:23,bold:true}},chartFill:C.white});applyPresentationChartFont(ch,{fontFamily:F});
text(s,'少数例数が同じでも、\n推定は難しくなる',770,224,430,110,34,C.navy,true);
text(s,'正則化で揺れを抑える\n強さは検証データで選ぶ',770,407,430,100,29);
take(s,'正則化は安定性と依存の再現のトレードオフを持つ');


// 10. SMOTE
const islands=[[.6,1],[.85,1.15],[1,.8],[3,1],[3.15,1.2],[3.4,.8]];
const majority=[[1.75,.8],[1.9,1.3],[2.1,1],[2.25,1.4]];
s=add('SMOTEは近傍の線分も同じクラスとみなす','生成方法', 'SMOTEはxnew=xi+λ(xj−xi),0≤λ≤1で少数クラス内の近傍を補間します。図は少数クラスが二つの集団に分かれ、選んだ近傍が集団をまたぐ説明例です。十分近くに同じ集団の点があれば、必ず橋を作るわけではありません。標準化と近傍数の影響を確認します。','集団間に補間しない制約を加えるとどうなるかを考えます。',['smote']);
scatter(s,[series('少数例',islands),series('多数例',majority,C.muted,'square',9),series('集団間の補間',[[1.3,1],[1.7,1],[2.1,1],[2.5,1],[2.8,1]],C.orange,'x',12)]);
label(s,'補間の式',770,183,440);
text(s,'x_new = x_i\n+ λ(x_j − x_i)',770,240,440,120,35,C.navy,true);
text(s,'0 ≤ λ ≤ 1',770,366,440,45,25,C.muted);
text(s,'近傍が別の集団に届くと、\n多数側の領域へ入りうる',770,423,440,110,29);
take(s,'近傍数や集団内補間を、原因に対応する改善案として調べる');


// 17. local comparison
s=add('SMOTEの補助輪：集団内の近傍を使う','改善案', '左右は同じ観測座標を用いた対照の説明図です。左は集団間の近傍を選んだ場合、右は集団内に限定した場合です。右は橋が少ない一方、集団の推定や少数例の分割による不安定性が残ります。これはSMOTEの実測結果ではありません。','次は補間する空間を変えるコピュラSMOTEです。');
label(s,'集団間に補間した説明例',76,156,540,C.orange);label(s,'集団内に限定した説明例',690,156,540,C.teal);
scatter(s,[series('少数例',islands),series('多数例',majority,C.muted,'square',8),series('合成例',[[1.4,1],[1.8,1],[2.2,1],[2.6,1]],C.orange,'x',11)],{x:53,y:215,w:570,h:335});
scatter(s,[series('少数例',islands),series('多数例',majority,C.muted,'square',8),series('合成例',[[.75,1.05],[.9,.9],[3.1,1.1],[3.25,1]],C.orange,'x',11)],{x:661,y:215,w:570,h:335});
take(s,'局所化しすぎると、推定に使える例が減る');


// 11. CopulaSMOTE
s=add('コピュラSMOTEは補間する空間を変える','生成方法', '本発表の操作上の定義です。クラス内でGaussian copulaの周辺変換を行い、正規空間でSMOTEして逆変換します。周辺分布の歪みを調整する仮説ですが、特徴が独立になるわけではなく、複数集団や非凸形状も解決するとは限りません。既存の特定手法と同一とは主張しません。','変換空間の近さだけでは不十分なので、元の空間でも検査します。');
table(s,[['段階','操作','検討する理由'],['1','各列を正規空間へ変換','周辺分布の歪みを調整する'],['2','変換空間でSMOTE','距離と補間の意味を変える'],['3','元の尺度へ逆変換','生成行として分類に使う']],[135,480,529],{h:320,size:28});
text(s,'仮説',76,540,120,45,27,C.teal,true);text(s,'変換後の近さは、分類上も妥当か',220,536,970,55,32,C.navy,true);



// Copula SMOTE guard
s=add('コピュラSMOTEの補助輪：逆変換後にも検査する','改善案 4／6','変換空間で近いことは元の空間でクラスが妥当であることを保証しません。クラス内で補間し、元の空間へ戻した後に既知の意味制約を検査します。近傍や分類器の一致は真のラベルではなく代理指標です。フィルタで難しい点を落としすぎる可能性もあるため、採択前後の品質と採択率を記録します。','次に、分布を柔軟に学ぶCTGANを考えます。');
table(s,[['段階','補助輪','確認する副作用'],['変換空間の補間','同じクラス・同じ集団内を候補にする','集団を分けると例数が減る'],['元の空間へ戻す','値域・既知の関係を検査する','妥当な点まで除いていないか'],['採択後の学習','同じ追加件数で性能を比較する','簡単な点だけに偏っていないか']],[235,505,404],{h:350,size:25});
take(s,'変換後の近さだけで判断せず、採択率と少数Recallも測る');

// 12. CTGAN
s=add('CTGANの柔軟さにも少数例の制約がある','生成方法', 'CTGANはmode-specific normalizationや条件付き生成、training-by-samplingなどを用います。ラベルをカテゴリ列として含め、少数クラスを条件に生成します。条件指定のAPIは実装に応じて確認します。少数条件のデータが乏しければ、過適合やモードの偏りを起こす可能性を検証する必要があります。','まず生成量を制限する補助輪の意味を考えます。',['ctgan']);
label(s,'学習時',76,181,510,C.teal);text(s,'特徴 x とラベル y',76,243,510,70,40,C.navy,true);text(s,'連続値・カテゴリを含む\nテーブルの分布を学ぶ',76,351,510,115,30);
label(s,'生成時',690,181,510,C.orange);text(s,'y = 少数クラス',690,243,510,70,40,C.navy,true);text(s,'その条件の合成行を得る\n重複・偏り・多様性を確認する',690,351,510,115,30);
take(s,'複雑なモデルでも、観測していない分布を必ず回復できるとは限らない');


// 18. quantity
s=add('CTGANの補助輪：生成量と偏りを管理する','改善案', '説明例として少数クラスの実例が20件あり、追加倍率0,1,3で合成0,20,60件を追加します。グラフは少数ラベルを付ける訓練行だけの内訳で、多数クラスは含みません。行を等重みで学習する場合に合成行の寄与が増えることを示します。最適な生成量は検証で選びます。','次にCTGANとコピュラを組み合わせる案を比較します。');
label(s,'説明例：少数ラベルの訓練行の内訳',72,156,690);
ch=s.charts.add('bar',{position:{left:60,top:225,width:675,height:325},categories:['追加0倍','追加1倍','追加3倍'],series:[{name:'元の少数実例',values:[20,20,20],fill:C.teal},{name:'合成行',values:[0,20,60],fill:C.orange}],barOptions:{direction:'column',grouping:'stacked',gapWidth:100,overlap:100},hasLegend:true,legend:{position:'bottom',overlay:false,textStyle:{fontSize:21}},xAxis:{textStyle:{fontSize:23}},yAxis:{min:0,max:80,title:'件数',textStyle:{fontSize:18},majorGridlines:{fill:C.grid,width:1}},chartFill:C.white});applyPresentationChartFont(ch,{fontFamily:F});
text(s,'実例20件は固定',790,220,420,60,34,C.navy,true);text(s,'増えるのは\n推定した分布からの行',790,310,420,100,30);
text(s,'妥当なら助けになる\n誤りがあれば影響も増える',790,455,420,90,27,C.orange);
take(s,'候補生成数・採択数・実行時間を別々に記録する');


// 13. Combination
s=add('CTGAN×コピュラで追加効果を確かめる','生成方法', '独自案は列ごとの分布変換、CTGANでの学習と生成、逆変換と定義します。SDVにはCopulaGANという既存実装があるため、それと独自案を区別します。CTGAN内部の正規化との重複、変換の推定誤差を確認します。二つを組み合わせるだけで改善するとは断定しません。','その追加効果を、処理を分けた比較で確かめます。',['sdv']);
table(s,[['比較','確認すること'],['CTGAN単独','基準となる性能・生成品質・実行時間'],['分布変換＋CTGANの独自案','変換による学習負担の軽減があるか'],['既存CopulaGAN','独自案との仕様・処理順の違い']],[500,644],{h:330,size:27});
take(s,'変換の利点と、変換誤差・内部正規化との重複を切り分ける');



// Combined guard
s=add('CTGAN×コピュラの補助輪：追加効果を分けて測る','改善案 6／6','CTGANとコピュラを併用しただけで改善とは判断しません。CTGAN単独、変換＋CTGAN、さらに制約を加えた版を比較し、どの変更に効果があるかを調べます。既存CopulaGANと独自案を区別します。同じデータ分割と採択後の追加件数、設定探索予算を使い、計算時間も記録します。','六手法で、問題と改善案をまとめて比較します。',['sdv']);
table(s,[['比較する版','追加する処理','調べること'],['CTGAN単独','基準となる生成器','基準性能と生成品質'],['分布変換＋CTGAN','変換と逆変換','変換による追加効果'],['上記＋生成後検査','意味制約などの採択条件','制約の効果と採択の偏り']],[360,385,399],{h:345,size:27});
take(s,'変換・生成器・検査を一度に変えず、単独の効果を確認する');


// Six-method summary
s=add('６手法の問題点と補助輪の対応','問題点と改善案','この表は研究計画で、まだ測定結果ではありません。生成の失敗はデータ構造と標本数に依存します。各改善が失敗に対応するか、分類性能まで改善するかを確認します。最初から改善策を全部載せず、単独と組み合わせで比較します。','補助輪をどの順番で入れるかを固定します。');
table(s,[['手法','問題候補','改善候補'],['シャッフル','列間の依存を壊す','関連列を一緒に動かす'],['コピュラ','少数例で推定が揺れる','相関の正則化'],['SMOTE','集団間や境界へ補間する','近傍数・集団内補間'],['コピュラSMOTE','変換距離が意味に合わない','逆変換後にも検査'],['CTGAN','過適合・生成の偏り','生成量の制限と品質確認'],['CTGAN×コピュラ','変換誤差・重複処理','変換と検査の効果を分離']],[300,435,409],{h:420,size:25});


// Guard sequence
s=add('補助輪は一つずつ加えて効果を確認する','問題点と改善案','クラス内生成は今回の各手法の基本定義として扱い、その上で追加の補助輪を検証します。最初から複数の変更を加えると寄与を説明できません。生成量の調整では追加件数を変える必要がありますが、生成方法やフィルタの比較では採択後の件数を揃えて品質の違いを切り分けます。','その効果を見るために、失敗が起きる構造を制御します。');
[['01','基本版','クラス内の生成で、まず挙動を記録'],['02','補助輪を１つ追加','正則化、局所化、検査の効果を分ける'],['03','有効な補助輪を併用','性能と副作用が両立するか確認']].forEach((r,i)=>{let y=180+i*124;text(s,r[0],76,y,90,70,45,C.teal,true);text(s,r[1],200,y+3,390,65,33,C.navy,true);text(s,r[2],650,y+7,550,90,28);});
take(s,'対策前後で、失敗の減少と分類性能の変化を両方記録する');

// 20. hypotheses
s=add('人工データで失敗の原因を切り分ける','実験計画', '人工データでは依存、複数集団、重なりを別々に操作します。真の生成分布から独立したテスト標本を得る設計にします。重なり領域ではラベルが一意に決まらないため、真の事後確率を使う診断を検討します。人工データの結論は実データで再確認します。','比較手順でも、手法以外の差を揃える必要があります。');
table(s,[['変える構造','仮説','対応する改善'],['特徴間の依存','独立生成は関係を壊しやすい','関連列を一緒に生成'],['少数側の複数集団','集団間補間は橋を作りうる','集団内に補間を限定'],['クラスの重なり','除外が難例を失わせうる','採択条件と量を調整']],[350,460,334],{h:345,size:26});
take(s,'一度に変える構造を絞り、仮説と診断指標を先に決める');


// 21. protocol
s=add('分割・生成・評価を混ぜない比較手順','実験計画', 'まず訓練、検証、テストに分けます。正規化と生成器と分類器の適合は訓練のみ、生成量や正則化、採択閾値、分類閾値は検証で選びます。交差検証ならfoldごとに適合をやり直します。分類器と設定探索予算を揃え、同じ分割で複数seedを比較します。初期はロジスティック回帰と木モデルを候補にします。','目的の達成と仕組みの診断を別々の指標で評価します。',['leak']);
table(s,[['データ','役割','使う処理'],['訓練','モデルを適合','前処理・生成器・分類器の学習'],['検証','設定を選択','生成量・正則化・採択条件・閾値'],['テスト','選択後に最終評価','元の評価分布で性能を測定']],[210,300,634],{h:330,size:27});
take(s,'同じ分割・分類器・探索予算で、対照群と改善前後を比較する');


// 22. metrics
s=add('分類性能は目的、生成品質は仕組みを測る','実験計画', 'macro F1は各クラスF1の平均、balanced accuracyは各クラスRecallの平均です。少数クラスを陽性にしたPrecision,Recall,PR-AUCも併記し、PR-AUCの実装定義を固定します。品質には意味制約、分布のずれ、多様性、重複、採択率を含めます。実データの近傍一致率は真のラベルではなく代理指標です。','各手法の結果をどう整理して報告するかを決めます。');
table(s,[['評価','主な指標','確かめること'],['分類性能','macro F1・balanced accuracy','未知の実例を識別できるか'],['少数側の挙動','Recall・Precision・PR-AUC','見逃しと誤検知のバランス'],['生成品質','制約違反・多様性・重複','想定した失敗が減ったか'],['安定性と負担','seedごとの差・実行時間','効果が安定し、実用的か']],[240,465,439],{h:370,size:26});
take(s,'品質と性能が同時に改善しても、条件を変えて再確認する');



// Reporting
s=add('結果は「何が起き、何を変えたか」で示す','実験計画','これは結果報告の整理方法です。未実施の実験値を置いていません。各手法の生成位置などを先に観察し、問題の原因仮説を立て、対応する補助輪を加えます。生成品質と分類性能が別の方向に動くこともあるので両方を記録します。特定のseedだけの改善で優位性を主張しません。','最後に、今回の中心課題と実施順をまとめます。');
table(s,[['報告する順番','記録する内容'],['1. 基本版の挙動','生成点・依存・重複・少数クラスの性能'],['2. 問題の原因','どの条件で、どの仮定が崩れたか'],['3. 追加した補助輪','どの処理だけを変更したか'],['4. 改善後の挙動','失敗・性能・採択率・時間がどう変わったか']],[380,764],{h:370,size:27});
take(s,'「生成できた」から一歩進めて、問題と改善の対応を説明する');


// Closing
s=add('全ラベル付きの偏ったデータで挙動を確かめる','今回のまとめ','今回の主題はユーザーのシナリオ①です。すべてラベル付きの不均衡データで六つの手法を動かし、問題点を整理し、原因に対応する改善案を考えます。最初はシャッフル、Gaussian copula、SMOTEと対照群で評価基盤を作り、複合手法とCTGAN系を加えます。各手法の研究上の優位性はまだ主張しません。','補足には複合手法の定義と出典を置きます。');
text(s,'６手法の生成と分類の挙動を確認する',76,190,1120,80,42,C.navy,true);
text(s,'問題点を整理し、\n原因に対応する補助輪を検証する',76,310,1120,125,41,C.teal,true);
text(s,'実施順：単純手法と対照群で評価基盤を作り、CTGAN系・複合手法を追加',80,492,1120,90,27);
take(s,'発表の中心は「問題の発見」と「改善前後の比較」');

// 24. definitions appendix
s=add('補足：複合手法は処理を固定して比較する','補足', '名称だけでは一意に定まらないので操作を定義します。独自案と既存実装の一致は仕様とソースで確認が必要です。変換は訓練データ内で適合し、カテゴリ列の扱いも記録します。少数クラス条件を指定してもラベルの意味は保証されません。','次は既存のVIME実験との違いです。',['sdv']);
table(s,[['方法','今回の扱い'],['コピュラSMOTE','クラス内の周辺変換、正規空間SMOTE、逆変換'],['CTGAN×コピュラの独自案','列の分布変換、CTGAN学習・生成、逆変換'],['既存CopulaGAN','独自案と区別し、仕様・内部処理を確認']],[390,754],{h:350,size:27});
take(s,'分類や半教師ありへの拡張だけで、新規性が成立するとは断定しない');


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
