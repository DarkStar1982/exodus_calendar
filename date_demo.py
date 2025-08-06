#!/opt/homebrew/bin/python3
import argparse
import time
from math import modf, ceil, floor
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo
###############################################################################
############################# SUMMARY INFORMATION ##########$##################
###############################################################################
###### |--------Calendar structure before and after epoch year----------| #####
###### |----------------------------------------------------------------| #####
###### |---------------------------Epoch Year---------------------------| #####
###### |-------negative timestamps-----||-----positive timestamps-------| #####
###### |-2^64 ................... -1.0 || 1.0 .................... 2^64 | #####
###### |-------------------------------||-------------------------------| #####
###### |-------negative cycle order----||----positive cycle order-------| #####
###### | 01 02 03 04 ..... 19 20 21 22 || 01 02 03 04 ..... 19 20 21 22 | #####
###### |-------------------------------||-------------------------------| #####
###### |------negative years order-----||-----positive years order------| #####
###### |-10 -9 -8 -7 -6 -5 -4 -3 -2 -1 || +1 +2 +3 +4 +5 +6 +7 +8 +9 +10| #####
###### |-------------------------------||-------------------------------| #####
###### |---negative year month order---||---positive year month order---| #####
###### |[Jan-------Dec] [Jan-------Dec]||[Jan-------Dec] [Jan-------Dec]| #####
###### |-------------------------------||-------------------------------| #####
###### |------negative year dates------||-------positive year dates-----| #####
###### | 01 02 03 04 ..... 51 52 53 54 || 01 02 03 04 ..... 53 54 55 56 | #####
###### |-------------------------------||-------------------------------| #####
###############################################################################

###############################################################################
################################## CONSTANTS ##################################
###############################################################################

# Start year same as in Unix time, preliminary designation, can be changed
EPOCH = "1970-01-01 00:00:00Z"

EARTH_TIMEZONE = ZoneInfo("UTC")

# Martian sol length in milliseconds:
# 24:39:35.244 seconds
SOL_LENGTH = 88775244

# Terrestrial day length in milliseconds
DAY_LENGTH = 86400000

# The northward equinox year length in sols
# Note that this value is not constant and slowly increases
# Needs to be replaced with better expression
MARS_YEAR_LENGTH = 668.5907
MARS_MONTH_LENGTH = 56 # except December

# Gregorian year in days
EARTH_YEAR_LENGTH = 365.2425

# Julian year in days
JULIAN_YEAR_LENGTH = 365.25

# 22-year cycle: 
# * 10 668-sol years
# * 11 669-sol years, 
# * 1 670 sol year marks end of cycle (leap year)
YEAR_CYCLE = [
    669, #1
    668, # 2
    669, #3
    668, # 4
    669, #5
    668, # 6
    669, #7
    668, # 8
    669, #9
    668, # 10
    669, #11
    668, # 12
    669, #13
    668, # 14
    669, #15
    668, # 16
    669, #17
    668, # 18
    669, #19
    668, # 20  
    669, #21
    670  # 22
]

MS_PER_CYCLE = sum(YEAR_CYCLE)*SOL_LENGTH
MS_PER_MARS_YEAR = (sum(YEAR_CYCLE)*SOL_LENGTH)/len(YEAR_CYCLE)

# Martian months and duration - 11 months x 56 days, 1 month variable duration
# Alternatively, name after Zodiacal signs (European or Chinese?)
MONTHS = [
    "January",  # Aries - Rat
    "February", # Taurus - Ox
    "March",    # Gemini - Tiger
    "April",    # Cancer - Rabbit
    "May",      # Leo - Dragon
    "June",     # Virgo - Snake
    "July",     # Libra - Horse
    "August",   # Scorpio - Goat
    "September",# Sagittarius - Monkey
    "October",  # Capricorn - Rooster
    "November", # Aquarius - Dog
    "December"  # Pisces - Pig
]

# MONTHS: 01  02  03  04  05  06  07  08  09  10  11  12
MONTH_LENGTH = {
    668: [56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 52],
    669: [56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 53],
    670: [56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 54],
}

DAYS = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]

# STRING CONSTANTS
STR_ANNUAL_ERROR = "Annual error for calendar year in seconds"
STR_AVG_YEAR_LENGTH = "Calendar year length"
STR_MARS_YEARS_TO_1SOL_ERROR = "Martian years to pass for 1 sol error"
STR_EARTH_YEARS_TO_1SOL_ERROR = "Earth years to pass for 1 sol error"

###############################################################################
################################ IMPLEMENTATION ###############################
###############################################################################

