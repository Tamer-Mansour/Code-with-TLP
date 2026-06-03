# Project: Employee Database

## Overview

In this project you'll build an **Employee Database** as a small full-stack application. A **Spring Boot** REST API backed by **MySQL 8** stores employee records and their departments, and a lightweight **HTML + CSS + JavaScript** page lets you list, add, edit, and delete employees in the browser.

This is the capstone of the *Databases with MySQL* module. You'll move beyond raw JDBC and let **Spring Data JPA** generate SQL for you, model a real **one-to-many** relationship (a department has many employees), and expose clean CRUD endpoints. The vanilla-JS frontend keeps the focus on the API contract — the same contract any Angular or React client would consume later.

## Learning Objectives

By the end of this project you will be able to:

- Bootstrap a Spring Boot web project wired to MySQL 8.
- Map JPA `@Entity` classes to tables, including a `@ManyToOne` / `@OneToMany` relationship.
- Build CRUD REST endpoints with `@RestController` and Spring Data `JpaRepository`.
- Validate request bodies with Bean Validation (`@Valid`, `@NotBlank`, `@Email`).
- Return correct HTTP status codes (`200`, `201`, `204`, `404`).
- Consume your own API from the browser with `fetch` and render it into the DOM.

## Prerequisites & Setup

You need:

- **JDK 17+** (`java -version`)
- **MySQL 8** running locally (`mysql --version`)
- **Maven** (the bundled `./mvnw` wrapper is fine)

