# Interfaces

Interfaces in Go are **structural** — a type implements an interface simply by having the right methods. No `implements` keyword.

## Defining one

```go
type Stringer interface {
    String() string
}
```

Any type with a `String() string` method satisfies `Stringer`. No declaration needed.

## Using an interface

```go
func describe(s fmt.Stringer) {
    fmt.Println("value:", s.String())
}
```

Pass any type with a matching method:

```go
type User struct{ Name string }
func (u User) String() string { return "User(" + u.Name + ")" }

describe(User{Name: "Alice"})    // works
```

## The empty interface

`interface{}` (or its alias `any` in 1.18+) accepts any value:

```go
func print(x any) {
    fmt.Println(x)
}
```

Useful for generic containers before Go got generics. With proper generics now, reach for `any` only when truly generic data needs to flow.

## Type assertions

```go
var x any = "hello"

s := x.(string)           // panics if x isn't a string
s, ok := x.(string)        // safer — ok is true if assertion succeeded
```

## Type switch

```go
switch v := x.(type) {
case string:
    fmt.Println("string of length", len(v))
case int:
    fmt.Println("int:", v)
case nil:
    fmt.Println("nil")
default:
    fmt.Printf("unknown type %T\n", v)
}
```

## io.Reader and io.Writer — design study

```go
type Reader interface {
    Read(p []byte) (n int, err error)
}

type Writer interface {
    Write(p []byte) (n int, err error)
}
```

Files, strings, network connections, gzip streams, HTTP bodies — all satisfy these. A function taking `io.Reader` works on every byte source. This is Go's killer interface pattern.

## Empty struct as a unit type

```go
type Set map[string]struct{}

s := make(Set)
s["a"] = struct{}{}
```

An empty struct takes 0 bytes. Common for sets and signaling channels.

## Accept interfaces, return structs

Convention: function parameters should be **interfaces** (flexible, accept any implementor). Returns should be **concrete types** (callers know exactly what they got).

```go
// good
func parse(r io.Reader) (*Result, error) { ... }

// bad
func parse(r *bytes.Buffer) (interface{}, error) { ... }
```

## Pointer vs value method sets

A subtle but important rule:

- Value type `T` has only the methods with value receivers.
- Pointer type `*T` has methods with both value and pointer receivers.

So `*User` satisfies more interfaces than `User`. If `MyInterface` includes a pointer-receiver method, pass `&user`, not `user`.

## Don't define interfaces for "future flexibility"

Define interfaces **at the call site, not the definition site**. Producers expose concrete types; consumers define small interfaces capturing only what they need. The "I" prefix from C# / Java doesn't fit Go culture — name interfaces by behavior (`Reader`, `Closer`, `Stringer`).
