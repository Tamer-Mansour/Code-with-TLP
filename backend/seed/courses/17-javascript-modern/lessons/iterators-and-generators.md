# Iterators and Generators

JavaScript's iteration protocol and generators give you a principled, memory-efficient way to produce sequences of values — one item at a time, on demand.

## The Iteration Protocol

Any object is **iterable** if it has a `[Symbol.iterator]()` method that returns an **iterator** — an object with a `next()` method. `next()` returns `{ value, done }`.

```javascript
const arr = [10, 20, 30];
const iter = arr[Symbol.iterator]();

iter.next();  // { value: 10, done: false }
iter.next();  // { value: 20, done: false }
iter.next();  // { value: 30, done: false }
iter.next();  // { value: undefined, done: true }
```

`for...of`, destructuring, `spread`, `Array.from`, and `Promise.all` all rely on this protocol internally.

## Custom Iterables

You can make any object iterable:

```javascript
const range = {
  from: 1,
  to: 5,
  [Symbol.iterator]() {
    let current = this.from;
    const last = this.to;
    return {
      next() {
        return current <= last
          ? { value: current++, done: false }
          : { value: undefined, done: true };
      }
    };
  }
};

for (const n of range) {
  console.log(n);  // 1 2 3 4 5
}
```

## Generator Functions

A generator function (`function*`) is a cleaner way to create an iterator. The `yield` keyword suspends execution and hands a value to the caller; execution resumes from that exact point on the next `next()` call.

```javascript
function* count(from, to) {
  for (let i = from; i <= to; i++) {
    yield i;
  }
}

const gen = count(1, 3);
gen.next();  // { value: 1, done: false }
gen.next();  // { value: 2, done: false }
gen.next();  // { value: 3, done: false }
gen.next();  // { value: undefined, done: true }
```

Or use `for...of` — it handles `done` automatically:

```javascript
for (const n of count(1, 5)) {
  process.stdout.write(n + " ");
}
// 1 2 3 4 5
```

## Infinite Sequences

Generators shine for infinite or very large sequences because they are lazy — values are computed only when requested:

```javascript
function* fibonacci() {
  let [a, b] = [0, 1];
  while (true) {
    yield a;
    [a, b] = [b, a + b];
  }
}

function take(gen, n) {
  const result = [];
  for (const val of gen) {
    result.push(val);
    if (result.length === n) break;
  }
  return result;
}

take(fibonacci(), 8);
// [0, 1, 1, 2, 3, 5, 8, 13]
```

No array of a million Fibonacci numbers is ever created in memory.

## `yield*` — Delegating to Another Iterable

```javascript
function* concat(...iterables) {
  for (const it of iterables) {
    yield* it;
  }
}

[...concat([1, 2], [3, 4], [5])];
// [1, 2, 3, 4, 5]
```

`yield*` hands control to another iterable and forwards every value it produces.

## Practical Use Cases

| Use case | Pattern |
|----------|---------|
| Lazy pagination | `yield` each page on demand |
| Infinite scroll data | Infinite generator with `take` |
| Flattening nested trees | Recursive `yield*` |
| State machine steps | `yield` at each state |
| Async generators (`async function*`) | `yield` resolved promises |

## Async Generators (bonus)

```javascript
async function* paginate(url) {
  while (url) {
    const res = await fetch(url);
    const data = await res.json();
    yield data.items;
    url = data.nextPage;
  }
}

for await (const page of paginate("/api/items")) {
  render(page);
}
```

`for await...of` pairs with async generators to pull pages one at a time without loading everything into memory first.

## Key Points

- **Iterator protocol**: objects with `[Symbol.iterator]()` returning `{ next() }`.
- **Generator functions** (`function*`) produce iterators automatically.
- `yield` suspends; `next()` resumes.
- Generators can be infinite — they compute values lazily.
- `yield*` delegates to another iterable.
