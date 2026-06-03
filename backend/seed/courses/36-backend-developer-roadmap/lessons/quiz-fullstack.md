# Quiz: Full-Stack Basics

Test your understanding of REST APIs, Spring Boot endpoints, CORS, the Fetch API, and JWT authentication covered in this module. Each question has exactly one correct answer.

---

**Q1. Which HTTP method and status code combination best represents a successful resource creation in a REST API?**
- [ ] `GET` with `200 OK`
- [ ] `PUT` with `200 OK`
- [x] `POST` with `201 Created`
- [ ] `DELETE` with `204 No Content`

---

**Q2. What does the `@RestController` annotation do in a Spring Boot application?**
- [ ] It replaces `@SpringBootApplication` and starts the embedded web server
- [ ] It marks the class as a Spring-managed service bean that performs business logic
- [ ] It makes the class act as an HTML template renderer using Thymeleaf
- [x] It combines `@Controller` and `@ResponseBody`, so every method's return value is serialized directly as the HTTP response body (typically JSON) rather than resolved as a view name

---

**Q3. A developer writes the following Spring Boot controller. What URL path and HTTP method will the `greet` method respond to?**

```java
@RestController
@RequestMapping("/api")
public class GreetController {

    @GetMapping("/hello")
    public String greet(@RequestParam(defaultValue = "World") String name) {
        return "Hello, " + name + "!";
    }
}
```

- [x] `GET /api/hello` — with an optional `name` query parameter
- [ ] `POST /api/hello` — with `name` in the request body
- [ ] `GET /hello` — the `@RequestMapping` on the class is ignored for method-level mappings
- [ ] `GET /api` — `@GetMapping("/hello")` overrides the class-level path entirely

---

**Q4. Your HTML page is served from `http://localhost:5500` and calls a Spring Boot API running at `http://localhost:8080`. The browser blocks the response. What is the root cause, and which Spring annotation fixes it on a single controller?**
- [ ] The browser blocks the request because the API port is not 443; adding `server.port=443` in `application.properties` fixes it
- [ ] The request is blocked because `fetch` requires HTTPS; switching to `XMLHttpRequest` resolves it
- [ ] The server returns the wrong `Content-Type`; annotating the method with `@ResponseBody` fixes it
- [x] The browser enforces the Same-Origin Policy and blocks cross-origin responses; adding `@CrossOrigin(origins = "http://localhost:5500")` to the controller tells the browser the server trusts that origin

---

**Q5. Consider the following JavaScript code that calls a Spring REST endpoint:**

```javascript
async function loadContacts() {
  const res = await fetch("http://localhost:8080/api/contacts");
  const contacts = await res.json();
  return contacts;
}
```

The server returns a `404 Not Found`. What actually happens, and how should the code be fixed?

- [ ] `fetch` rejects the Promise on any non-200 status, so the `catch` block handles it automatically
- [ ] The second `await res.json()` throws a `SyntaxError`, which is the correct way to detect the failure
- [x] `fetch` only rejects on network failure, not on HTTP error status codes; `res.ok` is `false` for a 404 but no exception is thrown — the fix is to check `if (!res.ok) throw new Error(\`HTTP \${res.status}\`)` before parsing the body
- [ ] `await res.json()` returns `null` for error responses, which is sufficient to detect the failure

---

**Q6. What are the three Base64URL-encoded parts of a JWT, in order?**
- [ ] Payload · Signature · Header
- [ ] Signature · Header · Payload
- [ ] Claims · Algorithm · Secret
- [x] Header · Payload · Signature

---

**Q7. A teammate proposes storing the user's password inside the JWT payload so the server can re-verify it on each request without a database lookup. Why is this a serious security mistake?**
- [ ] JWT payloads cannot hold string fields, so it would cause a parse error
- [ ] The `exp` claim would conflict with a custom password field and invalidate the token
- [x] The JWT payload is only Base64URL-encoded, not encrypted — anyone who intercepts the token can decode and read the password in plaintext
- [ ] Storing the password in the payload is fine as long as the token is signed with HS256

---

**Q8. Which of the following correctly sends a new contact as JSON to a Spring `POST /api/contacts` endpoint using the Fetch API?**

```javascript
// Option A
fetch("http://localhost:8080/api/contacts", {
  method: "POST",
  body: { name: "Alice", phone: "555-1234" },
});

// Option B
fetch("http://localhost:8080/api/contacts", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ name: "Alice", phone: "555-1234" }),
});
```

- [ ] Option A — plain objects are automatically serialized to JSON by `fetch`
- [ ] Both options are identical because browsers always set `Content-Type: application/json` for POST requests
- [ ] Option A — `JSON.stringify` is only needed when sending arrays, not objects
- [x] Option B — `fetch` does not serialize objects automatically; you must call `JSON.stringify` on the body and set the `Content-Type: application/json` header so the server knows how to parse it

---

**Q9. What is the purpose of the **preflight** `OPTIONS` request that a browser automatically sends before certain cross-origin requests?**
- [ ] It retrieves the first page of the API's response to check for errors before committing the full request
- [ ] It authenticates the browser with the server using a temporary session cookie
- [ ] It is a browser bug workaround; production apps disable it by sending a `no-preflight` header
- [x] It asks the server whether the actual request (with its method and headers) is permitted under the server's CORS policy — the browser only proceeds with the real request if the server's `OPTIONS` response grants permission

---

**Q10. You need Spring Boot to default to port `9090` instead of `8080`. Where is the correct place to set this, and what is the exact property?**

```properties
server.port=9090
```

- [ ] In `pom.xml` inside the `<build>` section as a Maven property
- [ ] In a `@Configuration` class annotated with `@EnableWebMvc`
- [ ] As a JVM flag passed to the `java` command: `-Dport=9090`
- [x] In `src/main/resources/application.properties` using the property `server.port=9090`, which Spring Boot reads at startup to configure the embedded Tomcat port
