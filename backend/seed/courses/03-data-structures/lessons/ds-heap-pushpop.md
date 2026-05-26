# Exercise: Min-Heap Push/Pop Sequence

Simulate a min-heap and output the result of each POP command.

## Approach

Use Python's `heapq` module which provides a min-heap directly.

```python
import heapq
import sys

def solve():
    data = sys.stdin.read().split('\n')
    q = int(data[0])
    heap = []
    out = []
    for i in range(1, q + 1):
        line = data[i].strip()
        if line.startswith('PUSH'):
            val = int(line.split()[1])
            heapq.heappush(heap, val)
        elif line == 'POP':
            if heap:
                out.append(str(heapq.heappop(heap)))
            else:
                out.append('EMPTY')
    print('\n'.join(out))

solve()
```
