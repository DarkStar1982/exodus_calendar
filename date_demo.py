#!/opt/homebrew/bin/python3
from math import modf, ceil, floor
import time
from datetime import datetime, timezone, timedelta

#######################################
############## CONSTANTS ##############
#######################################

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

# 1305795063996 milliseconds
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

LAST_MONTH_LENGTH = {
    668:52,
    669:53,
    670:54
}

# Five 22-year cycles form a "century", 
# 110 Martian years are ~ 200 Earth ones.
# 12 cycles make ~ 500 Earth ones
# Purely cosmetic features
CYCLES_5 = ['Earth', 'Water', 'Air', 'Fire', 'Aether']

# Zodiac signs or something else of same duration
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


# |----------------Schematics of the cycles and years--------------|
# |----------------------------------------------------------------|
# |---------------------------epoch year---------------------------|
# |-------------------------------||-------------------------------|
# |--------negative offsets-------||-------positive offsets--------|
# |-------------------------------||-------------------------------|
# |---------negative years--------||--------positive years---------|
# |-10 -9 -8 -7 -6 -5 -4 -3 -2 -1 || +1 +2 +3 +4 +5 +6 +7 +8 +9 +10|
# |-------------------------------||-------------------------------|
# |-------negative cycle order----||----positive cycle order-------|
# | 01 02 03 04 ..... 19 20 21 22 || 01 02 03 04 ..... 19 20 21 22 |
# |-------------------------------||-------------------------------|
# |------negative year months-----||-----positive year months------|
# |[Jan-------Dec] [Jan-------Dec]||[Jan-------Dec] [Jan-------Dec]|
# |-------------------------------||-------------------------------|

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


def process_positive_diff(p_epoch_date, p_input_date):
    diff = p_input_date - p_epoch_date
    # timedelta since start of calendar
    milliseconds_since_epoch = diff.total_seconds()*1000 # or time.time()*1000, within 1 millisecond of diff

    # how many 22 year cycles has passed since beginning of epoch
    cycle_count = milliseconds_since_epoch/MS_PER_CYCLE
    cycle_count_frac, cycle_count_int = modf(cycle_count)

    full_year_count = cycle_count_int*len(YEAR_CYCLE) + 1 # No Year 0
    remaining_milliseconds = milliseconds_since_epoch - cycle_count_int*MS_PER_CYCLE
    year_since_last_cycle = remaining_milliseconds/MS_PER_MARS_YEAR

    # calculate year in the cycle
    year_in_cycle = int(year_since_last_cycle)
    current_year = full_year_count + year_in_cycle
    year_selected_length = YEAR_CYCLE[year_in_cycle]
    
    # calculate month
    remaining_milliseconds = remaining_milliseconds - year_in_cycle*MS_PER_MARS_YEAR
    current_month_int = floor(remaining_milliseconds/(MARS_MONTH_LENGTH*SOL_LENGTH))
    
    # calculate date
    remaining_milliseconds = remaining_milliseconds - current_month_int*SOL_LENGTH*MARS_MONTH_LENGTH
    date_residual = remaining_milliseconds/SOL_LENGTH
    date_integer = floor(date_residual)
    
    # calculate time
    remaining_milliseconds = remaining_milliseconds - date_integer*SOL_LENGTH
    formatted_time = format_raw_time(remaining_milliseconds)

    # prepare data for display
    month_display = current_month_int+1
    date_display = date_integer + 1
    day_week = DAYS[date_integer % 7]

    return("Mars DateTime: %04d-%02d-%02d %s, %s" %(current_year,month_display,date_display,formatted_time,day_week))


