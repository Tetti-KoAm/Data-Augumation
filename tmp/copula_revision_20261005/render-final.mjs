import fs from 'node:fs/promises';
import {FileBlob,PresentationFile} from '@oai/artifact-tool';
const p=await PresentationFile.importPptx(await FileBlob.load('/Users/kouta/Github/data augumation/Data-Augumation/output/presentations/10.05_ゼミ発表_コピュラ解説改訂版_本編20枚_補足6枚_v2.pptx'));
await fs.writeFile('tmp/copula_revision_20261005/checked_inspect.txt',(await p.inspect({kind:'slide,layout',maxChars:12000})).ndjson);
console.log('slides',p.slides.items.length,'masters',p.masters.items.length);
for(let i=0;i<p.slides.items.length;i++){
 const b=await p.export({slide:p.slides.items[i],format:'png',scale:1});
 await fs.writeFile(`tmp/copula_revision_20261005/checked-${i+1}.png`,new Uint8Array(await b.arrayBuffer()));
}
