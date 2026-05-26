# GCD, Euclid's Algorithm, and Primes

## Greatest Common Divisor

The **greatest common divisor** of integers a and b (not both zero), written `gcd(a, b)`, is the largest positive integer that divides both a and b.

```
gcd(12, 8)   = 4
gcd(100, 75) = 25
gcd(7, 13)   = 1   (coprime / relatively prime)
gcd(0, 5)    = 5   (by convention, gcd(0, n) = n)
```

Two integers are **coprime** (relatively prime) if `gcd(a, b) = 1`. Coprimality is essential for modular inverses and the Chinese Remainder Theorem.

### Least Common Multiple

The **least common multiple** `lcm(a, b)` is the smallest positive integer divisible by both a and b.

```
gcd(a, b) · lcm(a, b) = |a · b|
```

So `lcm(12, 8) = 12·8 / gcd(12,8) = 96/4 = 24`.

**Why this formula works:** A prime p contributes `min(αₚ, βₚ)` to the GCD and `max(αₚ, βₚ)` to the LCM (where αₚ and βₚ are the exponents of p in a and b). Since `min + max = sum`, `gcd · lcm = a · b`.

## Euclid's Algorithm

Computing gcd by prime factorization is slow (factoring is hard for large numbers). Euclid's algorithm (c. 300 BCE) is fast:

```
gcd(a, b) = gcd(b, a mod b)   for b ≠ 0
gcd(a, 0) = a
```

**Correctness:** If `a = b·q + r`, then every common divisor of a and b also divides r (since `r = a − bq`), and vice versa. So `gcd(a, b) = gcd(b, r) = gcd(b, a mod b)`.

**Example — Trace through `gcd(48, 18)`:**
```
gcd(48, 18) = gcd(18, 48 mod 18) = gcd(18, 12)
            = gcd(12, 18 mod 12) = gcd(12, 6)
            = gcd(6,  12 mod 6)  = gcd(6, 0)
            = 6
```

**Complexity:** The algorithm terminates in `O(log(min(a, b)))` steps. At each step, the smaller number decreases by at least a factor of 2 every two steps (since `a mod b < a/2` when `b ≤ a/2`, or `a mod b = a − b < a/2` when `b > a/2`). This is extremely efficient even for 1000-digit numbers — a key reason number theory underpins modern cryptography.

## Extended Euclidean Algorithm

The extended version finds integers x, y such that:
```
a·x + b·y = gcd(a, b)   (Bézout's Identity)
```

