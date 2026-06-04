# Middleware Pipeline Executor

Express.js middleware functions form a pipeline. Each middleware either calls `next()` to pass control forward, sends a response to terminate the chain, passes an error with `next(err)`, or catches errors if it is an error handler.

Simulate the execution of a middleware pipeline and determine what gets logged and what response is sent.

## Input Format

- First line: integer `N` — the number of middleware entries
- Next `N` lines: each describes a middleware behavior in one of these formats:
  - `NEXT label` — logs `label` and calls `next()` (passes to next middleware)
  - `RESPOND code label` — terminates the chain; the response is `RESPONSE code label`
  - `ERROR label` — calls `next(err)`; switches to error mode (skips NEXT and RESPOND middlewares)
  - `ERROR_HANDLER label` — catches an active error; logs `label`, clears error mode, calls `next()`

## Execution Rules

1. Start in **normal mode** (no active error)
2. In normal mode:
   - `NEXT`: log its label, advance to next middleware
   - `RESPOND`: output the response line and stop
   - `ERROR`: switch to error mode, advance (no log output)
   - `ERROR_HANDLER`: skip (no log, advance)
3. In error mode:
   - `NEXT`: skip (no log, advance)
   - `RESPOND`: output the response line and stop
   - `ERROR`: skip (no log, advance)
   - `ERROR_HANDLER`: log its label, clear error mode, advance
4. If the pipeline ends without a `RESPOND`, output `NO RESPONSE`

## Output Format

Print each logged label on its own line (in order), then the final response line.

## Example

**Input:**
```
6
NEXT logger
NEXT auth
ERROR oops
NEXT business-logic
ERROR_HANDLER error-handler
RESPOND 500 internal-error
```

**Output:**
```
logger
auth
error-handler
RESPONSE 500 internal-error
```

## Constraints

- 1 ≤ N ≤ 50
- `code` in RESPOND is an integer (e.g. 200, 404, 500)
- Labels are single strings without spaces
