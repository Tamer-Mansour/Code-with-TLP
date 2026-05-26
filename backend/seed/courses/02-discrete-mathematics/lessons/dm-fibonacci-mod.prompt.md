# Fibonacci Modulo m

The Fibonacci sequence is defined as:
- F(0) = 0
- F(1) = 1  
- F(n) = F(n−1) + F(n−2) for n ≥ 2

Given two integers n and m, compute **F(n) mod m**.

## Input

Two space-separated integers on one line: `n` and `m`.  
Constraints: `0 ≤ n ≤ 1,000,000`, `1 ≤ m ≤ 1,000,000,000`.

## Output

A single integer: `F(n) mod m`.

## Examples

**Input:** `6 5`  
**Output:** `3`  
(F(6) = 8; 8 mod 5 = 3)

**Input:** `10 3`  
**Output:** `1`  
(F(10) = 55; 55 mod 3 = 1)

## Hint

Iterate from F(0) to F(n), reducing mod m at each step to keep numbers small. Time complexity: O(n).
