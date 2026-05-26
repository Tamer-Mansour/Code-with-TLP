# Exercise: Hamming Distance and Parity

Hamming distance and parity are fundamental concepts in error detection and correction, used in DRAM ECC, RAID systems, network protocols, and QR codes.

## Background

### Hamming Distance

The **Hamming distance** between two bit strings of equal length is the number of positions at which they differ. It measures how many single-bit errors would be needed to transform one string into the other.

```
10110
01001
↕↕↕↕↕  ← all 5 positions differ
Distance = 5
```

In error-correcting codes, a code with minimum Hamming distance d can:
- **Detect** up to d−1 errors.
- **Correct** up to ⌊(d−1)/2⌋ errors.

DRAM ECC (Error-Correcting Code) memory uses Hamming(72,64): 64 data bits + 8 check bits, allowing detection of 2-bit errors and correction of 1-bit errors.

### Even Parity

A **parity bit** is appended to a bit string so that the total count of 1-bits is even (for even parity). This provides single-bit error detection: any single flipped bit changes the parity.

```
Data: 10110  → three 1s (odd count) → parity bit = 1
Transmitted: 101101
If any one bit flips, receiver detects wrong parity → error!
```

Parity is used in UART serial communication, PS/2 keyboard interfaces, and as a building block for more powerful codes.

## Task

Read one line with two equal-length binary strings. Output the Hamming distance on the first line and the even parity bit of the **first** string on the second line.