def format_raw_time(p_milliseconds):
    seconds = p_milliseconds/1000
    hours = seconds/3600
    _, h_int = modf(hours)
    minutes = (hours - h_int)*60
    m_f, m_int = modf(minutes)
    seconds = m_f*60
    sec_f, sec_int = modf(seconds)
    ms = round((sec_f*1000.0),3)
    timestamp = "%02d:%02d:%02d.%03d" % (h_int, m_int, sec_int, ms)
    return timestamp


def martian_time_to_millisec(timestamp):
    time_split = [float(x) for x in timestamp.split(':')]
    p_hours = time_split[0]
    p_min = time_split[1]
    p_sec = time_split[2]
    milliseconds = p_sec*1000
    milliseconds = milliseconds + p_min*60*1000
    milliseconds = milliseconds + p_hours*3600*1000
    return int(milliseconds)


def process_negative_diff(p_epoch_date, p_input_date):
    diff = p_input_date - p_epoch_date
    milliseconds_since_epoch = diff.total_seconds()*1000
    absolute_milliseconds = abs(milliseconds_since_epoch)
    total_cycles = absolute_milliseconds // MS_PER_CYCLE
    # calculate total cycle years passed
    full_cycle_years = total_cycles*len(YEAR_CYCLE)
    ms_residual = absolute_milliseconds % MS_PER_CYCLE
    years_accumulated = 0
    for i in range(len(YEAR_CYCLE)-1, -1, -1):
        if (ms_residual - YEAR_CYCLE[i]*SOL_LENGTH)<0:
            break
        else:
            ms_residual = ms_residual - YEAR_CYCLE[i]*SOL_LENGTH
            years_accumulated = years_accumulated + 1
    # calculate current year duration
    year_len = YEAR_CYCLE[len(YEAR_CYCLE)-years_accumulated-1]
    # calculate months elapsed since start of year
    months_accumulated = 0
    for i in range(len(MONTH_LENGTH[year_len])-1, -1, -1):
        if (ms_residual - MONTH_LENGTH[year_len][i]*SOL_LENGTH)<0:
            break
        else:
            ms_residual = ms_residual - MONTH_LENGTH[year_len][i]*SOL_LENGTH
            months_accumulated = months_accumulated + 1
    months_accumulated = len(MONTH_LENGTH[year_len]) - months_accumulated
    # calculate days elapsed
    month_duration = MONTH_LENGTH[year_len][months_accumulated-1]
    days_accumulated = 0
    for i in range(month_duration-1, -1, -1):
        if (ms_residual - SOL_LENGTH)<0:
            break
        else:
            ms_residual = ms_residual - SOL_LENGTH
            days_accumulated = days_accumulated + 1
    days_accumulated = month_duration - days_accumulated
    # calculate time
    tt = format_raw_time(SOL_LENGTH-ms_residual)
    yyyy = - full_cycle_years - years_accumulated - 1
    mm = months_accumulated
    dd= days_accumulated
    wd = DAYS[(days_accumulated-1) % 7]
    return("Mars DateTime: %05d-%02d-%02d %s, %s" % (yyyy, mm, dd, tt, wd))


def process_positive_diff(p_epoch_date, p_input_date):
    diff = p_input_date - p_epoch_date
    milliseconds_since_epoch = diff.total_seconds()*1000
    total_cycles = milliseconds_since_epoch // MS_PER_CYCLE
    # calculate total cycle years passed
    full_cycle_years = total_cycles*len(YEAR_CYCLE)
    ms_residual = milliseconds_since_epoch % MS_PER_CYCLE
    years_accumulated = 0
    for i in range(0, len(YEAR_CYCLE), 1):
        if (ms_residual - YEAR_CYCLE[i]*SOL_LENGTH)<0:
            break
        else:
            ms_residual = ms_residual - YEAR_CYCLE[i]*SOL_LENGTH
            years_accumulated = years_accumulated + 1
    # calculate current year duration
    year_length = YEAR_CYCLE[years_accumulated]
    # calculate months elapsed since start of year
    months_accumulated = 0
    for i in range(0, len(MONTH_LENGTH[year_length]), 1):
        if (ms_residual - MONTH_LENGTH[year_length][i]*SOL_LENGTH)<0:
            break
        else:
            ms_residual = ms_residual - MONTH_LENGTH[year_length][i]*SOL_LENGTH
            months_accumulated = months_accumulated + 1
    # calculate days elapsed
    days_accumulated = 0
    month_duration = MONTH_LENGTH[year_length][months_accumulated]
    for i in range(0, month_duration, 1):
        if (ms_residual - SOL_LENGTH)<0:
            break
        else:
            ms_residual = ms_residual - SOL_LENGTH
            days_accumulated = days_accumulated + 1
    # get time
    tt = format_raw_time(ms_residual)
    # adds ones where necessary
    yyyy = full_cycle_years + years_accumulated + 1
    mm = months_accumulated + 1
    dd = days_accumulated + 1
    wd = DAYS[days_accumulated % 7]
    return("Mars DateTime: %04d-%02d-%02d %s, %s" %(yyyy, mm, dd, tt, wd))


