# Stacks & Queues

Stacks and queues are **linear abstract data types** that differ only in the order elements leave. Both are used to manage sequences of items where the arrival order matters — but which end you remove from changes everything.

## Stack — LIFO (Last In, First Out)

Think of a stack of dinner plates: the plate you just placed on top is the first one you take off. You can only interact with the top.

```
Push 1: [1]
Push 2: [1, 2]
Push 3: [1, 2, 3]
Pop  → 3      remaining: [1, 2]
Peek → 2      remaining: [1, 2]
Pop  → 2      remaining: [1]
Pop  → 1      remaining: []
```

### Core Operations and Complexity

| Operation    | Description                  | Time | Notes                   |
|--------------|------------------------------|------|-------------------------|
| `push(x)`    | Add x to top                 | O(1) | amortised for list-backed|
| `pop()`      | Remove and return top element| O(1) |                         |
| `peek()`     | Return top without removing  | O(1) |                         |
| `is_empty()` | True if no elements          | O(1) |                         |
| `size()`     | Number of elements           | O(1) |                         |

### Python Implementation Using list

Python's `list` is a perfectly efficient stack — `append` is push, `pop()` (no argument) is pop:

```python
stack = []
stack.append(1)        # push
stack.append(2)
stack.append(3)
print(stack[-1])       # peek → 3 (O(1))
print(stack.pop())     # pop  → 3
print(stack.pop())     # pop  → 2
print(len(stack))      # size → 1
```

### Classic Stack Applications

**1. Balanced parentheses / bracket matching**

Push every opening bracket onto the stack. On each closing bracket, check the top: if it's the matching opener, pop it; otherwise the expression is invalid.

```python
def is_balanced(s: str) -> bool:
    match = {')': '(', '}': '{', ']': '['}
    stack = []
    for ch in s:
        if ch in '({[':
            stack.append(ch)
        elif ch in ')}]':
            if not stack or stack[-1] != match[ch]:
                return False
            stack.pop()
    return len(stack) == 0
```

**2. Evaluating postfix (Reverse Polish Notation) expressions**

`3 4 + 2 *` = (3+4)*2 = 14. Scan left-to-right; push numbers, apply operators to the top two operands:

```python
def eval_rpn(tokens: list) -> int:
    stack = []
    ops = {'+': lambda a,b: a+b, '-': lambda a,b: a-b,
           '*': lambda a,b: a*b, '/': lambda a,b: int(a/b)}
    for t in tokens:
        if t in ops:
            b, a = stack.pop(), stack.pop()
            stack.append(ops[t](a, b))
        else:
            stack.append(int(t))
    return stack[0]

print(eval_rpn(["3","4","+","2","*"]))  # 14
```

**3. Function call stack (conceptual)**

Every function call pushes a **stack frame** (local variables, return address, saved registers) onto the call stack. `return` pops the frame. Stack overflow occurs when recursion is too deep — the call stack runs out of space.

**4. DFS with explicit stack**

