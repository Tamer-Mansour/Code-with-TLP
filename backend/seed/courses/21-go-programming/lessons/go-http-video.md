# Video: Building REST APIs in Go

This video walks through building a complete RESTful HTTP API in Go using only the standard library `net/http` package, with no external frameworks.

The tutorial covers creating a `ServeMux`, writing CRUD handlers, encoding and decoding JSON request/response bodies, adding middleware for logging and authentication, and graceful server shutdown using `context` and `os/signal`. Key takeaways include understanding the `http.Handler` interface, setting proper timeouts on the server, and structuring a Go HTTP project so it stays testable and maintainable as it grows.
