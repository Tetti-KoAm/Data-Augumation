import fs from 'node:fs/promises';
import {Presentation,PresentationFile} from '@oai/artifact-tool';
const DIR='/Users/kouta/Github/data augumation/Data-Augumation/tmp/copula_interpolation_slide';
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

const s=add('逆累積分布の線形補間：具体例','生成した身長の位置 u = 0.65 を、身長cmへ戻す。','共通データ10人を使用。NumPy quantile(method="linear")の定義、r=1+(n−1)u、k=floor(r)、w=r−k、Qhat=(1−w)x(k)+w x(k+1)。u=1では最大値を直接返す。これは線形補間した分位点で、階段状の逆経験CDFそのものではない。身長第6順序統計量173、第7統計量175。乱数は条件付き生成で位置を作る段階に使い、この補間段階は決定的な計算。根拠：research-bench/src/tabular_research/corruption.py _from_latent。',[],'');
const t=table(s,[['小さい順','1','2','3','4','5','6','7','8','9','10'],['身長 cm','155','160','165','168','170','173','175','178','182','185']],54,192,1172,92,23,[132,...Array(10).fill(104)]);
for(const c of [6,7])for(const r of [0,1]){t.getCell(r,c).fill='#D7EBE3';t.getCell(r,c).text.style={typeface:F,fontSize:23,bold:true,color:G,alignment:"center",verticalAlignment:"middle"};}
txt(s,'線形補間の一般式',65,304,595,38,28,true,T);
txt(s,'r = 1 + (n − 1)u\nk = ⌊r⌋,   w = r − k',70,353,580,82,30,true,T);
txt(s,'Q̂(u) = (1 − w)x₍ₖ₎ + wx₍ₖ₊₁₎',70,438,620,50,31,true,T);
txt(s,'n：データ数　k：rを切り捨てた順番\nw：次の値に近づける重み　x₍ₖ₎：k番目の値',70,498,625,64,24);
txt(s,'今回の値を代入',735,304,490,38,28,true,T);
txt(s,'n = 10、u = 0.65\nr = 1 + 9 × 0.65 = 6.85\nk = 6、w = 0.85\n6番目：173 cm、7番目：175 cm',740,352,480,142,28);
txt(s,'173 cmから175 cmへ、85%進む。',740,511,480,42,25,true,G);
rect(s,54,582,1172,77,'#E7F2EC');
txt(s,'Q̂(0.65) = 0.15 × 173 + 0.85 × 175 = 174.7 cm',68,597,1144,49,34,true,G,'center');
txt(s,'この補間の段階では乱数を引かず、生成済みの位置から値を計算する。',65,674,1150,29,19,false,'#777777');
await (await PresentationFile.exportPptx(p)).save(DIR+'/candidate.pptx');
const b=await p.export({slide:s,format:'png',scale:1});await fs.writeFile(DIR+'/preview.png',new Uint8Array(await b.arrayBuffer()));
