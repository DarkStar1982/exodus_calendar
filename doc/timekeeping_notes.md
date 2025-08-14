## Notes on Martian timekeeping.
Martian sol (day) is 24 h 39 m 35.244 seconds long.

Therefore a convinient convention is to define Martian secodn as 1.0275 of Earth one and use 
same amount of hours, minutes and seconds for any day-to-day timekeeping needs.

However... second is a fundamental unit in all of our science and engineering, so there is a 
need to maintain a clear distinction between the two.

The library itself uses milliseconds internally for most of the conversion calculations, converting timestamps to and from ones with Martian seconds where necessary.

Future Martian settlers should probably use a different name for their "second" of 1027.5 ms duration or use millisecond as fundamental time unit.


## NTP (Re-)implementation.
Because we don't want to confuse Earth-local and Mars-local times and timekeeping, a separate fork of NTP can be created to synchronize the Martian clocks across the users. As we don't expect any significant difference in timekeeping on different planets, other than requried by choice of local time. A simplified version of protocol can work initially, with the expectatio of eventual feature-parity with NTPv4

## Martian Network Time Protocol Proposed Packet Structure

As with NTP, it should contain some info on time source, required timestamps and checksum. Note that martian seconds can be either equal to Earth second (1000 ms) or smeared to 1027.5 ms to mantain the convieniens 24-hour sol. This should be specified explicitely by the users.

+-------+0---------------1---------------2---------------3--------------+
|BITS   | 0 1 2 3 4 5 6 7 0 1 2 3 4 5 6 7 0 1 2 3 4 5 6 7 0 1 2 3 4 5 6 7  
+-------+----+-----+-----+------+--------+---------------+--------------+
|00-31  | SC | LI  | VN  | Mode |Stratum |       Poll    |   Precision  |
+-------+---------------------------------------------------------------+
|32-63  | 					Root Delay                                  |
+-------+---------------------------------------------------------------+
|64-95  |                   Root Dispersion                             |
+-------+---------------------------------------------------------------+
|96-127 |  					Reference ID                                |
+-------+---------------------------------------------------------------+
|128-159|			        REFERENCE TIMESTAMP                         |
|160-191|                                                               |
+-------+---------------------------------------------------------------+
|192-223|			        ORIGIN TIMESTAMP                            |
|224-255|                                                               |
+-------+---------------------------------------------------------------+
|256-287|			        RECEIVE TIMESTAMP                           |
|288-319|                                                               |
+-------+---------------------------------------------------------------+
|320-351|			        TRANSMIT TIMESTAMP                          |
|352-383|                                                               |
+-------+---------------------------------------------------------------+
|384-415| 					128-bit CHECKSUM                            |
|416-447|                                                               |
|448-479|                                                               |
|480-512|                                                               |
+-------+---------------------------------------------------------------+

## Fields Explained

* SC - which second are we using to propagate timestamps, Earth or Martian one?
+-------+--------------------------------+
| Value | 	Meaning                      |
+-------+--------------------------------+
| 00(0) | Undefined value                |
| 01(1) | Terrestrial second (1000 ms)   |
| 10(2) | Martian second (1027.49125 ms) |
| 11(3) | Reserved for future use        |
+-------+--------------------------------+

* LI - Leap indicator warning
+-------+-----------------------------------------+
| Value | 	Meaning                               |
+-------+-----------------------------------------+
| 000(0) | No leap value incoming                 |
| 001(1) | Last minute of the day has 61 seconds  |
| 010(2) | last minute of the day has 59 seconds  |
| 011(3) | Reserved for leap minute warning use   |
| 100(4) | Reserved for leap minute warning use   |
| 101(5) | Reserved for leap hour warning use     |
| 110(6) | Reserved for leap hour warning use     |
| 111(7) | Undefined value                        |
+-------+-----------------------------------------+