def process_positive_diff_inv(input_date):
    datetimes = input_date.split()
    date_split = [int(x) for x in datetimes[0].split('-')]
    # calculate milliseconds elapsed
    ms_total = 0
    years_elapsed = date_split[0] - 1 
    total_cycles_passed = years_elapsed // len(YEAR_CYCLE)
    ms_total = ms_total + MS_PER_CYCLE*total_cycles_passed
    # add full years
    year_in_current_cycle = years_elapsed - total_cycles_passed*len(YEAR_CYCLE)
    year_length = YEAR_CYCLE[year_in_current_cycle]
    for i in range(0, year_in_current_cycle, 1):
        ms_total = ms_total + YEAR_CYCLE[i]*SOL_LENGTH
    months_elapsed = date_split[1] - 1 
    for i in range(0, months_elapsed, 1):
        ms_total = ms_total + MONTH_LENGTH[year_length][i]*SOL_LENGTH
    days_elapsed = date_split[2] - 1
    for i in range(0, days_elapsed, 1):
        ms_total = ms_total + SOL_LENGTH
    ms_total = ms_total + martian_time_to_millisec(datetimes[1])
    return ms_total

 
def process_negative_diff_inv(p_input_date):
    datetimes = p_input_date.split()
    date_split = [int(x) for x in datetimes[0].split('-')]
    # calculate milliseconds elapsed
    ms_total = 0
    years_elapsed = date_split[0] - 1
    # calculate cycles passed 
    total_cycles_passed = years_elapsed // len(YEAR_CYCLE)
    ms_total = ms_total + MS_PER_CYCLE*total_cycles_passed
    # calculate current year length
    year_in_current_cycle = years_elapsed - total_cycles_passed*len(YEAR_CYCLE)
    year_len = YEAR_CYCLE[len(YEAR_CYCLE) - year_in_current_cycle-1]
    for i in range(0, year_in_current_cycle,1):
        ms_total = ms_total + YEAR_CYCLE[len(YEAR_CYCLE)-i-1]*SOL_LENGTH
    months_elapsed = len(MONTHS) - date_split[1]
    for i in range(0, months_elapsed, 1):
        ms_total = ms_total + MONTH_LENGTH[year_len][len(MONTHS)-i-1]*SOL_LENGTH
    days_elapsed = MONTH_LENGTH[year_len][date_split[1]-1] - date_split[2]
    for i in range(0, days_elapsed, 1):
        ms_total = ms_total + SOL_LENGTH
    ms_total = ms_total + (SOL_LENGTH - martian_time_to_millisec(datetimes[1]))
    return -ms_total


def earth_datetime_to_mars_datetime(input_date):
    # Calculate year
    epoch_date = datetime.fromisoformat(EPOCH)
    if (epoch_date<=input_date):
        return process_positive_diff(epoch_date, input_date)
    else:
        return process_negative_diff(epoch_date, input_date)


def mars_datetime_to_earth_datetime(input_date):
    if input_date[0] == '-':
        return process_negative_diff_inv(input_date[1:])
    else:
        return process_positive_diff_inv(input_date)

###############################################################################
################################ ACCURACY TESTS ###############################
###############################################################################

def errors_test():
    calendar_year_length = sum(YEAR_CYCLE)/len(YEAR_CYCLE)
    annual_error = (((calendar_year_length- MARS_YEAR_LENGTH)*SOL_LENGTH)/1000)
    seconds_per_year = (MARS_YEAR_LENGTH*SOL_LENGTH)/1000
    mars_years_to_1_sol_error = (SOL_LENGTH/1000)/annual_error
    earth_y = DAY_LENGTH*EARTH_YEAR_LENGTH
    mars_y = MARS_YEAR_LENGTH*SOL_LENGTH
    earth_years_to_1_sol_error = (mars_years_to_1_sol_error*mars_y)/earth_y
    assert(calendar_year_length-MARS_YEAR_LENGTH == 0.00020909090915210982)
    assert(annual_error==18.562096478160385)
    assert(mars_years_to_1_sol_error==4782.608694252308)
    assert(earth_years_to_1_sol_error == 8995.431602985973)


###############################################################################
############################# FUNCTIONALITY TESTS #############################
###############################################################################

