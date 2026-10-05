import fs from 'node:fs/promises';
import {FileBlob,PresentationFile} from '@oai/artifact-tool';
const p=await PresentationFile.importPptx(await FileBlob.load('/Users/kouta/Github/data augumation/Data-Augumation/output/presentations/身長の位置0.65_条件付き生成の具体例_1枚.pptx'));
console.log((await p.inspect({kind:"slide,layout",maxChars:1000})).ndjson);
const b=await p.export({slide:p.slides.items[0],format:'png',scale:1});await fs.writeFile('/Users/kouta/Github/data augumation/Data-Augumation/tmp/copula_position_slide/checked.png',new Uint8Array(await b.arrayBuffer()));
