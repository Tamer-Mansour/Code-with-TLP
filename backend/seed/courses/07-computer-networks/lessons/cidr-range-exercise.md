# Exercise: CIDR Range Calculator

Given any CIDR notation like `192.168.1.0/24`, a network engineer needs to quickly determine the network address, broadcast address, first and last usable host addresses, and total usable host count.

In this exercise you will build a CIDR range calculator that performs all of these computations using only integer arithmetic and bitwise operations — exactly how routers and operating systems do it internally.

## Background

A CIDR block `A.B.C.D/N` means:
- The **network prefix** occupies the first `N` bits of the 32-bit address.
- The **host part** occupies the remaining `32 - N` bits.
- **Subnet mask**: 32-bit number with the first N bits set to 1, rest 0.
- **Network address**: IP AND mask (host bits zeroed).
- **Broadcast address**: IP OR (NOT mask) (host bits all ones).
- **First usable host**: network address + 1 (for /0 to /30).
- **Last usable host**: broadcast - 1 (for /0 to /30).
- **Usable hosts**: 2^(32-N) - 2 (for N ≤ 30). For /31 and /32 special rules apply, but you only need to handle N in the range 0–30 for this exercise.

## Your Task

See the exercise prompt for the exact input/output specification.
