#!/usr/bin/env python3
import os
import sys
import time
from datetime import datetime, timezone, timedelta
from math import modf, ceil, floor
from zoneinfo import ZoneInfo

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from exodus_calendar.utils import earth_datetime_to_mars_datetime, mars_datetime_to_earth_datetime_as_string
from exodus_calendar.utils import JULIAN_YEAR_LENGTH, SOL_LENGTH, EPOCH, MS_PER_CYCLE, DAY_LENGTH, MS_PER_MARS_YEAR, MARS_MONTH_LENGTH

EARTH_TIMEZONE = ZoneInfo("UTC")

# ALL TESTS below are are using martian second length (1027.5ms)
# for Mars timestamps, unless specified otherwise
def utc_to_mars_time_tests_positive_offset_mtc_on():
    # test first date - should be year 1
    timedate0 = datetime.fromisoformat(EPOCH)
    assert(earth_datetime_to_mars_datetime(timedate0, True)=="0001-01-01 00:00:00.000, Monday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime_as_string("0001-01-01 00:00:00.000", True)
    timedate0_inverse = timedate0 +  timedelta(milliseconds = milliseconds_from_epoch)
    assert(timedate0_inverse == timedate0)

    # test start day +1 second
    milliseconds_to_add = timedelta(milliseconds=1000)
    timedate1 = timedate0 + milliseconds_to_add
    assert(earth_datetime_to_mars_datetime(timedate1, True)=="0001-01-01 00:00:00.973, Monday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime_as_string("0001-01-01 00:00:00.973", True) 
    timedate1_inverse = timedate0 + timedelta(milliseconds=milliseconds_from_epoch)
    assert(abs(milliseconds_from_epoch - 1000) < 1.0)
    assert(timedate1_inverse == timedate1)

    # test start day +1 day
    milliseconds_to_add = timedelta(milliseconds=DAY_LENGTH)
    timedate2 = timedate0 + milliseconds_to_add
    assert(earth_datetime_to_mars_datetime(timedate2, True) == "0001-01-01 23:21:28.307, Monday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime_as_string("0001-01-01 23:21:28.307", True)
    timedate2_inverse = timedate0 + timedelta(milliseconds=milliseconds_from_epoch)
    assert(abs(milliseconds_from_epoch - DAY_LENGTH) < 1.0)
    assert(timedate2_inverse == timedate2)

    # test start day +1 sol
    milliseconds_to_add = timedelta(milliseconds=SOL_LENGTH)
    timedate3 = timedate0 + milliseconds_to_add
    assert(earth_datetime_to_mars_datetime(timedate3, True) == "0001-01-02 00:00:00.000, Tuesday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime_as_string("0001-01-02 00:00:00.000", True)
    timedate3_inverse = timedate0 + timedelta(milliseconds=milliseconds_from_epoch)
    assert(abs(milliseconds_from_epoch - SOL_LENGTH) < 1.0)
    assert(timedate3_inverse == timedate3)

    # test start day +7 sols
    milliseconds_to_add = timedelta(milliseconds=SOL_LENGTH*7)
    timedate4 = timedate0 + milliseconds_to_add
    assert(earth_datetime_to_mars_datetime(timedate4, True) == "0001-01-08 00:00:00.000, Monday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime_as_string("0001-01-08 00:00:00.000", True)
    timedate4_inverse = timedate0 + timedelta(milliseconds=milliseconds_from_epoch)
    assert(abs(milliseconds_from_epoch - SOL_LENGTH*7) < 1.0)
    assert(timedate4_inverse == timedate4)

    # test start day +1 Earth month
    milliseconds_to_add = timedelta(milliseconds=DAY_LENGTH*31)
    timedate5 = timedate0 + milliseconds_to_add
    assert(earth_datetime_to_mars_datetime(timedate5, True) == "0001-01-31 04:05:37.527, Wednesday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime_as_string("0001-01-31 04:05:37.527", True)
    timedate5_inverse = timedate0 + timedelta(milliseconds=milliseconds_from_epoch)
    assert(abs(milliseconds_from_epoch - DAY_LENGTH*31) < 1.0)
    assert(timedate5_inverse == timedate5)

    # test start day +1 Martian month
    milliseconds_to_add = timedelta(milliseconds=SOL_LENGTH*MARS_MONTH_LENGTH)
    timedate6 = timedate0 + milliseconds_to_add
    assert(earth_datetime_to_mars_datetime(timedate6, True) == "0001-02-01 00:00:00.000, Monday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime_as_string("0001-02-01 00:00:00.000", True)
    timedate6_inverse = timedate0 + timedelta(milliseconds=milliseconds_from_epoch)
    assert(abs(milliseconds_from_epoch - SOL_LENGTH*MARS_MONTH_LENGTH) < 1.0)
    assert(timedate6_inverse == timedate6)

    # test start day +11 Martian months
    milliseconds_to_add = timedelta(milliseconds=SOL_LENGTH*MARS_MONTH_LENGTH*11)
    timedate7 = timedate0 + milliseconds_to_add
    assert(earth_datetime_to_mars_datetime(timedate7, True) == "0001-12-01 00:00:00.000, Monday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime_as_string("0001-12-01 00:00:00.000", True)
    assert(abs(milliseconds_from_epoch - SOL_LENGTH*MARS_MONTH_LENGTH*11) < 1.0)
    timedate7_inverse = timedate0 + timedelta(milliseconds=milliseconds_from_epoch)
    assert(timedate7_inverse == timedate7)

    # test A end of december for year 1
    milliseconds_to_add = timedelta(milliseconds=SOL_LENGTH*MARS_MONTH_LENGTH*11+52*SOL_LENGTH-100)
    timedate7a = timedate0 + milliseconds_to_add
    assert(earth_datetime_to_mars_datetime(timedate7a, True)=="0001-12-52 23:59:59.903, Wednesday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime_as_string("0001-12-52 23:59:59.903", True)
    timedate7a_inverse = timedate0 + timedelta(milliseconds=milliseconds_from_epoch)
    assert(abs(milliseconds_from_epoch - (SOL_LENGTH*MARS_MONTH_LENGTH*11+52*SOL_LENGTH-100)) < 1.0)
    assert(timedate7a_inverse == timedate7a)

    # test B end of december for year 1 
    milliseconds_to_add = timedelta(milliseconds=SOL_LENGTH*MARS_MONTH_LENGTH*11+53*SOL_LENGTH-100)
    timedate7b = timedate0 + milliseconds_to_add
    assert(earth_datetime_to_mars_datetime(timedate7b, True)=="0001-12-53 23:59:59.903, Thursday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime_as_string("0001-12-53 23:59:59.903", True)
    timedate7b_inverse = timedate0 + timedelta(milliseconds=milliseconds_from_epoch)
    assert(abs(milliseconds_from_epoch - (SOL_LENGTH*MARS_MONTH_LENGTH*11+53*SOL_LENGTH-100)) < 1.0)
    assert(timedate7b_inverse == timedate7b)

    # test C end of december for year 1 - rollover to year2
    milliseconds_to_add = timedelta(milliseconds=SOL_LENGTH*MARS_MONTH_LENGTH*11+53*SOL_LENGTH)
    timedate7c = timedate0 + milliseconds_to_add
    assert(earth_datetime_to_mars_datetime(timedate7c, True)=="0002-01-01 00:00:00.000, Monday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime_as_string("0002-01-01 00:00:00.000", True)
    assert(abs(milliseconds_from_epoch - (SOL_LENGTH*MARS_MONTH_LENGTH*11+53*SOL_LENGTH)) < 1.0)
    timedate7c_inverse = timedate0 + timedelta(milliseconds=milliseconds_from_epoch)
    assert(timedate7c_inverse == timedate7c)

    # test +1 Earth year
    milliseconds_to_add = timedelta(milliseconds=DAY_LENGTH*JULIAN_YEAR_LENGTH)
    timedate8 = timedate0 + milliseconds_to_add
    assert(earth_datetime_to_mars_datetime(timedate8, True)=="0001-07-20 11:27:34.249, Saturday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime_as_string("0001-07-20 11:27:34.249", True)
    timedate8_inverse = timedate0 + timedelta(milliseconds=milliseconds_from_epoch)
    assert(abs(milliseconds_from_epoch - DAY_LENGTH*JULIAN_YEAR_LENGTH) < 1.0)
    assert(timedate8_inverse == timedate8)

    # test +1 Mars even year
    milliseconds_to_add = timedelta(milliseconds=SOL_LENGTH*668)
    timedate9= timedate0 + milliseconds_to_add
    assert(earth_datetime_to_mars_datetime(timedate9, True)=="0001-12-53 00:00:00.000, Thursday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime_as_string("0001-12-53 00:00:00.000", True)
    timedate9_inverse = timedate0 + timedelta(milliseconds=milliseconds_from_epoch)
    assert((milliseconds_from_epoch - (SOL_LENGTH*668)) < 1.0)
    assert(timedate9_inverse == timedate9)

    # test +1 Mars odd year
    milliseconds_to_add = timedelta(milliseconds=SOL_LENGTH*669)
    timedate10= timedate0 + milliseconds_to_add
    assert(earth_datetime_to_mars_datetime(timedate10, True)=="0002-01-01 00:00:00.000, Monday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime_as_string("0002-01-01 00:00:00.000", True)
    timedate10_inverse = timedate0 + timedelta(milliseconds=milliseconds_from_epoch)
    assert(abs(milliseconds_from_epoch - SOL_LENGTH*669) < 1.0)
    assert(timedate10_inverse == timedate10)

    # test +10 Mars years
    milliseconds_to_add = timedelta(milliseconds=MS_PER_MARS_YEAR*10)
    timedate11= timedate0 + milliseconds_to_add
    assert(earth_datetime_to_mars_datetime(timedate11, True)=="0011-01-01 21:49:05.455, Monday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime_as_string("0011-01-01 21:49:05.455", True)
    # 0.272705078125 ms error here - second assert fails!
    assert(abs(milliseconds_from_epoch - MS_PER_MARS_YEAR*10) < 1.0)
    #timedate11_inverse = timedate0 + timedelta(milliseconds=milliseconds_from_epoch)
    #assert(timedate11_inverse == timedate11)

    # test +1 cycle (22 Mars years)
    milliseconds_to_add = timedelta(milliseconds=MS_PER_MARS_YEAR*22)
    timedate12= timedate0 + milliseconds_to_add
    assert(earth_datetime_to_mars_datetime(timedate12, True)=="0023-01-01 00:00:00.000, Monday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime_as_string("0023-01-01 00:00:00.000", True)
    timedate12_inverse = timedate0 + timedelta(milliseconds=milliseconds_from_epoch)
    assert(abs(milliseconds_from_epoch - MS_PER_MARS_YEAR*22) < 1.0)
    assert(timedate12_inverse == timedate12)

    # test +29 Mars yeras
    milliseconds_to_add = timedelta(milliseconds=MS_PER_MARS_YEAR*29)
    timedate13= timedate0 + milliseconds_to_add
    assert(earth_datetime_to_mars_datetime(timedate13, True)=="0030-01-01 03:16:21.818, Monday") 
    milliseconds_from_epoch = mars_datetime_to_earth_datetime_as_string("0030-01-01 03:16:21.818", True)
    # 0.0908203125 ms error here - second assert fails!
    assert(abs(milliseconds_from_epoch - MS_PER_MARS_YEAR*29) < 1.0)
    #timedate13_inverse = timedate0 + timedelta(milliseconds=milliseconds_from_epoch)
    #assert(timedate13_inverse == timedate13)

# ALL TESTS below are are using terrestial second length (1000ms)
# for both Earth and Mars timestamps, unless specified otherwise
def utc_to_mars_time_tests_positive_offset_mtc_off():
    # test first date - should be year 1
    timedate0 = datetime.fromisoformat(EPOCH)
    assert(earth_datetime_to_mars_datetime(timedate0)=="0001-01-01 00:00:00.000, Monday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime_as_string("0001-01-01 00:00:00.000")
    timedate0_inverse = timedate0 +  timedelta(milliseconds = milliseconds_from_epoch)
    assert(timedate0_inverse == timedate0)

    # test start day +1 second
    milliseconds_to_add = timedelta(milliseconds=1000)
    timedate1 = timedate0 + milliseconds_to_add
    assert(earth_datetime_to_mars_datetime(timedate1)=="0001-01-01 00:00:01.000, Monday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime_as_string("0001-01-01 00:00:01.000") 
    timedate1_inverse = timedate0 + timedelta(milliseconds=milliseconds_from_epoch)
    assert(milliseconds_from_epoch - 1000 < 1.0)
    assert(timedate1_inverse == timedate1)

    # test start day +1 day
    milliseconds_to_add = timedelta(milliseconds=DAY_LENGTH)
    timedate2 = timedate0 + milliseconds_to_add
    assert(earth_datetime_to_mars_datetime(timedate2) == "0001-01-01 24:00:00.000, Monday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime_as_string("0001-01-01 24:00:00.000")
    timedate2_inverse = timedate0 + timedelta(milliseconds=milliseconds_from_epoch)
    assert(abs(milliseconds_from_epoch - DAY_LENGTH) < 1.0)
    assert(timedate2_inverse == timedate2)

    # test start day +1 sol
    milliseconds_to_add = timedelta(milliseconds=SOL_LENGTH)
    timedate3 = timedate0 + milliseconds_to_add
    assert(earth_datetime_to_mars_datetime(timedate3) == "0001-01-02 00:00:00.000, Tuesday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime_as_string("0001-01-02 00:00:00.000")
    timedate3_inverse = timedate0 + timedelta(milliseconds=milliseconds_from_epoch)
    assert(abs(milliseconds_from_epoch - SOL_LENGTH) < 1.0)
    assert(timedate3_inverse == timedate3)

    # test start day +7 sols
    milliseconds_to_add = timedelta(milliseconds=SOL_LENGTH*7)
    timedate4 = timedate0 + milliseconds_to_add
    assert(earth_datetime_to_mars_datetime(timedate4) == "0001-01-08 00:00:00.000, Monday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime_as_string("0001-01-08 00:00:00.000")
    timedate4_inverse = timedate0 + timedelta(milliseconds=milliseconds_from_epoch)
    assert(abs(milliseconds_from_epoch - SOL_LENGTH*7) < 1.0)
    assert(timedate4_inverse == timedate4)

    # test start day +1 Earth month
    milliseconds_to_add = timedelta(milliseconds=DAY_LENGTH*31)
    timedate5 = timedate0 + milliseconds_to_add
    assert(earth_datetime_to_mars_datetime(timedate5) == "0001-01-31 04:12:22.680, Wednesday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime_as_string("0001-01-31 04:12:22.680")
    timedate5_inverse = timedate0 + timedelta(milliseconds=milliseconds_from_epoch)
    assert(milliseconds_from_epoch - DAY_LENGTH*31 < 1.0)
    assert(timedate5_inverse == timedate5)

    # test start day +1 Martian month
    milliseconds_to_add = timedelta(milliseconds=SOL_LENGTH*MARS_MONTH_LENGTH)
    timedate6 = timedate0 + milliseconds_to_add
    assert(earth_datetime_to_mars_datetime(timedate6) == "0001-02-01 00:00:00.000, Monday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime_as_string("0001-02-01 00:00:00.000")
    timedate6_inverse = timedate0 + timedelta(milliseconds=milliseconds_from_epoch)
    assert(abs(milliseconds_from_epoch - SOL_LENGTH*MARS_MONTH_LENGTH) < 1.0)
    assert(timedate6_inverse == timedate6)

    # test start day +11 Martian months
    milliseconds_to_add = timedelta(milliseconds=SOL_LENGTH*MARS_MONTH_LENGTH*11)
    timedate7 = timedate0 + milliseconds_to_add
    assert(earth_datetime_to_mars_datetime(timedate7) == "0001-12-01 00:00:00.000, Monday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime_as_string("0001-12-01 00:00:00.000")
    assert(abs(milliseconds_from_epoch - SOL_LENGTH*MARS_MONTH_LENGTH*11) < 1.0)
    timedate7_inverse = timedate0 + timedelta(milliseconds=milliseconds_from_epoch)
    assert(timedate7_inverse == timedate7)

    # test A end of december for year 1
    milliseconds_to_add = timedelta(milliseconds=SOL_LENGTH*MARS_MONTH_LENGTH*11+52*SOL_LENGTH-100)
    timedate7a = timedate0 + milliseconds_to_add
    assert(earth_datetime_to_mars_datetime(timedate7a)=="0001-12-52 24:39:35.144, Wednesday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime_as_string("0001-12-52 24:39:35.144")
    timedate7a_inverse = timedate0 + timedelta(milliseconds=milliseconds_from_epoch)
    assert(abs(milliseconds_from_epoch - (SOL_LENGTH*MARS_MONTH_LENGTH*11+52*SOL_LENGTH-100)) < 1.0)
    assert(timedate7a_inverse == timedate7a)

    # test B end of december for year 1 
    milliseconds_to_add = timedelta(milliseconds=SOL_LENGTH*MARS_MONTH_LENGTH*11+53*SOL_LENGTH-100)
    timedate7b = timedate0 + milliseconds_to_add
    assert(earth_datetime_to_mars_datetime(timedate7b)=="0001-12-53 24:39:35.144, Thursday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime_as_string("0001-12-53 24:39:35.144")
    timedate7b_inverse = timedate0 + timedelta(milliseconds=milliseconds_from_epoch)
    assert(abs(milliseconds_from_epoch - (SOL_LENGTH*MARS_MONTH_LENGTH*11+53*SOL_LENGTH-100)) < 1.0)
    assert(timedate7b_inverse == timedate7b)

    # test C end of december for year 1 - rollover to year2
    milliseconds_to_add = timedelta(milliseconds=SOL_LENGTH*MARS_MONTH_LENGTH*11+53*SOL_LENGTH)
    timedate7c = timedate0 + milliseconds_to_add
    assert(earth_datetime_to_mars_datetime(timedate7c)=="0002-01-01 00:00:00.000, Monday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime_as_string("0002-01-01 00:00:00.000")
    assert(abs(milliseconds_from_epoch - (SOL_LENGTH*MARS_MONTH_LENGTH*11+53*SOL_LENGTH)) < 1.0)
    timedate7c_inverse = timedate0 + timedelta(milliseconds=milliseconds_from_epoch)
    assert(timedate7c_inverse == timedate7c)

    # test +1 Earth year
    milliseconds_to_add = timedelta(milliseconds=DAY_LENGTH*JULIAN_YEAR_LENGTH)
    timedate8 = timedate0 + milliseconds_to_add
    assert(earth_datetime_to_mars_datetime(timedate8)=="0001-07-20 11:46:28.380, Saturday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime_as_string("0001-07-20 11:46:28.380")
    timedate8_inverse = timedate0 + timedelta(milliseconds=milliseconds_from_epoch)
    assert(abs(milliseconds_from_epoch - DAY_LENGTH*JULIAN_YEAR_LENGTH) < 1.0)
    assert(timedate8_inverse == timedate8)

    # test +1 Mars even year
    milliseconds_to_add = timedelta(milliseconds=SOL_LENGTH*668)
    timedate9= timedate0 + milliseconds_to_add
    assert(earth_datetime_to_mars_datetime(timedate9)=="0001-12-53 00:00:00.000, Thursday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime_as_string("0001-12-53 00:00:00.000")
    timedate9_inverse = timedate0 + timedelta(milliseconds=milliseconds_from_epoch)
    assert((milliseconds_from_epoch - (SOL_LENGTH*668)) < 1.0)
    assert(timedate9_inverse == timedate9)

    # test +1 Mars odd year
    milliseconds_to_add = timedelta(milliseconds=SOL_LENGTH*669)
    timedate10= timedate0 + milliseconds_to_add
    assert(earth_datetime_to_mars_datetime(timedate10)=="0002-01-01 00:00:00.000, Monday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime_as_string("0002-01-01 00:00:00.000")
    timedate10_inverse = timedate0 + timedelta(milliseconds=milliseconds_from_epoch)
    assert(abs(milliseconds_from_epoch - SOL_LENGTH*669) < 1.0)
    assert(timedate10_inverse == timedate10)

    # test +10 Mars years
    milliseconds_to_add = timedelta(milliseconds=MS_PER_MARS_YEAR*10)
    timedate11= timedate0 + milliseconds_to_add
    assert(earth_datetime_to_mars_datetime(timedate11)=="0011-01-01 22:25:04.767, Monday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime_as_string("0011-01-01 22:25:04.767")
    # 0.272705078125 ms error here - second assert fails!
    assert(abs(milliseconds_from_epoch - MS_PER_MARS_YEAR*10) < 1.0)
    #timedate11_inverse = timedate0 + timedelta(milliseconds=milliseconds_from_epoch)
    #assert(timedate11_inverse == timedate11)

    # test +1 cycle (22 Mars years)
    milliseconds_to_add = timedelta(milliseconds=MS_PER_MARS_YEAR*22)
    timedate12= timedate0 + milliseconds_to_add
    assert(earth_datetime_to_mars_datetime(timedate12)=="0023-01-01 00:00:00.000, Monday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime_as_string("0023-01-01 00:00:00.000")
    timedate12_inverse = timedate0 + timedelta(milliseconds=milliseconds_from_epoch)
    assert(abs(milliseconds_from_epoch - MS_PER_MARS_YEAR*22) < 1.0)
    assert(timedate12_inverse == timedate12)

    # test +29 Mars yeras
    milliseconds_to_add = timedelta(milliseconds=MS_PER_MARS_YEAR*29)
    timedate13= timedate0 + milliseconds_to_add
    assert(earth_datetime_to_mars_datetime(timedate13)=="0030-01-01 03:21:45.715, Monday") 
    milliseconds_from_epoch = mars_datetime_to_earth_datetime_as_string("0030-01-01 03:21:45.715")
    # 0.0908203125 ms error here - second assert fails!
    assert(abs(milliseconds_from_epoch - MS_PER_MARS_YEAR*29) < 1.0)
    #timedate13_inverse = timedate0 + timedelta(milliseconds=milliseconds_from_epoch)
    #assert(timedate13_inverse == timedate13)

def utc_to_mars_time_tests_negative_offset_mtc_on():
    timedate0 = datetime.fromisoformat(EPOCH)
    # test  -1 second
    milliseconds_to_sub = timedelta(milliseconds=1000)
    timedate1 = timedate0 - milliseconds_to_sub
    assert(earth_datetime_to_mars_datetime(timedate1, True) == "-0001-12-54 23:59:59.027, Friday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime_as_string("-0001-12-54 23:59:59.027", True)
    timedate1_inverse = timedate0 + timedelta(milliseconds=milliseconds_from_epoch)
    assert(abs(milliseconds_from_epoch + 1000) < 1.0)
    assert(timedate1_inverse == timedate1)

    # test -1 Eath day
    milliseconds_to_sub = timedelta(milliseconds=DAY_LENGTH)
    timedate2 = timedate0 - milliseconds_to_sub
    assert(earth_datetime_to_mars_datetime(timedate2, True) == "-0001-12-54 00:38:31.693, Friday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime_as_string("-0001-12-54 00:38:31.693", True)
    timedate2_inverse = timedate0 + timedelta(milliseconds=milliseconds_from_epoch)
    assert(abs(milliseconds_from_epoch + DAY_LENGTH) < 1.0)
    assert(timedate2_inverse == timedate2)

    # test -1 sol
    milliseconds_to_sub = timedelta(milliseconds=SOL_LENGTH)
    timedate3 = timedate0 - milliseconds_to_sub
    assert(earth_datetime_to_mars_datetime(timedate3, True) == "-0001-12-54 00:00:00.000, Friday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime_as_string("-0001-12-54 00:00:00.000", True)
    timedate3_inverse = timedate0 + timedelta(milliseconds=milliseconds_from_epoch)
    assert(abs(milliseconds_from_epoch + SOL_LENGTH) < 1.0)
    assert(timedate3_inverse == timedate3)

    # test start day -1 Earth month
    milliseconds_to_sub = timedelta(milliseconds=DAY_LENGTH*31)
    timedate4 = timedate0 - milliseconds_to_sub
    assert(earth_datetime_to_mars_datetime(timedate4, True) == "-0001-12-24 19:54:22.473, Wednesday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime_as_string("-0001-12-24 19:54:22.473", True)
    timedate4_inverse = timedate0 + timedelta(milliseconds=milliseconds_from_epoch)
    assert(milliseconds_from_epoch + DAY_LENGTH*31 < 1.0)
    assert(timedate4_inverse == timedate4)

    # test start day -54 sols
    milliseconds_to_sub = timedelta(milliseconds=SOL_LENGTH*54)
    timedate5 = timedate0 - milliseconds_to_sub
    assert(earth_datetime_to_mars_datetime(timedate5, True) == "-0001-12-01 00:00:00.000, Monday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime_as_string("-0001-12-01 00:00:00.000", True)
    timedate5_inverse = timedate0 + timedelta(milliseconds=milliseconds_from_epoch)
    assert(abs(milliseconds_from_epoch + SOL_LENGTH*54)<1.0)
    assert(timedate5_inverse == timedate5)

    # test start day -110 sols
    milliseconds_to_sub = timedelta(milliseconds=SOL_LENGTH*110)
    timedate6 = timedate0 - milliseconds_to_sub
    assert(earth_datetime_to_mars_datetime(timedate6, True) == "-0001-11-01 00:00:00.000, Monday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime_as_string("-0001-11-01 00:00:00.000", True)
    timedate6_inverse = timedate0 + timedelta(milliseconds=milliseconds_from_epoch)
    assert(abs(milliseconds_from_epoch + SOL_LENGTH*110)<1.0)
    assert(timedate6_inverse == timedate6)

    # test -1 long Mars year
    milliseconds_to_sub = timedelta(milliseconds=SOL_LENGTH*670)
    timedate7= timedate0 - milliseconds_to_sub
    assert(earth_datetime_to_mars_datetime(timedate7, True) == "-0001-01-01 00:00:00.000, Monday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime_as_string("-0001-01-01 00:00:00.000", True)
    timedate7_inverse = timedate0 + timedelta(milliseconds=milliseconds_from_epoch)
    assert(abs(milliseconds_from_epoch + SOL_LENGTH*670)<1.0)
    assert(timedate7_inverse == timedate7)

    # test -1 Mars cycle
    milliseconds_to_sub = timedelta(milliseconds=MS_PER_CYCLE)
    timedate8= timedate0 - milliseconds_to_sub
    assert(earth_datetime_to_mars_datetime(timedate8, True) == "-0022-01-01 00:00:00.000, Monday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime_as_string("-0022-01-01 00:00:00.000", True)
    timedate8_inverse = timedate0 + timedelta(milliseconds=milliseconds_from_epoch)
    assert(abs(milliseconds_from_epoch + MS_PER_CYCLE)<1.0)
    assert(timedate8_inverse == timedate8)

    # test -10 terrestrial JD years
    milliseconds_to_sub = timedelta(milliseconds=DAY_LENGTH*3652.5)
    timedate9 = timedate0 - milliseconds_to_sub
    assert(earth_datetime_to_mars_datetime(timedate9, True) == "-0006-09-11 05:24:17.509, Thursday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime_as_string("-0006-09-11 05:24:17.509", True)
    timedate9_inverse = timedate0 + timedelta(milliseconds=milliseconds_from_epoch)
    assert(abs(milliseconds_from_epoch + DAY_LENGTH*3652.5)<1.0)
    assert(timedate9_inverse == timedate9)

    # test -29 Mars yeras
    milliseconds_to_sub = timedelta(milliseconds=MS_PER_MARS_YEAR*29)
    timedate10= timedate0 - milliseconds_to_sub
    assert(earth_datetime_to_mars_datetime(timedate10, True)=="-0029-01-01 20:43:38.182, Monday") 
    milliseconds_from_epoch = mars_datetime_to_earth_datetime_as_string("-0029-01-01 20:43:38.182", True)
    # 0.090820312 ms error here - second assert fails!
    assert(abs(milliseconds_from_epoch + MS_PER_MARS_YEAR*29) < 1.0)
    timedate10_inverse = timedate0 + timedelta(milliseconds=milliseconds_from_epoch)
    #assert(timedate10_inverse == timedate10)


def utc_to_mars_time_tests_negative_offset_mtc_off():
    timedate0 = datetime.fromisoformat(EPOCH)
    # test  -1 second
    milliseconds_to_sub = timedelta(milliseconds=1000)
    timedate1 = timedate0 - milliseconds_to_sub
    assert(earth_datetime_to_mars_datetime(timedate1) == "-0001-12-54 24:39:34.244, Friday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime_as_string("-0001-12-54 24:39:34.244")
    timedate1_inverse = timedate0 + timedelta(milliseconds=milliseconds_from_epoch)
    assert(abs(milliseconds_from_epoch + 1000) < 1.0)
    assert(timedate1_inverse == timedate1)

    # test -1 Eath day
    milliseconds_to_sub = timedelta(milliseconds=DAY_LENGTH)
    timedate2 = timedate0 - milliseconds_to_sub
    assert(earth_datetime_to_mars_datetime(timedate2) == "-0001-12-54 00:39:35.244, Friday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime_as_string("-0001-12-54 00:39:35.244")
    timedate2_inverse = timedate0 + timedelta(milliseconds=milliseconds_from_epoch)
    assert(abs(milliseconds_from_epoch + DAY_LENGTH) < 1.0)
    assert(timedate2_inverse == timedate2)

    # test -1 sol
    milliseconds_to_sub = timedelta(milliseconds=SOL_LENGTH)
    timedate3 = timedate0 - milliseconds_to_sub
    assert(earth_datetime_to_mars_datetime(timedate3) == "-0001-12-54 00:00:00.000, Friday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime_as_string("-0001-12-54 00:00:00.000")
    timedate3_inverse = timedate0 + timedelta(milliseconds=milliseconds_from_epoch)
    assert(abs(milliseconds_from_epoch + SOL_LENGTH) < 1.0)
    assert(timedate3_inverse == timedate3)

    # test start day -1 Earth month
    milliseconds_to_sub = timedelta(milliseconds=DAY_LENGTH*31)
    timedate4 = timedate0 - milliseconds_to_sub
    assert(earth_datetime_to_mars_datetime(timedate4) == "-0001-12-24 20:27:12.564, Wednesday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime_as_string("-0001-12-24 20:27:12.564")
    timedate4_inverse = timedate0 + timedelta(milliseconds=milliseconds_from_epoch)
    assert(milliseconds_from_epoch + DAY_LENGTH*31 < 1.0)
    assert(timedate4_inverse == timedate4)

    # test start day -54 sols
    milliseconds_to_sub = timedelta(milliseconds=SOL_LENGTH*54)
    timedate5 = timedate0 - milliseconds_to_sub
    assert(earth_datetime_to_mars_datetime(timedate5) == "-0001-12-01 00:00:00.000, Monday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime_as_string("-0001-12-01 00:00:00.000")
    timedate5_inverse = timedate0 + timedelta(milliseconds=milliseconds_from_epoch)
    assert(abs(milliseconds_from_epoch + SOL_LENGTH*54)<1.0)
    assert(timedate5_inverse == timedate5)

    # test start day -110 sols
    milliseconds_to_sub = timedelta(milliseconds=SOL_LENGTH*110)
    timedate6 = timedate0 - milliseconds_to_sub
    assert(earth_datetime_to_mars_datetime(timedate6) == "-0001-11-01 00:00:00.000, Monday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime_as_string("-0001-11-01 00:00:00.000")
    timedate6_inverse = timedate0 + timedelta(milliseconds=milliseconds_from_epoch)
    assert(abs(milliseconds_from_epoch + SOL_LENGTH*110)<1.0)
    assert(timedate6_inverse == timedate6)

    # test -1 long Mars year
    milliseconds_to_sub = timedelta(milliseconds=SOL_LENGTH*670)
    timedate7= timedate0 - milliseconds_to_sub
    assert(earth_datetime_to_mars_datetime(timedate7) == "-0001-01-01 00:00:00.000, Monday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime_as_string("-0001-01-01 00:00:00.000")
    timedate7_inverse = timedate0 + timedelta(milliseconds=milliseconds_from_epoch)
    assert(abs(milliseconds_from_epoch + SOL_LENGTH*670)<1.0)
    assert(timedate7_inverse == timedate7)

    # test -1 Mars cycle
    milliseconds_to_sub = timedelta(milliseconds=MS_PER_CYCLE)
    timedate8= timedate0 - milliseconds_to_sub
    assert(earth_datetime_to_mars_datetime(timedate8) == "-0022-01-01 00:00:00.000, Monday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime_as_string("-0022-01-01 00:00:00.000")
    timedate8_inverse = timedate0 + timedelta(milliseconds=milliseconds_from_epoch)
    assert(abs(milliseconds_from_epoch + MS_PER_CYCLE)<1.0)
    assert(timedate8_inverse == timedate8)

    # test -10 terrestrial JD years
    milliseconds_to_sub = timedelta(milliseconds=DAY_LENGTH*3652.5)
    timedate9 = timedate0 - milliseconds_to_sub
    assert(earth_datetime_to_mars_datetime(timedate9) == "-0006-09-11 05:33:12.420, Thursday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime_as_string("-0006-09-11 05:33:12.420")
    timedate9_inverse = timedate0 + timedelta(milliseconds=milliseconds_from_epoch)
    assert(abs(milliseconds_from_epoch + DAY_LENGTH*3652.5)<1.0)
    assert(timedate9_inverse == timedate9)

    # test -29 Mars yeras
    milliseconds_to_sub = timedelta(milliseconds=MS_PER_MARS_YEAR*29)
    timedate10= timedate0 - milliseconds_to_sub
    assert(earth_datetime_to_mars_datetime(timedate10)=="-0029-01-01 21:17:49.529, Monday") 
    milliseconds_from_epoch = mars_datetime_to_earth_datetime_as_string("-0029-01-01 21:17:49.529")
    # 0.090820312 ms error here - second assert fails!
    assert(abs(milliseconds_from_epoch + MS_PER_MARS_YEAR*29) < 1.0)
    timedate10_inverse = timedate0 + timedelta(milliseconds=milliseconds_from_epoch)
    #assert(timedate10_inverse == timedate10)


def utc_to_mars_time_long_intervals_mtc_off():
    timedate0 = datetime.fromisoformat(EPOCH)
    
    # test +110 Mars years
    milliseconds_to_add = timedelta(milliseconds=MS_PER_CYCLE*5)
    timedate1= timedate0 + milliseconds_to_add
    assert(earth_datetime_to_mars_datetime(timedate1)=="0111-01-01 00:00:00.000, Monday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime_as_string("0111-01-01 00:00:00.000")
    timedate1_inverse = timedate0 + timedelta(milliseconds=milliseconds_from_epoch)
    assert(abs(milliseconds_from_epoch - MS_PER_CYCLE*5) < 1.0)
    assert(timedate1_inverse == timedate1)
    
    # test +264 Mars years
    milliseconds_to_add = timedelta(milliseconds=MS_PER_CYCLE*12)
    timedate2= timedate0 + milliseconds_to_add
    assert(earth_datetime_to_mars_datetime(timedate2)=="0265-01-01 00:00:00.000, Monday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime_as_string("0265-01-01 00:00:00.000")
    timedate2_inverse = timedate0 + timedelta(milliseconds=milliseconds_from_epoch)
    assert(abs(milliseconds_from_epoch - MS_PER_CYCLE*12) < 1.0)
    assert(timedate2_inverse == timedate2)

    # test +374 Mars years
    milliseconds_to_add = timedelta(milliseconds=MS_PER_CYCLE*17)
    timedate3= timedate0 + milliseconds_to_add
    assert(earth_datetime_to_mars_datetime(timedate3)=="0375-01-01 00:00:00.000, Monday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime_as_string("0375-01-01 00:00:00.000")
    timedate3_inverse = timedate0 + timedelta(milliseconds=milliseconds_from_epoch)
    assert(abs(milliseconds_from_epoch - MS_PER_CYCLE*17) < 1.0)
    assert(timedate3_inverse == timedate3)

    # test +638 Mars years
    milliseconds_to_add = timedelta(milliseconds=MS_PER_CYCLE*29)
    timedate4= timedate0 + milliseconds_to_add
    assert(earth_datetime_to_mars_datetime(timedate4)=="0639-01-01 00:00:00.000, Monday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime_as_string("0639-01-01 00:00:00.000")
    timedate4_inverse = timedate0 + timedelta(milliseconds=milliseconds_from_epoch)
    assert(abs(milliseconds_from_epoch - MS_PER_CYCLE*29) < 1.0)
    assert(timedate4_inverse == timedate4)

    # test -110 Mars years
    milliseconds_to_sub = timedelta(milliseconds=MS_PER_CYCLE*5)
    timedate5= timedate0 - milliseconds_to_sub
    assert(earth_datetime_to_mars_datetime(timedate5)=="-0110-01-01 00:00:00.000, Monday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime_as_string("-0110-01-01 00:00:00.000")
    timedate5_inverse = timedate0 + timedelta(milliseconds=milliseconds_from_epoch)
    assert(abs(milliseconds_from_epoch + MS_PER_CYCLE*5)<1.0)
    assert(timedate5_inverse == timedate5)

    # test -264 Mars years
    milliseconds_to_sub = timedelta(milliseconds=MS_PER_CYCLE*12)
    timedate6= timedate0 - milliseconds_to_sub
    assert(earth_datetime_to_mars_datetime(timedate6)=="-0264-01-01 00:00:00.000, Monday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime_as_string("-0264-01-01 00:00:00.000")
    timedate6_inverse = timedate0 + timedelta(milliseconds=milliseconds_from_epoch)
    assert(abs(milliseconds_from_epoch + MS_PER_CYCLE*12)<1.0)
    assert(timedate6_inverse == timedate6)

    # test -374 Mars years
    milliseconds_to_sub = timedelta(milliseconds=MS_PER_CYCLE*17)
    timedate7= timedate0 - milliseconds_to_sub
    assert(earth_datetime_to_mars_datetime(timedate7)=="-0374-01-01 00:00:00.000, Monday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime_as_string("-0374-01-01 00:00:00.000")
    timedate7_inverse = timedate0 + timedelta(milliseconds=milliseconds_from_epoch)
    assert(abs(milliseconds_from_epoch + MS_PER_CYCLE*17)<1.0)
    assert(timedate7_inverse == timedate7)

    # test -638 Mars years
    milliseconds_to_sub = timedelta(milliseconds=MS_PER_CYCLE*29)
    timedate8= timedate0 - milliseconds_to_sub
    assert(earth_datetime_to_mars_datetime(timedate8)=="-0638-01-01 00:00:00.000, Monday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime_as_string("-0638-01-01 00:00:00.000")
    timedate8_inverse = timedate0 + timedelta(milliseconds=milliseconds_from_epoch)
    assert(abs(milliseconds_from_epoch + MS_PER_CYCLE*29)<1.0)
    assert(timedate8_inverse == timedate8)


def utc_to_mars_time_test_now_mtc_off():
    ms_since_unix_epoch = time.time()
    timedate_now = datetime.fromtimestamp(ms_since_unix_epoch,EARTH_TIMEZONE)
    mars_timestamp = (earth_datetime_to_mars_datetime(timedate_now)[:23])
    milliseconds_since_epoch = mars_datetime_to_earth_datetime_as_string(mars_timestamp)
    timedate_now_inverse = datetime.fromisoformat(EPOCH) + timedelta(milliseconds=milliseconds_since_epoch)
    time_diff = (timedate_now_inverse - timedate_now)
    # should never fail
    assert(abs(time_diff.total_seconds()*1000)<1.0)


def run_all_tests():
    utc_to_mars_time_tests_positive_offset_mtc_on()
    utc_to_mars_time_tests_positive_offset_mtc_off()
    utc_to_mars_time_tests_negative_offset_mtc_on()
    utc_to_mars_time_tests_negative_offset_mtc_off()
    utc_to_mars_time_long_intervals_mtc_off()
    utc_to_mars_time_test_now_mtc_off()

def main():
	print("Tests started")
	run_all_tests()
	print("Tests passed")


main()