# Caesar Cipher

The Caesar cipher is one of the oldest encryption techniques. Each letter in the plaintext is shifted by a fixed number of positions in the alphabet. Non-letter characters are left unchanged.

Read two lines from standard input:

1. **Line 1:** An integer `K` (0 ≤ K ≤ 25) — the shift amount.
2. **Line 2:** A string — the message to encrypt.

Shift each **letter** forward by `K` positions in the alphabet, wrapping around from Z back to A. Preserve the original case (uppercase stays uppercase, lowercase stays lowercase). Leave all non-letter characters unchanged.

Print the encrypted message.

## Input format

```
K
message
```

## Output format

The encrypted message on one line.

## Examples

**Input:**
```
3
Hello, World!
```

**Output:**
```
Khoor, Zruog!
```

**Input:**
```
13
The Quick Brown Fox
```

**Output:**
```
Gur Dhvpx Oebja Sbk
```

**Input:**
```
0
No change here.
```

**Output:**
```
No change here.
```

## Hints

- `ord('A')` = 65, `ord('a')` = 97
- `chr()` converts an integer back to a character
- Use `(ord(c) - ord('A') + K) % 26 + ord('A')` for uppercase
