# Exercise: IP Address to 32-bit Integer

Given a dotted-decimal IPv4 address, convert it to its equivalent **unsigned 32-bit integer** representation and print it.

## Input Format

A single line containing a valid IPv4 address:
```
A.B.C.D
```

## Output Format

A single integer on one line.

## Example

Input:
```
192.168.1.1
```

Output:
```
3232235777
```

Explanation: `192 * 2^24 + 168 * 2^16 + 1 * 2^8 + 1 = 3232235777`
