# Landing Page — Implementation Plan

**App:** Code with TLP · **Goal:** a modern, animated marketing landing page that shows off every
feature · **Drafted:** 2026-05-27

A high-conversion public landing page (the new entry point for logged-out visitors) that presents
the whole product — courses, the code runner, data-structure visualizers, TLP Chat, and the
ranking system — with tasteful, performant animations, in the app's purple→blue gradient style.

---

## 1. Stack & constraints

- **Angular 21 standalone** · **Tailwind only** (no component CSS files; shared styles via
  `styles.scss` `@apply`) · new control flow `@if/@for` · **lucide-angular** icons · CSS-variable
  light/dark theming · matches the existing gradient/soft look.
- **Routing change:** `/` currently redirects to `/catalog`. New rule: **`/` = landing page for
  guests; authenticated users auto-redirect** to `/dashboard` (or `/catalog`). Add `/login` &
  `/register` CTAs throughout.
- **Animation philosophy:** mostly **pure CSS keyframes + an IntersectionObserver reveal
  directive** (zero heavy deps). Always honor **`prefers-reduced-motion`**.

---

## 2. Page structure (top → bottom)

```
┌───────────────────────────────────────────────────────────────┐
│ 0. Sticky navbar  (transparent → solid on scroll, theme toggle) │
├───────────────────────────────────────────────────────────────┤
│ 1. HERO  — headline + typed subline + CTAs                      │
│           animated gradient-mesh bg · floating blobs · grid     │
│           visual: live code editor mock running tests ✓         │
├───────────────────────────────────────────────────────────────┤
│ 2. STATS BAR — animated count-up (courses / lessons / …)        │
├───────────────────────────────────────────────────────────────┤
│ 3. FEATURE BENTO — every feature as an animated card            │
├───────────────────────────────────────────────────────────────┤
│ 4. HOW IT WORKS — 3-step animated stepper                       │
├───────────────────────────────────────────────────────────────┤
│ 5. CURRICULUM — subjects grid + course-name marquee             │
├───────────────────────────────────────────────────────────────┤
│ 6. PLAYGROUND TEASER — mini Monaco "Run → tests pass" demo       │
├───────────────────────────────────────────────────────────────┤
│ 7. VISUALIZER TEASER — live array sort + tree insert animation  │
├───────────────────────────────────────────────────────────────┤
│ 8. TLP CHAT TEASER — animated AI chat explaining progress       │
├───────────────────────────────────────────────────────────────┤
│ 9. RANKS & GAMIFICATION — 8 tiers, glowing/shimmering badge     │
├───────────────────────────────────────────────────────────────┤
│ 10. TESTIMONIALS — auto-scroll marquee of cards                 │
├───────────────────────────────────────────────────────────────┤
│ 11. FAQ — accordion                                             │
├───────────────────────────────────────────────────────────────┤
│ 12. FINAL CTA — big gradient banner "Start learning today"      │
├───────────────────────────────────────────────────────────────┤
│ 13. FOOTER — links · social · theme · newsletter                │
└───────────────────────────────────────────────────────────────┘
```

---

## 3. Section-by-section content

| # | Section | Content & what it showcases |
|---|---|---|
| 0 | **Navbar** | Logo (TLP), anchor links (Features · Courses · Visualize · Pricing · FAQ) with scroll-spy, theme toggle, **Log in** + **Get started** (gradient) buttons. Transparent over hero → frosted/solid on scroll. |
| 1 | **Hero** | Big gradient headline ("Master Computer Science by *doing* it"), typed rotating subline, two CTAs (Start free · See a demo), trust line. Right side: a faux code editor card that **types code and shows test cases turning green**. |
| 2 | **Stats** | Animated counters: **14 courses · 10 subjects · 109 modules · 407 lessons · 149 challenges · 5 languages**. Count-up when scrolled into view. |
| 3 | **Feature bento** | Asymmetric bento grid, each tile an animated mini-demo: Interactive coding (Monaco + runner) · A–Z CS curriculum · LeetCode-style challenges + test cases · **Data-structure visualizers** · **TLP Chat AI** · Steam-style ranks · Progress dashboard · Dark/light themes. |
| 4 | **How it works** | 3 steps with connecting animated line: **Pick a path → Learn & practice → Track & rank up.** Icons animate on reveal. |
| 5 | **Curriculum** | Subject cards using each subject's gradient/color accent; an infinite **marquee** of course titles (Intro to CS, Data Structures, OS, Networks, AI/ML, …). |
| 6 | **Playground teaser** | Small embedded Monaco (or styled mock) that runs a snippet → animated test panel "3/3 passed". Reuses the real editor look. |
| 7 | **Visualizer teaser** | Auto-playing **array bubble-sort** + **BST insert** animations (the engine from `ds-animations-demo.html`), looping subtly. "See algorithms come alive." |
| 8 | **TLP Chat teaser** | Animated chat thread: user asks "How am I doing?", AI streams a progress summary with citation chips. Shows the RAG assistant value. |
| 9 | **Ranks** | The 8 tiers (Newcomer → Legend) with an animated badge using the existing **glow-pulse / shimmer** keyframes; XP/score bar fills on reveal. |
| 10 | **Testimonials** | Card marquee (two rows, opposite directions, pause on hover). |
| 11 | **FAQ** | Accordion (animated expand). |
| 12 | **Final CTA** | Full-width gradient banner with floating particles + "Create your free account". |
| 13 | **Footer** | Product/Resources/Legal columns, socials, theme toggle, newsletter input, copyright. |

