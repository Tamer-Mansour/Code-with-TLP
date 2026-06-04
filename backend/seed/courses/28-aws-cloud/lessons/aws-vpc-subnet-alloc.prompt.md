# VPC CIDR Subnet Allocator

When designing a VPC, you need to choose a subnet prefix that provides enough usable IP addresses for your workload.

## AWS Subnet IP Reservation

AWS reserves **5 IP addresses** in every subnet:

| Reserved for       | Address          |
|--------------------|------------------|
| Network address    | First IP (.0)    |
| VPC router         | Second IP (.1)   |
| DNS server         | Third IP (.2)    |
| Future use         | Fourth IP (.3)   |
| Broadcast address  | Last IP          |

A subnet with prefix `/N` has `2^(32-N)` total IPs, so **usable IPs = 2^(32-N) - 5**.

Examples:
- `/28` → 16 total - 5 = **11 usable**
- `/27` → 32 total - 5 = **27 usable**
- `/24` → 256 total - 5 = **251 usable**

## Task

Given a VPC CIDR block and N subnet requests (each specifying the number of **usable IPs** needed), find the **smallest valid subnet prefix** for each request.

"Smallest valid prefix" means the highest prefix number (e.g., `/27` before `/26`) that still provides enough usable IPs. The maximum useful prefix is `/28` (11 usable IPs); `/29` and smaller are too small to be practical and are not considered.

If the requirement cannot be met by any prefix from `/1` to `/28`, output `IMPOSSIBLE`.

## Input Format

- Line 1: VPC CIDR in `A.B.C.D/prefix` format (for context only — you do not need to check fits)
- Line 2: integer `N` — number of subnet requests
- Lines 3 to N+2: one integer per line — required usable IP count

## Output Format

`N` lines. Each line is either `/prefix` (e.g., `/24`) or `IMPOSSIBLE`.

## Example

```
Input:
10.0.0.0/16
4
251
11
500
4090

Output:
/24
/28
/23
/20
```

Explanation:
- Need 251 usable: /24 gives 251 ✓ (smallest prefix that works)
- Need 11 usable: /28 gives 11 ✓
- Need 500 usable: /24 gives 251 (not enough), /23 gives 507 ✓
- Need 4090 usable: /20 gives 4091 ✓

## Constraints

- 1 ≤ N ≤ 100
- 1 ≤ required usable IPs ≤ 100000
