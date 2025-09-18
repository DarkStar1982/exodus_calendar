#!/usr/bin/env python3
import os
import sys
import time
from datetime import datetime, timezone, timedelta
from math import modf, ceil, floor
from zoneinfo import ZoneInfo

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from exodus_calendar.utils import earth_datetime_to_mars_datetime, mars_datetime_to_earth_datetime
from exodus_calendar.utils import JULIAN_YEAR_LENGTH, SOL_LENGTH, EPOCH, MS_PER_CYCLE, DAY_LENGTH, MS_PER_MARS_YEAR, MARS_MONTH_LENGTH

EARTH_TIMEZONE = ZoneInfo("UTC")


TEST_DATA_A_MTC_ON = [
    [EPOCH, ('0001-01-01', '00:00:00.000', ' Monday', 0.172), 0]
]

def run_basic_tests():
    timedate = datetime.fromisoformat(TEST_DATA_A_MTC_ON[0][0])
    assert(earth_datetime_to_mars_datetime(timedate, True)==TEST_DATA_A_MTC_ON[0][1])

def main():
    run_basic_tests()

main()
