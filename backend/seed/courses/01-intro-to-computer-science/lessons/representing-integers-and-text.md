# Representing Integers and Text

Every piece of information a computer handles—whether a number, a letter, or an emoji—is ultimately stored as a pattern of 0s and 1s. This lesson explains exactly how integers and text are encoded in memory, why those design decisions were made, and what goes wrong when things are misused.

## Integers

### Unsigned Integers

The simplest encoding: treat the binary pattern directly as a non-negative whole number.

With *n* bits, you can represent 2ⁿ different values: **0 through 2ⁿ − 1**.

| Bits | Range | Common use |
|------|-------|------------|
| 8   | 0 – 255           | Byte, pixel color channel, ASCII character code |
| 16  | 0 – 65,535        | Port numbers, small counters |
| 32  | 0 – 4,294,967,295 | Array indices, IPv4 addresses |
| 64  | 0 – ~18.4 × 10¹⁸  | File sizes, timestamps, 64-bit pointers |

**Worked example:** What 8-bit unsigned integer corresponds to `0100 1101`?

Position weights (right to left): 1, 2, 4, 8, 16, 32, 64, 128.
Bits set: positions 0 (1), 2 (4), 3 (8), 6 (64).
Sum: 1 + 4 + 8 + 64 = **77**.

### Signed Integers: Two's Complement

To represent negative numbers, modern computers use **two's complement**. With *n* bits, the range is **−2^(n−1) through 2^(n−1) − 1**.

For 8-bit signed integers: −128 to 127.

**The sign bit rule:** The most significant (leftmost) bit acts as the *sign bit*. If it is 1, the number is negative.

| Binary | Unsigned value | Signed 8-bit value |
|--------|----------------|---------------------|
| `0000 0001` | 1   | 1   |
| `0111 1111` | 127 | 127 |
| `1000 0000` | 128 | −128 |
| `1111 1110` | 254 | −2  |
| `1111 1111` | 255 | −1  |

**How to find the two's complement of a number:**
1. Write the positive version in binary.
2. Flip all the bits (0 → 1, 1 → 0). This is called the *one's complement*.
3. Add 1.

**Example: Find the 8-bit two's complement of −46.**
1. 46 in binary: `0010 1110`
2. Flip bits: `1101 0001`
3. Add 1: `1101 0010`

Verify: `1101 0010` as unsigned = 210. Since 210 + 46 = 256 = 2⁸, we know −46 is represented as 210 in an 8-bit two's complement system. ✓

**Why two's complement?** The crucial advantage: **addition works without knowing the signs**. The same adder circuit handles positive + positive, positive + negative, and negative + negative identically. No special cases needed in hardware.

Demonstration: 5 + (−3) in 8-bit two's complement:
```
  0000 0101   (5)
+ 1111 1101   (-3, the two's complement of 3)
─────────────
1 0000 0010   = 2, with a carry-out that is discarded ✓
```

### Integer Overflow

If a calculation produces a result outside the representable range, **integer overflow** occurs and the value wraps around.

**Example:** In an 8-bit unsigned integer, 255 + 1 = 0 (wraps to zero). In a signed 8-bit integer, 127 + 1 = −128.

Real-world consequences: the Y2K bug arose partly from 2-digit year fields wrapping; many video game bugs occur from score or health counters overflowing. In 1996, an Ariane 5 rocket was destroyed because a 64-bit float was converted to a 16-bit integer, causing overflow and a fatal software exception.

**In Python:** Python integers have *arbitrary precision*—they grow as large as your memory allows and never overflow. This is convenient but uses more memory than fixed-width types.

```python
print(2 ** 100)
# 1267650600228229401496703205376  — no overflow in Python
```

In contrast, C's `int` is typically 32 bits and silently overflows.

## Text: ASCII

How does a computer store the letter `A`? By agreeing on a standard mapping between numbers and characters.

**ASCII** (American Standard Code for Information Interchange, 1963) assigns a 7-bit number (0–127) to each character:

| Character | Decimal | Binary (7-bit) | Notes |
|-----------|---------|----------------|-------|
| `NUL`     | 0       | `000 0000`     | Null character (string terminator in C) |
| `TAB`     | 9       | `000 1001`     | Horizontal tab |
| `LF`      | 10      | `000 1010`     | Line feed (newline on Unix) |
| `CR`      | 13      | `000 1101`     | Carriage return (Windows uses CR+LF) |
| `Space`   | 32      | `010 0000`     | — |
| `0`–`9`   | 48–57   | —              | Digit '0' = 48, '1' = 49, … |
| `A`–`Z`   | 65–90   | —              | Uppercase letters |
| `a`–`z`   | 97–122  | —              | Lowercase letters |

