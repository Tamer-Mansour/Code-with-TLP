# Quiz: REST APIs

Test your understanding of building REST APIs with Spring Boot 3 — covering REST constraints, HTTP semantics, Spring MVC annotations, status codes, request data binding, and controller design best practices.

---

**Q1. Which annotation combination is equivalent to `@RestController`?**
- [ ] `@Controller` + `@RequestMapping`
- [ ] `@Component` + `@ResponseBody`
- [x] `@Controller` + `@ResponseBody`
- [ ] `@Service` + `@RequestMapping`

---

**Q2. A `POST /api/products` endpoint successfully creates a new product. Which HTTP status code and response practice best follows REST conventions?**

```java
URI location = ServletUriComponentsBuilder.fromCurrentRequest()
        .path("/{id}")
        .buildAndExpand(created.id())
        .toUri();
return ResponseEntity.created(location).body(created);
```

- [ ] Return `200 OK` with the created resource in the body.
- [ ] Return `204 No Content` to indicate the operation succeeded silently.
- [x] Return `201 Created` with a `Location` header pointing to the new resource.
- [ ] Return `202 Accepted` because the creation may not be immediate.

---

**Q3. Which annotation is used to bind a dynamic segment of the URL path to a method parameter?**

```java
// Route: GET /api/orders/{orderId}/items/{itemId}
@GetMapping("/{orderId}/items/{itemId}")
public Item getItem(/* which annotation? */ Long orderId,
                    /* which annotation? */ Long itemId) { ... }
```

- [ ] `@RequestParam`
- [ ] `@RequestBody`
- [ ] `@RequestHeader`
- [x] `@PathVariable`

---

**Q4. A client sends `GET /api/products?category=electronics&page=2&size=15`. Which Spring MVC annotation correctly binds the `category`, `page`, and `size` values?**
- [ ] `@PathVariable`
- [ ] `@RequestBody`
- [x] `@RequestParam`
- [ ] `@ModelAttribute`

---

**Q5. Examine this controller method. What HTTP status will a caller receive when `productService.delete(id)` completes without throwing an exception?**

```java
@DeleteMapping("/{id}")
public ResponseEntity<Void> delete(@PathVariable Long id) {
    productService.delete(id);
    return ResponseEntity.noContent().build();
}
```

- [ ] 200 OK
- [ ] 201 Created
- [x] 204 No Content
- [ ] 202 Accepted

---

**Q6. Which of the following HTTP methods is idempotent but NOT safe?**

| Method | Safe | Idempotent |
|--------|------|------------|
| GET | yes | yes |
| POST | no | no |
| PUT | no | yes |
| DELETE | no | yes |

- [ ] `GET`
- [ ] `POST`
- [x] `PUT`
- [ ] `PATCH`

---

**Q7. A developer writes this handler. What is the problem with it?**

```java
@PostMapping
public Product create(@RequestBody Product product) {
    return productRepository.save(product);
}
```

- [ ] `@RequestBody` cannot be used with `POST` mappings.
- [ ] The method must be `void` when using `@RequestBody`.
- [ ] `productRepository.save()` always returns `null` for new entities.
- [x] The JPA entity `Product` is exposed directly as the request body, risking mass-assignment vulnerabilities and tight coupling; a dedicated request DTO should be used instead.

---

**Q8. Which `application.properties` setting changes the default context path so that all endpoints are served under `/api` instead of `/`?**
- [ ] `spring.mvc.path=/api`
- [ ] `server.context=/api`
- [x] `server.servlet.context-path=/api`
- [ ] `spring.web.base-path=/api`

---

**Q9. What does the `@RequestMapping` annotation at the class level accomplish in the following controller?**

```java
@RestController
@RequestMapping("/api/v1/customers")
public class CustomerController {

    @GetMapping("/{id}")
    public CustomerDto getById(@PathVariable Long id) { ... }

    @PostMapping
    public ResponseEntity<CustomerDto> create(@RequestBody CreateCustomerRequest req) { ... }
}
```

- [x] It sets a base URL prefix `/api/v1/customers` that is prepended to every handler method's path in the class.
- [ ] It limits the controller to processing only GET requests.
- [ ] It registers the controller as a Spring bean; without it the class would not be detected.
- [ ] It configures content negotiation so the controller only returns `application/json`.

---

**Q10. A client sends a request with a missing required query parameter and no `defaultValue` is configured. What does Spring Boot return by default?**

```java
@GetMapping("/search")
public List<Product> search(@RequestParam String keyword) { ... }
// Request: GET /api/products/search   (no ?keyword=...)
```

- [ ] An empty list `[]` with status 200.
- [ ] A `NullPointerException` propagated as a 500 Internal Server Error.
- [ ] A redirect to the same endpoint with `keyword=` appended.
- [x] A `400 Bad Request` response indicating that the required parameter `keyword` is missing.
