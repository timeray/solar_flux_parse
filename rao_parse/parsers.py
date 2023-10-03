from collections import defaultdict
from pathlib import Path
from typing import Dict, List
import datetime as dt

import numpy as np
from astropy.io import fits


class Record:
    def __init__(self, time_marks: np.ndarray, rcp: np.ndarray, lcp: np.ndarray):
        self.time_marks = time_marks
        self.rcp = rcp
        self.lcp = lcp

    @property
    def flux(self):
        return self.rcp + self.lcp


FreqRecordDict = Dict[int, Record]


def parse_date(filename: str) -> dt.date:
    return dt.datetime.strptime(filename.split('_')[1], '%Y%m%d').date()


def read_sp2_24_fit_file(path: Path) -> FreqRecordDict:
    ref_date = parse_date(path.name)
    ref_datetime = dt.datetime(ref_date.year, ref_date.month, ref_date.day)
    with fits.open(str(path)) as hdul:
        if len(hdul) < 2 or hdul[1].data.dtype[1].itemsize == 0:
            return {}

        result = {}
        for hdu in hdul[1].data:
            result[int(hdu[0])] = Record(
                time_marks=np.array([ref_datetime + dt.timedelta(seconds=ms) for ms in hdu[1]],
                                    dtype=dt.datetime),
                rcp=hdu[2],
                lcp=hdu[3],
            )
    return result


def _concat_records(record_list: List[Record]) -> Record:
    tms = []
    rcps = []
    lcps = []
    for record in record_list:
        tms.append(record.time_marks)
        rcps.append(record.rcp)
        lcps.append(record.lcp)
    return Record(np.concatenate(tms), np.concatenate(rcps), np.concatenate(lcps))


def _read_sp2_24_fit_files(filepaths: List[Path]) -> FreqRecordDict:
    parsed_records_dicts = []
    for filepath in filepaths:
        try:
            freq_dict = read_sp2_24_fit_file(filepath)
        except OSError:
            continue
        if not freq_dict:
            continue
        parsed_records_dicts.append(freq_dict)

    if len(parsed_records_dicts) == 0:
        return {}
    if len(parsed_records_dicts) == 1:
        return parsed_records_dicts[0]

    freqs = set(parsed_records_dicts[0])
    for records_dict in parsed_records_dicts:
        assert freqs == set(records_dict)

    result = {
        freq: _concat_records([freq_dict[freq] for freq_dict in parsed_records_dicts])
        for freq in freqs
    }

    return result


class SP2_24DailyReader:
    def __init__(self, dirpath: Path):
        filepaths = sorted(dirpath.glob('*/smf*.fit'))
        dates = [parse_date(filepath.name) for filepath in filepaths]
        self.filepaths_dict = defaultdict(list)
        for date, filepath in zip(dates, filepaths):
            self.filepaths_dict[date].append(filepath)

    def get_daily_data(self, date: dt.date) -> FreqRecordDict:
        return _read_sp2_24_fit_files(self.filepaths_dict[date])
