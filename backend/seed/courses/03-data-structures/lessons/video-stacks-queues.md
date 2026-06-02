# Video: Stacks & Queues — LIFO, FIFO, and Deque

This video explains the stack (LIFO) and queue (FIFO) abstractions, implements both with Python lists and `collections.deque`, and walks through the classic queue-from-two-stacks construction.

**Key takeaways:**
- A stack is the right tool for problems involving matching, undo/redo, and recursive call simulation.
- Python's `collections.deque` gives O(1) append and popleft — never use a plain list for a queue (O(n) `pop(0)`).
- Building a queue from two stacks shows how amortised analysis applies to multi-operation sequences, not just single operations.

**Approximate timestamps:**
- 0:00 — Stack operations: push, pop, peek, and balanced-parentheses demo
- 12:00 — Queue operations with `deque` and the circular buffer idea
- 22:00 — Queue from two stacks: code + amortised cost proof
- 30:00 — Monotonic stack pattern for "next greater element" problems
