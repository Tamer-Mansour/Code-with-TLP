# Responsive Design and Media Queries

Responsive design is the practice of building web pages that adapt their layout and appearance to fit any screen size — from a 320 px phone to a 4K monitor. Instead of maintaining separate sites for desktop and mobile, you write one codebase that reflows intelligently using CSS rules.

## The Viewport Meta Tag

Before any CSS takes effect on a mobile device, the browser must be told not to fake a desktop width. Add this tag to every HTML `<head>`:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Responsive Page</title>
  <link rel="stylesheet" href="styles.css">
</head>
<body>
  <header class="site-header">
    <nav class="nav">
      <a href="/">Home</a>
      <a href="/courses">Courses</a>
      <a href="/about">About</a>
    </nav>
  </header>
  <main class="container">
    <h1>Welcome</h1>
    <p>This layout adapts to any screen size.</p>
  </main>
</body>
</html>
```

Without `width=device-width` the browser renders the page at ~980 px and then scales it down, breaking all your breakpoints.

## Media Queries

A media query applies a CSS block only when a condition — typically the viewport width — is true.

```css
/* Base styles — mobile first */
.container {
  padding: 1rem;
  font-size: 1rem;
}

.nav {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

/* Tablet: 600 px and wider */
@media (min-width: 600px) {
  .container {
    max-width: 720px;
    margin: 0 auto;
  }

  .nav {
    flex-direction: row;
    gap: 1.5rem;
  }
}

/* Desktop: 1024 px and wider */
@media (min-width: 1024px) {
  .container {
    max-width: 1100px;
    padding: 2rem;
    font-size: 1.125rem;
  }
}
```

### Mobile-First vs. Desktop-First

| Approach | Starting point | Query direction | Recommended? |
|---|---|---|---|
| Mobile-first | Smallest screen | `min-width` — grow up | Yes |
| Desktop-first | Largest screen | `max-width` — shrink down | Legacy / avoid for new work |

Mobile-first is preferred because it forces you to prioritise content over decoration and typically produces lighter CSS.

## Responsive Fluid Grid with CSS Grid

Hard-coded pixel columns break on small screens. Use `auto-fill` + `minmax` to create a self-adjusting grid:

```css
.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1.5rem;
  padding: 1.5rem;
}

.card {
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 1.25rem;
}
```

On a 320 px phone this renders one column; on a 900 px tablet it renders three — no explicit breakpoints required.

## Responsive Images

Images need two attributes to behave well on all screens:

```html
<img
  src="course-banner.jpg"
  alt="Java Spring course banner"
  style="max-width: 100%; height: auto;"
/>
```

Or set it globally in your stylesheet:

```css
img, video {
  max-width: 100%;
  height: auto;
}
```

## Common Mistakes

- **Forgetting the viewport meta tag** — your media queries will appear to do nothing on a real device.
- **Mixing `min-width` and `max-width` without a plan** — breakpoints overlap and rules fight each other.
- **Using `px` for everything** — prefer `rem` for font sizes and `%` or `ch` for widths so the layout scales with the user's browser font setting.
- **Testing only in the browser's device toolbar** — always test on a real device or a hosted preview; the toolbar does not emulate touch, scroll inertia, or actual pixel density.

## Best Practices

- Define 2-3 breakpoints based on your content, not on specific device models.
- Keep your breakpoints in one place (CSS custom properties or a dedicated section at the top of the file).
- Use `clamp()` for fluid typography: `font-size: clamp(1rem, 2.5vw, 1.5rem);` scales smoothly between a minimum and maximum without any `@media` rule.

---

Responsive design combines the viewport meta tag, mobile-first media queries, and fluid layout techniques (Flexbox, Grid, relative units) to deliver a single codebase that works correctly on every screen size.
