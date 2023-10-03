import argparse
from pathlib import Path

from rstn_parse.parsers import load_collected_data, RSTN_FREQS_MHZ, STATIONS

import pandas as pd
from matplotlib import pyplot as plt


def plot_all_flux(data: pd.DataFrame):
    fig, axes = plt.subplots(4, 2, sharex=True, figsize=(15, 8))

    dates = data.index.to_pydatetime()
    for ax, freq in zip(axes.ravel(), RSTN_FREQS_MHZ):
        ax.set_title(freq)

        freq_df = data.loc[:, (slice(None), str(freq))]
        for station in STATIONS:
            ax.plot(dates, freq_df[station, str(freq)].values.ravel())
            ax.plot(dates, freq_df.mean(axis=1).values, color='k', lw=0.75)

    plt.show()


def main():
    parser = argparse.ArgumentParser(description='Plots for RSTN database')
    parser.add_argument('path_to_database', help='Path to RSTN noonflux database generated with '
                                                 'collect_database.py script')
    args = parser.parse_args()
    path_to_database = Path(args.path_to_database)

    database = load_collected_data(path_to_database)

    plot_all_flux(database)


if __name__ == '__main__':
    main()
