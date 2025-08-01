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


def errors_test():
    calendar_year_length = sum(YEAR_CYCLE)/len(YEAR_CYCLE)
    annual_error = (((calendar_year_length- MARS_YEAR_LENGTH)*SOL_LENGTH)/1000)
    seconds_per_year = (MARS_YEAR_LENGTH*SOL_LENGTH)/1000
    mars_years_to_1_sol_error = (SOL_LENGTH/1000)/annual_error
    earth_years_to_1_sol_error = (mars_years_to_1_sol_error*MARS_YEAR_LENGTH*SOL_LENGTH)/(DAY_LENGTH*EARTH_YEAR_LENGTH)

    print("%s: %s" % (STR_AVG_YEAR_LENGTH, calendar_year_length))
    print("%s: %s" % (STR_ANNUAL_ERROR, annual_error))
    print("%s: %s" % (STR_MARS_YEARS_TO_1SOL_ERROR, mars_years_to_1_sol_error))
    print("%s: %s" % (STR_EARTH_YEARS_TO_1SOL_ERROR, earth_years_to_1_sol_error))


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
    remaining_sols = cycle_count_frac*len(YEAR_CYCLE)
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
    
    # calculat time
    remaining_milliseconds = remaining_milliseconds - date_integer*SOL_LENGTH
    formatted_time = format_raw_time(remaining_milliseconds)

    # prepare data for display
    month_display = current_month_int+1
    date_display = date_integer + 1
    day_week = DAYS[date_integer % 7]

    return("Mars DateTime: %04d-%02d-%02d %s, %s" %(current_year,month_display,date_display,formatted_time,day_week))


def process_negative_diff(p_epoch_date, p_input_date):
    pass

def mars_date_time_to_earth_datetime(input_date):
    # split into YYYY-MM-DD format
    values = input_date.split()
    date_values = values[0].split('-')
    year = date_values[0]
    month = date_values[1]
    date = date_values[2] 
    print(int(year))
    print(int(month))
    print(int(date))


def earth_datetime_to_mars_datetime(input_date):
    # Calculate year
    epoch_date = datetime.fromisoformat(EPOCH)
    if (epoch_date<=input_date):
        return process_positive_diff(epoch_date, input_date)
    else:
        return process_negative_diff(epoch_date, input_date)
    


def utc_to_mars_time_tests():
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
    print("Earth DateTime: %s" % timedate2.strftime("%Y-%m-%d %H:%M:%S+%Z, %A"))
    print(earth_datetime_to_mars_datetime(timedate2))

    # test start day + 2 months
    milliseconds_to_add = timedelta(milliseconds=SOL_LENGTH*112)
    timedate3 = timedate0 + milliseconds_to_add
    print("Earth DateTime: %s" % timedate3.strftime("%Y-%m-%d %H:%M:%S+%Z, %A"))
    print(earth_datetime_to_mars_datetime(timedate3))

    # test end of december
    timedate4 = datetime.fromisoformat("2000-01-06T00:00:00Z")
    print("Earth DateTime: %s" % timedate4.strftime("%Y-%m-%d %H:%M:%S+%Z, %A"))
    print(earth_datetime_to_mars_datetime(timedate4))

    # test negatives
    timedate_A = timedate0 - timedelta(milliseconds=100)
    #print("Earth DateTime: %s" % timedate_A.strftime("%Y-%m-%d %H:%M:%S+%Z, %A"))
    #print(earth_datetime_to_mars_datetime(timedate_A))
    # test negatives
    timedate_B = timedate0 - timedelta(milliseconds=DAY_LENGTH*365.25)
    #print("Earth DateTime: %s" % timedate_B.strftime("%Y-%m-%d %H:%M:%S+%Z, %A"))
    #print(earth_datetime_to_mars_datetime(timedate_B))

     # test negatives
    timedate_C = timedate0 - timedelta(milliseconds=DAY_LENGTH*365.25*25)
    #print("Earth DateTime: %s" % timedate_C.strftime("%Y-%m-%d %H:%M:%S+%Z, %A"))
    #print(earth_datetime_to_mars_datetime(timedate_C))


def test_data_run_2():
    test_date_1 = "0001-01-01 00:00:00.000, Monday"
    mars_date_time_to_earth_datetime(test_date_1)

def main():
    # errors_test()
    utc_to_mars_time_tests()
    # test_data_run_2()
    timedate = datetime.now(timezone.utc)
    print("Earth DateTime: %s" % timedate.strftime("%Y-%m-%d %H:%M:%S+%Z, %A"))
    print(earth_datetime_to_mars_datetime(timedate))

main()