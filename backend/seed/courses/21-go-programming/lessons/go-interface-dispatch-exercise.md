# Interface Dispatch: Polymorphic Shape Areas

Interfaces are Go's mechanism for polymorphism. Unlike Java or C#, there is no `implements` keyword. A type satisfies an interface the moment it defines all the required methods — the compiler checks this silently at assignment.

## Defining the Shape interface

```go
type Shape interface {
    Area() float64
}
```

Any type with an `Area() float64` method satisfies `Shape`. You never declare it.

## Implementing the interface

```go
import "math"

type Circle struct {
    Radius float64
}

func (c Circle) Area() float64 {
    return math.Pi * c.Radius * c.Radius
}

type Rectangle struct {
    Width, Height float64
}

func (r Rectangle) Area() float64 {
    return r.Width * r.Height
}

type Triangle struct {
    Base, Height float64
}

func (t Triangle) Area() float64 {
    return 0.5 * t.Base * t.Height
}
```

None of these types mention `Shape`. Satisfaction is structural and implicit.

## Polymorphic dispatch

```go
func printArea(s Shape) {
    fmt.Printf("%.2f\n", s.Area())
}

shapes := []Shape{
    Circle{Radius: 7},
    Rectangle{Width: 4, Height: 5},
    Triangle{Base: 6, Height: 8},
}

for _, s := range shapes {
    printArea(s)
}
```

Output:
```
153.94
20.00
24.00
```

The `printArea` function has no knowledge of `Circle`, `Rectangle`, or `Triangle`. It only knows about the `Area()` method. This is the essence of **duck typing** — if it has the right methods, it works.

## The nil interface trap

One subtlety to know: a nil pointer stored in an interface variable is **not** a nil interface. An interface value is a `(type, value)` pair. The interface is nil only when **both** type and value are absent.

```go
var c *Circle = nil
var s Shape = c      // s is NOT nil — it has a type descriptor!
fmt.Println(s == nil) // false
```

This is one of Go's most notorious gotchas. Always pass a plain `nil` (not a typed nil pointer) when you want a nil interface.

## Accepted interface, returned struct

A Go convention worth memorizing:

```go
// Prefer this:
func describe(s Shape) string { ... }   // accepts interface — flexible

// Over this:
func describe(c *Circle) string { ... } // locked to one concrete type
```

Functions that accept interfaces work with any present and future implementor. Functions that return values should return concrete types so callers know exactly what they hold.

## Further reading

- *Effective Go* — [https://go.dev/doc/effective_go](https://go.dev/doc/effective_go) — "Interfaces and other types" section explains Go's implicit satisfaction and the `io.Reader`/`io.Writer` design philosophy
- *A Tour of Go* — [https://go.dev/tour/](https://go.dev/tour/) — "Methods and interfaces" section with interactive exercises
- *Go by Example* — [https://gobyexample.com/](https://gobyexample.com/) — "Interfaces" page
