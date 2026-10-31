import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {Presentation,PresentationFile} from '@oai/artifact-tool';

const ROOT='/Users/kouta/Github/data augumation/Data-Augumation';
const DIR=ROOT+'/tmp/layout_reference_20261024';
const SKILL='/Users/kouta/.codex/plugins/cache/openai-primary-runtime/presentations/26.1022.11436/skills/presentations';
const {applyPresentationChartFont}=await import(pathToFileURL(SKILL+'/container_tools/artifact_tool_utils.mjs').href);
const p=Presentation.create({slideSize:{width:1280,height:720}});
const C={navy:'#222222',teal:'#2D8061',orange:'#D95332',ink:'#222222',muted:'#808080',grid:'#222222',pale:'#F5F5F5',white:'#FFFFFF'};
const F='Hiragino Sans';
const sources={smote:'https://www.cs.cmu.edu/afs/cs/project/jair/pub/volume16/chawla02a.pdf',ctgan:'https://papers.nips.cc/paper/2019/hash/254ed7d2de3b23ab10936522dd547b78-Abstract.html',sdv:'https://docs.sdv.dev/sdgym/benchmarking/run/local',leak:'https://imbalanced-learn.org/0.14/common_pitfalls.html',shared:'https://www.sciencedirect.com/science/article/pii/S0925231226020369'};
const manifest=[];
function text(s,t,x,y,w,h,size=30,color=C.ink,bold=false,align='left'){
 const q=s.shapes.add({geometry:'textbox',position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});
 q.text=t;q.text.style={typeface:F,fontFamily:F,fontSize:size,color,bold,alignment:align};return q;
}
function add(title,section,notes,bridge,refs=[]){
 const s=p.slides.add();const n=p.slides.items.length;s.background.fill=C.white;
 text(s,title,34,10,1212,78,title.length>26?40:48,C.ink,true,'center');
 if(title)s.shapes.add({geometry:'rect',position:{left:34,top:97,width:1212,height:1.4},fill:'#222222',line:{fill:'none',width:0}});
 text(s,section,60,686,1000,25,16,C.muted);
 text(s,String(n),1160,682,73,30,18,C.muted,false,'right');
 s.speakerNotes.text='説明\n'+notes+'\n\n次のスライドへのつなぎ\n'+bridge+'\n\n出典・位置づけ\n'+refs.map(r=>sources[r]??r).join('\n')+'\n実験日：2026-10-23。結果は同条件５回の探索的比較。';
 manifest.push({number:n,title,section});return s;
}
function take(s,t){s.shapes.add({geometry:'rect',position:{left:54,top:590,width:1172,height:70},fill:'#E6F1EB',line:{fill:'none',width:0}});text(s,t,66,605,1148,48,t.length>44?25:29,C.teal,true,'center');}
function label(s,t,x,y,w=500,color=C.muted){text(s,t,x,y,w,42,24,color,true);}
function table(s,v,widths,{x=68,y=175,w=1144,h=365,size=26}={}){
 let q=s.tables.add({rows:v.length,columns:v[0].length,left:x,top:y,width:w,height:h,values:v,columnWidths:widths});
 for(let r=0;r<v.length;r++)for(let c=0;c<v[0].length;c++){
  let z=q.getCell(r,c);z.fill=r===0?'#E6F1EB':r%2?C.white:C.pale;
  z.text.style={typeface:F,fontFamily:F,fontSize:size,bold:r===0,color:r===0?C.teal:C.ink,alignment:'center'};
 }
 q.borders.assign({fill:C.grid,width:1,style:'solid'});
 q.cells.block({row:0,column:0,rowCount:v.length,columnCount:v[0].length}).assign({margins:{left:13,right:10,top:2,bottom:2}});
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




const E=ROOT+'/output/experiments/minority_ratios_20261023/results';
const D=JSON.parse(await fs.readFile(E+'/slide_data.json','utf8'));
const methods=['none','duplicate','class_weight','shuffle','copula','smote','copula_smote','ctgan','ctgan_copula'],gens=methods.slice(3),ratios=[.1,.2,.3],datasets=['rice','raisin','grid'];
const names={none:'拡張なし',duplicate:'ランダム複製',class_weight:'クラス重み付け',shuffle:'列シャッフル',copula:'コピュラ',smote:'SMOTE',copula_smote:'コピュラSMOTE',ctgan:'CTGAN',ctgan_copula:'CTGAN×コピュラ'};
const dn={rice:'米',raisin:'レーズン',grid:'電力網'},charts=[];
const avg=a=>a.reduce((x,y)=>x+y,0)/a.length;const sd=a=>Math.sqrt(a.reduce((x,y)=>x+(y-avg(a))**2,0)/(a.length-1));
function select(d,r,m,c='logistic',v='base'){return D.metrics.filter(x=>x.dataset===d&&x.minority_fraction===r&&x.method===m&&x.classifier===c&&x.variant===v)}
const mean=(d,r,m,c='logistic',metric='macro_f1')=>avg(select(d,r,m,c).map(x=>x[metric]));
function fmt(d,r,m,c='logistic'){let a=select(d,r,m,c).map(x=>x.macro_f1);return avg(a).toFixed(3)+' ± '+sd(a).toFixed(3)}
function prose(title,section,blocks,conclusion,notes='',refs=[]){let s=add(title,section,notes||blocks.join('\n'),'次の内容へ進みます。',refs);blocks.forEach((t,i)=>text(s,t,76,177+i*120,1125,102,31));if(conclusion)take(s,conclusion);return s}
function note(s,t){text(s,t,76,133,1125,32,21,C.muted)}
function tbl(s,v,widths,opt={}){return table(s,v,widths,{y:178,h:390,size:25,...opt})}
function resultTable(d,c){let s=add(dn[d]+'：'+(c==='logistic'?'ロジスティック回帰':'勾配ブースティング'),'実験結果','Macro-F1の５回平均±標本SD。閾値0.5、固定設定。比率は拡張前の訓練集合における少数割合。全６手法は訓練クラス件数1:1へ拡張。10/20/30%のテスト集合は同じseedで共通。','比率による変化を比較します。');note(s,'Macro-F1（５回の平均 ± 標本標準偏差）／割合は拡張前');tbl(s,[['手法','少数10％','少数20％','少数30％'],...methods.map(m=>[names[m],...ratios.map(r=>fmt(d,r,m,c))])],[365,260,260,259],{y:175,h:405,size:23});let winners=ratios.map(r=>{let order=[...methods].sort((a,b)=>mean(d,r,b,c)-mean(d,r,a,c));return Math.round(r*100)+'％：'+names[order[0]]});take(s,'最高平均　'+winners.join(' ／ '));}
// 1
s=add('','','全件ラベル付き二値分類を対象とし、少数クラス割合を10%,20%,30%に制御した実験。','まずデータ拡張の課題を定義します。');
text(s,'ゼミ発表',80,185,1120,100,76,C.ink,false,'center');
text(s,'テーブルデータにおけるデータ拡張',60,325,1160,80,49,C.ink,false,'center');
text(s,'少数クラスの割合：10％・20％・30％の比較',80,435,1120,48,28,C.ink,false,'center');
text(s,'齊藤光汰',80,505,1120,48,27,C.ink,false,'center');

prose('発表の流れ','導入',['１．データ拡張の課題：何を改善し、何を保つ必要があるか','２．６手法の解説：どう生成し、どのような仮定を置くか','３．公開データで実験：少数割合10％・20％・30％を比較'],'すべての行に正解ラベルが付いている条件を扱う');
s=add('クラス不均衡で生じる学習上の課題','課題の定義','説明用の例。100件中少数10件の場合、全て多数と予測すれば正解率90%だが少数再現率0%。今回の実験結果とは区別する。多数例だけで識別を学べるという意味ではない。','少数例を増やすと何が変わるか考えます。');note(s,'説明例：100件中、少数クラス10件・多数クラス90件');tbl(s,[['予測の方法','全体の正解率','少数の再現率'],['すべて多数クラスと予測','90％','０％']],[560,292,292],{y:200,h:160,size:28});text(s,'少数クラスの誤りが、全体の正解率に表れにくい\n少数例が少ないと、クラス内の多様性も学びにくい',76,418,1125,120,32);take(s,'目標は件数を増やすことではなく、少数クラスの識別を改善すること');
prose('データ拡張の課題を定義する','課題の定義',['課題１：少数例の分布を、少ない観測からどこまで再現できるか','課題２：列どうしの関係や、ラベルとの対応を保てるか','課題３：生成例を加えると、未使用データでの識別が改善するか'],'「生成できた」と「役に立った」を分けて検証する','教師付きデータ拡張は特徴とラベルの組を追加する。少数クラス条件の分布P(X|Y=minority)を観測データから近似する。新しい正解ラベルを独立に観測する操作ではない。');
s=add('６手法が少数例を増やす方法','手法の全体像','列再抽出、統計的分布、局所補間、生成学習の違い。混合手法は操作上の定義を明示する。','単純な列の組み替えから説明します。');tbl(s,[['考え方','手法','生成位置の決め方'],['列の組み替え','列シャッフル','各列を別々に再抽出'],['分布の推定','コピュラ','周辺分布と依存を推定'],['近傍の補間','SMOTE','近い少数例の間を補間'],['変換＋補間','コピュラSMOTE','正規化した空間で補間'],['生成モデル','CTGAN','条件付きGANで学習'],['変換＋生成モデル','CTGAN×コピュラ','正規化してGANで学習']],[290,350,504],{h:410,size:25});
s=add('列シャッフル：観測済みの値を組み替える','手法１／６','行順を入れ替えるだけでは新しい特徴ベクトルができない。本実装は少数クラスの列ごとに独立に復元抽出し組み合わせる。以下は説明例。','列間の依存を扱う方法がコピュラです。');note(s,'説明例：元の少数クラスが x₂ = x₁ を満たす場合');tbl(s,[['行','特徴 x₁','特徴 x₂'],['元の行Ａ','１','１'],['元の行Ｂ','３','３'],['列を別々に抽出した生成例','１','３']],[560,292,292],{y:195,h:270,size:28});text(s,'長所：単純で速い。各列の観測値を利用できる\n課題：列の対応を壊し、実在しない組み合わせを作りうる',76,493,1125,92,28);take(s,'補助輪の候補：関連する列を同じ行からまとめて抽出する');
s=add('コピュラ：周辺分布と依存を分けて扱う','手法２／６','Gaussian copulaの操作。少数クラスの経験分布Fjでuj=Fj(xj)、zj=Φ逆(uj)。変換後の相関を推定して多変量正規から生成、xj=Fj逆(Φ(zj))。今回はR=.95Rhat+.05Iで縮小。非線形な等式は保証しない。','局所的に近い例を使うSMOTEを説明します。');text(s,'① 各列の順位を、標準正規分布の尺度に変換する\n　 uⱼ = Fⱼ(xⱼ)、zⱼ = Φ⁻¹(uⱼ)',76,178,1125,110,31);text(s,'② 変換後の相関を推定し、まとめて生成する\n③ 各列を逆変換し、元の尺度に戻す',76,325,1125,120,31);text(s,'長所：列ごとの分布と依存を同時に扱える\n課題：Gaussian copulaで表せる依存には限界がある',76,484,1125,94,28);take(s,'今回はGaussian copulaを使用。相関を５％縮小して推定を安定化');
s=add('SMOTE：少数例の近傍を線形補間する','手法３／６','Chawla et al. 2002。標準化は実訓練集合だけで学習。少数例からi、その５近傍からjを選びλ一様0〜1で線分上に生成。近傍の間が同じクラスである保証はない。','分布を変換してから補間する方法へ進みます。',['smote']);text(s,'x_new = xᵢ + λ(xⱼ − xᵢ)　　0 ≤ λ ≤ 1',76,180,1125,70,38,C.navy,true);tbl(s,[['説明例','特徴 x₁','特徴 x₂'],['少数例 i','１','２'],['近傍の少数例 j','３','４'],['λ=0.5 の生成例','２','３']],[560,292,292],{y:270,h:225,size:28});text(s,'長所：近傍の間に新しい行を作れる\n課題：クラスの境界や異なる集団をまたぐ可能性',76,516,1125,73,26);take(s,'今回は標準化した空間を使い、近傍数 k=5 で比較する');
prose('コピュラSMOTE：変換空間で近傍を補間','手法４／６',['① 少数クラスの各列を、経験順位から正規分布の尺度に変換','② 変換後の空間で、５近傍を使ってSMOTE型の補間','③ 少数クラスの経験分布を使い、元の尺度に逆変換'],'尺度や歪みを調整できる一方、逆変換後の関係は保証されない','本資料の操作上の定義。Gaussian copulaの相関から正規生成する方法ではなく、周辺分布変換＋近傍補間。変換後の距離が近傍の選択を変え、非線形な逆変換は元空間の線形等式を保つとは限らない。',['smote']);
s=add('CTGAN：ラベルを条件に行の分布を学習','手法５／６','Xu et al.2019。生成器と識別器の対抗学習。CTGANは連続値のモード別正規化と離散列の条件ベクトルを用いる。本比較では全特徴とラベルを学習し、minorityを条件指定して抽出。生成ラベルの不一致は棄却。条件指定は真のクラス保証ではない。','入力分布を変換してGANを使う方法を説明します。',['ctgan']);text(s,'生成器：実データに似た行を作る\n識別器：実データと生成データを見分ける',76,180,1125,123,36,C.navy,true);text(s,'両者を競わせて学習し、少数ラベルを条件に生成する',76,348,1125,65,31);text(s,'長所：複雑な特徴間の依存を学習することを狙う\n課題：少数例の不足や学習条件の影響を受ける',76,471,1125,112,30);take(s,'今回のCTGAN２法は、同じ構成・300 epochで学習する');
prose('CTGAN×コピュラ：分布変換とGANを組み合わせる','手法６／６',['① クラスごとに、各列を経験順位から正規分布の尺度に変換','② 変換した特徴とラベルを使い、CTGANを学習する','③ 少数条件で生成し、少数クラスの経験分布で逆変換する'],'今回の実装をこの名前で呼ぶ。公式CopulaGANとの同一性は主張しない','コピュラの周辺分布変換とCTGANを組み合わせる操作上の定義。クラスごとに別の変換器。少数用分布で逆変換するので周辺の観測範囲に戻るが列間の等式や本当のクラスは保証しない。',['ctgan']);
s=add('６手法で異なる仮定と課題','手法の整理','仮定が成立すれば必ず性能向上する、という主張ではない。少数クラスの観測が限られる条件で、各仮定がどの程度役立つか実験する。','ここから実験条件と結果を示します。');tbl(s,[['手法','主な仮定・狙い','注意する課題'],['列シャッフル','列を独立に組み替えられる','列間の依存を失う'],['コピュラ','変換後の相関で依存を表す','非線形な制約'],['SMOTE','近傍間も同じクラス','境界・集団をまたぐ補間'],['コピュラSMOTE','変換後の距離が有用','元尺度に戻した関係'],['CTGAN','分布を学ぶ情報がある','少数例と学習の安定性'],['CTGAN×コピュラ','分布変換が学習に役立つ','変換とGAN双方の誤差']],[325,430,389],{h:410,size:24});
prose('公開データで確かめること','実験の目的',['少数割合が10％・20％・30％になると、手法の効果は変わるか','単純な複製や重み付けと比べても、生成する利点があるか','分類性能が良い手法は、特徴間の関係も保てているか'],'訓練件数を固定し、少数割合の違いを比較する');
s=add('使用する公開データ','実験条件','UCI公式データ、CC BY4.0。全件ラベルあり、全特徴数値。Gridは模擬データ。stabはターゲット直結のため除外。','少数割合の作り方を示します。',D.metadata.filter(x=>x.seed===11&&x.minority_fraction===.1).map(x=>x.source));tbl(s,[['データ','元の件数／入力特徴','少数クラスとしたラベル'],['米（Rice）','3,810件／７特徴','Cammeo'],['レーズン（Raisin）','900件／７特徴','Besni'],['模擬電力網（Grid）','10,000件／12特徴','stable']],[370,390,384],{h:300,size:26});text(s,'米・レーズンは画像から抽出した形状特徴\n電力網はシミュレーション。連続ターゲット stab を入力から除く。',76,500,1125,90,27);take(s,'「少数」は実験で作る条件。元データの割合と区別する');
s=add('少数割合10％・20％・30％の作り方','実験条件','元データを層化70:30分割後、訓練側のみ抽出。固定総数は米1100,Raisin350,Grid1100。総数1100上限で多数が90%と少数30%を共に確保できる10の倍数。各クラスで同じ乱数の並びを使用し各比率はprefixを選択。訓練多数例は比率が増えると減り、少数例が増える。純粋な比率だけの因果効果ではない。','同じテスト集合で各比率を比較します。');note(s,'表は多数件数／少数件数。全件に正解ラベルがある。');tbl(s,[['データ／固定総数','少数10％','少数20％','少数30％'],['米／1,100','990／110','880／220','770／330'],['レーズン／350','315／35','280／70','245／105'],['電力網／1,100','990／110','880／220','770／330']],[380,254,255,255],{h:280,size:27});text(s,'生成法は、少数件数を多数件数と同じになるまで増やす\n米の追加件数：10％で880件、20％で660件、30％で440件',76,497,1125,90,28);take(s,'割合を変えても、拡張前の訓練総数とテスト集合を共通にする');
prose('実験手順と比較の対照','実験条件',['元データを訓練70％・テスト30％に分割し、訓練側だけ割合を調整','６生成法に加え、拡張なし・ランダム複製・重み付けを比較','２種類の分類器で評価し、同じ乱数５種を全条件に使用'],'３データ × ３割合 × ５回。テストは元のクラス比率を保つ','乱数11,23,37,51,67。LRとHistGradientBoosting。学習・周辺分布変換・標準化は訓練内。ハイパーパラメータ探索なし、判定閾値0.5。比率別に同じテスト集合を使用。５回は重なる反復holdoutで5foldCVではない。',['leak']);
prose('評価指標','実験条件',['主指標：Macro-F1（少数・多数それぞれのF1の平均）','補助指標：少数クラスの再現率・適合率、Balanced accuracy','生成品質：既知の関係の違反率、相関の誤差、複製率'],'結果は５回の平均 ± 標本標準偏差。小差の有意性は主張しない','少数クラスのF1だけでなく多数の誤りも評価。全AP,ROC-AUCと混同行列はCSVに保存。合成行の真のラベルは独立に観測していない。近傍ラベル一致は代理指標。');
for(const d of datasets)for(const c of ['logistic','hist_boost'])resultTable(d,c);
// 24
s=add('電力網：少数割合と性能の変化','実験結果','Macro-F1の５回平均。点のばらつきは前スライド表を参照。Boostのみ。複数データのスコアを混合平均しない。','生成品質も確認します。');note(s,'勾配ブースティング／Macro-F1の平均（ばらつきは前の表）');const colors=['#647789','#167C80','#102B46','#D96B35','#8B63A9','#C59B28'];ch=s.charts.add('line',{position:{left:70,top:180,width:1130,height:390},categories:['10％','20％','30％'],series:gens.map((m,i)=>({name:names[m],values:ratios.map(r=>mean('grid',r,m,'hist_boost')),line:{fill:colors[i],width:3},marker:{symbol:'circle',size:7,fill:colors[i]}})),hasLegend:true,legend:{position:'bottom',textStyle:{fontSize:19}},xAxis:{title:{text:'拡張前の少数割合',textStyle:{fontSize:23}},textStyle:{fontSize:23}},yAxis:{min:.65,max:.95,majorUnit:.05,title:{text:'Macro-F1',textStyle:{fontSize:23}},textStyle:{fontSize:19},majorGridlines:{fill:C.grid,width:1}},chartFill:C.white});applyPresentationChartFont(ch,{fontFamily:F});charts.push(p.slides.items.length);take(s,'学習データの構成が変わると、生成法の効果も変わる');
s=add('生成品質：電力の収支関係の違反率','実験結果','Gridの合成行でabs(p1+p2+p3+p4)>.01の割合。５回平均。元の少数例の違反率0%。線形関係を満たす行の凸結合は同じ関係を保つため、SMOTEではこの等式を保てる。分類の正しさとは別。','結果を課題と対応させます。');note(s,'電力網：|p₁+p₂+p₃+p₄| > 0.01 の生成例の割合（低いほど良い）');tbl(s,[['手法','少数10％','少数20％','少数30％'],...gens.map(m=>[names[m],...ratios.map(r=>{let a=D.quality.filter(x=>x.dataset==='grid'&&x.minority_fraction===r&&x.method===m&&x.variant==='base');return(100*avg(a.map(x=>x.relation_violation))).toFixed(1)+'％'})])],[365,260,260,259],{h:390,size:26});take(s,'分布を学習できても、等式を満たす保証はない');
s=add('実験結果をデータ拡張の課題に戻して読む','考察','下記の観察は今回の固定設定での結果。単純対照と性能、割合変化、構造整合性という異なる観点を区別する。','次の改善案を示します。');note(s,'LR＝ロジスティック回帰。値はMacro-F1の５回平均。');tbl(s,[['課題','今回の比較で確認する点'],['少数割合で効果は変わるか','米のLR：拡張なし 10％ 0.880、30％ 0.927'],['生成する利点があるか','米のLR：複製は10％ 0.928、30％ 0.927'],['関係やラベルを保てるか','電力収支の違反は、生成学習でも残る']],[440,704],{h:300,size:28});text(s,'生成データの真のクラスは未確認\n性能の上昇だけで、生成例がすべて正しいとは言えない',76,505,1125,80,28);take(s,'「何が改善したか」と「何が残る課題か」を分ける');
s=add('課題に対応する改善案','改善案','下記は今後の比較候補。今回の主比較は固定設定。別途コードで既知制約の修正前後も保存しているが主比較の数値には修正を含めない。','結論と限界を整理します。');tbl(s,[['問題の原因','補助輪として試すこと'],['シャッフルで列の関係が崩れる','関連列をまとめて抽出する'],['分布モデルが等式を保証しない','独立な列を生成し、従属列は算出する'],['近傍の補間が境界をまたぐ','近傍数やクラスタ内補間を検証する'],['GANの学習条件に依存する','学習回数や生成比率を訓練内で調整する']],[580,564],{h:360,size:27});take(s,'改善案も同じテスト条件で比較し、効果を確かめる');
prose('今回の実験の限界','限界',['人工的に作った10％・20％・30％。実運用の偏りとは異なる','固定設定・閾値0.5。調整後の各手法の最良性能ではない','数値の二値分類３件。カテゴリ混在やラベルなしは未検証'],'割合を変えると少数・多数の観測件数も変わる点に注意する','元のテスト比率を保持し、事前確率補正なし。５回のholdoutはテストが重なる。米とレーズンは同系の形状特徴、電力網はシミュレーション。CTGANxCopula等は操作上の定義。');
prose('まとめ','結論',['データ拡張の課題は、少数例の識別を改善しつつ関係を保つこと','６手法は、列の組み替え・分布推定・補間・学習の仮定が異なる','米のロジスティック回帰では、少数割合を増やすと拡張なしとの差が縮小'],'手法の優劣は、データ・分類器・少数割合を含めて評価する');
s=add('再現のための実装設定','付録','米レーズンのArea/ConvexAreaは全生成法で整数化。他の制約修正はbaseには含めない。生成ラベルと真のラベルは区別。モデルpickleは添付対象外。','文献と配布元を示します。');tbl(s,[['設定','値'],['乱数／テスト','11,23,37,51,67／層化30％'],['コピュラ／SMOTE','相関５％縮小／k=5'],['CTGAN２法','300 epoch、hidden=(128,128)、batch=200、pac=10'],['ロジスティック回帰','標準化、C=1、max_iter=2000'],['勾配ブースティング','100反復、葉15、L2=1、早期終了なし']],[380,764],{h:390,size:25});take(s,'生成行、訓練・テスト分割、全指標、設定を添付データに保存');
s=add('参考文献と公開データの出典','付録','共有されたScienceDirect論文の本文は確認できておらず、今回内容や新規性は引用しない。UCIデータCCBY4.0。詳細URLは本ノート。','以上です。',['smote','ctgan',...D.metadata.filter(x=>x.seed===11&&x.minority_fraction===.1).map(x=>x.source)]);text(s,'Chawla et al. (2002)  SMOTE\nXu et al. (2019)  Modeling Tabular Data using Conditional GAN',76,175,1125,115,29,C.navy,true);text(s,'UCI：Rice Cammeo and Osmancik  DOI: 10.24432/C5MW4Z\nUCI：Raisin  DOI: 10.24432/C5660T\nUCI：Electrical Grid Stability  DOI: 10.24432/C5PG66',76,345,1125,165,27);text(s,'公開データは CC BY 4.0。実装の操作上の定義は本文と添付資料に記載。',76,555,1125,60,24,C.muted);
await fs.writeFile(DIR+'/manifest.json',JSON.stringify(manifest,null,2));await fs.writeFile(DIR+'/chart-slides.json',JSON.stringify(charts));await(await PresentationFile.exportPptx(p)).save(DIR+'/candidate.pptx');
for(let i=0;i<p.slides.items.length;i++){let b=await p.export({slide:p.slides.items[i],format:'png',scale:1});await fs.writeFile(DIR+'/slide-'+String(i+1).padStart(2,'0')+'.png',new Uint8Array(await b.arrayBuffer()));}
console.log(JSON.stringify({slides:p.slides.items.length,charts}));
