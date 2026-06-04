# Exercise: Temperature Converter

Practice reading input, performing arithmetic, and formatting output by building a classic unit converter.

## What You Will Practice

- Reading floating-point input with `float(input())`
- Arithmetic operators: multiplication, division, addition
- f-string format specifiers (`:.2f`) for rounded output

## The Formula

To convert Celsius to Fahrenheit:

```
F = C × 9/5 + 32
```

Some reference points:

| Celsius | Fahrenheit |
|---------|------------|
| -273.15 | -459.67 (absolute zero) |
| -40     | -40 (the crossover point) |
| 0       | 32 (freezing) |
| 100     | 212 (boiling) |

## Key Concepts

**Reading a float from stdin:**
```python
celsius = float(input())
```

**Applying the formula:**
```python
fahrenheit = celsius * 9 / 5 + 32
```

**Formatting to 2 decimal places:**
```python
print(f"{fahrenheit:.2f}F")
```

The `:.2f` format specifier tells Python to display exactly two digits after the decimal point and to round if necessary.

## Common Mistakes

- Forgetting the `float()` cast — `input()` always returns a string.
- Writing `9/5` as integer division `9//5 = 1`, which gives the wrong answer — but in Python 3 `/` always produces a float, so this is fine.
- Adding a space before the `F` when the spec says no space.

## Further Reading

This exercise is a classic "hello world" of I/O. For a deeper look at Python's number types and arithmetic, see Chapter 2 of [*Think Python*](https://greenteapress.com/thinkpython2/thinkpython2.pdf) by Allen B. Downey (free PDF).
