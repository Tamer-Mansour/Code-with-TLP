# @RestController and Request Mapping

Spring MVC's `@RestController` and its family of mapping annotations are the entry points for every HTTP request your API handles. Understanding how they work — and how they compose — is the foundation of every REST endpoint you will ever write in Spring Boot.

## @RestController vs @Controller

`@RestController` is a composed annotation that combines `@Controller` and `@ResponseBody`.

| Annotation | Behavior |
|---|---|
| `@Controller` | Marks a Spring bean as an MVC controller; return values are resolved as view names (Thymeleaf, JSP). |
| `@ResponseBody` | Serializes the return value directly to the HTTP response body (JSON by default via Jackson). |
| `@RestController` | Both of the above together — every method's return value is written to the response body. |

Use `@RestController` for every REST API endpoint. Reserve `@Controller` for server-side rendered views.

## @RequestMapping

`@RequestMapping` on a class sets a **base path** that all methods in that class inherit. On a method it adds more specificity (sub-path, HTTP method, content types).

```java
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/products")
public class ProductController {

    @RequestMapping(method = RequestMethod.GET)
    public List<String> list() {
        return List.of("Laptop", "Phone", "Tablet");
    }

    @RequestMapping(value = "/{id}", method = RequestMethod.GET)
    public String getOne(@PathVariable Long id) {
        return "Product " + id;
    }
}
```

Writing `method = RequestMethod.GET` every time is verbose. Spring provides shortcut annotations for each HTTP verb.

## HTTP Method Shortcuts

| Annotation | Equivalent |
|---|---|
| `@GetMapping` | `@RequestMapping(method = GET)` |
| `@PostMapping` | `@RequestMapping(method = POST)` |
| `@PutMapping` | `@RequestMapping(method = PUT)` |
| `@PatchMapping` | `@RequestMapping(method = PATCH)` |
| `@DeleteMapping` | `@RequestMapping(method = DELETE)` |

Rewriting the example above with shortcuts:

```java
@RestController
@RequestMapping("/api/products")
public class ProductController {

    // GET /api/products
    @GetMapping
    public List<Product> list() {
        return productService.findAll();
    }

    // GET /api/products/{id}
    @GetMapping("/{id}")
    public Product getOne(@PathVariable Long id) {
        return productService.findById(id);
    }

    // POST /api/products
    @PostMapping
    public Product create(@RequestBody Product product) {
        return productService.save(product);
    }

    // PUT /api/products/{id}
    @PutMapping("/{id}")
    public Product replace(@PathVariable Long id,
                           @RequestBody Product product) {
        return productService.update(id, product);
    }

    // DELETE /api/products/{id}
    @DeleteMapping("/{id}")
    public void delete(@PathVariable Long id) {
        productService.delete(id);
    }
}
```

The class-level `@RequestMapping("/api/products")` acts as a prefix — every method path is appended to it. This keeps the base URL in one place and avoids repetition.

## A Realistic Worked Example

Below is a self-contained controller backed by an in-memory list. It compiles and runs with no extra dependencies beyond `spring-boot-starter-web`.

```java
package com.example.demo.controller;

import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.server.ResponseStatusException;

import java.util.*;
import java.util.concurrent.atomic.AtomicLong;

@RestController
@RequestMapping("/api/notes")
public class NoteController {

    record Note(Long id, String content) {}

    private final Map<Long, Note> store = new LinkedHashMap<>();
    private final AtomicLong seq = new AtomicLong(1);

    @GetMapping
    public Collection<Note> list() {
        return store.values();
    }

    @GetMapping("/{id}")
    public Note get(@PathVariable Long id) {
        Note note = store.get(id);
        if (note == null) throw new ResponseStatusException(HttpStatus.NOT_FOUND);
        return note;
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public Note create(@RequestBody Note note) {
        Long id = seq.getAndIncrement();
        Note saved = new Note(id, note.content());
        store.put(id, saved);
        return saved;
    }

    @DeleteMapping("/{id}")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    public void delete(@PathVariable Long id) {
        store.remove(id);
    }
}
```

Sending `POST /api/notes` with body `{"content":"Buy milk"}` returns `201 Created` with the saved note including its generated id.

## Narrowing by Consumes and Produces

You can restrict a mapping to specific media types:

```java
@PostMapping(
    consumes = "application/json",
    produces = "application/json"
)
public Product create(@RequestBody Product product) { ... }
```

Spring returns `415 Unsupported Media Type` if the request `Content-Type` does not match, and `406 Not Acceptable` if `Accept` does not match — useful for strict API contracts.

## Common Mistakes

- **Missing `@RequestMapping` prefix** — every method ends up at the root or its individual path with no shared base. Define the resource path at the class level.
- **Returning `null` from a `@GetMapping`** — Jackson serializes `null` as an empty response body with `200 OK`. Throw a `ResponseStatusException(HttpStatus.NOT_FOUND)` instead.
- **Overlapping mappings** — two methods with the same path and HTTP verb throw `AmbiguousRequestMappingException` at startup. Ensure each (path, method) combination is unique.
- **`@Controller` instead of `@RestController`** — forgetting `@ResponseBody` causes Spring MVC to look for a view template named after the return value and return a `500` or blank page.
- **Putting business logic in the controller** — controllers should delegate to a `@Service` layer; keep them thin.

`@RestController` combined with the HTTP-method shortcut annotations gives you a clean, readable way to declare every endpoint in your API — the class-level `@RequestMapping` defines the resource path and each method handles exactly one operation.
