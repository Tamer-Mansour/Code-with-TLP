# Exercise: Validate Commit Messages

Good commit messages follow a consistent format. In this exercise you will validate a batch of commit messages against the Conventional Commits standard.

## Task

Read commit messages from standard input (one per line). For each message, print `valid` if it matches the format, or `invalid` if it does not.

A commit message is **valid** if and only if it starts with one of these type prefixes followed by a colon and a space, then at least one character of description:

```
feat: <description>
fix: <description>
docs: <description>
style: <description>
refactor: <description>
test: <description>
chore: <description>
```

The type must be lowercase. A scope in parentheses is **not** required. The description must have at least one non-space character after `": "`.

## Example

**Input:**
```
feat: add login endpoint
Fix: wrong type capitalisation
docs: update README
chore:missing space after colon
test: write unit tests for auth
random commit message
```

**Output:**
```
valid
invalid
valid
invalid
valid
invalid
```
