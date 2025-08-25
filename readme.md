# EXODUS CALENDAR FOR MARS
Revision 2025.08.24

## INTRODUCTION
An accurate and user-friendly Martian calendar would be invaluable for future Martian
colonists, yet no commonly accepted system exists today. Current proposals, such as the
Darian calendar [1], may appear overly complex and demand memorization of numerous
unfamiliar terms. The ideal Martian calendar should combine both accuracy and simplicity, retaining familiar month and weekday names. Additionally, maintaining some degree of
backwards compatibility with existing Martian timekeeping solutions would be highly beneficial.

## DEFINITIONS
* The duration of Martian solar day (“sol”), that is, the time for the plane to rotate around its axis with respect to the Sun is currently 24 hours 39 minutes and 35.244 seconds (88775.244 seconds, equal to 1.02749125 Earth solar days)

* The duration of Martian tropical year (orbital period with respect to the Sun) is 668.5921 sols, but for the planetary calendar purposes, time between vernal equinoxes is often used, as in Gregorian calendar, allowing more close alignment with seasons of the year. In Mars case, this value is equal to 668.5907 sols [1, p. 3]


## DESCRIPTION
I propose the following scheme:

Using the northward equinox year (668.5907 sols) as the reference year length, this
calendar operates on a 22-year cycle:
- Ten 668-sol years (even-numbered years: second, fourth, sixth, etc.)
- Eleven 669-sol years (odd-numbered years: first, third, fifth, etc.)
- One 670-sol year (leap year)

In one sentence, rephrased: _odd years are 669 sols, even years are 668 sols except when divisible by 22, then they are 670 sol long._

Each year comprises 12 months bearing the same names as their terrestrial counterparts,
with each containing 56 sols except December, which varies in length: 52, 53, or 54 sols.
Weeks maintain the familiar seven-day structure with Earth’s weekday names (Monday,
Tuesday, etc.), and each month contains exactly eight weeks. All months begin on Monday
and conclude on Sunday, with only December's final week ending on Wednesday,
Thursday, or Friday, depending on the year's length. Every new year begins on Monday.

![martian calendar](https://raw.githubusercontent.com/DarkStar1982/exodus_calendar/master/doc/infographics.png "Infographics")

This concept requires minimal new information to memorize: essentially just the 22-year cycle structure and two month lengths: one constant and one dependent on the year's position within the cycle.

### EPOCH
The epoch date and time is provisionally set to Mars vernal equinox of April 11, 1955, at UTC 19:21:51 to keep the calendar aligned with planetary seasons and in sync with MST (Mean Solar Time). Years are counted from 1, and negative years start from -1, as in Gregorian calendar (i.e. there is no year 0).

![Calendar epoch structure](https://raw.githubusercontent.com/DarkStar1982/exodus_calendar/master/doc/calendar_epochs.png "Structure of cycles and years before and after epoch starting year")

### ACCURACY

_Calendar Year Length=(668 x 10 + 669 x 11 + 670)/22_

This yields an average calendar year duration of 668.5909(09) sols, creating a naive error estimate of 0.00021 sols per year, comparable to the Gregorian calendar's 0.00013-day annual discrepancy. If no other factors take into account, such a system would remain reasonably accurate for the foreseeable future, accumulating an error of only 1 sol after approximately 4,782 Martian years, assuming fixed duration of Mars northward equinox year. But as the Martian year length is known to drift (+0.00079 sols per 1,000 Martian years [1, p3]), more accurate error expression that includes annual duration drift can be expressed as following:

$$
Accumulated\ Error(sols) = \int_0^t \left(\frac{668 \times 10 + 669 \times 11 + 670}{22} - (668.5907 + 0.00079t/1000)\right) dt
$$

Solving for t, error expression becomes: 

$$
2.1 \times 10^{-4}𝑡 - 3.95 \times 10^{-7}𝑡^2
$$

So 1 sol error will accumulate in 1878 Martian years (approximately 3532 Earth ones), illustrated below:

![error chart](https://raw.githubusercontent.com/DarkStar1982/exodus_calendar/master/doc/accuracy.png "Accuracy")

## SOURCE CODE
A simple command-line utility ("exodus.py") is is available that allows conversions between terrestrial (UTC) and Martian (in MTC) dates. Packaged into library that is available on PyPi:
https://pypi.org/project/exodus-calendar/


## CODE USAGE
Import from PyPi. Functions of value are in exodus_orbitals.utils:

- **earth_datetime_to_mars_datetime(input_date, mars_sec_on)**. 
Converts timestamp in UTC to Martian date time. 

- **mars_datetime_to_earth_datetime_as_isoformat(input_date, mars_sec_on)** 
Converts Martian timestamp to Earth one in UTC as datetime object

- **mars_datetime_to_earth_datetime_as_string(input_date, mars_sec_on)** 
Converts Martian timestamp to Earth one in UTC as string

- **mars_datetime_to_earth_datetime_as_ms(input_date, mars_sec_on)** 
Converts Martian timestamp to Earth one as milliseconds since calendar epoch (not Unix epoch!)

- **compute_mars_timedelta(date_a, date_b, mars_sec_on)** 
Computes time delta in milliseconds between two Martian dates. Returns _date_b - date_a_

- **add_timedelta_to_mars_date(date, millis, mars_sec_on)** 
Adds time delta in millisecond to a Martian date. Returns Martian date.

_"mars_sec_on"_ parameter allows to use either standard second (1000 ms) when False or Martian second (1027.5 ms) when True for more convienient 24-hour timekeeping. When used, the time returned will be in sync with (unofficial) MTC timezone - time at zero Martian meridian, Mars equivalent to UTC. Set to False by default.


## SUPPORT PROJECT DEVELOPMENT 
https://www.paypal.com/paypalme/DenysSilin


## SUBSCRIBE TO AUTHOR'S YOUTUBE CHANNEL
https://www.youtube.com/@exodusorbitals4092

## REFERENCES

1. Gangale, Thomas. (2006). The Architecture of Time, Part 2: The Darian System for Mars. SAE Technical Papers. 10.4271/2006-01-2249. 