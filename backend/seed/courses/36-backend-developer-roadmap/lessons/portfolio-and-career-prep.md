# Portfolio and Career Preparation

Finishing a technical roadmap is only the first step. Employers evaluate you on the work you can show them, how clearly you can explain it, and how well you fit their hiring process. This lesson turns the projects you built throughout this course into a compelling portfolio, and prepares you for the Java/Spring job search.

## What Belongs in a Backend Portfolio

A strong backend portfolio demonstrates depth, not quantity. Three well-documented projects beat ten half-finished ones.

| Project type | What it proves |
|---|---|
| REST API with authentication (JWT) | Spring Boot, security, layered architecture |
| Multi-table CRUD with MySQL | Schema design, relationships, JPA/Hibernate |
| Frontend-connected full-stack project | End-to-end thinking, CORS, JSON contracts |
| Open-source contribution or PR | Collaboration, reading unfamiliar code |

Every project in this course — the Student Management API, the Finance Tracker, and the Employee Database — qualifies as one of the rows above. Polish at least two of them.

## Structuring a Project Repository

Recruiters spend about 90 seconds on a repo. A consistent, professional layout makes every second count.

```
my-spring-api/
├── src/
│   ├── main/
│   │   ├── java/com/example/api/
│   │   │   ├── controller/
│   │   │   ├── service/
│   │   │   ├── repository/
│   │   │   └── model/
│   │   └── resources/
│   │       ├── application.properties
│   │       └── schema.sql
│   └── test/
│       └── java/com/example/api/
├── .gitignore
├── pom.xml
└── README.md
```

A good `README.md` includes: a one-paragraph description, a screenshot or API response example, a "Getting Started" section with exact commands, and a list of endpoints. Nothing else is required.

## Writing a Useful README

```markdown
## Getting Started

**Prerequisites:** Java 17, Maven 3.9, MySQL 8

```bash
# 1. Clone and enter the repo
git clone https://github.com/yourname/student-api.git
cd student-api

# 2. Create the database
mysql -u root -p -e "CREATE DATABASE student_db;"

# 3. Configure credentials (never commit real passwords)
cp src/main/resources/application.properties.example \
   src/main/resources/application.properties
# edit the file and fill in your DB password

# 4. Run
mvn spring-boot:run
```

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/students | List all students |
| POST | /api/students | Create a student |
| PUT | /api/students/{id} | Update a student |
| DELETE | /api/students/{id} | Delete a student |
```

Store real credentials only in `application-local.properties`, which must be in `.gitignore`. Provide an `.example` file with placeholder values so others can onboard without guessing.

```properties
# application.properties.example
spring.datasource.url=jdbc:mysql://localhost:3306/student_db
spring.datasource.username=root
spring.datasource.password=CHANGE_ME
spring.jpa.hibernate.ddl-auto=validate
```

## Preparing for Technical Interviews

Java/Spring backend interviews test three areas: language fundamentals, Spring concepts, and system thinking.

**Common Java questions to be ready for:**

- What is the difference between `HashMap` and `LinkedHashMap`?
- Explain `equals()` vs `==` for objects.
- What does `Optional` solve, and when should you avoid it?

**Common Spring Boot questions:**

- What is the Spring IoC container and how does dependency injection work?
- What is the difference between `@Component`, `@Service`, and `@Repository`?
- How does `@Transactional` work, and what happens if an exception is thrown inside a transactional method?

A crisp, practiced answer to "walk me through this project" is just as important as knowing the theory. Write a two-minute narrative for each portfolio project: the problem it solved, the decisions you made (e.g., why you chose a particular schema design), and what you would do differently.

## A Minimal Take-Home Test Pattern

Many companies send a take-home REST API challenge. Use this skeleton every time so you ship clean code quickly.

```java
// Typical take-home structure — adapt to the given domain
@RestController
@RequestMapping("/api/products")
@RequiredArgsConstructor
public class ProductController {

    private final ProductService productService;

    @GetMapping
    public List<ProductResponse> getAll() {
        return productService.findAll();
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public ProductResponse create(@RequestBody @Valid CreateProductRequest req) {
        return productService.create(req);
    }
}
```

Always add `@Valid` on request bodies, use a response DTO (not the entity directly), and include at least one unit test. These three habits separate candidates who pass the review from those who do not.

## Common Mistakes to Avoid

- **Exposing your entity as the API response.** Returning the JPA entity directly couples your API contract to your database schema. Use a dedicated response DTO.
- **No tests at all.** Even two or three `@SpringBootTest` integration tests show you understand testability.
- **Hardcoded credentials in the repo.** Recruiters run `git log` to see your history; a leaked password is an immediate disqualifier.
- **Dead links in your README.** Before every interview, clone your own repo from scratch in a fresh directory and follow your own instructions.

---

A polished repository, a clear README, and the ability to narrate your own decisions out loud are the three things that convert technical skill into job offers.
