# REST API Design

REST isn't an exact standard — it's a set of conventions for HTTP APIs that make them predictable. Following them makes your API easier to consume and document.

## Resources and methods

Model your API around **resources** (nouns), use HTTP **methods** (verbs):

| Method   | URL                  | Meaning                          |
|----------|----------------------|----------------------------------|
| `GET`    | `/users`             | List users                       |
| `GET`    | `/users/42`          | Fetch user 42                    |
| `POST`   | `/users`             | Create a user                    |
| `PUT`    | `/users/42`          | Replace user 42                  |
| `PATCH`  | `/users/42`          | Partially update user 42         |
| `DELETE` | `/users/42`          | Delete user 42                   |
| `GET`    | `/users/42/orders`   | User 42's orders (sub-resource)  |

Names are plural. URLs avoid verbs (no `/getUsers`). Sub-resources nest.

## Status codes

Use them correctly:

| Code | Meaning                                        |
|------|------------------------------------------------|
| 200  | OK — request succeeded                         |
| 201  | Created — new resource (return `Location:`)    |
| 204  | No Content — success, body empty (e.g., DELETE)|
| 400  | Bad Request — invalid input                    |
| 401  | Unauthorized — not authenticated               |
| 403  | Forbidden — authenticated but not allowed      |
| 404  | Not Found                                      |
| 409  | Conflict — duplicate, version mismatch         |
| 422  | Unprocessable Entity — semantic validation fail|
| 429  | Too Many Requests — rate-limited               |
| 500  | Internal Server Error                          |
| 503  | Service Unavailable — try again later          |

## Pagination

Don't return 1M rows. Pick one strategy:

**Offset/limit** — simple, breaks for large pages:

```
GET /users?page=2&perPage=20
```

**Cursor** — scales to billions of rows:

```
GET /users?cursor=...&limit=20
```

Return the next cursor in the response body or `Link:` header.

## Filtering and sorting

```
GET /orders?status=paid&since=2025-01-01&sort=-created_at
```

`-` for descending. Document your filterable fields explicitly — don't let users `WHERE` anything.

## Response shape

Consistency matters. Pick a convention and stick with it:

```json
{
  "data": { "id": 42, "name": "Alice" },
  "meta": { "requestId": "..." }
}
```

For collections:

```json
{
  "data": [ ... ],
  "meta": { "nextCursor": "...", "total": 1234 }
}
```

For errors:

```json
{
  "error": {
    "code": "VALIDATION_FAILED",
    "message": "email is required",
    "fields": { "email": "required" }
  }
}
```

A stable `code` enum is more useful than free-text `message` for client logic.

## Versioning

Two common approaches:

- In URL: `/v1/users`, `/v2/users`. Simple, visible, easy to deprecate.
- In header: `Accept: application/vnd.myapi.v2+json`. Cleaner URLs, harder to test.

URL versioning is the pragmatic choice for most APIs.

## Idempotency

`GET`, `PUT`, `DELETE` should be **idempotent** — repeated calls have the same effect. `POST` typically isn't.

For non-idempotent operations a client may retry, accept an **idempotency key**:

```
POST /orders
Idempotency-Key: 8a9b2c... (client-generated UUID)
```

Server stores the result for ~24h keyed by the header. A retry returns the cached response — no duplicate orders.

## OpenAPI / Swagger

Document your API in OpenAPI. Generated clients, generated docs, generated tests. Don't skip this.

Tools: **Swagger UI**, **Redoc**, **Scalar** for docs; **openapi-typescript** for TS clients; **Spectral** for linting your spec.

## Avoid

- Verbs in URLs (`/getUser`, `/createOrder`).
- Hiding errors as 200 with `{ "ok": false }`.
- Returning lists as a top-level array (locked from adding metadata later).
- Versioning by query string.
