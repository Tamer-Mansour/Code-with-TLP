# Error Propagation and Wrapping

Go 1.13 introduced first-class error wrapping. The pattern lets you attach context at each layer of your call stack while preserving the original error for programmatic inspection.

## Wrapping with %w

```go
func loadConfig(path string) (*Config, error) {
    data, err := os.ReadFile(path)
    if err != nil {
        return nil, fmt.Errorf("loadConfig %s: %w", path, err)
    }
    // ...
}
```

The `%w` verb wraps `err` inside the returned error. The message reads as a chain:

```
loadConfig /etc/app.yaml: open /etc/app.yaml: no such file or directory
```

## errors.Is — searching the chain

`errors.Is` traverses the entire chain looking for a match:

```go
var ErrNotFound = errors.New("not found")

err := fmt.Errorf("get user: %w", fmt.Errorf("db query: %w", ErrNotFound))

errors.Is(err, ErrNotFound) // true — found three levels deep
```

Contrast with `==`:

```go
err == ErrNotFound  // false — err is a wrapped copy, not ErrNotFound itself
```

Always use `errors.Is` for sentinel error comparison.

## errors.As — typed unwrapping

```go
type DBError struct {
    Code    int
    Message string
}

func (e *DBError) Error() string {
    return fmt.Sprintf("db error %d: %s", e.Code, e.Message)
}

// ---

var dbErr *DBError
if errors.As(err, &dbErr) {
    fmt.Println("database error code:", dbErr.Code)
}
```

`errors.As` finds the first error in the chain that matches the target type and assigns it.

## Building an error chain

```go
inner := errors.New("timeout")
middle := fmt.Errorf("connection refused: %w", inner)
outer := fmt.Errorf("network error: %w", middle)
```

The chain is:
```
network error -> connection refused -> timeout
```

Calling `errors.Is(outer, inner)` returns `true`. The chain is traversed automatically.

## Error chain semantics vs message strings

An important distinction: `errors.Is` compares by **identity** (same pointer for sentinel errors, or a custom `Is` method). It does not do string matching. This exercise simulates the string-matching view to help you understand how the chain is traversed.

In real Go code:

```go
// WRONG — wrapping breaks == comparison
if err == ErrNotFound { }

// CORRECT — works through any number of wrapping layers
if errors.Is(err, ErrNotFound) { }
```

## Further reading

- *Effective Go* — [https://go.dev/doc/effective_go](https://go.dev/doc/effective_go) — "Errors" section
- *Go by Example* — [https://gobyexample.com/](https://gobyexample.com/) — "Errors" and "Custom Errors" pages
- *Go 101* — [https://go101.org/article/101.html](https://go101.org/article/101.html) — error handling chapter, including the `errors.Is`/`errors.As` internals
