"""仅凭归档中的最终源码和冻结表，离线核验或恢复图1—6。

不读取项目根、原始工作簿、其他run、实验ENV或LLM接口。
几何比较不采用坐标容差：SVG只忽略metadata和结构缩进，PDF只忽略
文档元数据及不影响字形的字体子集前缀；文字位置和绘图路径精确比较。
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from typing import Any
import xml.etree.ElementTree as ET


OUT = Path(__file__).resolve().parents[1]
ARCHIVE = OUT.parent
FIGURES = [
    ('figure_01_framework', (180, 66)),
    ('figure_02_observed_trends', (180, 52)),
    ('figure_03_observed_platforms', (180, 52)),
    ('figure_04_simulated_trajectories', (180, 52)),
    ('figure_05_feedback_exposure', (180, 54)),
    ('figure_06_bdr_ablation', (180, 84)),
]
DATA_FILES = [
    'ablation_metrics.csv', 'ablation_source_index.json', 'feedback_runs.csv',
    'main_runs.csv', 'observed_sources.json', 'observed_total.csv',
    'observed_weekly.csv', 'official_manifest.json', 'official_provenance.json',
    'official_run_metrics.csv', 'official_weekly.csv', 'provenance.json',
    'weekly_supply.csv',
]
SCRIPT_FILES = [f'gen_fig{number}.py' for number in range(1, 7)] + [
    'paper_plot_style.py', 'audit_panel_alignment.py',
]
FITZ: Any = None


class ArchiveError(RuntimeError):
    def __init__(self, message: str, details: Any = None):
        super().__init__(message)
        self.details = details


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_report(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2,
                               allow_nan=False) + '\n', encoding='utf-8')


def verify_manifest() -> dict[str, Any]:
    """归档清单保持相对路径，拒绝越出归档的记录。"""
    path = ARCHIVE / 'recovery/final_assets.json'
    manifest = json.loads(path.read_text(encoding='utf-8'))
    files = manifest.get('files')
    if not isinstance(files, list) or not files:
        raise ArchiveError('归档清单缺少files列表')
    errors = []
    seen = set()
    for item in files:
        name = item.get('path', '')
        relative = Path(name)
        if not name or relative.is_absolute() or '..' in relative.parts or name in seen:
            errors.append({'path': name, 'error': '非法或重复的相对路径'})
            continue
        seen.add(name)
        target = ARCHIVE / relative
        if not target.resolve().is_relative_to(ARCHIVE.resolve()):
            errors.append({'path': name, 'error': '路径越出归档目录'})
            continue
        if not target.is_file():
            errors.append({'path': name, 'error': '文件缺失'})
            continue
        actual_bytes = target.stat().st_size
        actual_sha = digest(target)
        if actual_bytes != item.get('bytes') or actual_sha != item.get('sha256'):
            errors.append({'path': name, 'error': '清单字节数或SHA256不匹配',
                           'expected_bytes': item.get('bytes'), 'actual_bytes': actual_bytes,
                           'expected_sha256': item.get('sha256'), 'actual_sha256': actual_sha})
    if errors:
        raise ArchiveError('归档文件完整性核验失败', errors)
    return {'passed': True, 'files': len(files), 'manifest_sha256': digest(path)}


def svg_length_mm(value: str) -> float:
    match = re.fullmatch(r'([+-]?(?:\d+(?:\.\d*)?|\.\d+))(pt|mm|cm|in|px)?', value)
    if match is None:
        raise ArchiveError('无法解析SVG物理尺寸', value)
    number, unit = match.groups()
    return float(number) * {'pt': 25.4 / 72, 'mm': 1, 'cm': 10,
                           'in': 25.4, 'px': 25.4 / 96, None: 25.4 / 96}[unit]


def verify_figures(directory: Path) -> list[dict[str, Any]]:
    """最终单图须为原生矢量，实际PDF文字不低于8pt。"""
    records = []
    for stem, expected_mm in FIGURES:
        svg_path = directory / f'{stem}.svg'
        svg = ET.parse(svg_path).getroot()
        if any(node.tag.rsplit('}', 1)[-1] == 'image' for node in svg.iter()):
            raise ArchiveError(f'{stem}的SVG包含位图')
        if not any(node.tag.rsplit('}', 1)[-1] == 'text' for node in svg.iter()):
            raise ArchiveError(f'{stem}的SVG缺少可编辑文字')
        svg_mm = [svg_length_mm(svg.attrib[key]) for key in ('width', 'height')]
        if any(abs(actual - expected) > 0.0001 for actual, expected in zip(svg_mm, expected_mm)):
            raise ArchiveError(f'{stem}的SVG物理尺寸不符',
                               {'expected_mm': expected_mm, 'actual_mm': svg_mm})
        pdf_path = directory / f'{stem}.pdf'
        with FITZ.open(pdf_path) as document:
            if len(document) != 1:
                raise ArchiveError(f'{stem}的PDF不是单页')
            page = document[0]
            text = page.get_text('dict')
            if page.get_images(full=True) or any(block['type'] == 1 for block in text['blocks']):
                raise ArchiveError(f'{stem}的PDF包含位图')
            size_mm = [page.rect.width * 25.4 / 72, page.rect.height * 25.4 / 72]
            if any(abs(actual - expected) > 0.0001 for actual, expected in zip(size_mm, expected_mm)):
                raise ArchiveError(f'{stem}的PDF物理尺寸不符',
                                   {'expected_mm': expected_mm, 'actual_mm': size_mm})
            spans = [span for block in text['blocks'] if block['type'] == 0
                     for line in block['lines'] for span in line['spans']
                     if span['text'].strip()]
            if not spans:
                raise ArchiveError(f'{stem}的PDF缺少原生文字')
            minimum = min(span['size'] for span in spans)
            if minimum < 8 - 0.00001:
                raise ArchiveError(f'{stem}有低于8pt的文字', {'minimum_pt': minimum})
            outside = [span['text'] for span in spans
                       if not page.rect.contains(FITZ.Rect(span['bbox']))]
            if outside:
                raise ArchiveError(f'{stem}有画幅外文字', outside)
            records.append({'figure': stem, 'passed': True,
                            'size_mm': list(expected_mm), 'pdf_min_font_pt': minimum,
                            'svg_sha256': digest(svg_path), 'pdf_sha256': digest(pdf_path),
                            'png_sha256': digest(directory / f'{stem}.png')})
    return records


def canonical_svg(path: Path) -> Any:
    """只去掉metadata与非文字区域的缩进；不改任何几何值或文字。"""
    root = ET.parse(path).getroot()

    def whitespace(value: str | None, in_text: bool) -> str | None:
        if in_text or value is None or value.strip():
            return value
        return None

    def element(node: ET.Element, parent_text: bool = False) -> Any:
        name = node.tag.rsplit('}', 1)[-1]
        if name == 'metadata':
            return None
        in_text = parent_text or name in {'text', 'tspan', 'textPath'}
        return {
            'tag': node.tag,
            'attributes': dict(sorted(node.attrib.items())),
            'text': whitespace(node.text, in_text),
            'children': [child for child in (element(item, in_text) for item in node)
                         if child is not None],
            'tail': whitespace(node.tail, parent_text),
        }

    return element(root)


def normalize_pdf(value: Any, key: str | None = None) -> Any:
    """保留所有数值与绘制顺序，不对坐标取整或设置几何容差。"""
    if isinstance(value, (FITZ.Point, FITZ.Rect, FITZ.Quad)):
        return {'kind': type(value).__name__,
                'values': [normalize_pdf(item) for item in value]}
    if isinstance(value, dict):
        return {str(name): normalize_pdf(item, str(name)) for name, item in sorted(value.items())}
    if isinstance(value, (tuple, list)):
        return [normalize_pdf(item) for item in value]
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ArchiveError('PDF几何含非有限数值')
        return 0.0 if value == 0 else value
    if isinstance(value, str) and key == 'font':
        return re.sub(r'^[A-Z]{6}\+', '', value)
    return value


def pdf_geometry(path: Path) -> Any:
    with FITZ.open(path) as document:
        return [normalize_pdf({'page_rect': page.rect,
                               'text': page.get_text('rawdict'),
                               'drawings': page.get_drawings()})
                for page in document]


def first_difference(expected: Any, actual: Any, location: str = '$') -> dict[str, Any] | None:
    if type(expected) is not type(actual):
        return {'location': location, 'expected_type': type(expected).__name__,
                'actual_type': type(actual).__name__}
    if isinstance(expected, dict):
        if set(expected) != set(actual):
            return {'location': location, 'expected_keys': sorted(expected), 'actual_keys': sorted(actual)}
        for key in sorted(expected):
            difference = first_difference(expected[key], actual[key], f'{location}.{key}')
            if difference:
                return difference
    elif isinstance(expected, list):
        if len(expected) != len(actual):
            return {'location': location, 'expected_length': len(expected), 'actual_length': len(actual)}
        for index, (first, second) in enumerate(zip(expected, actual)):
            difference = first_difference(first, second, f'{location}[{index}]')
            if difference:
                return difference
    elif expected != actual:
        return {'location': location, 'expected': str(expected)[:500], 'actual': str(actual)[:500]}
    return None


def compare_figure(stem: str, restored: Path) -> dict[str, Any]:
    comparisons = {}
    for kind, expected, actual in [
        ('svg_xml_without_metadata', canonical_svg(OUT / f'{stem}.svg'),
         canonical_svg(restored / f'{stem}.svg')),
        ('pdf_text_and_vector_geometry', pdf_geometry(OUT / f'{stem}.pdf'),
         pdf_geometry(restored / f'{stem}.pdf')),
    ]:
        difference = first_difference(expected, actual)
        comparisons[kind] = {'passed': difference is None}
        if difference:
            comparisons[kind]['first_difference'] = difference
    expected_png = OUT / f'{stem}.png'
    actual_png = restored / f'{stem}.png'
    comparisons['png_exact_bytes'] = {
        'passed': expected_png.read_bytes() == actual_png.read_bytes(),
        'expected_sha256': digest(expected_png), 'actual_sha256': digest(actual_png),
        'expected_bytes': expected_png.stat().st_size, 'actual_bytes': actual_png.stat().st_size,
    }
    return {'figure': stem, 'passed': all(item['passed'] for item in comparisons.values()),
            'comparisons': comparisons}


def check_output_directory(path: Path) -> None:
    if path.is_symlink():
        raise ArchiveError('输出目录不能是符号链接', str(path))
    if path.exists() and (not path.is_dir() or any(path.iterdir())):
        raise ArchiveError('拒绝覆盖非空输出目录', str(path))


def rebuild(destination: Path, report: dict[str, Any]) -> None:
    """恢复包只带最终绘图源码和冻结表，不带旧图或外部准备入口。"""
    for subdirectory in ('scripts', 'source_data', 'qa/framework_utility'):
        (destination / subdirectory).mkdir(parents=True, exist_ok=True)
    for name in SCRIPT_FILES:
        shutil.copy2(OUT / 'scripts' / name, destination / 'scripts' / name)
    for name in DATA_FILES:
        shutil.copy2(OUT / 'source_data' / name, destination / 'source_data' / name)
    environment = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
    report['generation'] = []
    for number in range(1, 7):
        result = subprocess.run(
            [sys.executable, str(destination / 'scripts' / f'gen_fig{number}.py')],
            cwd=destination, env=environment, capture_output=True, text=True, timeout=60)
        record = {'figure': number, 'exit_code': result.returncode,
                  'stdout': result.stdout.strip(), 'stderr': result.stderr.strip()}
        report['generation'].append(record)
        if result.returncode:
            raise ArchiveError(f'图{number}离线重绘失败', record)
    report['restored_figure_audits'] = verify_figures(destination)
    report['comparisons'] = [compare_figure(stem, destination) for stem, _ in FIGURES]
    if not all(item['passed'] for item in report['comparisons']):
        raise ArchiveError('重绘图件与归档最终版存在差异',
                           [item for item in report['comparisons'] if not item['passed']])
    combined = destination / 'all_figures_1_to_6.pdf'
    document = FITZ.open()
    for stem, _ in FIGURES:
        with FITZ.open(destination / f'{stem}.pdf') as source:
            document.insert_pdf(source)
    document.save(combined)
    document.close()
    difference = first_difference(pdf_geometry(OUT / combined.name), pdf_geometry(combined))
    report['combined_pdf'] = {'passed': difference is None, 'pages': len(FIGURES),
                              'sha256': digest(combined)}
    if difference:
        report['combined_pdf']['first_difference'] = difference
        raise ArchiveError('六页合集的文字或矢量几何有差异', difference)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--verify-only', action='store_true', help='只核验归档清单与六图')
    mode.add_argument('--output', type=Path, help='在新的空目录中离线恢复并精确比对')
    parser.add_argument('--pymupdf-path', type=Path, help='可选的现有PyMuPDF安装目录')
    arguments = parser.parse_args()
    report: dict[str, Any] = {'passed': False, 'mode': 'verify' if arguments.verify_only else 'restore',
                              'network_calls': 0, 'simulation_calls': 0,
                              'geometry_tolerance': 0}
    report_path = OUT / 'qa/archive_verify.json' if arguments.verify_only else None
    try:
        destination = None
        if arguments.output is not None:
            requested = arguments.output.expanduser().absolute()
            check_output_directory(requested)
            destination = requested.resolve()
        if arguments.pymupdf_path is not None:
            sys.path.insert(0, str(arguments.pymupdf_path.expanduser().resolve()))
        global FITZ
        import fitz
        FITZ = fitz
        report['manifest'] = verify_manifest()
        report['source_figure_audits'] = verify_figures(OUT)
        if destination is not None:
            # 重新确认，避免在核验来源期间写入已被他人占用的目录。
            check_output_directory(destination)
            destination.mkdir(parents=True, exist_ok=True)
            report_path = destination / 'qa/archive_restore.json'
            rebuild(destination, report)
        report['passed'] = True
    except Exception as error:
        report['error'] = {'type': type(error).__name__, 'message': str(error)}
        if isinstance(error, ArchiveError) and error.details is not None:
            report['error']['details'] = error.details
    if report_path is not None:
        try:
            write_report(report_path, report)
        except Exception as error:
            report['passed'] = False
            report['report_write_error'] = str(error)
    summary = {'passed': report['passed'], 'mode': report['mode'],
               'figures': len(report.get('source_figure_audits', [])),
               'report': str(report_path) if report_path else None}
    if not report['passed']:
        summary['error'] = report.get('error') or report.get('report_write_error')
    print(json.dumps(summary, ensure_ascii=False, allow_nan=False))
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
