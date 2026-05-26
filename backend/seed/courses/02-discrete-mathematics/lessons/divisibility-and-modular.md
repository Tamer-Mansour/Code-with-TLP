# Divisibility and Modular Arithmetic

Number theory is the study of the integers, and it forms the mathematical backbone of modern cryptography, hashing, error correction, and random number generation. Two foundational concepts are divisibility and modular arithmetic.

## Divisibility

We say **a divides b** (written `a | b`) if there exists an integer k such that `b = a·k`.

- `3 | 12` because `12 = 3·4`. ✓
- `7 | 0` because `0 = 7·0`. ✓ (0 is divisible by everything)
- `5 ∤ 7` because no integer k satisfies `7 = 5k`.

### Divisibility Properties

| Property | Statement | Example |
|----------|-----------|---------|
| Reflexive | `a | a` | `7 | 7` |
| Transitivity | `a | b` and `b | c` ⟹ `a | c` | `2|6` and `6|12` ⟹ `2|12` |
| Linearity | `a | b` and `a | c` ⟹ `a | (mb + nc)` for all integers m,n | `5|10` and `5|15` ⟹ `5|30` |
| Antisymmetry (positive) | `a | b` and `b | a` and both positive ⟹ `a = b` | |

**Proof of linearity:** If `b = ak` and `c = am` for integers k, m, then `mb + nc = mak + nam = a(mk + nm)`, which is divisible by a. QED.

## Division Algorithm

**Theorem:** For any integer a (dividend) and positive integer d (divisor), there exist **unique** integers q (quotient) and r (remainder) with `0 ≤ r < d` such that:
```
a = d·q + r
```

This is not just a computational procedure — it is an existence and uniqueness theorem, proven via the Well-Ordering Principle.

**Examples:**
```
37 = 5·7 + 2    (q=7, r=2)
-7 = 3·(-3) + 2 (q=-3, r=2; note r≥0)
24 = 6·4 + 0    (exact divisibility)
```

Note: in many programming languages, `%` gives the C-remainder (which can be negative for negative dividends). The mathematical remainder is always non-negative.

## Modular Arithmetic

We say `a ≡ b (mod m)` (a is **congruent** to b modulo m) if `m | (a − b)`, equivalently if a and b have the same remainder when divided by m.

```
17 ≡ 5  (mod 6)   because 17 − 5 = 12 = 6·2
-3 ≡ 4  (mod 7)   because -3 − 4 = -7 = 7·(-1)
100 ≡ 0 (mod 10)  because 100 − 0 = 100 = 10·10
```

### Arithmetic Operations Mod m

Congruences support addition, subtraction, and multiplication:

```
If a ≡ b (mod m) and c ≡ d (mod m), then:
  a + c ≡ b + d  (mod m)
  a − c ≡ b − d  (mod m)
  a · c ≡ b · d  (mod m)
```

**Proof of multiplication:** a = b + km and c = d + lm for integers k, l. Then:
```
a·c = (b + km)(d + lm) = bd + bml + dkm + klm²
    = bd + m(bl + dk + klm) ≡ bd (mod m)
```

**Example (mod 7):** `5 · 6 = 30 ≡ 2 (mod 7)` because `30 = 4·7 + 2`.

### Fast Modular Exponentiation (Repeated Squaring)

For large exponents, reduce intermediate results at each multiplication:

```
Compute 3^13 mod 7:
  3^1  = 3
  3^2  = 9  ≡ 2  (mod 7)
  3^4  = (3^2)^2 ≡ 2^2 = 4  (mod 7)
  3^8  = (3^4)^2 ≡ 4^2 = 16 ≡ 2  (mod 7)
  3^13 = 3^8 · 3^4 · 3^1 ≡ 2 · 4 · 3 = 24 ≡ 3  (mod 7)
```

This is the **binary exponentiation** method: write the exponent in binary `(13 = 1101₂ = 8 + 4 + 1)` and multiply the corresponding powers. It requires only `O(log e)` multiplications, making it the basis of RSA and Diffie-Hellman.

## The Integers Modulo m

The **integers modulo m**, written `ℤ_m` or `ℤ/mℤ`, is the set `{0, 1, 2, …, m−1}` with arithmetic performed modulo m.

`ℤ_m` forms a **ring** (closed under addition and multiplication). When m is prime, every non-zero element has a multiplicative inverse — `ℤ_p` is a **field**.

This algebraic structure is the foundation of:
- **Finite fields** (Galois fields) used in AES, Reed-Solomon codes.
- **Elliptic curve cryptography:** arithmetic over `ℤ_p` for large primes.
- **Polynomial arithmetic** in coding theory.

## Applications in Computer Science

### Hash Tables

A hash function `h(k) = k mod m` maps keys to buckets `{0, …, m−1}`. For uniform distribution, m should be prime and not close to a power of 2 (to avoid correlation with binary key patterns).

### Checksums and Error Detection

The **ISBN-10** check digit satisfies: `Σᵢ₌₁^{10} i·dᵢ ≡ 0 (mod 11)`. This detects all single-digit errors and all transpositions of adjacent digits.

**CRC (Cyclic Redundancy Check):** Models data as a polynomial over `ℤ₂` and divides by a generator polynomial. Detects burst errors.

### Pseudorandom Number Generation

A **Linear Congruential Generator (LCG):**
```
X_{n+1} = (a · X_n + c) mod m
```
generates a sequence of pseudorandom integers. The period divides m. Proper choices of a, c, m give full period `m` (Hull-Dobell theorem).

### Cryptography (Preview)

RSA encryption: given `n = p·q` (product of two large primes):
- Encryption: `C ≡ M^e (mod n)`
- Decryption: `M ≡ C^d (mod n)`

where `e·d ≡ 1 (mod φ(n))` and `φ(n) = (p−1)(q−1)`.

Security rests on the hardness of factoring n back into p and q. The fast modular exponentiation algorithm makes encryption and decryption efficient; the lack of a fast factoring algorithm makes the system secure.

## Common Pitfalls

| Mistake | Correction |
|---------|-----------|
| `a ≡ b (mod m)` means a = b | It means a and b have the same remainder; a = b is a special case |
| Division always works mod m | Division by a only works if `gcd(a, m) = 1` |
| Python `%` matches mathematical mod | For positive operands yes; for negative: `-7 % 3 = 2` in Python, which matches math |
| Mod only works for positive numbers | Any integer a can be reduced mod m to `{0,…,m−1}` |

## Summary

| Concept | Notation | Key property |
|---------|----------|-------------|
| Divisibility | `a \| b` | `b = a·k` for some integer k |
| Division Algorithm | `a = d·q + r`, `0 ≤ r < d` | Unique q and r |
| Congruence | `a ≡ b (mod m)` | `m \| (a − b)` |
| Modular arithmetic | `(a·b) mod m` | Distribute, then reduce |
| Fast modular exp | Repeated squaring | O(log e) multiplications |
| ℤ_p (p prime) | Field | Every non-zero element is invertible |

Modular arithmetic appears everywhere: hash tables, checksums, random number generators, cryptographic protocols, and competitive programming.
