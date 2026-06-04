# Caesar Cipher

The Caesar cipher demonstrates how programs manipulate data at the character level — the same way a CPU operates on bytes. It also illustrates how character encoding (ASCII/Unicode) maps letters to numbers and back.

## What You Will Practice

- Reading and processing strings character-by-character
- Using `ord()` and `chr()` to convert between characters and their integer codes
- Modular arithmetic for wrapping (e.g., Z + 1 = A)
- Preserving case with `isupper()` / `islower()` checks

## Character Encoding Refresher

Every character is stored as a number:
- `'A'` = 65, `'B'` = 66, ..., `'Z'` = 90
- `'a'` = 97, `'b'` = 98, ..., `'z'` = 122

To shift a letter forward by K and wrap: `(ord(c) - ord('A') + K) % 26 + ord('A')`

## Approach

```python
k = int(input())
message = input()
result = []
for c in message:
    if c.isupper():
        shifted = (ord(c) - ord('A') + k) % 26 + ord('A')
        result.append(chr(shifted))
    elif c.islower():
        shifted = (ord(c) - ord('a') + k) % 26 + ord('a')
        result.append(chr(shifted))
    else:
        result.append(c)          # non-letter: unchanged
print(''.join(result))
```

This connection between character encoding and numeric manipulation is exactly how every text processing system — from compilers to web servers — handles characters under the hood.
