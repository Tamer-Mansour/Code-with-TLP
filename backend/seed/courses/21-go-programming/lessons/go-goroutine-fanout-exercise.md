# Goroutine Fan-Out Pattern

Fan-out is one of the most common concurrency patterns in Go: dispatch many independent tasks to goroutines, collect results through a channel, and process them as they arrive.

## The pattern

```go
func process(id, work int, results chan<- Result) {
    time.Sleep(time.Duration(work) * time.Millisecond)
    results <- Result{ID: id, Work: work}
}

func fanOut(tasks []Task) []Result {
    results := make(chan Result, len(tasks))

    for _, t := range tasks {
        go process(t.ID, t.Work, results)
    }

    collected := make([]Result, 0, len(tasks))
    for range tasks {
        collected = append(collected, <-results)
    }
    return collected
}
```

All goroutines run concurrently. Results arrive in **completion order** (shortest work first), not submission order.

## Why results are out of order

Each goroutine sleeps for `work` milliseconds. The goroutine with the smallest `work` value finishes first and sends its result to the channel first. The channel is a buffered collector — it holds results until the main goroutine drains them.

## Race-free by design

The channel is the only shared data structure. Each goroutine writes to it exactly once. No mutex needed — this is the Go motto: **share memory by communicating**.

```go
// Safe: channel handles synchronization
results <- Result{ID: id, Work: work}

// Unsafe (would need a mutex):
// sharedSlice = append(sharedSlice, result)
```

## sync.WaitGroup vs channel collection

Two common approaches for waiting on goroutines:

**Channel collection** (shown above) — use when you need to collect return values:

```go
results := make(chan int, n)
for i := 0; i < n; i++ {
    go func(i int) { results <- compute(i) }(i)
}
for i := 0; i < n; i++ {
    total += <-results
}
```

**WaitGroup** — use when goroutines write to shared state with a mutex, or when no value is returned:

```go
var wg sync.WaitGroup
for i := 0; i < n; i++ {
    wg.Add(1)
    go func(i int) {
        defer wg.Done()
        doWork(i)
    }(i)
}
wg.Wait()
```

## Detecting races

The Go race detector catches data races that reviews miss. Always test concurrent code with:

```
go test -race ./...
go run -race main.go
```

A "data race" means two goroutines access the same variable concurrently without synchronization and at least one access is a write. The result is undefined behavior.

## Further reading

- *A Tour of Go* — [https://go.dev/tour/](https://go.dev/tour/) — "Concurrency" section with interactive goroutine and channel exercises
- *Effective Go* — [https://go.dev/doc/effective_go](https://go.dev/doc/effective_go) — "Concurrency" section: goroutine model, channels, and the pipeline pattern
- *Go 101* — [https://go101.org/article/101.html](https://go101.org/article/101.html) — channel use cases, goroutine scheduling model, and common concurrent programming mistakes
- *Go by Example* — [https://gobyexample.com/](https://gobyexample.com/) — "Goroutines", "Channels", "Select", and "WaitGroups" pages
