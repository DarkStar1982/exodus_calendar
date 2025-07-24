# EXODUS CALENDAR FOR MARS
Revision 2025.07.24

## INTRODUCTION
Martian calendar would be useful for future martian colonists, but there isn't any such commonly agreed today. Existing proposals (e.g Darian calendar) seem to be overly complicated and require to memorize too many new terms. Accuracy, simplicity and reuse of the names we already have for months and days of the week are desirable.

A degree of synchronicity between Earth and Mars timekeeping would be also desirable.


## DESCRIPTION
I suggest the following scheme:

Using northward equinox year (668.5907 sols) as reference year length, create a calendar based on 22-year cycle:
 
- eleven 669-sol years (odd years - first, third, fifth and so on)
- ten 668-sol years (even years - second, fourth, sixth and so on.)
- one 670-sol year (last year only)

5 such cycles (110 Martian years) will form a Martian "century", which will be approximately equal to 200 Earth years, given some degree of cross-referencing dates between two planets. The name of each cycle in the "century" can be flavoured for cosmetic purposes ("Earth", "Water", "Air", "Fire", "Aether"), but completely optional.

This gives an average duration of calendar year as 668.5909(09) sols, a difference of 0.00021 sols per year, similar to Gregorian calendar (0.0003 days per year.  It would  be reasonably accurate (an error of 1 sol after 4782.6 Martian years) for foreseeable future. Adjustments as Martian year length inevitably drift (+0.00079 sols per 1,000 Martian years[1]) can be done as required, in a manner to similar adjustments done on Earth.

Starting epoch is chosed to be same as Unix time (January 1st 1970) - subject to discussion! 1971 year would seem more appropriate as this was the year of first Martian missions reaching the planet (Mars 2 and 3, Mariner 9).

Years are composed of 12 months with same name as terrestrial ones, each with 56 days with the exception of December, which will have variable length - 52, 53 or 54 days. Weeks are 7-days with the same duration and day names as on Earth (Monday, Tuesday, etc.) and each month will have 8 weeks. All months start on Monday and end on Sunday, with only final week of December terminating on Wednesday, Thursday or Friday, depending on the year length. All new years start on Monday as well. 

This concepts allow minimal amount of new information to remember (essentially, just the 22-year cycle structure and two month lengths, one constant and one depending on the year in the cycle.)

## DEMO
A simple reference code is available that allows conversions between terrestrial and Martian dates. Pull requests accepted. Should be packaged into a library soon. 

## MISC
Part of the bigger Prometheus Unbound project (a knowledge base for future Martian colonists).
Subscribe to our YT channel:
https://www.youtube.com/@exodusorbitals4092

Support us financially on Artizen:
https://artizen.fund/index/p/prometheus-unbound?season=5