**Key pattern:** lowercase letters are exactly 32 more than their uppercase versions. In binary, that means flipping bit 5. This is why the ASCII `AND`/`OR` tricks for toggling case work.

```python
print(ord('A'))   # 65
print(ord('a'))   # 97
print(chr(65))    # 'A'
print(chr(97))    # 'a'
print(ord('a') - ord('A'))  # 32
```

ASCII covers only 128 characters: the English alphabet, digits, punctuation, and some control codes. That is not enough for the world's languages.

## Text: Unicode and UTF-8

**Unicode** is a universal standard that assigns a unique *code point* (a number) to every character in every writing system on Earth. As of Unicode 15.1, it defines over **149,000 characters**, including emoji, ancient scripts, and mathematical symbols.

Code point notation: `U+` followed by 4–6 hex digits.

| Character | Code point | Notes |
|-----------|------------|-------|
| `A`  | U+0041 | Latin capital A |
| `é`  | U+00E9 | Latin small e with acute |
| `中` | U+4E2D | Chinese character "middle" |
| `Δ`  | U+0394 | Greek capital delta |
| `😀` | U+1F600 | Grinning face emoji |
| `☃`  | U+2603 | Snowman |

Unicode defines the *code point* (the number) but not how to store it in bytes. That is the job of an *encoding*.

### UTF-8: The Dominant Encoding

**UTF-8** is the most common encoding of Unicode. It is a **variable-length** encoding:

| Code point range | Bytes used | Bit pattern |
|------------------|-----------|-------------|
| U+0000 – U+007F   | 1 | `0xxxxxxx` |
| U+0080 – U+07FF   | 2 | `110xxxxx 10xxxxxx` |
| U+0800 – U+FFFF   | 3 | `1110xxxx 10xxxxxx 10xxxxxx` |
| U+10000 – U+10FFFF | 4 | `11110xxx 10xxxxxx 10xxxxxx 10xxxxxx` |

**Critical property:** code points 0–127 use exactly 1 byte, identical to ASCII. This makes UTF-8 **backward-compatible with ASCII**—every valid ASCII file is also valid UTF-8.

**Example in Python:**

```python
text = "Hello 😀"
encoded = text.encode("utf-8")
print(encoded)
# b'Hello \xf0\x9f\x98\x80'
#   H(1) e(1) l(1) l(1) o(1) ' '(1) 😀(4) = 10 bytes total
print(len(text))     # 7 characters
print(len(encoded))  # 10 bytes
```

Note: `len(text)` counts **characters** (code points); `len(encoded)` counts **bytes**. For ASCII text they are the same; for text with emoji or non-Latin characters they differ. Confusing the two is a common source of bugs.

### UTF-16 and UTF-32

- **UTF-16** uses 2 or 4 bytes per character. Used internally by Windows, Java, and JavaScript.
- **UTF-32** uses exactly 4 bytes per character. Simple but wastes space for mostly-ASCII text.
- **UTF-8** dominates on the web (>98% of web pages) because of its ASCII compatibility and space efficiency.

## The Encoding Declaration Problem

When you open a file, you must know its encoding to interpret it correctly. If you open a UTF-8 file and interpret it as Latin-1, accented characters become garbled—this is called *mojibake* (文字化け). Always declare or detect the encoding:

```python
# Explicit encoding is best practice
with open("data.txt", encoding="utf-8") as f:
    content = f.read()
```

## Why This Matters

- When you see garbled characters (like `Ã©` instead of `é`), the program is using the wrong encoding to interpret the bytes.
- Knowing that `'A'` == 65 lets you write code like `ord('A')` or compute letter offsets.
- Security vulnerabilities—such as SQL injection and buffer overflows—often arise from programs that confuse byte lengths with character lengths, especially in web applications handling multi-byte Unicode text.
- Sorting text correctly requires knowing the encoding *and* the locale (language rules for ordering characters).

## Key Takeaways

- Unsigned integers map binary directly to non-negative numbers; signed integers use **two's complement**, which allows the same hardware adder to work for positive and negative numbers.
- **Integer overflow** wraps the value around silently in most languages (but not Python).
- **ASCII** encodes 128 characters in 7 bits; lowercase letters are exactly 32 above uppercase.
- **Unicode** assigns a code point to every character in every writing system (149,000+); **UTF-8** is the dominant encoding, using 1–4 bytes per code point and staying backward-compatible with ASCII.
- Always be explicit about encoding when reading or writing text files.