Replace the recursion stack with a manual `list`-stack for iterative depth-first search (avoids Python's recursion limit of ~1000):

```python
def dfs_iterative(graph: dict, start: int) -> list:
    visited = set()
    stack = [start]
    order = []
    while stack:
        node = stack.pop()
        if node not in visited:
            visited.add(node)
            order.append(node)
            for nb in reversed(graph[node]):   # reversed to match recursive order
                if nb not in visited:
                    stack.append(nb)
    return order
```

---

## Queue — FIFO (First In, First Out)

Think of a supermarket checkout line: the first customer to arrive is the first to be served. New arrivals join the back; service happens at the front.

```
Enqueue 1: [1]
Enqueue 2: [1, 2]
Enqueue 3: [1, 2, 3]
Dequeue → 1    remaining: [2, 3]
Front   → 2    remaining: [2, 3]
```

### Core Operations and Complexity

| Operation    | Description                   | Time | Notes                        |
|--------------|-------------------------------|------|------------------------------|
| `enqueue(x)` | Add x to the back             | O(1) |                              |
| `dequeue()`  | Remove and return the front   | O(1) | O(n) for list-backed!        |
| `front()`    | Return front without removing | O(1) |                              |
| `is_empty()` | True if no elements           | O(1) |                              |

**Never use `list.pop(0)` for a queue** — it shifts all n elements left, giving O(n) per dequeue. Use `collections.deque.popleft()` which is O(1):

```python
from collections import deque

q = deque()
q.append(1)          # enqueue at back
q.append(2)
q.append(3)
print(q[0])          # front → 1 (O(1))
print(q.popleft())   # dequeue → 1
print(q.popleft())   # dequeue → 2
```

### Classic Queue Applications

- **BFS** — explore the graph layer by layer. Nodes discovered at depth d are processed before nodes at depth d+1.
- **OS ready queue** — processes waiting to be scheduled by the CPU.
- **Rate limiting** — maintain a sliding window of recent request timestamps.
- **Printer spooler / message buffer** — jobs processed in arrival order.

---

## Deque (Double-Ended Queue)

A **deque** (double-ended queue) supports O(1) push and pop at **both** ends, making it the most general of the three. Python's `collections.deque` is implemented as a doubly-linked list of fixed-size blocks (each block holds ~64 objects), giving O(1) operations at both ends with good cache locality.

```python
from collections import deque

d = deque()
d.appendleft(0)    # push front  — O(1)
d.append(5)        # push back   — O(1)
print(d.popleft()) # pop front   → 0  — O(1)
print(d.pop())     # pop back    → 5  — O(1)

# Bounded deque: evicts oldest element automatically
recent = deque(maxlen=3)
for i in range(6):
    recent.append(i)
print(list(recent))  # [3, 4, 5]
```

**Monotonic deque** trick: maintain a deque in decreasing order to find the sliding-window maximum in O(n):

```python
def sliding_window_max(arr: list, k: int) -> list:
    """O(n) — maximum of each window of size k."""
    d = deque()  # stores indices; front = index of current max
    result = []
    for i, val in enumerate(arr):
        while d and arr[d[-1]] <= val:
            d.pop()           # remove smaller values from back
        d.append(i)
        if d[0] == i - k:     # front index is out of window
            d.popleft()
        if i >= k - 1:
            result.append(arr[d[0]])
    return result

print(sliding_window_max([1, 3, -1, -3, 5, 3, 6, 7], 3))
# [3, 3, 5, 5, 6, 7]
```

---

## Circular Buffer (Ring Buffer)

A circular buffer implements a **fixed-capacity queue** using an array with two indices (`head` and `tail`) that wrap around modulo `capacity`. No element shifting is needed — perfect for OS I/O buffers, audio processing, and network packet queues.

```
capacity=5, head=0, tail=0 (empty: head==tail)

Enqueue 10:  arr[0]=10, tail=(0+1)%5=1   [10, _, _, _, _]
Enqueue 20:  arr[1]=20, tail=2           [10, 20, _, _, _]
Dequeue:     return arr[0]=10, head=1    [__, 20, _, _, _]
Enqueue 30:  arr[2]=30, tail=3           [__, 20, 30, _, _]
Enqueue 40:  arr[3]=40, tail=4           [__, 20, 30, 40, _]
Enqueue 50:  arr[4]=50, tail=0 (wrap)    [__, 20, 30, 40, 50]
```

```python
class CircularBuffer:
    def __init__(self, capacity: int):
        self.buf = [None] * capacity
        self.capacity = capacity
        self.head = 0    # next dequeue position
        self.tail = 0    # next enqueue position
        self.size = 0

    def enqueue(self, val) -> None:
        if self.size == self.capacity:
            raise OverflowError("Buffer full")
        self.buf[self.tail] = val
        self.tail = (self.tail + 1) % self.capacity
        self.size += 1

    def dequeue(self):
        if self.size == 0:
            raise IndexError("Buffer empty")
        val = self.buf[self.head]
        self.head = (self.head + 1) % self.capacity
        self.size -= 1
        return val
```

---

## Implementing a Queue with Two Stacks

A classic interview question: implement a queue (FIFO) using only two stacks (LIFO). The key insight is that reversing a stack (by pushing everything onto a second stack) yields FIFO order.

```python
class QueueFromTwoStacks:
    def __init__(self):
        self.inbox = []   # enqueue here
        self.outbox = []  # dequeue from here

    def enqueue(self, val) -> None:
        self.inbox.append(val)   # O(1) always

    def dequeue(self):
        if not self.outbox:
            # Transfer inbox → outbox, reversing order
            while self.inbox:
                self.outbox.append(self.inbox.pop())
        if not self.outbox:
            raise IndexError("Queue empty")
        return self.outbox.pop()   # O(1) amortised
```

**Why O(1) amortised?** Each element crosses the inbox→outbox boundary at most once. The total work over n operations is O(n), so amortised O(1) per operation.

---

## Complexity Summary

| Structure                  | Push/Enqueue | Pop/Dequeue | Peek | Space           |
|----------------------------|-------------|-------------|------|-----------------|
| Stack (`list`)             | O(1)*       | O(1)        | O(1) | O(n)            |
| Queue (`deque`)            | O(1)        | O(1)        | O(1) | O(n)            |
| Deque (`collections.deque`)| O(1) both ends | O(1) both ends | O(1) | O(n)      |
| Circular buffer (array)    | O(1)        | O(1)        | O(1) | O(capacity)     |
| Queue from two stacks      | O(1)        | O(1)*       | O(1)*| O(n)            |

*amortised

## Key Takeaways

- Use a **stack** (Python `list`) whenever you need LIFO order: bracket matching, DFS, undo/redo, expression evaluation.
- Use a **queue** (`collections.deque`) for BFS and any FIFO processing pipeline. Never use `list.pop(0)` — it is O(n).
- A **deque** is the most general: O(1) at both ends. Use it for sliding-window algorithms and bounded history buffers (`maxlen=k`).
- The **two-stacks** trick is a favourite interview question: it shows that data structures can be composed to change their behavioural contract.
