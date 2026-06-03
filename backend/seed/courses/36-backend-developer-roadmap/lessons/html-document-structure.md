# HTML Document Structure

Every HTML page follows a well-defined skeleton that browsers rely on to parse and render content correctly. Understanding this structure is the foundation of all web development work — front-end or back-end.

## The Minimal Valid HTML5 Document

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>My First Page</title>
  </head>
  <body>
    <h1>Hello, World!</h1>
    <p>This is a valid HTML5 document.</p>
  </body>
</html>
```

Every line here has a purpose — none are optional in production-quality code.

## Breaking Down Each Part

### `<!DOCTYPE html>`

This is a document type declaration, not a tag. It tells the browser to render the page in **standards mode** (HTML5). Without it the browser falls back to quirks mode, which interprets CSS and the box model differently across browsers — causing layout bugs that are hard to trace.

### `<html lang="en">`

The root element that wraps all content. The `lang` attribute declares the primary language of the page. Screen readers use it to pick the correct voice; search engines use it for language-targeted results.

### `<head>` — Metadata Section

The `<head>` is never displayed directly. It carries instructions for the browser and external services.

| Tag | Purpose |
|-----|---------|
| `<meta charset="UTF-8">` | Character encoding — supports all Unicode characters including Arabic, Chinese, emoji |
| `<meta name="viewport" ...>` | Makes the page responsive on mobile devices |
| `<title>` | Text shown in the browser tab and in search-engine result titles |
| `<link rel="stylesheet">` | Attaches an external CSS file |
| `<meta name="description">` | SEO snippet shown under the page title in search results |
| `<script>` | Embeds or links JavaScript (usually placed before `</body>`) |

### `<body>` — Content Section

Everything the user sees lives here: headings, paragraphs, images, forms, navigation, and scripts that manipulate the DOM.

## A More Complete Example

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <meta name="description" content="Course registration portal for Code with TLP." />
    <title>Course Registration – Code with TLP</title>
    <link rel="stylesheet" href="styles/main.css" />
  </head>
  <body>
    <header>
      <nav>
        <a href="/">Home</a>
        <a href="/courses">Courses</a>
      </nav>
    </header>

    <main>
      <h1>Register for a Course</h1>
      <form action="/register" method="POST">
        <label for="name">Full Name</label>
        <input type="text" id="name" name="name" required />
        <button type="submit">Register</button>
      </form>
    </main>

    <footer>
      <p>&copy; 2025 Code with TLP</p>
    </footer>

    <script src="scripts/main.js"></script>
  </body>
</html>
```

Notice that the `<script>` tag is placed just before `</body>`. This ensures the DOM elements are fully parsed before JavaScript tries to access them, avoiding `null` reference errors.

## Common Mistakes

- **Omitting `<!DOCTYPE html>`** — triggers quirks mode; CSS layout behaves unexpectedly.
- **Missing `charset` meta tag** — special characters render as garbled symbols (`Ã©` instead of `é`).
- **Missing `viewport` meta tag** — the page appears zoomed-out and unusable on phones.
- **Nesting block elements inside inline elements** — for example, placing a `<div>` inside a `<span>` is invalid HTML5 and produces unpredictable rendering.
- **Multiple `<h1>` tags** — while technically allowed in HTML5, using one `<h1>` per page remains the SEO and accessibility best practice.
- **Placing `<script>` in `<head>` without `defer`** — blocks page rendering; always use `defer` or move scripts to the end of `<body>`.

## Best Practices

- Always declare `lang` on `<html>` for accessibility compliance.
- Keep `<head>` metadata complete: charset, viewport, title, and description are the minimum for any production page.
- Use semantic sectioning elements (`<header>`, `<main>`, `<footer>`, `<section>`, `<article>`) inside `<body>` instead of generic `<div>` wrappers everywhere — this improves both accessibility and SEO.
- Validate your HTML with the [W3C Validator](https://validator.w3.org/) before deploying.

---

A well-formed HTML document structure is the contract between your markup and the browser; getting it right once means every CSS rule and JavaScript interaction you add later will behave predictably across all devices and browsers.