def utc_to_mars_time_tests_positive_offset():
    # test first date - should be year 1
    timedate0 = datetime.fromisoformat(EPOCH)
    assert(earth_datetime_to_mars_datetime(timedate0)=="Mars DateTime: 0001-01-01 00:00:00.000, Monday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime("0001-01-01 00:00:00.000")
    assert(datetime.fromtimestamp(milliseconds_from_epoch/1000,EARTH_TIMEZONE) == timedate0)

    # test start day +1 second
    milliseconds_to_add = timedelta(milliseconds=1000)
    timedate1 = timedate0 + milliseconds_to_add
    assert(earth_datetime_to_mars_datetime(timedate1)=="Mars DateTime: 0001-01-01 00:00:01.000, Monday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime("0001-01-01 00:00:01.000") 
    timedate1_inverse = timedate0 + timedelta(milliseconds=milliseconds_from_epoch)
    assert(milliseconds_from_epoch - 1000 < 1.0)
    assert(datetime.fromtimestamp(milliseconds_from_epoch/1000,EARTH_TIMEZONE) == timedate1)

    # test start day +1 day
    milliseconds_to_add = timedelta(milliseconds=DAY_LENGTH)
    timedate2 = timedate0 + milliseconds_to_add
    assert(earth_datetime_to_mars_datetime(timedate2) == "Mars DateTime: 0001-01-01 24:00:00.000, Monday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime("0001-01-01 24:00:00.000")
    assert(abs(milliseconds_from_epoch - DAY_LENGTH) < 1.0)
    assert(datetime.fromtimestamp(milliseconds_from_epoch/1000,EARTH_TIMEZONE) == timedate2)

    # test start day +1 sol
    milliseconds_to_add = timedelta(milliseconds=SOL_LENGTH)
    timedate3 = timedate0 + milliseconds_to_add
    assert(earth_datetime_to_mars_datetime(timedate3) == "Mars DateTime: 0001-01-02 00:00:00.000, Tuesday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime("0001-01-02 00:00:00.000")
    assert(abs(milliseconds_from_epoch - SOL_LENGTH) < 1.0)
    assert(datetime.fromtimestamp(milliseconds_from_epoch/1000,EARTH_TIMEZONE) == timedate3)

    # test start day +7 sols
    milliseconds_to_add = timedelta(milliseconds=SOL_LENGTH*7)
    timedate4 = timedate0 + milliseconds_to_add
    assert(earth_datetime_to_mars_datetime(timedate4) == "Mars DateTime: 0001-01-08 00:00:00.000, Monday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime("0001-01-08 00:00:00.000")
    assert(abs(milliseconds_from_epoch - SOL_LENGTH*7) < 1.0)
    assert(datetime.fromtimestamp(milliseconds_from_epoch/1000,EARTH_TIMEZONE) == timedate4)

    # test start day +1 Earth month
    milliseconds_to_add = timedelta(milliseconds=DAY_LENGTH*31)
    timedate5 = timedate0 + milliseconds_to_add
    assert(earth_datetime_to_mars_datetime(timedate5) == "Mars DateTime: 0001-01-31 04:12:22.680, Wednesday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime("0001-01-31 04:12:22.680")
    assert(milliseconds_from_epoch - DAY_LENGTH*31 < 1.0)
    assert(datetime.fromtimestamp(milliseconds_from_epoch/1000,EARTH_TIMEZONE) == timedate5)

    # test start day +1 Martian month
    milliseconds_to_add = timedelta(milliseconds=SOL_LENGTH*MARS_MONTH_LENGTH)
    timedate6 = timedate0 + milliseconds_to_add
    assert(earth_datetime_to_mars_datetime(timedate6) == "Mars DateTime: 0001-02-01 00:00:00.000, Monday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime("0001-02-01 00:00:00.000")
    assert(abs(milliseconds_from_epoch - SOL_LENGTH*MARS_MONTH_LENGTH) < 1.0)
    assert(datetime.fromtimestamp(milliseconds_from_epoch/1000,EARTH_TIMEZONE) == timedate6)

    # test start day +11 Martian months
    milliseconds_to_add = timedelta(milliseconds=SOL_LENGTH*MARS_MONTH_LENGTH*11)
    timedate7 = timedate0 + milliseconds_to_add
    assert(earth_datetime_to_mars_datetime(timedate7) == "Mars DateTime: 0001-12-01 00:00:00.000, Monday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime("0001-12-01 00:00:00.000")
    assert(abs(milliseconds_from_epoch - SOL_LENGTH*MARS_MONTH_LENGTH*11) < 1.0)
    assert(datetime.fromtimestamp(milliseconds_from_epoch/1000,EARTH_TIMEZONE) == timedate7)

    # test A end of december for year 1
    milliseconds_to_add = timedelta(milliseconds=SOL_LENGTH*MARS_MONTH_LENGTH*11+52*SOL_LENGTH-100)
    timedate7a = timedate0 + milliseconds_to_add
    assert(earth_datetime_to_mars_datetime(timedate7a)=="Mars DateTime: 0001-12-52 24:39:35.144, Wednesday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime("0001-12-52 24:39:35.144")
    assert(abs(milliseconds_from_epoch - (SOL_LENGTH*MARS_MONTH_LENGTH*11+52*SOL_LENGTH-100)) < 1.0)
    assert(datetime.fromtimestamp(milliseconds_from_epoch/1000,EARTH_TIMEZONE) == timedate7a)

    # test B end of december for year 1 
    milliseconds_to_add = timedelta(milliseconds=SOL_LENGTH*MARS_MONTH_LENGTH*11+53*SOL_LENGTH-100)
    timedate7b = timedate0 + milliseconds_to_add
    milliseconds_from_epoch = mars_datetime_to_earth_datetime("0001-12-53 24:39:35.144")
    assert(abs(milliseconds_from_epoch - (SOL_LENGTH*MARS_MONTH_LENGTH*11+53*SOL_LENGTH-100)) < 1.0)
    assert(datetime.fromtimestamp(milliseconds_from_epoch/1000,EARTH_TIMEZONE) == timedate7b)
    
    # test C end of december for year 1 - rollover to year2
    milliseconds_to_add = timedelta(milliseconds=SOL_LENGTH*MARS_MONTH_LENGTH*11+53*SOL_LENGTH)
    timedate7c = timedate0 + milliseconds_to_add
    assert(earth_datetime_to_mars_datetime(timedate7c)=="Mars DateTime: 0002-01-01 00:00:00.000, Monday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime("0002-01-01 00:00:00.000")
    assert(abs(milliseconds_from_epoch - (SOL_LENGTH*MARS_MONTH_LENGTH*11+53*SOL_LENGTH)) < 1.0)
    assert(datetime.fromtimestamp(milliseconds_from_epoch/1000,EARTH_TIMEZONE) == timedate7c)

    # test +1 Earth year
    milliseconds_to_add = timedelta(milliseconds=DAY_LENGTH*JULIAN_YEAR_LENGTH)
    timedate8 = timedate0 + milliseconds_to_add
    assert(earth_datetime_to_mars_datetime(timedate8)=="Mars DateTime: 0001-07-20 11:46:28.380, Saturday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime("0001-07-20 11:46:28.380")
    assert(abs(milliseconds_from_epoch - DAY_LENGTH*JULIAN_YEAR_LENGTH) < 1.0)
    assert(datetime.fromtimestamp(milliseconds_from_epoch/1000,EARTH_TIMEZONE) == timedate8)

    # test +1 Mars even year
    milliseconds_to_add = timedelta(milliseconds=SOL_LENGTH*668)
    timedate9= timedate0 + milliseconds_to_add
    assert(earth_datetime_to_mars_datetime(timedate9)=="Mars DateTime: 0001-12-53 00:00:00.000, Thursday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime("0001-12-53 00:00:00.000")
    assert((milliseconds_from_epoch - (SOL_LENGTH*668)) < 1.0)
    assert(datetime.fromtimestamp(milliseconds_from_epoch/1000,EARTH_TIMEZONE) == timedate9)

    # test +1 Mars odd year
    milliseconds_to_add = timedelta(milliseconds=SOL_LENGTH*669)
    timedate10= timedate0 + milliseconds_to_add
    assert(earth_datetime_to_mars_datetime(timedate10)=="Mars DateTime: 0002-01-01 00:00:00.000, Monday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime("0002-01-01 00:00:00.000")
    assert(abs(milliseconds_from_epoch - SOL_LENGTH*669) < 1.0)
    assert(datetime.fromtimestamp(milliseconds_from_epoch/1000,EARTH_TIMEZONE) == timedate10)

    # test +10 Mars years
    milliseconds_to_add = timedelta(milliseconds=MS_PER_MARS_YEAR*10)
    timedate11= timedate0 + milliseconds_to_add
    assert(earth_datetime_to_mars_datetime(timedate11)=="Mars DateTime: 0011-01-01 22:25:04.767, Monday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime("0011-01-01 22:25:04.767")
    # 0.272705078125 ms error here - second assert fails!
    assert(abs(milliseconds_from_epoch - MS_PER_MARS_YEAR*10) < 1.0)
    #assert(datetime.fromtimestamp(milliseconds_from_epoch/1000,EARTH_TIMEZONE) == timedate11)

    # test +1 cycle (22 Mars years)
    milliseconds_to_add = timedelta(milliseconds=MS_PER_MARS_YEAR*22)
    timedate12= timedate0 + milliseconds_to_add
    assert(earth_datetime_to_mars_datetime(timedate12)=="Mars DateTime: 0023-01-01 00:00:00.000, Monday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime("0023-01-01 00:00:00.000")
    assert(abs(milliseconds_from_epoch - MS_PER_MARS_YEAR*22) < 1.0)
    assert(datetime.fromtimestamp(milliseconds_from_epoch/1000,EARTH_TIMEZONE) == timedate12)

    # test +29 Mars yeras
    milliseconds_to_add = timedelta(milliseconds=MS_PER_MARS_YEAR*29)
    timedate13= timedate0 + milliseconds_to_add
    assert(earth_datetime_to_mars_datetime(timedate13)=="Mars DateTime: 0030-01-01 03:21:45.715, Monday") 
    milliseconds_from_epoch = mars_datetime_to_earth_datetime("0030-01-01 03:21:45.715")
    # 0.0908203125 ms error here - second assert fails!
    assert(abs(milliseconds_from_epoch - MS_PER_MARS_YEAR*29) < 1.0)
    #assert(datetime.fromtimestamp(milliseconds_from_epoch/1000,EARTH_TIMEZONE) == timedate13)


def utc_to_mars_time_tests_negative_offset():
    timedate0 = datetime.fromisoformat(EPOCH)
    # test  -1 second
    milliseconds_to_sub = timedelta(milliseconds=1000)
    timedate1 = timedate0 - milliseconds_to_sub
    assert(earth_datetime_to_mars_datetime(timedate1) == "Mars DateTime: -0001-12-54 24:39:34.244, Friday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime("-0001-12-54 24:39:34.244")
    assert(abs(milliseconds_from_epoch + 1000) < 1.0)
    assert(datetime.fromtimestamp(milliseconds_from_epoch/1000,EARTH_TIMEZONE) == timedate1)

    # test -1 Eath day
    milliseconds_to_sub = timedelta(milliseconds=DAY_LENGTH)
    timedate2 = timedate0 - milliseconds_to_sub
    assert(earth_datetime_to_mars_datetime(timedate2) == "Mars DateTime: -0001-12-54 00:39:35.244, Friday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime("-0001-12-54 00:39:35.244")
    assert(abs(milliseconds_from_epoch + DAY_LENGTH) < 1.0)
    assert(datetime.fromtimestamp(milliseconds_from_epoch/1000,EARTH_TIMEZONE) == timedate2)

    # test -1 sol
    milliseconds_to_sub = timedelta(milliseconds=SOL_LENGTH)
    timedate3 = timedate0 - milliseconds_to_sub
    assert(earth_datetime_to_mars_datetime(timedate3) == "Mars DateTime: -0001-12-53 24:39:35.244, Thursday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime("-0001-12-53 24:39:35.244")
    assert(abs(milliseconds_from_epoch + SOL_LENGTH) < 1.0)
    assert(datetime.fromtimestamp(milliseconds_from_epoch/1000,EARTH_TIMEZONE) == timedate3)

    # test start day -1 Earth month
    milliseconds_to_sub = timedelta(milliseconds=DAY_LENGTH*31)
    timedate4 = timedate0 - milliseconds_to_sub
    assert(earth_datetime_to_mars_datetime(timedate4) == "Mars DateTime: -0001-12-24 20:27:12.564, Wednesday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime("-0001-12-24 20:27:12.564")
    assert(milliseconds_from_epoch + DAY_LENGTH*31 < 1.0)
    assert(datetime.fromtimestamp(milliseconds_from_epoch/1000,EARTH_TIMEZONE) == timedate4)

    # test start day -54 sols
    milliseconds_to_sub = timedelta(milliseconds=SOL_LENGTH*54)
    timedate5 = timedate0 - milliseconds_to_sub
    assert(earth_datetime_to_mars_datetime(timedate5) == "Mars DateTime: -0001-11-56 24:39:35.244, Sunday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime("-0001-11-56 24:39:35.244")
    assert(abs(milliseconds_from_epoch + SOL_LENGTH*54)<1.0)
    assert(datetime.fromtimestamp(milliseconds_from_epoch/1000,EARTH_TIMEZONE) == timedate5)

    # test start day -110 sols
    milliseconds_to_sub = timedelta(milliseconds=SOL_LENGTH*110)
    timedate6 = timedate0 - milliseconds_to_sub
    assert(earth_datetime_to_mars_datetime(timedate6) == "Mars DateTime: -0001-10-56 24:39:35.244, Sunday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime("-0001-10-56 24:39:35.244")
    assert(abs(milliseconds_from_epoch + SOL_LENGTH*110)<1.0)
    assert(datetime.fromtimestamp(milliseconds_from_epoch/1000,EARTH_TIMEZONE) == timedate6)

    # test -1 long Mars year
    milliseconds_to_sub = timedelta(milliseconds=SOL_LENGTH*670)
    timedate7= timedate0 - milliseconds_to_sub
    assert(earth_datetime_to_mars_datetime(timedate7) == "Mars DateTime: -0002-12-53 24:39:35.244, Thursday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime("-0002-12-53 24:39:35.244")
    assert(abs(milliseconds_from_epoch + SOL_LENGTH*670)<1.0)
    assert(datetime.fromtimestamp(milliseconds_from_epoch/1000,EARTH_TIMEZONE) == timedate7)

    # test -1 Mars cycle
    milliseconds_to_sub = timedelta(milliseconds=MS_PER_CYCLE)
    timedate8= timedate0 - milliseconds_to_sub
    assert(earth_datetime_to_mars_datetime(timedate8) == "Mars DateTime: -0023-12-54 24:39:35.244, Friday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime("-0023-12-54 24:39:35.244")
    assert(abs(milliseconds_from_epoch + MS_PER_CYCLE)<1.0)
    assert(datetime.fromtimestamp(milliseconds_from_epoch/1000,EARTH_TIMEZONE) == timedate8)

    # test -10 terrestrial JD years
    milliseconds_to_sub = timedelta(milliseconds=DAY_LENGTH*3652.5)
    timedate9 = timedate0 - milliseconds_to_sub
    assert(earth_datetime_to_mars_datetime(timedate9) == "Mars DateTime: -0006-09-11 05:33:12.420, Thursday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime("-0006-09-11 05:33:12.420")
    assert(abs(milliseconds_from_epoch + DAY_LENGTH*3652.5)<1.0)
    assert(datetime.fromtimestamp(milliseconds_from_epoch/1000,EARTH_TIMEZONE) == timedate9)

    # test -29 Mars yeras
    milliseconds_to_sub = timedelta(milliseconds=MS_PER_MARS_YEAR*29)
    timedate10= timedate0 - milliseconds_to_sub
    assert(earth_datetime_to_mars_datetime(timedate10)=="Mars DateTime: -0029-01-01 21:17:49.528, Monday") 
    milliseconds_from_epoch = mars_datetime_to_earth_datetime("-0029-01-01 21:17:49.528")
    # 0.9091796875 ms error here - second assert fails!
    assert(abs(milliseconds_from_epoch + MS_PER_MARS_YEAR*29) < 1.0)
    #assert(datetime.fromtimestamp(milliseconds_from_epoch/1000,EARTH_TIMEZONE) == timedate10)

def utc_to_mars_time_long_intervals():
    timedate0 = datetime.fromisoformat(EPOCH)
    
    # test +110 Mars years
    milliseconds_to_add = timedelta(milliseconds=MS_PER_CYCLE*5)
    timedate1= timedate0 + milliseconds_to_add
    assert(earth_datetime_to_mars_datetime(timedate1)=="Mars DateTime: 0111-01-01 00:00:00.000, Monday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime("0111-01-01 00:00:00.000")
    assert(abs(milliseconds_from_epoch - MS_PER_CYCLE*5) < 1.0)
    assert(datetime.fromtimestamp(milliseconds_from_epoch/1000,EARTH_TIMEZONE) == timedate1)

    # test +264 Mars years
    milliseconds_to_add = timedelta(milliseconds=MS_PER_CYCLE*12)
    timedate2= timedate0 + milliseconds_to_add
    assert(earth_datetime_to_mars_datetime(timedate2)=="Mars DateTime: 0265-01-01 00:00:00.000, Monday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime("0265-01-01 00:00:00.000")
    assert(abs(milliseconds_from_epoch - MS_PER_CYCLE*12) < 1.0)
    assert(datetime.fromtimestamp(milliseconds_from_epoch/1000,EARTH_TIMEZONE) == timedate2)

    # test +374 Mars years
    milliseconds_to_add = timedelta(milliseconds=MS_PER_CYCLE*17)
    timedate3= timedate0 + milliseconds_to_add
    assert(earth_datetime_to_mars_datetime(timedate3)=="Mars DateTime: 0375-01-01 00:00:00.000, Monday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime("0375-01-01 00:00:00.000")
    # 0.001 ms error here - second assert fails!
    assert(abs(milliseconds_from_epoch - MS_PER_CYCLE*17) < 1.0)
    #assert(datetime.fromtimestamp(milliseconds_from_epoch/1000,EARTH_TIMEZONE) == timedate3)

    # test +638 Mars years
    milliseconds_to_add = timedelta(milliseconds=MS_PER_CYCLE*29)
    timedate4= timedate0 + milliseconds_to_add
    assert(earth_datetime_to_mars_datetime(timedate4)=="Mars DateTime: 0639-01-01 00:00:00.000, Monday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime("0639-01-01 00:00:00.000")
    # 0.003 ms error here - second assert fails!
    assert(abs(milliseconds_from_epoch - MS_PER_CYCLE*29) < 1.0)
    # assert(datetime.fromtimestamp(milliseconds_from_epoch/1000,EARTH_TIMEZONE) == timedate4)

    # test -110 Mars years
    milliseconds_to_sub = timedelta(milliseconds=MS_PER_CYCLE*5)
    timedate5= timedate0 - milliseconds_to_sub
    assert(earth_datetime_to_mars_datetime(timedate5)=="Mars DateTime: -0111-12-54 24:39:35.244, Friday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime("-0111-12-54 24:39:35.244")
    assert(abs(milliseconds_from_epoch + MS_PER_CYCLE*5)<1.0)
    assert(datetime.fromtimestamp(milliseconds_from_epoch/1000,EARTH_TIMEZONE) == timedate5)

    # test -264 Mars years
    milliseconds_to_sub = timedelta(milliseconds=MS_PER_CYCLE*12)
    timedate6= timedate0 - milliseconds_to_sub
    assert(earth_datetime_to_mars_datetime(timedate6)=="Mars DateTime: -0265-12-54 24:39:35.244, Friday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime("-0265-12-54 24:39:35.244")
    assert(abs(milliseconds_from_epoch + MS_PER_CYCLE*12)<1.0)
    assert(datetime.fromtimestamp(milliseconds_from_epoch/1000,EARTH_TIMEZONE) == timedate6)

    # test -374 Mars years
    milliseconds_to_sub = timedelta(milliseconds=MS_PER_CYCLE*17)
    timedate7= timedate0 - milliseconds_to_sub
    assert(earth_datetime_to_mars_datetime(timedate7)=="Mars DateTime: -0375-12-54 24:39:35.244, Friday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime("-0375-12-54 24:39:35.244")
    # 0.001 ms error here - second assert fails!
    assert(abs(milliseconds_from_epoch + MS_PER_CYCLE*17)<1.0)

    # test -638 Mars years
    milliseconds_to_sub = timedelta(milliseconds=MS_PER_CYCLE*29)
    timedate8= timedate0 - milliseconds_to_sub
    assert(earth_datetime_to_mars_datetime(timedate8)=="Mars DateTime: -0639-12-54 24:39:35.244, Friday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime("-0639-12-54 24:39:35.244")
    assert(abs(milliseconds_from_epoch + MS_PER_CYCLE*29)<1.0)
    # 0.003 ms error here - second assert fails!
    #assert(datetime.fromtimestamp(milliseconds_from_epoch/1000,EARTH_TIMEZONE) == timedate8)


def run_all_tests():
    errors_test()
    utc_to_mars_time_tests_positive_offset()
    utc_to_mars_time_tests_negative_offset()
    utc_to_mars_time_long_intervals()


def main():
    run_all_tests()
    parser = argparse.ArgumentParser(
        prog='exodus_calendar.py',
        description='Converts the time and date between Earth and Mars.'
    )
    parser.add_argument(
        '-m',
        "--mars", 
        type=str, 
        dest='MARS_DATETIME', 
        help='convert Mars datetime to Earth one (in UTC)'
    )
    parser.add_argument(
        '-e',
        "--earth", 
        type=str, 
        dest='EARTH_DATETIME', 
        help='convert Earth datetime in UTC to Mars one'
    )

    args = parser.parse_args()
    if args.EARTH_DATETIME is not None:
        input_date = datetime.fromisoformat(args.EARTH_DATETIME)
        print(earth_datetime_to_mars_datetime(input_date))
    elif args.MARS_DATETIME is not None:
        milliseconds_from_epoch = mars_datetime_to_earth_datetime(args.MARS_DATETIME)
        output_date = datetime.fromtimestamp(milliseconds_from_epoch/1000,EARTH_TIMEZONE)
        print("Earth DateTime: %s" % output_date)
    else:
        timedate = datetime.now(timezone.utc)
        print("Earth DateTime: %s" % timedate.strftime("%Y-%m-%d %H:%M:%S+%Z, %A"))
        print(earth_datetime_to_mars_datetime(timedate))

main()