# CIDR Range Calculator

Read a single line of standard input containing a CIDR notation: an IPv4 address followed by a `/` and a prefix length.

Print five lines:
```
Network: <network address>
Broadcast: <broadcast address>
First: <first usable host>
Last: <last usable host>
Usable: <count of usable hosts>
```

All addresses in dotted-decimal. Usable hosts = 2^(32-prefix) - 2.
Prefix length is guaranteed to be in the range 0–30 (inclusive).

## Examples

Input:
```
192.168.1.0/24
```
Output:
```
Network: 192.168.1.0
Broadcast: 192.168.1.255
First: 192.168.1.1
Last: 192.168.1.254
Usable: 254
```

Input:
```
192.168.10.45/26
```
Output:
```
Network: 192.168.10.0
Broadcast: 192.168.10.63
First: 192.168.10.1
Last: 192.168.10.62
Usable: 62
```
