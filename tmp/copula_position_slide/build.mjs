import fs from 'node:fs/promises';
import {Presentation,PresentationFile} from '@oai/artifact-tool';
const DIR='/Users/kouta/Github/data augumation/Data-Augumation/tmp/copula_position_slide';
const p=Presentation.create({slideSize:{width:1280,height:720}});
const F='Noto Sans JP', K='#222222', G='#2E7D5B', T='#2B6777', O='#E0562B', R='#D94343';
const SRC={base:'https://www.columbia.edu/~mh2078/QRM/Copulas_MasterSlides.pdf',seg:'https://www.columbia.edu/~rf2283/Conference/1Fundamentals%20%281%29Seagers.pdf',sch:'https://people.math.ethz.ch/~embrecht/ftp/copulas.pdf',t:'https://doi.org/10.1111/j.1751-5823.2005.tb00254.x',vine:'https://www.annualreviews.org/content/journals/10.1146/annurev-statistics-040220-101153',beta:'https://arxiv.org/abs/1607.04430',vime:'https://papers.nips.cc/paper/2020/hash/7d97667a3e056acab9aaf653807b4a03-Abstract.html',cc:'https://arxiv.org/abs/2404.17489',udell:'https://arxiv.org/abs/1910.12845',shap:'https://martinjullum.com/publication/aas-2021-explaining/aas-2021-explaining.pdf'};
let n=0;const manifest=[];
function txt(s,text,x,y,w,h,size=27,bold=false,color=K,align='left'){
 let q=s.shapes.add({geometry:'textbox',position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});q.text=text;q.text.style={typeface:F,fontSize:size,bold,color,alignment:align,autoFit:'none',verticalAlignment:'middle'};return q;
}
function rect(s,x,y,w,h,fill,line='none'){return s.shapes.add({geometry:'rect',position:{left:x,top:y,width:w,height:h},fill,line:{fill:line,width:line==='none'?0:1.3}})}
function add(title,lead,notes='',refs=[],section='コピュラの基礎'){
 const s=p.slides.add();n++;s.background.fill='#FFFFFF';
 txt(s,title,36,20,1208,66,44,true,K,'center');rect(s,34,97,1210,2,K);
 txt(s,lead,54,118,1172,64,28,true);
 txt(s,section,52,683,1090,25,16,false,'#777777');txt(s,String(n),1180,681,58,28,18,false,'#777777','right');
 s.speakerNotes.textFrame.setText(notes+'\n\n出典・根拠\n'+refs.map(r=>SRC[r]??r).join('\n'));
 manifest.push({slide:n,title,section});return s;
}
function panel(s,x,y,w,h,title,body,color=K,size=26){rect(s,x,y,w,h,'#F6F6F6');txt(s,title,x+20,y+12,w-40,50,29,true,color);txt(s,body,x+20,y+70,w-40,h-80,size)}
function takeaway(s,text,color=G){rect(s,54,590,1172,68,color===O?'#FFF2EB':'#E7F2EC');txt(s,text,74,600,1132,47,27,true,color,'center')}
function rows(s,arr,y=203,h=345,size=28){let step=h/arr.length;for(let i=0;i<arr.length;i++){txt(s,`${i+1}`,58,y+i*step,50,step-8,34,true,T,'center');txt(s,arr[i],132,y+i*step,1070,step-8,size)}}
function table(s,values,x=54,y=205,w=1172,h=340,size=25,widths){
 const a=s.tables.add({rows:values.length,columns:values[0].length,left:x,top:y,width:w,height:h,values,columnWidths:widths??(values[0].length===2?[280,w-280]:undefined)});
 a.borders.assign({fill:'#D3D3D3',width:1});
 for(let r=0;r<values.length;r++)for(let c=0;c<values[0].length;c++){let cell=a.getCell(r,c);cell.fill=r===0?'#E7F2EC':r%2?'#FFFFFF':'#F6F6F6';cell.text.style={typeface:F,fontSize:size,color:r===0?G:K,bold:r===0,alignment:'center',verticalAlignment:'middle'};}
 if(values.length>8){a.cells.block({row:0,column:0,rowCount:values.length,columnCount:values[0].length}).assign({margins:{top:1,bottom:1,left:4,right:4}});for(let r=0;r<values.length;r++)a.rows[r].height=h/values.length;}
 return a;
}
function equation(s,text,y=228,size=43){rect(s,54,y-10,1172,105,'#F6F6F6');txt(s,text,74,y,1132,80,size,true,T,'center')}
function scatter(s,xs,ys,x,y,w,h,xlabel='U：身長の位置',ylabel='V：体重の位置',color=T,min=0,max=1){
 return s.charts.add('scatter',{position:{left:x,top:y,width:w,height:h},hasLegend:false,scatterOptions:{style:'marker'},series:[{name:'説明用データ',xValues:xs.map(x=>+x.toFixed(6)),values:ys.map(y=>+y.toFixed(6)),fill:color,line:{fill:'none',width:0},marker:{symbol:'circle',size:5}}],xAxis:{title:{text:xlabel,textStyle:{typeface:F,fontSize:18}},min,max,numberFormatCode:'0.0',textStyle:{typeface:F,fontSize:16},majorGridlines:{fill:'#E0E0E0',width:1}},yAxis:{title:{text:ylabel,textStyle:{typeface:F,fontSize:18}},min,max,numberFormatCode:'0.0',textStyle:{typeface:F,fontSize:16},majorGridlines:{fill:'#E0E0E0',width:1}},chartFill:'#FFFFFF',plotAreaFill:'#F6F6F6'});
}


