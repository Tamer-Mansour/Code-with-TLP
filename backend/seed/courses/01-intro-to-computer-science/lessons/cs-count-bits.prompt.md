# Count the Bits

Given a non-negative decimal integer, count how many `1` bits appear in its binary representation. This is also known as the **popcount** or **Hamming weight**.

Read one integer per line from standard input until EOF. For each integer, print the count of `1` bits in its binary form.

## Input format

Each line contains a single non-negative integer (0 ≤ n ≤ 65535).

## Output format

One integer per line: the number of `1` bits in the binary representation of the input.

## Examples

| Input | Binary | Output |
|-------|--------|--------|
| 0 | 0 | 0 |
| 1 | 1 | 1 |
| 7 | 111 | 3 |
| 255 | 11111111 | 8 |
| 10 | 1010 | 2 |
