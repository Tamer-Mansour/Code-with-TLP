# Worker Pool Sum

The Go equivalent:

```go
sum := 0
for _, n := range nums {
    sum += n
}
fmt.Println(sum)
```

## Input

```
N
<integer 1> <integer 2> ... <integer N>
```

`N` is the count (0 ≤ N ≤ 10000). The integers follow on subsequent lines (whitespace-separated, possibly spread across lines).

## Output

A single integer: the sum.

## Examples

Input:

```
5
1 2 3 4 5
```

Output: `15`

Input:

```
4
-10 5 -3 8
```

Output: `0`

Input:

```
0
```

Output: `0`
