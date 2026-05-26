# Exercise: Longest Prefix Match

Every router in the Internet uses **longest prefix match** to forward packets. Given a routing table with multiple overlapping prefixes, the router selects the most specific (longest) matching prefix for the destination IP. This exercise implements that core algorithm in Python.

## Background

A routing table entry is a CIDR prefix and a next-hop label. For a destination IP, the algorithm:
1. Tests each routing table entry: does (dst_ip AND mask) == (network_ip AND mask)?
2. Among all matching entries, picks the one with the **longest prefix length**.
3. Returns the next-hop label.

Example routing table:
```
10.0.1.0/24  → eth0    (256 addresses)
10.0.0.0/8   → eth1    (16.7 M addresses — less specific)
0.0.0.0/0    → eth2    (default route — matches everything)
```

For destination `10.0.1.45`:
- `10.0.1.0/24` matches → length 24
- `10.0.0.0/8` matches → length 8
- `0.0.0.0/0` matches → length 0
- **Winner: `/24`** → forward to eth0

## Your Task

See the exercise prompt for the exact input/output specification.
