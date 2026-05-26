# Exercise: Fibonacci Modulo m

The Fibonacci sequence is defined by F(0) = 0, F(1) = 1, and F(n) = F(n−1) + F(n−2) for n ≥ 2.

Given n and m, compute F(n) mod m.

For large n (up to 10^15), the naïve approach of computing each Fibonacci number is too slow. However, the **Pisano period** (the period of Fibonacci numbers mod m) guarantees the sequence is periodic, so you can:
1. Find the Pisano period π(m): the smallest k > 0 such that F(k) ≡ 0 (mod m) and F(k+1) ≡ 1 (mod m).
2. Compute F(n mod π(m)) mod m.

For this exercise, n ≤ 10^6, so a simple iterative approach is sufficient without needing the Pisano period optimization.

Read two integers n and m from standard input. Output F(n) mod m.
