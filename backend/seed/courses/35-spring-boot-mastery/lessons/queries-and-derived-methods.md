# Derived Queries, JPQL, and @Query

Spring Data JPA gives you three complementary ways to fetch data from a `JpaRepository`: **derived query methods** (Spring writes the query from the method name), **JPQL** via `@Query` (object-oriented queries you write yourself), and **native SQL** when you need database-specific features. Knowing when to reach for each keeps repositories clean and predictable.

## Derived query methods

Spring parses the method name and generates the query for you. Start with a verb keyword (`findBy`, `readBy`, `getBy`, `countBy`, `existsBy`, `deleteBy`), then chain properties and conditions.

```java
public interface BookRepository extends JpaRepository<Book, Long> {

    List<Book> findByTitle(String title);

    List<Book> findByAuthorNameAndPublishedYearGreaterThan(String name, int year);

    List<Book> findByTitleContainingIgnoreCase(String fragment);

    Optional<Book> findFirstByOrderByPublishedYearDesc();

    boolean existsByIsbn(String isbn);

    long countByAuthorName(String name);
}
```

Note `findByAuthorName` traverses the relationship `Book.author.name`. Common keywords:

| Keyword | Meaning | Example |
| --- | --- | --- |
| `And` / `Or` | Combine conditions | `findByTitleAndIsbn` |
| `GreaterThan` / `LessThan` | Range | `findByPriceGreaterThan` |
| `Between` | Inclusive range | `findByPublishedYearBetween` |
| `Containing` / `StartingWith` | LIKE matching | `findByTitleContaining` |
| `In` | Membership | `findByIdIn` |
| `IgnoreCase` | Case-insensitive | `findByTitleIgnoreCase` |
| `OrderBy...Desc` | Sorting | `findByAuthorNameOrderByTitleAsc` |

Derived methods shine for simple lookups but get unreadable past three or four conditions—switch to `@Query` at that point.

## JPQL with @Query

JPQL queries against **entity names and fields**, not table and column names. Bind parameters by position (`?1`) or—preferably—by name with `@Param`.

```java
public interface BookRepository extends JpaRepository<Book, Long> {

    @Query("SELECT b FROM Book b WHERE b.author.name = :name AND b.publishedYear > :year")
    List<Book> search(@Param("name") String name, @Param("year") int year);

    @Query("SELECT new com.tlp.dto.BookSummary(b.title, b.author.name) " +
           "FROM Book b WHERE b.price < :max")
    List<BookSummary> findSummaries(@Param("max") BigDecimal max);
}
```

The second example uses a **constructor expression** to project straight into a DTO—great for read-only views. For data changes, mark the method `@Modifying`:

```java
@Modifying
@Transactional
@Query("UPDATE Book b SET b.price = b.price * :factor WHERE b.author.name = :name")
int applyPriceChange(@Param("name") String name, @Param("factor") BigDecimal factor);
```

## Native queries

When you need vendor-specific SQL (window functions, full-text search), set `nativeQuery = true`. You now write real **table/column names**:

```java
@Query(value = "SELECT * FROM books WHERE to_tsvector(title) @@ plainto_tsquery(:q)",
       nativeQuery = true)
List<Book> fullTextSearch(@Param("q") String q);
```

## Comparison

| Approach | Query style | Portable? | Best for |
| --- | --- | --- | --- |
| Derived method | Generated from name | Yes | Simple, readable lookups |
| `@Query` (JPQL) | Entity/field names | Yes | Complex conditions, joins, DTO projections |
| `@Query` native | Table/column names | No | DB-specific SQL |

## Common mistakes and best practices

- **Wrong property names** in derived methods fail loudly at startup—a good thing. Trust the error.
- Prefer **named parameters** (`:name`) over positional `?1`; they survive refactors.
- Always pair `@Modifying` with `@Transactional`; forgetting the transaction throws at runtime.
- After a `@Modifying` query, the persistence context can be stale—use `@Modifying(clearAutomatically = true)` if you re-read affected entities in the same transaction.
- Accept a `Pageable` parameter on any query method to add paging and sorting without changing the query.

## Summary

Use derived methods for simple finders, JPQL `@Query` for complex logic and DTO projections, and native queries only when you truly need database-specific SQL. Named parameters and `@Modifying`/`@Transactional` are the details that keep these queries correct.
