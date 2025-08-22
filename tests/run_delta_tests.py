#!/usr/bin/env python3
import os
import sys
import time
from datetime import datetime, timezone, timedelta
from math import modf, ceil, floor
from zoneinfo import ZoneInfo

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from exodus_calendar.utils import compute_mars_timedelta, mars_datetime_to_earth_datetime_as_isoformat, add_timedelta_to_mars_date, earth_datetime_to_mars_datetime
from exodus_calendar.utils import DAY_LENGTH, SOL_LENGTH, EPOCH, JULIAN_YEAR_LENGTH, DAY_LENGTH, MS_PER_MARS_YEAR, MARS_MONTH_LENGTH

EARTH_TIMEZONE = ZoneInfo("UTC")

# run test cases: 
#   positive and positive = negative time delta
#   positive and negative = positive time delta
#   positive and negative = negative time delta
#   negative and negative = positive time delta
#   negative and negative = negative time delta
TEST_DATA_MTC_OFF = [
    #  positive and positive = positive time delta
    ["0001-01-01 00:00:00.000", "0001-01-01 00:00:01.000", 1000.0],
    ["0001-01-01 00:00:00.000", "0001-01-01 24:00:00.000", DAY_LENGTH],
    ["0001-01-01 00:00:00.000", "0001-01-02 00:00:00.000", SOL_LENGTH],
    ["0001-01-01 00:00:00.000", "0001-01-08 00:00:00.000", 7*SOL_LENGTH],
    ["0001-01-01 00:00:00.000", "0001-01-31 04:12:22.680", 31*DAY_LENGTH],
    ["0001-01-01 00:00:00.000", "0001-02-01 00:00:00.000", MARS_MONTH_LENGTH*SOL_LENGTH],
    ["0001-01-01 00:00:00.000", "0001-12-01 00:00:00.000", 11*MARS_MONTH_LENGTH*SOL_LENGTH],
    ["0001-01-01 00:00:00.000", "0001-12-52 24:39:35.144", SOL_LENGTH*MARS_MONTH_LENGTH*11+52*SOL_LENGTH-100],
    ["0001-01-01 00:00:00.000", "0001-12-53 24:39:35.144", SOL_LENGTH*MARS_MONTH_LENGTH*11+53*SOL_LENGTH-100],
    ["0001-01-01 00:00:00.000", "0002-01-01 00:00:00.000", SOL_LENGTH*MARS_MONTH_LENGTH*11+53*SOL_LENGTH],
    ["0001-01-01 00:00:00.000", "0001-07-20 11:46:28.380", DAY_LENGTH*JULIAN_YEAR_LENGTH]
]


def run_positive_dates_mtc_off():
    for i in range(0, len(TEST_DATA_MTC_OFF),1):
        # calculate timedelta between two Mars timestamps
        # convert them into Earth timestamps
        delta_ms_M = compute_mars_timedelta(TEST_DATA_MTC_OFF[i][0], TEST_DATA_MTC_OFF[i][1])
        earth_date_1 = mars_datetime_to_earth_datetime_as_isoformat(TEST_DATA_MTC_OFF[i][0], False)
        earth_date_2 = mars_datetime_to_earth_datetime_as_isoformat(TEST_DATA_MTC_OFF[i][1], False)
        
        # timedelta between two Earth timestamps should be identical to Mars
        delta_time = (earth_date_2 - earth_date_1)
        delta_ms_E = (delta_time.total_seconds()*1000)
        assert(TEST_DATA_MTC_OFF[i][2]==delta_ms_E)
        assert(delta_ms_M==delta_ms_E)
        
        # convert from Earth datetimes back to Mars datetimes,
        # those should be identical to input dates
        mars_date_1 = earth_datetime_to_mars_datetime(earth_date_1)
        mars_date_2 = earth_datetime_to_mars_datetime(earth_date_2)
        assert(TEST_DATA_MTC_OFF[i][0]==mars_date_1[:23])
        assert(TEST_DATA_MTC_OFF[i][1]==mars_date_2[:23])
        
        # first timedate + timedelta = second timedate
        # second timedate - timedelta = first time_date
        check_date_1 = add_timedelta_to_mars_date(TEST_DATA_MTC_OFF[i][0], TEST_DATA_MTC_OFF[i][2])
        check_date_2 = add_timedelta_to_mars_date(TEST_DATA_MTC_OFF[i][1], -TEST_DATA_MTC_OFF[i][2])
        assert(check_date_1[:23]==TEST_DATA_MTC_OFF[i][1])
        assert(check_date_2[:23]==TEST_DATA_MTC_OFF[i][0])


def delta_tests():
    print("Running time delta tests")
    run_positive_dates_mtc_off()
    print("Finished time delta tests")


def main():
    delta_tests()

main()