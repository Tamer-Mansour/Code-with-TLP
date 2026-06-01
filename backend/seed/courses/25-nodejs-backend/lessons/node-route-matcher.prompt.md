# Express-style Route Matcher

## Input

```
N
<route 1>
<route 2>
... N routes
<query 1>
<query 2>
... any number of queries (until EOF)
```

- N is the number of route patterns (1 ≤ N ≤ 100).
- Each route starts with `/` and uses `:name` for parameters (e.g. `/users/:id`).
- Each query is an incoming URL path also starting with `/`.

## Output

For each query, print one line:

- If a route matches: print the route pattern, then space-separated `param=value` pairs in pattern order.
- Otherwise: print `NO MATCH`.

A pattern matches if it has the same number of `/`-separated segments and every non-`:` segment is identical.

Try patterns in declaration order; the **first** match wins.

## Example

Input:

```
2
/users/:id
/posts/:postId/comments/:cid
/users/42
/posts/9/comments/3
/about
```

Output:

```
/users/:id id=42
/posts/:postId/comments/:cid postId=9 cid=3
NO MATCH
```

## More

Input:

```
2
/users/me
/users/:id
/users/me
/users/42
```

Output:

```
/users/me
/users/:id id=42
```

(Exact-match `/users/me` wins because it comes first.)

Input:

```
2
/about
/users/:id
/about
/users/1
```

Output:

```
/about
/users/:id id=1
```

## Notes

- Routes with no parameters print just the pattern (no trailing space).
- All segment text is alphanumeric.
- No trailing slashes; the leading slash is always present.
