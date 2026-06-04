# Exercise: Count Inversions

Count the number of inversions in an array using an augmented merge sort in O(n log n) time.

## What Is an Inversion?

A pair of indices (i, j) with i < j is an **inversion** if A[i] > A[j]. The number of inversions measures how far an array is from being sorted:
- Sorted array: 0 inversions
- Reverse-sorted array of length n: n*(n-1)/2 inversions (maximum)

## Why It Matters

- Inversions are a common metric in algorithm courses for practising divide-and-conquer.
- Counting inversions is equivalent to the problem of measuring the "sortedness" or disorder of a sequence.
- The naive O(n²) approach checks every pair; divide-and-conquer achieves O(n log n).

## Key Insight

During merge sort, whenever an element from the **right** half is placed before remaining elements in the **left** half, each of those remaining left elements forms an inversion with the right element. Counting these during the merge step gives the total split inversions in O(n) per level.

## Input Format

- Line 1: N (number of elements)
- Line 2: N space-separated integers

## Output Format

Print the number of inversions (a single non-negative integer).

## Examples

```
Input:          Output:
5               3
3 1 2 5 4
```

Inversions: (3,1), (3,2), (5,4) — three pairs.

```
Input:          Output:
4               6
4 3 2 1
```

All 4×3/2 = 6 pairs are inversions (fully reverse-sorted).
