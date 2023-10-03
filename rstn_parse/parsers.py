from pathlib import Path
from typing import Dict, Tuple
import datetime as dt

import numpy as np
import pandas as pd


RSTN_FREQS_MHZ = [245, 410, 610, 1415, 2695, 4995, 8800, 15400]
STATIONS = ['LEAR', 'SVTO', 'SGMR', 'PALE']


def parse_swpc_noonflux_data(path: Path) -> Dict[str, Dict[int, float]]:
    with open(path) as file:
        lines = file.readlines()
        if not lines:
            return {}
        result = {name: {} for name in STATIONS}
        expected_freqs = sorted(RSTN_FREQS_MHZ + [2800])

        def proc_value(_val: int) -> float:
            if _val == -1:
                return np.nan
            else:
                return float(_val)

        for expected_freq, line in zip(expected_freqs, lines[23:32]):
            values = [int(val) for val in line.split()]
            assert len(values) == 8
            assert values[0] == expected_freq

            if expected_freq != 2800:
                result['LEAR'][expected_freq] = proc_value(values[1])
                result['SVTO'][expected_freq] = proc_value(values[2])
                result['SGMR'][expected_freq] = proc_value(values[3])
                result['PALE'][expected_freq] = proc_value(values[6])

    return result


DateArray = np.ndarray


def parse_old_noonflux_data(path: Path) -> Tuple[str, DateArray, Dict[int, np.ndarray]]:
    name = None

    def str2val(_s: str) -> float:
        _s = _s.strip(' *!U\n')
        if _s:
            return float(_s)
        else:
            return np.nan

    with open(path) as file:
        dates = []
        result = {freq: [] for freq in RSTN_FREQS_MHZ}
        for line in file:
            if not line.rstrip() or line == '\x00\n':
                continue

            date_str = line[:6]
            # Fake date for month average
            if int(date_str[4:6] == '32'):
                continue

            year_short = int(date_str[:2])
            if year_short <= 11:
                year = 2000 + year_short
            else:
                year = 1900 + year_short

            dates.append(dt.date(year, int(date_str[2:4]), int(date_str[4:6])))

            if name is None:
                name = line[7:11]
            result[245].append(str2val(line[11:17]))
            result[410].append(str2val(line[17:25]))
            result[610].append(str2val(line[25:33]))
            result[1415].append(str2val(line[33:41]))
            result[2695].append(str2val(line[41:49]))
            result[4995].append(str2val(line[49:57]))
            result[8800].append(str2val(line[57:65]))
            result[15400].append(str2val(line[65:73]))

    dates = np.array(dates, dtype=dt.date)
    result = {freq: np.array(values) for freq, values in result.items()}
    return name, dates, result


def load_collected_data(path: Path) -> pd.DataFrame:
    return pd.read_csv(str(path), sep='\t', na_values='NaN', header=[0, 1], index_col=0,
                       parse_dates=True)
