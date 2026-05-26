# Internet Checksum

Compute the Internet checksum (RFC 1071) of a sequence of 16-bit words.

## Algorithm

1. Read the space-separated 16-bit words.
2. Sum them all using regular integer addition.
3. Fold any carry bits back into the 16-bit result: `total = (total >> 16) + (total & 0xFFFF)`, repeat until no carry.
4. Take the one's complement: `checksum = (~total) & 0xFFFF`.
5. Print the result as a decimal integer.

## Input

A single line of space-separated non-negative integers, each in [0, 65535].

## Output

A single decimal integer in [0, 65535].

## Examples

**Input:** `46336 5888`  
**Output:** `13311`

(0xB500 + 0x1700 = 0xCC00; ~0xCC00 & 0xFFFF = 0x33FF = 13311)

**Input:** `0`  
**Output:** `65535`

(~0x0000 & 0xFFFF = 0xFFFF = 65535)

**Input:** `65535`  
**Output:** `0`

(0xFFFF; fold carry: 0xFFFF → still 0xFFFF; ~0xFFFF & 0xFFFF = 0)

**Input:** `256 512 1024`  
**Output:** `64743`

(0x0100 + 0x0200 + 0x0400 = 0x0700; ~0x0700 & 0xFFFF = 0xF8FF = 63743)

Wait — let me recalculate: ~0x0700 = 0xF8FF = 63743. Output: 63743.

## Constraints

- At least one word in the input.
- Use only the Python standard library.
