# Exercise: 32-bit Integer to IP Address

The complement to converting a dotted-decimal IP to an integer is converting an integer back to dotted-decimal notation. Both operations are used constantly in networking code — for bitwise subnet calculations, storing IPs efficiently in databases, and implementing protocol parsers.

## Background

A 32-bit unsigned integer encodes an IPv4 address with the most-significant byte corresponding to the first octet:

```
Integer 3232235777 in binary:
11000000 10101000 00000001 00000001
   192      168       1        1
→ 192.168.1.1
```

Extraction uses bitwise shifts and masking:
```python
a = (n >> 24) & 0xFF   # bits 31-24
b = (n >> 16) & 0xFF   # bits 23-16
c = (n >>  8) & 0xFF   # bits 15-8
d =  n        & 0xFF   # bits 7-0
```

## Your Task

See the exercise prompt for the exact input/output specification.
