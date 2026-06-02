# Exercise: Line Number Filter

Practice reading input line-by-line and applying filters — a fundamental I/O pattern in Java.

Given a list of lines followed by a keyword, print every line that **contains** the keyword (case-sensitive), prefixed by its 1-based line number.

## Input format

```
<N>
<line 1>
<line 2>
...
<line N>
<keyword>
```

## Output format

One matching line per output line:

```
<line_number>: <original_line>
```

## Example

Input:
```
4
Hello world
Java is great
hello again
Goodbye world
world
```

Output:
```
1: Hello world
4: Goodbye world
```
