# Exercise: Hexadecimal Converter

Practice your understanding of hexadecimal notation by building a two-way converter.

Given a string in the format `"H <number>"` or `"D <number>"`:

- If the prefix is `H`, treat `<number>` as a **hexadecimal** string (uppercase, no `0x` prefix) and print its **decimal** value.
- If the prefix is `D`, treat `<number>` as a **decimal** integer and print its **uppercase hexadecimal** representation without leading zeros or `0x` prefix. Exception: `0` prints as `0`.

Each line of input is one conversion request. Read until EOF.

## Example

**Input:**
```
H FF
D 255
H 1A
D 0
H 10
D 16
```

**Output:**
```
255
FF
26
0
16
16
```

## Hints

- In Python, `int("FF", 16)` converts hex string `"FF"` to decimal integer 255.
- `hex(255)` returns `'0xff'`; use `hex(n)[2:].upper()` or `format(n, 'X')` to get `'FF'`.
