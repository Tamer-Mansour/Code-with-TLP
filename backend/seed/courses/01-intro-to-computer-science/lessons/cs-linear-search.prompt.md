# Linear Search

Write a program that performs a linear search on a list of integers.

Each test case occupies two lines of input:
1. A space-separated list of integers (the list to search)
2. A single integer (the target value to find)

Print the **0-based index** of the first occurrence of the target in the list, or `-1` if the target is not present.

Process multiple test cases until EOF.

## Input format

```
<n1> <n2> ... <nk>
<target>
```

Repeat until EOF. The list on line 1 always contains at least one integer.

## Output format

One integer per test case: the index of the first occurrence, or -1.

## Example

**Input:**
```
3 1 4 1 5 9 7 6
7
10 20 30 40 50
25
5 5 5 5
5
1
1
```

**Output:**
```
6
-1
0
0
```
