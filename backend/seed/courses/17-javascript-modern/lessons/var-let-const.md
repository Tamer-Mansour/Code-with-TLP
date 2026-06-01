# var, let, const, and Scope

JavaScript has three ways to declare variables. Use **`const` by default, `let` when you must reassign, and never `var`**.

## var — function-scoped, hoisted

```javascript
function f() {
  console.log(x);    // undefined, not ReferenceError
  var x = 1;
}
```

`var` declarations are **hoisted** to the top of the enclosing *function*. The assignment isn't — only the declaration. This is the source of countless bugs.

Block scope doesn't apply:

```javascript
if (true) {
  var x = 10;
}
console.log(x);     // 10   ← leaked out of the block
```

## let — block-scoped, NOT hoisted (well, sort of)

```javascript
{
  let x = 10;
}
console.log(x);     // ReferenceError
```

`let` is hoisted but enters a **temporal dead zone** until the actual `let` line executes. Using it before that throws.

You can reassign:

```javascript
let count = 0;
count = 1;
```

## const — block-scoped, single-assignment

```javascript
const PI = 3.14;
PI = 4;             // TypeError
```

`const` binds the variable, not the value. Objects can still mutate:

```javascript
const user = { name: "Alice" };
user.name = "Bob";       // OK
user = {};               // TypeError
```

If you want truly immutable, use `Object.freeze()` or TypeScript's `readonly`.

## Why "const by default"

Code that doesn't reassign is easier to follow. When you see `let`, you know to look for a later mutation. When you see `const`, you can trust the binding stays put.

Convert to `let` only when you must:

```javascript
let total = 0;
for (const n of nums) total += n;
```

## Scope rules in one sentence

`let` and `const` are scoped to the **nearest enclosing `{}`**. `var` is scoped to the **nearest enclosing function**. Always.

## A loop quirk

```javascript
const handlers = [];
for (var i = 0; i < 3; i++) {
  handlers.push(() => console.log(i));
}
handlers.forEach(h => h());
// 3 3 3
```

With `var`, all closures share the same `i`. With `let`, each iteration gets a new binding:

```javascript
for (let i = 0; i < 3; i++) ...
// 0 1 2
```

This alone is reason enough to abandon `var`.

## Linting

ESLint's `no-var` rule and `prefer-const` rule together enforce the convention automatically. Turn them both on.
