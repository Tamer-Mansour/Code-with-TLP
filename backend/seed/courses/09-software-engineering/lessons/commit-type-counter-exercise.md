# Exercise: Count Conventional Commit Types

Conventional Commits give your git history machine-readable structure. In this exercise you will parse a list of commit message subjects and count how many commits belong to each known type.

## Background

A valid conventional commit subject has the form:

```
<type>[optional scope]: <description>
```

Where `<type>` is one of: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`.

A scope is an optional parenthesised qualifier after the type: `feat(auth): add login`.
A `!` before the colon marks a breaking change but does not change the type: `feat!: remove v1 API`.

Your job is to count the valid commits by type and print the counts in alphabetical order by type. Lines that do not match the pattern should be silently ignored.

## Example

**Input:**
```
feat: add login
fix: null pointer in auth
feat(auth): add logout
chore: upgrade deps
docs: update README
fix!: remove broken endpoint
random commit message
```

**Output:**
```
chore: 1
docs: 1
feat: 2
fix: 2
```

Note: `fix!` counts as type `fix`.
