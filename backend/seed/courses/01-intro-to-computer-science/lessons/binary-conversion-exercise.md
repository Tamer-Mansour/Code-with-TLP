# Exercise: Binary ↔ Decimal Converter

Practice binary and decimal conversions by building a simple converter program.

Given a string in the format `"B <number>"` or `"D <number>"`, your program should:

- If the prefix is `B`, treat `<number>` as a **binary** string and print its **decimal** value.
- If the prefix is `D`, treat `<number>` as a **decimal** integer and print its **binary** representation (no leading zeros, except the number 0 itself which prints as `0`).

Each line of input is one conversion request. Read until EOF.

## Example

**Input:**
```
B 1010
D 13
B 11111111
D 0
```

**Output:**
```
10
1101
255
0
```
