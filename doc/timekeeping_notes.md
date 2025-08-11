## Notes on Martian timekeeping.
Martian sol (day) is 24 h 39 m 35.244 seconds long.

Therefore a convinient convention is to define Martian secodn as 1.0275 of Earth one and use 
same amount of hours, minutes and seconds for any day-to-day timekeeping needs.

However... second is a fundamental unit in all of our science and engineering, so there is a 
need to maintain a clear distinction between the two.

The library itself uses milliseconds internally for most of the conversion calculations, converting timestamps to and from ones with Martian seconds where necessary.

Future Martian settlers should probably use a different name for their "second" of 1027.5 ms duration or use millisecond as fundamental time unit.