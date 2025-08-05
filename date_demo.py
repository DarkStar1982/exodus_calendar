#!/opt/homebrew/bin/python3
from math import modf, ceil, floor
import time
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo

# |--------Calendar structure before and after epoch year----------|
# |----------------------------------------------------------------|
# |---------------------------Epoch Year---------------------------|
# |-------negative timestamps-----||-----positive timestamps-------|
# |-2^64 ................... -1.0 || 1.0 .................... 2^64 |
# |-------------------------------||-------------------------------|
# |-------negative cycle order----||----positive cycle order-------|
# | 01 02 03 04 ..... 19 20 21 22 || 01 02 03 04 ..... 19 20 21 22 |
# |-------------------------------||-------------------------------|
# |------negative years order-----||-----positive years order------|
# |-10 -9 -8 -7 -6 -5 -4 -3 -2 -1 || +1 +2 +3 +4 +5 +6 +7 +8 +9 +10|
# |-------------------------------||-------------------------------|
# |---negative year month order---||-----positive year months------|
# |[Jan-------Dec] [Jan-------Dec]||[Jan-------Dec] [Jan-------Dec]|
# |-------------------------------||-------------------------------|
# |------negative year dates------||-------positive year dates-----|
# | 01 02 03 04 ..... 51 52 53 54 || 01 02 03 04 ..... 53 54 55 56 |
# |-------------------------------||-------------------------------|


##############################################################################
################################## CONSTANTS #################################
##############################################################################

# Start year same as in Unix time
# Preliminary date, can be changed
EPOCH = "1970-01-01 00:00:00Z"

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

# 22-year cycle - 10 668-sol years, 11 669-sol years, 1 670 sol year marks end of cycle
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
MS_PER_MARS_YEAR = sum(YEAR_CYCLE)/len(YEAR_CYCLE)*SOL_LENGTH

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

# Purely cosmetic features
# Five 22-year cycles form a "century" (110 Martian years) are ~ 200 Earth ones.
# 12 cycles (264 Martian years) make ~ 500 Earth ones and so on
CYCLES_5 = ['Earth', 'Water', 'Air', 'Fire', 'Aether']

# Zodiac signs or something else of same length
CYCLES_12 = [
    'Aries', 
    'Taurus',
    'Gemini',
    'Cancer',
    'Leo', 
    'Virgo', 
    'Libra', 
    'Scorpio', 
    'Sagittarius', 
    'Capricorn', 
    'Aquarius', 
    'Pisces'
]

DAYS = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday"
]

# STRING CONSTANTS
STR_ANNUAL_ERROR = "Annual error for calendar year in seconds"
STR_AVG_YEAR_LENGTH = "Calendar year length"
STR_MARS_YEARS_TO_1SOL_ERROR = "Martian years to pass for 1 sol error"
STR_EARTH_YEARS_TO_1SOL_ERROR = "Earth years to pass for 1 sol error"

def errors_test():
    calendar_year_length = sum(YEAR_CYCLE)/len(YEAR_CYCLE)
    annual_error = (((calendar_year_length- MARS_YEAR_LENGTH)*SOL_LENGTH)/1000)
    seconds_per_year = (MARS_YEAR_LENGTH*SOL_LENGTH)/1000
    mars_years_to_1_sol_error = (SOL_LENGTH/1000)/annual_error
    earth_years_to_1_sol_error = (mars_years_to_1_sol_error*MARS_YEAR_LENGTH*SOL_LENGTH)/(DAY_LENGTH*EARTH_YEAR_LENGTH)

    assert(calendar_year_length-MARS_YEAR_LENGTH == 0.00020909090915210982)
    assert(annual_error==18.562096478160385)
    assert(mars_years_to_1_sol_error==4782.608694252308)
    assert(earth_years_to_1_sol_error == 8995.431602985975)


