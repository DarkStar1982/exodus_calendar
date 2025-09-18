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


# will replace the basic tests
TEST_DATA_A_MTC_ON = [
    [('0001-01-01', '00:00:00.000', 'Monday', 0.172), 0],
    [('0001-01-01', '00:00:00.973', 'Monday', 0.172), 1000],
    [('0001-01-01', '23:21:28.307', 'Monday', 0.67), DAY_LENGTH],
    [('0001-01-02', '00:00:00.000', 'Tuesday', 0.683), SOL_LENGTH],
    [('0001-01-08', '00:00:00.000', 'Monday', 3.736), SOL_LENGTH*7],
    [('0001-01-31', '04:05:37.527', 'Wednesday', 15.265), DAY_LENGTH*31],
    [('0001-02-01', '00:00:00.000', 'Monday', 27.692), SOL_LENGTH*MARS_MONTH_LENGTH],
    [('0001-12-01', '00:00:00.000', 'Monday', 331.999), SOL_LENGTH*MARS_MONTH_LENGTH*11],
    [('0001-12-52', '23:59:59.903', 'Wednesday', 359.881), SOL_LENGTH*MARS_MONTH_LENGTH*11+52*SOL_LENGTH-100],
    [('0001-12-53', '23:59:59.903', 'Thursday', 0.393), SOL_LENGTH*MARS_MONTH_LENGTH*11+53*SOL_LENGTH-100],
    [('0002-01-01', '00:00:00.000', 'Monday', 0.393), SOL_LENGTH*MARS_MONTH_LENGTH*11+53*SOL_LENGTH],
    [('0001-07-20', '11:27:34.249', 'Saturday', 170.859), DAY_LENGTH*JULIAN_YEAR_LENGTH],
    [('0001-12-53', '00:00:00.000', 'Thursday', 359.881), SOL_LENGTH*668],
    [('0002-01-01', '00:00:00.000', 'Monday', 0.393), SOL_LENGTH*669],
    [('0011-01-01', '21:49:05.455', 'Monday', 0.168), MS_PER_MARS_YEAR*10],
    [('0023-01-01', '00:00:00.000', 'Monday', 0.165), MS_PER_CYCLE],
    [('0030-01-01', '03:16:21.818', 'Monday', 0.172), MS_PER_MARS_YEAR*29]


]

def run_basic_tests():
    for i in range(0, len(TEST_DATA_A_MTC_ON),1):
        timedate0 = datetime.fromisoformat(EPOCH)
        milliseconds_to_add = timedelta(milliseconds=TEST_DATA_A_MTC_ON[i][1])
        timedate1 = timedate0 + milliseconds_to_add
        assert(earth_datetime_to_mars_datetime(timedate1, True)==TEST_DATA_A_MTC_ON[i][0])

def main():
    print("Running foundational tests")
    run_basic_tests()
    print("Finished foundational tests")


main()