Such integers always exist (by Bézout's theorem). The extended algorithm runs the standard Euclidean steps and back-substitutes to find x and y.

**Example — Extended gcd(48, 18):**
Working backwards from `gcd = 6`:
```
6 = 12 − 6·1
6 = 12 − (18 − 12·1)·1 = 12·2 − 18·1
6 = (48 − 18·2)·2 − 18·1 = 48·2 − 18·5
```
So `48·2 + 18·(-5) = 6`. Here `x = 2, y = -5`.

**Application — Modular Inverse:** If `gcd(a, m) = 1`, the extended Euclidean algorithm computes x such that `a·x ≡ 1 (mod m)`. This modular inverse is the foundation of RSA key generation and modular division.

## Modular Inverses

The **modular inverse** of a modulo m is an integer x such that:
```
a · x ≡ 1 (mod m)
```

It exists **if and only if** `gcd(a, m) = 1`.

**Example:** Find `7⁻¹ mod 11`.

Extended gcd(7, 11): `7·8 = 56 = 5·11 + 1`, so `7·8 ≡ 1 (mod 11)`. Thus `7⁻¹ ≡ 8 (mod 11)`.

**Why this matters:** In RSA, the private key d satisfies `e·d ≡ 1 (mod φ(n))` — it is the modular inverse of the public exponent e.

## Prime Numbers

A **prime** is an integer `p ≥ 2` whose only positive divisors are 1 and p itself.

**Fundamental Theorem of Arithmetic:** Every integer `n ≥ 2` has a unique factorization as a product of primes (unique up to ordering). For example:
```
360 = 2³ · 3² · 5
```

This uniqueness is what makes primes the "atoms" of number theory.

### Trial Division Primality Test

Check all potential divisors up to `√n`:

```python
def is_prime(n):
    if n < 2: return False
    if n == 2: return True
    if n % 2 == 0: return False
    i = 3
    while i * i <= n:
        if n % i == 0:
            return False
        i += 2
    return True
```

**Complexity:** `O(√n)` — feasible for numbers up to `10^{12}` but too slow for cryptographic primes (2048-bit numbers ≈ 10^{617}).

### Sieve of Eratosthenes

Finds all primes up to n in `O(n log log n)` time:

```
Create a boolean array of size n+1, initialized to True.
Set sieve[0] = sieve[1] = False.
For p from 2 to √n:
    if sieve[p] is True:
        for k = p², p²+p, p²+2p, … ≤ n:
            sieve[k] = False
Output all i where sieve[i] is True.
```

**Why start marking at p²?** All smaller multiples of p (namely `2p, 3p, …, (p−1)p`) have a smaller prime factor and were already marked off by an earlier iteration.

**Example (primes up to 20):**
After the sieve: 2, 3, 5, 7, 11, 13, 17, 19.

### Fermat's Little Theorem

If p is prime and `gcd(a, p) = 1`:
```
a^(p−1) ≡ 1 (mod p)
```

Equivalently, `a^p ≡ a (mod p)` for all integers a.

**Proof sketch:** Consider the set `{a, 2a, 3a, …, (p−1)a} mod p`. Since `gcd(a,p)=1`, these are all distinct and non-zero, forming a permutation of `{1, 2, …, p−1}`. Their product is `aᵖ⁻¹ · (p−1)!`, which equals `(p−1)! mod p`. Canceling `(p−1)!` gives `aᵖ⁻¹ ≡ 1`.

**Probabilistic primality test:** If `a^(p−1) mod p ≠ 1` for some a, then p is **definitely composite**. If it equals 1 for many random a, p is **probably prime** (Miller-Rabin test refines this into a deterministic or probabilistic primality test).

### Prime Number Theorem

The number of primes `≤ n`, denoted `π(n)`, satisfies:
```
π(n) ~ n / ln(n)   as n → ∞
```

More precisely, the probability that a random integer near n is prime is approximately `1/ln(n)`. This is used to estimate how many random numbers to test before finding a prime — relevant in RSA key generation.

## Proof: Infinitely Many Primes

**Euclid's proof (c. 300 BCE) — by contradiction:**

Assume there are finitely many primes: `p₁, p₂, …, pₖ`. Consider:
```
N = p₁ · p₂ · … · pₖ + 1
```
N is not divisible by any `pᵢ` (remainder is 1 each time). But `N ≥ 2`, so it must have a prime factor — a prime not in our list. Contradiction. Therefore infinitely many primes exist. QED.

## Euler's Totient Function

`φ(n)` counts the integers from 1 to n that are **coprime** to n (i.e., `gcd(k, n) = 1`).

**Key values:**
- `φ(1) = 1`
- `φ(p) = p − 1` for prime p (all of 1, …, p−1 are coprime to p)
- `φ(p^k) = p^k − p^(k−1) = p^(k−1)(p−1)` (exclude multiples of p)
- `φ(m·n) = φ(m)·φ(n)` when `gcd(m, n) = 1` (multiplicativity)
- `φ(p·q) = (p−1)(q−1)` for distinct primes p, q

**RSA connection:** The RSA modulus is `n = p·q`. The private key d satisfies `e·d ≡ 1 (mod φ(n))`. The security relies on the difficulty of computing `φ(n)` without knowing p and q — which requires factoring n.

**Euler's Theorem (generalization of Fermat's Little Theorem):**
```
a^φ(n) ≡ 1 (mod n)   for all a with gcd(a, n) = 1
```

This is the mathematical foundation of RSA correctness.

## Summary

| Concept | Formula / Algorithm |
|---------|-------------------|
| GCD | Euclid: `gcd(a,b) = gcd(b, a mod b)` |
| LCM | `lcm(a,b) = a·b / gcd(a,b)` |
| Bézout's Identity | `∃x,y: a·x + b·y = gcd(a,b)` |
| Modular inverse | Exists iff `gcd(a,m) = 1`; use extended Euclidean |
| Sieve | All primes ≤ n in `O(n log log n)` |
| Fermat's Little | `a^(p−1) ≡ 1 (mod p)` for prime p, `gcd(a,p)=1` |
| Euler's Totient | `φ(pq) = (p−1)(q−1)`; Euler's Theorem: `a^φ(n) ≡ 1 (mod n)` |
