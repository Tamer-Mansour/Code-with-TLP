# FizzBuzz with Configurable Range

Read two integers `N` and `M` from stdin (one per line). `M` is present but unused.

Print every integer from `1` to `N` (inclusive). Replace:
- multiples of **3** with `Fizz`
- multiples of **5** with `Buzz`
- multiples of **both 3 and 5** with `FizzBuzz`
- otherwise print the integer itself

After the sequence, print one final line: `Plain numbers: <count>` where `<count>` is how many integers were printed as plain numbers (not Fizz / Buzz / FizzBuzz).

## Input format

```
N
M
```

## Output format

One line per integer from `1` to `N`, then a summary line.

## Example

**Input**
```
15
0
```

**Output**
```
1
2
Fizz
4
Buzz
Fizz
7
8
Fizz
Buzz
11
Fizz
13
14
FizzBuzz
Plain numbers: 8
```

## Constraints

- `1 <= N <= 100`
