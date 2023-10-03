import argparse
from pathlib import Path

import pandas as pd
from matplotlib import pyplot as plt

from norp_parse.parsers import load_norp_station_avg_daily_data


def plot_data(data: pd.DataFrame):
    plt.figure(figsize=(12, 7))
    dates = data.index.to_pydatetime()
    columns = data.columns
    for col in columns:
        plt.plot(dates, data[col], label=f'{col} MHz')
    plt.legend()
    plt.xlim(dates[0], dates[-1])
    plt.ylim(0, None)
    plt.xlabel('Time, UT')
    plt.ylabel('Flux, sfu')
    plt.tight_layout()
    plt.show()


def main():
    parser = argparse.ArgumentParser(description='Plot NoRP data')
    parser.add_argument('dirpath', help='Path to NoRP daily flux data')
    args = parser.parse_args()

    data = load_norp_station_avg_daily_data(Path(args.dirpath))
    plot_data(data)


if __name__ == '__main__':
    main()
