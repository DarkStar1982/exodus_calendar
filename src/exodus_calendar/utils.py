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

# Start year, preliminary designation, can be changed
EPOCH = "1955-04-11 19:21:51Z"

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
    669, 668, 669, 668, 669, 668, 669, 668, 669, 668, 669,
    668, 669, 668, 669, 668, 669, 668, 669, 668, 669, 670
]

MS_PER_CYCLE = sum(YEAR_CYCLE)*SOL_LENGTH
MS_PER_MARS_YEAR = (sum(YEAR_CYCLE)*SOL_LENGTH)/len(YEAR_CYCLE)

# Martian months and duration - 11 months x 56 days, 1 month variable duration
MONTHS = [
    "JAN", "FEB", "MAR", "APR", "MAY", "JUN",
    "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"
]

# MONTHS: 01  02  03  04  05  06  07  08  09  10  11  12
MONTH_LENGTH = {
    668: [56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 52],
    669: [56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 53],
    670: [56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 54],
}

WEEKDAYS = [
    "Monday", "Tuesday","Wednesday", "Thursday", "Friday", "Saturday", "Sunday"
]

# STRING CONSTANTS
STR_ANNUAL_ERROR = "Annual error for calendar year in seconds"
STR_AVG_YEAR_LENGTH = "Calendar year length"
STR_MARS_YEARS_TO_1SOL_ERROR = "Martian years to pass for 1 sol error"
STR_EARTH_YEARS_TO_1SOL_ERROR = "Earth years to pass for 1 sol error"

###############################################################################
################################ IMPLEMENTATION ###############################
###############################################################################

def format_raw_time(p_milliseconds, mars_second_on=False):
    if mars_second_on:
        martian_second = round((SOL_LENGTH/DAY_LENGTH)*1000.0,1)
        seconds = p_milliseconds/martian_second
    else:
        seconds = p_milliseconds/1000
    hours = seconds/3600
    _, h_int = modf(hours)
    minutes = (hours - h_int)*60
    m_f, m_int = modf(minutes)
    seconds = m_f*60
    sec_f, sec_int = modf(seconds)
    # the fractional part is not in "ms" if 
    # "Martian second" is used!
    ms = round((sec_f*1000.0),3)
    timestamp = "%02d:%02d:%02d.%03d" % (h_int, m_int, sec_int, ms)
    return timestamp


def martian_time_to_millisec(timestamp, mars_second_on=False):
    ts_s = [float(x) for x in timestamp.split(':')]
    # ts_s = [hours, minutes, seconds]
    if mars_second_on:
        martian_second = round((SOL_LENGTH/DAY_LENGTH)*1000.0,1)
        milliseconds = (ts_s[2]+ts_s[1]*60+ts_s[0]*3600)*martian_second
    else:
        milliseconds = (ts_s[2]+ts_s[1]*60+ts_s[0]*3600)*1000
    return round(milliseconds,0)


def process_negative_diff(p_epoch_date, p_input_date, mars_second_on=False):
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
    tt = format_raw_time(SOL_LENGTH-ms_residual, mars_second_on)
    yyyy = - full_cycle_years - years_accumulated - 1
    mm = months_accumulated
    dd= days_accumulated
    wd = WEEKDAYS[(days_accumulated-1) % 7]
    return("Mars DateTime: %05d-%02d-%02d %s, %s" % (yyyy, mm, dd, tt, wd))


def process_positive_diff(p_epoch_date, p_input_date, p_mars_second_on=False):
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
    tt = format_raw_time(ms_residual, p_mars_second_on)
    # adds ones where necessary
    yyyy = full_cycle_years + years_accumulated + 1
    mm = months_accumulated + 1
    dd = days_accumulated + 1
    wd = WEEKDAYS[days_accumulated % 7]
    return("Mars DateTime: %04d-%02d-%02d %s, %s" %(yyyy, mm, dd, tt, wd))


def process_positive_diff_inv(input_date, p_mars_second_on=False):
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
    ms_total = ms_total + martian_time_to_millisec(datetimes[1], p_mars_second_on)
    return ms_total

 
def process_negative_diff_inv(p_input_date, p_mars_second_on=False):
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
    time_to_ms = martian_time_to_millisec(datetimes[1],p_mars_second_on)
    ms_total = ms_total + (SOL_LENGTH - time_to_ms)
    return -ms_total


def earth_datetime_to_mars_datetime(input_date, p_mars_second_on=False):
    epoch_date = datetime.fromisoformat(EPOCH)
    if (epoch_date<=input_date):
        return process_positive_diff(epoch_date, input_date, p_mars_second_on)
    else:
        return process_negative_diff(epoch_date, input_date, p_mars_second_on)


def mars_datetime_to_earth_datetime(input_date, p_mars_second_on=False):
    if input_date[0] == '-':
        return process_negative_diff_inv(input_date[1:], p_mars_second_on)
    else:
        return process_positive_diff_inv(input_date, p_mars_second_on)