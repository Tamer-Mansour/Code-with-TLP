# Exercise: Simulate a TLB With LRU Replacement

In this exercise you will simulate a fully-associative TLB that uses the **Least Recently Used (LRU)** replacement policy. You will track TLB hits and misses for a sequence of virtual page number accesses, and compute the final hit ratio.

## What You Will Implement

Your program reads:

1. The TLB capacity (number of entries it can hold).
2. A sequence of virtual page number (VPN) accesses.

For each access, your simulator must:

- Check whether the VPN is currently in the TLB.
- On a **hit**: record a hit, update the LRU order (this entry is now most recently used).
- On a **miss**: record a miss, install the VPN. If the TLB is full, evict the LRU entry first.

After processing all accesses, print the total number of hits, the total number of misses, and the hit ratio as a percentage rounded to two decimal places.

## Why LRU?

LRU is the most common replacement policy studied in OS courses because it approximates optimal replacement for workloads with temporal locality. A TLB simulation with LRU cleanly illustrates how working-set size relative to TLB capacity drives the hit ratio — exactly the relationship explored in the reading lessons.

## Input / Output

See the prompt file for exact format, constraints, and sample cases.
