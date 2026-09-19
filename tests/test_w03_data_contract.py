"""Exercise the notebook's actual SQL and evaluation with synthetic, offline fixtures.

These checks never write notebook outputs or stand in for warehouse verification.
"""
import contextlib
import io
from pathlib import Path
import unittest

import duckdb
import nbformat
import numpy as np
import pandas as pd


NOTEBOOK = Path(__file__).resolve().parents[1] / 'work/notebooks/w03_data_contract.ipynb'
SOURCES = [c.source for c in nbformat.read(NOTEBOOK, as_version=4).cells if c.cell_type == 'code']


def cell(prefix):
    return next(source for source in SOURCES if source.startswith(prefix))


class ContractTests(unittest.TestCase):
    def setUp(self):
        self.con = duckdb.connect()
        records = []
        for client in range(12):
            for page in range(8):
                for day in range(1, 32):
                    clicks = 4 if day <= 12 else (1 if page % 2 else 5)
                    records.append((f'client_{client}', f'page_{client}_{page}',
                                    pd.Timestamp(2026, 3, day), clicks, 100, 5.0, True))
        self.rows = pd.DataFrame(records, columns=['client_hash_id', 'content_hash_id',
                                                 'day', 'gsc_clicks', 'gsc_impressions',
                                                 'gsc_avg_position', 'search_data_available'])
        self.env = {'con': self.con, 'np': np, 'pd': pd, 'display': lambda *args: None,
                    'FEATURE_START': '2026-03-01', 'FEATURE_END': '2026-03-12',
                    'OUTCOME_START': '2026-03-16', 'OUTCOME_END': '2026-03-27',
                    'FEATURE_COLS': ['total_impressions', 'total_clicks', 'ctr',
                                     'weighted_position', 'click_change']}

    def tearDown(self):
        self.con.close()

    def load(self):
        self.con.register('march', self.rows)

    def run_cell(self, prefix):
        with contextlib.redirect_stdout(io.StringIO()):
            exec(cell(prefix), self.env)

    def test_feature_values_no_future_contamination_and_leak_removed(self):
        self.load()
        for prefix in ['grain_sql', 'count_sql', 'availability_sql', 'feature_sql']:
            self.run_cell(prefix)
        before = self.env['X'].copy()
        self.assertTrue((before.total_clicks == 48).all())
        self.assertTrue((before.total_impressions == 1200).all())
        np.testing.assert_allclose(before.ctr, 0.04)
        np.testing.assert_allclose(before.weighted_position, 5)
        self.run_cell('from sklearn.model_selection')
        self.assertAlmostEqual(self.env['leaky_score'], 1.0)
        self.run_cell("X_leaky.drop")
        self.assertNotIn('X_leaky', self.env)
        self.assertEqual(self.env['X'].shape[1], 5)
        self.rows.loc[self.rows.day >= '2026-03-16', 'gsc_clicks'] = 80
        self.load()
        self.run_cell('feature_sql')
        pd.testing.assert_frame_equal(before, self.env['X'])
        self.assertEqual(self.env['y'].sum(), 0)

    def test_missing_day_and_false_availability_exclude_pages(self):
        self.rows = self.rows[~((self.rows.content_hash_id == 'page_0_0') & (self.rows.day == '2026-03-02'))]
        self.rows.loc[(self.rows.content_hash_id == 'page_0_1') & (self.rows.day == '2026-03-16'), 'search_data_available'] = False
        self.rows.loc[self.rows.content_hash_id == 'page_0_2', 'gsc_avg_position'] = 0
        self.load()
        self.run_cell('feature_sql')
        self.assertEqual(len(self.env['data']), 94)
        selected = self.env['data'].set_index('content_hash_id')
        self.assertNotIn('page_0_0', selected.index)
        self.assertNotIn('page_0_1', selected.index)
        self.assertTrue(pd.isna(selected.loc['page_0_2', 'weighted_position']))

    def test_duplicates_fail_grain(self):
        self.rows = pd.concat([self.rows, self.rows.iloc[[0]]], ignore_index=True)
        self.load()
        with self.assertRaisesRegex(AssertionError, 'Raw grain failed'):
            self.run_cell('grain_sql')

    def test_weighted_position_and_zero_earlier_clicks(self):
        page = self.rows.content_hash_id == 'page_0_0'
        self.rows.loc[page & (self.rows.day <= '2026-03-06'), 'gsc_clicks'] = 0
        self.rows.loc[page & (self.rows.day <= '2026-03-06'), 'gsc_impressions'] = 200
        self.rows.loc[page & (self.rows.day <= '2026-03-06'), 'gsc_avg_position'] = 2
        self.load()
        self.run_cell('feature_sql')
        result = self.env['data'].set_index('content_hash_id').loc['page_0_0']
        self.assertEqual(result.click_change, 24)
        self.assertEqual(result.weighted_position, 3)
        self.assertAlmostEqual(result.ctr, 24 / 1800)

    def test_one_class_stops_evaluation(self):
        self.rows.gsc_clicks = 4
        self.load()
        self.run_cell('feature_sql')
        with self.assertRaisesRegex(RuntimeError, 'both label classes'):
            self.run_cell('from sklearn.model_selection')

    def test_search_availability_predicate_and_client_join(self):
        clients = pd.DataFrame({'client_hash_id': [f'client_{c}' for c in range(12)],
                                'gsc_data_start': [pd.Timestamp('2026-03-02')] * 12})
        raw = self.rows.rename(columns={'day': 'report_date'}).drop(columns='search_data_available')
        raw['gsc_data_available'] = True
        raw.loc[raw.report_date == '2026-03-03', 'gsc_data_available'] = False
        self.con.register('march_raw', raw)
        self.con.register('clients', clients)
        setup = cell("if 'con' in globals():")
        view_code = setup[setup.index('flag_check ='):setup.index("print('Cached release revision:")]
        for has_flag, expected_days in [(False, 30), (True, 29)]:
            self.env['manifest'] = {'has_search_flag': has_flag}
            exec(view_code, self.env)
            self.run_cell('availability_sql')
            self.assertEqual(self.env['availability_result'].rows_after.iloc[0], expected_days * 96)


if __name__ == '__main__':
    unittest.main()
