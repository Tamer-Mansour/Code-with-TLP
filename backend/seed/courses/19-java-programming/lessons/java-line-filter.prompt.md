# Line Number Filter

Read N lines from stdin, then read a keyword. Print every line that contains the keyword (case-sensitive), prefixed by its 1-based line number in the format `<n>: <line>`.

**Input format:**
```
N
line1
line2
...
lineN
keyword
```

**Output:** One matching line per output line: `<line_number>: <original_line>`

**Example:**

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
