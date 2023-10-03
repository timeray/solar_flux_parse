from unittest import main, TestCase
from pathlib import Path
import datetime as dt

import numpy as np

from rstn_parse.parsers import parse_swpc_noonflux_data, RSTN_FREQS_MHZ, STATIONS, \
    parse_old_noonflux_data


TEST_DATA_DIR = Path(__file__).parent / 'test_data'
TEST_SWPC_NOONFLUX_PATH = TEST_DATA_DIR / '20110512dayind.txt'
TEST_OLD_NOONFLUX_PATH_LEAR_1988 = TEST_DATA_DIR / 'lear_noontime-flux_1988.txt'
TEST_OLD_NOONFLUX_PATH_PALE_2000 = TEST_DATA_DIR / 'pale_noontime-flux_2000.txt'
TEST_OLD_NOONFLUX_PATH_SGMR_1966 = TEST_DATA_DIR / 'sgmr_noontime-flux_1966.txt'
TEST_OLD_NOONFLUX_PATH_SVTO_2011 = TEST_DATA_DIR / 'svto_noontime-flux_2011.txt'


class TestSWPCNoonflux(TestCase):
    def test_parse_swpc_noonflux_data(self):
        result = parse_swpc_noonflux_data(TEST_SWPC_NOONFLUX_PATH)
        self.assertIsInstance(result, dict)
        self.assertListEqual(sorted(STATIONS), sorted(result))
        for key, value_dict in result.items():
            self.assertIsInstance(value_dict, dict)
            self.assertListEqual(RSTN_FREQS_MHZ, sorted(value_dict))
            for sub_dict_key, value in value_dict.items():
                self.assertIsInstance(value, float)
                self.assertTrue(np.isnan(value) or (value >= 0.0), value)

        self.assertAlmostEqual(result['LEAR'][245], 16.0)
        self.assertAlmostEqual(result['SVTO'][15400], 560.0)
        self.assertAlmostEqual(result['SGMR'][410], 36.0)
        self.assertAlmostEqual(result['PALE'][4995], 141.0)

    def _test_old_noonflux(self, path: Path, station: str, year: int):
        res = parse_old_noonflux_data(path)
        self.assertIsInstance(res, tuple)
        self.assertEqual(len(res), 3)
        self.assertIsInstance(res[0], str)
        self.assertIsInstance(res[1], np.ndarray)
        self.assertIsInstance(res[1][0], dt.date)
        self.assertIsInstance(res[2], dict)

        file_station, file_dates, file_res = res
        self.assertEqual(file_station, station)
        for date in file_dates:
            self.assertEqual(date.year, year)

        size = len(file_dates)
        self.assertEqual(len(file_res), len(RSTN_FREQS_MHZ))
        for freq, values in file_res.items():
            self.assertIsInstance(freq, int)
            self.assertIn(freq, RSTN_FREQS_MHZ)
            self.assertIsInstance(values, np.ndarray)
            self.assertEqual(size, len(values))
        return res

    def test_parse_old_noonflux_data(self):
        res = self._test_old_noonflux(TEST_OLD_NOONFLUX_PATH_LEAR_1988, 'LEAR', 1988)
        values_dict = res[2]
        self.assertAlmostEqual(values_dict[245][0], 27.0)
        self.assertAlmostEqual(values_dict[410][2], 29.0)
        self.assertAlmostEqual(values_dict[610][2], 48.0)
        self.assertTrue(np.isnan(values_dict[1415][12]))
        self.assertAlmostEqual(values_dict[2695][30], 100.0)
        self.assertAlmostEqual(values_dict[4995][31], 125.0)
        self.assertAlmostEqual(values_dict[8800][33], 250.0)
        self.assertAlmostEqual(values_dict[15400][33], 546.0)
        self._test_old_noonflux(TEST_OLD_NOONFLUX_PATH_PALE_2000, 'PALE', 2000)
        self._test_old_noonflux(TEST_OLD_NOONFLUX_PATH_SGMR_1966, 'SGMR', 1966)
        self._test_old_noonflux(TEST_OLD_NOONFLUX_PATH_SVTO_2011, 'SVTO', 2011)


if __name__ == '__main__':
    main()
