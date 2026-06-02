# Packages and the Go Standard Library

Go ships with a rich standard library that covers most everyday needs — no heavy third-party frameworks required for many production services. Understanding how packages work and what stdlib offers saves you time and avoids unnecessary dependencies.

## Packages

Every `.go` file starts with a `package` declaration. Files in the same directory share a package name and see each other's unexported identifiers.

```go
// math/stats.go
package math

import "sort"

// Median is exported (capital letter).
func Median(nums []float64) float64 {
    sorted := make([]float64, len(nums))
    copy(sorted, nums)
    sort.Float64s(sorted)
    n := len(sorted)
    if n%2 == 0 {
        return (sorted[n/2-1] + sorted[n/2]) / 2
    }
    return sorted[n/2]
}
```

Rules:
- **Exported** = identifier starts with an uppercase letter.
- **Unexported** = lowercase; visible only within the package.
- `main` is the only package allowed to have a `main()` entry point.

## Organising a Real Project

```
myapp/
  go.mod
  main.go            # package main
  internal/
    store/
      store.go       # package store (unexported to external modules)
  api/
    handler.go       # package api
```

`internal/` is special — the compiler prevents code outside the module from importing it. Use it for packages you do not want to expose as a public API.

## Commonly Used Standard Library Packages

| Package | Purpose |
|---|---|
| `fmt` | Formatted I/O — `Printf`, `Sprintf`, `Errorf` |
| `strings` | String splitting, trimming, replacing |
| `strconv` | String ↔ int/float conversions |
| `os` | File ops, environment, exit |
| `io` | Interfaces: `Reader`, `Writer`, `Closer` |
| `bufio` | Buffered reading (line-by-line `Scanner`) |
| `bytes` | Byte-slice manipulation, `Buffer` |
| `encoding/json` | JSON marshal/unmarshal |
| `net/http` | HTTP client and server |
| `time` | Durations, timers, formatting |
| `math/rand` | Pseudo-random numbers |
| `sort` | Generic sort (since 1.21: `slices.Sort`) |
| `log` | Simple levelled logging (stdlib) |
| `sync` | Mutex, WaitGroup, Once |
| `context` | Cancellation and deadlines |

## A Quick Tour of `strings` and `strconv`

```go
import (
    "fmt"
    "strings"
    "strconv"
)

func main() {
    s := "  Hello, Go!  "
    fmt.Println(strings.TrimSpace(s))       // "Hello, Go!"
    fmt.Println(strings.ToUpper(s))         // "  HELLO, GO!  "
    fmt.Println(strings.Contains(s, "Go"))  // true
    parts := strings.Split("a,b,c", ",")   // ["a","b","c"]

    n, err := strconv.Atoi("42")
    if err == nil {
        fmt.Println(n + 1) // 43
    }
    fmt.Println(strconv.Itoa(100)) // "100"
}
```

## JSON Encoding

```go
import (
    "encoding/json"
    "fmt"
)

type User struct {
    Name  string `json:"name"`
    Email string `json:"email,omitempty"`
}

func main() {
    u := User{Name: "Alice", Email: "alice@example.com"}
    b, _ := json.Marshal(u)
    fmt.Println(string(b)) // {"name":"Alice","email":"alice@example.com"}

    var u2 User
    json.Unmarshal(b, &u2)
    fmt.Println(u2.Name) // Alice
}
```

Struct tags (`json:"name"`) control the key name. `omitempty` skips zero-value fields.

## Reading Docs Offline

```bash
go doc strings.Split        # signature + comment
go doc -all strings         # all exported symbols
godoc -http :6060           # local web server for pkg docs
```

Go's documentation is embedded in source comments — every public identifier you see in `pkg.go.dev` is generated from those comments.
