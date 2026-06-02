# Prompt: Parse an Instruction Trace to Find a Hang Loop

## Problem Statement

You are given a simplified CPU instruction trace: a list of records, one per line, each containing an instruction count and a program-counter (PC) value. Your task is to find the **tightest spin loop** — the smallest repeating block of unique PC addresses that the CPU is stuck executing.

A **spin loop** is a consecutive sequence of instructions where a fixed pattern of PC values (of length L >= 2) repeats at least **3 times in a row**. The pattern must consist of **exactly L distinct PC values** appearing in the same order each repetition.

Among all valid spin loops found in the trace, output the one with the **highest repeat count**. If two loops have the same repeat count, output the one with the **earliest start instruction count** (i.e., the loop that was entered first in the trace).

## Input Format

```
Line 1: N  (integer, the number of trace entries, 1 <= N <= 10000)
Lines 2..N+1: count PC
```

- `count` is a positive integer (instruction number, strictly increasing).
- `PC` is a hexadecimal address prefixed with `0x` (e.g., `0x000100a0`).
- All tokens on a line are separated by a single space.

## Output Format

If a spin loop is found:
```
LOOP START <count>
LOOP LENGTH <L>
PCS <pc1> <pc2> ... <pcL>
REPEATS <R>
```

- `START <count>` — the instruction count of the **first instruction of the first full repetition** of the winning loop.
- `LENGTH <L>` — the number of distinct PC values in one repetition.
- `PCS` — the PC values in the loop, in the order they appear during the first repetition, space-separated.
- `REPEATS <R>` — how many times the pattern repeats consecutively (at least 3).

If no spin loop exists:
```
NO LOOP
```

## Constraints

- 1 <= N <= 10000
- 2 <= L <= N/3 (only loops with at least 3 full repetitions are considered)
- PC values are 32-bit hex addresses (8 hex digits after `0x`)
- Instruction counts are strictly increasing positive integers
- The pattern must have **exactly L distinct** PC values (no repeated PCs within one cycle)
- `time_limit_ms`: 3000
- `memory_limit_mb`: 256
- Language: Python 3 (stdlib only)

## Sample Input 1

```
10
1 0x00010050
2 0x00010054
3 0x000100a0
4 0x000100a4
5 0x000100a0
6 0x000100a4
7 0x000100a0
8 0x000100a4
9 0x00010060
10 0x00010064
```

## Sample Output 1

```
LOOP START 3
LOOP LENGTH 2
PCS 0x000100a0 0x000100a4
REPEATS 3
```

Explanation: PCs `0x000100a0, 0x000100a4` repeat 3 times consecutively starting at instruction 3.

## Sample Input 2

```
5
1 0x00010000
2 0x00010004
3 0x00010008
4 0x0001000c
5 0x00010010
```

## Sample Output 2

```
NO LOOP
```

No pattern of length >= 2 repeats 3 or more times.

## Notes for Implementors

- Scan for every possible loop length L from 2 to N//3.
- For each L, slide through the trace looking for runs where the same L-PC pattern repeats consecutively.
- Track: the PC pattern, the start instruction count, and the repeat count.
- After scanning all L values, select the loop with the maximum repeat count (earliest start on ties).
- The loop must have all-distinct PCs within one period (e.g., `A B A` is NOT a valid period of length 3 because A repeats; it would be captured as a period of length 2: `A B`).
