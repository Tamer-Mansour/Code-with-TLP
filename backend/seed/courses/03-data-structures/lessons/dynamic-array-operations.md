# Dynamic Array Operations

Now that we understand memory layout and amortised growth, let's examine every core operation in depth — with step-by-step walkthroughs, implementation code, and the subtle bugs that trip up beginners.

## Insertion

### Appending to the End — O(1) Amortised

This is the "cheap" path: place the new element at index `size`, increment `size`. If `size == capacity`, trigger a resize first (O(n) work, but amortised O(1) as shown in the previous lesson).

```python
# Python list append — using the built-in
arr = [1, 2, 3]
arr.append(4)   # O(1) amortised — arr is now [1, 2, 3, 4]
```

### Inserting in the Middle at Index k — O(n)

Every element from `k` to `size-1` must shift one position to the right to open a gap:

```
Before:  [10, 20, 30, 40, 50]   insert 99 at index 2
         ← shift right →
After:   [10, 20, 99, 30, 40, 50]
```

Step-by-step implementation (without using the built-in `insert`):

```python
def insert_at(arr: list, index: int, value) -> None:
    """Insert value at index, shifting elements right. O(n) time."""
    arr.append(None)                         # grow by one slot
    for i in range(len(arr) - 1, index, -1):
        arr[i] = arr[i - 1]                  # shift right
    arr[index] = value

a = [10, 20, 30, 40, 50]
insert_at(a, 2, 99)
print(a)  # [10, 20, 99, 30, 40, 50]
```

The worst case is inserting at index 0 (front): all n elements shift — O(n). The best case is inserting at the last position — O(1) (no shift needed, just append).

Python's built-in `list.insert(k, v)` is O(n - k): inserting at the front of a million-element list shifts a million pointers.

## Deletion

### Removing from the End — O(1)

```python
arr = [1, 2, 3, 4]
last = arr.pop()    # removes 4, returns 4 — O(1)
```

### Removing from the Middle at Index k — O(n)

Elements from `k+1` to the end must shift left to close the gap:

```
Before:  [10, 20, 30, 40, 50]   delete index 2 (value 30)
         ← shift left ←
After:   [10, 20, 40, 50]
```

```python
def delete_at(arr: list, index: int) -> None:
    """Delete element at index, shifting remaining elements left. O(n) time."""
    for i in range(index, len(arr) - 1):
        arr[i] = arr[i + 1]    # shift left
    arr.pop()                   # remove the now-duplicate last slot

a = [10, 20, 30, 40, 50]
delete_at(a, 2)
print(a)  # [10, 20, 40, 50]
```

**Common bug:** `arr.pop(0)` works but is O(n) because Python shifts all elements left in C. For frequent front-deletions use `collections.deque.popleft()` which is O(1).

## Two-Pointer Technique

Two pointers at different positions or moving at different speeds solve many array problems in O(n) instead of O(n²).

### Reverse an Array In-Place — O(n)

```python
def reverse(arr: list) -> None:
    left, right = 0, len(arr) - 1
    while left < right:
        arr[left], arr[right] = arr[right], arr[left]
        left += 1
        right -= 1

a = [1, 2, 3, 4, 5]
reverse(a)
print(a)  # [5, 4, 3, 2, 1]
```

### Check Palindrome — O(n)

```python
def is_palindrome(s: str) -> bool:
    left, right = 0, len(s) - 1
    while left < right:
        if s[left] != s[right]:
            return False
        left += 1
        right -= 1
    return True

print(is_palindrome("racecar"))  # True
print(is_palindrome("hello"))    # False
```

### Remove Duplicates from Sorted Array — O(n), O(1) Space

The "fast/slow pointer" pattern: `slow` tracks the write position, `fast` scans ahead.

```python
def remove_duplicates(arr: list) -> int:
    if not arr:
        return 0
    slow = 0
    for fast in range(1, len(arr)):
        if arr[fast] != arr[slow]:
            slow += 1
            arr[slow] = arr[fast]
    return slow + 1   # new length

a = [1, 1, 2, 3, 3, 3, 4]
k = remove_duplicates(a)
print(a[:k])  # [1, 2, 3, 4]
```

## Sliding Window Technique

Use a sliding window for contiguous subarray problems. Move the right boundary forward one step at a time; shrink the left boundary when a constraint is violated.

### Fixed-Size Window: Maximum Sum Subarray of Size k — O(n)

```python
def max_sum_subarray(arr: list, k: int) -> int:
    """O(n) — slide a window of size k across the array."""
    window_sum = sum(arr[:k])
    best = window_sum
    for i in range(k, len(arr)):
        window_sum += arr[i] - arr[i - k]   # add right, remove left
        best = max(best, window_sum)
    return best

print(max_sum_subarray([2, 1, 5, 1, 3, 2], 3))  # 9  (5+1+3)
```

