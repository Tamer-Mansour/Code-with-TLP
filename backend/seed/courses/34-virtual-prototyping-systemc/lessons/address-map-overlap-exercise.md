# Detect Overlapping Regions in an Address Map

A well-formed address map must have **no overlapping regions**. In this exercise you will implement a validator that reads an address map and reports every pair of regions whose address ranges intersect.

## What You Will Implement

Write a program that reads a set of named memory regions (each with a base address and size) and outputs all overlapping pairs in lexicographic order, or `"OK"` if no overlaps exist.

## Why This Matters

Overlapping entries in a TLM router cause non-deterministic behavior: two targets may both receive the same transaction, or the first-match rule silently hides a misconfiguration. Catching overlaps at elaboration time — before simulation starts — is the correct approach. Many commercial VP frameworks (e.g., GreenSocs, Arm FVP) validate the address map during `end_of_elaboration()`.

## Key Concepts Practiced

- Interval overlap detection: two intervals `[a, a+sa)` and `[b, b+sb)` overlap if and only if `a < b+sb && b < a+sa`.
- O(n^2) pair-wise scan (acceptable for maps up to ~50 regions).
- Deterministic output ordering for reproducible regression tests.

## Your Task

Read the address map, find all overlapping pairs, and print them one per line as:

```
<name1> <name2>
```

where `name1 < name2` lexicographically and pairs are printed in lexicographic order of `(name1, name2)`. If no overlaps exist print `OK`.

See the prompt file (`vp-address-map-overlap-exercise.prompt.md`) for the full specification and sample test cases.
