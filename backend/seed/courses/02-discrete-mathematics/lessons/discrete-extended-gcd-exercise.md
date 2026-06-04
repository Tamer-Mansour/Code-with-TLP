# Exercise: Extended Euclidean Algorithm

The **Extended Euclidean Algorithm** does more than compute `gcd(a, b)` — it also finds the **Bezout coefficients**: integers `x` and `y` satisfying:

```
a·x + b·y = gcd(a, b)
```

This is called **Bezout's identity** and it has profound applications:

- **Modular inverse:** If `gcd(a, m) = 1`, then `x` from Bezout's identity is `a⁻¹ (mod m)` — the modular inverse used in RSA decryption.
- **Chinese Remainder Theorem:** Constructing solutions uses modular inverses computed via this algorithm.
- **Linear Diophantine equations:** The equation `ax + by = c` has an integer solution if and only if `gcd(a, b) | c`.

## Algorithm Sketch

The extended algorithm runs recursively alongside the standard Euclidean algorithm:

```
If b = 0: return (a, 1, 0)   # gcd = a, x = 1, y = 0
Otherwise:
  (g, x1, y1) = extended_gcd(b, a mod b)
  return (g, y1, x1 - (a // b) * y1)
```

At each recursive level the coefficients are updated so that the Bezout identity holds for the current pair.

## Verification Step

After computing `g, x, y`, always verify: `a*x + b*y == g`. This sanity check catches off-by-one errors in the recursion.

Read the problem statement for the exact input and output specification.

## Further Reading

- *Mathematics for Computer Science* (Lehman, Leighton, Meyer) — Chapter 9 on Number Theory covers Bezout's theorem in depth: https://people.csail.mit.edu/meyer/mcs.pdf
- *Discrete Mathematics: An Open Introduction* by Oscar Levin — https://discrete.openmathbooks.org/dmoi4/
