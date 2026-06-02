# Classes in TypeScript

TypeScript extends JavaScript classes with access modifiers, abstract classes, and structural typing — giving you the full object-oriented toolkit while remaining compatible with modern JS.

## Declaring a class

```ts
class Animal {
  name: string;           // public by default

  constructor(name: string) {
    this.name = name;
  }

  speak(): string {
    return `${this.name} makes a sound.`;
  }
}

const a = new Animal("Cat");
console.log(a.speak());  // "Cat makes a sound."
```

## Access modifiers

| Modifier | Visible to | Notes |
|---|---|---|
| `public` (default) | Everyone | Same as no modifier |
| `private` | Class only | Compile-time only (not runtime) |
| `#` (JS private field) | Class only | True runtime encapsulation |
| `protected` | Class + subclasses | — |
| `readonly` | Everyone (read only) | Can only be set in constructor |

```ts
class BankAccount {
  readonly id: string;
  #balance: number = 0;         // true private field

  constructor(id: string) {
    this.id = id;
  }

  deposit(amount: number): void {
    if (amount <= 0) throw new Error("Amount must be positive");
    this.#balance += amount;
  }

  get balance(): number {
    return this.#balance;
  }
}
```

## Constructor shorthand

Prefix parameters with access modifiers to declare and assign in one step:

```ts
class Point {
  constructor(
    public x: number,
    public y: number,
  ) {}

  distanceTo(other: Point): number {
    return Math.hypot(this.x - other.x, this.y - other.y);
  }
}

const p = new Point(3, 4);
console.log(p.x);              // 3
```

## Inheritance

```ts
class Dog extends Animal {
  breed: string;

  constructor(name: string, breed: string) {
    super(name);               // must call super first
    this.breed = breed;
  }

  override speak(): string {   // 'override' is a TS keyword (TS 4.3+)
    return `${this.name} barks.`;
  }
}
```

The `override` keyword causes a compile error if the parent method doesn't exist — protects you from typos.

## Abstract classes

Abstract classes define a contract for subclasses without being instantiable themselves:

```ts
abstract class Serializable {
  abstract toJSON(): object;   // subclasses must implement

  toString(): string {
    return JSON.stringify(this.toJSON());
  }
}

class User extends Serializable {
  constructor(public name: string, public email: string) {
    super();
  }

  toJSON(): object {
    return { name: this.name, email: this.email };
  }
}
```

## Implementing interfaces

A class can implement one or more interfaces — useful for dependency inversion:

```ts
interface Logger {
  log(msg: string): void;
  error(msg: string): void;
}

class ConsoleLogger implements Logger {
  log(msg: string)   { console.log("[LOG]", msg); }
  error(msg: string) { console.error("[ERR]", msg); }
}
```

## Static members

```ts
class IdGenerator {
  private static nextId = 1;

  static generate(): number {
    return IdGenerator.nextId++;
  }
}

IdGenerator.generate();  // 1
IdGenerator.generate();  // 2
```

## Classes are structurally typed

TypeScript checks class instances by shape, not by name — two unrelated classes with the same fields are mutually assignable:

```ts
class Point2D { constructor(public x: number, public y: number) {} }
class Vector2D { constructor(public x: number, public y: number) {} }

const p: Point2D = new Vector2D(1, 2);  // OK — same shape
```

This differs from Java/C# nominal typing and is important to know when classes are used as types in APIs.

## Key takeaways

- Use access modifiers to enforce encapsulation at the type level.
- Prefer `#` private fields when you need true runtime privacy.
- Use `abstract` to define shared structure without implementation.
- `implements` decouples consumers from concrete classes.
- TypeScript classes are structurally — not nominally — typed.
