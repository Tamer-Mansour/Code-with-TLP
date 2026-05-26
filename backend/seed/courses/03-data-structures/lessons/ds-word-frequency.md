# Exercise: Word Frequency Counter

Use a dictionary to count word occurrences, then print results in sorted order.

## Approach

```python
import sys
from collections import Counter

def solve():
    data = sys.stdin.read().split()
    n = int(data[0])
    words = data[1:n+1]
    freq = Counter(words)
    for word in sorted(freq):
        print(word, freq[word])

solve()
```

`Counter` builds the frequency map in O(n). Sorting the keys is O(k log k) where k is the number of distinct words.
