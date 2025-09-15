#!/usr/bin/env python3
import os
import sys
import time
from datetime import datetime, timezone, timedelta
from math import modf, ceil, floor
from zoneinfo import ZoneInfo

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from exodus_calendar.utils import compute_mars_timedelta, mars_datetime_to_earth_datetime_as_isoformat, add_timedelta_to_mars_date, earth_datetime_to_mars_datetime
from exodus_calendar.utils import DAY_LENGTH, SOL_LENGTH, EPOCH, JULIAN_YEAR_LENGTH, DAY_LENGTH, MS_PER_MARS_YEAR, MARS_MONTH_LENGTH, MS_PER_CYCLE, MARS_SECOND_LENGTH

EARTH_TIMEZONE = ZoneInfo("UTC")


# positive and positive timestamps = positive time delta
SEASONS_DATA = [
    ["0001-01-01 00:00:00.000", "0001-02-06 04:48:00.000", SOL_LENGTH*61.2],
    ["0001-01-01 00:00:00.000", "0001-02-06 04:48:00.000", SOL_LENGTH*126.6],
    ["0001-01-01 00:00:00.000", "0001-02-06 04:48:00.000", SOL_LENGTH*193.3],
    ["0001-01-01 00:00:00.000", "0001-02-06 04:48:00.000", SOL_LENGTH*257.8],
    ["0001-01-01 00:00:00.000", "0001-02-06 04:48:00.000", SOL_LENGTH*317.5],
    ["0001-01-01 00:00:00.000", "0001-02-06 04:48:00.000", SOL_LENGTH*371.9],
    ["0001-01-01 00:00:00.000", "0001-02-06 04:48:00.000", SOL_LENGTH*421.6],
    ["0001-01-01 00:00:00.000", "0001-02-06 04:48:00.000", SOL_LENGTH*468.5],
    ["0001-01-01 00:00:00.000", "0001-02-06 04:48:00.000", SOL_LENGTH*514.6],
    ["0001-01-01 00:00:00.000", "0001-02-06 04:48:00.000", SOL_LENGTH*562.0],
    ["0001-01-01 00:00:00.000", "0001-02-06 04:48:00.000", SOL_LENGTH*612.9],
    ["0001-01-01 00:00:00.000", "0001-02-06 04:48:00.000", SOL_LENGTH*668.6],
]


def seasons_test():
    print("Running season dates tests")
    for i in range(0, len(SEASONS_DATA),1):
        check_date = add_timedelta_to_mars_date(SEASONS_DATA[i][0], SEASONS_DATA[i][2], True)
        print(check_date)
    print("Finished season dates tests")


def main():
    seasons_test()

main()