def process_negative_diff(p_epoch_date, p_input_date):
    diff = p_input_date - p_epoch_date
    milliseconds_since_epoch = diff.total_seconds()*1000 # or time.time()*1000, within 1 millisecond of diff
    absolute_milliseconds = abs(milliseconds_since_epoch)

    # calculat remaining milliseconds before end of year
    cycles_elapsed = absolute_milliseconds / MS_PER_CYCLE
    cycle_count_frac, cycle_count_int = modf(cycles_elapsed)
    total_years_elapsed = cycle_count_int*len(YEAR_CYCLE) +cycle_count_frac*len(YEAR_CYCLE)
    year_in_cycle = len(YEAR_CYCLE) - cycle_count_frac*len(YEAR_CYCLE)
    year_in_cycle_frac, year_in_cycle_int = modf(year_in_cycle)
    total_years_elapsed_frac, total_years_elapsed_int = modf(total_years_elapsed)
    year_length = YEAR_CYCLE[int(year_in_cycle_int)]
    years_since_cycle_start = floor(cycle_count_frac*len(YEAR_CYCLE))

    # here might be mistakes!
    remaining_milliseconds = abs(MS_PER_CYCLE*cycle_count_int + years_since_cycle_start*MS_PER_MARS_YEAR  - absolute_milliseconds)
    remaining_milliseconds = year_length*SOL_LENGTH - remaining_milliseconds
    
    #calculate month 
    current_month_int = floor(remaining_milliseconds/(MARS_MONTH_LENGTH*SOL_LENGTH))

    # calculate date 
    remaining_milliseconds = remaining_milliseconds - current_month_int*SOL_LENGTH*MARS_MONTH_LENGTH
    date_residual = remaining_milliseconds/SOL_LENGTH
    date_integer = floor(date_residual)

    # calculate time
    remaining_milliseconds = remaining_milliseconds - date_integer*SOL_LENGTH
    formatted_time = format_raw_time(remaining_milliseconds)
    
    # prepare data for display
    month_display = current_month_int+1
    date_display = date_integer + 1
    day_week = DAYS[date_integer % 7]
    year_int = - floor(total_years_elapsed)-1
    return("Mars DateTime: %05d-%02d-%02d %s, %s" %(year_int,month_display,date_display,formatted_time,day_week))

def earth_datetime_to_mars_datetime(input_date):
    # Calculate year
    epoch_date = datetime.fromisoformat(EPOCH)
    if (epoch_date<=input_date):
        return process_positive_diff(epoch_date, input_date)
    else:
        return process_negative_diff(epoch_date, input_date)

def mars_date_time_to_earth_datetime(input_date):
    # split into YYYY-MM-DD format
    values = input_date.split()
    date_values = values[0].split('-')
    year = date_values[0]
    month = date_values[1]
    date = date_values[2] 
    #print(int(year))
    #print(int(month))
    #print(int(date)) 

