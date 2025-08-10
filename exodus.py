#!/usr/bin/env python3
import argparse
from datetime import datetime, timezone
from src.exodus_calendar.utils import earth_datetime_to_mars_datetime, mars_datetime_to_earth_datetime
from src.exodus_calendar.utils import WEEKDAYS, EARTH_TIMEZONE

def main():
    parser = argparse.ArgumentParser(
        prog='exodus.py',
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
        try:
            input_date = datetime.fromisoformat(args.EARTH_DATETIME)
            print(earth_datetime_to_mars_datetime(input_date))
        except:
            print("Input date is not in the correct format!")
            print("Correct example below:")
            print("exodus.py -e '2025-01-01 00:00:01+00:00'")
    elif args.MARS_DATETIME is not None:
        try:
            milliseconds_from_epoch = mars_datetime_to_earth_datetime(args.MARS_DATETIME)
            output_date = datetime.fromtimestamp(milliseconds_from_epoch/1000,EARTH_TIMEZONE)
            print("Earth DateTime: %s, %s" % (output_date, WEEKDAYS[output_date.weekday()]))
        except:
            print("Input date is not in the correct format!")
            print("Correct example below:")
            print("exodus.py -m '0030-03-51 12:26:45.556'")
    else:
        timedate = datetime.now(timezone.utc)
        timedate_str = timedate.strftime("%Y-%m-%d %H:%M:%S.%f+%Z, %A")
        print("Earth DateTime: %s, %s" % (timedate_str[:23], timedate_str[32:]))
        mars_date_earth_second = earth_datetime_to_mars_datetime(timedate, False)
        mars_date_mars_second = earth_datetime_to_mars_datetime(timedate, True)
        print(mars_date_earth_second)
        print(mars_date_mars_second)

main()