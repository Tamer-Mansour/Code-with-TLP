# Semantic HTML and Forms

HTML is not just a markup language — it is a contract between your page and the browser, screen readers, search engines, and other developer tools. **Semantic HTML** means choosing elements that describe the *meaning* of content, not just its visual appearance. Semantic markup also makes your Spring Boot-rendered templates and REST-driven SPAs far easier to maintain.

---

## Semantic vs. Non-Semantic Elements

A `<div>` and a `<section>` can look identical on screen, but only `<section>` tells the browser (and assistive technology) "this is a thematically related block of content."

| Non-semantic | Semantic replacement | What it communicates |
|---|---|---|
| `<div id="header">` | `<header>` | Site or section header |
| `<div id="nav">` | `<nav>` | Primary navigation links |
| `<div id="main">` | `<main>` | The dominant page content |
| `<div class="article">` | `<article>` | Self-contained, shareable content |
| `<div class="sidebar">` | `<aside>` | Content tangentially related to the main body |
| `<div id="footer">` | `<footer>` | Footer for its nearest sectioning ancestor |
| `<b>` | `<strong>` | Strong importance (not just bold) |
| `<i>` | `<em>` | Stress emphasis (not just italics) |

### A Correctly Structured Page Skeleton

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Course Dashboard</title>
  <link rel="stylesheet" href="styles.css" />
</head>
<body>
  <header>
    <h1>Code with TLP</h1>
    <nav aria-label="Main navigation">
      <ul>
        <li><a href="/courses">Courses</a></li>
        <li><a href="/roadmap">Roadmap</a></li>
        <li><a href="/profile">Profile</a></li>
      </ul>
    </nav>
  </header>

  <main>
    <section aria-labelledby="progress-heading">
      <h2 id="progress-heading">Your Progress</h2>
      <!-- progress cards here -->
    </section>

    <article>
      <h2>Latest Lesson: Semantic HTML and Forms</h2>
      <p>Learn how to write HTML that makes sense to browsers and humans alike.</p>
    </article>
  </main>

  <aside>
    <h2>Quick Links</h2>
    <ul>
      <li><a href="/forum">Community Forum</a></li>
    </ul>
  </aside>

  <footer>
    <p>&copy; 2025 Code with TLP. All rights reserved.</p>
  </footer>
</body>
</html>
```

---

## HTML Forms

Forms are the primary way users send data to your Spring Boot backend. Every `<input>` type, attribute, and label has a purpose — misusing them breaks accessibility and browser autofill.

### Input Types That Matter

```html
<form action="/api/register" method="POST">

  <!-- Text: free-form single-line input -->
  <label for="username">Username</label>
  <input type="text" id="username" name="username"
         minlength="3" maxlength="30" required />

  <!-- Email: browser validates format, mobile shows @ keyboard -->
  <label for="email">Email</label>
  <input type="email" id="email" name="email" required />

  <!-- Password: value is masked, never autofilled as text -->
  <label for="password">Password</label>
  <input type="password" id="password" name="password"
         minlength="8" required />

  <!-- Number: spinner control, rejects non-numeric input -->
  <label for="age">Age</label>
  <input type="number" id="age" name="age" min="16" max="120" />

  <!-- Date: native date-picker in modern browsers -->
  <label for="dob">Date of Birth</label>
  <input type="date" id="dob" name="dob" />

  <!-- Checkbox -->
  <input type="checkbox" id="terms" name="terms" value="accepted" required />
  <label for="terms">I agree to the Terms of Service</label>

  <!-- Select (dropdown) -->
  <label for="role">Role</label>
  <select id="role" name="role">
    <option value="">-- choose --</option>
    <option value="student">Student</option>
    <option value="instructor">Instructor</option>
  </select>

  <!-- Textarea: multi-line text -->
  <label for="bio">Bio</label>
  <textarea id="bio" name="bio" rows="4" maxlength="500"></textarea>

  <button type="submit">Register</button>
</form>
```

### Why `<label>` Is Non-Negotiable

Every interactive control needs a `<label>` whose `for` attribute matches the input's `id`. Without it:

- Screen readers cannot announce what the field is for.
- Clicking the label text does not focus the input (reduced usability).
- Browser autofill heuristics become unreliable.

The two valid patterns are:

```html
<!-- Explicit association (preferred) -->
<label for="email">Email</label>
<input type="email" id="email" name="email" />

<!-- Implicit wrapping -->
<label>
  Email
  <input type="email" name="email" />
</label>
```

---

## Native Form Validation Attributes

The browser can reject invalid input *before* JavaScript or your Spring controller even runs.

| Attribute | Applicable to | What it enforces |
|---|---|---|
| `required` | All inputs | Field must not be empty on submit |
| `minlength` / `maxlength` | text, password, textarea | String length bounds |
| `min` / `max` | number, date, range | Numeric / date bounds |
| `pattern` | text, tel, url | Regex the value must match |
| `type="email"` | input | Must contain `@` and a domain |

Example — phone field that only accepts Egyptian mobile numbers:

```html
<label for="phone">Mobile (Egypt)</label>
<input type="tel" id="phone" name="phone"
       pattern="^01[0125][0-9]{8}$"
       placeholder="01XXXXXXXXX"
       required />
```

---

## Common Mistakes and Best Practices

- **Skipping `<label>`** — Always associate every input with a label. A placeholder is not a label; it disappears as soon as the user starts typing.
- **Using `<div>` for buttons** — `<button type="submit">` has built-in keyboard support and semantics; a `<div>` does not.
- **Wrong `method` on sensitive forms** — Registration and login forms must use `method="POST"`. `GET` puts credentials in the URL, in browser history, and in server logs.
- **Missing `<fieldset>` and `<legend>` on grouped controls** — Wrap radio buttons and related checkboxes in `<fieldset><legend>...</legend></fieldset>` so screen readers announce the group label.
- **Relying solely on client-side validation** — HTML validation is a convenience, not security. Always validate and sanitize input on the server (e.g., with Spring's `@Valid` and Bean Validation annotations).

---

## Summary

Semantic HTML replaces generic `<div>` containers with elements that carry meaning — improving accessibility, SEO, and maintainability. Forms built with correct `<label>` associations, appropriate `type` attributes, and native validation constraints give users a better experience and reduce the load on server-side validation logic.
