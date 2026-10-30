"""核验真实总量、小时主实验、原批消融及矢量图件的交付边界。"""
from pathlib import Path
import argparse
import hashlib
import json
import re
import sys
import xml.etree.ElementTree as ET

import numpy as np
import pandas as pd

OUT = Path(__file__).resolve().parents[1]
ROOT = OUT.parents[2]
DATA = OUT / 'source_data'
QA = OUT / 'qa'
STEMS = ['figure_02_observed_trends', 'figure_03_observed_platforms',
         'figure_04_simulated_trajectories', 'figure_05_feedback_exposure',
         'figure_06_bdr_ablation']
ARMS = ['random', 'chronological', 'interest']
CATS = ['education', 'mourning', 'meme', 'other', 'marketing']


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--pymupdf-path')
    args = parser.parse_args()
    if args.pymupdf_path:
        sys.path.insert(0, args.pymupdf_path)
    import fitz
    baseline = json.loads((QA / 'baseline.json').read_text())
    for path, digest in baseline['protected_sha256'].items():
        assert sha(ROOT / path) == digest, ('protected asset changed', path)
    provenance = json.loads((DATA / 'provenance.json').read_text())
    for name, digest in provenance['output_sha256'].items():
        assert sha(DATA / name) == digest, name
    for path, digest in provenance['source_sha256'].items():
        assert sha(ROOT / path) == digest, path
    assert sha(OUT / 'scripts/prepare_data.py') == provenance['preparation_script_sha256']
    assert json.loads((QA / 'data_checks.json').read_text())['passed']

    totals = pd.read_csv(DATA / 'observed_total.csv')
    total = totals[totals.platform.eq('pooled')].set_index('week').total_posts
    assert len(total) == 18 and total.sum() == 49930
    assert total.loc['2026-W13'] == 10674
    assert np.array_equal(totals.query('platform != "pooled"').groupby('week').total_posts.sum(), total)
    observed = pd.read_csv(DATA / 'observed_weekly.csv')
    assert len(observed) == 270 and observed.query('platform == "pooled"')['count'].sum() == 46602
    assert observed.query('platform == "douyin"')['count'].sum() == 15186
    assert observed.query('platform == "xiaohongshu"')['count'].sum() == 31416
    assert np.allclose(observed['share'], observed['count'] / observed.total_five)

    weekly = pd.read_csv(DATA / 'weekly_supply.csv')
    runs = pd.read_csv(DATA / 'main_runs.csv')
    official = pd.read_csv(DATA / 'official_weekly.csv')
    assert len(weekly) == 330 and len(runs) == 30
    assert not weekly.duplicated(['arm', 'seed', 'week']).any()
    assert not runs.duplicated(['arm', 'seed']).any()
    assert all(weekly.groupby(['arm', 'seed']).size() == 11)
    assert all(set(runs.loc[runs.arm.eq(arm), 'seed']) == set(range(10)) for arm in ARMS)
    merged = weekly.merge(official, left_on=['arm', 'seed', 'week'], right_on=['algorithm', 'seed', 'week'], validate='one_to_one')
    for cat in CATS:
        assert np.array_equal(merged[f'agent_supply_{cat}'], merged[f'posted_{cat}_authors'])
    assert np.array_equal(weekly[[f'agent_supply_{cat}' for cat in CATS]].sum(axis=1), weekly.agent_supply)
    assert weekly[[f'agent_supply_{cat}' for cat in CATS]].max().max() < 25
    late = weekly.loc[weekly.week.between('2026-W19', '2026-W22')].groupby(['arm', 'seed'])
    late_sum = late[['agent_supply', 'agent_supply_meme']].sum()
    late_run = runs.set_index(['arm', 'seed']).sort_index()
    assert np.array_equal(late_sum.agent_supply, late_run.late_total_posts)
    assert np.array_equal(late_sum.agent_supply_meme, late_run.late_meme_posts)
    assert np.allclose(late_sum.agent_supply_meme / late_sum.agent_supply, late_run.late_meme_share)
    feedback = pd.read_csv(DATA / 'feedback_runs.csv')
    assert len(feedback) == 30 and not feedback.duplicated(['arm', 'seed']).any()
    for field, numerator, denominator, expected in [
        ('own_share', 'own_numerator', 'own_denominator', 760),
        ('meme_post_rate', 'meme_post_numerator', 'meme_post_denominator', 76),
        ('cross_generated_share', 'cross_generated_numerator', 'cross_generated_denominator', 3240)]:
        assert feedback[denominator].eq(expected).all()
        assert np.allclose(feedback[field], feedback[numerator] / feedback[denominator])
    ablation = pd.read_csv(DATA / 'ablation_metrics.csv')
    assert len(ablation) == 100 and not ablation.duplicated(['panel', 'condition', 'seed']).any()
    assert np.allclose(ablation.value, ablation.numerator / ablation.denominator)
    assert ablation.groupby(['panel', 'condition']).size().eq(10).all()

    result = {'passed': True, 'protected_assets_unchanged': len(baseline['protected_sha256']),
              'observed_total_posts': 49930, 'main_hourly_runs': 30,
              'ablation_pairs_per_comparison': 10, 'figures': {}}
    for number, stem in zip(range(2, 7), STEMS):
        svg = ET.parse(OUT / f'{stem}.svg').getroot()
        ns = {'svg': 'http://www.w3.org/2000/svg'}
        text_nodes = svg.findall('.//svg:text', ns)
        text = '\n'.join(''.join(node.itertext()) for node in text_nodes)
        assert not re.search(r'Fig\.?\s*\.?\s*\d', text)
        assert 'Xiaohongshu' not in text and 'R = 1' not in text
        assert 'no inferential' not in text and 'n = ' not in text
        assert not svg.findall('.//svg:image', ns)
        assert len(text_nodes) >= 20 and svg.get('viewBox') and svg.get('preserveAspectRatio')
        if number in [2, 3, 4]:
            assert 'Official obituary' in text and 'W13' in text
            assert '†' not in text
            star_ids = [node.get('id', '') for node in svg.iter() if node.get('id', '').startswith('event-star-W13-')]
            assert len(star_ids) == (3 if number == 4 else 2)
        if number == 3:
            assert 'Douyin' in text and 'Rednote' in text
        if number == 4:
            assert 'Cumulative successful posts' not in text
            assert '(d)' not in text
            assert all(f'({letter}) {name}' in text for letter, name in zip('abc', ['Random', 'Chronological', 'Interest-based']))
            assert 'Memetic-type supply share' not in text
        if number == 5:
            for metric in ['own_share', 'meme_post_rate', 'cross_generated_share']:
                for mean in feedback.groupby('arm')[metric].mean() * 100:
                    assert f'{mean:.1f}%' in text
        if number == 6:
            assert text.count('R → 1') == 3
            for (panel, _), group in ablation.groupby(['panel', 'condition']):
                mean = group.value.mean() * (1 if panel == 'a' else 100)
                assert f'{mean:.1f}' + ('' if panel == 'a' else '%') in text
        build = json.loads((QA / f'{stem}.build.json').read_text())
        assert not build['outside_canvas'], build['outside_canvas']
        assert min(item['font_pt'] for item in build['rendered_text_boxes']) >= 8
        assert build['size_mm'][0] == 180
        alignment = json.loads((QA / f'{stem}.alignment.json').read_text())
        assert alignment['verdict'] == 'PASS'
        assert build['font'] == 'Arial'
        assert all(abs(m['visible_center_delta_pt']) <= .1 for m in build['event_alignment'])
        for suffix, digest in build['outputs'].items():
            assert sha(OUT / f'{stem}.{suffix}') == digest
        with fitz.open(OUT / f'{stem}.pdf') as doc:
            assert len(doc) == 1 and not doc[0].get_images(full=True)
            page = doc[0]
            spans = [span for block in page.get_text('dict')['blocks'] if block['type'] == 0
                     for line in block['lines'] for span in line['spans'] if span['text'].strip()]
            assert spans and min(span['size'] for span in spans) >= 7.99
            outside = [span['text'] for span in spans if not page.rect.contains(fitz.Rect(span['bbox']))]
            assert not outside, (stem, outside)
            overlaps = []
            for i, first in enumerate(spans):
                for second in spans[i + 1:]:
                    box1, box2 = fitz.Rect(first['bbox']), fitz.Rect(second['bbox'])
                    intersection = box1 & box2
                    if intersection.is_empty:
                        continue
                    if intersection.get_area() / min(box1.get_area(), box2.get_area()) > .2:
                        overlaps.append([first['text'], second['text']])
            assert not overlaps, (stem, overlaps)
            result['figures'][str(number)] = {'stem': stem, 'size_mm': build['size_mm'],
                'svg_text_objects': len(text_nodes), 'pdf_min_font_pt': min(s['size'] for s in spans),
                'pdf_fonts': sorted({s['font'] for s in spans}), 'pdf_text_overlaps': overlaps,
                'vector_svg_pdf': True, 'output_sha256': build['outputs']}
    caption = (OUT / 'CAPTIONS_ZH.md').read_text()
    assert all(f'图{number}：' in caption for number in range(2, 7))
    assert 'R → 1' in caption and 'R=1' not in caption
    (QA / 'delivery_checks.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'passed': True, 'figures': list(result['figures']), 'protected_unchanged': result['protected_assets_unchanged']}))


if __name__ == '__main__':
    main()
