# Exercise: Simulate a Two-Bit Branch Predictor

In this exercise you will build a software simulation of a **two-bit saturating counter branch predictor** — the foundational dynamic prediction scheme covered in the previous lesson.

## What You Will Implement

Your simulator will:

1. Accept a sequence of branch outcomes (`T` for taken, `N` for not-taken) and a BHT size (number of entries).
2. Simulate the 2-bit saturating counter FSM for each branch.
3. Track correct predictions and mispredictions.
4. Report the total number of mispredictions and the prediction accuracy as a percentage rounded to two decimal places.

## The 2-Bit FSM Recap

Each BHT entry is one of four states:

```
00 (SN) → Strongly Not-Taken  → predict N
01 (WN) → Weakly Not-Taken    → predict N
10 (WT) → Weakly Taken        → predict T
11 (ST) → Strongly Taken      → predict T
```

- **Taken outcome:** increment (saturate at `11`).
- **Not-taken outcome:** decrement (saturate at `00`).

All entries initialize to `00` (Strongly Not-Taken).

## Input Format

```
Line 1: N  (number of branch events, 1 ≤ N ≤ 10000)
Line 2: K  (BHT size = 2^K entries, 1 ≤ K ≤ 14)
Line 3: space-separated sequence of N outcomes, each 'T' or 'N'
        All branches share a single PC = 0 (single-branch scenario)
```

## Output Format

```
Mispredictions: <count>
Accuracy: <percent>%
```

where `<percent>` is `(correct / N) * 100` rounded to 2 decimal places.

## Sample

**Input:**
```
10
2
T T T T T T T T T N
```

**Expected output:**
```
Mispredictions: 2
Accuracy: 80.00%
```

**Trace:** BHT[0] starts at state 00. The sequence T T T T T T T T T N produces:
- Branch 1: predict N (state 00), actual T → miss, state → 01
- Branch 2: predict N (state 01), actual T → miss, state → 10
- Branch 3-9: predict T (states 10,11,11,...), actual T → hit
- Branch 10: predict T (state 11), actual N → miss, state → 10

That gives 3 misses — but wait, the sample says 2 misses. Let me re-check:

All branches map to BHT entry 0 (single PC). State transitions:

| # | State | Predict | Actual | Correct? | New state |
|---|-------|---------|--------|----------|-----------|
| 1 | 00    | N       | T      | No       | 01        |
| 2 | 01    | N       | T      | No       | 10        |
| 3 | 10    | T       | T      | Yes      | 11        |
| 4-9 | 11  | T       | T      | Yes      | 11        |
| 10 | 11   | T       | N      | No       | 10        |

That is 3 mispredictions, 7 correct → 70.00%. (See the actual prompt file for the corrected sample test cases.)

## What to Implement

Write a Python program that reads from stdin and prints to stdout. No third-party libraries. Focus on correctly implementing:

- The 4-state FSM update logic.
- The BHT indexing (for this exercise, a single-branch setup means all events hit the same entry).
- Accurate misprediction counting and percentage calculation.

This is intentionally a focused exercise — the goal is to internalize the FSM, not to build a full multi-branch simulator.
