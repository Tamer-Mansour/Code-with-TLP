# Binary Search

Binary search is the classic example of how a smarter algorithm beats brute force. Linear search checks every element — O(n). Binary search on a sorted array eliminates half the remaining elements with each comparison — O(log n). For one million elements, binary search needs at most 20 comparisons; linear search needs up to one million.

## What You Will Practice

- Implementing binary search from scratch
- Maintaining `low`, `high`, and `mid` pointers
- Understanding why O(log n) is dramatically faster than O(n)

## How Binary Search Works

```
sorted list: [2, 5, 8, 12, 16, 23, 38]   target: 23
indices:       0  1  2   3   4   5   6

Step 1: low=0, high=6, mid=3 → list[3]=12 < 23 → search right half
Step 2: low=4, high=6, mid=5 → list[5]=23 == 23 → FOUND at index 5
```

## Template

```python
n = int(input())
nums = list(map(int, input().split()))
target = int(input())

lo, hi = 0, n - 1
result = -1
while lo <= hi:
    mid = (lo + hi) // 2
    if nums[mid] == target:
        result = mid
        break
    elif nums[mid] < target:
        lo = mid + 1      # target must be in right half
    else:
        hi = mid - 1      # target must be in left half

print(result)
```

## The Key Invariant

At every iteration, if the target exists in the list, it must be within `nums[lo..hi]`. The loop maintains this invariant. When `lo > hi`, the search space is empty and the target is not present.
