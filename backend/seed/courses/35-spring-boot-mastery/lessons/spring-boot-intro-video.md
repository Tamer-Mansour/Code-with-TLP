# Video: Spring Boot Crash Course

This video gives you a hands-on, end-to-end tour of Spring Boot 3 — from project creation to a running REST API — in a single focused session.

## What you'll learn

- Bootstrap a project with **Spring Initializr** (Maven, Java 17, `spring-boot-starter-web`)
- Understand auto-configuration and the `@SpringBootApplication` entry point
- Build a REST controller using `@RestController`, `@GetMapping`, and `@PostMapping`
- Wire dependencies with Spring's IoC container (`@Service`, `@Repository`, `@Autowired`)
- Externalize configuration via `application.properties` / `application.yml`
- Run and test the app with the embedded Tomcat server and `curl` / Postman

## Key takeaways

- Spring Boot removes boilerplate by auto-configuring sensible defaults based on the classpath
- A single `main` method with `SpringApplication.run(...)` starts a fully embedded web server
- Profile-specific config files (`application-dev.properties`) make environment switching trivial
- The fat JAR produced by `mvn package` is self-contained and runs anywhere with `java -jar`

## Follow-along checklist

- [ ] Install JDK 17+ and confirm `java -version`
- [ ] Generate a project at [start.spring.io](https://start.spring.io) with the **Spring Web** dependency
- [ ] Run `mvn spring-boot:run` and hit `http://localhost:8080`
- [ ] Add one `@RestController` returning a JSON response
- [ ] Verify the response with `curl http://localhost:8080/api/hello`

The video link in this lesson opens a curated YouTube search featuring free, high-quality crash courses from channels like freeCodeCamp covering exactly this topic.
