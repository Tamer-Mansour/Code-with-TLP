# C++ Uniform Initialization and Type Classification

Given a list of C++ variable declarations, determine:
1. Whether the initialization uses **uniform (brace) initialization** or **classic initialization**
2. Whether the variable type is **integral**, **floating**, **bool**, **string**, or **other**

## Input Format

- Line 1: integer `N`
- Lines 2..N+1: one declaration per line in the format `TYPE NAME = VALUE` or `TYPE NAME{VALUE}`
  - TYPE is one of: `int`, `double`, `float`, `bool`, `string`, `auto`
  - Brace initialization uses `{VALUE}`, classic uses `= VALUE`

## Output Format

For each declaration, one line:
```
NAME: TYPE_CLASS INIT_STYLE
```

Where:
- `TYPE_CLASS` is `integral` (int), `floating` (double/float), `bool`, `string`, or `auto`
- `INIT_STYLE` is `uniform` (braces) or `classic` (equals)

## Example

**Input:**
```
5
int x = 42
double pi{3.14}
bool flag = true
string name{hello}
auto count = 10
```

**Output:**
```
x: integral classic
pi: floating uniform
flag: bool classic
name: string uniform
count: auto classic
```

## Constraints

- `1 <= N <= 50`
- Variable names and values contain no spaces
- TYPE is always one of the listed types
