# HTTP Request Router

Spring's `@RequestMapping` matches incoming HTTP requests to handler methods by HTTP method and path. Build a simple request router.

First read **M** route registrations, each as:
```
METHOD /path HandlerName
```
(e.g. `GET /users listUsers`)

Then read **Q** incoming requests, each as:
```
METHOD /path
```

For each request, print the handler name if a route matches, or `404 Not Found` if none does.

Routes are matched **exactly** (no path variables or wildcards). If the same `METHOD /path` is registered more than once, the **last registration wins**.

## Input format

```
M
METHOD /path HandlerName
...
Q
METHOD /path
...
```

## Output format

One line per request: the handler name or `404 Not Found`.

## Example

**Input:**
```
5
GET /users listUsers
POST /users createUser
GET /users/1 getUser
DELETE /users/1 deleteUser
GET /health healthCheck
4
GET /users
POST /users
GET /products
DELETE /users/1
```

**Output:**
```
listUsers
createUser
404 Not Found
deleteUser
```
