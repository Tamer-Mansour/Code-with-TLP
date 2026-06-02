# Capstone Exercise: Run-Length Encoding

Run-Length Encoding (RLE) is a simple compression scheme where consecutive identical characters are replaced by a count and the character.

## Input

A single line of text containing only lowercase ASCII letters and digits. The string length is 1–1000 characters.

## Task

- **Encode**: if the input contains no digits, apply RLE encoding. Replace runs of consecutive identical characters with `<count><char>`. A run of length 1 is written as `1<char>`.
- **Decode**: if the input starts with a digit, decode it back to the original string. Consecutive digit characters before a letter form the count.

## Output

Print the encoded or decoded string on a single line.

## Examples

Encoding:
```
aaabccddddee
```
Output:
```
3a1b2c4d2e
```

Decoding:
```
3a1b2c4d2e
```
Output:
```
aaabccddddee
```
