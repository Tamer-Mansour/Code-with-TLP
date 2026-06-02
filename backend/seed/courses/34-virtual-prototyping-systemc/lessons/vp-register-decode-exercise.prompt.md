# Exercise: Decode a Register Write into Bit-Field Effects

## Problem Description

You are building a peripheral register model. Given a 32-bit register description with named bit fields, each with an access type, compute the new register value after a firmware write.

Access type rules:
- **RW**: Replace field bits in current value with the written bits.
- **W1C**: For each bit in the field, if the written bit is 1, clear that bit in current value; if written bit is 0, leave it unchanged. Formula: `result &= ~(written & mask)`.
- **RO**: Ignore the written value entirely; current value bits are preserved. Formula: `result = (result & ~mask) | (current & mask)`.

Apply all field rules to a running `result` initialized to `current`, processing fields in the order they appear in input.

All values are 32-bit unsigned integers represented in hexadecimal (with `0x` prefix).

## Input Format

```
Line 1: N          (number of bit fields, 1 <= N <= 16)
Lines 2..N+1: each line describes one field as:
    <name> <hi> <lo> <access>
    where hi >= lo, 0 <= lo <= hi <= 31, access in {RW, W1C, RO}
Line N+2: current  <hex_value>   (current register value)
Line N+3: written  <hex_value>   (value firmware is writing)
```

Fields do not overlap. Together they may or may not cover all 32 bits; uncovered bits behave as RO (preserved from current).

## Output Format

```
<hex_value>
```

A single line: the resulting 32-bit register value in lowercase hexadecimal with `0x` prefix. Always print exactly 10 characters: `0x` followed by exactly 8 hex digits, zero-padded.

## Constraints

- 1 <= N <= 16
- 0 <= lo <= hi <= 31
- Fields do not overlap
- All values fit in a 32-bit unsigned integer
- Time limit: 3000 ms
- Memory limit: 256 MB

## Sample Input

```
3
STATUS 7 4 W1C
CTRL 3 2 RW
MODE 1 0 RO
current 0x000000ff
written 0x00000030
```

## Sample Output

```
0x000000c3
```

## Explanation of Sample

- Initialize `result = current = 0xFF`.
- STATUS field covers bits 7:4, mask = `((1<<4)-1) << 4 = 0xF0`. Access W1C: `result &= ~(written & mask)` = `0xFF & ~(0x30 & 0xF0)` = `0xFF & ~0x30` = `0xFF & 0xCF` = `0xCF`.
- CTRL field covers bits 3:2, mask = `0x0C`. Access RW: `result = (result & ~0x0C) | (written & 0x0C)` = `(0xCF & 0xF3) | (0x30 & 0x0C)` = `0xC3 | 0x00` = `0xC3`.
- MODE field covers bits 1:0, mask = `0x03`. Access RO: `result = (result & ~0x03) | (current & 0x03)` = `(0xC3 & 0xFC) | (0xFF & 0x03)` = `0xC0 | 0x03` = `0xC3`.
- Final result: `0x000000c3`.

## Additional Test Cases

**Test 2 — All RW fields:**
```
2
HIGH 31 16 RW
LOW 15 0 RW
current 0x00000000
written 0xdeadbeef
```
Expected: `0xdeadbeef`

**Test 3 — All RO:**
```
1
FULL 31 0 RO
current 0xabcdef12
written 0xffffffff
```
Expected: `0xabcdef12`

**Test 4 — W1C clears only written-1 bits:**
```
1
FLAGS 7 0 W1C
current 0x000000ff
written 0x0000000f
```
Expected: `0x000000f0`

**Test 5 — Mixed with uncovered bits (treated as RO):**
```
2
CTRL 3 2 RW
STATUS 7 6 W1C
current 0x000000ff
written 0x000000c4
```
Expected: `0x00000037`

Trace: result=0xFF. CTRL RW mask=0x0C: result=(0xFF&0xF3)|(0xC4&0x0C)=0xF3|0x04=0xF7. STATUS W1C mask=0xC0: result=0xF7&~(0xC4&0xC0)=0xF7&~0xC0=0xF7&0x3F=0x37.

**Test 6 — Single RW full register:**
```
1
DATA 31 0 RW
current 0x12345678
written 0xaabbccdd
```
Expected: `0xaabbccdd`
