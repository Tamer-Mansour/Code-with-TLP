# while, for, do-while: Choosing the Right Loop

C++ provides three loop constructs. They are semantically equivalent — anything you can write with one, you can write with another — but each signals a different *intent*, which matters for readability and correctness.

## while: "Loop while condition holds"

```cpp
// Read bytes until EOF
int ch;
while ((ch = getchar()) != EOF) {
    process(ch);
}
```

Use `while` when the number of iterations is unknown up front and you need to test the condition **before** doing any work. The body may run zero times.

## for: "Iterate over a range"

```cpp
for (int i = 0; i < n; ++i) {
    buffer[i] = 0;
}
```

The classic `for` packs init / condition / increment into one line, keeping the loop variable scoped to the loop. This is the preferred form for index-based traversal.

### Range-based for (C++11)

```cpp
std::vector<int> v = {1, 2, 3};
for (int x : v) {
    printf("%d\n", x);
}
```

Use `const auto&` when iterating containers of non-trivial types to avoid unnecessary copies:

```cpp
for (const auto& entry : registry) { ... }
```

### Common for-loop pitfalls

| Mistake | Why it breaks |
|---|---|
| `i <= n` instead of `i < n` | Off-by-one, accesses `arr[n]` |
| `i++` vs `++i` in complex expressions | `i++` creates a temporary; prefer `++i` in loops |
| Unsigned counter going negative | `for (size_t i = n-1; i >= 0; --i)` loops forever because `size_t` wraps |

The signed-vs-unsigned pitfall is particularly nasty in systems code:

```cpp
// Bug: size_t i wraps to SIZE_MAX when i hits 0 and decrements
for (size_t i = n - 1; i >= 0; --i)  // infinite loop!

// Fix: cast or use a signed counter
for (int i = (int)n - 1; i >= 0; --i)  // OK
```

## do-while: "Do once, then loop while condition holds"

```cpp
int choice;
do {
    printf("Enter 1-3: ");
    scanf("%d", &choice);
} while (choice < 1 || choice > 3);
```

The body runs **at least once** before the condition is checked. This is ideal for menus, retry loops, and CRC/checksum computations where you must process the first element unconditionally.

In practice `do-while` is rare — overuse is a code smell — but it is the clearest way to express "execute then validate".

## Choosing the Right Loop

| Situation | Preferred loop |
|---|---|
| Known number of iterations / index | `for` |
| Iterate container or range | Range `for` |
| Unknown iterations, check first | `while` |
| Must execute at least once | `do-while` |

## Worked Example: Processing a Ring Buffer

```cpp
#include <cstdio>

constexpr int CAP = 8;
int buf[CAP];
int head = 0, tail = 0, count = 0;

void enqueue(int v) { buf[tail++ % CAP] = v; ++count; }
int  dequeue()      { --count; return buf[head++ % CAP]; }

int main() {
    for (int i = 1; i <= 5; ++i) enqueue(i * 10);

    while (count > 0) {
        int v = dequeue();
        printf("%d ", v);
    }
    printf("\n");
}
```

**Output:**
```
10 20 30 40 50
```

The `for` loop fills the buffer (known count), the `while` drains it (runs until empty).

> **Interview answer:** Use `for` for index-driven or range-based iteration, `while` when the iteration count is unknown and the loop may not run at all, and `do-while` only when the body must execute at least once. Watch out for unsigned counter underflow when decrementing to zero.
