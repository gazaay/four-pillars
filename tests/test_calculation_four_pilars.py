import unittest
from datetime import datetime
from app import bazi


class TestYourModule(unittest.TestCase):

    def test_get_heavenly_stem_earthly_branch(self):
        test_cases = [
            {
                'year': 2023,
                'month': 7,
                'expected_heavenly_stem': bazi.HeavenlyStem.GUI.value,
                'expected_earthly_branch': bazi.EarthlyBranch.MAO.value
            },
            {
                'year': 2023,
                'month': 6,
                'expected_heavenly_stem': bazi.HeavenlyStem.GUI.value,
                'expected_earthly_branch': bazi.EarthlyBranch.MAO.value
            },
            # Add more test cases here...
        ]

        for test_case in test_cases:
            year = test_case['year']
            month = test_case['month']
            expected_heavenly_stem = test_case['expected_heavenly_stem']
            expected_earthly_branch = test_case['expected_earthly_branch']

            heavenly_stem, earthly_branch = bazi.get_heavenly_stem_earthly_branch(year, month)

            self.assertEqual(heavenly_stem, expected_heavenly_stem)
            self.assertEqual(earthly_branch, expected_earthly_branch)

    def test_calculate_month_heavenly(self):
        test_cases = [
           {
                'year': 2023,
                'month': 6,
                'expected_month_heavenly_stem': bazi.HeavenlyStem.JI.value,
                'expected_month_earthly_branch': bazi.EarthlyBranch.WEI.value
            },
            {
                'year': 2023,
                'month': 7,
                'expected_month_heavenly_stem': bazi.HeavenlyStem.GENG.value,
                'expected_month_earthly_branch': bazi.EarthlyBranch.SHEN.value
            },
            # Add more test cases here...
        ]

        for test_case in test_cases:
            year = test_case['year']
            month = test_case['month']
            expected_month_heavenly_stem = test_case['expected_month_heavenly_stem']
            expected_month_earthly_branch = test_case['expected_month_earthly_branch']

            month_heavenly_stem, earthly_branch_stem = bazi.calculate_month_heavenly(year, month)

            self.assertEqual(month_heavenly_stem.value, expected_month_heavenly_stem)
            self.assertEqual(earthly_branch_stem.value, expected_month_earthly_branch)

    def test_calculate_day_heavenly(self):
        test_cases = [
            {
                'year': 2023,
                'month': 6,
                'day': 3,
                'expected_heavenly_stem': bazi.HeavenlyStem.JI.value,
                'expected_earthly_branch': bazi.EarthlyBranch.MAO.value
            },
            {
                'year': 2023,
                'month': 6,
                'day': 5,
                'expected_heavenly_stem': bazi.HeavenlyStem.XIN.value,
                'expected_earthly_branch': bazi.EarthlyBranch.SI.value
            },
            # Add more test cases here...
        ]

        for test_case in test_cases:
            year = test_case['year']
            month = test_case['month']
            day = test_case['day']
            expected_heavenly_stem = test_case['expected_heavenly_stem']
            expected_earthly_branch = test_case['expected_earthly_branch']

            heavenly_stem, earthly_branch = bazi.calculate_day_heavenly(year, month, day)

            self.assertEqual(heavenly_stem.value, expected_heavenly_stem)
            self.assertEqual(earthly_branch.value, expected_earthly_branch)

    def test_calculate_hour_heavenly(self):
        test_cases = [
            {
                'year': 2023,
                'month': 6,
                'day': 3,
                'hour': 9,
                'expected_heavenly_stem': bazi.HeavenlyStem.JI.value,
                'expected_earthly_branch': bazi.EarthlyBranch.SI.value
            },
            # Add more test cases here...
        ]

        for test_case in test_cases:
            year = test_case['year']
            month = test_case['month']
            day = test_case['day']
            hour = test_case['hour']
            expected_heavenly_stem = test_case['expected_heavenly_stem']
            expected_earthly_branch = test_case['expected_earthly_branch']

            heavenly_stem, earthly_branch = bazi.calculate_hour_heavenly(year, month, day, hour)

            self.assertEqual(heavenly_stem.value, expected_heavenly_stem)
            self.assertEqual(earthly_branch.value, expected_earthly_branch)

if __name__ == '__main__':
    unittest.main()