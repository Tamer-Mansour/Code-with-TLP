# Advanced Type Guards

A type guard is any expression that narrows a type at runtime and makes that narrowing visible to the TypeScript compiler. You have already seen `typeof` and `instanceof`; this lesson covers user-defined guards, assertion functions, and the `satisfies` operator.

## Recap: built-in guards

```ts
function printLength(x: string | number[] | null): void {
  if (x === null) return;                        // null guard
  if (typeof x === "string") {
    console.log(x.toUpperCase());               // x: string
  } else {
    console.log(x.length);                      // x: number[]
  }
}
```

`typeof`, `instanceof`, `in`, equality checks (`=== null`, `=== "circle"`) all trigger narrowing automatically.

## User-defined type guard functions

A function can act as a type guard with `x is T` as its return type:

```ts
interface Cat { kind: "cat"; meow(): void }
interface Dog { kind: "dog"; bark(): void }

function isCat(animal: Cat | Dog): animal is Cat {
  return animal.kind === "cat";
}

function interact(animal: Cat | Dog) {
  if (isCat(animal)) {
    animal.meow();    // animal: Cat
  } else {
    animal.bark();    // animal: Dog
  }
}
```

The function body is your responsibility — TypeScript trusts the annotation. Make sure the runtime check and the type annotation agree.

## Assertion functions

Assertion functions narrow inside the **same block** after the call (they throw instead of returning `false`):

```ts
function assertIsString(val: unknown): asserts val is string {
  if (typeof val !== "string") {
    throw new TypeError(`Expected string, got ${typeof val}`);
  }
}

function processInput(input: unknown) {
  assertIsString(input);
  console.log(input.toUpperCase());   // input: string — narrowed after assert
}
```

`asserts val is T` means: *"if this function returns normally, `val` is `T` from here on."*

A parameter-free variant asserts a condition:

```ts
function assert(condition: boolean, msg?: string): asserts condition {
  if (!condition) throw new Error(msg ?? "Assertion failed");
}

function divide(a: number, b: number): number {
  assert(b !== 0, "Cannot divide by zero");
  return a / b;                         // TS knows b !== 0 here
}
```

## `in` operator narrowing

The `in` operator narrows to types that include the checked property:

```ts
type Fish  = { swim(): void };
type Bird  = { fly(): void };
type Penguin = { swim(): void; fly: never };

function move(animal: Fish | Bird) {
  if ("swim" in animal) {
    animal.swim();   // Fish (or Penguin if added)
  } else {
    animal.fly();    // Bird
  }
}
```

## Narrowing arrays with `filter` — the `flatMap` trick

`Array.prototype.filter` loses the narrowed type by default:

```ts
const items: (number | null)[] = [1, null, 2, null, 3];

// Wrong: TS infers (number | null)[]
const nums = items.filter(x => x !== null);

// Correct: use a type guard predicate
function isNonNull<T>(x: T | null | undefined): x is T {
  return x != null;
}

const nums2 = items.filter(isNonNull);  // number[]
```

## The `satisfies` operator (TS 4.9+)

`satisfies` validates that a value matches a type **without widening** it:

```ts
const palette = {
  red:   [255, 0,   0  ],
  green: "#00ff00",
  blue:  [0,   0,   255],
} satisfies Record<string, string | number[]>;

// palette.red is still number[] (not string | number[])
palette.red.map(c => c / 255);   // OK — TS kept the specific type

// palette.green is still string
palette.green.toUpperCase();     // OK
```

Without `satisfies`, a type annotation would widen all values to `string | number[]`.

## Summary

| Technique | Use case |
|---|---|
| `typeof` / `instanceof` | Primitives and class instances |
| `=== literal` | Discriminated union narrowing |
| `in "prop"` | Duck-type narrowing |
| `x is T` function | Custom runtime checks |
| `asserts x is T` | Throw-on-fail validation |
| `satisfies` | Validate without widening |

Type guards are the bridge between runtime reality and compile-time types. Combine them with discriminated unions for safe, exhaustive data modelling.
