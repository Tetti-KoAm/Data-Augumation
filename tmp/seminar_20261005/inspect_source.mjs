import fs from 'node:fs/promises';
import {FileBlob,PresentationFile} from '@oai/artifact-tool';
const p=await PresentationFile.importPptx(await FileBlob.load('/Users/kouta/Library/CloudStorage/OneDrive-個人用/大学院/研究/10.05＿齊藤光汰.pptx'));
await fs.writeFile('tmp/seminar_20261005/source_inspect.txt',(await p.inspect({kind:'slide,layout',maxChars:12000})).ndjson);
console.log('slides',p.slides.items.length,'masters',p.masters.items.length);
for(let i=0;i<p.slides.items.length;i++){
 const b=await p.export({slide:p.slides.items[i],format:'png',scale:1});
 await fs.writeFile(`tmp/seminar_20261005/source-${i+1}.png`,new Uint8Array(await b.arrayBuffer()));
}
