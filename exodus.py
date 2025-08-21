#!/usr/bin/env python3
import argparse
from datetime import datetime, timezone, timedelta
from src.exodus_calendar.utils import earth_datetime_to_mars_datetime, mars_datetime_to_earth_datetime
from src.exodus_calendar.utils import WEEKDAYS, EARTH_TIMEZONE, EPOCH

def main():
    parser = argparse.ArgumentParser(
        prog='exodus.py',
        description='Converts the time and date between Earth and Mars.'
    )
    parser.add_argument(
        '-m',
        "--mtc_to_utc", 
        type=str, 
        dest='MARS_DATETIME_UTC', 
        help='convert Mars datetime (in MTC) to Earth one (in UTC)'
    )
    parser.add_argument(
        '-u',
        "--utc_to_mtc", 
        type=str, 
        dest='EARTH_DATETIME_MTC', 
        help='convert Earth datetime (in UTC) to Mars one (in MTC)'
    )
    parser.add_argument(
        '-r',
        "--utc_to_raw", 
        type=str, 
        dest='EARTH_DATETIME_RAW', 
        help='convert Earth datetime in UTC to Mars one (with 1000ms seconds)'
    )
    parser.add_argument(
        '-x',
        "--raw_to_utc", 
        type=str, 
        dest='MARS_DATETIME_RAW', 
        help='convert Mars datetime (with 1000ms seconds) to Earth one in UTC'
    )

    args = parser.parse_args()
    if args.EARTH_DATETIME_MTC is not None:
        try:
            input_date = datetime.fromisoformat(args.EARTH_DATETIME_MTC)
            print(earth_datetime_to_mars_datetime(input_date, True))
        except:
            print("Input date is not in the correct format!")
            print("Correct example below:")
            print("exodus.py -u '2025-01-01 00:00:01+00:00'")
    elif args.MARS_DATETIME_UTC is not None:
        try:
            timedate_str = mars_datetime_to_earth_datetime(args.MARS_DATETIME_UTC, True, False)
            print("Earth DateTime: %s" % timedate_str)
        except:
            print("Input date is not in the correct format!")
            print("Correct example below:")
            print("exodus.py -m '0030-03-51 12:26:45.556'")
    elif args.EARTH_DATETIME_RAW is not None:
        try:
            input_date = datetime.fromisoformat(args.EARTH_DATETIME_RAW)
            print(earth_datetime_to_mars_datetime(input_date, False))
        except:
            print("Input date is not in the correct format!")
            print("Correct example below:")
            print("exodus.py -r '2025-01-01 00:00:01+00:00'")
    elif args.MARS_DATETIME_RAW is not None:
        try:
            timedate_str = mars_datetime_to_earth_datetime(args.MARS_DATETIME_RAW, False, False)
            print("Earth DateTime: %s" % timedate_str)
        except:
            print("Input date is not in the correct format!")
            print("Correct example below:")
            print("exodus.py -x '0030-03-51 12:26:45.556'")

    else:
        timedate = datetime.now(timezone.utc)
        timedate_str = timedate.strftime("%Y-%m-%d %H:%M:%S.%f+%Z, %A")
        print("Earth DateTime [UTC]: %s, %s" % (timedate_str[:23], timedate_str[32:]))
        mars_date_mars_second = earth_datetime_to_mars_datetime(timedate, True)
        print(" Mars DateTime [MTC]: %s" % mars_date_mars_second)


main()