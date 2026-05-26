# Counting Rules: Sum and Product

Counting is the foundation of combinatorics and directly influences algorithm analysis, probability, and complexity theory. Two simple rules underlie almost every counting argument, and building mastery with them will let you reason about passwords, permutations, subsets, and algorithm state spaces alike.

## The Product Rule

**Statement:** If a task can be performed by making a sequence of k independent choices, where choice i has `nᵢ` options, the total number of ways to perform the task is:
```
n₁ × n₂ × … × nₖ
```

The word "independent" is critical: the options for choice i must not depend on what was chosen at earlier steps (or if they do, the counts must be fixed regardless of the specific earlier choice).

**Example 1 — Passwords:** A 4-character password uses lowercase letters (26) and digits (10), so 36 choices per character. Total: `36⁴ = 1,679,616` passwords.

**Example 2 — License Plates:** 3 letters followed by 3 digits: `26³ × 10³ = 17,576,000` plates.

**Example 3 — Functions:** The number of functions from set A (size m) to set B (size n) is `n^m`. Each of the m inputs independently selects one of n outputs — m choices, each with n options.

**Example 4 — Binary Strings:** There are `2^n` binary strings of length n: each of n positions independently picks 0 or 1. This is why a bitmask of n flags has `2^n` possible states.

**Example 5 — IPv4 Addresses:** Each of 4 octets is an integer from 0 to 255 (256 values). Total IPv4 addresses: `256⁴ = 4,294,967,296` ≈ 4.3 billion — why IPv4 address exhaustion occurred.

## The Sum Rule

**Statement:** If a task can be done by exactly one of k **mutually exclusive** (disjoint) methods, where method i has `nᵢ` ways, then the total number of ways is:
```
n₁ + n₂ + … + nₖ
```

The key condition is **mutual exclusion**: no outcome can be accomplished by more than one method simultaneously.

**Example 1 — Selecting a representative:** A committee of 5 seniors and 8 juniors. Choosing one representative from either group (but not both simultaneously): `5 + 8 = 13` ways.

**Example 2 — Passwords with length constraint:** Count passwords that are either exactly 6 letters or exactly 8 digits: `26^6 + 10^8`. These are disjoint cases (a string cannot be both).

## Inclusion-Exclusion (Overlapping Cases)

When choices are **not** mutually exclusive, the sum rule overcounts the overlap. The **Inclusion-Exclusion Principle** corrects this:

### Two Sets
```
|A ∪ B| = |A| + |B| − |A ∩ B|
```

**Example:** How many integers from 1 to 100 are divisible by 3 or by 5?
- Divisible by 3: `⌊100/3⌋ = 33`
- Divisible by 5: `⌊100/5⌋ = 20`
- Divisible by 15 (both): `⌊100/15⌋ = 6`
- Total: `33 + 20 − 6 = 47`

### Three Sets
```
|A ∪ B ∪ C| = |A| + |B| + |C|
             − |A∩B| − |A∩C| − |B∩C|
             + |A∩B∩C|
```

**Example:** Among 200 students, 120 take Math, 80 take CS, 70 take Physics, 40 take both Math and CS, 30 take both Math and Physics, 20 take both CS and Physics, and 10 take all three.

How many take at least one of these subjects?
```
= 120 + 80 + 70 − 40 − 30 − 20 + 10
= 270 − 90 + 10
= 190
```

### General Pattern

For n sets, the formula alternates: add singles, subtract pairs, add triples, subtract quadruples, …
```
|A₁ ∪ … ∪ Aₙ| = Σᵢ|Aᵢ| − Σᵢ<ⱼ|Aᵢ∩Aⱼ| + Σᵢ<ⱼ<ₖ|Aᵢ∩Aⱼ∩Aₖ| − …
```

**CS application:** Counting derangements (permutations where no element stays in place), counting surjective functions, and analyzing hash collision rates all use inclusion-exclusion.

## Subtraction Rule (Complement Counting)

Sometimes it is easier to count what you do **not** want:
```
|desired| = |total| − |undesired|
```

**Example:** Count 8-bit strings that are **not** all zeros and not all ones.
Total: `2^8 = 256`. Subtract 2 bad strings: `256 − 2 = 254`.

**Example:** Count passwords of exactly 8 characters (lowercase letters) that contain **at least one** digit.

With digits as part of a 36-char alphabet:
- All 8-char strings: `36^8`
- Strings with NO digits (only letters): `26^8`
- Strings with at least one digit: `36^8 − 26^8`

This is much simpler than summing over "exactly 1 digit," "exactly 2 digits," etc.

## Division Rule

If n distinct objects come in groups of d that are considered identical (or indistinguishable in some sense), there are `n/d` distinct groups.

**Example:** Count unordered pairs from a set of 10 people.
- Ordered pairs: `10 × 9 = 90` (Product Rule, two positions, second excludes first).
- Each unordered pair is counted twice (once per ordering).
- Unordered pairs: `90 / 2 = 45`.

This is the start of combination counting — covered in the next lesson.

## Combining the Rules: A Worked Problem

**Problem:** Count 8-character strings over `{a,…,z,0,…,9}` (36 characters) that:
1. Are at least 6 characters long and at most 8 characters long.
2. Start with a letter.
3. Have no repeated characters.

Break into cases by length (Sum Rule), then use Product Rule with decreasing counts:

- **Length 6:** `26 × 35 × 34 × 33 × 32 × 31` (first is one of 26 letters, subsequent positions pick from remaining 35, 34, … characters)
- **Length 7:** `26 × 35 × 34 × 33 × 32 × 31 × 30`
- **Length 8:** `26 × 35 × 34 × 33 × 32 × 31 × 30 × 29`

Total = sum of the three.

**CS application:** Password strength analysis. The "no repeated characters" constraint significantly reduces the count compared to `36^n`, but "starting with a letter" only reduces the first factor from 36 to 26.

## Summary

| Rule | When to use | Formula |
|------|------------|---------|
| Product | Sequential independent choices | n₁ × n₂ × … |
| Sum | Mutually exclusive alternatives | n₁ + n₂ + … |
| Inclusion-Exclusion | Overlapping alternatives | Alternating sum of intersections |
| Complement | Easier to count the opposite | Total − bad |
| Division | Groups of identical objects | n / d |

These five rules, applied carefully and combined, solve the vast majority of counting problems in discrete mathematics, algorithm analysis, and probability.