### Variable-Size Window: Smallest Subarray with Sum ≥ Target — O(n)

```python
def min_len_subarray(arr: list, target: int) -> int:
    left = 0
    current_sum = 0
    min_len = float('inf')
    for right in range(len(arr)):
        current_sum += arr[right]
        while current_sum >= target:
            min_len = min(min_len, right - left + 1)
            current_sum -= arr[left]
            left += 1
    return min_len if min_len != float('inf') else 0

print(min_len_subarray([2, 3, 1, 2, 4, 3], 7))  # 2  (subarray [4,3])
```

## Prefix Sums

Precompute cumulative sums to answer **range-sum queries in O(1)** after O(n) setup.

```python
def build_prefix(arr: list) -> list:
    """prefix[i] = sum of arr[0..i-1]; prefix[0] = 0."""
    prefix = [0] * (len(arr) + 1)
    for i, v in enumerate(arr):
        prefix[i + 1] = prefix[i] + v
    return prefix

def range_sum(prefix: list, l: int, r: int) -> int:
    """Sum of arr[l..r] inclusive — O(1)."""
    return prefix[r + 1] - prefix[l]

arr = [3, 1, 4, 1, 5, 9, 2, 6]
pre = build_prefix(arr)
print(range_sum(pre, 2, 5))  # arr[2]+arr[3]+arr[4]+arr[5] = 4+1+5+9 = 19
```

**Why it works:** `prefix[r+1] = arr[0]+…+arr[r]` and `prefix[l] = arr[0]+…+arr[l-1]`, so their difference cancels the prefix and leaves `arr[l]+…+arr[r]`.

**Difference array variant:** For batch range-update problems ("add `v` to every element in `[l, r]`"), a difference array lets you apply updates in O(1) and reconstruct in O(n).

```python
def apply_updates(arr: list, updates: list) -> list:
    """Each update: (l, r, val) — add val to arr[l..r]."""
    n = len(arr)
    diff = [0] * (n + 1)
    for l, r, val in updates:
        diff[l] += val
        diff[r + 1] -= val
    running = 0
    result = arr[:]
    for i in range(n):
        running += diff[i]
        result[i] += running
    return result
```

## Binary Search on Arrays — O(log n)

Binary search finds a target in a **sorted** array by halving the search space each step.

```python
def binary_search(arr: list, target: int) -> int:
    """Returns the index of target, or -1 if not found."""
    lo, hi = 0, len(arr) - 1
    while lo <= hi:
        mid = lo + (hi - lo) // 2   # avoids integer overflow vs. (lo+hi)//2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1

print(binary_search([1, 3, 5, 7, 9, 11], 7))  # 3
print(binary_search([1, 3, 5, 7, 9, 11], 4))  # -1
```

**Common bug:** `mid = (lo + hi) // 2` can overflow in C/Java when `lo + hi > INT_MAX`. In Python integers are arbitrary precision so it is safe, but `lo + (hi - lo) // 2` is the canonical form.

## Complexity Reference Table

| Operation               | Time     | Space | Notes                              |
|-------------------------|----------|-------|------------------------------------|
| Append (end)            | O(1)*    | O(1)* | amortised; O(n) worst on resize    |
| Insert at index k       | O(n−k)   | O(1)  | shifts n−k elements right          |
| Delete at index k       | O(n−k)   | O(1)  | shifts n−k elements left           |
| Pop from end            | O(1)     | O(1)  |                                    |
| Access `arr[k]`         | O(1)     | O(1)  | direct address calculation         |
| Linear search           | O(n)     | O(1)  | unsorted array                     |
| Binary search           | O(log n) | O(1)  | sorted array only                  |
| Prefix sum build        | O(n)     | O(n)  | one-time setup                     |
| Prefix sum range query  | O(1)     | O(1)  | after O(n) build                   |
| Reverse in-place        | O(n)     | O(1)  | two-pointer swap                   |
| Sliding window          | O(n)     | O(1)  | one pass, two pointers             |

## Key Takeaways

- Dynamic arrays are the default workhorse: fast random access, cache-friendly layout, amortised O(1) append.
- Every middle-insert and middle-delete is O(n) because of the required shift. Front-insertions on a large list are expensive — use `deque` if you need O(1) at both ends.
- **Prefix sums** turn range-sum queries from O(n) to O(1). **Two pointers** reduce many O(n²) brute-force problems to O(n). **Sliding window** handles fixed and variable-size contiguous subarray problems efficiently.
- When you see "find a contiguous subarray that satisfies X", think sliding window or prefix sums first.
