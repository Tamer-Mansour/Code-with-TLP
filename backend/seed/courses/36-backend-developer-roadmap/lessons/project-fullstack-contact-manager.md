# Project: Full-Stack Contact Manager

## Overview

In this project you'll build a **Full-Stack Contact Manager**: a Spring Boot REST API backed by MySQL, plus a plain HTML/CSS/JavaScript frontend that talks to it with `fetch`. The user can create, list, edit, and delete contacts (name, email, phone) from a web page — no manual SQL, no page reloads.

This is your first time wiring every layer together: a browser UI calls a JSON API, the API persists to a relational database, and the response flows back to update the page. The layered shape (entity → repository → service → controller, plus a static frontend) is the backbone of nearly every web application you'll build from here on.

## Learning Objectives

By the end of this project you will be able to:

- Scaffold a Spring Boot project with Web, JPA, and the MySQL driver.
- Map a Java class to a database table with JPA annotations.
- Expose CRUD endpoints with `@RestController` and the correct HTTP verbs.
- Persist data using a Spring Data `JpaRepository` (no hand-written SQL).
- Return proper status codes (`200`, `201`, `404`) and validate input.
- Consume the API from the browser with the **Fetch API** and `async/await`.
- Handle CORS so a static page can call your API during development.

## Prerequisites & Setup

You need:

- **JDK 17+** (`java -version` reports 17 or higher)
- **MySQL 8** running locally (`mysql --version`)
- **Maven** (or the bundled `mvnw` wrapper)

Generate a project from [start.spring.io](https://start.spring.io) with dependencies **Spring Web**, **Spring Data JPA**, and **MySQL Driver**, then create the database:

```sql
CREATE DATABASE IF NOT EXISTS contact_manager;
```

Configure `src/main/resources/application.properties`:

```properties
spring.datasource.url=jdbc:mysql://localhost:3306/contact_manager
spring.datasource.username=root
spring.datasource.password=your_password
spring.jpa.hibernate.ddl-auto=update
spring.jpa.show-sql=true
```

Run the API:

```bash
./mvnw spring-boot:run
# API now listening on http://localhost:8080
```

## Requirements

| # | Capability | Method | Endpoint |
|---|------------|--------|----------|
| 1 | List all contacts | `GET` | `/api/contacts` |
| 2 | Get one contact | `GET` | `/api/contacts/{id}` |
| 3 | Create a contact | `POST` | `/api/contacts` |
| 4 | Update a contact | `PUT` | `/api/contacts/{id}` |
| 5 | Delete a contact | `DELETE` | `/api/contacts/{id}` |

Rules:

- `name` and `email` are required; `email` must be unique and valid.
- A missing `id` returns `404 Not Found`, not a 500 crash.
- Creating returns `201 Created`; the frontend updates the list without reloading.

## Step-by-Step Tasks

### 1. Model the Contact entity

- [ ] Create a `Contact` class with `id`, `name`, `email`, `phone`.
- [ ] Annotate it as a JPA entity with a generated primary key.

```java
package com.tlp.contacts;

import jakarta.persistence.*;
import jakarta.validation.constraints.*;

@Entity
@Table(name = "contacts")
public class Contact {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @NotBlank
    private String name;

    @NotBlank @Email
    @Column(unique = true)
    private String email;

    private String phone;
    // getters and setters
}
```

### 2. Create the repository

- [ ] Extend `JpaRepository` to get CRUD methods for free.

```java
package com.tlp.contacts;

import org.springframework.data.jpa.repository.JpaRepository;

public interface ContactRepository
        extends JpaRepository<Contact, Long> { }
```

### 3. Build the REST controller

- [ ] Add `GET` (all + by id), `POST`, `PUT`, and `DELETE` handlers.
- [ ] Return `ResponseEntity` so you control the status code.

```java
package com.tlp.contacts;

import jakarta.validation.Valid;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.util.List;

@RestController
@RequestMapping("/api/contacts")
@CrossOrigin(origins = "*") // dev only
public class ContactController {

    private final ContactRepository repo;
    public ContactController(ContactRepository repo) { this.repo = repo; }

    @GetMapping
    public List<Contact> all() { return repo.findAll(); }

    @GetMapping("/{id}")
    public ResponseEntity<Contact> one(@PathVariable Long id) {
        return repo.findById(id)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    @PostMapping
    public ResponseEntity<Contact> create(@Valid @RequestBody Contact c) {
        Contact saved = repo.save(c);
        return ResponseEntity.status(201).body(saved);
    }

    @PutMapping("/{id}")
    public ResponseEntity<Contact> update(@PathVariable Long id,
                                          @Valid @RequestBody Contact c) {
        return repo.findById(id).map(existing -> {
            existing.setName(c.getName());
            existing.setEmail(c.getEmail());
            existing.setPhone(c.getPhone());
            return ResponseEntity.ok(repo.save(existing));
        }).orElse(ResponseEntity.notFound().build());
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> delete(@PathVariable Long id) {
        if (!repo.existsById(id)) return ResponseEntity.notFound().build();
        repo.deleteById(id);
        return ResponseEntity.noContent().build();
    }
}
```

### 4. Test the API before touching the UI

- [ ] Hit each endpoint with `curl` to confirm it works.

```bash
curl -X POST http://localhost:8080/api/contacts \
  -H "Content-Type: application/json" \
  -d '{"name":"Ada Lovelace","email":"ada@example.com","phone":"555-0101"}'

curl http://localhost:8080/api/contacts
```

### 5. Build the frontend page

- [ ] Create `index.html` with a form and a contacts list.
- [ ] Style it with a simple `style.css`.

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>Contact Manager</title>
  <link rel="stylesheet" href="style.css" />
</head>
<body>
  <h1>Contacts</h1>
  <form id="contact-form">
    <input id="name" placeholder="Name" required />
    <input id="email" type="email" placeholder="Email" required />
    <input id="phone" placeholder="Phone" />
    <button type="submit">Add</button>
  </form>
  <ul id="contact-list"></ul>
  <script src="app.js"></script>
</body>
</html>
```

### 6. Wire the UI to the API with fetch

- [ ] Load contacts on page load and render them.
- [ ] Submit the form with `POST`, then refresh the list.

```javascript
const API = "http://localhost:8080/api/contacts";

async function loadContacts() {
  const res = await fetch(API);
  const contacts = await res.json();
  const list = document.getElementById("contact-list");
  list.innerHTML = contacts
    .map((c) => `<li>${c.name} — ${c.email}
      <button onclick="removeContact(${c.id})">x</button></li>`)
    .join("");
}

document.getElementById("contact-form")
  .addEventListener("submit", async (e) => {
    e.preventDefault();
    await fetch(API, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        name: document.getElementById("name").value,
        email: document.getElementById("email").value,
        phone: document.getElementById("phone").value,
      }),
    });
    e.target.reset();
    loadContacts();
  });

