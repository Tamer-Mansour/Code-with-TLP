# CSS Selectors and the Box Model

CSS controls the visual presentation of every HTML element on the page. Two concepts underpin virtually everything you write in a stylesheet: **selectors** (which elements a rule targets) and the **box model** (how space is calculated around those elements). Getting both right eliminates most layout bugs before they start.

## CSS Selectors

A selector is the part of a CSS rule that sits before the curly braces. It tells the browser which elements should receive the declarations inside.

### Selector Types at a Glance

| Selector | Syntax | Matches |
|---|---|---|
| Universal | `*` | Every element |
| Type (element) | `p` | All `<p>` elements |
| Class | `.card` | Elements with `class="card"` |
| ID | `#main-nav` | The element with `id="main-nav"` |
| Attribute | `input[type="text"]` | `<input>` elements whose `type` is `"text"` |
| Descendant | `nav a` | Any `<a>` inside a `<nav>`, at any depth |
| Child | `ul > li` | `<li>` that is a direct child of `<ul>` |
| Adjacent sibling | `h2 + p` | A `<p>` immediately after an `<h2>` |
| Pseudo-class | `a:hover` | An `<a>` while the pointer is over it |
| Pseudo-element | `p::first-line` | The first rendered line of a `<p>` |

### A Realistic Example

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Selector Demo</title>
  <link rel="stylesheet" href="styles.css">
</head>
<body>
  <nav id="main-nav">
    <ul>
      <li><a href="/" class="active">Home</a></li>
      <li><a href="/about">About</a></li>
    </ul>
  </nav>
  <main>
    <h2>Welcome</h2>
    <p>First paragraph.</p>
    <p>Second paragraph.</p>
  </main>
</body>
</html>
```

```css
/* styles.css */

/* All links inside the nav */
#main-nav a {
  text-decoration: none;
  color: #334155;
}

/* Only the active link */
#main-nav a.active {
  color: #6366f1;
  font-weight: 600;
}

/* Links change colour on hover */
#main-nav a:hover {
  color: #4f46e5;
}

/* The paragraph immediately after an h2 */
h2 + p {
  font-size: 1.1rem;
  color: #475569;
}

/* Direct children li of the nav ul only */
#main-nav ul > li {
  display: inline-block;
  margin-right: 1rem;
}
```

### Specificity

When two rules target the same element, the one with higher **specificity** wins:

- Inline style `style="..."` — 1-0-0-0
- ID selector `#id` — 0-1-0-0
- Class / attribute / pseudo-class — 0-0-1-0
- Type / pseudo-element — 0-0-0-1

`.card .title` scores 0-0-2-0 and beats `h2` (0-0-0-1) for the same `<h2 class="title">` inside `.card`.

---

## The CSS Box Model

Every element is rendered as a rectangular box made of four layers, from innermost to outermost:

```
┌─────────────────────────────────┐
│             margin              │
│  ┌───────────────────────────┐  │
│  │          border           │  │
│  │  ┌─────────────────────┐  │  │
│  │  │       padding       │  │  │
│  │  │  ┌───────────────┐  │  │  │
│  │  │  │    content    │  │  │  │
│  │  │  └───────────────┘  │  │  │
│  │  └─────────────────────┘  │  │
│  └───────────────────────────┘  │
└─────────────────────────────────┘
```

- **Content** — the area where text and child elements render; sized by `width` and `height`.
- **Padding** — transparent space between the content and the border; background colour fills it.
- **Border** — a visible (or invisible) line around the padding.
- **Margin** — transparent space outside the border; does not inherit the background colour.

### `box-sizing`: the Most Important Setting

By default (`box-sizing: content-box`), `width` only covers the content area. Padding and border are added on top, making math awkward:

```css
/* content-box (default): actual rendered width = 200 + 20 + 4 = 224px */
.box-default {
  width: 200px;
  padding: 10px;
  border: 2px solid #6366f1;
}

/* border-box: actual rendered width stays exactly 200px */
.box-border {
  box-sizing: border-box;
  width: 200px;
  padding: 10px;
  border: 2px solid #6366f1;
}
```

Almost every modern project applies this reset globally:

```css
*, *::before, *::after {
  box-sizing: border-box;
}
```

With `border-box` active, the width you write is the width you get — padding and border are subtracted from the content area instead of added to the outside.

### Worked Sizing Example

```css
.card {
  box-sizing: border-box;
  width: 320px;
  padding: 24px;
  border: 1px solid #e2e8f0;
  margin: 16px auto;
}
```

The card occupies exactly **320 px** horizontally. Its content area is `320 - 2*(24) - 2*(1) = 270 px` wide. The `margin: 16px auto` adds 16 px above and below and centres the card horizontally inside its parent.

---

## Common Mistakes and Best Practices

- **Forgetting `box-sizing: border-box`.** Add the global reset at the top of your stylesheet; layout widths become predictable immediately.
- **Overusing ID selectors for styling.** IDs have very high specificity and are hard to override. Reserve them for JavaScript hooks and use classes for all styling.
- **Collapsing margins surprise.** Vertical margins between sibling block elements collapse to the larger of the two values. `margin-bottom: 24px` on an `<h2>` and `margin-top: 16px` on the next `<p>` produces a gap of 24 px, not 40 px.
- **Using `!important` to fix specificity wars.** Instead, restructure selectors to be more targeted. `!important` creates its own escalation problems.
- **Padding vs. margin for spacing.** Use padding to add space inside a component (affects background/border area). Use margin to push a component away from its siblings.

---

Mastering CSS selectors lets you target exactly the right elements without fighting specificity, while understanding the box model gives you precise control over spacing and layout — both are prerequisites for every CSS framework and design system you will encounter on the backend roadmap.
