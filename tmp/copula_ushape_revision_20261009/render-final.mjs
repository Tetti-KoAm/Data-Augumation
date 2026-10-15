import fs from 'node:fs/promises';
import {FileBlob,PresentationFile} from '@oai/artifact-tool';
const dir='/Users/kouta/Github/data augumation/Data-Augumation/tmp/copula_ushape_revision_20261009';
const p=await PresentationFile.importPptx(await FileBlob.load('/Users/kouta/Github/data augumation/Data-Augumation/output/presentations/コピュラ解説_非単調データ版_本編20枚_補足9枚_改訂.pptx'));
await p.inspect({kind:'slide,layout',maxChars:1000});
for(let i=0;i<p.slides.items.length;i++){const b=await p.export({slide:p.slides.items[i],format:'png',scale:1});await fs.writeFile(`${dir}/checked-${i+1}.png`,new Uint8Array(await b.arrayBuffer()));}console.log('rendered',p.slides.items.length);
