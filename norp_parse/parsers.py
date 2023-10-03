from pathlib import Path
import datetime as dt
from typing import List

import pandas as pd
import numpy as np


TYKW_AGGREGATE_FILENAME = 'TYKW-NoRP_dailyflux.txt'


def parse_tykw_aggregate_file(path: Path) -> pd.DataFrame:
    return pd.read_csv(str(path), skiprows=2, index_col=0, parse_dates=True,
                       names=['Date', 1000, 2000, 3750, 9400])


def parse_norp_daily_flux(path: Path) -> pd.DataFrame:
    flux_dict = {}
    dates = []
    freqs = []
    with open(path) as file:
        for line_num, line in enumerate(file):
            line = line.strip()

            if line_num == 9:
                freqs = [int(x) for x in line.split()]
                for freq in freqs:
                    flux_dict[freq] = []

            if line_num >= 13 and line and not line.startswith('#'):
                line = line.split()
                dates.append(dt.datetime.strptime(line[0], '%Y-%m-%d'))
                for freq, val in zip(freqs, line[1:]):
                    flux_dict[freq].append(float(val) if val != '-' else np.nan)

    return pd.DataFrame(data=flux_dict, index=dates)


def load_station_daily_data(paths: List[Path]) -> pd.DataFrame:
    dfs = []
    for path in paths:
        dfs.append(parse_norp_daily_flux(path))

    return pd.concat(dfs)


def load_norp_daily_data(dirpath: Path) -> pd.DataFrame:
    if not dirpath.exists():
        raise FileExistsError(str(dirpath))

    if not dirpath.is_dir():
        raise NotADirectoryError(str(dirpath))

    tykm_data = parse_tykw_aggregate_file(dirpath / TYKW_AGGREGATE_FILENAME)
    tok_data = load_station_daily_data(sorted(dirpath.glob('tok*[0-9]')))
    nbym_data = load_station_daily_data(sorted(dirpath.glob('nbym*[0-9]')))

    return pd.concat([tykm_data, tok_data, nbym_data], axis=1, keys=['tykm', 'tok', 'nbym'])


def load_norp_station_avg_daily_data(dirpath: Path) -> pd.DataFrame:
    return load_norp_daily_data(dirpath).groupby(level=1, axis=1).mean()
