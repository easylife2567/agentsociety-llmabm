"""生成四图预览、矢量图册、LaTeX片段及不含原图5的交付包。"""
from pathlib import Path
import argparse,hashlib,json,re,sys,zipfile
from PIL import Image,ImageDraw,ImageFont,ImageOps
from validate_delivery import STEMS

OUT=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--pymupdf-path',type=Path)
 args=parser.parse_args()
 if args.pymupdf_path:sys.path.insert(0,str(args.pymupdf_path))
 import fitz
 book=fitz.open()
 for stem in STEMS:
  with fitz.open(OUT/f'{stem}.pdf') as doc:book.insert_pdf(doc)
 book.save(OUT/'all_figures.pdf');book.close()
 tiles=[];font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',29)
 for i,stem in enumerate(STEMS,1):
  im=Image.open(OUT/f'{stem}.png').convert('RGB');im.thumbnail((1120,1100),Image.Resampling.LANCZOS)
  tile=Image.new('RGB',(1200,im.height+86),'white')
  ImageDraw.Draw(tile).text((40,17),f'Figure {i}',font=font,fill='#17212B')
  tile.paste(im,((1200-im.width)//2,66));tiles.append(tile)
 rowh=[max(t.height for t in tiles[:2]),max(t.height for t in tiles[2:])]
 sheet=Image.new('RGB',(2400,sum(rowh)+20),'#E8EDF1')
 for i,tile in enumerate(tiles):
  row=i//2;cell=Image.new('RGB',(1200,rowh[row]),'white');cell.paste(tile,(0,0))
  sheet.paste(cell,((i%2)*1200,0 if not row else rowh[0]+20))
 sheet.save(OUT/'all_figures_preview.png')
 ImageOps.grayscale(sheet).save(OUT/'qa/all_figures_grayscale.png')
 caption=(OUT/'CAPTIONS_ZH.md').read_text();tex=[]
 for i,stem in enumerate(STEMS,1):
  paragraph=caption.split(f'## 图{i}\n',1)[1].split('\n## ',1)[0].strip().replace('**','')
  paragraph=re.sub(rf'^图{i}\s*','',paragraph).replace('%',r'\%')
  tex.append('% 中文图注需要支持中文的LaTeX文档。\n'+
    '\\begin{figure*}[t]\n\\centering\n'+
    f'\\includegraphics[width=\\textwidth]{{{stem}.pdf}}\n'+
    f'\\caption{{{paragraph}}}\n\\label{{fig:seed10-{i}}}\n\\end{{figure*}}\n')
 (OUT/'latex_includes.tex').write_text('\n'.join(tex))
 manifest=json.loads((OUT.parent/'inputs/ICA2027-V5.manifest.json').read_text())
 assert sha(manifest['source'])==manifest['sha256']
 assert sha(OUT.parent/'inputs/ICA2027-V5.docx')==manifest['sha256']
 members=[OUT/f'{s}.{e}' for s in STEMS for e in ('svg','pdf','png')]
 members += [OUT/n for n in ('CAPTIONS_ZH.md','REVISION_ADVICE.md','latex_includes.tex','all_figures.pdf','all_figures_preview.png')]
 members += list((OUT/'scripts').glob('*.py'))+list((OUT/'source_data').glob('*.csv'))+list((OUT/'source_data').glob('*.json'))
 members += [OUT/'qa/delivery_checks.json',OUT/'qa/REVIEW.md']
 members += list((OUT/'qa').glob('*.build.json'))
 members += [OUT/'source_data/README.md',OUT/'scripts/README.md']
 assert not any('figure_05' in str(p) or 'deferred_ablation' in str(p) for p in members)
 archive=OUT/'figures_seed10_delivery.zip'
 with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED) as z:
  z.writestr('README.md','# ICA2027四图交付：十组主实验\n\n图1、2为现实内容分析；图3、4为每制度10个种子的30次主运行。原图5按用户决定不纳入本包。SVG文字和路径可编辑，PDF同为矢量，PNG只作预览。插入Word请锁定纵横比。\n\nCAPTIONS_ZH.md为四段中文图注；REVISION_ADVICE.md为正文数字与论证修改意见。其涉及旧稿/延后资料的链接只在原run完整目录可用，本包不包含原Word与旧图5。\n\nsource_data保存冻结CSV与来源；scripts/gen_fig1.py—gen_fig4.py按顺序离线重绘，依赖Python、Matplotlib、Pandas、NumPy、Pillow和Times New Roman（缺失时使用字体fallback）。无需重跑仿真。qa保存数据与图件检查。\n')
  for path in members:z.write(path,path.relative_to(OUT))
 check={'date':'2026-10-24','primary_figures':[1,2,3,4],'excluded_figure':5,
  'word_original_unchanged':True,'word_sha256':manifest['sha256'],
  'zip_file':archive.name,'zip_sha256':sha(archive),
  'files':{str(p.relative_to(OUT)):sha(p) for p in members},
  'note':'ZIP压缩仅减小文件字节数，不栅格化或拉伸SVG。'}
 (OUT/'qa/package_checks.json').write_text(json.dumps(check,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'zip':str(archive),'members':len(members)+1,'bytes':archive.stat().st_size,'word_unchanged':True},ensure_ascii=False))

if __name__=='__main__':main()
