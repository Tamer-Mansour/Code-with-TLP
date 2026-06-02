# File I/O and Building CLI Tools

Go's standard library makes reading files, parsing arguments, and writing CLI tools straightforward without any external packages.

## Reading Files

### Read the entire file

```go
import "os"

data, err := os.ReadFile("data.txt")
if err != nil {
    log.Fatal(err)
}
fmt.Println(string(data))
```

### Read line by line (buffered)

```go
import (
    "bufio"
    "os"
)

f, err := os.Open("data.txt")
if err != nil {
    log.Fatal(err)
}
defer f.Close()

scanner := bufio.NewScanner(f)
for scanner.Scan() {
    line := scanner.Text()
    fmt.Println(line)
}
if err := scanner.Err(); err != nil {
    log.Fatal(err)
}
```

`bufio.Scanner` is the idiomatic way to process large files without loading them into memory.

### Writing Files

```go
err := os.WriteFile("out.txt", []byte("hello\n"), 0644)
```

For appending or streaming writes, open with flags:

```go
f, err := os.OpenFile("log.txt", os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
defer f.Close()
fmt.Fprintln(f, "new log line")
```

## Parsing Command-Line Arguments

### Raw `os.Args`

```go
// os.Args[0] is the program name; os.Args[1:] are the arguments
if len(os.Args) < 2 {
    fmt.Fprintln(os.Stderr, "usage: greet <name>")
    os.Exit(1)
}
fmt.Println("Hello,", os.Args[1])
```

### `flag` Package

```go
import "flag"

var (
    verbose = flag.Bool("v", false, "verbose output")
    port    = flag.Int("port", 8080, "HTTP port")
    name    = flag.String("name", "world", "name to greet")
)

func main() {
    flag.Parse()
    if *verbose {
        fmt.Println("verbose mode on")
    }
    fmt.Printf("Hello, %s on port %d\n", *name, *port)
}
```

```bash
./greet -name Alice -port 9090 -v
```

`flag.Parse()` must be called before accessing flag values. `flag.Args()` returns non-flag arguments after `--`.

## Working with Paths

```go
import "path/filepath"

dir := filepath.Dir("/tmp/logs/app.log")   // "/tmp/logs"
base := filepath.Base("/tmp/logs/app.log") // "app.log"
ext := filepath.Ext("photo.png")          // ".png"
abs, _ := filepath.Abs("./data")          // absolute path
joined := filepath.Join("tmp", "logs", "app.log") // cross-platform join
```

## Environment Variables

```go
val := os.Getenv("DATABASE_URL")
if val == "" {
    log.Fatal("DATABASE_URL not set")
}
```

## A Complete Mini CLI

```go
package main

import (
    "bufio"
    "flag"
    "fmt"
    "os"
    "strings"
)

func main() {
    upper := flag.Bool("upper", false, "convert to uppercase")
    flag.Parse()

    scanner := bufio.NewScanner(os.Stdin)
    for scanner.Scan() {
        line := scanner.Text()
        if *upper {
            line = strings.ToUpper(line)
        }
        fmt.Println(line)
    }
}
```

Build and distribute as a single binary:

```bash
go build -o transform .
echo "hello world" | ./transform -upper
# HELLO WORLD
```

## Common Patterns

| Task | Approach |
|---|---|
| Config file | `encoding/json` or `gopkg.in/yaml.v3` |
| Subcommands | `flag.NewFlagSet` per subcommand |
| Pretty output | `text/tabwriter` for aligned tables |
| Interactive prompts | `bufio.NewReader(os.Stdin).ReadString('\n')` |
| Colour terminal output | `github.com/fatih/color` (popular third-party) |
