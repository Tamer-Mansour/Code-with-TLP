# Caching with Spring

Repeated reads of the same data — a product catalogue, a configuration lookup, a user profile — are one of the cheapest wins available in a backend. Spring's cache abstraction lets you add a transparent caching layer to any `@Service` method with a single annotation, then swap the underlying store (ConcurrentHashMap, Redis, Caffeine) without touching the business logic.

## Enabling the cache abstraction

Add `@EnableCaching` to your main application class (or any `@Configuration` class). Spring Boot will then wire up a `CacheManager` automatically.

```java
@SpringBootApplication
@EnableCaching
public class BookApplication {
    public static void main(String[] args) {
        SpringApplication.run(BookApplication.class, args);
    }
}
```

With no extra dependencies on the classpath, Spring Boot uses a `ConcurrentMapCacheManager` backed by plain `ConcurrentHashMap`. That is fine for development; in production you will replace it with Caffeine or Redis (see below).

## Core annotations

| Annotation        | What it does                                                                 |
|-------------------|------------------------------------------------------------------------------|
| `@Cacheable`      | Returns the cached value if present; otherwise runs the method and stores the result. |
| `@CachePut`       | Always runs the method and updates the cache — useful after a write/update.  |
| `@CacheEvict`     | Removes one entry (or all entries) from the cache — useful after a delete.   |
| `@Caching`        | Groups multiple cache annotations on one method.                             |

## A realistic service example

```java
@Service
@RequiredArgsConstructor
public class BookService {

    private final BookRepository bookRepository;

    // Cache the result; key defaults to the method argument (bookId).
    @Cacheable(value = "books", key = "#bookId")
    public BookDto findById(Long bookId) {
        return bookRepository.findById(bookId)
                .map(BookDto::from)
                .orElseThrow(() -> new EntityNotFoundException("Book not found: " + bookId));
    }

    // Write operation: always execute AND refresh the cache entry.
    @CachePut(value = "books", key = "#result.id")
    public BookDto update(Long bookId, UpdateBookRequest req) {
        Book book = bookRepository.findById(bookId)
                .orElseThrow(() -> new EntityNotFoundException("Book not found: " + bookId));
        book.setTitle(req.title());
        book.setAuthor(req.author());
        return BookDto.from(bookRepository.save(book));
    }

    // Delete operation: evict the single entry so stale data is not served.
    @CacheEvict(value = "books", key = "#bookId")
    public void delete(Long bookId) {
        bookRepository.deleteById(bookId);
    }

    // Evict the entire cache (e.g. after a bulk import).
    @CacheEvict(value = "books", allEntries = true)
    public void evictAll() { }
}
```

`key` is a Spring Expression Language (SpEL) expression. `#bookId` refers to the method parameter; `#result` refers to the return value (only valid in `@CachePut`).

## Swapping to Caffeine (recommended for single-node production)

Add the dependency:

```xml
<dependency>
    <groupId>com.github.ben-manes.caffeine</groupId>
    <artifactId>caffeine</artifactId>
</dependency>
```

Configure cache behaviour in `application.properties` (or `.yml`):

```properties
spring.cache.type=caffeine
spring.cache.caffeine.spec=maximumSize=500,expireAfterWrite=10m
```

Spring Boot auto-detects Caffeine and switches the `CacheManager` automatically — no Java config needed for this common case.

## Swapping to Redis (for distributed/multi-node deployments)

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-data-redis</artifactId>
</dependency>
```

```properties
spring.cache.type=redis
spring.data.redis.host=localhost
spring.data.redis.port=6379
# Optional: set a default TTL for all Redis caches
spring.cache.redis.time-to-live=600000
```

With Redis, cached objects must be `Serializable` (or you must configure a `RedisSerializer`). Use `implements Serializable` on your DTOs, or configure a `Jackson2JsonRedisSerializer`.

## Common mistakes and best practices

- **Caching `void` methods.** `@Cacheable` on a void method stores `null` and gives you nothing. Use `@CacheEvict` for side-effecting methods instead.
- **Self-invocation.** Calling a `@Cacheable` method from the same bean bypasses the proxy and hits the database every time. Inject the bean into itself or move the method to a separate service.
- **Forgetting `@CacheEvict` after writes.** Stale data accumulates quickly. Always pair a `@CachePut` or `@CacheEvict` with every create/update/delete path.
- **No TTL in production.** `ConcurrentMapCacheManager` never expires entries. Always configure `expireAfterWrite` (Caffeine) or `time-to-live` (Redis) in a production profile.
- **Caching large collections without a key.** If `findAll()` is cached under a single key, one new record invalidates the whole entry. Cache individual entities by ID and paginate heavy list queries instead.

## Summary

Spring's cache abstraction adds transparent read-through and write-through caching to any Spring bean with three annotations (`@Cacheable`, `@CachePut`, `@CacheEvict`) and zero changes to calling code. Choose Caffeine for single-node speed and Redis when you need a shared, distributed store.
