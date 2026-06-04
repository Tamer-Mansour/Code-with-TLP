# Dockerfile Layer Order Analyzer

## Problem

A Dockerfile is given as a series of instructions (one per line). Docker caches each instruction as a layer. When a layer is invalidated, **all subsequent layers are also invalidated**.

Rules:
- `COPY` and `ADD` instructions are invalidated when **any listed changed file** matches the instruction's source pattern using a **simple substring match** (the changed filename contains the source token, or the source token contains the changed filename).
- All other instructions (`RUN`, `ENV`, `CMD`, `ENTRYPOINT`, etc.) are invalidated **only if a previous layer was already invalidated**.
- `FROM` is never invalidated by file changes.

Given a Dockerfile and a list of changed files, output the **1-indexed line numbers** of instructions that must re-execute, separated by spaces.

If no instructions need re-executing, output nothing (empty line).

## Input Format

```
<Dockerfile instruction 1>
<Dockerfile instruction 2>
...
---
<changed file 1>
<changed file 2>
...
```

The Dockerfile instructions come first, then a line with exactly `---`, then the changed filenames (one per line).

## Output Format

Space-separated 1-indexed line numbers of instructions that must re-run. If none, print an empty line.

## Example 1

Input:
```
FROM python:3.11-slim
RUN apt-get update && apt-get install -y curl
COPY requirements.txt /app/
RUN pip install -r /app/requirements.txt
COPY src/ /app/src/
CMD ["python", "/app/src/main.py"]
---
src/main.py
```

Output:
```
5 6
```

**Explanation:**
- Lines 1–2: no invalidation yet.
- Line 3: `COPY requirements.txt` — `requirements.txt` is NOT in changed files → cache hit.
- Line 4: `RUN pip install` — no prior invalidation → cache hit.
- Line 5: `COPY src/` — `src/main.py` contains `src/` → **invalidated**. Re-run line 5.
- Line 6: `CMD` — prior layer invalidated → **invalidated**. Re-run line 6.

## Example 2

Input:
```
FROM node:20-alpine
COPY package.json /app/
RUN npm ci
COPY . /app/
CMD ["node", "app.js"]
---
package.json
```

Output:
```
2 3 4 5
```

**Explanation:** Changing `package.json` invalidates line 2 (`COPY package.json`). All subsequent lines (3, 4, 5) cascade.

## Example 3

Input:
```
FROM golang:1.22
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN go build -o /app .
---
internal/handler.go
```

Output:
```
4 5
```

## Constraints

- 1 ≤ number of Dockerfile instructions ≤ 30
- 0 ≤ number of changed files ≤ 20
- Substring matching is case-sensitive.
- `FROM` is always line 1 and is never invalidated.
- Instruction tokens (first word) are uppercase.
