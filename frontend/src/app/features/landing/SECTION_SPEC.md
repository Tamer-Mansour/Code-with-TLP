# Landing Section — authoring contract

You are building ONE section of the Code with TLP landing page (Angular 21 standalone + Tailwind v3).
Read this fully, and READ the reference example before writing:
`frontend/src/app/features/landing/sections/landing-hero/landing-hero.ts` + `.html`.

## Files to create (only these two)
`frontend/src/app/features/landing/sections/<folder>/<file>.ts` and `.html`
- Standalone component, `ChangeDetectionStrategy.OnPush`, `templateUrl` (no inline template).
- Exact `selector`, `folder`, and class name are given in your task.

## Styling rules
- **Tailwind utility classes ONLY** — no component CSS files, no `<style>`.
- Use the **theme-aware tokens** (work in light + dark automatically):
  `bg-app-bg`, `bg-app-surface`, `bg-app-surface-2`, `border-app-border`, `border-app-border-2`,
  `text-app-text`, `text-app-text-2`, `text-app-text-muted`.
- Accent = purple→blue gradient: `bg-gradient-to-br from-purple-500 to-blue-500`, or `text-brand`
  (blue) / `text-gradient` utility for gradient text.
- Section wrapper: `<section [id]="..."?> <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 sm:py-28"> … </div></section>`.
- Use new control flow **`@if` / `@for`** (NEVER `*ngIf` / `*ngFor`). `@for` needs `track`.
- Fully responsive; mobile-first. Keep contrast strong in both themes.

## Animation (already available globally — just use the classes/directive)
- **Reveal on scroll:** import `RevealDirective` from `'../../shared/reveal.directive'`, add to imports,
  then put `appReveal` on elements (optionally `appReveal="left"|"right"|"scale"` and `[revealDelay]="120"`).
- Global CSS animation utilities you may add as classes: `anim-float`, `anim-pop`, `anim-blink`,
  `anim-mesh`, `text-gradient`, `bg-grid`, and **`.marquee-track`** (infinite scroll: a `flex w-max`
  container with the children duplicated once; it auto-scrolls and pauses on hover).
- Reduced-motion is handled globally — don't add your own media queries.

## Icons
- Import icon objects directly: `import { LucideAngularModule, Zap, Trophy, ... } from 'lucide-angular';`
  expose them as readonly fields, render `<lucide-icon [img]="Zap" [size]="18">`. Any lucide icon works.

## Hard rules
- Do NOT edit any other file (routing, landing.component, styles.scss, app.config, other sections).
  Only create your two files. The shell owner will import your component.
- All TS imports must be used; the project builds with strict template checks.
- No external libraries, no Monaco, no network calls — teasers are pure HTML/CSS/TS mockups.

## Validate
From `frontend/`, run `npm run build` is NOT your job (the shell owner builds). But make sure your
TS is valid and every binding/import resolves. Keep the component self-contained.
