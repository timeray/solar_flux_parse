from pathlib import Path
import argparse
from typing import List
import datetime as dt

import pandas as pd

from rstn_parse.parsers import parse_swpc_noonflux_data, parse_old_noonflux_data, \
    STATIONS, RSTN_FREQS_MHZ


def collect_old_data(dirpath: Path) -> pd.DataFrame:
    if not dirpath.exists():
        raise FileExistsError(f'No such directory for old data: {dirpath}')

    tables = []
    for path in sorted(dirpath.glob('*/*noontime-flux*.txt')):
        station, dates, values_dict = parse_old_noonflux_data(path)
        tables.append(pd.DataFrame(
            index=pd.Index(data=dates, name='Date'),
            data={(station, freq): values for freq, values in values_dict.items()}
        ))

    return pd.concat(tables, axis=0).sort_index().groupby(by='Date').mean()


def collect_swpc_data(dirpaths: List[Path]) -> pd.DataFrame:
    for dirpath in dirpaths:
        if not dirpath.exists():
            raise FileExistsError(f'No such directory for swpc data: {dirpath}')

        if not dirpath.is_dir():
            raise ValueError(f'{dirpath} is not a directory')

    dates = []
    values_dict = {(station, freq): [] for station in STATIONS for freq in RSTN_FREQS_MHZ}
    for year_dirpath in sorted(dirpaths):
        for month_dirpath in sorted(year_dirpath.glob('*')):
            for day_path in sorted(month_dirpath.glob('*dayind.txt')):
                station_dict = parse_swpc_noonflux_data(day_path)
                if not station_dict:
                    continue

                dates.append(dt.datetime.strptime(day_path.name[:8], '%Y%m%d').date())
                for station, freq_values in station_dict.items():
                    for freq in sorted(freq_values):
                        values_dict[(station, freq)].append(freq_values[freq])
    return pd.DataFrame(data=values_dict, index=pd.Index(data=dates, name='Date'))


def main():
    parser = argparse.ArgumentParser(description='Parse RSTN database to a single file')
    parser.add_argument('output_path', help='Path to output file')
    parser.add_argument('data_dirpath', help='Path to directory RSTN data')
    args = parser.parse_args()

    output_path = Path(args.output_path)
    data_dirpath = Path(args.data_dirpath)
    if not data_dirpath.exists():
        raise FileExistsError(f'No such directory: {data_dirpath}')

    old_data_df = collect_old_data(data_dirpath / 'old')
    new_data_df = collect_swpc_data(sorted(data_dirpath.glob('20*')))
    pd.concat([old_data_df, new_data_df]).to_csv(output_path, sep='\t', na_rep='NaN')


if __name__ == '__main__':
    main()
