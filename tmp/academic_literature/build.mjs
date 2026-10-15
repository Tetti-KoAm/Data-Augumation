import fs from 'node:fs/promises';
import {Workbook, SpreadsheetFile} from '@oai/artifact-tool';
const out='/Users/kouta/Github/data augumation/Data-Augumation/outputs/academic_seminar_20261006';
const wb=Workbook.create();
const s=wb.worksheets.add('文献一覧');
const n=wb.worksheets.add('研究との関連・付記');
const rows=[
 [1,'Jinsung Yoon; Yao Zhang; James Jordon; Mihaela van der Schaar',2020,'VIME: Extending the Success of Self- and Semi-supervised Learning to Tabular Domain','Advances in Neural Information Processing Systems 33 (NeurIPS 2020)','会議論文','公式会議掲載ページ','https://proceedings.nips.cc/paper_files/paper/2020/hash/7d97667a3e056acab9aaf653807b4a03-Abstract.html',new Date('2026-10-06T00:00:00Z')],
 [2,'Dara Bahri; Heinrich Jiang; Yi Tay; Donald Metzler',2022,'SCARF: Self-Supervised Contrastive Learning using Random Feature Corruption','International Conference on Learning Representations (ICLR 2022)','会議論文','arXiv:2106.15147v2（初稿2021年、ICLR採択情報あり）','https://arxiv.org/abs/2106.15147',new Date('2026-10-06T00:00:00Z')],
 [3,'Wei Cui; Rasa Hosseinzadeh; Junwei Ma; Tongzi Wu; Yi Sui; Keyvan Golestan',2024,'Tabular Data Contrastive Learning via Class-Conditioned and Feature-Correlation Based Augmentation','arXiv:2404.17489v2','プレプリント','arXiv:2404.17489v2（2024-04-30改訂）','https://arxiv.org/abs/2404.17489',new Date('2026-10-06T00:00:00Z')],
 [4,'Yuxuan Zhao; Madeleine Udell',2020,'Missing Value Imputation for Mixed Data via Gaussian Copula','Proceedings of the 26th ACM SIGKDD International Conference on Knowledge Discovery & Data Mining (KDD 2020)','会議論文','arXiv:1910.12845v3（初稿2019年、KDD公式採択ページでも確認）','https://arxiv.org/abs/1910.12845',new Date('2026-10-06T00:00:00Z')],
 [5,'Kjersti Aas; Martin Jullum; Anders Løland',2021,'Explaining individual predictions when features are dependent: More accurate approximations to Shapley values','Artificial Intelligence, 298, Article 103502','学術雑誌論文','DOI: 10.1016/j.artint.2021.103502','https://martinjullum.com/publication/aas-2021-explaining/aas-2021-explaining.pdf',new Date('2026-10-06T00:00:00Z')]
];
s.getRange('A1:I1').values=[['No.','著者','発表年','論文名','掲載誌・会議名','文献種別','識別子・確認内容','実在確認先・入手先URL','確認日']];
s.getRange('A2:I6').values=rows;
s.getRange('I2:I6').setNumberFormat('yyyy-mm-dd');
s.getRange('C2:C6').setNumberFormat('0');
s.getRange('A1:I6').format.font={name:'Arial',size:11,color:'#243247'};
s.getRange('A1:I6').format.wrapText=true;
s.getRange('A1:I6').format.verticalAlignment='top';
s.getRange('A1:I1').format.fill='#243B53';
s.getRange('A1:I1').format.font={name:'Arial',size:11,bold:true,color:'#FFFFFF'};
s.getRange('A1:I1').format.horizontalAlignment='center';
s.getRange('A1:I1').format.rowHeight=38;
s.getRange('A2:I6').format.rowHeight=78;
const widths=[6,31,9,53,42,17,36,55,14];
widths.forEach((w,i)=>s.getRangeByIndexes(0,i,6,1).format.columnWidth=w);
for(const r of [2,4,6])s.getRange(`A${r}:I${r}`).format.fill='#F0F4F8';
s.tables.add('A1:I6',true,'LiteratureTable');
s.freezePanes.freezeRows(1);
s.freezePanes.freezeColumns(1);
s.showGridLines=false;
s.tabColor='#243B53';
const notes=[
 ['課題1　文献5本',''],
 ['研究テーマ','表形式データの半教師あり学習における、特徴間の依存を考慮したGaussian copulaによるデータ拡張'],
 ['氏名・学籍番号','提出前に記入'],
 ['No.／文献','要点・自分の研究との関連（生成AIによる整理）'],
 ['1　VIME','特徴を置換したデータからマスク推定と元の値の復元を学習し、半教師あり学習へ利用する。現在の研究の基準手法であり、置換処理をコピュラによる条件付き生成へ変更する際の出発点となる。'],
 ['2　SCARF','ランダムな特徴置換で作るビューを利用した表形式データの対照学習。VIMEと異なる学習目的でも置換による拡張が使われることを確認し、拡張手法と学習目的の効果を分けて考えるために選定。'],
 ['3　Cui et al.','擬似ラベルを用いて同じクラスの行から置換値を採り、特徴相関に基づく置換対象の選択も検討する。クラスの意味の保持を意識した関連手法。観測特徴を条件に生成する自分の方法との違いを比較する。'],
 ['4　Zhao & Udell','Gaussian copulaを用いて連続・順序・Booleanの混合データをモデル化し、欠損を補完する。特徴間の依存を利用した条件付き推定の参考になる。欠損補完の成果を、そのまま分類用データ拡張の効果とはみなさない。'],
 ['5　Aas et al.','特徴が依存する場合のShapley値近似を扱い、条件付き分布を用いて依存を考慮する。特徴を独立に扱うことで不自然な組合せが生じる問題と、Gaussian copulaによる条件付きサンプリングの参考になる。説明手法の論文であり、拡張による分類性能向上の直接の証拠ではない。'],
 ['生成AI利用の付記','文献候補の選定、書誌情報の整理、研究との関連の文章化、Excelファイルの作成にOpenAIのCodexを利用した。CodexがNeurIPS公式掲載ページ、arXiv、KDD公式採択ページおよび著者公開の掲載版PDFを参照し、各文献の題名・著者・発表情報と実在を確認した。本文の精読や、提出者自身による全項目の再確認を行ったとする記述は含めていない。'],
 ['実在確認の補足','確認日は2026年10月6日。No.3は参照したarXiv版をプレプリントとして登録した。No.2・4の発表年は会議発表年を採用し、arXiv初稿の年とは区別した。No.4の公式採択確認先：https://www.kdd.org/kdd2020/accepted-papers/view/missing-value-imputation-for-mixed-data-via-gaussian-copula.html'],
 ['課題条件の確認範囲','第1回の講義スライドに記載された「文献5本」「Excelまたは文献管理ツールの画面ショット」「生成AI利用時の実在確認と付記」に基づいて作成。別テキストp.11の詳細条件は未確認。提出前に照合する。'],
 ['提出期限','2026年10月9日（金）の次回授業開始時刻まで。提出先：青学Moodleの第1回授業「課題1」。']
];
n.getRange('A1:B13').values=notes;
n.getRange('A1:B13').format.font={name:'Arial',size:11,color:'#243247'};
n.getRange('A1:B13').format.wrapText=true;
n.getRange('A1:B13').format.verticalAlignment='top';
n.getRange('A1:A13').format.columnWidth=25;
n.getRange('B1:B13').format.columnWidth=108;
n.getRange('A1:B13').format.rowHeight=78;
n.getRange('A1:B1').format.rowHeight=28;
n.getRange('A1').format.font={name:'Arial',size:15,bold:true,color:'#243B53'};
n.getRange('A2:B3').format.rowHeight=44;
n.getRange('A3:B3').format.fill='#FFF2CC';
n.getRange('A4:B4').format.rowHeight=27;
n.getRange('A4:B4').format.fill='#243B53';
n.getRange('A4:B4').format.font={name:'Arial',size:11,bold:true,color:'#FFFFFF'};
n.getRange('A10:B10').format.rowHeight=112;
n.getRange('A11:B11').format.rowHeight=95;
n.getRange('A13:B13').format.rowHeight=44;
n.showGridLines=false;
wb.recalculate();
console.log((await wb.inspect({kind:'table',range:'文献一覧!A1:G6',tableMaxRows:6,tableMaxCols:7,maxChars:2200})).ndjson);
console.log((await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!',options:{useRegex:true,maxResults:20},maxChars:1000})).ndjson);
await fs.mkdir(out,{recursive:true});
await (await SpreadsheetFile.exportXlsx(wb)).save(`${out}/課題1_研究関連文献5本.xlsx`);
for(const [sheetName,range,file] of [['文献一覧','A1:I6','literature.png'],['研究との関連・付記','A1:B13','notes.png']]){
 const p=await wb.render({sheetName,range,scale:1,format:'png'});
 await fs.writeFile(`/Users/kouta/Github/data augumation/Data-Augumation/tmp/academic_literature/${file}`,new Uint8Array(await p.arrayBuffer()));
}
console.log('EXPORT_OK');
