# Exercise: Compute Pointer Offsets and Array Strides

Pointer arithmetic is only meaningful once you understand that the step size depends on the pointed-to type. In this exercise you will compute the byte offsets that result from pointer addition for different element types, and calculate the strides needed to traverse rows of a 2D array.

## What You Will Implement

Write a program that reads a base address, an element type size (in bytes), and a series of pointer operations, then prints the resulting byte address after each operation.

### Your Task

Given:
- A **base address** (integer, representing a memory address in bytes)
- An **element size** in bytes (this is `sizeof` the pointed-to type)
- A list of **operations**, each either `+N` or `-N` (advance or retreat N elements)

For each operation, compute the new address:

```
new_address = current_address + (N × element_size)
```

Print the resulting address after every operation on its own line.

## Skills Practiced

- Understanding that pointer arithmetic scales by element size, not by bytes
- Simulating what the CPU and compiler compute when you write `p + n`
- Working with signed pointer differences (`-N` means stepping backwards)

## Input Format

```
base_address element_size
op_count
op_1
op_2
...
```

- `base_address`: integer in range [0, 10^9]
- `element_size`: integer in {1, 2, 4, 8}
- `op_count`: integer in [1, 20]
- Each `op`: an integer N (may be negative); represents adding N elements to the current pointer

## Output Format

Print `op_count` lines. Each line contains the address after applying the cumulative operation.

## Example

**Input:**
```
1000 4
3
1
2
-1
```

**Trace:**
- Start: 1000
- After `+1 element of size 4`: 1000 + 1×4 = 1004
- After `+2 elements of size 4`: 1004 + 2×4 = 1012
- After `-1 element of size 4`: 1012 + (-1)×4 = 1008

**Output:**
```
1004
1012
1008
```

## Constraints

- All resulting addresses will be non-negative integers
- `|N|` ≤ 100 for each step
- No floating-point arithmetic needed
