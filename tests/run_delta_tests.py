#!/usr/bin/env python3
import os
import sys
import time
from datetime import datetime, timezone, timedelta
from math import modf, ceil, floor
from zoneinfo import ZoneInfo

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from exodus_calendar.utils import compute_mars_timedelta
from exodus_calendar.utils import JULIAN_YEAR_LENGTH, SOL_LENGTH, EPOCH, MS_PER_CYCLE, DAY_LENGTH, MS_PER_MARS_YEAR, MARS_MONTH_LENGTH

EARTH_TIMEZONE = ZoneInfo("UTC")


TEST_DATA_MTC_OFF = [
    ["0001-01-01 00:00:00.000", "0001-01-01 00:00:01.000", 1000]
]

# 0. calculate timedelta between two Mars timestamps
# 1. convert them into Earth timestamps
# 2. timedelta between two Earth timestamps should be identical
# 3. convert from Earth datetime to Mars datetime,
# 4  should be identical to input dates
# 5. first timedate + timedelta = second timedate
# 6. second timedate - timedelta = first time_date
# run test cases: 
#   positive and positive = positive time delta
#   positive and positive = negative time delta
#   positive and negative = positive time delta
#   positive and negative = negative time delta
#   negative and negative = positive time delta
#   negative and negative = negative time delta
def delta_tests():
    result = compute_mars_timedelta(TEST_DATA_MTC_OFF[0][0], TEST_DATA_MTC_OFF[0][1])
    print(result)
    print("Running time delta tests")


def main():
    delta_tests()

main()