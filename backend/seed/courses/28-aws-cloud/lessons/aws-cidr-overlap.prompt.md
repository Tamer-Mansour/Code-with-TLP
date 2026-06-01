# VPC CIDR Overlap Check

Determine whether two IPv4 CIDR blocks overlap.

## Input

A single line with two CIDR blocks separated by a space:

```
<cidr-A> <cidr-B>
```

Each CIDR is `a.b.c.d/N` with N between 0 and 32 inclusive.

## Output

- `YES` if the address ranges overlap (one is a subset of the other, identical, or partially intersect).
- `NO` otherwise.

## Examples

Input: `10.0.0.0/16 10.0.1.0/24` → Output: `YES`

Input: `10.0.0.0/16 10.1.0.0/16` → Output: `NO`

Input: `192.168.0.0/24 192.168.0.0/24` → Output: `YES`

Input: `10.0.0.0/24 10.0.1.0/24` → Output: `NO` (adjacent, not overlapping)

## Notes

- Treat each CIDR as the contiguous range from the network address to the broadcast address (inclusive).
- Two ranges overlap if range1.end >= range2.start AND range2.end >= range1.start.
