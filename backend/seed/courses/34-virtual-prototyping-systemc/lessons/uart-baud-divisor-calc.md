# Computing a UART Baud-Rate Divisor

Configuring a UART correctly starts with calculating the right baud-rate divisor for the hardware. Get it wrong and you get framing errors, garbage output, or a completely silent line — often with no error message to guide you.

## The Formula

Most UART peripherals derive their baud clock from the system (peripheral) clock through a divider:

```
BRD = f_clk / (16 × baud_rate)
```

The factor of 16 comes from the UART's internal oversampling: it samples each incoming bit 16 times and takes a majority vote to reject noise. When oversampling by 8 is enabled (some high-speed modes), replace 16 with 8.

Many peripherals (ARM PL011, STM32 USART, TI UART) split the divisor into:

- **IBRD** — integer part: `floor(BRD)`
- **FBRD** — fractional part: `round(frac(BRD) × 64)` (for PL011) or `round(frac(BRD) × 16)` (for STM32)

### Worked Example

System clock `f_clk = 48 MHz`, target `baud_rate = 115200`.

```
BRD = 48_000_000 / (16 × 115200)
    = 48_000_000 / 1_843_200
    = 26.0417...

IBRD = 26
FBRD = round(0.0417 × 64) = round(2.67) = 3    (PL011 style)
```

Actual baud rate achieved:

```
actual = 48_000_000 / (16 × (26 + 3/64))
       = 48_000_000 / (16 × 26.046875)
       = 115_107 baud   (error = 0.08% — well within ±2% tolerance)
```

## What You Will Implement

In this exercise you will write a Python program that reads UART configuration parameters from standard input and prints the computed integer divisor, fractional divisor, the actual achieved baud rate, and the percentage error.

The exercise tests your ability to apply the UART baud-rate formula accurately, handle rounding correctly, and format numeric output to the required precision — exactly the kind of back-of-the-envelope calculation you will do when configuring a virtual UART model or debugging a physical one.

Your program must:

1. Read three values from stdin: `f_clk` (Hz, integer), `baud_rate` (integer), and `frac_bits` (integer — number of fractional bits in the hardware register, e.g. 6 for PL011, 4 for STM32).
2. Compute `BRD = f_clk / (16 * baud_rate)`.
3. Output `IBRD`, `FBRD` (rounded), actual baud rate (rounded to nearest integer), and percentage error (two decimal places).

See the prompt file for the exact input/output format and sample test cases.
