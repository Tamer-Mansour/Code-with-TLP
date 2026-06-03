# What Is a REST API?

A **REST API** (Representational State Transfer Application Programming Interface) is the standard contract your Spring backend uses to expose data and behaviour to any client — a browser, a mobile app, another service, or a command-line tool. Understanding REST before writing your first Spring controller will save you from designing awkward endpoints you'll have to undo later.

## The client-server model

Every REST call follows the same pattern: a **client** sends an **HTTP request** to a **server** URL; the server performs an action and returns an **HTTP response**. The client and server are fully decoupled — they share only this contract.

```
Client                          Server
------                          ------
GET /api/students/42  ------>   Look up student 42
                      <------   200 OK  { "id": 42, "name": "Sara" }
```

## HTTP methods map to CRUD operations

REST uses standard HTTP methods so the URL names a **resource** (a noun) while the method names the **action** (a verb).

| HTTP Method | CRUD   | Typical use                        |
|-------------|--------|------------------------------------|
| `GET`       | Read   | Fetch a resource or a list         |
| `POST`      | Create | Submit a new resource              |
| `PUT`       | Update | Replace an entire resource         |
| `PATCH`     | Update | Partially update a resource        |
| `DELETE`    | Delete | Remove a resource                  |

## Resource-oriented URLs

Resources are named as **plural nouns** in the path. IDs go in path variables, filters go in query parameters.

```
GET    /api/courses          → list all courses
GET    /api/courses/7        → fetch course with id 7
POST   /api/courses          → create a new course
PUT    /api/courses/7        → replace course 7 entirely
PATCH  /api/courses/7        → update one or more fields of course 7
DELETE /api/courses/7        → delete course 7
```

Avoid verbs in URLs (`/api/getCourses`, `/api/deleteCourse?id=7`). The HTTP method already carries that meaning.

## HTTP status codes

The server communicates outcome through a numeric status code, not just the body.

| Range | Meaning      | Common codes                                      |
|-------|--------------|---------------------------------------------------|
| 2xx   | Success      | `200 OK`, `201 Created`, `204 No Content`         |
| 3xx   | Redirect     | `301 Moved Permanently`, `304 Not Modified`       |
| 4xx   | Client error | `400 Bad Request`, `401 Unauthorized`, `404 Not Found` |
| 5xx   | Server error | `500 Internal Server Error`                       |

A well-designed API always returns the most precise code: `201` when a resource is created, `204` when a delete succeeds and there is nothing to return, `404` when the requested ID does not exist.

## JSON — the universal data format

REST APIs almost always exchange data as **JSON** (JavaScript Object Notation). It maps naturally to Java objects and is native to JavaScript.

```json
{
  "id": 7,
  "title": "Spring Boot Fundamentals",
  "level": "Beginner",
  "enrolledCount": 312
}
```

A list of resources is simply a JSON array:

```json
[
  { "id": 1, "title": "Java Foundations" },
  { "id": 7, "title": "Spring Boot Fundamentals" }
]
```

## A minimal Spring Boot REST controller

Here is a complete, compilable example of the concepts above wired into Spring Boot. You will build on this pattern throughout the rest of the course.

```java
package com.codewithTlp.courses;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.util.List;

@RestController
@RequestMapping("/api/courses")
public class CourseController {

    private final CourseRepository repo;

    public CourseController(CourseRepository repo) {
        this.repo = repo;
    }

    // GET /api/courses  → 200 OK + list
    @GetMapping
    public List<Course> getAll() {
        return repo.findAll();
    }

    // GET /api/courses/{id}  → 200 OK + course, or 404
    @GetMapping("/{id}")
    public ResponseEntity<Course> getById(@PathVariable Long id) {
        return repo.findById(id)
                   .map(ResponseEntity::ok)
                   .orElse(ResponseEntity.notFound().build());
    }

    // POST /api/courses  → 201 Created + saved course
    @PostMapping
    public ResponseEntity<Course> create(@RequestBody Course course) {
        Course saved = repo.save(course);
        return ResponseEntity.status(201).body(saved);
    }

    // DELETE /api/courses/{id}  → 204 No Content
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> delete(@PathVariable Long id) {
        repo.deleteById(id);
        return ResponseEntity.noContent().build();
    }
}
```

`@RestController` combines `@Controller` and `@ResponseBody`, so every return value is serialized to JSON automatically. `@RequestMapping` sets the base URL prefix for all methods in the class.

## Calling the API from JavaScript

The front end you built in earlier modules can consume this endpoint directly with `fetch`:

```javascript
// Fetch all courses and render them
async function loadCourses() {
  const response = await fetch("/api/courses");
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  const courses = await response.json();

  const list = document.getElementById("course-list");
  list.innerHTML = "";
  for (const course of courses) {
    const li = document.createElement("li");
    li.textContent = course.title;
    list.appendChild(li);
  }
}
```

The browser and the Java server never share code — they communicate only through this HTTP + JSON contract, which is exactly what REST is designed for.

## Common mistakes and best practices

- **Verbs in URLs.** `POST /api/createCourse` is wrong; `POST /api/courses` is correct.
- **Always returning 200.** Return `201` on creation, `204` on successful delete, `404` when a resource is not found.
- **Exposing internal IDs without access control.** A `DELETE /api/courses/3` must check that the caller has permission before deleting.
- **Returning raw database exceptions.** Catch exceptions in a `@ControllerAdvice` and return a structured error body with a meaningful status code instead of a stack trace.
- **Mixing singular and plural nouns.** Pick plural (`/courses`, `/students`) and stay consistent across the entire API.

## Summary

A REST API is a set of HTTP endpoints that follow a resource + method convention, return meaningful status codes, and exchange data as JSON. This contract is the bridge between the Spring backend you are about to build and any client that needs its data.
