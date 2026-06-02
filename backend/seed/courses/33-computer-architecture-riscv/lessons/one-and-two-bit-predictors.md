# One-Bit and Two-Bit Saturating Predictors

The simplest dynamic predictors store a tiny piece of state per branch and use it to make a taken/not-taken decision. Understanding the 1-bit and 2-bit predictors builds the intuition for every more sophisticated scheme in use today.

## 1-Bit Predictor

Each BHT entry holds a single bit:

- `1` → predict taken
- `0` → predict not-taken

**Update rule:** set the bit to the actual outcome after resolution.

```
if (actual == TAKEN)     entry = 1;
else                     entry = 0;
```

### Problem: Double Misprediction on Loop Exit

Consider a loop that iterates 10 times (outcomes: T T T T T T T T T NT):

```
Iteration  Actual  Prediction  Correct?  New bit
---------  ------  ----------  --------  -------
   1–9      T        T          Yes       1
   10       NT       T          No  ←     0
   1 (next) T        NT         No  ← Two misses!
   2        T        T          Yes       1
```

The predictor misses at the exit (NT) and then again at the first iteration of the next loop invocation (because it remembered the NT). This **double misprediction** is the defining failure of the 1-bit scheme.

## 2-Bit Saturating Counter

Each BHT entry holds a 2-bit counter with four states, arranged as a finite state machine:

```
         Taken            Taken
  00 ──────────→ 01 ──────────→ 11
  SN              WN              WT
  ←──────────  ←──────────
      NT               NT         

  00 = Strongly Not-Taken (predict NT)
  01 = Weakly Not-Taken   (predict NT)
  10 = Weakly Taken       (predict T)
  11 = Strongly Taken     (predict T)
```

Note: Some implementations use 10 as WT and 11 as ST (the exact encoding varies, but the FSM shape is the same).

**Prediction rule:** predict Taken if the top bit is 1, Not-Taken if top bit is 0.

**Update rule:**
- If outcome is Taken: increment (saturate at 11).
- If outcome is Not-Taken: decrement (saturate at 00).

### Loop Exit Revisited

Same 10-iteration loop, starting from state `11` (Strongly Taken):

```
Iteration  Actual  State before  Prediction  Correct?  State after
---------  ------  -----------   ----------  --------  -----------
   1–9      T        11            T           Yes       11
   10       NT       11            T           No        10
   1 (next) T        10            T           Yes       11
```

Only **one** misprediction at the exit — the strongly-taken state provides hysteresis that absorbs the single anomalous NT without flipping the prediction for the next execution.

## Hardware Implementation

```c
// Conceptual 2-bit saturating counter update in C
uint8_t update_2bit(uint8_t counter, int taken) {
    if (taken) {
        return (counter < 3) ? counter + 1 : 3;  // saturate at 11
    } else {
        return (counter > 0) ? counter - 1 : 0;  // saturate at 00
    }
}

// Prediction: top bit
int predict(uint8_t counter) {
    return counter >> 1;  // 1 if state >= 2 (WT or ST)
}
```

## Accuracy of 2-Bit Predictors

| Benchmark class     | 1-bit accuracy | 2-bit accuracy |
|---------------------|---------------|----------------|
| Integer (SPEC)      | ~83%          | ~87%           |
| Floating-point      | ~90%          | ~93%           |
| Loop-heavy          | ~75%          | ~92%           |

The improvement is most dramatic for regular loops (the double-misprediction problem). For highly irregular branches, both predictors perform similarly poorly — which motivates correlating predictors.

## BHT Size and Aliasing

A BHT with N entries uses log2(N) bits of PC for indexing. Typical parameters:

| BHT entries | PC bits used | Storage (2-bit/entry) |
|-------------|-------------|----------------------|
| 256         | 8           | 512 bits (64 B)      |
| 1024        | 10          | 2048 bits (256 B)    |
| 4096        | 12          | 8192 bits (1 KB)     |

Larger tables reduce destructive aliasing. Real processors use 4 K–16 K entries for the base predictor.

## Common Pitfall

Using only `PC[1:0]` (or not shifting out the byte-offset bits) means all branches within the same 4-byte word alias. Always index with `PC[k+1:2]` — strip the two least-significant bits first because RISC-V instructions are 4-byte aligned.

> **Interview answer:** A 2-bit saturating counter adds hysteresis to the 1-bit predictor: the state must be pushed twice in the same direction before the prediction flips. This eliminates the double-misprediction problem at loop exits while keeping each BHT entry at just 2 bits of storage.
