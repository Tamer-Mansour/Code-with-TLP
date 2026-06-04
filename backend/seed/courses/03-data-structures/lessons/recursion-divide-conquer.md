# Recursion and Divide-and-Conquer

Recursion is a function calling itself with a smaller version of the same problem until a trivial case is reached. It is not just a coding trick — it is the natural language for describing algorithms that operate on hierarchically structured or self-similar data (trees, fractals, sorted subarrays).

## Anatomy of a Recursive Function

Every correct recursive function has two parts:

1. **Base case**: The simplest input that can be answered directly without recursion. Omitting or miscoding the base case causes infinite recursion and a stack overflow.
2. **Recursive case**: Break the problem into one or more strictly smaller sub-problems, solve them recursively, and combine the results.

```python
def factorial(n: int) -> int:
    # Base case
    if n == 0:
        return 1
    # Recursive case: n! = n * (n-1)!
    return n * factorial(n - 1)

def fibonacci(n: int) -> int:
    if n <= 1:          # base cases: fib(0)=0, fib(1)=1
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)  # two sub-problems
```

## Recursion vs. Iteration

Any recursive algorithm can be rewritten iteratively (using an explicit stack), and vice versa. The trade-offs are:

| Aspect | Recursion | Iteration |
|--------|-----------|-----------|
| Readability | Often cleaner for tree/graph problems | More explicit for simple loops |
| Stack usage | O(depth) call stack — may overflow | O(1) or explicit stack, no overflow |
| Performance | Function call overhead | Generally faster |
| Debug | Stack traces are informative | Easier to step through |

Python's default recursion limit is 1000 frames. For deep recursion set `sys.setrecursionlimit(n)` or convert to an iterative approach.

## Recurrence Relations

The runtime of a recursive algorithm is expressed as a **recurrence relation**. For example:

- Merge sort: T(n) = 2T(n/2) + O(n)
- Binary search: T(n) = T(n/2) + O(1)
- Factorial: T(n) = T(n−1) + O(1)

## The Master Theorem

For recurrences of the form T(n) = a·T(n/b) + f(n) where a ≥ 1, b > 1, and f(n) is the cost of the "combine" step:

Let c = log_b(a) (the critical exponent).

| Condition | Result | Example |
|-----------|--------|---------|
| f(n) = O(n^(c−ε)) for some ε > 0 | T(n) = Θ(n^c) | Binary tree height |
| f(n) = Θ(n^c · log^k(n)) | T(n) = Θ(n^c · log^(k+1)(n)) | Merge sort: k=0, T=Θ(n log n) |
| f(n) = Ω(n^(c+ε)) and regularity | T(n) = Θ(f(n)) | — |

**Merge sort:** a=2, b=2, f(n)=O(n). c = log₂(2) = 1. f(n) = Θ(n^1) → case 2 with k=0 → T(n) = Θ(n log n).

**Binary search:** a=1, b=2, f(n)=O(1). c = log₂(1) = 0. f(n) = Θ(n^0) → case 2 → T(n) = Θ(log n).

## Divide-and-Conquer Pattern

Divide-and-conquer algorithms follow three steps:

1. **Divide**: Split the problem into sub-problems (usually of equal size).
2. **Conquer**: Solve each sub-problem recursively.
3. **Combine**: Merge the sub-problem solutions into the final answer.

The efficiency gain comes from the fact that dividing halves the problem size at each level, giving O(log n) levels — and if the combine step is O(n) or less, total work is O(n log n).

### Example: Count Inversions

An inversion in array A is a pair (i, j) with i < j and A[i] > A[j]. Naive O(n²) counts all pairs. Divide-and-conquer counts inversions in O(n log n) by augmenting merge sort: during the merge step, whenever a right-half element is placed before a left-half element, count the remaining left elements as inversions.

```python
def count_inversions(arr):
    if len(arr) <= 1:
        return arr, 0
    mid = len(arr) // 2
    left, left_inv = count_inversions(arr[:mid])
    right, right_inv = count_inversions(arr[mid:])
    merged, split_inv = merge_count(left, right)
    return merged, left_inv + right_inv + split_inv

def merge_count(left, right):
    result = []
    inversions = 0
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i]); i += 1
        else:
            result.append(right[j]); j += 1
            inversions += len(left) - i   # all remaining left elements form inversions
    result.extend(left[i:])
    result.extend(right[j:])
    return result, inversions

_, inv = count_inversions([3, 1, 2, 5, 4])
print(inv)   # 3  (pairs: (3,1), (3,2), (5,4))
```

## Memoization — Caching Recursive Results

The naive `fibonacci(n)` is O(2ⁿ) because it recomputes the same sub-problems exponentially. **Memoization** stores results so each sub-problem is solved only once.

```python
from functools import lru_cache

@lru_cache(maxsize=None)
def fibonacci(n: int) -> int:
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

print(fibonacci(50))   # 12586269025 — instant vs. minutes without cache
```

Memoization converts exponential recursion to O(n) time and O(n) space. This is the foundation of **dynamic programming**: identify overlapping sub-problems and cache results.

## Tail Recursion

A recursive call is **tail-recursive** if it is the very last operation in the function — no work is done after the recursive call returns. Tail-recursive functions can theoretically be optimised by the compiler into iteration (tail-call optimisation, TCO).

```python
# Standard recursion — NOT tail-recursive (multiplication after call)
def factorial(n):
    if n == 0: return 1
    return n * factorial(n - 1)   # must wait for result to multiply

# Tail-recursive version — accumulator carries the state
def factorial_tail(n, acc=1):
    if n == 0: return acc
    return factorial_tail(n - 1, n * acc)   # last operation is the call
```

Python does **not** perform TCO, so tail-recursive Python code still uses O(n) stack space. In languages like Scheme, Haskell, or Scala, TCO makes tail recursion as efficient as a loop.

## Common Recursion Patterns

```python
# Power (fast exponentiation — O(log n))
def power(base, exp):
    if exp == 0: return 1
    half = power(base, exp // 2)
    if exp % 2 == 0:
        return half * half
    return half * half * base

# Flatten nested list (arbitrary depth)
def flatten(lst):
    result = []
    for item in lst:
        if isinstance(item, list):
            result.extend(flatten(item))
        else:
            result.append(item)
    return result

print(flatten([1, [2, [3, 4], 5], 6]))   # [1, 2, 3, 4, 5, 6]
```

## Further Reading

- *Open Data Structures: An Introduction* by Pat Morin — https://opendatastructures.org/ — rigorous treatment of divide-and-conquer and recurrence analysis.
- *Introduction to Algorithms* (MIT 6.006 OCW) — https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-spring-2020/ — Master Theorem proof and divide-and-conquer case studies.
- *Problem Solving with Algorithms and Data Structures using Python* (Miller & Ranum) — https://runestone.academy/ns/books/published/pythonds/index.html — interactive Python implementations with visualisations.
