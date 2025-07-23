#!/opt/homebrew/bin/python3

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
MONTHS = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December"
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

def earth_datetime_to_mars_datetime(p_timestamp):
    print(p_timestamp)

def mars_datetime_to_earth_datetime(p_timestamp):
    print(p_timestamp)

def main():
    errors_test()
    earth_datetime_to_mars_datetime("TEST 1")
    mars_datetime_to_earth_datetime("TEST 2")

main()