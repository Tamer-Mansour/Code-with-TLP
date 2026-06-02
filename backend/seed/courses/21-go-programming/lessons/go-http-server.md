# Building HTTP Servers with `net/http`

Go's standard library `net/http` package is production-grade. Companies run millions of requests per second through it. No framework is required — you can reach for one (Gin, Echo, Chi) once you understand what the stdlib provides.

## The Simplest Server

```go
package main

import (
    "fmt"
    "net/http"
)

func hello(w http.ResponseWriter, r *http.Request) {
    fmt.Fprintln(w, "Hello, World!")
}

func main() {
    http.HandleFunc("/", hello)
    http.ListenAndServe(":8080", nil)
}
```

`http.HandleFunc` registers a handler on the default `ServeMux`. `ListenAndServe` blocks until the server exits.

## The `http.Handler` Interface

```go
type Handler interface {
    ServeHTTP(ResponseWriter, *Request)
}
```

Any type implementing `ServeHTTP` is an `http.Handler`. `http.HandlerFunc` adapts a function to this interface automatically.

## Reading Request Data

```go
func handler(w http.ResponseWriter, r *http.Request) {
    // Method and URL
    fmt.Println(r.Method, r.URL.Path)

    // Query params: /search?q=go&limit=10
    q := r.URL.Query().Get("q")

    // JSON body
    var payload struct {
        Name string `json:"name"`
    }
    json.NewDecoder(r.Body).Decode(&payload)
    defer r.Body.Close()

    // Headers
    auth := r.Header.Get("Authorization")
    _ = q; _ = auth
}
```

## Writing Responses

```go
func jsonResp(w http.ResponseWriter, r *http.Request) {
    w.Header().Set("Content-Type", "application/json")
    w.WriteHeader(http.StatusCreated) // must call before writing body

    json.NewEncoder(w).Encode(map[string]any{
        "message": "created",
        "id":      42,
    })
}
```

Calling `w.Write` or `json.NewEncoder(w).Encode` after `WriteHeader` is fine; calling `WriteHeader` after writing is ignored.

## Using a Custom ServeMux

```go
mux := http.NewServeMux()
mux.HandleFunc("/api/users", usersHandler)
mux.HandleFunc("/api/users/", userHandler) // trailing slash: prefix match
mux.Handle("/static/", http.StripPrefix("/static/", http.FileServer(http.Dir("./public"))))

srv := &http.Server{
    Addr:         ":8080",
    Handler:      mux,
    ReadTimeout:  5 * time.Second,
    WriteTimeout: 10 * time.Second,
    IdleTimeout:  120 * time.Second,
}
log.Fatal(srv.ListenAndServe())
```

Always set timeouts on production servers — the defaults are unbounded.

## Middleware Pattern

```go
func logging(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        start := time.Now()
        next.ServeHTTP(w, r)
        log.Printf("%s %s %s", r.Method, r.URL.Path, time.Since(start))
    })
}

// Wrap the mux
log.Fatal(http.ListenAndServe(":8080", logging(mux)))
```

Chain multiple middlewares by wrapping repeatedly: `cors(logging(mux))`.

## Making HTTP Requests (Client Side)

```go
resp, err := http.Get("https://api.github.com/repos/golang/go")
if err != nil {
    log.Fatal(err)
}
defer resp.Body.Close()

var repo struct {
    Stars int `json:"stargazers_count"`
}
json.NewDecoder(resp.Body).Decode(&repo)
fmt.Println("Stars:", repo.Stars)
```

For production use a custom client with timeouts:

```go
client := &http.Client{Timeout: 10 * time.Second}
resp, err := client.Get(url)
```

## Quick Reference

| Task | API |
|---|---|
| Register route | `http.HandleFunc(pattern, fn)` |
| Set response header | `w.Header().Set(key, val)` |
| Set status code | `w.WriteHeader(code)` |
| Redirect | `http.Redirect(w, r, url, http.StatusFound)` |
| Serve static files | `http.FileServer(http.Dir(path))` |
| Parse JSON body | `json.NewDecoder(r.Body).Decode(&v)` |
| Write JSON response | `json.NewEncoder(w).Encode(v)` |
