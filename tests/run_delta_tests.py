#!/usr/bin/env python3
import os
import sys
import time
from datetime import datetime, timezone, timedelta
from math import modf, ceil, floor
from zoneinfo import ZoneInfo

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from exodus_calendar.utils import compute_mars_timedelta, mars_datetime_to_earth_datetime_as_isoformat, earth_datetime_to_mars_datetime
from exodus_calendar.utils import JULIAN_YEAR_LENGTH, SOL_LENGTH, EPOCH, MS_PER_CYCLE, DAY_LENGTH, MS_PER_MARS_YEAR, MARS_MONTH_LENGTH

EARTH_TIMEZONE = ZoneInfo("UTC")

# run test cases: 
#   positive and positive = positive time delta
#   positive and positive = negative time delta
#   positive and negative = positive time delta
#   positive and negative = negative time delta
#   negative and negative = positive time delta
#   negative and negative = negative time delta
TEST_DATA_MTC_OFF = [
    ["0001-01-01 00:00:00.000", "0001-01-01 00:00:01.000", 1000.0]
]

# 0. calculate timedelta between two Mars timestamps
# 1. convert them into Earth timestamps
# 2. timedelta between two Earth timestamps should be identical
# 3. convert from Earth datetime to Mars datetime,
# 4  should be identical to input dates
# 5. first timedate + timedelta = second timedate
# 6. second timedate - timedelta = first time_date
def delta_tests():
    print("Running time delta tests")
    delta_ms_M = compute_mars_timedelta(TEST_DATA_MTC_OFF[0][0], TEST_DATA_MTC_OFF[0][1])
    earth_date_1 = mars_datetime_to_earth_datetime_as_isoformat(TEST_DATA_MTC_OFF[0][0], False)
    earth_date_2 = mars_datetime_to_earth_datetime_as_isoformat(TEST_DATA_MTC_OFF[0][1], False)
    delta_time = (earth_date_2 - earth_date_1)
    delta_ms_E = (delta_time.total_seconds()*1000)
    assert(TEST_DATA_MTC_OFF[0][2]==delta_ms_M)
    assert(TEST_DATA_MTC_OFF[0][2]==delta_ms_E)
    mars_date_1 = earth_datetime_to_mars_datetime(earth_date_1)
    mars_date_2 = earth_datetime_to_mars_datetime(earth_date_2)
    assert(TEST_DATA_MTC_OFF[0][0]==mars_date_1[:23])
    assert(TEST_DATA_MTC_OFF[0][1]==mars_date_2[:23])


def main():
    delta_tests()

main()