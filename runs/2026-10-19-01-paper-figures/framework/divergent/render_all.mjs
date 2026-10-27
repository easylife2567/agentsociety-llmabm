// 原生SVG的PNG预览、构图拼版与灰度校样。
import {createRequire} from 'node:module';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
const require=createRequire(import.meta.url);
const sharp=require('/Users/easylife/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp');
const dir=path.dirname(fileURLToPath(import.meta.url));
const variants=[['editorial','A  Editorial research map'],['orbit','B  Circular mechanism · refined scientific palette'],['ribbon','C  Flowing research streams']];
const comp=[];
for(let i=0;i<variants.length;i++){
 const [name,label]=variants[i];
 const png=path.join(dir,name+'.png');
 await sharp(path.join(dir,name+'.svg'),{density:339}).resize(2400,850).withMetadata({density:339}).png().toFile(png);
 const thumb=await sharp(png).resize(1200,425).png().toBuffer();
 const title=Buffer.from(`<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="46"><rect width="1200" height="46" fill="white"/><text x="13" y="32" font-family="Arial" font-size="24" font-weight="bold" fill="#17212B">${label}</text></svg>`);
 comp.push({input:title,left:0,top:i*485},{input:thumb,left:0,top:i*485+46});
 const {data,info}=await sharp(png).removeAlpha().raw().toBuffer({resolveWithObject:true});
 let color=0;
 for(let j=0;j<data.length;j+=info.channels){if(Math.max(data[j],data[j+1],data[j+2])-Math.min(data[j],data[j+1],data[j+2])>30)color++;}
 process.stdout.write(`${name}: colored pixel fraction ${(100*color/(info.width*info.height)).toFixed(2)}% (RGB span >30)\n`);
}
await sharp({create:{width:1200,height:1455,channels:3,background:'white'}}).composite(comp).png().toFile(path.join(dir,'comparison.png'));
await sharp(path.join(dir,'comparison.png')).grayscale().png().toFile(path.join(dir,'comparison_grayscale.png'));
await sharp(path.join(dir,'orbit.png')).grayscale().withMetadata({density:339}).png().toFile(path.join(dir,'orbit_grayscale.png'));
