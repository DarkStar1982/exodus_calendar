#!/opt/homebrew/bin/python3
from math import modf, ceil
from datetime import datetime, timezone

#######################################
############## CONSTANTS ##############
#######################################

# Start year same as in Unix time
# Preliminary date, can be changed
EPOCH = "1970-01-01T00:00:00Z"

# Martian day length in milliseconds
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
    668, # 1
    669, #2
    668, # 2
    669, #3
    668, # 3
    669, #4
    668, # 4
    669, #5
    668, # 5
    669, #6
    668, # 6
    669, #7
    668, # 7
    669, #8
    668, # 8
    669, #9
    668, # 9
    669, #10
    668, # 10  
    669, #11
    670  #1
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
    return "%s:%s:%2.3f" % (int(hours_int), int(minutes_int), seconds_raw)


def earth_datetime_to_mars_datetime(input_date):
    epoch_date = datetime.fromisoformat(EPOCH)
    diff = input_date - epoch_date

    milliseconds_since_epoch = diff.total_seconds()*1000
    milliseconds_per_22y_cycle = sum(YEAR_CYCLE)*SOL_LENGTH

    cycle_count = milliseconds_since_epoch/milliseconds_per_22y_cycle

    year_raw = cycle_count*len(YEAR_CYCLE)
    year_frac, year_int = modf(year_raw)
    
    cycle_count_frac, cycle_count_int = modf(cycle_count)
    current_year_in_cycle = int(cycle_count_frac*len(YEAR_CYCLE))+1
    length_of_year = YEAR_CYCLE[current_year_in_cycle-1]
    
    current_sol = length_of_year*year_frac
    raw_month = current_sol/MARS_MONTH_LENGTH;
    raw_sol_frac, raw_sol_int = modf(raw_month)

    year_adj = ceil(year_raw)+1
    month_adj = ceil(raw_month)
    if raw_month<11:
        raw_sol_time = raw_sol_frac*MARS_MONTH_LENGTH
        sol_month_adj = ceil(raw_sol_time)+1
    else:
        last_month_length = LAST_MONTH_LENGTH[length_of_year]
        raw_sol_time = raw_sol_frac*last_month_length
        sol_month_adj = ceil(raw_sol_time)+1
    
    raw_sol_time_frac, raw_sol_time_int = modf(raw_sol_time)
    day_of_the_week = (DAYS[sol_month_adj % 7])
    formatted_time = format_raw_time(raw_sol_time_frac*SOL_LENGTH)

    print("Mars:  %04d-%02d-%s %s, %s" %(year_adj,month_adj+1,sol_month_adj,formatted_time,day_of_the_week))

def main():
    # errors_test()
    timedate = datetime.now(timezone.utc)
    print("Earth: %s" % timedate.strftime("%Y-%m-%d %H:%M:%S+%Z, %A"))
    earth_datetime_to_mars_datetime(timedate)

main()