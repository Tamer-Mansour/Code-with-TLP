# break, continue, and the goto Debate

Loop-control statements let you exit or skip iterations without restructuring the entire loop. Used well they simplify code; abused, they turn control flow into spaghetti.

## break: Exit the Innermost Loop or switch

`break` immediately exits the nearest enclosing `for`, `while`, `do-while`, or `switch`. Execution resumes after the closing brace.

```cpp
// Search: stop as soon as the target is found
int find(const int* arr, int n, int target) {
    int pos = -1;
    for (int i = 0; i < n; ++i) {
        if (arr[i] == target) { pos = i; break; }
    }
    return pos;
}
```

`break` only escapes **one** level of nesting. Breaking out of nested loops requires a flag, a function return, or (rarely) `goto`.

```cpp
// Breaking nested loops with a flag
bool done = false;
for (int r = 0; r < rows && !done; ++r)
    for (int c = 0; c < cols && !done; ++c)
        if (grid[r][c] == target) { found_r = r; found_c = c; done = true; }
```

## continue: Skip to the Next Iteration

`continue` skips the rest of the loop body and jumps to the update expression (for `for`) or back to the condition check (for `while`/`do-while`).

```cpp
// Skip blank lines
for (int i = 0; i < line_count; ++i) {
    if (lines[i][0] == '\0') continue;  // skip empty
    process(lines[i]);
}
```

`continue` reduces nesting and keeps the "happy path" left-aligned. It is generally accepted good style.

## goto: The Infamous Statement

`goto` transfers control to a labeled statement anywhere in the same function. It is legal C++, and it is used in practice — but narrowly.

### When goto is acceptable

**Breaking out of deeply nested loops** is the classic legitimate use:

```cpp
for (int x = 0; x < NX; ++x)
    for (int y = 0; y < NY; ++y)
        for (int z = 0; z < NZ; ++z)
            if (check(x, y, z)) goto found;

// ... nothing found path
return false;

found:
printf("found at %d %d %d\n", x, y, z);
return true;
```

The Linux kernel source uses `goto` extensively for **error-handling cleanup** — a pattern sometimes called "goto cleanup":

```cpp
int setup() {
    if (!alloc_a()) goto err_a;
    if (!alloc_b()) goto err_b;
    if (!alloc_c()) goto err_c;
    return 0;

err_c: free_b();
err_b: free_a();
err_a: return -1;
}
```

This is arguably cleaner than deeply nested `if` chains when you need to undo multiple resource acquisitions in reverse order.

### When goto is harmful

- Jumping **forward over** variable declarations with initializers is ill-formed.
- Jumping **into** the middle of a loop or block creates undefined behavior risks.
- Using `goto` in place of structured loops or `break` makes code harder to reason about and refactor.

## Quick Reference

| Statement | Scope | Effect |
|---|---|---|
| `break` | Innermost loop/switch | Exit the construct immediately |
| `continue` | Innermost loop | Skip to next iteration |
| `goto label` | Entire function | Jump to named label (use sparingly) |

## Worked Example: Tokenizer with continue and break

```cpp
#include <cstdio>
#include <cctype>

void tokenize(const char* s) {
    int i = 0;
    while (s[i]) {
        if (isspace((unsigned char)s[i])) { ++i; continue; }  // skip whitespace
        if (s[i] == '#') break;                                // stop at comment
        putchar(s[i]);
        ++i;
    }
    putchar('\n');
}

int main() {
    tokenize("  hello world # comment ignored");
    tokenize("no-comment-here");
}
```

**Output:**
```
helloworld
no-comment-here
```

> **Interview answer:** `break` exits the nearest loop or switch; `continue` skips to the next iteration. `goto` is legitimately used in C and low-level C++ for breaking nested loops and for reverse-order cleanup of multiple resources, but it should never replace normal structured control flow.