async function removeContact(id) {
  await fetch(`${API}/${id}`, { method: "DELETE" });
  loadContacts();
}

loadContacts();
```

## Acceptance Criteria

- [ ] `./mvnw spring-boot:run` starts the API and auto-creates the `contacts` table.
- [ ] All five endpoints work and return the correct status codes (`200`, `201`, `204`, `404`).
- [ ] Data persists across restarts (it lives in MySQL, not memory).
- [ ] The web page lists contacts, adds one via the form, and deletes one — all without a full page reload.
- [ ] Creating a contact with a blank name/email or a malformed email is rejected with a `400`.
- [ ] Duplicate emails are not silently saved twice.
- [ ] The frontend successfully calls the API across origins (CORS configured).

## Stretch Challenges

1. Add an **edit** flow: clicking a contact loads it into the form and submits a `PUT`.
2. Add a **search box** that filters by name via `GET /api/contacts?name=` and a `findByNameContainingIgnoreCase` repository method.
3. Replace the entity in JSON responses with a **DTO** so you never expose the raw `id`/internal fields you don't want.
4. Add a global `@ControllerAdvice` exception handler that turns validation errors into clean JSON messages.
5. Serve the frontend from Spring's `src/main/resources/static` folder so the whole app runs on one origin (and you can drop the wildcard CORS).

## Hints

- `ddl-auto=update` is great for learning but unsafe in production — use migrations (Flyway) later in the roadmap.
- `@Valid` on the `@RequestBody` triggers the `@NotBlank`/`@Email` checks; without it, validation is silently skipped.
- A `404` should come from your code (the `orElse(...notFound())`), not from an unhandled exception that returns `500`.
- In `removeContact`, `DELETE` returns `204 No Content` — don't call `res.json()` on an empty body or `fetch` will throw.
- If the browser logs a CORS error, confirm `@CrossOrigin` is present and the API is actually running on `8080`.
