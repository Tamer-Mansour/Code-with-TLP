# Component Scanning and Stereotype Annotations

Spring Boot wires your application together by detecting classes that carry special marker annotations and registering them as beans in the `ApplicationContext`. This mechanism is called **component scanning**, and the markers are the **stereotype annotations**.

## How Component Scanning Works

When you annotate your main class with `@SpringBootApplication`, it implicitly activates `@ComponentScan` on the same package (and all sub-packages). Spring Boot walks those packages at startup, inspects every class, and registers any class annotated with a stereotype as a Spring bean.

```java
@SpringBootApplication          // includes @ComponentScan on com.example.demo
public class DemoApplication {
    public static void main(String[] args) {
        SpringApplication.run(DemoApplication.class, args);
    }
}
```

All classes in `com.example.demo` and its sub-packages are candidates. Classes in sibling or parent packages are **not** scanned unless you add them explicitly.

## The Core Stereotype Annotations

| Annotation | Inherits from | Intended role |
|---|---|---|
| `@Component` | — | Generic Spring-managed bean |
| `@Service` | `@Component` | Business / domain logic layer |
| `@Repository` | `@Component` | Data-access layer; adds exception translation |
| `@Controller` | `@Component` | Spring MVC web layer (returns views) |
| `@RestController` | `@Controller` | REST API layer (adds `@ResponseBody`) |
| `@Configuration` | `@Component` | Bean-factory class; source of `@Bean` methods |

All four leaf annotations are composed on top of `@Component`, so they are all picked up by the component scan. The different names communicate architectural intent and, in the case of `@Repository`, activate Spring's persistence-exception translation.

## A Realistic Three-Layer Example

**Repository** — data access:

```java
package com.example.demo.repository;

import com.example.demo.model.Product;
import org.springframework.stereotype.Repository;
import java.util.List;
import java.util.ArrayList;

@Repository
public class ProductRepository {

    // In a real app this would be a JpaRepository;
    // kept simple to focus on component scanning.
    private final List<Product> store = new ArrayList<>();

    public void save(Product product) {
        store.add(product);
    }

    public List<Product> findAll() {
        return List.copyOf(store);
    }
}
```

**Service** — business logic, depends on the repository:

```java
package com.example.demo.service;

import com.example.demo.model.Product;
import com.example.demo.repository.ProductRepository;
import org.springframework.stereotype.Service;
import java.util.List;

@Service
public class ProductService {

    private final ProductRepository repository;

    // Constructor injection — the recommended approach
    public ProductService(ProductRepository repository) {
        this.repository = repository;
    }

    public void addProduct(Product product) {
        repository.save(product);
    }

    public List<Product> listProducts() {
        return repository.findAll();
    }
}
```

**Controller** — HTTP layer, depends on the service:

```java
package com.example.demo.controller;

import com.example.demo.model.Product;
import com.example.demo.service.ProductService;
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
    public List<Product> all() {
        return service.listProducts();
    }

    @PostMapping
    public void add(@RequestBody Product product) {
        service.addProduct(product);
    }
}
```

Spring scans all three classes, constructs `ProductRepository` first (no dependencies), then `ProductService` (injects the repository), then `ProductController` (injects the service).

## Customising the Scan Scope

You can override the base package or exclude specific types when you need finer control:

```java
@SpringBootApplication
@ComponentScan(
    basePackages = {"com.example.demo", "com.shared.utils"},
    excludeFilters = @ComponentScan.Filter(
        type  = FilterType.ANNOTATION,
        value = Repository.class   // exclude all @Repository beans here
    )
)
public class DemoApplication { ... }
```

## Common Mistakes

- **Wrong package placement** — placing a class outside the main class's package (or its sub-packages) means it is never scanned. Fix: move the class inside the scanned tree, or add its package to `basePackages`.
- **Using `@Component` everywhere** — works, but hurts readability and loses `@Repository`'s exception translation. Use the most specific stereotype that matches the layer.
- **Field injection instead of constructor injection** — `@Autowired` on a field compiles but makes the bean hard to test. Prefer constructor injection; Spring wires it automatically when there is exactly one constructor.
- **Multiple `@ComponentScan` declarations** — having `@ComponentScan` on both `@SpringBootApplication` and another `@Configuration` class can cause beans to be scanned twice or from unintended packages. Use one definitive scan configuration.

## Summary

Component scanning, driven by `@SpringBootApplication`, automatically discovers and registers beans annotated with `@Component`, `@Service`, `@Repository`, `@RestController`, or `@Configuration`. Choose the stereotype that matches the architectural layer — the names document intent, and some annotations carry extra behavior beyond mere registration.
