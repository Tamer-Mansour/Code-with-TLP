# Recursion and Problem Solving

**Recursion** is when a function calls itself as part of its own definition. It sounds circular, but it works because each call moves closer to a simple base case that does not recurse further.

## The Two Parts of Every Recursive Function

1. **Base case** — a condition where the function returns directly without calling itself. This stops the recursion.
2. **Recursive case** — the function calls itself with a *smaller* or *simpler* version of the problem.

```python
def factorial(n):
    # Base case: 0! = 1 by definition
    if n == 0:
        return 1
    # Recursive case: n! = n × (n-1)!
    return n * factorial(n - 1)

print(factorial(5))   # 120
```

## Tracing the Call Stack

When `factorial(4)` runs, Python keeps a **call stack** — a record of all active function calls:

```
factorial(4)
  └── 4 * factorial(3)
            └── 3 * factorial(2)
                      └── 2 * factorial(1)
                                └── 1 * factorial(0)
                                          └── returns 1
                                ← returns 1 * 1 = 1
                      ← returns 2 * 1 = 2
            ← returns 3 * 2 = 6
  ← returns 4 * 6 = 24
```

Each call pauses, waiting for the inner call to return. Once the base case returns `1`, values unwind back up the stack.

## Fibonacci Numbers

The Fibonacci sequence: 0, 1, 1, 2, 3, 5, 8, 13, 21, …

Each number is the sum of the two preceding it. This is a natural recursive definition:

```python
def fib(n):
    if n <= 1:
        return n
    return fib(n - 1) + fib(n - 2)
```

**Warning:** this naive implementation is O(2^n) — it recomputes the same values exponentially. `fib(50)` would take hours. The iterative version is O(n):

```python
def fib_iterative(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a
```

This is a critical lesson: **recursion is not always more efficient than iteration.** Python does not perform tail-call optimisation, so deeply recursive calls also consume stack memory and can raise `RecursionError`.

## Divide and Conquer

The real power of recursion is **divide-and-conquer**: split a hard problem into two (or more) smaller instances of the same problem, solve each recursively, and combine results.

Merge sort is the canonical example:

```
MergeSort([38, 27, 43, 3])
├── MergeSort([38, 27]) → [27, 38]
├── MergeSort([43, 3])  → [3, 43]
└── Merge([27, 38], [3, 43]) → [3, 27, 38, 43]
```

Each level halves the problem size, giving O(log n) levels. Merging costs O(n) at each level — total: **O(n log n)**.

## Recursive vs Iterative: When to Use Which

| Criterion | Recursive | Iterative |
|-----------|-----------|-----------|
| Clarity | Often clearer for tree/graph problems | Often clearer for simple loops |
| Memory | Uses call-stack frames (O(depth)) | O(1) extra space for simple loops |
| Performance | Risk of O(2^n) without memoisation | Typically O(n) |
| Python limit | Default recursion limit ~1000 calls | No limit |

Use recursion when the problem has a naturally recursive structure (trees, grammars, divide-and-conquer). Use iteration when the problem is a straightforward sequence.

## Common Misconceptions

> "Recursion is always more elegant and efficient."

Elegant: sometimes yes. Efficient: not always. Naive recursive Fibonacci is O(2^n); the iterative version is O(n). Always reason about complexity before choosing recursion.

> "You need a loop to repeat something."

Recursion achieves repetition through self-calls. Both loops and recursion are Turing-complete — any loop can be rewritten as recursion and vice versa.

## Further Reading

- **Think Python (Ch. 5)** — https://greenteapress.com/wp/think-python-2e/
- **MIT 6.0001 Lecture 6: Recursion and Dictionaries** — https://ocw.mit.edu/courses/6-0001-introduction-to-computer-science-and-programming-in-python-fall-2016/
- **Introduction to Computer Science (OpenStax, Ch. on Algorithms)** — https://openstax.org/books/introduction-computer-science/pages/1-introduction

## Key Takeaways

- Every recursive function needs a **base case** (stops recursion) and a **recursive case** (reduces the problem).
- Python maintains a **call stack**; each recursive call adds a frame. Too many calls cause `RecursionError`.
- Naive recursion can be exponentially slow — memoisation or iteration may be necessary.
- **Divide and conquer** — split, recurse, combine — is the engine behind merge sort and binary search.
