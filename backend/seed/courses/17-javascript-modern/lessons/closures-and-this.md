# Closures and this

## Closures

A function "closes over" variables in its lexical scope. The function keeps access to them even after the enclosing function returns.

```javascript
function makeCounter() {
  let count = 0;
  return () => ++count;
}

const c = makeCounter();
c();   // 1
c();   // 2
c();   // 3
```

Each call to `makeCounter` creates a fresh `count` and a fresh closure over it.

### Practical uses

**Private state:**
```javascript
function bank(initial) {
  let balance = initial;
  return {
    deposit:  (n) => balance += n,
    withdraw: (n) => balance -= n,
    balance:  () => balance,
  };
}
```

**Configured callbacks:**
```javascript
button.addEventListener("click", (() => {
  let clicks = 0;
  return () => console.log(++clicks);
})());
```

**Memoization:**
```javascript
function memo(fn) {
  const cache = new Map();
  return (key) => {
    if (!cache.has(key)) cache.set(key, fn(key));
    return cache.get(key);
  };
}
```

## `this` — the source of all evil

`this` is the most surprising part of JavaScript. The value depends on **how a function is called**, not where it's defined.

```javascript
function f() { return this; }
f();                  // undefined in strict mode, window otherwise
const o = { f };
o.f();                // o
new f();              // a new object
f.call("hello");      // "hello"
f.bind({a:1})();      // {a:1}
```

Five binding rules, in order:

1. **`new`** — `this` is the new object.
2. **`fn.call(x)` / `fn.apply(x)`** — `this` is `x`.
3. **`obj.fn()`** — `this` is `obj`.
4. **Plain call** — `this` is `undefined` (strict) or `window` (sloppy).
5. **Arrow function** — `this` is the *lexical* `this` from the enclosing scope. The above rules don't apply.

### The classic gotcha

```javascript
class Counter {
  constructor() { this.n = 0; }
  inc() { this.n++; console.log(this.n); }
}

const c = new Counter();
setTimeout(c.inc, 1000);    // TypeError: cannot read 'n' of undefined
```

`c.inc` was extracted from `c`, losing the `c` binding. Fix one of three ways:

```javascript
setTimeout(() => c.inc(), 1000);          // arrow wraps it
setTimeout(c.inc.bind(c), 1000);          // pre-bind
// or define inc as an arrow class field:
class Counter {
  n = 0;
  inc = () => { this.n++; };
}
```

## Method binding in React-era code

In modern React with function components, `this` largely disappears — components are plain functions. In class components and Node code you still meet it. Default to **arrow class fields** when you want `this` to mean what you think it means.

## bind, call, apply

```javascript
fn.call(thisArg, arg1, arg2);       // call now with this and args
fn.apply(thisArg, [arg1, arg2]);    // same, args as array
const bound = fn.bind(thisArg);     // returns a new function pre-bound
```

`bind` is one-shot — calling `bound.call(other)` doesn't re-bind it.
