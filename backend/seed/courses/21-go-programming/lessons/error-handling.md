# Errors as Values

Go has no exceptions. Errors are values returned alongside results, and you handle them explicitly. This is verbose, intentional, and surprisingly effective.

## The error interface

```go
type error interface {
    Error() string
}
```

That's it. Anything with an `Error() string` method is an error.

## Returning and checking

```go
func divide(a, b float64) (float64, error) {
    if b == 0 {
        return 0, fmt.Errorf("divide by zero")
    }
    return a / b, nil
}

result, err := divide(10, 0)
if err != nil {
    fmt.Println("error:", err)
    return
}
fmt.Println(result)
```

The `if err != nil` block is everywhere. Embrace it.

## errors.New and fmt.Errorf

```go
import "errors"

var ErrNotFound = errors.New("not found")

func lookup(id int) (User, error) {
    if id == 0 {
        return User{}, ErrNotFound
    }
    if id < 0 {
        return User{}, fmt.Errorf("invalid id %d", id)
    }
    ...
}
```

`fmt.Errorf` with `%w` **wraps** an error:

```go
return fmt.Errorf("lookup user %d: %w", id, err)
```

The wrapped error is preserved for inspection.

## errors.Is and errors.As

Check identity:

```go
if errors.Is(err, ErrNotFound) {
    // handle not-found, even through wrapping
}
```

Check type and unwrap into a typed error:

```go
var pathErr *fs.PathError
if errors.As(err, &pathErr) {
    fmt.Println("path:", pathErr.Path)
}
```

Don't use `==` to compare errors — wrapping breaks it.

## Custom error types

```go
type ValidationError struct {
    Field   string
    Message string
}

func (e *ValidationError) Error() string {
    return fmt.Sprintf("validation: %s: %s", e.Field, e.Message)
}
```

Then:

```go
err := &ValidationError{Field: "email", Message: "missing @"}
return err
```

And callers can `errors.As` for the typed details.

## panic / recover — not for control flow

```go
panic("something went very wrong")     // crashes goroutine with stack trace

defer func() {
    if r := recover(); r != nil {
        log.Println("recovered:", r)
    }
}()
```

Reserve `panic` for *truly unrecoverable* programmer errors (index out of bounds, nil pointer dereference, impossible state). Convert them to errors at API boundaries with `recover` only at well-defined points (HTTP middleware, goroutine roots).

## defer for cleanup

```go
file, err := os.Open(path)
if err != nil { return err }
defer file.Close()
```

`defer`-ed calls run when the function returns, in LIFO order. The Go idiom for guaranteed cleanup.

## Error wrapping in practice

A function that calls another function should add context, not just propagate:

```go
func loadUserOrders(ctx context.Context, userID int64) ([]Order, error) {
    u, err := getUser(ctx, userID)
    if err != nil {
        return nil, fmt.Errorf("get user %d: %w", userID, err)
    }
    orders, err := listOrders(ctx, u.ID)
    if err != nil {
        return nil, fmt.Errorf("list orders for user %d: %w", u.ID, err)
    }
    return orders, nil
}
```

The chained `%w` calls produce stack-trace-like messages without an exception system.

## The verbosity is the feature

You write 3 lines for what other languages do in 1. The compensation: every error path is visible at the call site. Reviewers and readers know exactly what can go wrong, and where.
