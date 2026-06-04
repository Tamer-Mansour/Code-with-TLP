# The Pumping Lemma: A Computational Perspective

The pumping lemma gives a property that every regular language must satisfy. Its real use is as a **disproof tool**: if a language fails the pumping property, it cannot be regular. This exercise lets you explore the argument computationally, by checking whether a specific string from the language {a^n b^n} can survive being "pumped down."

## Recall the Lemma

If L is regular with pumping length p, then every string s ∈ L with |s| ≥ p can be split as s = xyz where:
1. |y| ≥ 1
2. |xy| ≤ p
3. For all i ≥ 0: xy^i z ∈ L

The standard non-regularity proof for L = {a^n b^n | n ≥ 0} works like this:

- Choose s = a^p b^p ∈ L (|s| = 2p ≥ p).
- Any split with |xy| ≤ p forces x and y to consist entirely of a's (since the first p symbols are all a's).
- So y = a^k for some k ≥ 1.
- Pump with i = 0: xy⁰z = xz = a^(p-k) b^p. Since k ≥ 1, we have fewer a's than b's, so xz ∉ {a^n b^n}. Contradiction.

## What This Exercise Checks

Given a string s of the form a^m b^m and a pumping length p, the exercise asks: does ANY valid split result in xy⁰z (pumping down) still being of the form a^k b^k? If even one split survives, output `STAYS_REGULAR`; if every valid split pumps the string OUT of the language, output `PUMPS_OUT`.

For the classic string a^p b^p with p ≥ 1, no valid split survives — the adversary always wins. This is exactly the computation that underlies the proof.

## Important Subtlety

The pumping lemma checks a necessary condition, NOT a sufficient one. A language can satisfy the pumping lemma and still not be regular. The Myhill-Nerode theorem gives the correct if-and-only-if condition.

The lesson here: you are modeling the **adversarial game** in the pumping lemma proof. The prover (you) picks s; the adversary picks the split xyz; the prover picks i. In this exercise, the prover uses i = 0 (pump down) and checks if it always breaks the structure.

## Example: s = "aabb", p = 3

Valid splits with |xy| ≤ 3 and |y| ≥ 1:

| y | xz (pump i=0) | Form a^k b^k? |
|---|---------------|---------------|
| a (y=s[0:1]) | xz = "abb" | No (1a, 2b) |
| aa (y=s[0:2]) | xz = "bb" | No (0a, 2b — but 0=0... wait, 0a and 2b, 0≠2) |
| aab (y=s[0:3]) | xz = "b" | No (0a, 1b) |
| a (y=s[1:2]) | xz = "abb" | No |
| ab (y=s[1:3]) | xz = "ab" | No (1a, 1b) — YES! |

Wait: "ab" with x="a", y="ab", z="b" → xz = "a"+"b" = "ab" — this IS a^1 b^1. So this split STAYS_REGULAR. But wait — is |xy| = |"a"+"ab"| = 3 ≤ p=3? Yes. So output `STAYS_REGULAR`.

When s = "aabbaabb" (m=4, p=3), all valid splits pump out — try it.

## Further Reading

- Sipser §1.4 (Pumping Lemma) — MIT OpenCourseWare: https://ocw.mit.edu/courses/18-404j-theory-of-computation-fall-2020/
- Hefferon, Chapter 3 (worked pumping lemma examples) — https://jheffero.w3.uvm.edu/computation/book.pdf
