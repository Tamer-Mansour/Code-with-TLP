# Testing APIs with Postman and curl

Once a REST controller is running locally, you need fast feedback: did the endpoint return the right status code, the right body, the right headers? Two tools cover the full range — **curl** for quick terminal-based checks and scriptable pipelines, and **Postman** for a GUI workflow with saved collections, environments, and automated test scripts.

## The sample controller

All examples below target this minimal Spring Boot controller, assumed running on `http://localhost:8080`:

```java
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.util.List;

@RestController
@RequestMapping("/api/products")
public class ProductController {

    private final ProductService service;

    public ProductController(ProductService service) {
        this.service = service;
    }

    @GetMapping
    public List<Product> findAll() {
        return service.findAll();
    }

    @GetMapping("/{id}")
    public ResponseEntity<Product> findById(@PathVariable Long id) {
        return service.findById(id)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    @PostMapping
    public ResponseEntity<Product> create(@RequestBody Product product) {
        Product saved = service.save(product);
        return ResponseEntity.status(201).body(saved);
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> delete(@PathVariable Long id) {
        service.delete(id);
        return ResponseEntity.noContent().build();
    }
}
```

## Testing with curl

curl ships with every major OS (Windows 10+, macOS, Linux). Open a terminal and run the commands below directly.

### GET all products

```bash
curl -s http://localhost:8080/api/products | jq .
```

The `-s` flag silences the progress bar. Pipe to `jq` for pretty-printed JSON (install via `brew install jq` on macOS or `sudo apt install jq` on Ubuntu).

### GET a single product

```bash
curl -s http://localhost:8080/api/products/1
```

If the product does not exist, Spring returns `404 Not Found`. To see the HTTP status code alongside the body:

```bash
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8080/api/products/999
```

### POST — create a product

```bash
curl -s -X POST http://localhost:8080/api/products \
     -H "Content-Type: application/json" \
     -d '{"name": "Laptop", "price": 1299.99}'
```

Spring Boot reads the `Content-Type` header to select the correct `HttpMessageConverter`. Omitting it returns `415 Unsupported Media Type`.

### DELETE a product

```bash
curl -s -X DELETE http://localhost:8080/api/products/1 -o /dev/null -w "%{http_code}\n"
```

Expected output: `204`

## curl flag quick reference

| Flag | Meaning |
|------|---------|
| `-X METHOD` | Override HTTP method (`POST`, `PUT`, `DELETE`) |
| `-H "Header: value"` | Add a request header |
| `-d '{"key":"val"}'` | Send a request body |
| `-s` | Silent mode — suppress progress output |
| `-i` | Include response headers in output |
| `-o /dev/null -w "%{http_code}"` | Print only the status code |
| `-u user:password` | Basic authentication |

## Testing with Postman

Postman provides a persistent workspace where you organize requests into **Collections**, share **Environments** (e.g., `localhost` vs `staging`), and attach JavaScript **Tests** that assert on the response.

### Creating a request

1. Open Postman and click **New → HTTP Request**.
2. Set the method to `POST` and the URL to `{{baseUrl}}/api/products`.
3. Open the **Body** tab, choose **raw → JSON**, and paste:

```json
{
  "name": "Mechanical Keyboard",
  "price": 149.99
}
```

4. Click **Send**. Postman displays the response status, time, body, and headers.

### Environments

Define a variable `baseUrl` in an Environment so every request in the collection picks it up:

| Variable | Initial value | Current value |
|----------|---------------|---------------|
| `baseUrl` | `http://localhost:8080` | `http://localhost:8080` |

Switch the active environment in the top-right dropdown to point the whole collection at a different host instantly.

### Writing automated tests

In the **Tests** tab of any request, write JavaScript assertions using Postman's built-in `pm` API:

```javascript
pm.test("Status is 201", () => {
    pm.response.to.have.status(201);
});

pm.test("Response has an id", () => {
    const body = pm.response.json();
    pm.expect(body.id).to.be.a("number");
});
```

Run the full collection via **Collection Runner** or the Postman CLI (`postman collection run`) in a CI pipeline.

## Common mistakes and best practices

- **Missing `Content-Type` header on POST/PUT.** Spring Boot's `@RequestBody` requires `Content-Type: application/json`. Without it, the server returns `415`.
- **Sending a string instead of a JSON body in curl.** On Windows CMD, use double quotes around the `-d` value and escape inner quotes: `-d "{\"name\":\"Laptop\"}"`. In PowerShell, use single-quoted here-strings to avoid escaping.
- **Not checking 4xx/5xx details.** Enable Spring Boot's `/actuator/health` or include `server.error.include-message=always` in `application.properties` to surface error messages during development.
- **Hard-coded URLs in Postman.** Always use environment variables (`{{baseUrl}}`) so requests are portable across environments.
- **Ignoring response headers.** Use `curl -i` or Postman's **Headers** tab to inspect `Location`, `Content-Type`, and custom headers your API is supposed to set.

## Summary

curl is the fastest way to fire a one-off request from the terminal or a shell script, while Postman shines for building a reusable, documented, and testable collection that the whole team can run. Both tools together give you full visibility into your Spring Boot REST API at every stage of development.
