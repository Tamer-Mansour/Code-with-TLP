# Project: Personal Portfolio Website

## Overview

In this project you'll build a **personal portfolio website** from scratch using **HTML5**, **CSS3**, and a sprinkle of **vanilla JavaScript (ES6+)**. The site presents who you are: a hero introduction, an about section, a grid of projects, a skills list, and a working contact form.

Why does this matter to a *backend* developer? Because you can't escape the browser. You'll wire up Spring controllers that return HTML, debug CSS layout issues in admin panels, and read front-end code your teammates write. A backend engineer who understands the box model, flexbox/grid, and the DOM is far more effective. This project also gives you a real artifact to host and share when you apply for jobs.

You'll write **static** files only — no server, no database yet. Everything runs by opening `index.html` in a browser.

## Learning Objectives

By the end of this project you will be able to:

- Structure a page with semantic HTML5 (`header`, `nav`, `main`, `section`, `footer`).
- Style a responsive layout using **CSS Flexbox** and **CSS Grid**.
- Apply a consistent design system with **CSS custom properties** (variables).
- Make the layout adapt to screen size with **media queries**.
- Add interactivity with vanilla JS: smooth scrolling, a mobile nav toggle, and client-side form validation.
- Organize a small front-end project into clean, separate files.

## Prerequisites & Setup

You need only a text editor and a browser. Git is recommended so you can version and later deploy the site.

```bash
mkdir portfolio && cd portfolio
git init
mkdir css js assets
type nul > index.html        # Windows; use 'touch index.html' on macOS/Linux
type nul > css/styles.css
type nul > js/main.js
```

Project structure:

```text
portfolio/
├── index.html
├── css/styles.css
├── js/main.js
└── assets/        (images, resume.pdf)
```

## Requirements

| # | Section   | Must contain                                              |
|---|-----------|-----------------------------------------------------------|
| 1 | Header/Nav| Site name + links to About, Projects, Skills, Contact     |
| 2 | Hero      | Your name, a one-line tagline, a call-to-action button    |
| 3 | About     | A short bio paragraph and a photo or avatar               |
| 4 | Projects  | A responsive grid of at least 3 project cards             |
| 5 | Skills    | A list/grid of technologies (Java, MySQL, Git, etc.)      |
| 6 | Contact   | A form with name, email, message + client-side validation |
| 7 | Footer    | Copyright and social links                                |

Rules:

- The layout must be **responsive** (usable on a 375px-wide phone and a desktop).
- Colors, spacing, and fonts must come from **CSS variables**, not magic numbers scattered everywhere.
- No CSS frameworks (no Bootstrap/Tailwind) — write your own CSS.

## Step-by-Step Tasks

### 1. Build the HTML skeleton

- [ ] Add the `<!DOCTYPE html>`, `lang`, charset, and viewport meta tags.
- [ ] Link the stylesheet and defer the script.
- [ ] Lay out semantic sections with `id`s the nav can target.

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Tamer Mansour — Backend Developer</title>
  <link rel="stylesheet" href="css/styles.css" />
  <script src="js/main.js" defer></script>
</head>
<body>
  <header class="site-header">
    <a href="#" class="logo">TLP.dev</a>
    <button class="nav-toggle" aria-label="Open menu">&#9776;</button>
    <nav class="nav"><ul>
      <li><a href="#about">About</a></li>
      <li><a href="#projects">Projects</a></li>
      <li><a href="#skills">Skills</a></li>
      <li><a href="#contact">Contact</a></li>
    </ul></nav>
  </header>
  <main>
    <section id="hero" class="hero">…</section>
    <section id="about">…</section>
    <section id="projects">…</section>
    <section id="skills">…</section>
    <section id="contact">…</section>
  </main>
  <footer>© 2026 Your Name</footer>
