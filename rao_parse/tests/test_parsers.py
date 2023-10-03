from pathlib import Path
from unittest import TestCase, main

from rao_parse.parsers import read_sp2_24_fit_file


TEST_DATA_PATH = Path(__file__).parent / 'test_data' / 'smf_20200101_000000.fit'


class TestRaoParsers(TestCase):
    def test_sp2_24_fits(self):
        res_dict = read_sp2_24_fit_file(TEST_DATA_PATH)
        self.assertIsInstance(res_dict, dict)
        self.assertEqual(len(res_dict), 16)


if __name__ == '__main__':
    main()
