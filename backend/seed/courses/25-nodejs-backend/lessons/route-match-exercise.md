# Route Matcher

Implement a tiny Express-like router. Given a set of route patterns and a series of incoming URL paths, decide which pattern matches each path and extract the parameters.

Patterns look like:

```
/users/:id
/posts/:postId/comments/:cid
/about
```

Routes are tried **in declaration order**; the first match wins.

See the prompt for the exact contract.
