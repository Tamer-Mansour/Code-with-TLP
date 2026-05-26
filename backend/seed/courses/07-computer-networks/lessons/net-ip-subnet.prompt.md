# IP Network Calculator

Read an IPv4 address and prefix length from standard input, then print the network address and the number of usable host addresses.

## Input

One line with two space-separated tokens:
```
IP_ADDRESS PREFIX_LENGTH
```

- `IP_ADDRESS` is a valid dotted-decimal IPv4 address (e.g., `192.168.10.45`).
- `PREFIX_LENGTH` is an integer from 0 to 30.

## Output

Two lines:
```
Network: NETWORK_ADDRESS
Hosts: COUNT
```

- `NETWORK_ADDRESS` is the network address in dotted-decimal notation (all host bits set to 0).
- `COUNT` is the number of usable host addresses = 2^(32 - prefix_length) - 2.

## Examples

**Input:**
```
192.168.10.45 26
```
**Output:**
```
Network: 192.168.10.0
Hosts: 62
```

**Input:**
```
10.0.0.1 8
```
**Output:**
```
Network: 10.0.0.0
Hosts: 16777214
```

## Constraints

- Use only the Python standard library.
- No special imports needed — just integer arithmetic and string splitting.
