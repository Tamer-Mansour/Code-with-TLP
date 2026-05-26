# Bitwise Operations Evaluator

Given two non-negative integers **A** and **B** (each fitting in a 16-bit unsigned integer, 0 ≤ A, B ≤ 65535) and a bitwise operation name, compute and print the result.

## Input Format

```
A B OP
```

Where `OP` is one of: `AND`, `OR`, `XOR`, `NAND`, `NOR`

For `NAND` and `NOR`, apply 16-bit masking (result & 0xFFFF).

## Output Format

A single integer: the result of applying OP to A and B.

## Examples

**Input:**
```
12 10 AND
```
**Output:**
```
8
```
Explanation: 12 = 0b1100, 10 = 0b1010, AND = 0b1000 = 8

**Input:**
```
12 10 XOR
```
**Output:**
```
6
```
Explanation: 0b1100 XOR 0b1010 = 0b0110 = 6

**Input:**
```
12 10 NAND
```
**Output:**
```
65527
```
Explanation: NOT(12 AND 10) = NOT(8) in 16 bits = 0xFFFF - 8 = 65527
