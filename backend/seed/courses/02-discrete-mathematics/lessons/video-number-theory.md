# Video: Number Theory — Foundations of Cryptography

This video covers the number-theoretic ideas that underpin modern cryptography: divisibility, modular arithmetic, Euclid's GCD algorithm, prime numbers, the Sieve of Eratosthenes, Fermat's little theorem, and the Chinese Remainder Theorem, with direct connections to RSA encryption.

**Key takeaways:**

- Divisibility and the division algorithm: a = qb + r with 0 ≤ r < b.
- gcd(a, b) = gcd(b, a mod b) — Euclid's algorithm runs in O(log(min(a,b))) steps.
- The extended Euclidean algorithm finds integers x, y such that ax + by = gcd(a,b) — essential for computing modular inverses.
- Fermat's little theorem: if p is prime and gcd(a, p) = 1, then a^(p-1) ≡ 1 (mod p).
- RSA in a nutshell: choose primes p, q; n = pq; public exponent e with gcd(e, φ(n)) = 1; private key d = e^(-1) mod φ(n).

The Chinese Remainder Theorem section explains how to reconstruct a number from its residues modulo pairwise coprime moduli, and why this is used in high-performance arithmetic libraries.
