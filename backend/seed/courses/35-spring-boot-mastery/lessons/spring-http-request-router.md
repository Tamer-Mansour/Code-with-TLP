# Exercise: HTTP Request Router

Spring's `@RequestMapping` system matches every incoming HTTP request to exactly one handler method by comparing the request's **HTTP method** and **path** against registered routes. This exercise asks you to build a simplified version of that routing table.

## What you need to implement

Build an in-memory router that:

1. Registers routes: each route maps `(HTTP method, path)` to a handler name.
2. Handles incoming requests: for each request, look up the matching handler or return `404 Not Found`.
3. When the same `(method, path)` pair is registered more than once, the **last registration wins** (this mirrors Spring's behaviour when multiple `@Bean` definitions produce the same mapping — only one survives).

## Real-world connection

Every `@GetMapping`, `@PostMapping`, `@PutMapping`, and `@DeleteMapping` annotation registers exactly one route in Spring's `RequestMappingHandlerMapping`. When a request arrives, the `DispatcherServlet` asks `HandlerMapping` for the correct handler; if none matches, it falls through to the 404 error handler (`NoHandlerFoundException`).

Route collisions (two methods mapped to the same path and HTTP verb) throw `IllegalStateException` at startup in real Spring — here you are simulating a lenient registry where last-write-wins.

## Input format

```
M
METHOD /path HandlerName
...
Q
METHOD /path
...
```

- First line: `M` — number of route registrations.
- Next `M` lines: `METHOD /path HandlerName` (e.g. `GET /users listUsers`).
- Next line: `Q` — number of incoming requests.
- Next `Q` lines: `METHOD /path` (e.g. `GET /users`).

Paths are exact strings; no wildcards or path variables.

## Output format

For each request, print the handler name, or `404 Not Found` if no route matches.

## Example

**Input:**
```
5
GET /users listUsers
POST /users createUser
GET /users/1 getUser
DELETE /users/1 deleteUser
GET /health healthCheck
4
GET /users
POST /users
GET /products
DELETE /users/1
```

**Output:**
```
listUsers
createUser
404 Not Found
deleteUser
```

## Further reading

- [Spring Boot Reference — MVC](https://docs.spring.io/spring-boot/docs/current/reference/htmlsingle/)
- [Building REST Services with Spring (Baeldung PDF)](https://www.baeldung.com/wp-content/uploads/2013/09/Building-REST-Services-with-Spring.pdf) — Chapter on request mapping