Generate the project from [start.spring.io](https://start.spring.io) with dependencies **Spring Web**, **Spring Data JPA**, **MySQL Driver**, and **Validation**, or run:

```bash
curl https://start.spring.io/starter.zip \
  -d dependencies=web,data-jpa,mysql,validation \
  -d javaVersion=17 -d type=maven-project \
  -d groupId=com.tlp -d artifactId=employee-db \
  -o employee-db.zip
unzip employee-db.zip && cd employee-db
```

Create the database, then configure the connection:

```sql
CREATE DATABASE IF NOT EXISTS employee_db;
```

```properties
# src/main/resources/application.properties
spring.datasource.url=jdbc:mysql://localhost:3306/employee_db
spring.datasource.username=root
spring.datasource.password=your_password
spring.jpa.hibernate.ddl-auto=update
spring.jpa.show-sql=true
```

```bash
./mvnw spring-boot:run   # app starts on http://localhost:8080
```

## Requirements

| # | Capability | Endpoint |
|---|-----------|----------|
| 1 | List all employees | `GET /api/employees` |
| 2 | Get one employee | `GET /api/employees/{id}` |
| 3 | Create an employee | `POST /api/employees` |
| 4 | Update an employee | `PUT /api/employees/{id}` |
| 5 | Delete an employee | `DELETE /api/employees/{id}` |
| 6 | List departments | `GET /api/departments` |

Rules:

- An employee has `firstName`, `lastName`, `email` (unique), `salary`, and belongs to one `Department`.
- A department has many employees (one-to-many).
- Invalid input returns `400`; a missing id returns `404`.
- `salary` is stored as `DECIMAL` and represented with `BigDecimal` in Java.

## Step-by-Step Tasks

### 1. Model the entities

- [ ] Create a `Department` entity with `id` and `name`.
- [ ] Create an `Employee` entity with a `@ManyToOne` link to `Department`.

```java
@Entity
public class Employee {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @NotBlank private String firstName;
    @NotBlank private String lastName;

    @Email @Column(unique = true)
    private String email;

    @Column(precision = 12, scale = 2)
    private BigDecimal salary;

    @ManyToOne(optional = false)
    @JoinColumn(name = "department_id")
    private Department department;
    // getters & setters
}
```

### 2. Create repositories

- [ ] Add a `JpaRepository` for each entity — no SQL needed.

```java
public interface EmployeeRepository extends JpaRepository<Employee, Long> { }
public interface DepartmentRepository extends JpaRepository<Department, Long> { }
```

### 3. Build the REST controller

- [ ] Inject the repository and expose the six endpoints.
- [ ] Use `ResponseEntity` so you control status codes.

```java
@RestController
@RequestMapping("/api/employees")
public class EmployeeController {
    private final EmployeeRepository repo;
    public EmployeeController(EmployeeRepository repo) { this.repo = repo; }

    @GetMapping
    public List<Employee> all() { return repo.findAll(); }

    @PostMapping
    public ResponseEntity<Employee> create(@Valid @RequestBody Employee e) {
        Employee saved = repo.save(e);
        return ResponseEntity.status(HttpStatus.CREATED).body(saved);
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> delete(@PathVariable Long id) {
        if (!repo.existsById(id)) return ResponseEntity.notFound().build();
        repo.deleteById(id);
        return ResponseEntity.noContent().build();
    }
}
```

### 4. Handle missing records

- [ ] Throw a 404 when a lookup fails instead of returning `null`.

```java
@GetMapping("/{id}")
public Employee one(@PathVariable Long id) {
    return repo.findById(id).orElseThrow(() ->
        new ResponseStatusException(HttpStatus.NOT_FOUND, "Employee not found"));
}
```

### 5. Seed a few departments

- [ ] Verify the table from MySQL and insert starter rows.

```sql
INSERT INTO department (name) VALUES ('Engineering'), ('Sales'), ('HR');
SELECT * FROM employee;
```

### 6. Build the browser UI

- [ ] Put `index.html` in `src/main/resources/static/` (served at `/`).
- [ ] Fetch the list on load and render a table; wire up the add form.

```html
<table id="emp-table"><tbody></tbody></table>
<form id="add-form">
  <input name="firstName" required>
  <input name="email" type="email" required>
  <button>Add</button>
</form>
```

```javascript
async function loadEmployees() {
  const res = await fetch('/api/employees');
  const employees = await res.json();
  const body = document.querySelector('#emp-table tbody');
  body.innerHTML = employees.map(e =>
    `<tr><td>${e.firstName} ${e.lastName}</td><td>${e.email}</td></tr>`
  ).join('');
}
loadEmployees();
```

## Acceptance Criteria

- [ ] The app starts and connects to MySQL; tables are created automatically.
- [ ] `POST /api/employees` returns `201` and a row appears in the `employee` table.
- [ ] `GET /api/employees` returns every employee as JSON, each with its department.
- [ ] `GET /api/employees/{missing}` returns `404`, not `500` or an empty body.
- [ ] `PUT` updates an existing record; `DELETE` returns `204` and removes the row.
- [ ] Posting a blank name or invalid email returns `400`.
- [ ] The `email` column rejects duplicates.
- [ ] The browser page lists employees and adding one through the form updates the table.

## Stretch Challenges

1. Add **pagination and sorting** with `findAll(Pageable)` and `?page=0&size=10&sort=lastName`.
2. Add a **search** derived query: `List<Employee> findByLastNameContainingIgnoreCase(String q)`.
3. Replace direct entity binding with **DTOs** so the API never leaks the entity shape.
4. Add a global `@RestControllerAdvice` that turns validation errors into a tidy JSON error body.
5. Write **integration tests** with `@SpringBootTest` and `MockMvc` against the CRUD endpoints.

## Hints

- Set `spring.jpa.hibernate.ddl-auto=update` while developing so schema changes apply automatically; switch to `validate` once stable.
- A `@ManyToOne` serializes the full department object — that's fine here. If you see infinite JSON loops, you've added a back-reference; annotate the `@OneToMany` side with `@JsonIgnore`.
- Test the API without the UI using `curl -X POST localhost:8080/api/employees -H "Content-Type: application/json" -d '{...}'` before debugging the frontend.
- `@Valid` only triggers validation when paired with the `validation` starter on the classpath — confirm it's in your `pom.xml`.
- Use `BigDecimal` for `salary`; map it with `precision`/`scale` so MySQL stores `DECIMAL(12,2)`.
