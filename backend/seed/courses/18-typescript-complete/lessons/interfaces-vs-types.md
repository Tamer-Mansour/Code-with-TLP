# Interfaces vs Type Aliases

TypeScript has two ways to name a shape: `interface` and `type`. They're 95% interchangeable. Knowing the 5% saves arguments on PRs.

## Interface

```ts
interface User {
  id: number;
  name: string;
}

interface User {
  email?: string;     // declaration merging — adds to existing interface
}
```

Defining the same `interface` twice **merges** the declarations. Useful for extending libraries you don't control.

```ts
interface Admin extends User {
  role: "admin";
}
```

## Type alias

```ts
type User = {
  id: number;
  name: string;
};

type Admin = User & { role: "admin" };       // intersection

type Direction = "left" | "right";           // union — interface can't do this
type Pair<T> = [T, T];                       // type aliases anything: tuples, primitives, unions
```

## The differences

| Feature                       | interface | type |
|-------------------------------|:---------:|:----:|
| Object shapes                 |    ✓      |  ✓   |
| Extend / merge                | extends + merge | & (intersection) |
| Union / primitive aliasing    |     ✗     |  ✓   |
| Tuples                        |     ✗     |  ✓   |
| Declaration merging           |     ✓     |  ✗   |
| Mapped/conditional types      |     ✗     |  ✓   |

## A practical convention

- **`interface`** for **object shapes** that other code consumes (especially library APIs).
- **`type`** for **unions, tuples, mapped types**, and short aliases.

```ts
interface User {
  id: number;
  name: string;
}

type UserId = User["id"];                  // indexed access (always type)
type UserKind = "guest" | "member" | "admin";
type UserMap = Record<UserId, User>;
```

## Extending vs intersecting

`extends` (interface):

```ts
interface Animal { name: string }
interface Dog extends Animal { breed: string }
```

Error messages are slightly cleaner; circular issues are slightly easier to debug.

`&` (intersection):

```ts
type Animal = { name: string }
type Dog = Animal & { breed: string }
```

Works on types and interfaces alike, and lets you compose with unions:

```ts
type ApiResponse<T> = ({ ok: true; data: T } | { ok: false; error: string }) & { duration: number };
```

## Performance

For very large object types, `interface extends` is generally faster for the compiler than long chains of `&`. Doesn't matter until your project is huge — but file it away.

## A note on classes

A class implements an interface or type:

```ts
class UserModel implements User {
  constructor(public id: number, public name: string) {}
}
```

`implements` is purely a check — the class still needs to provide every member itself.

## Bottom line

Use `interface` for objects, `type` for everything else, and don't lose sleep over the choice.
