# Objects, Prototypes, and Classes

## Object literals

```javascript
const user = {
  name: "Alice",
  age: 30,
  greet() { return `hi, ${this.name}`; },
  [computedKey()]: "value",          // dynamic key
};
```

Property shorthand:

```javascript
const name = "Alice", age = 30;
const user = { name, age };          // same as { name: name, age: age }
```

Spread to clone/merge:

```javascript
const updated = { ...user, age: 31 };
```

## Accessing and mutating

```javascript
user.name           // "Alice"
user["name"]        // same
user.email = "...";
delete user.age;
"email" in user;
Object.keys(user);
Object.values(user);
Object.entries(user);
```

## Destructuring

```javascript
const { name, age, email = "n/a" } = user;
const { name: userName } = user;     // rename
const { a, ...rest } = obj;          // grab one, keep rest
```

## Prototypes

Every object has an internal `[[Prototype]]` link to another object (or null). Property lookup walks the chain.

```javascript
const animal = { speak() { return "..."; } };
const dog = Object.create(animal);
dog.speak();           // "..."
Object.getPrototypeOf(dog) === animal;   // true
```

Functions have a `prototype` property — methods on it become methods of instances created with `new`:

```javascript
function User(name) { this.name = name; }
User.prototype.greet = function() { return `hi, ${this.name}`; };
const alice = new User("Alice");
alice.greet();         // "hi, Alice"
```

Modern code uses **classes** instead — they're sugar over the same prototype machinery.

## Classes

```javascript
class User {
  static count = 0;            // class field (static)
  greeting = "Hello";          // instance field

  constructor(name) {
    this.name = name;
    User.count++;
  }

  greet() {
    return `${this.greeting}, ${this.name}`;
  }

  static fromJSON(s) {
    return new User(JSON.parse(s).name);
  }
}

const u = new User("Alice");
u.greet();             // "Hello, Alice"
User.count;            // 1
```

### Private fields

Prefix with `#`:

```javascript
class Counter {
  #count = 0;
  inc() { return ++this.#count; }
}
```

Truly inaccessible from outside.

### Inheritance

```javascript
class Animal {
  speak() { return "..."; }
}

class Dog extends Animal {
  constructor(name) {
    super();
    this.name = name;
  }
  speak() {
    return super.speak() + " woof";
  }
}
```

## When to use classes vs plain objects

Modern JavaScript leans heavily on **functions + plain objects + closures** for most data. Classes shine for:

- Libraries with stateful "things" (a `WebSocket`, a `Stream`, a `Model`).
- When you want inheritance hierarchies (rare in good designs).
- Interop with libraries that expect class instances.

For "data shape with no behavior", plain objects + TypeScript interfaces are usually cleaner.

## Iterating

```javascript
for (const key in obj)   ...    // enumerates own + inherited enumerable keys (avoid)
for (const key of Object.keys(obj)) ...
for (const [k, v] of Object.entries(obj)) ...
```

`for...in` has surprises with prototypes — prefer `Object.keys/entries/values`.
