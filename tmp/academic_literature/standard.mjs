import fs from 'node:fs/promises';
import {FileBlob,Workbook,SpreadsheetFile} from '@oai/artifact-tool';
const base='/Users/kouta/Github/data augumation/Data-Augumation';
const source=await SpreadsheetFile.importXlsx(await FileBlob.load(`${base}/outputs/academic_seminar_20261006/課題1_研究関連文献5本.xlsx`));
const wb=Workbook.create();
for(const [name,range] of [['文献一覧','A1:I6'],['研究との関連・付記','A1:B13']]){
 const values=source.worksheets.getItem(name).getRange(range).values;
 const sheet=wb.worksheets.add(name);
 sheet.getRange(range).values=values;
 sheet.showGridLines=true;
 if(name==='文献一覧')sheet.getRange('I2:I6').setNumberFormat('m/d/yy');
 if(JSON.stringify(sheet.getRange(range).values)!==JSON.stringify(values))throw Error('Content mismatch');
}
wb.recalculate();
for(const [name,range,file] of [['文献一覧','A1:I6','standard_literature.png'],['研究との関連・付記','A1:D13','standard_notes.png']]){
 const p=await wb.render({sheetName:name,range,scale:2,format:'png'});
 await fs.writeFile(`${base}/tmp/academic_literature/${file}`,new Uint8Array(await p.arrayBuffer()));
}
await (await SpreadsheetFile.exportXlsx(wb)).save(`${base}/outputs/academic_seminar_20261006/課題1_研究関連文献5本_標準.xlsx`);
console.log('Verified all cell values unchanged; exported default-format workbook.');
