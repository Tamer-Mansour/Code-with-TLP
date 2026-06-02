# Correlating and Tournament Predictors

A plain 2-bit predictor considers only a single branch in isolation. Many real branches are correlated — the outcome of one branch directly influences the outcome of a nearby branch. Correlating predictors exploit this relationship to achieve higher accuracy.

## Motivation: Correlated Branches

```c
if (a == 0)   // Branch 1
    a = 1;
if (b == 0)   // Branch 2
    b = 1;
if (a != b)   // Branch 3
    do_something();
```

If Branch 1 and Branch 2 are both not-taken (a and b were both non-zero), Branch 3 is almost certainly not-taken too. A predictor that "remembers" the outcomes of Branches 1 and 2 can predict Branch 3 perfectly — but a plain 2-bit predictor that only looks at Branch 3's own history cannot.

## Global History Register (GHR)

The key hardware component is the **Global History Register** — a shift register of k bits that records the outcomes of the last k branches executed by any branch:

```
GHR (k=4):  T NT T NT  →  1010
             ↑ oldest      ↑ newest
```

When a branch resolves, its outcome (1 for taken, 0 for not-taken) is shifted into the LSB and the MSB is discarded.

## Two-Level Adaptive Predictor (Correlating Predictor)

The Two-Level predictor (Yeh and Patt, 1991) combines the GHR with the branch PC to index a **Pattern History Table (PHT)** of 2-bit saturating counters:

```
PHT index = GHR XOR PC[k:2]    (common "gshare" variant)
```

The structure:

```
PC ──────────────────────────────┐
                                 ↓
GHR → [shift register] → XOR → PHT[index] → 2-bit counter → prediction
                                                     ↑
                                               update after resolve
```

Variants:

| Predictor  | Index formula       | Notes                              |
|------------|---------------------|-------------------------------------|
| GAg        | GHR only            | All branches share one PHT          |
| PAg        | per-branch history  | Each branch has its own shift reg   |
| gshare     | GHR XOR PC          | Best area-accuracy tradeoff; widely used |

**gshare** dominates in practice because XOR-hashing mixes PC and history well, spreading entries across the PHT and reducing aliasing.

## Tournament Predictor

No single predictor is best for all branches. A **tournament predictor** (also called a **hybrid predictor**) runs multiple predictors in parallel and uses a **meta-predictor** (a 2-bit counter table) to choose which one to trust:

```
       ┌─────────────────┐
       │ Local predictor  │──→ pred_L ──┐
PC ───►│  (per-branch)   │             ├──→ [meta-predictor] → final prediction
       │                  │             │
       │ Global predictor │──→ pred_G ──┘
       │  (gshare)        │
       └─────────────────┘
```

**Meta-predictor update rule:**
- If local was correct and global was wrong → decrement counter (favor local).
- If global was correct and local was wrong → increment counter (favor global).
- If both right or both wrong → no update.

The Alpha 21264 (1998) popularized tournament prediction. Its predictor had:
- A 4 K-entry local history table (10-bit per-branch history).
- A 4 K-entry global predictor (gshare with 12-bit GHR).
- A 4 K-entry choice predictor (meta).
- Combined accuracy: ~97% on SPECint95.

## TAGE: Tagged Geometric History Length Predictor

Modern processors (Intel Skylake, AMD Zen series, Apple M-series) use **TAGE**, which uses multiple PHTs with geometrically increasing history lengths (e.g., 2, 4, 8, 16, 32 bits) and PC-hash tags to confirm a hit:

```
History lengths:  H1=2  H2=4  H4=8  H8=16  H16=32
PHT tables:       T1    T2    T3    T4     T5
                        ↑ longest matching entry wins
```

TAGE achieves < 3 MPKI on SPEC CPU2017 — better than any single-level scheme.

## Accuracy vs. Storage Tradeoff

| Predictor          | Storage   | Accuracy (SPECint) |
|--------------------|-----------|-------------------|
| 2-bit bimodal      | 4 KB      | ~87%              |
| gshare (14-bit)    | 32 KB     | ~93%              |
| Tournament (Alpha) | ~12 KB    | ~97%              |
| TAGE (64 KB)       | 64 KB     | ~99%              |

## Common Pitfall

A long GHR history length is not always better. Very long histories cause **aliasing** in the PHT (more bits to hash into fewer entries) and slow down the initial training for rare branches. The geometric spacing in TAGE is specifically designed to balance short-history accuracy against long-history correlation coverage.

> **Interview answer:** Correlating predictors index the PHT using a combination of the branch PC and the Global History Register (GHR), capturing inter-branch correlations. Tournament predictors extend this by choosing at runtime between a local and a global predictor using a meta-predictor — achieving ~97% accuracy versus ~87% for a plain 2-bit table.
