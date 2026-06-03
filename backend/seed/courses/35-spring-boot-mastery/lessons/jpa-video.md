# Video: Spring Data JPA and Hibernate

This video covers how Spring Data JPA sits on top of Hibernate to let you persist, query, and manage relational data in a Spring Boot 3 application with minimal boilerplate — from entity mapping to repository-driven CRUD and custom JPQL queries.

## What you'll learn

- Annotate a Java class as a JPA entity with `@Entity`, `@Table`, `@Id`, and `@GeneratedValue`
- Configure a datasource and Hibernate dialect in `application.properties` for H2 or PostgreSQL
- Extend `JpaRepository<T, ID>` to get full CRUD and pagination for free
- Write derived query methods (e.g. `findByEmailIgnoreCase`) and custom `@Query` JPQL statements
- Map one-to-many and many-to-one relationships with `@OneToMany` / `@ManyToOne` and control lazy vs eager loading
- Use `spring.jpa.hibernate.ddl-auto` to manage schema generation safely across environments

## Key takeaways

- Hibernate is the JPA provider; Spring Data JPA is the abstraction layer — you code to JPA interfaces, not Hibernate APIs directly
- Derived query methods are parsed at startup, so a typo becomes a compile-time-style error before the app runs
- Fetch type defaults (`LAZY` for collections, `EAGER` for single associations) strongly affect N+1 query problems — always profile with `spring.jpa.show-sql=true`
- `@Transactional` on a service method ensures a consistent unit of work; omitting it on write operations can silently skip persistence

## Follow-along checklist

- [ ] Add `spring-boot-starter-data-jpa` and an appropriate driver (e.g. `h2` or `postgresql`) to `pom.xml`
- [ ] Create an `@Entity` class with `@Id` and `@GeneratedValue(strategy = GenerationType.IDENTITY)`
- [ ] Create a `@Repository` interface that extends `JpaRepository<YourEntity, Long>`
- [ ] Set `spring.jpa.hibernate.ddl-auto=create-drop` in `application.properties` for local development
- [ ] Inject the repository into a `@Service` and call `save()`, `findById()`, and `findAll()`
- [ ] Add `spring.jpa.show-sql=true` and verify SQL output in the console

The video link in this lesson opens a curated YouTube search featuring free, high-quality tutorials from channels like freeCodeCamp covering Spring Data JPA and Hibernate with Spring Boot end-to-end.
