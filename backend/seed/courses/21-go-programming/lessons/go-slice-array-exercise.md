# Slice vs Array Semantics

Arrays and slices look similar in Go but behave very differently. This exercise tests your understanding of how `append` interacts with the backing array and when Go is forced to reallocate memory.

## Arrays are value types

In Go, arrays are **value types**. Assigning an array to a new variable copies every element. Passing an array to a function copies it too.

```go
a := [3]int{1, 2, 3}
b := a        // b is a full copy
b[0] = 99
fmt.Println(a[0]) // still 1 — a is unchanged
```

This is different from most languages where arrays are references.

## Slices are reference types

A slice is a three-word header: **pointer to backing array, length, capacity**. Assigning a slice copies the header, not the data.

```go
xs := []int{1, 2, 3}
ys := xs        // ys and xs share the same backing array
ys[0] = 99
fmt.Println(xs[0]) // 99 — both see the change!
```

## How append works

`append` adds elements to a slice. It uses the available capacity first:

```go
xs := make([]int, 3, 6)   // len=3, cap=6
xs = append(xs, 7)         // len=4, cap=6 — no reallocation
```

When the length would exceed the capacity, Go allocates a **new**, larger backing array and copies the elements over. The old backing array is discarded.

```go
xs := make([]int, 4, 4)   // len=4, cap=4 — full
xs = append(xs, 9)         // reallocation: new cap = 8 (roughly 2x)
```

The exact growth factor is implementation-defined. For this exercise, the rule is `new_cap = 2 * old_cap`.

## Why this matters

Slices that share a backing array can surprise you:

```go
a := []int{1, 2, 3, 4}
b := a[:2]          // shares backing array with a
b = append(b, 99)   // len(b)=3 but still within a's cap
fmt.Println(a)      // [1 2 99 4] — a[2] was clobbered!
```

Once `b` triggers a reallocation, mutations no longer affect `a`. This invisible coupling is a common source of bugs.

## Key points

- **Arrays**: fixed size, value semantics, rarely used directly
- **Slices**: dynamic, reference semantics (share backing array), always use the return of `append`
- **Reallocation**: triggered when `len == cap` and you append; produces a new independent array

## Further reading

- *A Tour of Go* — [https://go.dev/tour/](https://go.dev/tour/) — the "More types" section covers slice internals with interactive examples
- *Go 101* — [https://go101.org/article/101.html](https://go101.org/article/101.html) — deep dive on slice value parts and memory layout
- *Go by Example* — [https://gobyexample.com/](https://gobyexample.com/) — "Slices" and "Arrays" pages with annotated, runnable code
