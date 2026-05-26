# Exercise: Parse an HTTP Request Line

Given the first line of an HTTP request, extract and print the **method** and **path**, each on its own line.

## Input Format

A single line containing a valid HTTP request line:
```
METHOD /path HTTP/version
```

## Output Format

Two lines:
```
Method: METHOD
Path: /path
```

## Example

Input:
```
GET /api/users HTTP/1.1
```

Output:
```
Method: GET
Path: /api/users
```
