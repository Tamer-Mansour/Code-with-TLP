# Exercise: Hamming(7,4) Error Detection and Correction

The **Hamming(7,4)** code is the foundation of single-bit error correction used in ECC RAM, SECDED codes in enterprise hardware, and as a pedagogical introduction to forward error correction. It encodes 4 data bits into a 7-bit codeword by inserting 3 parity bits at positions 1, 2, and 4 (powers of two).

## Bit Layout

```
Position: 1   2   3   4   5   6   7
Bit type: p1  p2  d1  p3  d2  d3  d4
```

- **Parity bit p1** (position 1) covers positions 1, 3, 5, 7 → checks d1, d2, d4
- **Parity bit p2** (position 2) covers positions 2, 3, 6, 7 → checks d1, d3, d4
- **Parity bit p3** (position 4) covers positions 4, 5, 6, 7 → checks d2, d3, d4

Each parity bit is set to make XOR of its covered positions equal 0 (even parity).

## Error Detection via Syndrome

The receiver computes a 3-bit syndrome `(s1, s2, s3)`:

```python
s1 = r[1] ^ r[3] ^ r[5] ^ r[7]
s2 = r[2] ^ r[3] ^ r[6] ^ r[7]
s3 = r[4] ^ r[5] ^ r[6] ^ r[7]
error_position = s1 + 2*s2 + 4*s3
```

If `error_position == 0`, no error. Otherwise, `error_position` is the index of the corrupted bit — flip it to correct the codeword.

## What You Need to Implement

Given a 4-bit data string, encode it into a valid 7-bit Hamming codeword. Then, given a received 7-bit codeword (which may have one bit error), detect and correct any error and recover the original 4-bit data.

For the full input/output format, see the exercise prompt.

## Example Encoding: data = "1010"

```
d1=1, d2=0, d3=1, d4=0
bits[3]=1, bits[5]=0, bits[6]=1, bits[7]=0

p1 = d1 ^ d2 ^ d4 = 1^0^0 = 1   (covers positions 1,3,5,7)
p2 = d1 ^ d3 ^ d4 = 1^1^0 = 0   (covers positions 2,3,6,7)
p3 = d2 ^ d3 ^ d4 = 0^1^0 = 1   (covers positions 4,5,6,7)

Codeword: p1 p2 d1 p3 d2 d3 d4 = 1 0 1 1 0 1 0 = "1011010"
```

## Further Reading

- *Error Detection in Networks* — see the lesson in this module for a full treatment of CRC, parity, and Hamming codes.
- *Computer Networks: A Top-Down Approach* by Kurose & Ross, Chapter 6 (Link Layer):
  https://archive.org/details/computernetworki0000jame_y6m8
