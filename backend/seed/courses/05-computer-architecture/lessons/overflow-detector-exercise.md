# Exercise: Two's Complement Overflow Detector

Two's complement overflow is a fundamental concept in computer arithmetic. This exercise tests your understanding of representable ranges and when addition produces an unrepresentable result.

## The Problem

Given an N-bit two's complement system and two valid N-bit integers A and B, determine whether `A + B` overflows.

An overflow occurs when the true mathematical sum falls outside the range `[-(2^(N-1)), 2^(N-1) - 1]`.

## Key Insight

The representable range shrinks as N decreases:

| N  | Min         | Max        |
|----|-------------|------------|
| 4  | -8          | 7          |
| 8  | -128        | 127        |
| 16 | -32768      | 32767      |
| 32 | -2147483648 | 2147483647 |

If the sum of two N-bit values falls outside these bounds, an overflow has occurred and the stored result would be incorrect in hardware.

## Approach

1. Read N, A, and B.
2. Compute `R = A + B` using Python's arbitrary-precision integers.
3. Compare R against `[-(2**(N-1)), 2**(N-1) - 1]`.
4. Print `OVERFLOW` or `OK R`.