def utc_to_mars_time_tests_positive_offset():
    # test first date - should be year 1
    timedate0 = datetime.fromisoformat(EPOCH)
    assert(earth_datetime_to_mars_datetime(timedate0)=="Mars DateTime: 0001-01-01 00:00:00.000, Monday")

    # test start day + 1 day
    milliseconds_to_add = timedelta(milliseconds=DAY_LENGTH)
    timedate1 = timedate0 + milliseconds_to_add
    assert(earth_datetime_to_mars_datetime(timedate1) == "Mars DateTime: 0001-01-01 24:00:00.000, Monday")

    # test start day + 1 sol
    milliseconds_to_add = timedelta(milliseconds=SOL_LENGTH)
    timedate2 = timedate0 + milliseconds_to_add
    assert(earth_datetime_to_mars_datetime(timedate2) == "Mars DateTime: 0001-01-02 00:00:00.000, Tuesday")

    # test start day + 7 sol
    milliseconds_to_add = timedelta(milliseconds=SOL_LENGTH*7)
    timedate3 = timedate0 + milliseconds_to_add
    assert(earth_datetime_to_mars_datetime(timedate3) == "Mars DateTime: 0001-01-08 00:00:00.000, Monday")

    # test start day + 1 Earth month
    milliseconds_to_add = timedelta(milliseconds=DAY_LENGTH*31)
    timedate4 = timedate0 + milliseconds_to_add
    assert(earth_datetime_to_mars_datetime(timedate4) == "Mars DateTime: 0001-01-31 04:12:22.679, Wednesday")

    # test start day + 1 Martian month
    milliseconds_to_add = timedelta(milliseconds=SOL_LENGTH*MARS_MONTH_LENGTH)
    timedate5 = timedate0 + milliseconds_to_add
    assert(earth_datetime_to_mars_datetime(timedate5) == "Mars DateTime: 0001-02-01 00:00:00.000, Monday")

    # test start day + 11 Martian months
    milliseconds_to_add = timedelta(milliseconds=SOL_LENGTH*MARS_MONTH_LENGTH*11)
    timedate6 = timedate0 + milliseconds_to_add
    assert(earth_datetime_to_mars_datetime(timedate6) == "Mars DateTime: 0001-12-01 00:00:00.000, Monday")

    # test end of december
    milliseconds_to_add = timedelta(milliseconds=SOL_LENGTH*MARS_MONTH_LENGTH*11+52*SOL_LENGTH-100)
    timedate7 = timedate0 + milliseconds_to_add
    assert(earth_datetime_to_mars_datetime(timedate7)=="Mars DateTime: 0001-12-52 24:39:35.144, Wednesday")
    
    # test + 1 Earth year
    milliseconds_to_add = timedelta(milliseconds=DAY_LENGTH*365.2425)
    timedate8 = timedate0 + milliseconds_to_add
    assert(earth_datetime_to_mars_datetime(timedate8)=="Mars DateTime: 0001-07-20 11:35:40.379, Saturday")

    # test + 1 Mars even year
    milliseconds_to_add = timedelta(milliseconds=SOL_LENGTH*668)
    timedate9= timedate0 + milliseconds_to_add
    assert(earth_datetime_to_mars_datetime(timedate9)=="Mars DateTime: 0001-12-53 00:00:00.000, Thursday")

    # test + 1 Mars year average
    milliseconds_to_add = timedelta(milliseconds=SOL_LENGTH*668.5909091)
    timedate10= timedate0 + milliseconds_to_add
    assert(earth_datetime_to_mars_datetime(timedate10)=="Mars DateTime: 0002-01-01 00:00:00.000, Monday")

    # test + 10 Mars years
    milliseconds_to_add = timedelta(milliseconds=SOL_LENGTH*10*668.590909091)
    timedate11= timedate0 + milliseconds_to_add
    assert(earth_datetime_to_mars_datetime(timedate11)=="Mars DateTime: 0011-01-01 00:00:00.000, Monday")

    # test + 29 Mars years
    milliseconds_to_add = timedelta(milliseconds=SOL_LENGTH*29*668.590909091)
    timedate12= timedate0 + milliseconds_to_add
    assert(earth_datetime_to_mars_datetime(timedate12)=="Mars DateTime: 0030-01-01 00:00:00.000, Monday")

def utc_to_mars_time_tests_negative_offset():
    timedate0 = datetime.fromisoformat(EPOCH)

    # test  - 1 second
    milliseconds_to_sub = timedelta(milliseconds=1000)
    timedate1 = timedate0 - milliseconds_to_sub
    assert(earth_datetime_to_mars_datetime(timedate1) == "Mars DateTime: -0001-12-54 24:39:34.244, Friday")

    # test - 1 day
    milliseconds_to_sub = timedelta(milliseconds=DAY_LENGTH)
    timedate2 = timedate0 - milliseconds_to_sub
    assert(earth_datetime_to_mars_datetime(timedate2) == "Mars DateTime: -0001-12-54 00:39:35.244, Friday")

    # test - 1 sol
    milliseconds_to_sub = timedelta(milliseconds=SOL_LENGTH)
    timedate3 = timedate0 - milliseconds_to_sub
    assert(earth_datetime_to_mars_datetime(timedate3) == "Mars DateTime: -0001-12-54 00:00:00.000, Friday")

    # test - 10 terrestrial JD years
    milliseconds_to_sub = timedelta(milliseconds=10*DAY_LENGTH*365.25)
    timedate4 = timedate0 - milliseconds_to_sub
    assert(earth_datetime_to_mars_datetime(timedate4) == "Mars DateTime: -0006-09-10 04:25:57.181, Wednesday")

    # test - 29 Mars years
    milliseconds_to_sub = timedelta(milliseconds=SOL_LENGTH*29*668.590909091)
    timedate5= timedate0 - milliseconds_to_sub
    #print("Earth DateTime: %s" % timedate5.strftime("%Y-%m-%d %H:%M:%S+%Z, %A"))
    #print(earth_datetime_to_mars_datetime(timedate5))


def main():
    errors_test()
    utc_to_mars_time_tests_positive_offset()
    utc_to_mars_time_tests_negative_offset()
    timedate = datetime.now(timezone.utc)
    print("Earth DateTime: %s" % timedate.strftime("%Y-%m-%d %H:%M:%S+%Z, %A"))
    print(earth_datetime_to_mars_datetime(timedate))

main()