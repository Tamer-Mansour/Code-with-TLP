# Exercise: Stack Operations

A stack is a Last-In-First-Out (LIFO) data structure. This exercise has you build a `Stack` class and drive it from stdin — practising OOP, class design, and command parsing all in one.

## What You Will Practice

- Defining a class with `__init__` and instance methods
- Using a list as the internal storage for a container class
- Encapsulation: hiding `_data` behind a clean public API
- Reading commands from stdin until EOF
- Defensive coding: handling the empty-stack case gracefully

## Class Skeleton

```python
class Stack:
    def __init__(self):
        self._data = []          # underscore = "private by convention"

    def push(self, value):
        self._data.append(value)

    def pop(self):
        if not self._data:
            return 'Empty'
        return self._data.pop()  # list.pop() removes and returns the last element

    def peek(self):
        if not self._data:
            return 'Empty'
        return self._data[-1]    # negative index: last element without removing

    def size(self):
        return len(self._data)
```

## Reading Commands Until EOF

```python
import sys

stack = Stack()
for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    parts = line.split()
    cmd = parts[0]
    if cmd == 'PUSH':
        stack.push(int(parts[1]))
    elif cmd == 'POP':
        print(stack.pop())
    elif cmd == 'PEEK':
        print(stack.peek())
    elif cmd == 'SIZE':
        print(stack.size())
```

## Access Conventions in Python

Python has no `private` keyword. The convention is:
- `_name` — "internal, treat as private" (single underscore)
- `__name` — name-mangled to `_ClassName__name` (double underscore, rarely needed)

For most cases, a single underscore is all you need to signal "don't call this from outside the class."

## Further Reading

OOP fundamentals including encapsulation and class design are covered thoroughly in [*Think Python*, 2nd Edition](https://greenteapress.com/thinkpython2/thinkpython2.pdf) by Allen B. Downey (Chapters 15–18). For interactive exercises with a built-in code runner, see [How to Think Like a Computer Scientist](https://runestone.academy/ns/books/published/thinkcspy/index.html) on Runestone Academy (free).
