# Prompt: Split a Virtual Address Into Page Number and Offset

## Problem Statement

Given a page size (always a power of two) and a list of virtual addresses, split each virtual address into its **Virtual Page Number (VPN)** and its **byte offset** within the page.

Use the following formulas:

```
offset_bits = log2(page_size)
VPN         = virtual_address >> offset_bits
offset      = virtual_address  &  (page_size - 1)
```

Print each result on its own line as two decimal integers separated by a single space: `VPN offset`.

## Input Format

```
Line 1: page_size          (integer, power of two, 64 <= page_size <= 1073741824)
Line 2: n                  (integer, 1 <= n <= 1000)
Lines 3..n+2: virtual_address  (non-negative integer, fits in 64-bit unsigned)
```

## Output Format

For each virtual address (in order), print one line:

```
VPN offset
```

Both values are printed as plain decimal integers.

## Constraints

- `page_size` is always a power of two.
- All virtual addresses are non-negative and fit in a 64-bit unsigned integer.
- 1 <= n <= 1000
- No trailing spaces; one newline after each line.

## Sample Input 1

```
4096
3
0
4096
8193
```

## Sample Output 1

```
0 0
1 0
2 1
```

**Explanation:**
- Page size = 4096, offset bits = 12.
- `0 >> 12 = 0`, `0 & 4095 = 0`
- `4096 >> 12 = 1`, `4096 & 4095 = 0`
- `8193 >> 12 = 2`, `8193 & 4095 = 1`

## Sample Input 2

```
256
4
255
256
512
1023
```

## Sample Output 2

```
0 255
1 0
2 0
3 255
```
