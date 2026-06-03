# Quiz: JavaScript

**Q1. Which keyword should you prefer when declaring a variable whose value will never be reassigned?**
- [ ] `var`
- [ ] `let`
- [x] `const`
- [ ] `static`

---

**Q2. What is the output of the following code?**

```javascript
const nums = [1, 2, 3, 4, 5];
const result = nums.filter(n => n % 2 === 0).map(n => n * 10);
console.log(result);
```

- [ ] `[1, 3, 5]`
- [ ] `[10, 20, 30, 40, 50]`
- [x] `[20, 40]`
- [ ] `[2, 4]`

---

**Q3. What does the following arrow function return?**

```javascript
const add = (a, b) => a + b;
console.log(add(3, 4));
```

- [ ] `undefined` — arrow functions without curly braces return nothing
- [ ] `"34"` — the `+` operator concatenates when used in an arrow function
- [ ] `NaN`
- [x] `7`

---

**Q4. Which statement correctly describes the difference between `==` and `===` in JavaScript?**
- [ ] `==` checks value and type; `===` checks value only
- [ ] Both operators always behave identically in modern JavaScript
- [x] `==` performs type coercion before comparing; `===` checks both value and type without coercion
- [ ] `===` is only valid for comparing objects; `==` works for all types

---

**Q5. What will the following `async`/`await` snippet log to the console?**

```javascript
async function fetchData() {
  const result = await Promise.resolve("hello");
  console.log(result);
}
fetchData();
```

- [ ] `Promise { 'hello' }`
- [ ] `undefined`
- [x] `"hello"`
- [ ] A TypeError is thrown because `Promise.resolve` cannot be awaited directly

---

**Q6. Given the object below, which destructuring assignment correctly extracts `name` and `role`?**

```javascript
const user = { id: 1, name: "Alice", role: "admin" };
```

- [ ] `const [name, role] = user;`
- [x] `const { name, role } = user;`
- [ ] `const { user.name, user.role } = user;`
- [ ] `const name = user[name], role = user[role];`

---

**Q7. What is the purpose of the spread operator (`...`) in the following expression?**

```javascript
const a = [1, 2, 3];
const b = [...a, 4, 5];
```

- [ ] It converts `a` into a string before appending `4` and `5`
- [ ] It mutates `a` in-place by pushing `4` and `5`
- [x] It creates a new array `b` containing all elements of `a` followed by `4` and `5`, leaving `a` unchanged
- [ ] It merges `a` and the values `4, 5` using reference equality

---

**Q8. Which module syntax correctly exports a function named `greet` and imports it in another file?**

```javascript
// greet.js
export function greet(name) {
  return `Hello, ${name}!`;
}

// main.js — which import is correct?
```

- [ ] `import greet from './greet.js';`
- [x] `import { greet } from './greet.js';`
- [ ] `require('./greet.js').greet;`
- [ ] `import * greet from './greet.js';`

---

**Q9. What will the following closure example print?**

```javascript
function makeCounter() {
  let count = 0;
  return function () {
    count++;
    return count;
  };
}

const counter = makeCounter();
console.log(counter());
console.log(counter());
console.log(counter());
```

- [ ] `0`, `0`, `0`
- [ ] `1`, `1`, `1`
- [ ] `0`, `1`, `2`
- [x] `1`, `2`, `3`

---

**Q10. Which array method transforms every element and returns a new array of the same length?**

| Method | Behaviour |
|--------|-----------|
| `filter` | Returns a subset of elements that pass a test |
| `reduce` | Accumulates elements into a single value |
| `map` | Returns a new array with each element transformed |
| `find` | Returns the first element that passes a test |

- [ ] `filter`
- [ ] `reduce`
- [x] `map`
- [ ] `find`