const s=add('身長の位置0.65の生成過程','体重72 kgを残し、マスクした身長の位置を条件付きで生成する。','共通の10人の体重：45,55,50,60,67,75,63,70,90,80 kg。72kg以下7人。_to_latentは未観測値72kgでleft=right=7、u=.7。rho=.6は説明用で、共通10人から推定した実測値ではない。Phi^-1(.7)=.5244005、mu=.3146403、sd=.8。epsilon=.0885ならz=.3854403、Phi(z)=.6500445。表記は丸め値。epsilonは逆算して選んだ例で、実行時は標準正規から抽出するためuは毎回変わる。実装の正則化・jitterは直感を優先して省略。乱数生成後、linear quantileのu=.65を例に174.7cmへ戻す。根拠：research-bench/src/tabular_research/corruption.py。',[],'');
txt(s,'設定：潜在空間の相関 ρ = 0.6（説明用の仮定）',65,181,1150,38,26,true,T);
const ys=[240,323,406,489];
const labels=['① 体重を確率位置へ','② 正規の尺度へ変換','③ 身長の潜在値を生成','④ 身長の位置へ戻す'];
const formulas=['v = 7 / 10 = 0.7','zᵧ = Φ⁻¹(0.7) ≈ 0.524','zₓ = ρzᵧ + √(1 − ρ²) ε','u = Φ(zₓ) ≈ Φ(0.385) ≈ 0.65'];
const explain=['共通データ10人のうち、72 kg以下は7人。','Φ⁻¹：標準正規分布の逆累積分布関数。','ε ~ N(0, 1)。ε ≈ 0.0885なら、zₓ ≈ 0.315 + 0.8 × 0.0885 ≈ 0.385。','Φ：標準正規分布の累積分布関数。'];
for(let i=0;i<4;i++){txt(s,labels[i],65,ys[i],330,34,27,true,T);txt(s,formulas[i],425,ys[i]-3,795,42,32,true,T);txt(s,explain[i],425,ys[i]+41,795,36,i===2?22:25);}
rect(s,54,586,1172,74,'#E7F2EC');txt(s,'0.65は乱数から得られる位置の一例。この後、逆変換で約174.7 cmへ戻す。',72,604,1136,42,27,true,G,'center');
txt(s,'実際の生成ではεを乱数で引くため、身長の位置uは毎回変わる。',65,675,1150,29,19,false,'#777777');
await (await PresentationFile.exportPptx(p)).save(DIR+'/candidate.pptx');
const b=await p.export({slide:s,format:'png',scale:1});await fs.writeFile(DIR+'/preview.png',new Uint8Array(await b.arrayBuffer()));
