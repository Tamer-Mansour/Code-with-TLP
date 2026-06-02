# Temporal and Spatial Locality

The memory hierarchy would be useless without one crucial insight: programs are not random in their memory access patterns. They exhibit **locality of reference** — a strong tendency to reuse the same data and to access nearby data. This principle is why a small cache can dramatically reduce average memory access time for real workloads.

## Temporal Locality

**Temporal locality** means that if a memory location is accessed now, it is likely to be accessed again soon.

Classic examples:
- A loop counter (`i++`) is read and written on every iteration.
- A frequently called function's code is fetched repeatedly.
- A configuration flag checked inside a hot loop.

```c
int sum = 0;
for (int i = 0; i < N; i++) {
    sum += arr[i];   // 'sum' exhibits strong temporal locality
}
```

Here `sum` is accessed on every iteration. Once loaded into a register (or L1 cache), the hardware or compiler keeps it there for the duration of the loop.

## Spatial Locality

**Spatial locality** means that if a memory location is accessed, nearby locations are likely to be accessed soon.

Classic examples:
- Iterating through an array element-by-element.
- Executing sequential instructions (instruction fetch has perfect spatial locality).
- Accessing fields of a struct that is laid out contiguously in memory.

```c
// Good spatial locality — sequential access
for (int i = 0; i < N; i++) {
    total += arr[i];   // arr[0], arr[1], arr[2], ... are contiguous
}

// Poor spatial locality — strided / pointer-chasing access
for (Node* p = head; p != NULL; p = p->next) {
    total += p->value;   // each node may be scattered in memory
}
```

Cache hardware exploits spatial locality by fetching an entire **cache line** (typically 64 bytes) on every miss, even if only one byte was requested. If the program then accesses adjacent bytes (which is likely given spatial locality), they are already in the cache.

## The Working Set

The **working set** at time `t` is the set of distinct memory locations referenced in the window `[t - T, t]`. If the working set fits in a cache level, most accesses will hit that level.

- Working set fits in L1: excellent performance
- Working set fits in L3 but not L1/L2: moderate performance
- Working set exceeds all cache: frequent DRAM misses — performance suffers

## Why Cache Line Size Matters

A cache line is fetched as an atomic unit. A 64-byte cache line holds 16 × 32-bit integers or 8 × 64-bit doubles.

```
Cache line: [ int[0] | int[1] | int[2] | ... | int[15] ]
```

If a program accesses `int[0]`, all 16 integers enter the cache. The next 15 accesses are free (hits). This is spatial locality exploitation at the hardware level.

Accessing a column in a 2D row-major array destroys this benefit:

```c
// Accessing column 0 of a 1000×1000 int matrix
for (int i = 0; i < 1000; i++) {
    total += matrix[i][0];   // row i is 4000 bytes apart — skips 15 of every 16 loaded ints
}
```

Each access loads a new cache line but uses only one of its 16 integers before the next iteration, which lands in a completely different cache line.

## Measuring Locality in Practice

- **Hit rate**: fraction of accesses served from a given cache level. Healthy L1 hit rates are >90%.
- **Miss rate**: 1 - hit rate. Even a 5% miss rate can dominate execution time if the miss penalty is 200+ cycles.
- **Reuse distance**: the number of distinct cache lines accessed between two successive references to the same line. Short reuse distance = good temporal locality.

## Common Pitfalls

- **Linked list traversal**: pointer-chasing has poor spatial and temporal locality because nodes are scattered in the heap.
- **Hash table random probing**: probes land at pseudorandom addresses — effectively killing spatial locality.
- **Large stride array access**: accessing every Nth element where N × element_size > cache line size wastes every fetched line.

## Worked Example: Matrix Multiplication

```c
// Version A: poor locality (j, k inner loops swap kills C's reuse)
for (int i = 0; i < N; i++)
  for (int k = 0; k < N; k++)
    for (int j = 0; j < N; j++)
      C[i][j] += A[i][k] * B[k][j];  // B[k][j] strides columns

// Version B: loop-reordered for locality (i,k,j order)
for (int i = 0; i < N; i++)
  for (int k = 0; k < N; k++)
    for (int j = 0; j < N; j++)      // B[k][j] now sequential
      C[i][j] += A[i][k] * B[k][j];
```

Both produce the same result, but the i-k-j ordering can be 2–5× faster on real hardware because it accesses B row-by-row instead of column-by-column.

> **Interview answer:** Temporal locality means recently accessed data will be reused soon; spatial locality means nearby data will be accessed soon. Caches exploit both — temporal by retaining recently used lines, spatial by fetching a full 64-byte line on each miss.
