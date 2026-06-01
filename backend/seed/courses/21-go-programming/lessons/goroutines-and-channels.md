# Goroutines and Channels

Go's headline feature: lightweight concurrent execution and a built-in messaging primitive.

## Goroutines

A goroutine is a function running concurrently with other goroutines. Spawn one with `go`:

```go
go fetch(url)         // returns immediately; fetch runs in background
```

Goroutines are cheap — kilobytes of stack each, multiplexed onto OS threads by the Go runtime. Tens of thousands at once is normal.

## Channels

A channel is a typed pipe. Use it to send values between goroutines.

```go
ch := make(chan int)        // unbuffered
ch <- 42                    // send (blocks until someone receives)
v := <-ch                   // receive (blocks until someone sends)
```

With a buffer:

```go
ch := make(chan int, 100)   // up to 100 in flight before send blocks
```

## A worked example

```go
package main

import (
    "fmt"
    "time"
)

func work(id int, jobs <-chan int, results chan<- int) {
    for j := range jobs {
        time.Sleep(100 * time.Millisecond)   // simulate work
        results <- j * 2
        fmt.Printf("worker %d did job %d\n", id, j)
    }
}

func main() {
    jobs := make(chan int, 100)
    results := make(chan int, 100)

    for w := 1; w <= 3; w++ {
        go work(w, jobs, results)
    }

    for j := 1; j <= 5; j++ {
        jobs <- j
    }
    close(jobs)              // workers' range loops will exit

    for r := 1; r <= 5; r++ {
        fmt.Println("got", <-results)
    }
}
```

Three workers consume jobs from one channel and produce on another. Classic worker pool — easy to extend to dozens or thousands.

## Channel directions

```go
func sender(ch chan<- int) { ch <- 1 }     // send-only
func receiver(ch <-chan int) int { return <-ch } // receive-only
```

Improves API clarity; the compiler enforces direction.

## Closing channels

```go
close(ch)
v, ok := <-ch          // ok is false if channel was closed and drained
```

Close from the **sender side** when no more values will be sent. Receivers can `for v := range ch` to drain until close.

## select — multiplexed receive

```go
select {
case v := <-ch1:
    fmt.Println("ch1:", v)
case v := <-ch2:
    fmt.Println("ch2:", v)
case ch3 <- 99:
    fmt.Println("sent")
case <-time.After(time.Second):
    fmt.Println("timeout")
}
```

`select` picks the first ready case (randomly if multiple). Powerful for timeouts and cancellation.

## context — cancellation & deadlines

```go
ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
defer cancel()

result, err := doSomething(ctx)
```

Pass `ctx` down through every blocking call. If the deadline expires or someone calls `cancel`, downstream operations stop. Goroutines listen for cancellation via `<-ctx.Done()`.

## sync — when channels are overkill

For pure mutation guards:

```go
import "sync"

var (
    mu sync.Mutex
    n  int
)

func inc() {
    mu.Lock()
    defer mu.Unlock()
    n++
}
```

For counters without contention, `sync/atomic`.

For waiting on multiple goroutines:

```go
var wg sync.WaitGroup
for i := 0; i < 5; i++ {
    wg.Add(1)
    go func(i int) {
        defer wg.Done()
        work(i)
    }(i)
}
wg.Wait()
```

## Don't share memory; communicate via channels

The Go motto. Channels make data ownership clear — the sender hands off the value, the receiver owns it next. Far fewer races than ad-hoc shared state.

## go test -race

The race detector is the single best concurrency tool you have. Run your tests with `-race` in CI. It catches "this works most of the time" bugs that no review can.
