# Exercise: IP Network Calculator

Given an IPv4 address in dotted-decimal notation and a prefix length (CIDR notation), compute and print the **network address** and the **number of usable host addresses**.

## Input Format

Two space-separated values on one line:
```
IP_ADDRESS PREFIX_LENGTH
```

## Output Format

```
Network: NETWORK_ADDRESS
Hosts: COUNT
```

Where `COUNT` is the number of usable host addresses (total addresses minus 2: network and broadcast).

## Example

Input:
```
192.168.10.45 26
```

Output:
```
Network: 192.168.10.0
Hosts: 62
```

(Block size = 2^(32-26) = 64; usable = 64 - 2 = 62; network = 192.168.10.0)
