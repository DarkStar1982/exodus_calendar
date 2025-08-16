## Notes on Martian timekeeping.
Martian sol (day) is 24 h 39 m 35.244 seconds long.

Therefore a convinient convention is to define Martian secodn as 1.0275 of Earth one and use 
same amount of hours, minutes and seconds for any day-to-day timekeeping needs.

However... second is a fundamental unit in all of our science and engineering, so there is a 
need to maintain a clear distinction between the two.

The library itself uses milliseconds internally for most of the conversion calculations,
converting timestamps to and from ones with Martian seconds where necessary.

Future Martian settlers should probably use a different name for their "second" of 1027.5 ms
duration or use millisecond as fundamental time unit.


## NTP (Re-)implementation.
Because we don't want to confuse Earth-local and Mars-local times and timekeeping, a 
separate fork of NTP can be created to synchronize the Martian clocks across the users. As
we don't expect any significant difference in timekeeping on different planets, other than
requried by choice of local time. A simplified version of protocol can work initially, with
the expectation of eventual feature-parity with NTPv4 or later version at the time of the
MNTP wide-scale adoption.

## Martian Network Time Protocol Proposed Packet Structure

As with NTP, it should contain some info on time source, required timestamps and checksum.
Note that martian seconds can be either equal to Earth second (1000 ms) or stretched to
1027.5 ms to mantain the convieniens 24-hour sol. This should be specified explicitely by
the users.

+-------+0---------------1---------------2---------------3--------------+
|BITS   | 0 1|2 3 4|5 6 7|0 1 2|3 4 5 6 7|0 1 2 3 4 5 6 7|0 1 2 3 4 5 6 7  
+-------+----+-----+-----+-----+---------+---------------+--------------+
|00-31  | SC | LI  | VN  |Mode | Stratum |     Poll      |   Precision  |
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
+--------+-----------------------------------------+
| Value  | 	Meaning                                |
+--------+-----------------------------------------+
| 000(0) | No leap value incoming                  |
| 001(1) | Last minute of the day has 61 seconds   |
| 010(2) | last minute of the day has 59 seconds   |
| 011(3) | Reserved for future use                 |
| 100(4) | Reserved for future use                 |
| 101(5) | Reserved for future use                 |
| 110(6) | Reserved for future use                 |
| 111(7) | Undefined value                         |
+--------+-----------------------------------------+

* VN - Version Number (version): 3-bit integer representing Mars NTP version number, set to 1

* Mode - 3-bit integer representing the association mode
+--------+-----------------------------------------+
| Value  | 	Meaning                                |
+--------+-----------------------------------------+
| 000(0) | Diagnostic/debug mode - no valid timing |
| 001(1) | My role is set to be MNTP server        |
| 010(2) | My role is set to be MNTP client        |
| 011(3) | Reserved for future use  			   |
| 100(4) | Reserved for future use                 |
| 101(5) | Reserved for future use                 |
| 110(6) | Reserved for future use                 |
| 111(7) | Reserved for future use                 |
+--------+-----------------------------------------+

* Stratum - 5-bit integer representing the stratum

+-----------+----------------------------------------------------------+
|   Value   | 	 Meaning                                               |
+-----------+----------------------------------------------------------+
| 00000(0)  | Undefined/unspecified                                    |
| 00001(1)  | Primary MNTP server (high-precision time source)         |
| 00010(2)  | Secondary MNTP server (set from MNTP Stratum 1 source)   |
| 00011(3)  | Secondary MNTP server (set from MNTP Stratum 2 source)   |
| ......... | ......................................................   |
| 01111(15) | Secondary MNTP server (set from MNTP Stratum N-1 source) |
| 10000(16) | Unsynchronized                                           |
| 10001(17) | Reserved for future use                                  |
| ......... | ......................................................   |
| 11111(31) | Reserved for future use                                  |
+--------+-------------------------------------------------------------+

Poll: 8-bit unsigned integer representing the maximum interval between
successive messages, in seconds.  Suggested default limits for
minimum and maximum poll intervals are 1 and 256, respectively.

Precision: 8-bit unsigned integer representing the precision of the
system clock, in 1/(1^LOG2(value)), from +/-1s to +/-10 ns.


## MNTP Server-Client Operations

An MNTP software can operate in either client or server mode. In 
client it sends a request (MNTP mode 2) to a designated server 
and expects a reply (NTP mode 1) from that server.  

Client requests are normally sent at intervals depending on the
frequency tolerance of the client clock and the required accuracy.
  
To calculate the roundtrip delay d and system clock offset t relative
to the server, the client sets the Transmit Timestamp field in the
request to the time of day according to the client clock in NTP
timestamp format.  For this purpose, the clock need not be
synchronized.  The server copies this field to the Originate 
Timestamp in the reply and sets the Receive Timestamp and Transmit
Timestamp fields to the time of day according to the server clock in
NTP timestamp format.

When the server reply is received, the client determines a 
Destination Timestamp variable as the time of arrival according to
its clock in NTP timestamp format.  The following table summarizes 
the four timestamps.
+-----------------------+-----+----------------------------------+
| Timestamp Name        |  ID |  When Generated                  |
+-----------------------+-----+----------------------------------+
| Originate Timestamp   |  T1 |  time request sent by client.    |
| Receive Timestamp     |  T2 |  time request received by server |
| Transmit Timestamp    |  T3 |  time reply sent by server       |
| Destination Timestamp |  T4 |  time reply received by client.  |
+-----------------------+-----+----------------------------------+

The roundtrip delay d and system clock offset t are defined as:

d = (T4 - T1) - (T3 - T2)     t = ((T2 - T1) + (T3 - T4)) / 2