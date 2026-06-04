# Pipeline Hazard Detector

Simulate a 5-stage in-order pipeline (IF, ID, EX, MEM, WB) for a simple RISC-like instruction sequence. Detect RAW (Read After Write) data hazards and determine how many stall cycles must be inserted assuming **no forwarding** (a result is only available after the WB stage completes).

## Instruction Set

Each instruction is one of:

```
ADD  dst src1 src2   (writes dst, reads src1 and src2)
SUB  dst src1 src2   (writes dst, reads src1 and src2)
LOAD dst src         (writes dst, reads src)
STORE src val        (reads src; writes no register)
NOP                  (reads and writes no registers)
```

Registers are named `r0`–`r15`.

## Pipeline Timing Rules

- The pipeline reads source registers in the **ID stage**.
- A result is written to the register file in the **WB stage**.
- With no forwarding, ID of the consuming instruction must happen **strictly after** WB of the producing instruction completes.
- If a RAW hazard is detected, stall cycles are inserted before the consuming instruction's IF stage until the timing constraint is met.
- Stalls inserted for earlier instructions shift later instructions accordingly.

## Stall Count Formula

For two instructions where instruction J reads a register written by instruction I:

```
Stalls needed = max(0, WB_cycle(I) - ID_cycle(J))
```

where cycles are computed after accounting for all previously inserted stalls.

## Input Format

```
Line 1: N (number of instructions, 1 <= N <= 20)
Lines 2..N+1: one instruction per line
```

## Output Format

Print a single integer: the total number of stall cycles inserted.

## Examples

**Example 1 — No hazards**
```
Input:
3
ADD r1 r2 r3
ADD r4 r5 r6
ADD r7 r8 r9

Output:
0
```

**Example 2 — Single RAW hazard (adjacent instructions)**
```
Input:
2
ADD r1 r2 r3
ADD r4 r1 r5

Output:
2
```
Explanation: Without stalls, instruction 2 reads r1 in cycle 3 (ID), but instruction 1 writes r1 in cycle 5 (WB). Two stall cycles are inserted.

**Example 3 — RAW with NOP gap**
```
Input:
3
ADD r1 r2 r3
NOP
ADD r4 r1 r5

Output:
1
```
Explanation: With one NOP between them, effective gap is 2 cycles. WB(1) = cycle 5, ID(3) = cycle 4. Need 1 stall.

**Example 4 — NOP fills the hazard gap completely**
```
Input:
4
ADD r1 r2 r3
NOP
NOP
ADD r4 r1 r5

Output:
0
```

## Hints

- Track the actual cycle at which each instruction reaches IF (its IF cycle), accounting for all previously inserted stalls.
- ID cycle = IF cycle + 1; WB cycle = IF cycle + 4.
- For each instruction, scan all prior instructions to find the worst-case stall requirement.
- The worst case among all hazardous producers determines how many stalls to insert.
