#!/usr/bin/env python3
import os
import sys
import time
from datetime import datetime, timezone, timedelta
from math import modf, ceil, floor
from zoneinfo import ZoneInfo

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from exodus_calendar.utils import compute_mars_timedelta, mars_datetime_to_earth_datetime_as_isoformat, add_timedelta_to_mars_date, earth_datetime_to_mars_datetime
from exodus_calendar.utils import DAY_LENGTH, SOL_LENGTH, EPOCH, JULIAN_YEAR_LENGTH, DAY_LENGTH, MS_PER_MARS_YEAR, MARS_MONTH_LENGTH, MS_PER_CYCLE

EARTH_TIMEZONE = ZoneInfo("UTC")

# run test cases: 
#   positive and negative = negative time delta
#   positive and negative = positive time delta
#   negative and negative = positive time delta
#   negative and negative = negative time delta
TEST_DATA_A_MTC_OFF = [
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
    ["0001-01-01 00:00:00.000", "0001-07-20 11:46:28.380", DAY_LENGTH*JULIAN_YEAR_LENGTH],
    ["0001-01-01 00:00:00.000", "0001-12-53 00:00:00.000", SOL_LENGTH*668],
    ["0001-01-01 00:00:00.000", "0002-01-01 00:00:00.000", SOL_LENGTH*669],
    ["0001-01-01 00:00:00.000", "0011-01-01 22:25:04.767", MS_PER_MARS_YEAR*10], #<1ms error here
    ["0001-01-01 00:00:00.000", "0023-01-01 00:00:00.000", MS_PER_CYCLE],
    ["0001-01-01 00:00:00.000", "0030-01-01 03:21:45.715", MS_PER_MARS_YEAR*29], #<1ms error here
    ["0001-01-01 00:00:00.000", "0111-01-01 00:00:00.000", MS_PER_CYCLE*5],
    ["0001-01-01 00:00:00.000", "0265-01-01 00:00:00.000", MS_PER_CYCLE*12],
    ["0001-01-01 00:00:00.000", "0375-01-01 00:00:00.000", MS_PER_CYCLE*17],
    ["0001-01-01 00:00:00.000", "0639-01-01 00:00:00.000", MS_PER_CYCLE*29],
]

TEST_DATA_B_MTC_OFF = [
    ["0001-01-01 00:00:00.000", "-0001-12-54 24:39:34.244", -1000],
    ["0001-01-01 00:00:00.000", "-0001-12-54 00:39:35.244", -DAY_LENGTH],
    ["0001-01-01 00:00:00.000", "-0001-12-54 00:00:00.000", -SOL_LENGTH],
]

TEST_DATA_C_MTC_OFF = [
    ["-0001-12-54 24:39:34.244", "0001-01-01 00:00:00.000",  1000]
]

# more randomized start time
TEST_DATA_D_MTC_OFF = [
    ["0001-01-31 04:12:22.680", "0001-01-31 04:12:23.680", 1000],
    ["0001-07-20 11:46:28.380", "0001-07-20 11:46:29.380", 1000],
    ["0011-01-01 22:25:04.767", "0011-01-01 22:25:05.767", 1000],
    ["0030-01-01 03:21:45.715", "0030-01-01 03:21:46.715", 1000]
]


def run_delta_test(P_DATA):
    # calculate timedelta between two Mars timestamps
    # convert them into Earth timestamps
    delta_ms_M = compute_mars_timedelta(P_DATA[0], P_DATA[1])
    earth_date_1 = mars_datetime_to_earth_datetime_as_isoformat(P_DATA[0], False)
    earth_date_2 = mars_datetime_to_earth_datetime_as_isoformat(P_DATA[1], False)
        
    # timedelta between two Earth timestamps should be identical to Mars
    delta_time = (earth_date_2 - earth_date_1)
    delta_ms_E = (delta_time.total_seconds()*1000)
    try:
        assert(P_DATA[2]==delta_ms_E)
    except:
        delta_error = abs(P_DATA[2]-delta_ms_E)
        print ("Accuracy error: %3.4f ms for %s test case" % (delta_error,P_DATA[1]))
        assert(delta_error<1.0)
    assert(delta_ms_M==delta_ms_E)
        
    # convert from Earth datetimes back to Mars datetimes,
    # those should be identical to input dates
    mars_date_1 = earth_datetime_to_mars_datetime(earth_date_1)
    mars_date_2 = earth_datetime_to_mars_datetime(earth_date_2)
    assert(P_DATA[0]==mars_date_1[:len(P_DATA[0])])
    assert(P_DATA[1]==mars_date_2[:len(P_DATA[1])])
        
    # first timedate + timedelta = second timedate
    # second timedate - timedelta = first time_date
    check_date_1 = add_timedelta_to_mars_date(P_DATA[0], P_DATA[2])
    check_date_2 = add_timedelta_to_mars_date(P_DATA[1], -P_DATA[2])
    assert(check_date_1[:len(P_DATA[1])]==P_DATA[1])
    assert(check_date_2[:len(P_DATA[0])]==P_DATA[0])

def run_all_tests_mtc_off():
    #   positive and positive = positive time delta
    for i in range(0, len(TEST_DATA_A_MTC_OFF),1):
        run_delta_test(TEST_DATA_A_MTC_OFF[i])
    
    for i in range(0, len(TEST_DATA_B_MTC_OFF),1):
        run_delta_test(TEST_DATA_B_MTC_OFF[i])

    for i in range(0, len(TEST_DATA_C_MTC_OFF),1):
        run_delta_test(TEST_DATA_C_MTC_OFF[i])

    for i in range(0, len(TEST_DATA_D_MTC_OFF),1):
        run_delta_test(TEST_DATA_D_MTC_OFF[i])


def delta_tests():
    print("Running time delta tests")
    run_all_tests_mtc_off()
    print("Finished time delta tests")


def main():
    delta_tests()

main()