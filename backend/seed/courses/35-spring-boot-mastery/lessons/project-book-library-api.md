# Project: Book Library API

## Overview

In this capstone project for the **Data Persistence with Spring Data JPA** module, you'll build a production-style **Book Library REST API**. It lets clients manage a catalog of books and the authors who wrote them, with full CRUD operations, validation, pagination, and a one-to-many relationship persisted to a real database.

This project matters because nearly every backend role expects you to model entities, map relationships, expose clean REST endpoints, and let Spring Data JPA generate the SQL for you. You'll wire together everything from this module — `@Entity` mappings, repositories, derived queries, DTOs, and exception handling — into a coherent, testable service.

## Learning Objectives

By the end of this project you will be able to:

- Model a one-to-many relationship (`Author` → `Book`) with JPA annotations.
- Build `JpaRepository` interfaces and add derived + custom `@Query` methods.
- Expose RESTful endpoints with `@RestController` and correct HTTP semantics.
- Validate request bodies with Jakarta Bean Validation and map entities to DTOs.
- Add pagination and sorting using Spring Data's `Pageable`.
- Handle errors centrally with `@RestControllerAdvice`.

## Prerequisites & Setup

- JDK 17+, Maven 3.8+, and an IDE (IntelliJ IDEA or VS Code).
- Basic familiarity with REST and HTTP from earlier modules.

Generate a starter with Spring Initializr:

```bash
curl https://start.spring.io/starter.zip \
  -d type=maven-project \
  -d javaVersion=17 \
  -d bootVersion=3.3.4 \
  -d dependencies=web,data-jpa,validation,h2 \
  -d groupId=com.codewithtlp \
  -d artifactId=book-library \
  -d packageName=com.codewithtlp.library \
  -o book-library.zip
```

Unzip it, then configure the in-memory database in `src/main/resources/application.properties`:

```properties
spring.datasource.url=jdbc:h2:mem:library
spring.jpa.hibernate.ddl-auto=update
spring.jpa.show-sql=true
spring.h2.console.enabled=true
```

Run it with `./mvnw spring-boot:run` and confirm the H2 console at `http://localhost:8080/h2-console`.

## Requirements

The API must support managing **authors** and **books**:

| Method & Path | Purpose |
|---|---|
| `POST /api/authors` | Create an author |
| `GET /api/authors/{id}` | Get one author |
| `POST /api/books` | Create a book linked to an author |
| `GET /api/books` | List books (paginated, sortable) |
| `GET /api/books/{id}` | Get one book |
| `PUT /api/books/{id}` | Update a book |
| `DELETE /api/books/{id}` | Delete a book |
| `GET /api/books/search?title=...` | Find books by title fragment |

- A book belongs to exactly one author; an author has many books.
- Invalid input returns `400` with field-level messages; missing resources return `404`.

## Step-by-Step Tasks

### 1. Model the entities

- [ ] Create `Author` with `id`, `name`, and a `@OneToMany` list of books.
- [ ] Create `Book` with `id`, `title`, `isbn`, `publishedYear`, and a `@ManyToOne` author.

```java
@Entity
public class Author {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @NotBlank
    private String name;

    @OneToMany(mappedBy = "author", cascade = CascadeType.ALL, orphanRemoval = true)
    private List<Book> books = new ArrayList<>();
    // getters / setters
}

@Entity
public class Book {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @NotBlank
    private String title;

    @Column(unique = true)
    private String isbn;

    private Integer publishedYear;

    @ManyToOne(optional = false)
    @JoinColumn(name = "author_id")
    private Author author;
    // getters / setters
}
```

### 2. Create repositories

- [ ] Add `AuthorRepository extends JpaRepository<Author, Long>`.
- [ ] Add `BookRepository` with a derived query and a custom `@Query`.

```java
public interface BookRepository extends JpaRepository<Book, Long> {
    Page<Book> findByTitleContainingIgnoreCase(String title, Pageable pageable);

    @Query("select b from Book b where b.author.id = :authorId")
    List<Book> findByAuthor(@Param("authorId") Long authorId);
}
```

### 3. Define request/response DTOs

