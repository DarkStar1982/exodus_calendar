## Notes on Martian timekeeping.
Martian sol (day) is 24 h 39 m 35.244 seconds long.

Therefore a convinient convention is to define Martian secodn as 1.0275 of Earth one and use 
same amount of hours, minutes and seconds for any day-to-day timekeeping needs.

However... second is a fundamental unit in all of our science and engineering, so there is a 
need to maintain a clear distinction between the two. Therefore _millisecond_ is used for the
timestamps, removing this ambiguity.

The underlying Exodus calendar library itself uses milliseconds internally for most of the
conversion calculations, converting timestamps to and from ones with Martian seconds where
necessary.


## NTP (Re-)implementation.
Because we don't want to confuse Earth-local and Mars-local times and timekeeping, a 
separate fork of NTP can be created to synchronize the Martian clocks across the users. As
we don't expect any significant difference in timekeeping on different planets, other than
requried by choice of local time. A simplified version of protocol can work initially, with
the expectation of eventual feature-parity with NTPv4 or later version at the time of the
MNTP wide-scale adoption.

## Martian Network Time Protocol Proposed Packet Structure

As with NTP, it should contain some info on time source, required timestamps and checksum.
All timestamps are in milliseconds, using 64 bits this will allow for both reasonable
precision and uninterrupted duration of the single epoch far beyond any immediate needs.
For sub-millisecond precision a different protocol is needed, outside the scope of this proposal (i.e. PTP analog for Mars).

+-------+0---------------1---------------2---------------3--------------+
|BITS   | 0 1 2 3 45 6 7 |0 1 2 3 4 5 6 7|0 1 2 3 4 5 6 7|0 1 2 3 4 5 6 7  
+-------+----------------+---------------+---------+-----+--------------+
|00-31  | Verson Number  |     Mode      |     Poll      |   Precision  |
+-------+---------------------------------------------------------------+
|32-63  | 					Root Delay                                  |
+-------+---------------------------------------------------------------+
|64-95  |                   Root Dispersion                             |
+-------+---------------------------------------------------------------+
|96-127 |  					Reference ID                                |
+-------+---------------------------------------------------------------+
|128-159|			        REFERENCE TIMESTAMP (T0)                    |
|160-191|                                                               |
+-------+---------------------------------------------------------------+
|192-223|			        ORIGINATE TIMESTAMP (T1)                    |
|224-255|                                                               |
+-------+---------------------------------------------------------------+
|256-287|			        RECEIVE TIMESTAMP (T2)                      |
|288-319|                                                               |
+-------+---------------------------------------------------------------+
|320-351|			        TRANSMIT TIMESTAMP (T3)                     |
|352-383|                                                               |
+-------+---------------------------------------------------------------+
|384-415| 					256-bit SHA2 CHECKSUM                       |
|416-447|                                                               |
|448-479|                                                               |
|480-511|                                                               |
|512-575|																|
|576-639|                                                               |
+-------+---------------------------------------------------------------+

## Fields Explained


* VN - Version Number (version): 8-bit integer representing Mars NTP version number, set to 1

* Mode/Stratum - 8-bit integer representing the operations mode

+---------------+---------------------------------------------------+
|    Value      | 	Meaning                                         |
+---------------+---------------------------------------------------+
| 00000000(0)   | My role is set to be MNTP client                  |
| 00000001(1)   | My role is set to be MNTP Stratum 1 source        |
| 00000010(2)   | My role is set to be MNTP Stratum 2 source        |
| ...........   | ..........................................        |
| 00001111(15)  | My role is set to be MNTP Stratum 15 source       |
| 00010000(16)  | Reserved for future use                           |
| ...........   | ..........................................        |
| 11111111(255) | Diagnostic/debug mode - no valid timing           |
+-----------------+-------------------------------------------------+

Poll: 8-bit unsigned integer representing the maximum interval between
successive messages, in seconds.  Suggested default limits for
minimum and maximum poll intervals are 1 and 256, respectively.

Precision: 8-bit unsigned integer representing the precision of the
system clock, in 1/(1^LOG2(value)), from +/-1s to +/-10 ns.

Root Delay: The root delay is the round-trip packet delay from a client to a stratum 1 server

Root Dispersion: The root tells you how much error is added due to other factors.

Reference ID: Server identification information

Reference Timestamp: Time when the system clock was last set or corrected, 
in MNTP timestamp format.

Origin Timestamp: Time at the client when the request departed for the server,
in MNTP timestamp format.

Receive Timestamp: Time at the server when the request arrived from the client,
in MNTP timestamp format.

Transmit Timestamp: Time at the server when the response left for the client,
in MNTP timestamp format.

Destination Timestamp: Time at the client when the reply arrived from the server, 
in NTP timestamp format.


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