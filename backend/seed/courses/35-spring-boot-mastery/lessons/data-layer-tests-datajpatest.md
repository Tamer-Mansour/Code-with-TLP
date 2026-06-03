# Data Layer Tests with @DataJpaTest

Testing the data layer in isolation — without loading a full web context — keeps your test suite fast and focused. Spring Boot's `@DataJpaTest` slice annotation wires only the JPA-related beans: entities, repositories, Hibernate, and an in-memory database. Everything else (controllers, services, security) is left out.

## What @DataJpaTest does

- Scans for `@Entity` classes and Spring Data repositories.
- Configures an in-memory H2 database by default and creates the schema from your entity mappings.
- Wraps each test method in a transaction that is **rolled back automatically** at the end, so tests do not pollute each other.
- Does **not** load `@Service`, `@Component`, or `@Controller` beans.

## Adding the dependency

`spring-boot-starter-test` (included in every Spring Initializr project) already brings in H2, JUnit 5, and AssertJ. Nothing extra is required for basic `@DataJpaTest` usage.

```xml
<!-- pom.xml — already present in starter projects -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-test</artifactId>
    <scope>test</scope>
</dependency>
```

If H2 is not on the classpath, add it explicitly with `<scope>test</scope>`:

```xml
<dependency>
    <groupId>com.h2database</groupId>
    <artifactId>h2</artifactId>
    <scope>test</scope>
</dependency>
```

## A minimal example

Suppose you have a `Book` entity and a `BookRepository`:

```java
@Entity
public class Book {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private String title;
    private String isbn;
    // constructors, getters, setters …
}
```

```java
public interface BookRepository extends JpaRepository<Book, Long> {
    Optional<Book> findByIsbn(String isbn);
    List<Book> findByTitleContainingIgnoreCase(String keyword);
}
```

A `@DataJpaTest` class for these looks like:

```java
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.orm.jpa.DataJpaTest;

import java.util.Optional;

import static org.assertj.core.api.Assertions.assertThat;

@DataJpaTest
class BookRepositoryTest {

    @Autowired
    private BookRepository bookRepository;

    @Test
    void findByIsbn_returnsBook_whenIsbnExists() {
        Book book = new Book();
        book.setTitle("Effective Java");
        book.setIsbn("978-0134685991");
        bookRepository.save(book);

        Optional<Book> found = bookRepository.findByIsbn("978-0134685991");

        assertThat(found).isPresent();
        assertThat(found.get().getTitle()).isEqualTo("Effective Java");
    }

    @Test
    void findByTitleContainingIgnoreCase_returnsMatchingBooks() {
        Book b1 = new Book(); b1.setTitle("Spring in Action"); b1.setIsbn("111");
        Book b2 = new Book(); b2.setTitle("Spring Boot Up and Running"); b2.setIsbn("222");
        Book b3 = new Book(); b3.setTitle("Clean Code"); b3.setIsbn("333");
        bookRepository.saveAll(List.of(b1, b2, b3));

        List<Book> results = bookRepository.findByTitleContainingIgnoreCase("spring");

        assertThat(results).hasSize(2)
                .extracting(Book::getTitle)
                .containsExactlyInAnyOrder("Spring in Action", "Spring Boot Up and Running");
    }
}
```

Each test saves data, asserts, and then the transaction rolls back — the next test starts with an empty schema.

## Using TestEntityManager

`@DataJpaTest` also provides `TestEntityManager`, a test-friendly wrapper around `EntityManager`. Use it to persist setup data and flush/clear the persistence context so you actually test database round-trips rather than first-level cache hits:

```java
@DataJpaTest
class BookRepositoryWithTemTest {

    @Autowired
    private TestEntityManager em;

    @Autowired
    private BookRepository bookRepository;

    @Test
    void findByIsbn_hitsDatabase_notCache() {
        Book book = new Book();
        book.setTitle("Domain-Driven Design");
        book.setIsbn("978-0321125217");
        em.persistAndFlush(book);   // write to DB
        em.clear();                 // evict from first-level cache

        Optional<Book> found = bookRepository.findByIsbn("978-0321125217");

        assertThat(found).isPresent();
    }
}
```

Calling `em.clear()` after `persistAndFlush()` forces the repository to issue a real SQL `SELECT` instead of returning the cached entity — a subtle but important distinction.

## Key differences: @DataJpaTest vs @SpringBootTest

| Feature | `@DataJpaTest` | `@SpringBootTest` |
|---|---|---|
| Context loaded | JPA slice only | Full application context |
| Database | In-memory H2 by default | Configured datasource |
| Speed | Fast (seconds) | Slower (tens of seconds) |
| Auto rollback | Yes (per test) | No by default |
| Use when | Testing repositories and queries | Integration / end-to-end tests |

## Testing against the real database

If you need to run against your actual PostgreSQL or MySQL schema instead of H2, add `@AutoConfigureTestDatabase(replace = NONE)` and configure the datasource in `src/test/resources/application-test.properties`:

```java
@DataJpaTest
@AutoConfigureTestDatabase(replace = AutoConfigureTestDatabase.Replace.NONE)
class BookRepositoryRealDbTest { … }
```

```properties
# src/test/resources/application-test.properties
spring.datasource.url=jdbc:postgresql://localhost:5432/testdb
spring.datasource.username=test
spring.datasource.password=test
```

## Common mistakes and best practices

- **Do not autowire service beans.** They are not loaded; the test will fail to start. Test business logic in service-layer unit tests.
- **Use `em.persistAndFlush()` + `em.clear()` for setup data** when you want to confirm SQL is executed, not just cache reads.
- **Do not rely on auto-increment ID values** across tests; each run may produce different values depending on H2's sequence state.
- **Keep test data minimal.** Build only the fields your assertion actually cares about.
- **Name tests clearly** (`methodName_expectedBehavior_whenCondition`) so failures are self-documenting.

## Summary

`@DataJpaTest` gives you a fast, isolated slice test for your JPA repositories — automatic rollback, in-memory database, and `TestEntityManager` included. Use it to verify every custom query and derived method before wiring the data layer into a larger integration test.
