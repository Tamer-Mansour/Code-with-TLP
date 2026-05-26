# Hexadecimal: Base-16

Binary is perfect for hardware but awkward for humans: the number 255 requires eight digits (`11111111`) in binary. **Hexadecimal** (base-16, often called "hex") offers a compact shorthand that maps perfectly onto binary, which is why it appears everywhere in computing—from memory addresses to color codes to file formats.

## Base-16 Digits

Hexadecimal uses 16 symbols. Since we only have 10 Arabic numerals, we borrow letters A–F for values 10–15:

| Hex | Decimal | 4-bit Binary |
|-----|---------|--------------|
| 0   | 0       | 0000         |
| 1   | 1       | 0001         |
| 2   | 2       | 0010         |
| 3   | 3       | 0011         |
| 4   | 4       | 0100         |
| 5   | 5       | 0101         |
| 6   | 6       | 0110         |
| 7   | 7       | 0111         |
| 8   | 8       | 1000         |
| 9   | 9       | 1001         |
| A   | 10      | 1010         |
| B   | 11      | 1011         |
| C   | 12      | 1100         |
| D   | 13      | 1101         |
| E   | 14      | 1110         |
| F   | 15      | 1111         |

Notice: the letters are **case-insensitive**—`0xFF`, `0Xff`, and `0XFF` all mean the same value.

Hex is written with a `0x` prefix in code (e.g., `0xFF`) or a `#` prefix in CSS color codes (e.g., `#FF5733`).

## Why Hex Maps Perfectly onto Binary

One hex digit represents exactly **4 bits** (a nibble). Since 2⁴ = 16, the math works out exactly:

```
Binary:   1010  1111  0011  1100
               ↓         ↓         ↓         ↓
Hex:        A         F         3         C      →  0xAF3C
```

**To convert binary → hex:** split into groups of 4 bits from the right, then look up each group in the table.

**To convert hex → binary:** replace each hex digit with its 4-bit binary equivalent.

**Worked example:** Convert `0xB7` to binary.
- `B` = 1011
- `7` = 0111
- Result: `1011 0111`

**Worked example:** Convert `1110 0101` to hex.
- `1110` = E
- `0101` = 5
- Result: `0xE5`

This one-to-one correspondence between nibbles and hex digits is why hex is the standard shorthand for binary data. Two hex digits always represent exactly one byte (8 bits).

## Converting Hex → Decimal

Each position represents a power of **16**, just as each position in decimal represents a power of 10:

**Example: `0x2A`**

```
  2  ×  16¹  =   2  ×  16  =  32
  A  ×  16⁰  =  10  ×   1  =  10
                                ──
                                42
```

**Example: `0xFF`**

```
  F  ×  16¹  =  15  ×  16  = 240
  F  ×  16⁰  =  15  ×   1  =  15
                               ───
                               255
```

That is why `0xFF` represents 255—the maximum value of one byte.

**Example: `0x1A4`** (a 3-digit hex number)

```
  1  ×  16²  =   1  ×  256  = 256
  A  ×  16¹  =  10  ×   16  = 160
  4  ×  16⁰  =   4  ×    1  =   4
                               ───
                               420
```

## Converting Decimal → Hex

Divide by 16 repeatedly, recording remainders. If a remainder is 10–15, convert it to the letter A–F.

**Example: Convert 300 to hex.**

```
300 ÷ 16 = 18  remainder 12  →  C
 18 ÷ 16 =  1  remainder  2  →  2
  1 ÷ 16 =  0  remainder  1  →  1
```

Reading bottom to top: **0x12C**

Verify: 1 × 256 + 2 × 16 + 12 = 256 + 32 + 12 = 300 ✓

**Example: Convert 1000 to hex.**

```
1000 ÷ 16 = 62  remainder  8  →  8
  62 ÷ 16 =  3  remainder 14  →  E
   3 ÷ 16 =  0  remainder  3  →  3
```

Result: **0x3E8** → verify: 3 × 256 + 14 × 16 + 8 = 768 + 224 + 8 = 1000 ✓

## Hex in Python

Python makes working with hex easy:

```python
# Decimal to hex
print(hex(255))    # '0xff'
print(hex(300))    # '0x12c'

# Hex literal to decimal
x = 0xFF           # x = 255
y = 0x12C          # y = 300

# Hex string to integer
n = int("FF", 16)  # n = 255

# Format as uppercase hex
print(f"{255:X}")  # 'FF'
print(f"{255:08X}")# '000000FF'  (8 digits, zero-padded)
```

## Real-World Uses of Hex

| Context | Example | What it represents |
|---------|---------|-------------------|
| **Memory addresses** | `0x7FFF5FBF` | A location in a 64-bit RAM address space |
| **Web color codes** | `#FF5733` | R=255, G=87, B=51 |
| **Unicode code points** | `U+0041` | The character 'A' |
| **MAC addresses** | `00:1A:2B:3C:4D:5E` | A network interface hardware ID |
| **Error codes (Windows)** | `0xC0000005` | Access violation / segmentation fault |
| **File magic bytes** | `89 50 4E 47` | First 4 bytes of any PNG file |
| **IPv6 addresses** | `2001:0db8::1` | A network address |
| **SHA-256 hashes** | `a9d4...b7c2` | 64 hex digits = 32 bytes |

### File Magic Bytes in Detail

Many file formats begin with a special sequence of bytes called a "magic number" that identifies the file type—regardless of the file extension. Hex makes these easy to read:

| File type | Magic bytes (hex) | ASCII equivalent |
|-----------|-------------------|-----------------|
| PNG image | `89 50 4E 47` | `.PNG` |
| JPEG image | `FF D8 FF` | — |
| PDF | `25 50 44 46` | `%PDF` |
| ZIP / Office | `50 4B 03 04` | `PK..` |
| ELF executable (Linux) | `7F 45 4C 46` | `.ELF` |

This is why renaming a `.jpg` to `.png` does not make it a valid PNG—the file's content (its magic bytes) still identifies it as a JPEG.

## Summary of Number Bases

| Base | Name | Digits | Prefix | Notes |
|------|------|--------|--------|-------|
| 2   | Binary      | 0–1       | `0b`  | Native to hardware |
| 8   | Octal       | 0–7       | `0o`  | Used in Unix file permissions |
| 10  | Decimal     | 0–9       | none  | Human everyday use |
| 16  | Hexadecimal | 0–9, A–F  | `0x`  | Compact binary shorthand |

## Common Misconceptions

**"Hex is harder than decimal."**
For humans counting in daily life, decimal is natural. But for reading raw binary data—a byte stream, a color value, a memory address—hex is far more compact and regular than either binary or decimal.

**"`0xFF` is a large number."**
255 is not large in any absolute sense. The `0x` just tells you the number is written in base 16. `0xFF = 255`, a value that fits in a single byte.

**"Color #FFFFFF is some strange code."**
`#FFFFFF` means R=`FF`=255, G=`FF`=255, B=`FF`=255—full intensity on all three channels, which the eye sees as white. Once you know hex, color codes become self-explanatory.

## Key Takeaways

- Hexadecimal (base-16) uses digits 0–9 and letters A–F.
- One hex digit = exactly 4 binary bits; two hex digits = one byte. Conversion is trivial.
- Converting hex → decimal: multiply each digit by its power of 16 and sum.
- Converting decimal → hex: divide by 16 repeatedly; read remainders as hex digits bottom to top.
- Hex appears everywhere in real computing: memory addresses, colors, file formats, error codes, hashes.
