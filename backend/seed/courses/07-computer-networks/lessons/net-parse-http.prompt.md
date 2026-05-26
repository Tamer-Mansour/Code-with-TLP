# Parse HTTP Request Line

Read a single HTTP request line from standard input and print the HTTP method and path, each on its own line, in the format shown below.

## Input

A single line (with trailing newline):
```
METHOD /path HTTP/version
```

## Output

```
Method: METHOD
Path: /path
```

## Examples

**Input:**
```
GET /index.html HTTP/1.0
```
**Output:**
```
Method: GET
Path: /index.html
```

**Input:**
```
POST /api/login HTTP/1.1
```
**Output:**
```
Method: POST
Path: /api/login
```

## Constraints

- The input is always a valid HTTP request line with exactly three space-separated tokens.
- The path may contain slashes and query strings but no spaces.
- Use only the Python standard library.