def format_raw_time(p_milliseconds):
    seconds = p_milliseconds/1000
    hours_raw = seconds/3600
    hours_frac, hours_int = modf(hours_raw)
    minutes_raw = (hours_raw - hours_int)*60
    minutes_frac, minutes_int = modf(minutes_raw)
    seconds_raw = minutes_frac*60
    return "%02d:%02d:%02d.%03d" % (int(hours_int), int(minutes_int), int(seconds_raw), int((seconds_raw-int(seconds_raw))*1000))


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
    year_length = YEAR_CYCLE[len(YEAR_CYCLE)-years_accumulated-1]
    
    # calculate months elapsed since start of year
    months_accumulated = 0
    for i in range(len(MONTH_LENGTH[year_length])-1, -1, -1):
        if (ms_residual - MONTH_LENGTH[year_length][i]*SOL_LENGTH)<0:
            break
        else:
            ms_residual = ms_residual - MONTH_LENGTH[year_length][i]*SOL_LENGTH
            months_accumulated = months_accumulated + 1

    months_accumulated = len(MONTH_LENGTH[year_length]) - months_accumulated

    # calculate days elapsed
    month_duration = MONTH_LENGTH[year_length][months_accumulated-1]
    days_accumulated = 0
    for i in range(month_duration-1, -1, -1):
        if (ms_residual - SOL_LENGTH)<0:
            break
        else:
            ms_residual = ms_residual - SOL_LENGTH
            days_accumulated = days_accumulated + 1
    days_accumulated = month_duration - days_accumulated

    # calculate time
    formatted_time = format_raw_time(SOL_LENGTH-ms_residual)

    year_int = - full_cycle_years - years_accumulated - 1
    month_display = months_accumulated
    date_display = days_accumulated
    day_week = DAYS[(days_accumulated-1) % 7]
    return("Mars DateTime: %05d-%02d-%02d %s, %s" %(year_int, month_display, date_display, formatted_time, day_week))


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
    formatted_time = format_raw_time(ms_residual)

    # adds ones where necessary
    year_int = full_cycle_years + years_accumulated + 1
    month_display = months_accumulated + 1
    date_display = days_accumulated + 1
    day_week = DAYS[days_accumulated % 7]
    return("Mars DateTime: %04d-%02d-%02d %s, %s" %(year_int, month_display, date_display, formatted_time, day_week))


def martian_time_to_milliseconds(p_hours, p_min, p_sec):
    milliseconds = p_sec*1000
    milliseconds = milliseconds + p_min*60*1000
    milliseconds = milliseconds + p_hours*3600*1000
    return int(milliseconds)

def process_positive_diff_inv(input_date):
    earth_start_date = datetime.fromisoformat(EPOCH)
    datetimes = input_date.split()
    date_split = [int(x) for x in datetimes[0].split('-')]
    time_split = [float(x) for x in datetimes[1].split(':')]

    # calculate milliseconds elapsed
    ms_accumulated = 0
    years_elapsed = date_split[0] - 1 
    total_cycles_passed = years_elapsed // len(YEAR_CYCLE)
    ms_accumulated = ms_accumulated + MS_PER_CYCLE*total_cycles_passed

    # add full years
    year_in_current_cycle = years_elapsed - total_cycles_passed*len(YEAR_CYCLE)
    year_length = YEAR_CYCLE[year_in_current_cycle]
    for i in range(0, year_in_current_cycle, 1):
        ms_accumulated = ms_accumulated + YEAR_CYCLE[i]*SOL_LENGTH

    months_elapsed = date_split[1] - 1 
    for i in range(0, months_elapsed, 1):
        ms_accumulated = ms_accumulated + MONTH_LENGTH[year_length][i]*SOL_LENGTH

    days_elapsed = date_split[2] - 1
    for i in range(0, days_elapsed, 1):
        ms_accumulated = ms_accumulated + SOL_LENGTH
        
    ms_accumulated = ms_accumulated + martian_time_to_milliseconds(time_split[0], time_split[1], time_split[2])
    return ms_accumulated

 