- [ ] Create `BookRequest` (with validation) and `BookResponse`.
- [ ] Never expose entities directly — map in the service layer.

```java
public record BookRequest(
    @NotBlank String title,
    String isbn,
    @Min(1450) Integer publishedYear,
    @NotNull Long authorId) {}

public record BookResponse(Long id, String title, String isbn,
                           Integer publishedYear, String authorName) {}
```

### 4. Build the service layer

- [ ] Create `BookService` that loads the `Author`, builds the `Book`, and saves it.
- [ ] Throw a custom `ResourceNotFoundException` when an id is missing.

```java
@Service
public class BookService {
    private final BookRepository books;
    private final AuthorRepository authors;
    // constructor injection

    public BookResponse create(BookRequest req) {
        Author author = authors.findById(req.authorId())
            .orElseThrow(() -> new ResourceNotFoundException("Author", req.authorId()));
        Book book = new Book();
        book.setTitle(req.title());
        book.setIsbn(req.isbn());
        book.setPublishedYear(req.publishedYear());
        book.setAuthor(author);
        return toResponse(books.save(book));
    }
}
```

### 5. Expose the REST controller

- [ ] Map all endpoints from the Requirements table.
- [ ] Use `@Valid`, return `201 Created` on POST, and accept `Pageable`.

```java
@RestController
@RequestMapping("/api/books")
public class BookController {
    private final BookService service;

    @PostMapping
    public ResponseEntity<BookResponse> create(@Valid @RequestBody BookRequest req) {
        return ResponseEntity.status(HttpStatus.CREATED).body(service.create(req));
    }

    @GetMapping
    public Page<BookResponse> list(Pageable pageable) {
        return service.list(pageable);
    }
}
```

Clients can now page and sort: `GET /api/books?page=0&size=10&sort=title,asc`.

### 6. Add global error handling

- [ ] Create `@RestControllerAdvice` mapping `ResourceNotFoundException` → `404`.
- [ ] Map `MethodArgumentNotValidException` → `400` with field errors.

```java
@RestControllerAdvice
public class ApiExceptionHandler {
    @ExceptionHandler(ResourceNotFoundException.class)
    public ResponseEntity<Map<String, Object>> handleNotFound(ResourceNotFoundException ex) {
        return ResponseEntity.status(HttpStatus.NOT_FOUND)
            .body(Map.of("error", ex.getMessage()));
    }
}
```

## Acceptance Criteria

- [ ] App starts cleanly with `./mvnw spring-boot:run`.
- [ ] `POST /api/authors` and `POST /api/books` create rows visible in the H2 console.
- [ ] `POST /api/books` with a blank title returns `400` and a field error message.
- [ ] `POST /api/books` with an unknown `authorId` returns `404`.
- [ ] `GET /api/books?page=0&size=5&sort=title,asc` returns a paginated, sorted result.
- [ ] `GET /api/books/search?title=clean` matches case-insensitively.
- [ ] `PUT` updates an existing book; `DELETE` removes it and a follow-up `GET` returns `404`.
- [ ] No `@Entity` class is returned directly from any controller — only DTOs.

## Stretch Challenges

1. Swap H2 for **PostgreSQL** via Docker Compose and use **Flyway** migrations instead of `ddl-auto`.
2. Add a `Category` entity and model a **many-to-many** relationship with `Book`.
3. Add `@DataJpaTest` repository tests and `@WebMvcTest` controller tests with MockMvc.
4. Expose interactive docs with **springdoc-openapi** (`/swagger-ui.html`).
5. Add optimistic locking with a `@Version` field and handle the conflict as `409`.

## Hints

- Use `mappedBy` on the `@OneToMany` side so `Book.author_id` is the single foreign key — otherwise Hibernate creates a join table.
- Prefer constructor injection over `@Autowired` fields; it makes services trivially unit-testable.
- Spring Data binds `Pageable` from query params automatically — don't parse `page`/`size` yourself.
- A unique `isbn` constraint will throw `DataIntegrityViolationException` on duplicates; catch it in your advice and return `409`.
- Keep mapping logic (`toResponse`) in the service or a dedicated mapper, not in the controller.
