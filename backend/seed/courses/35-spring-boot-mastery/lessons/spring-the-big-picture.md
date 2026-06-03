# Spring: The Big Picture

Before writing a single line of Spring Boot code it is worth stepping back to understand what "Spring" actually means — because the name covers an entire ecosystem, not just one library.

## What Is the Spring Framework?

The **Spring Framework** is an open-source Java application framework first released in 2003 by Rod Johnson. Its central idea is simple but powerful: the framework, not your code, is responsible for creating and wiring together the objects your application needs. This concept is called **Inversion of Control (IoC)**, and the component that manages it is called the **IoC container** (or **Application Context**).

Every Spring application is built around beans — plain Java objects whose lifecycle (creation, wiring, destruction) is managed by the container. You declare what you need; Spring figures out how to deliver it.

```java
// A plain Java class becomes a Spring-managed bean with one annotation
@Service
public class OrderService {

    private final PaymentGateway paymentGateway;

    // Spring sees the constructor and injects PaymentGateway automatically
    public OrderService(PaymentGateway paymentGateway) {
        this.paymentGateway = paymentGateway;
    }

    public void placeOrder(Order order) {
        paymentGateway.charge(order.total());
    }
}
```

You never call `new OrderService(...)` in your code. Spring resolves `PaymentGateway`, constructs both objects, and hands you a wired-up `OrderService`. This is **Dependency Injection (DI)** in practice.

## The Spring Ecosystem

"Spring" is an umbrella brand for many specialized projects:

| Project | What it solves |
|---|---|
| **Spring Framework** | IoC container, DI, AOP, transaction management |
| **Spring Boot** | Auto-configuration, embedded server, production defaults |
| **Spring Data** | Repositories and query abstraction over JPA, MongoDB, Redis, etc. |
| **Spring Security** | Authentication, authorization, OAuth 2, JWT |
| **Spring MVC / Spring Web** | HTTP layer — controllers, request mapping, REST support |
| **Spring Batch** | Chunk-oriented batch processing |
| **Spring Cloud** | Distributed systems, service discovery, config servers |

In this course you will use **Spring Boot 3** as the entry point, which automatically pulls in Spring Framework 6, Spring MVC, Spring Data JPA, and Spring Security as you add starters to your `pom.xml`.

## How Spring MVC Handles a Request

When a browser or API client makes an HTTP request to a Spring Boot application, the request travels through a well-defined pipeline:

```
HTTP Request
    │
    ▼
DispatcherServlet  (front controller — one per app)
    │
    ▼
HandlerMapping     (which @Controller / @RestController handles this URL?)
    │
    ▼
HandlerAdapter     (invokes the matched method)
    │
    ▼
@RestController method  (your code runs here)
    │
    ▼
MessageConverter   (serializes the return value to JSON)
    │
    ▼
HTTP Response
```

A concrete controller looks like this:

```java
@RestController
@RequestMapping("/api/products")
public class ProductController {

    private final ProductService productService;

    public ProductController(ProductService productService) {
        this.productService = productService;
    }

    @GetMapping("/{id}")
    public ResponseEntity<Product> getProduct(@PathVariable Long id) {
        return productService.findById(id)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }
}
```

`DispatcherServlet` routes `GET /api/products/42` to `getProduct(42L)`. The return value is serialized to JSON by Jackson (included by default with the `spring-boot-starter-web` dependency).

## Why Not Just Use the Framework Directly?

Prior to Spring Boot (released in 2014), setting up a Spring application required:

- Writing XML files (or many `@Configuration` classes) for every bean
- Configuring an external servlet container (Tomcat, Jetty)
- Manually managing library versions to avoid conflicts

Spring Boot removes all of that friction through **auto-configuration**: it scans your classpath, detects what libraries are present, and applies sensible defaults automatically. Add `spring-boot-starter-web` and you instantly get an embedded Tomcat server, Jackson for JSON, and Spring MVC pre-wired — no XML, no deployment descriptor.

## Key Principles to Keep in Mind

- **Convention over configuration.** Spring Boot picks safe, tested defaults. Override them only when you have a reason.
- **Starter dependencies.** Each `spring-boot-starter-*` artifact bundles everything needed for a feature area, with compatible versions. Prefer starters over adding individual jars.
- **Fail fast.** The container validates bean wiring at startup. If a required dependency is missing, the application refuses to start and tells you exactly why.
- **Testing is a first-class concern.** Spring ships dedicated test slices (`@WebMvcTest`, `@DataJpaTest`, `@SpringBootTest`) that spin up only the layer you need.

## Common Mistake

A frequent beginner error is annotating a class with `@Component` (or a stereotype like `@Service`) but then instantiating it manually with `new`:

```java
// Wrong — Spring never manages this instance; DI won't work
OrderService svc = new OrderService(new PaymentGateway());
```

Always let Spring construct and inject your beans. If you find yourself writing `new SomeSpringBean()`, stop and inject it instead.

## Summary

The Spring Framework is a mature IoC container that manages object creation and wiring for you. Spring Boot builds on top of it with auto-configuration and embedded servers, letting you ship a production-ready REST API with almost zero boilerplate setup. Understanding this layered architecture — Framework at the core, Boot on top, specialized projects alongside — is the mental model every lesson in this course will reinforce.
