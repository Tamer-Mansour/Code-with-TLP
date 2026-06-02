# Symbols, WeakMap, and WeakSet

ES2015 introduced `Symbol` and two new collection types — `WeakMap` and `WeakSet` — that solve specific problems around unique keys, private-ish data, and memory management.

## Symbol — Truly Unique Values

A `Symbol` is a primitive whose value is guaranteed to be unique, even if you create two symbols with the same description:

```javascript
const a = Symbol("id");
const b = Symbol("id");

a === b;          // false  — always unique
typeof a;         // "symbol"
a.toString();     // "Symbol(id)"
a.description;    // "id"
```

### Using Symbols as Object Keys

Because symbols are unique, they are perfect for adding metadata to objects without polluting the string-key namespace:

```javascript
const HIDDEN = Symbol("hidden");

const obj = {
  name: "public",
  [HIDDEN]: "secret",
};

console.log(obj.name);    // "public"
console.log(obj[HIDDEN]); // "secret"

// Symbols are NOT enumerated by for..in or Object.keys
Object.keys(obj);         // ["name"]
```

This makes symbols ideal for library authors who need to attach private data to user objects without risking key collisions.

### Well-Known Symbols

JavaScript uses built-in symbols to customise language behaviour:

| Symbol | Controls |
|--------|---------|
| `Symbol.iterator` | `for...of` iteration protocol |
| `Symbol.toPrimitive` | Type coercion |
| `Symbol.hasInstance` | `instanceof` check |
| `Symbol.toStringTag` | `Object.prototype.toString` output |

```javascript
class MyList {
  constructor(...items) { this.items = items; }

  [Symbol.iterator]() {
    return this.items[Symbol.iterator]();
  }
}

for (const item of new MyList(1, 2, 3)) {
  console.log(item);  // 1, 2, 3
}
```

## WeakMap — Keys Must Be Objects

A `WeakMap` is like a `Map` but:

1. **Keys must be objects** (not primitives).
2. Keys are held **weakly** — if the key object has no other references, it can be garbage-collected and the entry silently disappears.

```javascript
const cache = new WeakMap();

function process(obj) {
  if (cache.has(obj)) return cache.get(obj);
  const result = heavyComputation(obj);
  cache.set(obj, result);
  return result;
}
```

When `obj` is no longer referenced elsewhere, the entry is removed automatically — no memory leak.

### Private Class Data Pattern

```javascript
const _private = new WeakMap();

class BankAccount {
  constructor(balance) {
    _private.set(this, { balance });
  }

  deposit(amount) {
    _private.get(this).balance += amount;
  }

  get balance() {
    return _private.get(this).balance;
  }
}

const account = new BankAccount(1000);
account.deposit(500);
account.balance;  // 1500
// No way to access _private.get(account) from outside the module
```

## WeakSet — Tracking Object Identity

A `WeakSet` stores a set of objects, again held weakly:

```javascript
const seen = new WeakSet();

function visitOnce(node) {
  if (seen.has(node)) return;
  seen.add(node);
  doWork(node);
}
```

Useful for cycle detection in graphs/trees — when the node is garbage-collected, its entry disappears too.

## WeakMap vs Map, WeakSet vs Set

| | Map / Set | WeakMap / WeakSet |
|-|-----------|-------------------|
| Key type | Any | Objects only |
| Memory | Strong reference | Weak reference (GC-friendly) |
| Iterable | Yes | No |
| Size property | Yes | No |
| Use case | General collections | Private data, caches, cycle detection |

## When to Reach for These

- **Symbol**: unique property keys, implementing protocols (`Symbol.iterator`), feature flags.
- **WeakMap**: associating private or cached data with an object without preventing its GC.
- **WeakSet**: tracking "have I seen this object" without leaking memory.

For most everyday code, plain `Map` and `Set` are the right tool. These three are for the moments when you need finer control.
