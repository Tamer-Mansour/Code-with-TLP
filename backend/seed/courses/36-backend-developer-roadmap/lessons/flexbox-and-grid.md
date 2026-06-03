# Layout with Flexbox and Grid

Modern CSS provides two purpose-built layout systems: **Flexbox** (one-dimensional, great for rows or columns of items) and **CSS Grid** (two-dimensional, great for full-page or card layouts). Every professional front-end — including the HTML pages you will serve from your Spring Boot application — relies on one or both.

## Flexbox at a Glance

Flexbox operates on a **container** and its direct **children** (flex items). You enable it with a single declaration on the parent.

```css
/* Container */
.card-row {
  display: flex;
  flex-direction: row;        /* default — main axis is horizontal */
  justify-content: space-between; /* distribute items along main axis */
  align-items: center;        /* align items on the cross axis */
  gap: 1rem;                  /* gutters between items (no negative margin hacks) */
  flex-wrap: wrap;            /* let items wrap to the next line if needed */
}

/* Item — override sizing for one child */
.card-row .featured {
  flex: 2;   /* takes twice as much free space as siblings with flex: 1 */
}
```

A minimal three-card row in HTML:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>Card Row</title>
  <link rel="stylesheet" href="styles.css" />
</head>
<body>
  <div class="card-row">
    <div class="card">Basics</div>
    <div class="card featured">Core Java</div>
    <div class="card">Spring Boot</div>
  </div>
</body>
</html>
```

### Key Flexbox Properties

| Property | Applied to | Effect |
|---|---|---|
| `display: flex` | container | activates Flexbox |
| `flex-direction` | container | `row` (default) or `column` |
| `justify-content` | container | main-axis alignment (`flex-start`, `center`, `space-between`, `space-around`, `space-evenly`) |
| `align-items` | container | cross-axis alignment (`stretch`, `center`, `flex-start`, `flex-end`) |
| `flex-wrap` | container | `nowrap` (default) or `wrap` |
| `gap` | container | space between items |
| `flex` | item | shorthand for `flex-grow flex-shrink flex-basis` |
| `align-self` | item | overrides `align-items` for one item |

## CSS Grid at a Glance

Grid lets you define explicit rows **and** columns, then place items into the resulting cells. It shines for two-dimensional layouts such as a dashboard, a lesson grid, or a page with a sidebar.

```css
/* 12-column fluid grid with a fixed sidebar */
.page-layout {
  display: grid;
  grid-template-columns: 240px 1fr; /* sidebar | main content */
  grid-template-rows: 64px 1fr auto; /* header | body | footer */
  grid-template-areas:
    "sidebar header"
    "sidebar main"
    "sidebar footer";
  min-height: 100vh;
  gap: 0;
}

.sidebar  { grid-area: sidebar; background: #1e293b; }
.header   { grid-area: header;  background: #0f172a; }
.main     { grid-area: main;    padding: 2rem; }
.footer   { grid-area: footer;  padding: 1rem; }
```

```html
<div class="page-layout">
  <nav class="sidebar">Nav</nav>
  <header class="header">Header</header>
  <main class="main">Content</main>
  <footer class="footer">Footer</footer>
</div>
```

### Responsive Card Grid with `auto-fill`

```css
.course-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 1.5rem;
}
```

`auto-fill` + `minmax` creates as many columns as fit, automatically adapting to the viewport — no media queries required for the column count.

## Flexbox vs Grid — When to Use Which

| Situation | Best choice |
|---|---|
| Single row or column of items | Flexbox |
| Navigation bar | Flexbox |
| Centering one element | Flexbox |
| Full-page layout (sidebar, header, footer) | Grid |
| Card/thumbnail gallery | Grid |
| Overlapping elements | Grid |
| Both axes need independent control | Grid |

You can nest them freely: use Grid for the page shell, Flexbox inside each card.

## Common Mistakes

- **Forgetting `flex-wrap: wrap`.** Without it, flex items shrink infinitely rather than wrapping on small screens.
- **Using `width` instead of `flex-basis`.** `flex-basis` participates in the flex algorithm; `width` fights it.
- **Implicit grid overflow.** If you place a Grid item beyond the defined rows/columns, the browser creates implicit tracks. Control their size with `grid-auto-rows` or `grid-auto-columns`.
- **Gap vs margin.** `gap` only adds space *between* items; it does not add space around the container edge. Use `padding` on the container for outer spacing.
- **Pixel-only column sizes.** Prefer `fr` units and `minmax()` so layouts adapt to all screen sizes without extra media queries.

## Best Practices

- Use CSS custom properties for spacing values so you only change one number site-wide.
- Combine `align-items: center` and `justify-content: center` on a flex container to perfectly center a single child.
- Use `grid-template-areas` with named strings — it makes the layout self-documenting and easy to rearrange.

---

Flexbox and Grid are complementary, not competing: reach for Flexbox when you have a list of items on one axis and Grid when you need to control two axes simultaneously. Together they cover every real-world layout you will encounter building UI for your Spring Boot projects.
