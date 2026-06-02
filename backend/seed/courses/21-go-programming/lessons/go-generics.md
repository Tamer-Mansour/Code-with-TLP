# Generics in Go (1.18+)

Go added generics in version 1.18. They let you write functions and types that work over multiple concrete types without sacrificing type safety or resorting to `interface{}`.

## The Problem Generics Solve

Before generics, you either wrote one function per type or used `any` and lost compile-time checking:

```go
// repetitive: one per type
func SumInts(nums []int) int { ... }
func SumFloat64s(nums []float64) float64 { ... }

// unsafe: boxing + manual assertion
func Sum(nums []any) any { ... }
```

## Generic Functions

```go
// T is a type parameter constrained to "numeric" types
func Sum[T int | int64 | float64](nums []T) T {
    var total T
    for _, n := range nums {
        total += n
    }
    return total
}

// Usage — type inferred from arguments
fmt.Println(Sum([]int{1, 2, 3}))          // 6
fmt.Println(Sum([]float64{1.1, 2.2}))     // 3.3000...
```

## Type Constraints

A constraint is an interface that lists which types satisfy it.

```go
// constraints package (golang.org/x/exp or define your own)
type Number interface {
    int | int8 | int16 | int32 | int64 |
        uint | uint8 | uint16 | uint32 | uint64 |
        float32 | float64
}

func Min[T Number](a, b T) T {
    if a < b {
        return a
    }
    return b
}
```

The built-in `comparable` constraint allows `==` and `!=` — useful for maps and sets.

## Generic Types (Data Structures)

```go
type Stack[T any] struct {
    items []T
}

func (s *Stack[T]) Push(v T) {
    s.items = append(s.items, v)
}

func (s *Stack[T]) Pop() (T, bool) {
    var zero T
    if len(s.items) == 0 {
        return zero, false
    }
    n := len(s.items)
    v := s.items[n-1]
    s.items = s.items[:n-1]
    return v, true
}

// Usage
s := &Stack[string]{}
s.Push("hello")
s.Push("world")
v, ok := s.Pop() // "world", true
```

## The `slices` and `maps` Packages (1.21+)

Go 1.21 added `slices` and `maps` packages that use generics internally:

```go
import (
    "cmp"
    "slices"
    "maps"
)

nums := []int{5, 2, 8, 1}
slices.Sort(nums)                     // in-place sort
idx, _ := slices.BinarySearch(nums, 5) // binary search
min := slices.Min(nums)               // 1

m := map[string]int{"a": 1, "b": 2}
keys := slices.Collect(maps.Keys(m))  // collect iterator to slice
```

## When NOT to Use Generics

Generics add complexity. Prefer them when:

- You are writing a reusable **data structure** (Stack, Queue, Set, Tree).
- You have **identical logic** over multiple types (Min, Max, Map, Filter, Reduce).

Avoid generics when a plain `interface` or `any` is simpler, or when the function is only used with one concrete type.

## Practical Example: Map/Filter

```go
func Map[T, U any](slice []T, fn func(T) U) []U {
    out := make([]U, len(slice))
    for i, v := range slice {
        out[i] = fn(v)
    }
    return out
}

func Filter[T any](slice []T, pred func(T) bool) []T {
    var out []T
    for _, v := range slice {
        if pred(v) {
            out = append(out, v)
        }
    }
    return out
}

// Usage
words := []string{"go", "rust", "python", "go-lang"}
long := Filter(words, func(s string) bool { return len(s) > 3 })
// ["rust", "python", "go-lang"]
upper := Map(long, strings.ToUpper)
// ["RUST", "PYTHON", "GO-LANG"]
```
