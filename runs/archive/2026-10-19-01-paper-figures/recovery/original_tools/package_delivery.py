"""生成本轮五图的矢量合辑、预览及可复现交付包。"""
from pathlib import Path
import argparse
import hashlib
import json
import sys
import zipfile

from PIL import Image, ImageDraw, ImageFont, ImageOps

OUT = Path(__file__).resolve().parents[1]
STEMS = ['figure_02_observed_trends', 'figure_03_observed_platforms',
         'figure_04_simulated_trajectories', 'figure_05_feedback_exposure',
         'figure_06_bdr_ablation']


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--pymupdf-path')
    args = parser.parse_args()
    if args.pymupdf_path:
        sys.path.insert(0, args.pymupdf_path)
    import fitz
    assert json.loads((OUT / 'qa/delivery_checks.json').read_text())['passed']
    document = fitz.open()
    for stem in STEMS:
        with fitz.open(OUT / f'{stem}.pdf') as source:
            document.insert_pdf(source)
    document.save(OUT / 'all_figures.pdf')
    document.close()
    width = 1200
    gap = 32
    cells = []
    font = ImageFont.truetype('/System/Library/Fonts/Supplemental/Times New Roman.ttf', 28)
    for number, stem in zip(range(2, 7), STEMS):
        original = Image.open(OUT / f'{stem}.png').convert('RGB')
        original.thumbnail((width, 900), Image.Resampling.LANCZOS)
        cell = Image.new('RGB', (width, original.height + 48), 'white')
        ImageDraw.Draw(cell).text((12, 5), f'Figure {number}', font=font, fill='#20262D')
        cell.paste(original, ((width - original.width) // 2, 48))
        cells.append(cell)
    # 总览的图号在单图画布之外；交付的五张图均无左上角Fig标签。
    heights = [max(cells[0].height, cells[1].height), max(cells[2].height, cells[3].height), cells[4].height]
    canvas = Image.new('RGB', (width * 2 + gap, sum(heights) + gap * 2), 'white')
    y = 0
    for row, indices in enumerate([(0, 1), (2, 3), (4,)]):
        for col, index in enumerate(indices):
            x = col * (width + gap) if len(indices) == 2 else (canvas.width - width) // 2
            canvas.paste(cells[index], (x, y))
        y += heights[row] + gap
    canvas.save(OUT / 'all_figures_preview.png')
    ImageOps.grayscale(canvas).save(OUT / 'qa/all_figures_grayscale.png')
    members = [path for path in OUT.rglob('*') if path.is_file()
               and path.suffix != '.zip' and '__pycache__' not in path.parts
               and path.name != 'package_checks.json'
               and 'before' not in path.relative_to(OUT).parts
               and 'candidate' not in path.relative_to(OUT).parts]
    archive = OUT / 'figures_2_to_6_unified_delivery.zip'
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as bundle:
        for path in sorted(members):
            bundle.write(path, path.relative_to(OUT))
    with zipfile.ZipFile(archive) as bundle:
        assert bundle.testzip() is None
        assert len(bundle.namelist()) == len(members)
        for path in members:
            assert bundle.read(str(path.relative_to(OUT))) == path.read_bytes()
    result = {'passed': True, 'members': len(members), 'crc': 'passed',
              'archive': archive.name, 'bytes': archive.stat().st_size,
              'archive_sha256': hashlib.sha256(archive.read_bytes()).hexdigest(),
              'member_sha256': {str(p.relative_to(OUT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(members)}}
    (OUT / 'qa/package_checks.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'passed': True, 'members': len(members), 'archive_bytes': archive.stat().st_size}))


if __name__ == '__main__':
    main()