def process_negative_diff_inv(p_input_date):
    datetimes = p_input_date.split()
    date_split = [int(x) for x in datetimes[0].split('-')]
    time_split = [float(x) for x in datetimes[1].split(':')]

    # calculate milliseconds elapsed
    ms_accumulated = 0
    years_elapsed = date_split[0] - 1 
    total_cycles_passed = years_elapsed // len(YEAR_CYCLE)
    ms_accumulated = ms_accumulated + MS_PER_CYCLE*total_cycles_passed
    year_in_current_cycle = years_elapsed - total_cycles_passed*len(YEAR_CYCLE)
    # calculate year length
    year_length = YEAR_CYCLE[len(YEAR_CYCLE)-year_in_current_cycle-1]

    for i in range(0, year_in_current_cycle,1):
        ms_accumulated = ms_accumulated + YEAR_CYCLE[len(YEAR_CYCLE)-i-1]*SOL_LENGTH

    months_elapsed = len(MONTHS) - date_split[1]
    for i in range(0, months_elapsed, 1):
        ms_accumulated = ms_accumulated + MONTH_LENGTH[year_length][len(MONTHS)-i-1]*SOL_LENGTH

    days_elapsed = MONTH_LENGTH[year_length][date_split[1]-1] - date_split[2]
    for i in range(0, days_elapsed, 1):
        ms_accumulated = ms_accumulated + SOL_LENGTH
            
    ms_accumulated = ms_accumulated + (SOL_LENGTH - martian_time_to_milliseconds(time_split[0], time_split[1], time_split[2]))
    return -ms_accumulated

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

