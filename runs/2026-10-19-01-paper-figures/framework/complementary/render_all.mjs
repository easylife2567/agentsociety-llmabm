// 三种原生SVG的PNG预览与黑白校样；使用本机Codex捆绑的sharp。
import {createRequire} from 'node:module';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
const require=createRequire(import.meta.url);
const sharp=require('/Users/easylife/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp');
const dir=path.dirname(fileURLToPath(import.meta.url));
const variants=[['a_linked','A  Linked studies · 30:70'],['b_bands','B  Parallel research bands · 40:60'],['c_loop','C  Mechanism circuit · 35:65']];
const composites=[];
for(let i=0;i<variants.length;i++){
 const [name,label]=variants[i];
 await sharp(path.join(dir,name+'.svg'),{density:339}).resize(2400,850).withMetadata({density:339}).png().toFile(path.join(dir,name+'.png'));
 const thumb=await sharp(path.join(dir,name+'.png')).resize(1200,425).png().toBuffer();
 const title=Buffer.from(`<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="46"><rect width="1200" height="46" fill="white"/><text x="13" y="32" font-family="Arial" font-size="24" font-weight="bold" fill="#111827">${label}</text></svg>`);
 composites.push({input:title,left:0,top:i*485},{input:thumb,left:0,top:i*485+46});
}
await sharp({create:{width:1200,height:1455,channels:3,background:'white'}}).composite(composites).png().toFile(path.join(dir,'comparison.png'));
await sharp(path.join(dir,'comparison.png')).grayscale().png().toFile(path.join(dir,'comparison_grayscale.png'));
process.stdout.write('Rendered 3 previews and 2 comparison proofs.\n');
