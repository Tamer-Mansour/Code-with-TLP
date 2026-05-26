# Exercise: Bubble Sort Step-by-Step

Implement the bubble sort algorithm and show its work pass-by-pass.

## What you need to do

Each line of input is a space-separated list of integers. For each list:

1. Run bubble sort (compare adjacent pairs left-to-right; swap if out of order).
2. After each complete pass that made **at least one swap**, print the list's current state as space-separated integers.
3. When no swaps occur in a pass (list is sorted), print `sorted:` followed by the final sorted list.

If the list is already sorted (first pass has zero swaps), just print `sorted:` followed by the list.

## Example

**Input:**
```
5 3 8 1 4
1 2 3
```

**Output:**
```
3 5 1 4 8
3 1 4 5 8
1 3 4 5 8
sorted: 1 3 4 5 8
sorted: 1 2 3
```

## Algorithm reminder

```
FOR i FROM 0 TO n-2:
    swapped = False
    FOR j FROM 0 TO n-2-i:
        IF list[j] > list[j+1]:
            SWAP list[j] and list[j+1]
            swapped = True
    IF swapped:
        print current list
    ELSE:
        print "sorted: " + list
        BREAK
```