---

## 4. Animation catalog

| Animation | Where | How |
|---|---|---|
| **Reveal on scroll** (fade/slide/stagger) | every section | reusable `appReveal` directive (IntersectionObserver) toggling a class |
| **Animated gradient mesh** + floating blobs | hero, final CTA | CSS keyframes on layered radial-gradients; `filter: blur` blobs drifting |
| **Animated grid background** | hero | reuse existing `.bg-grid` utility + slow pan |
| **Typed text** | hero subline | tiny typewriter (no lib) cycling phrases |
| **Code-typing + test pass** | hero, playground | timed token reveal → checkmarks flip green |
| **Count-up numbers** | stats | `appCountUp` directive, eased, triggers on view |
| **Bento hover** | features | gradient-border (existing trick), subtle tilt/scale, inner micro-demo loops |
| **Infinite marquee** | curriculum, testimonials | duplicated track + CSS translate loop, pause on hover |
| **Live DS animations** | visualizer teaser | port the demo's frame/player engine; autoplay loop |
| **Streaming chat** | chat teaser | sequential bubble reveal + token fade-in |
| **Rank glow / shimmer** | ranks | existing `rank-glow-pulse` + `rank-shimmer` keyframes |
| **Parallax / spotlight** | hero, sections | scroll-linked transform; optional cursor-follow radial glow |
| **Scroll-spy + smooth scroll** | navbar | IntersectionObserver highlights active anchor |
| **Reduced motion** | global | `@media (prefers-reduced-motion)` disables non-essential motion |

---

## 5. Component structure

```
frontend/src/app/features/landing/
  landing.component.ts/html              # page shell, assembles sections
  sections/
    landing-navbar/  hero/  stats/  features-bento/  how-it-works/
    curriculum/  playground-teaser/  visualizer-teaser/  chat-teaser/
    ranks/  testimonials/  faq/  final-cta/  landing-footer/
  shared/
    reveal.directive.ts                  # IntersectionObserver reveal
    count-up.directive.ts                # animated counters
    gradient-bg/                         # reusable animated background
    marquee/                             # infinite scroll strip
```

- Each section is a small standalone component → easy to **parallelize across agents** once the
  shell + shared directives exist.
- Reuse: existing lucide registration, theme service, gradient button styles, and the visualizer
  engine for the teaser.

---

## 6. Routing & auth behavior

- `/` → **LandingComponent** (public). Logged-in users hitting `/` are redirected to
  `/dashboard`/`/catalog` via a resolver/guard.
- Anchor sections use fragment routing (`/#features`) with smooth scroll.
- All CTAs route to `/register` (primary) and `/login` (secondary).

---

## 7. SEO, performance, accessibility

- **SEO:** add **Angular SSR / prerender** for the landing route, `<title>`/meta description,
  **Open Graph + Twitter cards**, JSON-LD (Course/Organization), sitemap, canonical.
- **Performance:** lazy-load below-the-fold sections, use the **Gemini-generated background images**
  (from `seed/image_prompts`) in modern formats with `loading="lazy"`, defer the Monaco teaser until
  visible, keep the animation engine lightweight, hit a Lighthouse ≥ 90 budget.
- **Accessibility:** honor `prefers-reduced-motion`, keyboard-navigable, focus-visible rings,
  sufficient contrast (carry over the recent contrast fixes), semantic landmarks, alt text.
- **Responsive:** mobile-first; bento collapses to single column; marquees slow/disable on mobile.

---

## 8. Tech decisions (recommended)

- **No heavy animation library** for v1 — a `reveal` directive + CSS keyframes covers ~90%.
  If richer sequencing is needed later, add **Motion One** (tiny, framework-agnostic) rather than
  GSAP; use **Lottie** only for a hero illustration if desired.
- **Reuse the visualizer engine** for the live teaser (don't rebuild).
- **SSR/prerender** specifically for `/` (and maybe `/catalog`) for SEO; the app stays SPA elsewhere.
- Build the **shell + shared directives first**, then fan out sections to agents.

---

## 9. Phased roadmap

| Phase | Deliverable |
|---|---|
| **1 — Skeleton** | routing (`/` = landing, guard redirect), landing shell, `reveal` + `count-up` directives, **navbar + hero + footer**, animated gradient bg. |
| **2 — Core sections** | stats, feature bento, how-it-works, curriculum + marquee. |
| **3 — Live teasers** | playground (Monaco), visualizer (DS animation), TLP Chat teaser. |
| **4 — Conversion + polish** | ranks, testimonials, FAQ, final CTA; SSR/SEO meta, reduced-motion, perf budget, responsive QA. |

---

## 10. Open questions

- Is there a **pricing** section (it's free/personal) — show "Free & open" or omit pricing entirely?
- Are testimonials **real** or placeholder for now?
- Should the visualizer/chat teasers be **live components** or lightweight pre-rendered mockups for
  the first cut (faster, lighter)?
- Add **SSR** now (best for SEO) or ship SPA-only first and add prerendering later?
