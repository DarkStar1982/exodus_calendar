#!/usr/bin/env python3
import os
import sys
import time
from datetime import datetime, timezone, timedelta
from math import modf, ceil, floor
from zoneinfo import ZoneInfo

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from exodus_calendar.utils import (
    earth_datetime_to_mars_datetime, 
    mars_datetime_to_earth_datetime, 
    earth_datetime_to_mars_datetime_as_string,
    mars_datetime_to_earth_datetime_as_ms
)

from exodus_calendar.utils import (
    JULIAN_YEAR_LENGTH, SOL_LENGTH, 
    EPOCH, 
    MS_PER_CYCLE, 
    DAY_LENGTH, 
    MS_PER_MARS_YEAR, 
    MARS_MONTH_LENGTH
)

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

TEST_DATA_A_MTC_OFF = [
    [('0001-01-01', '00:00:00.000', 'Monday', 0.172), 0],
    [('0001-01-01', '00:00:01.000', 'Monday', 0.172), 1000],
    [('0001-01-01', '24:00:00.000', 'Monday', 0.67), DAY_LENGTH],
    [('0001-01-02', '00:00:00.000', 'Tuesday', 0.683), SOL_LENGTH],
    [('0001-01-08', '00:00:00.000', 'Monday', 3.736), SOL_LENGTH*7],
    [('0001-01-31', '04:12:22.680', 'Wednesday', 15.265), DAY_LENGTH*31],
    [('0001-02-01', '00:00:00.000', 'Monday', 27.692), SOL_LENGTH*MARS_MONTH_LENGTH],
    [('0001-12-01', '00:00:00.000', 'Monday', 331.999), SOL_LENGTH*MARS_MONTH_LENGTH*11],
    [('0001-12-52', '24:39:35.144', 'Wednesday', 359.881), SOL_LENGTH*MARS_MONTH_LENGTH*11+52*SOL_LENGTH-100],
    [('0001-12-53', '24:39:35.144', 'Thursday', 0.393), SOL_LENGTH*MARS_MONTH_LENGTH*11+53*SOL_LENGTH-100],
    [('0002-01-01', '00:00:00.000', 'Monday', 0.393), SOL_LENGTH*MARS_MONTH_LENGTH*11+53*SOL_LENGTH],
    [('0001-07-20', '11:46:28.380', 'Saturday', 170.859), DAY_LENGTH*JULIAN_YEAR_LENGTH],
    [('0001-12-53', '00:00:00.000', 'Thursday', 359.881), SOL_LENGTH*668],
    [('0002-01-01', '00:00:00.000', 'Monday', 0.393), SOL_LENGTH*669],
    [('0011-01-01', '22:25:04.767', 'Monday', 0.168), MS_PER_MARS_YEAR*10],
    [('0023-01-01', '00:00:00.000', 'Monday', 0.165), MS_PER_MARS_YEAR*22],
    [('0030-01-01', '03:21:45.715', 'Monday', 0.172), MS_PER_MARS_YEAR*29]   
]


TEST_DATA_B_MTC_ON = [
    [('-0001-12-54', '23:59:59.027', 'Friday', 0.172), 1000],
    [('-0001-12-54', '00:38:31.693', 'Friday', 359.673), DAY_LENGTH],
    [('-0001-12-54', '00:00:00.000', 'Friday', 359.659), SOL_LENGTH],
    [('-0001-12-24', '19:54:22.473', 'Wednesday', 344.324), DAY_LENGTH*31],
    [('-0001-12-01', '00:00:00.000', 'Monday', 331.202), SOL_LENGTH*54],
    [('-0001-11-01', '00:00:00.000', 'Monday', 298.154), SOL_LENGTH*110],
    [('-0001-01-01', '00:00:00.000', 'Monday', 359.442), SOL_LENGTH*670],
    [('-0006-09-11', '05:24:17.509', 'Thursday', 232.708), DAY_LENGTH*3652.5],
    [('-0022-01-01', '00:00:00.000', 'Monday', 0.158), MS_PER_CYCLE],
    [('-0029-01-01', '20:43:38.182', 'Monday', 0.158), MS_PER_MARS_YEAR*29], 
]

TEST_DATA_B_MTC_OFF = [
    [('-0001-12-54', '24:39:34.244', 'Friday', 0.172), 1000],
    [('-0001-12-54', '00:39:35.244', 'Friday', 359.673), DAY_LENGTH],
    [('-0001-12-54', '00:00:00.000', 'Friday', 359.659), SOL_LENGTH],
    [('-0001-12-24', '20:27:12.564', 'Wednesday', 344.324), DAY_LENGTH*31],
    [('-0001-12-01', '00:00:00.000', 'Monday', 331.202), SOL_LENGTH*54],
    [('-0001-11-01', '00:00:00.000', 'Monday', 298.154), SOL_LENGTH*110],
    [('-0001-01-01', '00:00:00.000', 'Monday', 359.442), SOL_LENGTH*670],
    [('-0006-09-11', '05:33:12.420', 'Thursday', 232.708), DAY_LENGTH*3652.5],
    [('-0022-01-01', '00:00:00.000', 'Monday', 0.158), MS_PER_CYCLE],
    [('-0029-01-01', '21:17:49.529', 'Monday', 0.158), MS_PER_MARS_YEAR*29], 
]

