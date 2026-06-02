# Template Literals

Template literals (also called template strings) replace the old string concatenation idiom with a readable, powerful syntax introduced in ES2015.

## Basic Syntax

Use backticks `` ` `` instead of quotes. Embed any expression with `${...}`:

```javascript
const name = "Tamer";
const age = 30;

// Old way
"Hello, " + name + "! You are " + age + " years old.";

// Template literal
`Hello, ${name}! You are ${age} years old.`;
```

Any valid JavaScript expression works inside `${}`:

```javascript
const a = 5, b = 10;
`Sum: ${a + b}, Product: ${a * b}`;  // "Sum: 15, Product: 50"
`${a > b ? "a wins" : "b wins"}`;    // "b wins"
```

## Multi-line Strings

Template literals preserve newlines and indentation literally:

```javascript
const html = `
  <div class="card">
    <h2>${title}</h2>
    <p>${description}</p>
  </div>
`;
```

No more `\n` escapes or concatenating lines with `+`.

## Nested Templates

You can nest template literals — useful for building HTML or SQL dynamically:

```javascript
const items = ["Apple", "Banana", "Cherry"];

const list = `
  <ul>
    ${items.map(item => `<li>${item}</li>`).join("\n    ")}
  </ul>
`;
```

## Tagged Templates

A **tagged template** is a template literal prefixed with a function name. The function receives the static string parts and the interpolated values as arguments:

```javascript
function highlight(strings, ...values) {
  return strings.reduce((result, str, i) => {
    const val = values[i] !== undefined ? `<mark>${values[i]}</mark>` : "";
    return result + str + val;
  }, "");
}

const name = "Sara";
const score = 98;

highlight`Student ${name} scored ${score} points.`;
// "Student <mark>Sara</mark> scored <mark>98</mark> points."
```

Tagged templates power popular libraries like:

- **GraphQL** — `gql` tag from Apollo
- **CSS-in-JS** — `styled.div` in styled-components
- **SQL sanitisation** — `sql` tag to prevent injection

## Raw Strings

The special `String.raw` tag returns the raw string with escape sequences un-processed:

```javascript
String.raw`Line1\nLine2`;   // "Line1\\nLine2" — backslash-n, not newline
String.raw`C:\Users\name`;  // "C:\\Users\\name"
```

Handy for regular expressions and Windows file paths.

## Common Patterns

| Pattern | Example |
|---------|---------|
| String interpolation | `` `Hello, ${user.name}!` `` |
| Multi-line HTML | Backtick block with indented tags |
| Conditional text | `` `${count} item${count !== 1 ? "s" : ""}` `` |
| Padding/formatting | `` `${value.toString().padStart(3, "0")}` `` |
| URL building | `` `https://api.example.com/users/${id}` `` |

## Template Literals vs String Concatenation

```javascript
// Concatenation — hard to read
const msg = "User " + user.name + " (" + user.email + ") joined on " + date + ".";

// Template literal — reads like prose
const msg = `User ${user.name} (${user.email}) joined on ${date}.`;
```

Template literals almost always win on readability. The only exception is extremely simple single-value cases — even then most teams prefer backticks for consistency.
