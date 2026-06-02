# Exercise Prompt: Computing a UART Baud-Rate Divisor

## Background

UART peripherals derive their baud clock from the system clock using:

```
BRD        = f_clk / (16 * baud_rate)
IBRD       = floor(BRD)
FBRD       = round(frac(BRD) * 2^frac_bits)
actual_baud = f_clk / (16 * (IBRD + FBRD / 2^frac_bits))
error_pct  = abs(actual_baud - baud_rate) / baud_rate * 100
```

## Input Format

Three integers on separate lines:

```
f_clk       (system clock in Hz, integer)
baud_rate   (desired baud rate in bps, integer)
frac_bits   (fractional register width in bits, integer 1-8)
```

## Output Format

Four lines, in this order:

```
IBRD=<integer>
FBRD=<integer>
ACTUAL=<integer>
ERROR=<x.xx>%
```

- `IBRD` and `FBRD` are non-negative integers.
- `ACTUAL` is the achieved baud rate rounded to the nearest integer.
- `ERROR` is the absolute percentage error formatted to exactly 2 decimal places, followed by `%`.

## Constraints

- `f_clk` and `baud_rate` are positive integers.
- `frac_bits` is between 1 and 8 inclusive.
- `f_clk >= 16 * baud_rate` (BRD >= 1).

## Sample Input 1

```
48000000
115200
6
```

## Sample Output 1

```
IBRD=26
FBRD=3
ACTUAL=115177
ERROR=0.02%
```

**Explanation:**

- BRD = 48000000 / (16 * 115200) = 26.04166...
- IBRD = 26
- FBRD = round(0.04166... * 64) = round(2.666...) = 3
- divisor = 26 + 3/64 = 26.046875
- actual = 48000000 / (16 * 26.046875) = 115177.08... -> 115177
- error = |115177 - 115200| / 115200 * 100 = 0.02%

## Sample Input 2

```
16000000
9600
4
```

## Sample Output 2

```
IBRD=104
FBRD=3
ACTUAL=9598
ERROR=0.02%
```
