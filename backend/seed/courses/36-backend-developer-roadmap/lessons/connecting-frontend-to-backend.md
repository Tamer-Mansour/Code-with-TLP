# Connecting a Frontend to a Backend (fetch + CORS)

So far your Spring Boot API and your HTML page have lived in separate worlds. Now we'll wire them together: the browser calls your backend with the **Fetch API**, and your backend explicitly allows that call with **CORS**.

## Why CORS exists

Browsers enforce the **Same-Origin Policy**. An *origin* is the combination of scheme + host + port. If your page is served from `http://localhost:5500` but calls an API at `http://localhost:8080`, those are *different origins*, and the browser blocks the response by default.

| Page origin | API origin | Same origin? |
|---|---|---|
| `http://localhost:8080` | `http://localhost:8080` | Yes |
| `http://localhost:5500` | `http://localhost:8080` | No (port differs) |
| `https://app.tlp.com` | `http://api.tlp.com` | No (scheme + host differ) |

**CORS** (Cross-Origin Resource Sharing) is how the server says "I trust this origin." It does this by sending response headers like `Access-Control-Allow-Origin`. Without them, the browser throws a CORS error even though the server actually responded.

## Calling the backend with fetch

`fetch` returns a Promise. Here is a typical GET and POST against a Spring `/api/messages` endpoint:

```javascript
// GET a list of messages
async function loadMessages() {
  const res = await fetch("http://localhost:8080/api/messages");
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  const messages = await res.json();
  console.log(messages);
}

// POST a new message
async function sendMessage(text) {
  const res = await fetch("http://localhost:8080/api/messages", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text }),
  });
  return res.json();
}
```

Two things beginners forget: `fetch` does **not** reject on HTTP 404/500 (only on network failure), so always check `res.ok`; and you must `JSON.stringify` the body and set the `Content-Type` header yourself.

## Enabling CORS in Spring Boot

The simplest approach is `@CrossOrigin` on a controller:

```java
@RestController
@RequestMapping("/api/messages")
@CrossOrigin(origins = "http://localhost:5500")
public class MessageController {

    @GetMapping
    public List<String> all() {
        return List.of("Hello", "World");
    }
}
```

For a real app, configure CORS globally so every endpoint shares one policy:

```java
@Configuration
public class CorsConfig implements WebMvcConfigurer {

    @Override
    public void addCorsMappings(CorsRegistry registry) {
        registry.addMapping("/api/**")
                .allowedOrigins("http://localhost:5500")
                .allowedMethods("GET", "POST", "PUT", "DELETE")
                .allowedHeaders("*");
    }
}
```

### Preflight requests

For "non-simple" requests (e.g. a POST with `Content-Type: application/json`), the browser first sends an automatic `OPTIONS` request, the **preflight**, asking permission. Spring's CORS support answers it automatically once you've configured the mapping above. You don't write the `OPTIONS` handler yourself.

## Common mistakes and best practices

- **Don't** use `allowedOrigins("*")` together with credentials (cookies). The combination is rejected by the browser; use explicit origins instead.
- **Match the exact origin**, including the port. `localhost:5500` and `localhost:3000` are different.
- A CORS error is a *browser* enforcement. The same request from `curl` or Postman succeeds, so test cross-origin behavior in the browser.
- Keep allowed origins in `application.properties` so dev and prod differ cleanly:

```properties
app.cors.allowed-origin=http://localhost:5500
```

- Always handle failures in the UI: check `res.ok` and wrap calls in `try/catch`.

## Summary

The browser blocks cross-origin API calls until the server opts in via CORS headers. Use `fetch` (checking `res.ok`) on the frontend and configure `addCorsMappings` or `@CrossOrigin` with explicit origins on your Spring backend.
