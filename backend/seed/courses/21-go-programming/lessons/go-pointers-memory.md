# Pointers and Memory in Go

Go has pointers, but no pointer arithmetic and no manual memory management. The garbage collector handles allocation and deallocation automatically, so you use pointers mainly for two reasons: mutation and avoiding copies of large structs.

## Declaring and Using Pointers

```go
x := 42
p := &x          // p is *int; & takes the address of x
fmt.Println(*p)  // 42  — * dereferences the pointer
*p = 100
fmt.Println(x)   // 100  — x was mutated through the pointer
```

## Pointers in Functions

Go is pass-by-value. Without a pointer, a function gets a copy:

```go
func double(n int) {
    n *= 2 // modifies the copy, not the caller's variable
}

func doublePtr(n *int) {
    *n *= 2 // modifies the caller's variable
}

x := 5
double(x)      // x is still 5
doublePtr(&x)  // x is now 10
```

For large structs, passing a pointer avoids copying the whole struct on every call — important for performance.

## `new` vs Composite Literals

```go
// new allocates zero value and returns a pointer
p := new(int)     // *int pointing to 0
s := new([]string) // *[]string pointing to nil slice

// Composite literal — more idiomatic
type Point struct{ X, Y int }
pt := &Point{X: 1, Y: 2}  // *Point
```

Most Go code uses composite literals (`&Struct{...}`) rather than `new`.

## Stack vs Heap — Escape Analysis

The Go compiler decides whether to allocate on the stack (fast, automatically freed) or the heap (GC-managed):

```go
func newPoint() *Point {
    p := &Point{1, 2}  // p escapes to the heap — returned to caller
    return p
}

func localPoint() {
    p := Point{1, 2}   // stays on the stack — never escapes
    _ = p
}
```

You rarely need to think about this explicitly. Use `go build -gcflags="-m"` to see the compiler's escape analysis decisions.

## nil Pointers

A pointer's zero value is `nil`. Dereferencing `nil` panics:

```go
var p *int
fmt.Println(p)  // <nil>
fmt.Println(*p) // panic: nil pointer dereference
```

Always check pointers that might be nil before dereferencing, especially values returned from functions or maps.

## Pointers to Struct Fields

```go
type Config struct {
    Debug   bool
    Timeout int
}

cfg := Config{Debug: true, Timeout: 30}
p := &cfg
p.Debug = false  // Go auto-dereferences; same as (*p).Debug = false
fmt.Println(cfg.Debug) // false
```

## Value vs Pointer Receivers

```go
type Counter struct{ n int }

// Value receiver — works on a copy
func (c Counter) Value() int { return c.n }

// Pointer receiver — mutates the original
func (c *Counter) Increment() { c.n++ }

c := Counter{}
c.Increment()
fmt.Println(c.Value()) // 1
```

Rule of thumb: if any method needs to mutate, give all methods pointer receivers for consistency.

## Summary Table

| Scenario | Use |
|---|---|
| Read-only, small struct | value |
| Mutation needed | pointer |
| Large struct (avoids copy) | pointer |
| Optional/nullable value | pointer (nil = absent) |
| Implement interface with mutating methods | pointer receiver |
