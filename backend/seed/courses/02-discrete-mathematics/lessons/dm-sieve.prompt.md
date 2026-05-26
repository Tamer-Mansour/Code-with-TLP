# Count Primes — Sieve of Eratosthenes

Given a non-negative integer `n`, output the number of prime numbers `p` satisfying `2 ≤ p ≤ n`.

## Input

A single integer `n` (`0 ≤ n ≤ 1,000,000`).

## Output

A single integer: the count of primes less than or equal to n.

## Examples

**Input:** `10`  
**Output:** `4`  
(Primes ≤ 10 are 2, 3, 5, 7)

**Input:** `2`  
**Output:** `1`  
(Only prime ≤ 2 is 2 itself)

## Hint

Use the Sieve of Eratosthenes. For each prime p found, mark all multiples of p starting from p² as composite. The sieve runs in O(n log log n) time.
