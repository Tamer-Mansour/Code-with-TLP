# Hello, Go

Go (often "Golang") is a compiled, statically-typed language designed at Google in 2009 for fast builds, clear concurrency, and a small standard library you can read in an afternoon. Programs compile to a single static binary — no runtime to install.

## Install and verify

```bash
# macOS
brew install go
# Linux: download tarball or use distro package
# Windows: msi installer at go.dev
go version
```

## A first program

`hello.go`:

```go
package main

import "fmt"

func main() {
    fmt.Println("Hello, Go")
}
```

Run:

```bash
go run hello.go        # compile + run
go build hello.go      # produce ./hello
./hello
```

## Project layout

Go uses **modules** for dependency management:

```bash
mkdir myapp && cd myapp
go mod init github.com/me/myapp     # creates go.mod
```

Add dependencies with `go get`:

```bash
go get github.com/google/uuid
```

`go.mod` + `go.sum` together pin all transitive versions.

## Imports

```go
import (
    "fmt"
    "io"
    "net/http"

    "github.com/google/uuid"
)
```

Unused imports are a **compile error** — `goimports` and `gofmt` keep them tidy automatically.

## Formatting

Go has one official style. `gofmt` (or `goimports`) formats your file; editors run it on save. No style PRs to bikeshed.

## The Go toolchain

| Command           | What it does                          |
|-------------------|---------------------------------------|
| `go run`          | compile + run                         |
| `go build`        | compile to binary                     |
| `go test`         | run tests                             |
| `go test -race`   | tests with race detector              |
| `go vet`          | static analysis                       |
| `go mod tidy`     | sync go.mod with imports              |
| `go install pkg@latest` | install a CLI tool                 |
| `go doc fmt.Println` | offline docs                        |

## What Go is good for

- HTTP backends (Echo, Gin, native `net/http`).
- CLI tools (single static binaries).
- Containers / DevOps tools (Docker, Kubernetes, Terraform — all written in Go).
- Network services (gRPC, proxies).

## What Go won't give you

- Generics like C++ templates (you have basic generics since 1.18, more limited).
- A REPL (use `go run main.go` for tiny experiments).
- ML / data science (numerical ecosystem is thin).
- A fancy ORM (most apps use raw SQL with `database/sql` + `sqlc` or `pgx`).

That's the deal: a few opinionated choices in exchange for simplicity, speed, and concurrency that just works.
