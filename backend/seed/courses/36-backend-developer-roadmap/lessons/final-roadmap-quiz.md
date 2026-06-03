# Final Quiz: Roadmap Review

Test your understanding of the full Backend Developer Roadmap — from toolchain setup and Java foundations through MySQL, HTML/CSS, JavaScript, Spring Boot, and the capstone career-readiness skills covered in Week 16. Each question has exactly one correct answer.

---

**Q1. The 16-week roadmap recommends completing Java Foundations (Weeks 2–5) and MySQL (Weeks 6–8) before touching Spring Boot. Which project is the designated capstone for the Java Foundations module?**

- [ ] Employee Database — a multi-table MySQL schema populated with seed data
- [ ] Weather Dashboard — a JavaScript page calling the Open-Meteo API with `fetch`
- [x] Personal Finance Tracker — a console Java application that reads entries, calculates a running balance, and writes a summary report with `BufferedWriter`
- [ ] Full-Stack Contact Manager — a Spring Boot REST backend secured with JWT

---

**Q2. You run `curl "http://localhost:8080/api/hello"` and get back `Hello, World!`. You then open a browser page served from `http://localhost:5500` and call the same endpoint with `fetch`. The browser throws a CORS error. What is the minimal Spring Boot change that fixes this?**

- [ ] Switch the controller annotation from `@RestController` to `@Controller`
- [ ] Change the server port to `5500` in `application.properties`
- [ ] Return `ResponseEntity` instead of a plain `String`
- [x] Add `@CrossOrigin(origins = "http://localhost:5500")` to the controller, or configure `addCorsMappings` in a `WebMvcConfigurer` bean that allows `http://localhost:5500`

---

**Q3. A JWT returned by a Spring Boot login endpoint looks like `eyJ...header.eyJ...payload.signature`. What is true about the payload portion?**

- [ ] It is AES-encrypted, so only the server can read the user's claims
- [ ] It is compressed with GZIP but not encoded
- [x] It is Base64URL-encoded but not encrypted — anyone can decode and read the claims, so passwords or secrets must never be stored there
- [ ] It is signed with the user's password, allowing the client to verify it independently

---

**Q4. Which `.gitignore` entry correctly prevents the Maven build output directory from being committed to a Java project?**

- [ ] `*.java`
- [ ] `src/`
- [x] `target/`
- [ ] `pom.xml`

---

**Q5. After graduating from this roadmap, the recommended next course is Spring Boot Mastery. Which four topics does the roadmap explicitly defer to that course?**

- [ ] Spring MVC, Thymeleaf, JDBC Template, and Spring Batch
- [x] Spring Data JPA, Spring Security, Docker, and microservices
- [ ] REST controllers, JSON serialization, CORS configuration, and JWT
- [ ] MySQL schema design, HikariCP connection pooling, Flyway migrations, and Hibernate

---

**Q6. In the `fetch` + Spring Boot full-stack pattern taught in this course, what does the browser do before sending a cross-origin `POST` request with `Content-Type: application/json`?**

- [ ] It encodes the body as `application/x-www-form-urlencoded` to avoid the preflight
- [ ] It caches the CORS policy from the previous response and skips the check
- [ ] It opens a WebSocket handshake to verify the server supports JSON
- [x] It automatically sends a preflight `OPTIONS` request to ask the server whether the actual request is permitted, before sending the real `POST`

---

**Q7. Examine the following commit-message convention used throughout this course:**

```bash
git commit -m "feat: add GET /api/contacts endpoint"
git commit -m "fix: handle null pointer in ContactService.findById"
git commit -m "chore: add .gitignore for Java and IntelliJ"
```

What is the name of this convention, and what is the correct type prefix for a commit that only changes documentation?**

- [ ] Semantic Versioning; the type prefix is `ver`
- [ ] GitHub Flow; the type prefix is `update`
- [x] Conventional Commits; the type prefix is `docs`
- [ ] Keep a Changelog; the type prefix is `changed`

---

**Q8. The following Spring Boot controller method is intended to return a JSON object when `GET /api/greeting?name=TLP` is called. What is wrong with it?**

```java
@Controller
public class GreetingController {

    @GetMapping("/api/greeting")
    public Greeting greeting(@RequestParam(defaultValue = "World") String name) {
        return new Greeting("Hello, " + name + "!");
    }
}

record Greeting(String message) {}
```

- [ ] `@GetMapping` cannot be used without `@RequestMapping` on the class
- [ ] Java records cannot be returned from controller methods
- [ ] `@RequestParam` requires the parameter name to match the method parameter exactly; `defaultValue` is not valid
- [x] The class is annotated with `@Controller` instead of `@RestController`, so Spring tries to resolve a view named after the return value instead of serializing it to JSON

---

**Q9. A student has completed the capstone project and wants to prepare their GitHub profile for job applications. According to the course's career-readiness guidance, which of the following practices best demonstrates professional Git hygiene to a potential employer?**

- [ ] Squash all commits into a single commit before pushing, so the history is clean
- [ ] Keep the repository private until the project is 100% finished
- [x] Use feature branches for each piece of work, open pull requests to merge into `main`, write descriptive Conventional Commit messages, and include a `README.md` that explains how to run the project
- [ ] Tag every commit with a version number and push tags to the remote before any merge

---

**Q10. Which of the following accurately describes the difference between `@GetMapping`, `@PostMapping`, `@PutMapping`, and `@DeleteMapping` in a Spring Boot REST controller?**

| Annotation | HTTP Method | Typical use in a CRUD API |
|---|---|---|
| `@GetMapping` | GET | Read / list resources |
| `@PostMapping` | POST | Create a new resource |
| `@PutMapping` | PUT | Replace an existing resource |
| `@DeleteMapping` | DELETE | Remove a resource |

- [ ] All four annotations are functionally identical; the HTTP method is determined by the client, not the annotation
- [ ] `@PostMapping` and `@PutMapping` both create resources; the difference is only semantic
- [ ] `@GetMapping` can also receive a request body, which is the correct way to filter large result sets
- [x] Each annotation binds the method to one specific HTTP verb, and the table above reflects the standard REST semantics used throughout this course
