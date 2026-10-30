"""从匹配V7的既有SVG选择性更新回流说明与主实验规模，保留其他图形。"""
import hashlib
import json
from pathlib import Path
import subprocess
from xml.etree import ElementTree as ET

from PIL import Image
import numpy as np

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
SOURCE=ROOT/'runs/2026-10-19-01-paper-figures/framework/fusion/v2/framework_fusion_en_v2.svg'
SOURCE_PNG=SOURCE.with_suffix('.png')
DOCX_IMAGE=HERE.parent/'qa/image1.png'
NODE='/Users/easylife/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node'
SHARP='/Users/easylife/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp'


def sha(data):return hashlib.sha256(data).hexdigest()


def geometry(data):
    namespace='{http://www.w3.org/2000/svg}'
    return [(e.tag,sorted(e.attrib.items()),None if e.tag in {namespace+'text',namespace+'tspan'} else e.text,e.tail)
            for e in ET.fromstring(data).iter()]


def main():
    original=SOURCE.read_bytes()
    (HERE/'source_figure1.svg').write_bytes(original)
    pairs=[('Chronological: after batch; visible later','All regimes: pooled after the hour batch'),
           ('Random / Interest: eligible next week','Eligible from later action batches'),
           ('3 regimes × 3 seeds  ·  Interest-based interventions: B=0 / D=1 / R=1',
            'Main: 3 regimes × 10 seeds · B/D/R examples: legacy return')]
    edited=original
    for before,after in pairs:
        assert edited.count(before.encode())==1,before
        edited=edited.replace(before.encode(),after.encode())
    reverse=edited
    for before,after in pairs:reverse=reverse.replace(after.encode(),before.encode())
    assert reverse==original and geometry(original)==geometry(edited)
    svg=HERE/'figure1_hourly.svg';png=HERE/'figure1_hourly.png'
    svg.write_bytes(edited)
    width,height=4252,1671
    script="""const sharp=require(process.argv[1]);
(async()=>{
 await sharp(process.argv[2],{density:208}).flatten({background:'#ffffff'})
 .resize({width:4252,height:1671,fit:'contain',background:'#ffffff'})
 .withMetadata({density:600}).png().toFile(process.argv[3]);
 process.stdout.write(JSON.stringify(await sharp(process.argv[3]).metadata())+'\\n');
})().catch(e=>{process.stderr.write(String(e));process.exit(1);});
"""
    result=subprocess.run([NODE,'-e',script,SHARP,str(svg),str(png)],check=True,capture_output=True,text=True)
    meta=json.loads(result.stdout)
    assert (meta['width'],meta['height'],meta['density'])==(width,height,600)
    a=Image.open(DOCX_IMAGE).convert('RGB')
    b=Image.open(SOURCE_PNG).convert('RGB').resize(a.size,Image.Resampling.LANCZOS)
    difference=np.asarray(a,dtype=float)-np.asarray(b,dtype=float)
    report=dict(status='passed',source_svg=str(SOURCE),source_svg_sha256=sha(original),
        source_matching_png=str(SOURCE_PNG),source_matching_png_sha256=sha(SOURCE_PNG.read_bytes()),
        source_v7_image_sha256=sha(DOCX_IMAGE.read_bytes()),
        source_raster_match_mean_absolute_channel_error=float(np.abs(difference).mean()),
        source_raster_match_rmse=float(np.sqrt(np.mean(difference**2))),
        exact_text_replacements=[dict(before=a,after=b)for a,b in pairs],
        all_other_svg_bytes_unchanged=True,non_text_geometry_styles_numerals_and_icons_unchanged=True,
        non_text_fingerprint_sha256=sha(json.dumps(geometry(original),ensure_ascii=False).encode()),
        final_svg_sha256=sha(edited),final_png_sha256=sha(png.read_bytes()),png_size=[width,height],dpi=600,
        renderer='bundled sharp/libvips, vector rendering with contain fit',renderer_log=result.stderr,
        new_source_script_sha256=sha(Path(__file__).read_bytes()),dirty_drawio_read_or_modified=False,
        note='Only the two recirculation text lines and the main-size/legacy-example line changed; no new empirical data or mechanism geometry invented.')
    (HERE/'framework_update_validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report,ensure_ascii=False))


if __name__=='__main__':main()
