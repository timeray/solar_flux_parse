import datetime as dt
from typing import Union
from pathlib import Path

import numpy as np


class F107:
    OLD_FLUX_PATH = Path(__file__).parent / 'f10.7.csv'
    NEW_FLUX_PATH = Path(__file__).parent / 'f10.7_new.csv'

    def __init__(self):
        date_str, time_str, _, _, flux_obs, flux_adj, flux_ursi = np.loadtxt(
            str(self.NEW_FLUX_PATH),
            skiprows=2,
            dtype="O, O, f, f, f, f, f",
            unpack=True,
        )

        time_marks = np.array(
            [
                dt.datetime(
                    int(d[:4]), int(d[4:6]), int(d[6:]),
                    int(t[:2]), int(t[2:4]), int(t[4:])
                )
                for d, t in zip(date_str, time_str)
            ],
            dtype=dt.datetime
        )
        first_new_date = time_marks[0]

        old_time_marks = []
        flux = []
        with open(str(self.OLD_FLUX_PATH)) as file:
            for line_num, line in enumerate(file):
                line = line.strip()

                if not line:
                    continue

                line = [s for s in line.split(' ') if s]
                date = dt.datetime.strptime(line[0], '%Y%m%d')

                if date >= first_new_date:
                    break

                old_time_marks.append(date)

                if len(line) < 2:
                    flux.append(np.nan)
                else:
                    if line[1].endswith('+'):
                        line[1] = line[1][:-1]
                    flux.append(float(line[1]))

        self.time_marks = np.concatenate([old_time_marks, time_marks])
        self.dates = np.array([time_mark.date() for time_mark in self.time_marks], dtype=dt.date)
        self.flux = np.concatenate([flux, flux_adj])

    def get_closest(self, time_marks: Union[dt.datetime, np.ndarray]):
        time_marks = np.asarray(time_marks, dtype=dt.datetime)
        valid = (time_marks >= self.time_marks[0]) & (time_marks <= self.time_marks[-1])
        result = np.full(time_marks.size, np.nan, dtype=float)
        valid_marks = time_marks[valid]
        args = self.time_marks.searchsorted(valid_marks)
        left_args = args - 1
        left = valid_marks - self.time_marks[np.maximum(args - 1, 0)]
        right = self.time_marks[args] - valid_marks
        closest_args = np.where(left < right, left_args, args)
        result[valid] = self.flux[closest_args]
        return result

    def mean_daily(self, dates: Union[dt.date, np.ndarray]):
        dates = np.asarray(dates, dtype=dt.date)
        flux = np.empty(len(dates), dtype=float)
        for i, date in enumerate(dates):
            flux[i] = np.nanmean(self.flux[self.dates == date])

        if flux.size == 1:
            return flux.item()
        else:
            return flux