</body>
</html>
```

### 2. Define a design system with CSS variables

- [ ] Declare colors, font, and spacing on `:root`.
- [ ] Add a sensible reset and base typography.

```css
:root {
  --color-bg: #0f172a;
  --color-surface: #1e293b;
  --color-accent: #38bdf8;
  --color-text: #e2e8f0;
  --space: 1rem;
  --radius: 12px;
  --font: system-ui, "Segoe UI", Roboto, sans-serif;
}
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
  font-family: var(--font);
  background: var(--color-bg);
  color: var(--color-text);
  line-height: 1.6;
}
a { color: var(--color-accent); text-decoration: none; }
```

### 3. Lay out the header with Flexbox

- [ ] Use `display: flex` to push the logo left and nav right.
- [ ] Make the header `sticky` so it stays visible while scrolling.

```css
.site-header {
  position: sticky; top: 0;
  display: flex; align-items: center; justify-content: space-between;
  padding: var(--space) calc(var(--space) * 2);
  background: var(--color-surface);
}
.nav ul { display: flex; gap: var(--space); list-style: none; }
.nav-toggle { display: none; background: none; border: 0;
  color: var(--color-text); font-size: 1.5rem; cursor: pointer; }
```

### 4. Build the projects grid with CSS Grid

- [ ] Create reusable `.card` styling.
- [ ] Use `repeat(auto-fit, minmax(...))` so cards reflow automatically.

```css
.projects-grid {
  display: grid;
  gap: calc(var(--space) * 1.5);
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
}
.card {
  background: var(--color-surface);
  border-radius: var(--radius);
  padding: var(--space);
}
.card:hover { transform: translateY(-4px); transition: transform .2s; }
```

### 5. Make it responsive

- [ ] Hide the nav links and show the hamburger button under 768px.

```css
@media (max-width: 768px) {
  .nav-toggle { display: block; }
  .nav ul { display: none; flex-direction: column; }
  .nav ul.open { display: flex; }
}
```

### 6. Add interactivity with JavaScript

- [ ] Toggle the mobile nav.
- [ ] Validate the contact form on submit (no real backend yet).

```javascript
const toggle = document.querySelector(".nav-toggle");
const menu = document.querySelector(".nav ul");
toggle.addEventListener("click", () => menu.classList.toggle("open"));

const form = document.querySelector("#contact form");
form.addEventListener("submit", (e) => {
  e.preventDefault();
  const email = form.email.value.trim();
  const ok = /^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email);
  if (!form.name.value.trim() || !ok || !form.message.value.trim()) {
    alert("Please fill every field with a valid email.");
    return;
  }
  alert("Thanks! Your message is ready to send.");
  form.reset();
});
```

## Acceptance Criteria

- [ ] `index.html` validates as HTML5 and uses semantic sectioning elements.
- [ ] Nav links scroll to the correct section via matching `id`s.
- [ ] The header is sticky and laid out with Flexbox.
- [ ] Projects render in a Grid that reflows to one column on mobile.
- [ ] Colors, spacing, and fonts are driven by `:root` CSS variables.
- [ ] On a narrow screen the hamburger toggles the menu open/closed.
- [ ] The contact form blocks submission when a field is empty or the email is invalid.
- [ ] CSS and JS live in separate files; no inline `style=` or `onclick=` attributes.

## Stretch Challenges

1. Add a **dark/light theme toggle** that flips CSS variables and saves the choice in `localStorage`.
2. Animate sections into view on scroll using the **IntersectionObserver** API.
3. Make the projects load from a **`projects.json`** file via `fetch()` and render the cards dynamically.
4. Add a **print-friendly stylesheet** (`@media print`) so the page becomes a clean one-page resume.
5. **Deploy** the site for free with GitHub Pages and add the live URL to your README.

## Hints

- Set `scroll-behavior: smooth;` on `html` to get smooth anchor scrolling without any JS.
- Reach for **Flexbox** for one-dimensional rows (the navbar) and **Grid** for two-dimensional layouts (the project cards).
- `minmax(260px, 1fr)` means "at least 260px, otherwise share the leftover space equally" — this is the key to a fluid grid.
- Keep accessibility in mind: give the nav button an `aria-label`, use real `<label>` elements, and ensure text has enough contrast against the background.
- Prefer `defer` on your script tag so the DOM exists before `main.js` runs — no need for `DOMContentLoaded`.
