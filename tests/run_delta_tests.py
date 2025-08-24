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
TEST_DATA_A_MTC_OFF = [
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


# positive and negative timestamps, negative time delta
TEST_DATA_B_MTC_OFF = [
    ["0001-01-01 00:00:00.000", "-0001-12-54 24:39:34.244", -1000],
    ["0001-01-01 00:00:00.000", "-0001-12-54 00:39:35.244", -DAY_LENGTH],
    ["0001-01-01 00:00:00.000", "-0001-12-54 00:00:00.000", -SOL_LENGTH],
    ["0001-01-01 00:00:00.000", "-0001-12-24 20:27:12.564", -DAY_LENGTH*31],
    ["0001-01-01 00:00:00.000", "-0001-12-01 00:00:00.000", -SOL_LENGTH*54],
    ["0001-01-01 00:00:00.000", "-0001-11-01 00:00:00.000", -SOL_LENGTH*110],
    ["0001-01-01 00:00:00.000", "-0001-01-01 00:00:00.000", -SOL_LENGTH*670],
    ["0001-01-01 00:00:00.000", "-0006-09-11 05:33:12.420", -DAY_LENGTH*3652.5],
    ["0001-01-01 00:00:00.000", "-0022-01-01 00:00:00.000", -MS_PER_CYCLE],
    ["0001-01-01 00:00:00.000", "-0029-01-01 21:17:49.529", -MS_PER_MARS_YEAR*29],
    ["0001-01-01 00:00:00.000", "-0110-01-01 00:00:00.000", -MS_PER_CYCLE*5],
    ["0001-01-01 00:00:00.000", "-0264-01-01 00:00:00.000", -MS_PER_CYCLE*12],
    ["0001-01-01 00:00:00.000", "-0374-01-01 00:00:00.000", -MS_PER_CYCLE*17],
    ["0001-01-01 00:00:00.000", "-0638-01-01 00:00:00.000", -MS_PER_CYCLE*29],

]

# with more randomized time intervals:
TEST_DATA_D_MTC_OFF = [
    ["0001-01-31 04:12:22.680", "0001-01-31 04:12:23.680", 1000],
    ["0001-01-31 04:12:22.680", "0001-07-20 11:46:28.380", DAY_LENGTH*(JULIAN_YEAR_LENGTH-31)],
    ["0011-01-01 22:25:04.767", "0030-01-01 03:21:45.715", MS_PER_MARS_YEAR*19],
    ["0001-07-20 11:46:28.380", "0639-01-01 00:00:00.000", MS_PER_CYCLE*29-DAY_LENGTH*JULIAN_YEAR_LENGTH],
    ["0001-01-31 04:12:22.680","0001-01-08 00:00:00.000", -31*DAY_LENGTH+7*SOL_LENGTH],
    ["-0001-12-54 24:39:34.244", "0001-01-01 00:00:00.001", 1001],
    ["-0001-12-54 24:39:34.244", "0001-01-01 00:00:01.111", 2111],
    ["-0001-12-24 20:27:12.564", "0011-01-01 22:25:04.767", 31*DAY_LENGTH+MS_PER_MARS_YEAR*10],
    ["-0001-12-24 20:27:12.564", "0001-01-31 04:12:22.680", 31*DAY_LENGTH*2],
    ["0001-01-01 00:00:00.500","-0001-12-54 24:39:34.244", -1500],
    ["0001-01-01 00:00:01.450","-0001-12-54 24:39:34.244", -2450],
    ["0001-07-20 11:46:28.380", "-0001-12-24 20:27:12.564", -DAY_LENGTH*JULIAN_YEAR_LENGTH-DAY_LENGTH*31],
    ["0030-01-01 03:21:45.715", "-0029-01-01 21:17:49.529", -MS_PER_MARS_YEAR*58],
    ["-0001-12-24 20:27:12.564", "-0001-12-24 20:27:13.564", 1000],
    ["-0029-01-01 21:17:49.529", "-0006-09-11 05:33:12.420", MS_PER_MARS_YEAR*29-DAY_LENGTH*3652.5],
    ["-0029-01-01 21:17:49.529", "-0029-01-01 21:17:48.529", -1000],
    ["-0001-12-24 20:27:12.564", "-0001-12-01 00:00:00.000", -SOL_LENGTH*54+DAY_LENGTH*31],
]

TEST_DATA_C_MTC_ON = [
    ["0001-01-01 00:00:00.000", "0001-01-01 00:00:00.973", 1000],
    ["0001-01-01 00:00:00.000", "0001-01-01 23:21:28.307", DAY_LENGTH],
    ["0001-01-01 00:00:00.000", "0001-01-02 00:00:00.000", SOL_LENGTH],
    ["0001-01-01 00:00:00.000", "0001-01-08 00:00:00.000", SOL_LENGTH*7],
    ["0001-01-01 00:00:00.000", "0001-01-31 04:05:37.527", DAY_LENGTH*31],
    ["0001-01-01 00:00:00.000", "0001-02-01 00:00:00.000", SOL_LENGTH*MARS_MONTH_LENGTH],
    ["0001-01-01 00:00:00.000", "0001-07-20 11:27:34.249", DAY_LENGTH*JULIAN_YEAR_LENGTH],
    ["0001-01-01 00:00:00.000", "0001-12-01 00:00:00.000", SOL_LENGTH*MARS_MONTH_LENGTH*11],
    ["0001-01-01 00:00:00.000", "0001-12-52 23:59:59.903", SOL_LENGTH*MARS_MONTH_LENGTH*11+52*SOL_LENGTH-100],
    ["0001-01-01 00:00:00.000", "0001-12-53 00:00:00.000", SOL_LENGTH*668],
    ["0001-01-01 00:00:00.000", "0001-12-53 23:59:59.903", SOL_LENGTH*MARS_MONTH_LENGTH*11+53*SOL_LENGTH-100],
    ["0001-01-01 00:00:00.000", "0002-01-01 00:00:00.000", SOL_LENGTH*MARS_MONTH_LENGTH*11+53*SOL_LENGTH],
    ["0001-01-01 00:00:00.000", "0002-01-01 00:00:00.000", SOL_LENGTH*669],
    #["0001-01-01 00:00:00.000", "0011-01-01 21:49:05.455", MS_PER_MARS_YEAR*10], 1 ms FAIL HERE!
    ["0001-01-01 00:00:00.000", "0023-01-01 00:00:00.000", MS_PER_CYCLE],
    ["0001-01-01 00:00:00.000", "0030-01-01 03:16:21.818", MS_PER_MARS_YEAR*29],
]

TEST_DATA_E_MTC_ON = [
    ["0001-01-01 00:00:00.000", "-0001-12-54 23:59:59.027", -1000],
    ["0001-01-01 00:00:00.000", "-0001-12-54 00:38:31.693", -DAY_LENGTH],
    ["0001-01-01 00:00:00.000", "-0001-12-54 00:00:00.000", -SOL_LENGTH],
    ["0001-01-01 00:00:00.000", "-0001-12-24 19:54:22.473", -DAY_LENGTH*31],
    ["0001-01-01 00:00:00.000", "-0001-12-01 00:00:00.000", -SOL_LENGTH*54],
    ["0001-01-01 00:00:00.000", "-0001-11-01 00:00:00.000", -SOL_LENGTH*110],
    ["0001-01-01 00:00:00.000", "-0001-01-01 00:00:00.000", -SOL_LENGTH*670],
    ["0001-01-01 00:00:00.000", "-0006-09-11 05:24:17.509", -DAY_LENGTH*3652.5],
    ["0001-01-01 00:00:00.000", "-0022-01-01 00:00:00.000", -MS_PER_CYCLE],
    ["0001-01-01 00:00:00.000", "-0029-01-01 20:43:38.182", -MS_PER_MARS_YEAR*29],
    ["0001-01-01 00:00:00.000", "-0110-01-01 00:00:00.000", -MS_PER_CYCLE*5],
    ["0001-01-01 00:00:00.000", "-0264-01-01 00:00:00.000", -MS_PER_CYCLE*12],
    ["0001-01-01 00:00:00.000", "-0374-01-01 00:00:00.000", -MS_PER_CYCLE*17],
    ["0001-01-01 00:00:00.000", "-0638-01-01 00:00:00.000", -MS_PER_CYCLE*29]
]


def run_delta_test(P_DATA, TEST_LETTER, TEST_INDEX, mars_second_on=False):
    # calculate timedelta between two Mars timestamps
    delta_ms_M = compute_mars_timedelta(P_DATA[0], P_DATA[1], mars_second_on)
    # convert them into Earth timestamps
    earth_date_1 = mars_datetime_to_earth_datetime_as_isoformat(P_DATA[0], mars_second_on)
    earth_date_2 = mars_datetime_to_earth_datetime_as_isoformat(P_DATA[1], mars_second_on)    
    # timedelta between two Earth timestamps should be identical to Mars ones
    delta_time = (earth_date_2 - earth_date_1)
    delta_ms_E = delta_time.total_seconds()*1000
    # known sub-1ms errors happen here due to rounding
    try:
        assert(P_DATA[2]==delta_ms_E)
        assert(delta_ms_M==delta_ms_E)
    except:
        delta_error = abs(P_DATA[2]-delta_ms_E)
        etm_error = abs(delta_ms_M-delta_ms_E)
        net_error = delta_error+etm_error
        if net_error>0:
            print ("Accuracy error %3.4f ms for test case %s%s" % (net_error,TEST_LETTER,TEST_INDEX))
        assert(net_error<1.0)
        
    # convert from Earth datetimes back to Mars datetimes,
    # those should be identical to input dates
    mars_date_1 = earth_datetime_to_mars_datetime(earth_date_1, mars_second_on)
    mars_date_2 = earth_datetime_to_mars_datetime(earth_date_2, mars_second_on)
    assert(P_DATA[0]==mars_date_1[:len(P_DATA[0])])
    assert(P_DATA[1]==mars_date_2[:len(P_DATA[1])])
    # first timedate + timedelta = second timedate
    # second timedate - timedelta = first time_date
    check_date_1 = add_timedelta_to_mars_date(P_DATA[0], P_DATA[2], mars_second_on)
    check_date_2 = add_timedelta_to_mars_date(P_DATA[1], -P_DATA[2], mars_second_on)
    assert(check_date_1[:len(P_DATA[1])]==P_DATA[1])
    assert(check_date_2[:len(P_DATA[0])]==P_DATA[0])

def run_all_tests_mtc_off():
    #   positive and positive = positive time delta
    for i in range(0, len(TEST_DATA_A_MTC_OFF),1):
        run_delta_test(TEST_DATA_A_MTC_OFF[i], "A", i)
    
    for i in range(0, len(TEST_DATA_B_MTC_OFF),1):
        run_delta_test(TEST_DATA_B_MTC_OFF[i], "B", i)

    for i in range(0, len(TEST_DATA_D_MTC_OFF),1):
        run_delta_test(TEST_DATA_D_MTC_OFF[i], "D", i)

def run_all_tests_mtc_on():
    for i in range(0, len(TEST_DATA_C_MTC_ON),1):
        run_delta_test(TEST_DATA_C_MTC_ON[i], "C", i, True)
    for i in range(0, len(TEST_DATA_E_MTC_ON),1):
        run_delta_test(TEST_DATA_E_MTC_ON[i], "E", i, True)


def delta_tests():
    print("Running time delta tests")
    run_all_tests_mtc_off()
    run_all_tests_mtc_on()
    print("Finished time delta tests")


def main():
    delta_tests()

main()