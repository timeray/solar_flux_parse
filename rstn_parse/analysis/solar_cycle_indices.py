from pathlib import Path
import datetime as dt
from collections import namedtuple

import numpy as np


INT_SSN_PATH = Path(__file__).parent / 'international_sunspot_number.csv'
SSNDaily = namedtuple('SSNDaily', ['date', 'ssn'])


def get_international_daily_ssn(path: Path = INT_SSN_PATH) -> SSNDaily:
    with open(path) as file:
        dates = []
        ssn = []
        first = True
        for line in file:
            if first:
                first = False
                continue
            date_str, ssn_str = line.strip().split(',')
            dates.append(dt.datetime.strptime(date_str, '%Y %m %d').date())
            ssn.append(int(float(ssn_str)))
        return SSNDaily(date=np.array(dates, dtype=dt.date), ssn=np.array(ssn))
