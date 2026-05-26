# Count Conventional Commit Types

Read conventional commit message subjects from standard input (one per line). Count how many commits belong to each known type and print the counts in **alphabetical order by type**.

## Specification

- **Valid types:** `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`
- **Valid subject formats:**
  - `feat: description`
  - `feat(scope): description`
  - `feat!: description` (breaking change marker — type is still `feat`)
  - `feat(scope)!: description`
- Lines that do not match any valid type should be silently **ignored**
- Types with zero valid commits should **not** appear in the output
- Output one line per observed type in alphabetical order: `<type>: <count>`

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
