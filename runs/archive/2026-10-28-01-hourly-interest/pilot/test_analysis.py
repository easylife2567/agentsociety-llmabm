"""试运行分析器的纯离线口径检查；不用真实实验结果。"""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('pilot_analysis', Path(__file__).with_name('analyze_pilot.py'))
analysis = importlib.util.module_from_spec(spec)
spec.loader.exec_module(analysis)
plot_spec = importlib.util.spec_from_file_location('pilot_plot', Path(__file__).with_name('plot_pilot.py'))
plot = importlib.util.module_from_spec(plot_spec)
plot_spec.loader.exec_module(plot)


class AnalysisTests(unittest.TestCase):
    def test_real_exposure_denominators_and_empty_feed(self):
        rows = [dict(agent_type='meme', feed=[dict(source='agent', type='meme'),
                                             dict(source='external', type='education')]),
                dict(agent_type='education', feed=[dict(source='agent', type='meme')])]
        result = analysis.exposures(rows)
        self.assertEqual(result['feed_total'], 3)
        self.assertEqual(result['feed_agent_total'], 2)
        self.assertEqual(result['feed_meme_tag_share'], 2 / 3)
        self.assertEqual(result['own_meme_tag_share'], .5)
        self.assertEqual(result['cross_generated_meme_share'], 1)
        self.assertIsNone(analysis.exposures([])['feed_meme_tag_share'])
        self.assertIsNone(analysis.exposures([])['feed_agent_meme_tag_share'])

    def test_same_batch_and_delayed_queue_are_rejected(self):
        post = dict(source='agent', type='meme', source_week='2026-W12',
                    available_week='2026-W12', injected_week='2026-W12',
                    published_at='2026-03-16T10:00:00+08:00',
                    available_at='2026-03-16T10:00:00+08:00')
        action = dict(acted_at='2026-03-16T11:00:00+08:00', candidate_future=0, feed=[post])
        env = dict(_arrival_state=dict(actions=[action], delayed=[]), _posts={'1': post})
        self.assertEqual(analysis.audit_recirculation(env)['agent_exposures'], 1)
        action['acted_at'] = post['published_at']
        with self.assertRaisesRegex(ValueError, '小时回流审计'):
            analysis.audit_recirculation(env)
        action['acted_at'] = '2026-03-16T11:00:00+08:00'
        env['_arrival_state']['delayed'] = [post]
        with self.assertRaisesRegex(ValueError, '小时回流审计'):
            analysis.audit_recirculation(env)

    def test_incomplete_batch_never_creates_analysis(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            state = root / 'batch_execution.json'
            state.write_text(json.dumps(dict(status='running')))
            plan = root / 'runtime_plan.json'
            plan.write_text(json.dumps(dict(execution_authorized=True, state_path=str(state))))
            with self.assertRaisesRegex(ValueError, '三臂尚未全部完成'):
                analysis.outputs(plan, root / 'analysis')
            self.assertFalse((root / 'analysis').exists())

    def test_plot_keeps_empty_denominators_and_rejects_filled_zero(self):
        rows = [dict(algorithm=arm, seed='0', week=week, posted_total='0', posted_meme_authors='0',
                     feed_total='0', feed_meme_tag='0', meme_author_share='', feed_meme_tag_share='')
                for arm in plot.ARMS for week in plot.WEEKS]
        summary = dict(status='complete', scope='three-arms-seed0-exploratory-only', late_weeks=list(plot.LATE),
                       runs=[dict(algorithm=arm, total_posts=0, late_meme_posts=0, late_total_posts=0,
                                  late_exposures=dict(feed_total=0, feed_meme_tag=0)) for arm in plot.ARMS])
        self.assertEqual(set(plot.verified_rows(summary, rows)), set(plot.ARMS))
        rows[0]['meme_author_share'] = '0'
        with self.assertRaisesRegex(ValueError, '分母'):
            plot.verified_rows(summary, rows)


    def test_explicit_selection_only_reads_two_completed_arms_and_counts_withdrawn_cost(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            config, steps = root / 'config.json', root / 'steps.yaml'
            config.write_text('{}')
            steps.write_text('steps: []')
            runs = [dict(algorithm=arm, seed=0, run_id=arm, config=str(config), steps=str(steps)) for arm in analysis.ARMS]
            state_path = root / 'batch_execution.json'
            state = dict(status='completed', completed=[dict(run_id=arm) for arm in ('random', 'interest')],
                         excluded_runs=[dict(algorithm='chronological', consumed_requests=30, status='withdrawn')])
            state_path.write_text(json.dumps(state))
            plan_path = root / 'runtime_plan.json'
            plan_path.write_text(json.dumps(dict(execution_authorized=True, state_path=str(state_path),
                workspace=str(root), runs=runs, analysis_contract=dict(late_weeks=list(analysis.LATE)),
                body_outer_requests_limit=3630, requested_model='offline-fixture')))
            selection_path = root / 'selected_revision.json'
            selection = dict(selected_algorithms=['random', 'interest'], excluded_algorithms=['chronological'])
            selection_path.write_text(json.dumps(selection))

            def fixed_result(run, workspace, hashes):
                rows = [dict(algorithm=run['algorithm'], week=week) for week in analysis.WEEKS]
                exp = dict(feed_total=0, feed_agent_total=0, feed_meme_tag_share=None,
                           feed_agent_meme_tag_share=None, own_meme_tag_share=None, cross_generated_meme_share=None)
                metric = dict(algorithm=run['algorithm'], response_model_counts={'offline-fixture': 1},
                    body_outer_requests=5, total_posts=0, late_meme_posts=0, late_total_posts=0,
                    late_meme_share=None, late_exposures=exp)
                return rows, metric

            with patch.object(analysis, 'extract_run', side_effect=fixed_result) as extract:
                result = analysis.outputs(plan_path, root / 'analysis', selection_path)
                self.assertEqual([call.args[0]['algorithm'] for call in extract.call_args_list], ['random', 'interest'])
            summary = json.loads(result[root / 'analysis/summary.json'])
            self.assertEqual(summary['selected_algorithms'], ['random', 'interest'])
            self.assertEqual(summary['total_body_outer_requests'], 40)
            self.assertEqual(summary['excluded_body_outer_requests'], 30)
            self.assertEqual(len(result[root / 'analysis/weekly.csv'].strip().splitlines()), 23)
            state['completed'].append(dict(run_id='chronological'))
            state_path.write_text(json.dumps(state))
            with self.assertRaisesRegex(ValueError, '中止时序'):
                analysis.outputs(plan_path, root / 'analysis', selection_path)

    def test_two_curve_plot_requires_matching_explicit_selection(self):
        arms = ('random', 'interest')
        rows = [dict(algorithm=arm, seed='0', week=week, posted_total='0', posted_meme_authors='0',
                     feed_total='0', feed_meme_tag='0', meme_author_share='', feed_meme_tag_share='')
                for arm in arms for week in plot.WEEKS]
        summary = dict(status='complete', scope='selected-arms-seed0-exploratory-only', late_weeks=list(plot.LATE),
                       selected_algorithms=list(arms), excluded_algorithms=['chronological'],
                       runs=[dict(algorithm=arm, total_posts=0, late_meme_posts=0, late_total_posts=0,
                                  late_exposures=dict(feed_total=0, feed_meme_tag=0)) for arm in arms])
        selection = dict(selected_algorithms=list(arms), excluded_algorithms=['chronological'])
        self.assertEqual(list(plot.verified_rows(summary, rows, selection)), list(arms))
        with self.assertRaisesRegex(ValueError, '显式'):
            plot.verified_rows(summary, rows)


if __name__ == '__main__':
    unittest.main()
