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

# Martian months and duration - 11 months x 56 days, 1 month variable duration
# Alternatively, name after Zodiacal signs (European or Chinese)?
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
# Purely a cosmetic feature
CYCLES = ['Earth', 'Water', 'Air', 'Fire', 'Aether']

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

def sols_to_month(p_sol):
    raw_month = p_sol/MARS_MONTH_LENGTH
    raw_month_frac, raw_month_int = modf(raw_month)
    return (int(raw_month_int)+1,raw_month_frac)

def month_residual_to_date(p_month, p_residual, p_year_length):
    raw_date = p_residual*MARS_MONTH_LENGTH
    raw_date_frac, raw_date_int = modf(raw_date)
    raw_date_int = floor(raw_date_int+1.0)
    return (raw_date_int,raw_date_frac)

def day_of_the_weeka(p_date):
    return (DAYS[int(p_date) % 7])

def earth_datetime_to_mars_datetime(input_date):
    # Calculate year
    epoch_date = datetime.fromisoformat(EPOCH)
    diff = input_date - epoch_date
    #print(time.time()*1000) <-within 1 millisecond of diff
    milliseconds_since_epoch = diff.total_seconds()*1000 
    #print(milliseconds_since_epoch)
    cycle_years_total_sols = sum(YEAR_CYCLE)
    milliseconds_per_22y_cycle = cycle_years_total_sols*SOL_LENGTH
    assert(milliseconds_per_22y_cycle == 1305795063996)

    cycle_count = milliseconds_since_epoch/milliseconds_per_22y_cycle
    
    year_raw = cycle_count*len(YEAR_CYCLE) + 1 # No Year 0
    year_frac, year_int = modf(year_raw)
    cycle_count_frac, cycle_count_int = modf(cycle_count)

    year_in_cycle = cycle_count_frac*len(YEAR_CYCLE)
    year_count_frac, year_count_int = modf(year_in_cycle)
    current_year_in_cycle = int(year_count_int)
    length_of_year = YEAR_CYCLE[current_year_in_cycle]
    current_sol = length_of_year*year_frac
    current_sol_frac, current_sol_int = modf(current_sol)
    month, residual = sols_to_month(current_sol)
    date_month, date_month_residual = (month_residual_to_date(month,residual,length_of_year))
    date_adj = date_month

    day_week = day_of_the_weeka(date_adj-1)
    assert(current_sol_frac-date_month_residual<1e-13)
    formatted_time = format_raw_time(current_sol_frac*SOL_LENGTH)

    print("Mars DateTime:  %04d-%02d-%02d %s, %s" %(year_int,month,date_month,formatted_time,day_week))

def test_data_run():
    # test first date - should be year 1
    timedate0 = datetime.fromisoformat(EPOCH)
    #print("Earth DateTime: %s" % timedate0.strftime("%Y-%m-%d %H:%M:%S+%Z, %A"))
    #earth_datetime_to_mars_datetime(timedate0)

    # test start day + 1 day
    milliseconds_to_add = timedelta(milliseconds=DAY_LENGTH)
    timedate1 = timedate0 + milliseconds_to_add
    #print("Earth DateTime: %s" % timedate1.strftime("%Y-%m-%d %H:%M:%S+%Z, %A"))
    #earth_datetime_to_mars_datetime(timedate1)

    # test start day + 1 sol
    milliseconds_to_add = timedelta(milliseconds=SOL_LENGTH)
    timedate2 = timedate0 + milliseconds_to_add
    #print("Earth DateTime: %s" % timedate2.strftime("%Y-%m-%d %H:%M:%S+%Z, %A"))
    #earth_datetime_to_mars_datetime(timedate2)

    # test start day + 1 year
    milliseconds_to_add = timedelta(milliseconds=DAY_LENGTH*365.25)
    #timedate3 = timedate0 + milliseconds_to_add
    #print("Earth DateTime: %s" % timedate3.strftime("%Y-%m-%d %H:%M:%S+%Z, %A"))
    #earth_datetime_to_mars_datetime(timedate3)

    timedate4 = datetime.fromisoformat("2000-01-06T00:00:00Z")
    milliseconds_to_sub = timedelta(milliseconds=88775244)

    timedate5 = timedate4 + 28.75055*milliseconds_to_sub
    print("Earth DateTime: %s" % timedate5.strftime("%Y-%m-%d %H:%M:%S+%Z, %A"))
    earth_datetime_to_mars_datetime(timedate5)



def main():
    # errors_test()
    test_data_run()
    timedate = datetime.now(timezone.utc)
    #print("Earth DateTime: %s" % timedate.strftime("%Y-%m-%d %H:%M:%S+%Z, %A"))
    #earth_datetime_to_mars_datetime(timedate)

main()