# Challenge: To-Do App

The To-Do app is the classic capstone for front-end JavaScript. It is small enough to finish in one sitting, yet it exercises every core skill you need before moving to a backend: reading user input, manipulating the DOM, handling events, and persisting state. Build it once by hand and the patterns will stick.

## What this challenge teaches

- **DOM manipulation** — creating, appending, and removing elements with `document.createElement`, `append`, and `remove`.
- **Event handling** — responding to clicks and form submissions, and using **event delegation** for dynamically added items.
- **State + persistence** — keeping an array of tasks in memory and saving it to `localStorage` so data survives a page reload.

## Requirements

Your app must let the user:

| Feature | Behaviour |
|---------|-----------|
| Add | Type text, submit the form, and see the task appear in the list |
| Complete | Click a task to toggle a `done` (strike-through) state |
| Delete | Click a button to remove a single task |
| Persist | Reload the page and the tasks (and their done state) are still there |

## Suggested HTML

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>To-Do</title>
  <link rel="stylesheet" href="styles.css" />
</head>
<body>
  <form id="todo-form">
    <input id="todo-input" type="text" placeholder="Add a task" required />
    <button type="submit">Add</button>
  </form>
  <ul id="todo-list"></ul>
  <script src="app.js"></script>
</body>
</html>
```

A little CSS to mark completed items:

```css
.done {
  text-decoration: line-through;
  color: #888;
}
```

## Suggested JavaScript

Keep a single source of truth (the `todos` array), then re-render from it. Note the event delegation on the `<ul>` — one listener handles every current and future task.

```javascript
const form = document.querySelector("#todo-form");
const input = document.querySelector("#todo-input");
const list = document.querySelector("#todo-list");

let todos = JSON.parse(localStorage.getItem("todos")) || [];

function save() {
  localStorage.setItem("todos", JSON.stringify(todos));
}

function render() {
  list.innerHTML = "";
  todos.forEach((todo, index) => {
    const li = document.createElement("li");
    li.textContent = todo.text;
    li.dataset.index = index;
    if (todo.done) li.classList.add("done");

    const del = document.createElement("button");
    del.textContent = "x";
    del.className = "delete";
    li.append(del);
    list.append(li);
  });
}

form.addEventListener("submit", (e) => {
  e.preventDefault();
  const text = input.value.trim();
  if (!text) return;
  todos.push({ text, done: false });
  input.value = "";
  save();
  render();
});

list.addEventListener("click", (e) => {
  const li = e.target.closest("li");
  if (!li) return;
  const index = Number(li.dataset.index);
  if (e.target.classList.contains("delete")) {
    todos.splice(index, 1);     // delete
  } else {
    todos[index].done = !todos[index].done; // toggle
  }
  save();
  render();
});

render();
```

## Common pitfalls

- **Forgetting `e.preventDefault()`** — the form will reload the page on submit, wiping your in-memory list.
- **Attaching listeners to each `<li>`** — new tasks added later won't have a listener. Delegate to the parent `<ul>` instead.
- **Storing objects raw in `localStorage`** — it only holds strings. Always `JSON.stringify` on write and `JSON.parse` on read.
- **Not trimming input** — empty or whitespace-only tasks slip in. Guard with `text.trim()`.

## Summary

A To-Do app ties together DOM updates, delegated events, and `localStorage` persistence. Render from one `todos` array and the rest stays simple and predictable.
