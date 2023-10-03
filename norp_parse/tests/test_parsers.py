from unittest import main, TestCase
from norp_parse.parsers import parse_norp_daily_flux

from pathlib import Path


TEST_DATA_DIR = Path(__file__).parent / 'test_data'
TEST_NORP_DAILY_FLUX = TEST_DATA_DIR / 'nbym0001'


class TestParsers(TestCase):
    def test_parse_norp_daily_flux(self):
        res = parse_norp_daily_flux(TEST_NORP_DAILY_FLUX)
        self.assertTrue(res.size > 0)


if __name__ == '__main__':
    main()
