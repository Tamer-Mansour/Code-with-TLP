# Exercise: Sieve of Eratosthenes

Count the number of prime numbers that are less than or equal to n.

Use the Sieve of Eratosthenes for an efficient solution:

1. Create a boolean array `is_prime[0..n]`, initialized to `True`.
2. Set `is_prime[0] = is_prime[1] = False`.
3. For each `p` from 2 to √n: if `is_prime[p]` is True, mark all multiples of p starting from `p²` as False.
4. Count the positions where `is_prime[i]` is still True.

Read a single non-negative integer n from standard input. Output the count of primes ≤ n.
