# Exercise: Rotate Array

Practice rotating an array to the right by k steps using the three-reversal algorithm or Python slicing.

## Approach

A clean O(n) in-place solution uses three reversals:

1. Reverse the entire array.
2. Reverse the first `k % n` elements.
3. Reverse the remaining elements.

This works because rotation by k is equivalent to splitting the array into two parts and swapping them, which three reversals achieve without extra memory.

## Starter Hint

```python
import sys

def solve():
    data = sys.stdin.read().split()
    n, k = int(data[0]), int(data[1])
    arr = list(map(int, data[2:2+n]))
    # TODO: rotate arr right by k steps
    print(*arr)

solve()
```
