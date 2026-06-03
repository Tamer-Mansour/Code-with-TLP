# Entity Relationships: One-to-Many and Many-to-Many

Real domains are graphs of related data: an author writes many books, a course enrolls many students, and a student takes many courses. Spring Data JPA maps these relationships to your object model with a handful of annotations. This lesson covers the two relationships you will reach for most often — **One-to-Many** and **Many-to-Many** — and how to model them correctly with JPA and Hibernate.

## The Owning Side and the Inverse Side

Every bidirectional relationship has an **owning side** (the entity whose table holds the foreign key) and an **inverse side** (mapped with `mappedBy`). Hibernate only persists the relationship from the owning side, so updating the inverse side alone changes nothing in the database.

| Relationship | FK lives in | Owning side | Inverse side |
|--------------|-------------|-------------|--------------|
| One-to-Many  | "many" table | `@ManyToOne` | `@OneToMany(mappedBy = ...)` |
| Many-to-Many | join table   | either `@ManyToMany` | `@ManyToMany(mappedBy = ...)` |

## One-to-Many: Author and Book

The foreign key belongs in the `book` table, so `Book` is the owning side.

```java
@Entity
public class Author {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String name;

    @OneToMany(mappedBy = "author", cascade = CascadeType.ALL, orphanRemoval = true)
    private List<Book> books = new ArrayList<>();

    // helper keeps both sides in sync
    public void addBook(Book book) {
        books.add(book);
        book.setAuthor(this);
    }
}

@Entity
public class Book {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String title;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "author_id")
    private Author author;
}
```

- `mappedBy = "author"` points to the field on the `Book` side that owns the FK.
- `cascade = CascadeType.ALL` propagates persist/remove operations to children.
- `orphanRemoval = true` deletes a `Book` when it is removed from the collection.
- `@ManyToOne` is **eager by default** — set it `LAZY` to avoid loading the parent on every query.

## Many-to-Many: Student and Course

A many-to-many relationship requires a join table. Define it explicitly with `@JoinTable`.

```java
@Entity
public class Student {
    @Id @GeneratedValue
    private Long id;

    @ManyToMany
    @JoinTable(
        name = "student_course",
        joinColumns = @JoinColumn(name = "student_id"),
        inverseJoinColumns = @JoinColumn(name = "course_id"))
    private Set<Course> courses = new HashSet<>();
}

@Entity
public class Course {
    @Id @GeneratedValue
    private Long id;

    @ManyToMany(mappedBy = "courses")
    private Set<Student> students = new HashSet<>();
}
```

The generated join table looks like this:

```sql
CREATE TABLE student_course (
    student_id BIGINT NOT NULL,
    course_id  BIGINT NOT NULL,
    PRIMARY KEY (student_id, course_id),
    FOREIGN KEY (student_id) REFERENCES student(id),
    FOREIGN KEY (course_id)  REFERENCES course(id)
);
```

**Tip:** when the link needs extra columns (e.g. `enrolled_at`, `grade`), do not use `@ManyToMany`. Promote the join table to a real entity with two `@ManyToOne` associations instead.

## Common Mistakes and Best Practices

- **Use `Set`, not `List`, for `@ManyToMany`.** A `List` triggers Hibernate to delete and re-insert all rows on any change; a `Set` updates only what changed.
- **Always set `FetchType.LAZY` on collections** (it is the default for `@OneToMany`/`@ManyToMany`) and fetch eagerly per-query with `JOIN FETCH` when needed.
- **Keep both sides in sync** with helper methods. Setting only the inverse side leaves the FK null.
- **Avoid infinite loops** in `toString()`, `equals()`, and JSON serialization. Use `@JsonManagedReference`/`@JsonBackReference` or DTOs to break the cycle.
- **Watch the N+1 problem** — iterating a lazy collection in a loop fires one query per parent. Solve it with `@EntityGraph` or a fetch join.

## Summary

Model the FK side as `@ManyToOne` (owning) and the collection side as `@OneToMany(mappedBy=...)`; use `@ManyToMany` with `@JoinTable` and `Set` for simple links, and a join entity when the relationship carries its own data.
