# Quiz: HTML & CSS

**Q1. Which HTML element is the correct container for all visible page content?**
- [ ] `<head>`
- [ ] `<html>`
- [x] `<body>`
- [ ] `<main>`

---

**Q2. What is the correct way to link an external CSS file named `styles.css` inside an HTML document?**
- [ ] `<style src="styles.css">`
- [ ] `<script href="styles.css" rel="stylesheet">`
- [x] `<link rel="stylesheet" href="styles.css">`
- [ ] `<css href="styles.css">`

---

**Q3. In the CSS Box Model, which property adds space between the element's border and its content?**
- [ ] `margin`
- [ ] `border-spacing`
- [ ] `outline`
- [x] `padding`

---

**Q4. Which CSS selector has the highest specificity?**
- [ ] A class selector, e.g. `.card`
- [ ] An element selector, e.g. `div`
- [ ] A pseudo-class selector, e.g. `:hover`
- [x] An ID selector, e.g. `#header`

---

**Q5. Consider the following HTML snippet. Which statement about semantic elements is correct?**

```html
<article>
  <h2>Spring Boot Basics</h2>
  <p>Spring Boot simplifies Java application setup.</p>
</article>
```

- [ ] `<article>` is purely decorative and has no effect on accessibility or SEO
- [x] `<article>` conveys independent, self-contained content to browsers, screen readers, and search engines
- [ ] `<article>` is deprecated in HTML5 and should be replaced with `<section>`
- [ ] `<article>` cannot contain heading elements like `<h2>`

---

**Q6. What does the following CSS rule do?**

```css
.container {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
```

- [ ] Stacks child elements vertically and centres them on the horizontal axis
- [ ] Distributes child elements evenly with equal margins on all sides
- [x] Places child elements in a row, spreads them to opposite ends of the container, and centres them vertically
- [ ] Creates a CSS Grid layout with two equal columns

---

**Q7. Which HTML5 input type triggers native date-picker UI in supporting browsers and automatically validates date format?**
- [ ] `<input type="text" pattern="\d{4}-\d{2}-\d{2}">`
- [x] `<input type="date">`
- [ ] `<input type="datetime">`
- [ ] `<input type="calendar">`

---

**Q8. A developer writes the following CSS. Which colour will the paragraph actually render?**

```html
<style>
  p            { color: blue; }
  .highlight   { color: green; }
  #intro       { color: red; }
</style>
<p id="intro" class="highlight">Hello</p>
```

- [ ] Blue — element selectors always win
- [ ] Green — class selectors override element selectors
- [x] Red — the ID selector has higher specificity than both the class and element selectors
- [ ] The browser cannot resolve the conflict and falls back to the default colour

---

**Q9. What is the purpose of the `alt` attribute on an `<img>` element?**
- [ ] It sets the image title shown in a tooltip on hover
- [ ] It preloads the image before the page renders
- [ ] It specifies a fallback image URL if the primary source fails
- [x] It provides alternative text for screen readers and displays when the image cannot be loaded, improving accessibility and SEO

---

**Q10. Which CSS property and value pair makes an element invisible but still occupies space in the layout?**
- [ ] `display: none`
- [x] `visibility: hidden`
- [ ] `opacity: 0` combined with `pointer-events: none`
- [ ] `position: absolute; left: -9999px`