TEST_DATA_С = [
    [('0111-01-01', '00:00:00.000', 'Monday', 0.177), MS_PER_CYCLE*5],
    [('0265-01-01', '00:00:00.000', 'Monday', 0.193), MS_PER_CYCLE*12],
    [('0375-01-01', '00:00:00.000', 'Monday', 0.203), MS_PER_CYCLE*17],
    [('0639-01-01', '00:00:00.000', 'Monday', 0.198), MS_PER_CYCLE*29],
]

TEST_DATA_D = [
    [('-0110-01-01', '00:00:00.000', 'Monday', 0.143), MS_PER_CYCLE*5],
    [('-0264-01-01', '00:00:00.000', 'Monday', 0.121), MS_PER_CYCLE*12],
    [('-0374-01-01', '00:00:00.000', 'Monday', 0.073), MS_PER_CYCLE*17],
    [('-0638-01-01', '00:00:00.000', 'Monday', 359.967), MS_PER_CYCLE*29],
]


def run_positive_dates():
    for i in range(0, len(TEST_DATA_A_MTC_ON),1):
        timedate0 = datetime.fromisoformat(EPOCH)
        milliseconds_to_add = timedelta(milliseconds=TEST_DATA_A_MTC_ON[i][1])
        timedate1 = timedate0 + milliseconds_to_add
        assert(earth_datetime_to_mars_datetime(timedate1, True)==TEST_DATA_A_MTC_ON[i][0])

    for i in range(0, len(TEST_DATA_A_MTC_OFF),1):
        timedate0 = datetime.fromisoformat(EPOCH)
        milliseconds_to_add = timedelta(milliseconds=TEST_DATA_A_MTC_OFF[i][1])
        timedate1 = timedate0 + milliseconds_to_add
        assert(earth_datetime_to_mars_datetime(timedate1, False)==TEST_DATA_A_MTC_OFF[i][0])

def run_negative_dates():
    for i in range(0, len(TEST_DATA_B_MTC_ON),1):
        timedate0 = datetime.fromisoformat(EPOCH)
        milliseconds_to_sub = timedelta(milliseconds=TEST_DATA_B_MTC_ON[i][1])
        timedate1 = timedate0 - milliseconds_to_sub
        assert(earth_datetime_to_mars_datetime(timedate1, True)==TEST_DATA_B_MTC_ON[i][0])
    for i in range(0, len(TEST_DATA_B_MTC_OFF),1):
        timedate0 = datetime.fromisoformat(EPOCH)
        milliseconds_to_sub = timedelta(milliseconds=TEST_DATA_B_MTC_OFF[i][1])
        timedate1 = timedate0 - milliseconds_to_sub
        assert(earth_datetime_to_mars_datetime(timedate1, False)==TEST_DATA_B_MTC_OFF[i][0])

def run_long_intervals():
    for i in range(0, len(TEST_DATA_С),1):
        timedate0 = datetime.fromisoformat(EPOCH)
        milliseconds_to_add = timedelta(milliseconds=TEST_DATA_С[i][1])
        timedate1 = timedate0 + milliseconds_to_add
        assert(earth_datetime_to_mars_datetime(timedate1, True)==TEST_DATA_С[i][0])
    for i in range(0, len(TEST_DATA_D),1):
        timedate0 = datetime.fromisoformat(EPOCH)
        milliseconds_to_sub = timedelta(milliseconds=TEST_DATA_D[i][1])
        timedate1 = timedate0 - milliseconds_to_sub
        assert(earth_datetime_to_mars_datetime(timedate1, False)==TEST_DATA_D[i][0])

def utc_to_mars_time_test_now():
    # mtc off
    ms_since_unix_epoch = time.time()
    timedate_now = datetime.fromtimestamp(ms_since_unix_epoch,EARTH_TIMEZONE)
    mars_timestamp_a = (earth_datetime_to_mars_datetime_as_string(timedate_now)[:23])
    milliseconds_since_epoch_a = mars_datetime_to_earth_datetime_as_ms(mars_timestamp_a)
    timedate_now_inverse_a = datetime.fromisoformat(EPOCH) + timedelta(milliseconds=milliseconds_since_epoch_a)
    time_diff_a = (timedate_now_inverse_a - timedate_now)
    # should never fail - write to file if does!
    assert(abs(time_diff_a.total_seconds()*1000)<1.0)
    # mtc on
    mars_timestamp_b = (earth_datetime_to_mars_datetime_as_string(timedate_now,True)[:23])
    milliseconds_since_epoch_b = mars_datetime_to_earth_datetime_as_ms(mars_timestamp_b, True)
    timedate_now_inverse_b = datetime.fromisoformat(EPOCH) + timedelta(milliseconds=milliseconds_since_epoch_b)
    time_diff_b = (timedate_now_inverse_b - timedate_now)
    # should never fail - write to file if does!
    assert(abs(time_diff_b.total_seconds()*1000)<1.0)

def main():
    print("Running foundational tests")
    run_positive_dates()
    run_negative_dates()
    run_long_intervals()
    utc_to_mars_time_test_now()
    print("Finished foundational tests")


main()