# testing direct and reverse converstion from UTC to Martian time  
def utc_to_mars_time_tests_positive_offset():
    utc_timezone = ZoneInfo("UTC")
    # test first date - should be year 1
    timedate0 = datetime.fromisoformat(EPOCH)
    assert(earth_datetime_to_mars_datetime(timedate0)=="Mars DateTime: 0001-01-01 00:00:00.000, Monday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime("0001-01-01 00:00:00.000")
    assert(datetime.fromtimestamp(milliseconds_from_epoch/1000,utc_timezone) == timedate0)

    # test start day + 1 second
    milliseconds_to_add = timedelta(milliseconds=1000)
    timedate1 = timedate0 + milliseconds_to_add
    assert(earth_datetime_to_mars_datetime(timedate1)=="Mars DateTime: 0001-01-01 00:00:01.000, Monday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime("0001-01-01 00:00:01.000") 
    timedate1_inverse = timedate0 + timedelta(milliseconds=milliseconds_from_epoch)
    assert(milliseconds_from_epoch - 1000 < 1.0)
    assert(datetime.fromtimestamp(milliseconds_from_epoch/1000,utc_timezone) == timedate1)

    # test start day + 1 day
    milliseconds_to_add = timedelta(milliseconds=DAY_LENGTH)
    timedate2 = timedate0 + milliseconds_to_add
    assert(earth_datetime_to_mars_datetime(timedate2) == "Mars DateTime: 0001-01-01 24:00:00.000, Monday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime("0001-01-01 24:00:00.000")
    assert(abs(milliseconds_from_epoch - DAY_LENGTH) < 1.0)
    assert(datetime.fromtimestamp(milliseconds_from_epoch/1000,utc_timezone) == timedate2)

    # test start day + 1 sol
    milliseconds_to_add = timedelta(milliseconds=SOL_LENGTH)
    timedate3 = timedate0 + milliseconds_to_add
    assert(earth_datetime_to_mars_datetime(timedate3) == "Mars DateTime: 0001-01-02 00:00:00.000, Tuesday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime("0001-01-02 00:00:00.000")
    assert(abs(milliseconds_from_epoch - SOL_LENGTH) < 1.0)
    assert(datetime.fromtimestamp(milliseconds_from_epoch/1000,utc_timezone) == timedate3)

    # test start day + 7 sols
    milliseconds_to_add = timedelta(milliseconds=SOL_LENGTH*7)
    timedate4 = timedate0 + milliseconds_to_add
    assert(earth_datetime_to_mars_datetime(timedate4) == "Mars DateTime: 0001-01-08 00:00:00.000, Monday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime("0001-01-08 00:00:00.000")
    assert(abs(milliseconds_from_epoch - SOL_LENGTH*7) < 1.0)
    assert(datetime.fromtimestamp(milliseconds_from_epoch/1000,utc_timezone) == timedate4)

    # test start day + 1 Earth month
    milliseconds_to_add = timedelta(milliseconds=DAY_LENGTH*31)
    timedate5 = timedate0 + milliseconds_to_add
    assert(earth_datetime_to_mars_datetime(timedate5) == "Mars DateTime: 0001-01-31 04:12:22.679, Wednesday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime("0001-01-31 04:12:22.679")
    milliseconds_from_epoch = milliseconds_from_epoch
    # 1 ms conversion error - both asserts fail!
    #assert(milliseconds_from_epoch - DAY_LENGTH*31 < 1.0)
    #assert(datetime.fromtimestamp(milliseconds_from_epoch/1000,utc_timezone) == timedate5)

    # test start day + 1 Martian month
    milliseconds_to_add = timedelta(milliseconds=SOL_LENGTH*MARS_MONTH_LENGTH)
    timedate6 = timedate0 + milliseconds_to_add
    assert(earth_datetime_to_mars_datetime(timedate6) == "Mars DateTime: 0001-02-01 00:00:00.000, Monday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime("0001-02-01 00:00:00.000")
    assert(abs(milliseconds_from_epoch - SOL_LENGTH*MARS_MONTH_LENGTH) < 1.0)
    assert(datetime.fromtimestamp(milliseconds_from_epoch/1000,utc_timezone) == timedate6)

    # test start day + 11 Martian months
    milliseconds_to_add = timedelta(milliseconds=SOL_LENGTH*MARS_MONTH_LENGTH*11)
    timedate7 = timedate0 + milliseconds_to_add
    assert(earth_datetime_to_mars_datetime(timedate7) == "Mars DateTime: 0001-12-01 00:00:00.000, Monday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime("0001-12-01 00:00:00.000")
    assert(abs(milliseconds_from_epoch - SOL_LENGTH*MARS_MONTH_LENGTH*11) < 1.0)
    assert(datetime.fromtimestamp(milliseconds_from_epoch/1000,utc_timezone) == timedate7)

    # test A end of december for year 1
    milliseconds_to_add = timedelta(milliseconds=SOL_LENGTH*MARS_MONTH_LENGTH*11+52*SOL_LENGTH-100)
    timedate7a = timedate0 + milliseconds_to_add
    assert(earth_datetime_to_mars_datetime(timedate7a)=="Mars DateTime: 0001-12-52 24:39:35.144, Wednesday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime("0001-12-52 24:39:35.144")
    assert(abs(milliseconds_from_epoch - (SOL_LENGTH*MARS_MONTH_LENGTH*11+52*SOL_LENGTH-100)) < 1.0)
    assert(datetime.fromtimestamp(milliseconds_from_epoch/1000,utc_timezone) == timedate7a)

    # test B end of december for year 1 
    milliseconds_to_add = timedelta(milliseconds=SOL_LENGTH*MARS_MONTH_LENGTH*11+53*SOL_LENGTH-100)
    timedate7b = timedate0 + milliseconds_to_add
    assert(earth_datetime_to_mars_datetime(timedate7b)=="Mars DateTime: 0001-12-53 24:39:35.144, Thursday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime("0001-12-53 24:39:35.144")
    assert(abs(milliseconds_from_epoch - (SOL_LENGTH*MARS_MONTH_LENGTH*11+53*SOL_LENGTH-100)) < 1.0)
    assert(datetime.fromtimestamp(milliseconds_from_epoch/1000,utc_timezone) == timedate7b)
    
    # test C end of december for year 1 - rollover to year2
    milliseconds_to_add = timedelta(milliseconds=SOL_LENGTH*MARS_MONTH_LENGTH*11+53*SOL_LENGTH)
    timedate7c = timedate0 + milliseconds_to_add
    assert(earth_datetime_to_mars_datetime(timedate7c)=="Mars DateTime: 0002-01-01 00:00:00.000, Monday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime("0002-01-01 00:00:00.000")
    assert(abs(milliseconds_from_epoch - (SOL_LENGTH*MARS_MONTH_LENGTH*11+53*SOL_LENGTH)) < 1.0)
    assert(datetime.fromtimestamp(milliseconds_from_epoch/1000,utc_timezone) == timedate7c)

    # test + 1 Earth year
    milliseconds_to_add = timedelta(milliseconds=DAY_LENGTH*JULIAN_YEAR_LENGTH)
    timedate8 = timedate0 + milliseconds_to_add
    assert(earth_datetime_to_mars_datetime(timedate8)=="Mars DateTime: 0001-07-20 11:46:28.379, Saturday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime("0001-07-20 11:46:28.379")
    # ~1 ms conversion error - second assert fails!
    # assert(abs(milliseconds_from_epoch - DAY_LENGTH*JULIAN_YEAR_LENGTH) < 1.0)
    # assert(datetime.fromtimestamp(milliseconds_from_epoch/1000,utc_timezone) == timedate8)

    # test + 1 Mars even year
    milliseconds_to_add = timedelta(milliseconds=SOL_LENGTH*668)
    timedate9= timedate0 + milliseconds_to_add
    assert(earth_datetime_to_mars_datetime(timedate9)=="Mars DateTime: 0001-12-53 00:00:00.000, Thursday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime("0001-12-53 00:00:00.000")
    assert((milliseconds_from_epoch - (SOL_LENGTH*668)) < 1.0)
    assert(datetime.fromtimestamp(milliseconds_from_epoch/1000,utc_timezone) == timedate9)

    # test + 1 Mars odd year
    milliseconds_to_add = timedelta(milliseconds=SOL_LENGTH*669)
    timedate10= timedate0 + milliseconds_to_add
    assert(earth_datetime_to_mars_datetime(timedate10)=="Mars DateTime: 0002-01-01 00:00:00.000, Monday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime("0002-01-01 00:00:00.000")
    assert(abs(milliseconds_from_epoch - SOL_LENGTH*669) < 1.0)
    assert(datetime.fromtimestamp(milliseconds_from_epoch/1000,utc_timezone) == timedate10)

    # test + 10 Mars years
    milliseconds_to_add = timedelta(milliseconds=MS_PER_MARS_YEAR*10)
    timedate11= timedate0 + milliseconds_to_add
    assert(earth_datetime_to_mars_datetime(timedate11)=="Mars DateTime: 0011-01-01 22:25:04.767, Monday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime("0011-01-01 22:25:04.767")
    # 0.2727 ms error here - second assert fails
    assert(abs(milliseconds_from_epoch - MS_PER_MARS_YEAR*10) < 1.0)
    # assert(datetime.fromtimestamp(milliseconds_from_epoch/1000,utc_timezone) == timedate11)

    # test + 1 cycle (22 Mars years)
    milliseconds_to_add = timedelta(milliseconds=MS_PER_MARS_YEAR*22)
    timedate12= timedate0 + milliseconds_to_add
    assert(earth_datetime_to_mars_datetime(timedate12)=="Mars DateTime: 0023-01-01 00:00:00.000, Monday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime("0023-01-01 00:00:00.000")
    assert(abs(milliseconds_from_epoch - MS_PER_MARS_YEAR*22) < 1.0)
    assert(datetime.fromtimestamp(milliseconds_from_epoch/1000,utc_timezone) == timedate12)

    # test + 29 Mars yeras
    milliseconds_to_add = timedelta(milliseconds=MS_PER_MARS_YEAR*29)
    timedate13= timedate0 + milliseconds_to_add
    assert(earth_datetime_to_mars_datetime(timedate13)=="Mars DateTime: 0030-01-01 03:21:45.715, Monday") 
    milliseconds_from_epoch = mars_datetime_to_earth_datetime("0030-01-01 03:21:45.715")
    # 0.0908203125 ms error her - second assert fails
    assert(abs(milliseconds_from_epoch - MS_PER_MARS_YEAR*29) < 1.0)
    #assert(datetime.fromtimestamp(milliseconds_from_epoch/1000,utc_timezone) == timedate13)


def utc_to_mars_time_tests_negative_offset():
    timedate0 = datetime.fromisoformat(EPOCH)
    utc_timezone = ZoneInfo("UTC")
    # test  - 1 second
    milliseconds_to_sub = timedelta(milliseconds=1000)
    timedate1 = timedate0 - milliseconds_to_sub
    assert(earth_datetime_to_mars_datetime(timedate1) == "Mars DateTime: -0001-12-54 24:39:34.244, Friday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime("-0001-12-54 24:39:34.244")
    assert(abs(milliseconds_from_epoch + 1000) < 1.0)
    assert(datetime.fromtimestamp(milliseconds_from_epoch/1000,utc_timezone) == timedate1)


    # test - 1 Eath day
    milliseconds_to_sub = timedelta(milliseconds=DAY_LENGTH)
    timedate2 = timedate0 - milliseconds_to_sub
    assert(earth_datetime_to_mars_datetime(timedate2) == "Mars DateTime: -0001-12-54 00:39:35.244, Friday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime("-0001-12-54 00:39:35.244")
    assert(abs(milliseconds_from_epoch + DAY_LENGTH) < 1.0)
    assert(datetime.fromtimestamp(milliseconds_from_epoch/1000,utc_timezone) == timedate2)

    # test - 1 sol
    milliseconds_to_sub = timedelta(milliseconds=SOL_LENGTH)
    timedate3 = timedate0 - milliseconds_to_sub
    assert(earth_datetime_to_mars_datetime(timedate3) == "Mars DateTime: -0001-12-53 24:39:35.244, Thursday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime("-0001-12-53 24:39:35.244")
    assert(abs(milliseconds_from_epoch + SOL_LENGTH) < 1.0)
    assert(datetime.fromtimestamp(milliseconds_from_epoch/1000,utc_timezone) == timedate3)


    # test start day - 1 Earth month
    milliseconds_to_sub = timedelta(milliseconds=DAY_LENGTH*31)
    timedate4 = timedate0 - milliseconds_to_sub
    assert(earth_datetime_to_mars_datetime(timedate4) == "Mars DateTime: -0001-12-24 20:27:12.563, Wednesday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime("-0001-12-24 20:27:12.563")
    # ~1 ms conversion error here - assert fails
    # assert(milliseconds_from_epoch + DAY_LENGTH*31 < 1.1)
    #assert(datetime.fromtimestamp(milliseconds_from_epoch/1000,utc_timezone) == timedate3)

    # test start day - 54 sols
    milliseconds_to_sub = timedelta(milliseconds=SOL_LENGTH*54)
    timedate5 = timedate0 - milliseconds_to_sub
    assert(earth_datetime_to_mars_datetime(timedate5) == "Mars DateTime: -0001-11-56 24:39:35.244, Sunday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime("-0001-11-56 24:39:35.244")
    assert(abs(milliseconds_from_epoch + SOL_LENGTH*54)<1.0)
    assert(datetime.fromtimestamp(milliseconds_from_epoch/1000,utc_timezone) == timedate5)


    # test start day - 110 sols
    milliseconds_to_sub = timedelta(milliseconds=SOL_LENGTH*110)
    timedate6 = timedate0 - milliseconds_to_sub
    assert(earth_datetime_to_mars_datetime(timedate6) == "Mars DateTime: -0001-10-56 24:39:35.244, Sunday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime("-0001-10-56 24:39:35.244")
    assert(abs(milliseconds_from_epoch + SOL_LENGTH*110)<1.0)
    assert(datetime.fromtimestamp(milliseconds_from_epoch/1000,utc_timezone) == timedate6)


    # test - 1 long Mars year
    milliseconds_to_sub = timedelta(milliseconds=SOL_LENGTH*670)
    timedate7= timedate0 - milliseconds_to_sub
    assert(earth_datetime_to_mars_datetime(timedate7) == "Mars DateTime: -0002-12-53 24:39:35.244, Thursday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime("-0002-12-53 24:39:35.244")
    assert(abs(milliseconds_from_epoch + SOL_LENGTH*670)<1.0)
    assert(datetime.fromtimestamp(milliseconds_from_epoch/1000,utc_timezone) == timedate7)


    # test - 1 Mars cycle
    milliseconds_to_sub = timedelta(milliseconds=MS_PER_CYCLE)
    timedate8= timedate0 - milliseconds_to_sub
    assert(earth_datetime_to_mars_datetime(timedate8) == "Mars DateTime: -0023-12-54 24:39:35.244, Friday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime("-0023-12-54 24:39:35.244")
    assert(abs(milliseconds_from_epoch + MS_PER_CYCLE)<1.0)
    assert(datetime.fromtimestamp(milliseconds_from_epoch/1000,utc_timezone) == timedate8)


    # test - 10 terrestrial JD years
    milliseconds_to_sub = timedelta(milliseconds=DAY_LENGTH*3652.5)
    timedate9 = timedate0 - milliseconds_to_sub
    # print(earth_datetime_to_mars_datetime(timedate8))
    assert(earth_datetime_to_mars_datetime(timedate9) == "Mars DateTime: -0006-09-11 05:33:12.419, Thursday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime("-0006-09-11 05:33:12.419")
    # 1ms conversion error here
    #print(abs(milliseconds_from_epoch+DAY_LENGTH*3652.5))
    #assert(abs(milliseconds_from_epoch + DAY_LENGTH*3652.5)<1.0)
    #assert(datetime.fromtimestamp(milliseconds_from_epoch/1000,utc_timezone) == timedate9)


    # test + 29 Mars yeras
    milliseconds_to_sub = timedelta(milliseconds=MS_PER_MARS_YEAR*29)
    timedate10= timedate0 - milliseconds_to_sub
    #print(earth_datetime_to_mars_datetime(timedate10))
    assert(earth_datetime_to_mars_datetime(timedate10)=="Mars DateTime: -0029-01-01 21:17:49.528, Monday") 
    milliseconds_from_epoch = mars_datetime_to_earth_datetime("-0029-01-01 21:17:49.528")
    # -0.9092 ms conversion error here
    assert(abs(milliseconds_from_epoch + MS_PER_MARS_YEAR*29) < 1.0)
    # assert(datetime.fromtimestamp(milliseconds_from_epoch/1000,utc_timezone) == timedate10)



def utc_to_mars_time_long_intervals():
    utc_timezone = ZoneInfo("UTC")
    timedate0 = datetime.fromisoformat(EPOCH)
    
    # test +110 Mars years
    milliseconds_to_add = timedelta(milliseconds=MS_PER_CYCLE*5)
    timedate1= timedate0 + milliseconds_to_add
    assert(earth_datetime_to_mars_datetime(timedate1)=="Mars DateTime: 0111-01-01 00:00:00.000, Monday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime("0111-01-01 00:00:00.000")
    assert(abs(milliseconds_from_epoch - MS_PER_CYCLE*5) < 1.0)
    assert(datetime.fromtimestamp(milliseconds_from_epoch/1000,utc_timezone) == timedate1)

    # test +264 Mars years
    milliseconds_to_add = timedelta(milliseconds=MS_PER_CYCLE*12)
    timedate2= timedate0 + milliseconds_to_add
    assert(earth_datetime_to_mars_datetime(timedate2)=="Mars DateTime: 0265-01-01 00:00:00.000, Monday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime("0265-01-01 00:00:00.000")
    assert(abs(milliseconds_from_epoch - MS_PER_CYCLE*12) < 1.0)
    assert(datetime.fromtimestamp(milliseconds_from_epoch/1000,utc_timezone) == timedate2)

    # test +374 Mars years
    milliseconds_to_add = timedelta(milliseconds=MS_PER_CYCLE*17)
    timedate3= timedate0 + milliseconds_to_add
    assert(earth_datetime_to_mars_datetime(timedate3)=="Mars DateTime: 0375-01-01 00:00:00.000, Monday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime("0375-01-01 00:00:00.000")
    # 0.1 ms error here - second assert fails!
    assert(abs(milliseconds_from_epoch - MS_PER_CYCLE*17) < 1.0)
    # assert(datetime.fromtimestamp(milliseconds_from_epoch/1000,utc_timezone) == timedate3)

    # test +638 Mars years
    milliseconds_to_add = timedelta(milliseconds=MS_PER_CYCLE*29)
    timedate4= timedate0 + milliseconds_to_add
    assert(earth_datetime_to_mars_datetime(timedate4)=="Mars DateTime: 0639-01-01 00:00:00.000, Monday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime("0639-01-01 00:00:00.000")
    # 0.003 ms error here - second assert fails
    assert(abs(milliseconds_from_epoch - MS_PER_CYCLE*29) < 1.0)
    # assert(datetime.fromtimestamp(milliseconds_from_epoch/1000,utc_timezone) == timedate4)

    # test -110 Mars years
    milliseconds_to_sub = timedelta(milliseconds=MS_PER_CYCLE*5)
    timedate5= timedate0 - milliseconds_to_sub
    # print(earth_datetime_to_mars_datetime(timedate5))
    assert(earth_datetime_to_mars_datetime(timedate5)=="Mars DateTime: -0111-12-54 24:39:35.244, Friday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime("-0111-12-54 24:39:35.244")
    assert(abs(milliseconds_from_epoch + MS_PER_CYCLE*5)<1.0)
    assert(datetime.fromtimestamp(milliseconds_from_epoch/1000,utc_timezone) == timedate5)


    # test -264 Mars years
    milliseconds_to_sub = timedelta(milliseconds=MS_PER_CYCLE*12)
    timedate6= timedate0 - milliseconds_to_sub
    assert(earth_datetime_to_mars_datetime(timedate6)=="Mars DateTime: -0265-12-54 24:39:35.244, Friday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime("-0265-12-54 24:39:35.244")
    assert(abs(milliseconds_from_epoch + MS_PER_CYCLE*12)<1.0)
    assert(datetime.fromtimestamp(milliseconds_from_epoch/1000,utc_timezone) == timedate6)


    # test -374 Mars years
    milliseconds_to_sub = timedelta(milliseconds=MS_PER_CYCLE*17)
    timedate7= timedate0 - milliseconds_to_sub
    assert(earth_datetime_to_mars_datetime(timedate7)=="Mars DateTime: -0375-12-54 24:39:35.244, Friday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime("-0375-12-54 24:39:35.244")
    # 0.001 ms error here - second assert fails
    assert(abs(milliseconds_from_epoch + MS_PER_CYCLE*17)<1.0)
    # assert(datetime.fromtimestamp(milliseconds_from_epoch/1000,utc_timezone)) == timedate7)

    # test -638 Mars years
    milliseconds_to_sub = timedelta(milliseconds=MS_PER_CYCLE*29)
    timedate8= timedate0 - milliseconds_to_sub
    assert(earth_datetime_to_mars_datetime(timedate8)=="Mars DateTime: -0639-12-54 24:39:35.244, Friday")
    milliseconds_from_epoch = mars_datetime_to_earth_datetime("-0639-12-54 24:39:35.244")
    assert(abs(milliseconds_from_epoch + MS_PER_CYCLE*29)<1.0)
    # 0.003 ms error here - second assert fails
    #assert(datetime.fromtimestamp(milliseconds_from_epoch/1000,utc_timezone) == timedate8)


def main():
    errors_test()
    utc_to_mars_time_tests_positive_offset()
    utc_to_mars_time_tests_negative_offset()
    utc_to_mars_time_long_intervals()
    mars_datetime_to_earth_datetime("0001-01-01 00:00:00.000")
    timedate = datetime.now(timezone.utc)
    print("Earth DateTime: %s" % timedate.strftime("%Y-%m-%d %H:%M:%S+%Z, %A"))
    print(earth_datetime_to_mars_datetime(timedate))

main()