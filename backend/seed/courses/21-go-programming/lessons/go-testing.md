# Testing in Go

Go's testing support is built into the toolchain — no third-party framework needed. The `testing` package plus `go test` give you unit tests, benchmarks, and example-based documentation in one tool.

## Writing a Test

Create a file ending in `_test.go` in the same package:

```go
// math_test.go
package math_test

import (
    "testing"
    "myapp/math"
)

func TestMedian(t *testing.T) {
    got := math.Median([]float64{3, 1, 2})
    if got != 2 {
        t.Errorf("Median([3,1,2]) = %v; want 2", got)
    }
}
```

Run tests:

```bash
go test ./...         # run all tests in all packages
go test -v ./math/    # verbose output for one package
go test -run TestMedia # filter by test name (regex)
```

## Table-Driven Tests

The idiomatic Go pattern for covering many inputs:

```go
func TestMedian(t *testing.T) {
    cases := []struct {
        name  string
        input []float64
        want  float64
    }{
        {"odd", []float64{1, 3, 2}, 2},
        {"even", []float64{1, 2, 3, 4}, 2.5},
        {"single", []float64{7}, 7},
    }

    for _, tc := range cases {
        t.Run(tc.name, func(t *testing.T) {
            got := math.Median(tc.input)
            if got != tc.want {
                t.Errorf("Median(%v) = %v; want %v", tc.input, got, tc.want)
            }
        })
    }
}
```

`t.Run` creates sub-tests that show up individually in output and can be run by name.

## Subtests and Helpers

```go
func setup(t *testing.T) string {
    t.Helper() // marks this as a helper so line numbers in failures point to callers
    dir := t.TempDir() // automatically cleaned up after test
    return dir
}
```

## Benchmarks

```go
func BenchmarkMedian(b *testing.B) {
    data := []float64{5, 3, 9, 1, 7}
    for i := 0; i < b.N; i++ {
        math.Median(data)
    }
}
```

```bash
go test -bench=. -benchmem ./math/
```

Output shows ns/op and allocations per operation — great for hot-path tuning.

## Example Functions

```go
func ExampleMedian() {
    fmt.Println(math.Median([]float64{1, 2, 3}))
    // Output: 2
}
```

These appear in `go doc` and are also run as tests — if the output doesn't match the comment, the test fails.

## The Race Detector

```bash
go test -race ./...
```

Finds data races at runtime. Always run in CI. A race detector hit is a guaranteed bug even if the test otherwise passes.

## Code Coverage

```bash
go test -coverprofile=cover.out ./...
go tool cover -html=cover.out   # opens browser with highlighted source
```

Aim for high coverage on business logic; don't chase 100% on glue/infra code.

## Useful Testing Helpers Table

| What you need | How to do it |
|---|---|
| Fail and continue | `t.Errorf(...)` |
| Fail and stop | `t.Fatalf(...)` |
| Skip a test | `t.Skip("reason")` |
| Temp directory | `t.TempDir()` |
| Parallel subtests | `t.Parallel()` |
| Log (only on failure) | `t.Logf(...)` |
