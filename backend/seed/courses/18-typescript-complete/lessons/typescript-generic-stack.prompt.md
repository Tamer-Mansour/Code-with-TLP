# Generic Stack Simulator

**Generics** allow a single data structure to work correctly across many types. TypeScript's `Stack<T>` has the same push, pop, and peek behaviour regardless of whether `T` is `number`, `string`, or `User` — the type parameter preserves the relationship between what goes in and what comes out.

## Problem

Simulate a generic stack that stores **integers**. Read commands from stdin:

| Command | Behaviour |
|---|---|
| `PUSH <value>` | Push the integer onto the stack |
| `POP` | Remove and print the top value, or print `EMPTY` if the stack is empty |
| `PEEK` | Print the top value without removing it, or print `EMPTY` |
| `SIZE` | Print the current number of elements |

Only `POP` and `PEEK` produce output when the stack is empty. `PUSH` and `SIZE` always succeed silently / with their value.

## Input

Multiple lines, one command per line.

## Output

Print one line of output for each `POP`, `PEEK`, and `SIZE` command.

## Example

**Input:**
```
PUSH 10
PUSH 20
PUSH 30
PEEK
SIZE
POP
POP
SIZE
POP
POP
```

**Output:**
```
30
3
30
20
1
10
EMPTY
```

## TypeScript connection

```ts
class Stack<T> {
  private items: T[] = [];

  push(item: T): void        { this.items.push(item); }
  pop(): T | undefined       { return this.items.pop(); }
  peek(): T | undefined      { return this.items.at(-1); }
  get size(): number         { return this.items.length; }
  get isEmpty(): boolean     { return this.items.length === 0; }
}

const s = new Stack<number>();
s.push(10);
s.push(20);
console.log(s.peek()); // 20 — TypeScript knows this is number, not unknown
console.log(s.pop());  // 20
```

The type parameter `T` means the compiler knows exactly what type `pop()` returns — no casting needed, no `any` leaking out.
