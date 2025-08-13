# EXODUS CALENDAR FOR MARS
Revision 2025.08.12

## INTRODUCTION
An accurate and user-friendly Martian calendar would be invaluable for future Martian
colonists, yet no commonly accepted system exists today. Current proposals, such as the
Darian calendar [1], appear overly complex and demand memorization of numerous
unfamiliar terms. The ideal system should prioritize accuracy and simplicity while retaining
familiar month and weekday names. Additionally, maintaining some degree of
synchronization between Earth and Mars timekeeping systems would be highly beneficial


## DESCRIPTION
I propose the following scheme:

Using the northward equinox year (668.5907 sols) as the reference year length, this
calendar operates on a 22-year cycle:
- Ten 668-sol years (even-numbered years: second, fourth, sixth, etc.)
- Eleven 669-sol years (odd-numbered years: first, third, fifth, etc.)
- One 670-sol year (final year only)

Each year comprises 12 months bearing the same names as their terrestrial counterparts,
with each containing 56 sols except December, which varies in length: 52, 53, or 54 sols.
Weeks maintain the familiar seven-day structure with Earth’s weekday names (Monday,
Tuesday, etc.), and each month contains exactly eight weeks. All months begin on Monday
and conclude on Sunday, with only December's final week ending on Wednesday,
Thursday, or Friday, depending on the year's length. Every new year begins on Monday.

![martian calendar](https://raw.githubusercontent.com/DarkStar1982/exodus_calendar/master/doc/infographics.png "Infographics")

Five complete cycles (110 Martian years) constitute a Martian "century," roughly equivalent to 200 Earth years, facilitating cross-referencing between planetary calendars. Each cycle within the century may optionally receive thematic names for distinction ("Earth," "Water," "Air," "Fire," "Aether"), though this remains purely cosmetic

### ACCURACY

_Calendar Year Length=(668 x 10 + 669 x 11 + 670)/22_

This yields an average calendar year duration of 668.5909(09) sols, creating a difference of 0.00021 sols per year, comparable to the Gregorian calendar's 0.0003-day annual discrepancy. The system would remain reasonably accurate for the foreseeable future, accumulating an error of only 1 sol after approximately 4,782 Martian years. As the Martian year length inevitably drifts (+0.00079 sols per 1,000 Martian years [1, p3]), adjustments can be implemented as needed, like those made to Earth's calendar system

### EPOCH
The starting epoch is provisionally set to commonly used Mars calendar epoch (11 April, 1955) and epoch time to be aligned with MTC, though this remains open to discussion. Unix epoch (midnight, 1 Jan 1970) can be used as well. The epoch year of 1971 might be more appropriate, as it
marked the first successful Martian missions reaching the planet - Mars 2 and 3 from the
USSR, and Mariner 9 from the USA. Other dates are acceptable for consideration.

![Calendar epoch structure](https://raw.githubusercontent.com/DarkStar1982/exodus_calendar/master/doc/calendar_epochs.png "Structure of cycles and years before and after epoch starting year")

### EASE OF USE
This concept requires minimal new information to memorize—essentially just the 22-year cycle structure and two month lengths: one constant and one dependent on the year's position within the cycle.


### OPTIONAL FEATURES
Multiples of 22-year cycles, specifically 5, 12, 17, and 29, correspond approximately to
200, 500, 700, and 1,200 Earth years respectively, enabling a degree of cross-referencing
between two planetary calendars. Thematic cycle names can be used for additional
aesthetics (for example, "Earth," "Water," "Air," "Fire," and "Aether" for a five-cycle period).

## SOURCE CODE
A simple command-line utility ("exodus.py") is is available that allows conversions between terrestrial (UTC) and Martian (in MTC) dates. Packaged into library that is available on PyPi.

## MISC
Part of the bigger Prometheus Unbound project (a knowledge base for future Martian colonists):
https://github.com/DarkStar1982/prometheus_unbound

Subscribe to our YT channel:
https://www.youtube.com/@exodusorbitals4092

## SUPPORT DEVELOPMENT 
https://www.paypal.com/paypalme/DenysSilin

## REFERENCES

1. Gangale, Thomas. (2006). The Architecture of Time, Part 2: The Darian System for Mars. SAE Technical Papers. 10.4271/2006-01-2249. 