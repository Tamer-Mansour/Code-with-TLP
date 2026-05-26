# Float to IEEE 754 Bits

Given a decimal floating-point number (guaranteed to be exactly representable in IEEE 754 single precision), output its 32-bit IEEE 754 single-precision binary representation as a string of 32 `0`s and `1`s.

## Input

One line containing a single decimal number. The number is guaranteed to be exactly representable in IEEE 754 single precision (e.g., powers of 2, sums of powers of 2 with short binary representations).

## Output

One line: the 32-bit IEEE 754 single-precision bit string, MSB first (sign bit first).

## Constraints

- The input number fits in a 32-bit IEEE 754 float exactly.
- No special values (infinity, NaN, denormals).

## Examples

```
Input:  1.0
Output: 00111111100000000000000000000000
```

```
Input:  -0.375
Output: 10111110110000000000000000000000
```

```
Input:  0.0
Output: 00000000000000000000000000000000
```

## Hint

Recall that IEEE 754 single precision is: `sign(1) | exponent(8, biased by 127) | fraction(23)`.
To encode value `v`:
1. Convert `|v|` to binary scientific notation: `1.fraction × 2^exp`.
2. Stored exponent = `exp + 127`.
3. Concatenate sign, 8-bit exponent, 23-bit fraction.
