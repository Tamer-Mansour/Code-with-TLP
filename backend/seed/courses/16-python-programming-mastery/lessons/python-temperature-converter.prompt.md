# Temperature Converter

Write a program that reads a temperature in Celsius from standard input as a floating-point number, converts it to Fahrenheit using the formula:

```
F = C * 9/5 + 32
```

Print the result rounded to 2 decimal places immediately followed by the letter `F` (no space).

## Input

A single line containing one floating-point number representing degrees Celsius.

## Output

A single line: the Fahrenheit value rounded to 2 decimal places, immediately followed by `F`.

## Examples

**Example 1**
```
Input:  100
Output: 212.00F
```

**Example 2**
```
Input:  0
Output: 32.00F
```

**Example 3**
```
Input:  -40
Output: -40.00F
```

## Notes

- Use `float(input())` to read the value.
- Use an f-string with `:.2f` format specifier to round to 2 decimal places.
- Do not print a space between the number and the `F`.
