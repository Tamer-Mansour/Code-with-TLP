# Types, Slices, Maps

## Built-in types

```go
var i int = 42
var f float64 = 3.14
var s string = "hello"
var b bool = true
var by byte = 'A'      // alias for uint8
var r rune = '★'       // alias for int32, a Unicode code point
```

Shorthand declarations:

```go
i := 42
name := "Alice"
xs := []int{1, 2, 3}
```

`:=` declares and infers. Use inside functions; outside, use `var`.

## Zero values

A declared but uninitialized variable gets its **zero value**:

```go
var i int           // 0
var s string        // ""
var p *Foo          // nil
var m map[string]int  // nil — not usable until make()
```

No "undefined" surprises. Read zero-value-friendly designs into your APIs.

## Arrays vs slices

Arrays have a **fixed size** baked into the type:

```go
var a [3]int                 // [0,0,0]
b := [3]string{"a","b","c"}
```

You rarely use arrays directly. Use slices:

```go
xs := []int{1, 2, 3}                 // slice literal
ys := make([]int, 5)                 // length 5, capacity 5
zs := make([]int, 5, 100)            // length 5, capacity 100
```

A slice is a fat pointer: `{pointer, length, capacity}`. Multiple slices can share the same underlying array.

### Slice operations

```go
xs = append(xs, 4, 5)        // grow
sub := xs[1:4]               // [1:4), shares storage with xs
back := xs[len(xs)-1]
xs = xs[:len(xs)-1]          // pop
```

`append` may reallocate if capacity is exceeded — keep the return value.

## Strings

UTF-8 encoded byte sequences. Iterating with `range` yields runes:

```go
s := "héllo"
for i, r := range s {
    fmt.Printf("%d %c\n", i, r)
}
```

`s[i]` gives the *byte* at i (not rune). For Unicode-aware indexing, use `[]rune(s)`.

## Maps

```go
m := map[string]int{"a": 1, "b": 2}
m["c"] = 3
v, ok := m["a"]           // ok=true
delete(m, "b")
for k, v := range m { ... }   // iteration order is random!
```

Always declare with `make` or a literal — `var m map[K]V` is `nil` and panics on write.

Don't rely on iteration order. If you need stable order, sort the keys yourself.

## Pointers

```go
x := 5
p := &x
*p = 10            // x is now 10
```

No pointer arithmetic. Pointers are mostly used to:

- Avoid copying large structs.
- Express "this might be nil" or "modifies in place."
- Implement the `*receiver` pattern on methods (next lesson).

## Constants

```go
const Pi = 3.14159
const (
    StatusOK    = 200
    StatusError = 500
)
```

Untyped constants take the type of whatever they're assigned to:

```go
const Default = 10
var x int = Default      // OK
var y int64 = Default    // OK
```

## Type conversions

```go
i := 42
f := float64(i)
n := int(f)
b := []byte("hello")
s := string(b)
```

No implicit conversion — `int` to `float64` requires an explicit cast. Annoying at first, fewer bugs in production.

## iota — auto-incrementing constants

```go
const (
    Sunday = iota   // 0
    Monday          // 1
    Tuesday         // 2
    Wednesday
)
```

Useful for enums and bit flags.
