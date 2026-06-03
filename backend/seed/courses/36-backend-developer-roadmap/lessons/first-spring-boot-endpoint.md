# Your First Spring Boot Endpoint

You've set up your tools — now let's make the backend actually *respond*. In this lesson you'll build a tiny Spring Boot application that exposes one HTTP endpoint and returns data to the browser. This is the "Hello, World" of backend development, and it introduces the core building block you'll use for everything else: the **REST controller**.

## What is an endpoint?

An **endpoint** is a URL that your server listens on. When a client (a browser, mobile app, or another service) sends an HTTP request to that URL, your code runs and sends back a response.

| Term | Meaning | Example |
|------|---------|---------|
| Endpoint | A URL + HTTP method your app handles | `GET /api/hello` |
| HTTP method | The action being requested | `GET`, `POST`, `PUT`, `DELETE` |
| Controller | A Java class that maps requests to methods | `HelloController` |
| Response body | The data sent back | `"Hello, TLP!"` or JSON |

Spring Boot uses **annotations** (lines starting with `@`) to wire all this together so you don't write boilerplate networking code.

## The minimal application

A Spring Boot app needs one class with a `main` method and the `@SpringBootApplication` annotation. This starts an embedded Tomcat web server (no separate install needed).

```java
package com.tlp.demo;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class DemoApplication {
    public static void main(String[] args) {
        SpringApplication.run(DemoApplication.class, args);
    }
}
```

## Adding your first endpoint

Create a controller. The `@RestController` annotation tells Spring this class handles web requests and returns the data directly (not a web page). `@GetMapping` binds a method to a `GET` request at a path.

```java
package com.tlp.demo;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class HelloController {

    @GetMapping("/api/hello")
    public String hello(@RequestParam(defaultValue = "World") String name) {
        return "Hello, " + name + "!";
    }
}
```

That's it. Spring scans your classes, finds the controller, and registers the route automatically.

## Run it and test

From the project root, start the app:

```bash
./mvnw spring-boot:run
```

By default the server listens on port **8080**. Open your browser or use `curl`:

```bash
curl "http://localhost:8080/api/hello"
# Hello, World!

curl "http://localhost:8080/api/hello?name=TLP"
# Hello, TLP!
```

The `?name=TLP` part is a **query parameter**, captured by `@RequestParam`.

## Returning JSON

Real APIs return structured data, not plain strings. If a controller method returns an object, Spring automatically serializes it to JSON.

```java
@GetMapping("/api/greeting")
public Greeting greeting(@RequestParam(defaultValue = "World") String name) {
    return new Greeting("Hello, " + name + "!");
}

record Greeting(String message) {}
```

Calling `GET /api/greeting?name=TLP` now returns:

```json
{ "message": "Hello, TLP!" }
```

## Common mistakes and best practices

- **Wrong annotation:** Using `@Controller` instead of `@RestController` makes Spring try to find an HTML view named after your return string — you'll get a 404 or error. Use `@RestController` for APIs.
- **Controller in the wrong package:** Spring only scans the package of `DemoApplication` and its sub-packages. Keep controllers under that root package (e.g. `com.tlp.demo`).
- **Port already in use:** If 8080 is busy, set a different port in `src/main/resources/application.properties`:

```properties
server.port=8081
```

- **Prefix API routes** with `/api/...` so they're easy to distinguish from front-end pages later.
- **Stick to `GET`** for read-only data; you'll learn `POST` for creating data in a later lesson.

## Summary

You created a Spring Boot app, added a `@RestController` with a `@GetMapping` endpoint, ran it on an embedded server, and returned both plain text and JSON. This request-to-method mapping is the foundation of every Spring backend you'll build next.
