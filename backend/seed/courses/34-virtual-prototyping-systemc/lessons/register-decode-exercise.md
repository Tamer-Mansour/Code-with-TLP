# Decode a Register Write into Bit-Field Effects

In this exercise you will implement a register write decoder that correctly applies per-field access semantics to produce the new register value after a firmware write.

## What You Will Implement

Given a 32-bit register's current value, a firmware-written value, and a description of its bit fields (each with an access type of RO, RW, or W1C), compute the resulting register value after the write completes.

The rules are:
- **RW** field: replace the field bits in the current value with the written bits.
- **W1C** field: for each bit in the field, if the written bit is 1, clear that bit in the current value; if 0, leave it unchanged.
- **RO** field: written value is ignored; current value is preserved.

## Skills Practiced

- Applying bitmask operations (`&`, `|`, `~`, `<<`, `>>`)
- Modeling per-field access semantics independently within a register word
- Translating a hardware register specification into deterministic software logic

## Example

A register has three fields:

| Field | Bits | Access |
|-------|------|--------|
| STATUS | 7:4 | W1C |
| CTRL | 3:2 | RW |
| MODE | 1:0 | RO |

Current value: `0xFF` (binary `11111111`)
Written value: `0x30` (binary `00110000`)

Expected result: `0xCF` — the W1C STATUS field had bits 7:4 written as `0011`, so only bits 5 and 4 are cleared (bits 7 and 6 stay set because written bits were 0). CTRL is written as `00`. MODE is RO and stays `11`.

Work through the solution step by step, writing a Python program that reads the register description and access from standard input and prints the resulting register value.
