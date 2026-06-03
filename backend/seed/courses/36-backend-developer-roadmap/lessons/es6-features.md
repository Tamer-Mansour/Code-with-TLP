# Modern JavaScript (ES6+) Features

ES6 (ECMAScript 2015) and its successors introduced a set of language improvements that make JavaScript safer, shorter, and easier to reason about. As a backend developer you will encounter these features in build scripts, tooling configuration, and any Node.js or browser-side code you write alongside your Java APIs.

## `let` and `const` — Block-Scoped Variables

`var` is function-scoped and hoisted, which causes subtle bugs. Prefer `let` for values that change and `const` for values that do not.

```javascript
// var leaks outside the block
for (var i = 0; i < 3; i++) {}
console.log(i); // 3 — surprising!

// let stays inside the block
for (let j = 0; j < 3; j++) {}
// console.log(j); // ReferenceError — expected

const API_URL = 'http://localhost:8080/api';
// API_URL = 'other'; // TypeError — cannot reassign a const
```

`const` does not make an object immutable — it only prevents reassignment of the binding.

## Arrow Functions

Arrow functions provide a concise syntax and do not have their own `this` binding, which avoids a common pitfall with callbacks.

```javascript
// Traditional function
function square(n) {
  return n * n;
}

// Arrow — implicit return for single expressions
const square = n => n * n;

// Arrow with multiple parameters and a body
const add = (a, b) => {
  const result = a + b;
  return result;
};

// Practical use: chaining array methods
const courseIds = [1, 2, 3, 4, 5];
const evenIds = courseIds.filter(id => id % 2 === 0); // [2, 4]
```

## Template Literals

Template literals use backticks and support multi-line strings and embedded expressions — no more string concatenation.

```javascript
const name = 'Tamer';
const port = 8080;

// Old way
const msg1 = 'Hello, ' + name + '! Server running on port ' + port;

// Template literal
const msg2 = `Hello, ${name}! Server running on port ${port}`;

// Multi-line — useful for building SQL snippets or HTML fragments
const query = `
  SELECT id, title, description
  FROM courses
  WHERE active = 1
  ORDER BY created_at DESC
`;
```

## Destructuring

Destructuring unpacks values from arrays and properties from objects into named variables.

```javascript
// Object destructuring
const course = { id: 36, title: 'Backend Developer Roadmap', active: true };
const { id, title } = course;
console.log(title); // 'Backend Developer Roadmap'

// With rename
const { id: courseId } = course;

// Array destructuring
const [first, second, ...rest] = [10, 20, 30, 40];
console.log(first); // 10
console.log(rest);  // [30, 40]

// In function parameters — very common in React / Node callbacks
function printCourse({ title, active }) {
  console.log(`${title} — active: ${active}`);
}
printCourse(course);
```

## Spread and Rest Operators

Both use `...` but in opposite directions.

| Syntax | Direction | Typical use |
|---|---|---|
| `...arr` in a call / literal | Expands | Merge arrays, clone objects, pass array as args |
| `...rest` in a parameter list | Collects | Variadic functions, destructuring remainders |

```javascript
// Spread — merge two arrays
const a = [1, 2];
const b = [3, 4];
const merged = [...a, ...b]; // [1, 2, 3, 4]

// Spread — shallow-clone and override an object (useful for config merging)
const defaults = { timeout: 5000, retries: 3 };
const custom   = { ...defaults, timeout: 1000 }; // { timeout: 1000, retries: 3 }

// Rest — collect remaining arguments
function sum(...numbers) {
  return numbers.reduce((acc, n) => acc + n, 0);
}
console.log(sum(1, 2, 3, 4)); // 10
```

## Modules (`import` / `export`)

ES modules replace the older `<script>` tag soup with explicit dependency declarations.

```javascript
// math.js
export function add(a, b) { return a + b; }
export const PI = 3.14159;

// main.js
import { add, PI } from './math.js';
console.log(add(2, PI)); // 5.14159

// Default export / import
// api.js
export default class ApiClient {
  constructor(baseUrl) { this.baseUrl = baseUrl; }
  get(path) { return fetch(`${this.baseUrl}${path}`); }
}

// app.js
import ApiClient from './api.js';
const client = new ApiClient('http://localhost:8080');
```

In a browser, add `type="module"` to the `<script>` tag. In Node.js 12+ use `"type": "module"` in `package.json` or the `.mjs` extension.

## Promises and `async` / `await`

Promises represent a future value. `async`/`await` is syntactic sugar that makes promise chains read like synchronous code.

```javascript
// Fetch course data from the Spring Boot API
async function fetchCourse(id) {
  try {
    const response = await fetch(`http://localhost:8080/api/courses/${id}`);
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    const data = await response.json();
    console.log(data.title);
    return data;
  } catch (err) {
    console.error('Failed to fetch course:', err.message);
  }
}

fetchCourse(36);
```

Always `await` inside a `try/catch` — unhandled promise rejections will crash Node.js processes in newer versions.

## Common Mistakes

- Using `const` and expecting deep immutability — object properties are still mutable.
- Forgetting that arrow functions cannot be used as constructors (`new () => {}` throws).
- Destructuring a property that does not exist returns `undefined`, not an error — add a default: `const { port = 8080 } = config;`.
- Mixing CommonJS (`require`) and ES module (`import`) in the same Node.js project without proper configuration.

---

ES6+ features — block scoping, arrow functions, template literals, destructuring, spread/rest, modules, and async/await — form the foundation of modern JavaScript and appear throughout every full-stack project built alongside a Java Spring backend.
