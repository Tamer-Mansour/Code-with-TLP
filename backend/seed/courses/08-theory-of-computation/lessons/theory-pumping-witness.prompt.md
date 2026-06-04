# Pumping Lemma Witness for {a^n b^n}

The language L = {a^n b^n | n ≥ 0} is the classic example of a non-regular language. The pumping lemma proves it: any string a^m b^m with m ≥ p can be "pumped" out of L.

Given a string `s` of the form a^m b^m and a pumping length `p`, determine whether the string can survive being **pumped down** (i = 0) while staying in L.

## Task

Check all valid splits `s = xyz` where:
- |xy| ≤ p (the split point is within the first p characters)
- |y| ≥ 1 (the pumped portion is non-empty)

For each such split, compute `xz` (pump with i = 0, removing y). Check whether `xz` is still of the form a^k b^k (k ≥ 0, equal counts of leading a's then b's).

- If **any** valid split produces an `xz` that is still of the form a^k b^k, print `STAYS_REGULAR`.
- If **every** valid split produces an `xz` that is NOT of the form a^k b^k, print `PUMPS_OUT`.

## Input Format

- Line 1: integer `p` (pumping length, 1 ≤ p ≤ 20)
- Line 2: string `s` of the form a^m b^m (1 ≤ m ≤ 50), consisting only of characters `a` and `b`

## Output Format

Either `STAYS_REGULAR` or `PUMPS_OUT` on a single line.

## Examples

**Example 1:**
```
Input:
3
aabbaabb

Output:
PUMPS_OUT
```

**Example 2:**
```
Input:
3
aabb

Output:
STAYS_REGULAR
```

**Explanation for Example 2:**
With p=3 and s="aabb", the split x="a", y="ab", z="b" has |xy|=3 ≤ p=3 and |y|=2 ≥ 1. Pumping down gives xz = "a"+"b" = "ab" = a^1 b^1 ∈ L. So STAYS_REGULAR.

**Explanation for Example 1:**
With p=3 and s="aabbaabb", every valid split (with |xy| ≤ 3) produces an xz not in L. Every y falls within the first 3 characters (all a's or mixed), and removing y always unbalances the a's and b's. So PUMPS_OUT.

## Constraints

- 1 ≤ p ≤ 20
- s has the form a^m b^m with 1 ≤ m ≤ 50
- |s| = 2m
