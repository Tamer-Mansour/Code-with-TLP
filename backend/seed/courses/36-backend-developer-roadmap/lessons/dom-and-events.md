# The DOM and Events

When a browser loads an HTML page, it parses the markup into a tree of objects called the **Document Object Model (DOM)**. JavaScript can read and modify this tree at runtime, which is how a static page becomes interactive. As a backend developer, you'll touch the DOM whenever you wire up the front end that talks to your Spring REST API.

## The DOM tree

Every element, attribute, and piece of text becomes a **node**. The global `document` object is your entry point.

```html
<!DOCTYPE html>
<html lang="en">
  <body>
    <h1 id="title">Courses</h1>
    <ul id="list"></ul>
    <button id="load">Load</button>
  </body>
</html>
```

## Selecting elements

| Method | Returns | Example |
| --- | --- | --- |
| `getElementById(id)` | single element or `null` | `document.getElementById("title")` |
| `querySelector(css)` | first match or `null` | `document.querySelector(".active")` |
| `querySelectorAll(css)` | static `NodeList` | `document.querySelectorAll("li")` |

`querySelector` accepts any CSS selector, so it is usually the most flexible choice.

```javascript
const title = document.getElementById("title");
const items = document.querySelectorAll("#list li");
console.log(items.length); // number of <li> elements
```

## Reading and changing content

```javascript
const title = document.querySelector("#title");

title.textContent = "Available Courses"; // safe: plain text
title.classList.add("highlight");        // add a CSS class
title.setAttribute("data-count", "12");  // set an attribute
```

- Use `textContent` for plain text — it is fast and immune to HTML injection.
- Use `innerHTML` only with trusted content; injecting user input here invites XSS attacks.

## Handling events

User actions (clicks, typing, form submits) fire **events**. Attach a listener with `addEventListener`:

```javascript
const button = document.getElementById("load");
const list = document.getElementById("list");

button.addEventListener("click", async (event) => {
  event.preventDefault(); // stop default browser action if needed

  // Call your Spring REST endpoint
  const response = await fetch("/api/courses");
  const courses = await response.json();

  list.innerHTML = ""; // clear previous items
  for (const course of courses) {
    const li = document.createElement("li");
    li.textContent = course.title;
    list.appendChild(li);
  }
});
```

The listener receives an **event object**. Useful members include `event.target` (the element that triggered it), `event.preventDefault()`, and `event.stopPropagation()`.

## Event delegation

Events **bubble** up from the target to its ancestors. Instead of binding a listener to every `<li>`, bind one to the parent and inspect `event.target`:

```javascript
list.addEventListener("click", (event) => {
  const li = event.target.closest("li");
  if (li) {
    li.classList.toggle("selected");
  }
});
```

This works even for elements added later — a common win when rendering API data dynamically.

## Common mistakes and best practices

- **Running scripts too early.** If your script runs before the element exists, `getElementById` returns `null`. Place `<script>` at the end of `<body>`, add `defer` to the tag, or wrap code in `DOMContentLoaded`:

```javascript
document.addEventListener("DOMContentLoaded", () => {
  // DOM is fully parsed here
});
```

- **Re-rendering in a loop.** Building HTML strings and reassigning `innerHTML` on every iteration is slow. Build nodes (or one combined string) and append once.
- **Forgetting `event.preventDefault()` on form submits**, which causes a full page reload instead of an async `fetch`.
- **Using `==` in comparisons** — prefer `===` to avoid type coercion surprises.

## Summary

The DOM is a live, scriptable tree representing your page; you select nodes with `querySelector`, change them via `textContent`/`classList`, and respond to user input with `addEventListener`. Master event delegation and `DOMContentLoaded`, and your front end will reliably consume the Spring APIs you build.
