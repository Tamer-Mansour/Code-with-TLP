---
name: tlp-ui
description: >
  Documents the Code with TLP design system and reusable UI component kit
  (Angular 21 standalone + Tailwind v3). Use this skill whenever you are
  building or modifying any UI element in the app — cards, buttons, toasts,
  checkboxes, switches, radio buttons, inputs, badges — so every new piece
  stays visually consistent with the established theme, gradient convention,
  and accessibility standards.
---

# TLP UI Kit — Design System Reference

## Stack

- Angular 21 (standalone components, signals, ControlValueAccessor)
- Tailwind CSS v3 (`darkMode: 'class'`)
- SCSS per-component stylesheets + global `styles.scss`
- Lucide Angular for icons (registered in `app.config.ts`)
- Fonts: Inter (sans), JetBrains Mono (mono)

---

## Theme Tokens

All tokens are CSS custom properties on `:root` (light) and `.dark` (dark).
Tailwind aliases them via `tailwind.config.js`.

| Token                  | Tailwind class          | Light value         | Dark value          |
|------------------------|-------------------------|---------------------|---------------------|
| `--color-app-bg`       | `bg-app-bg`             | zinc-50             | zinc-950            |
| `--color-app-surface`  | `bg-app-surface`        | white               | zinc-900            |
| `--color-app-surface-2`| `bg-app-surface-2`      | zinc-100            | zinc-800            |
| `--color-app-border`   | `border-app-border`     | zinc-200            | zinc-800            |
| `--color-app-border-2` | `border-app-border-2`   | zinc-300            | zinc-700            |
| `--color-app-text`     | `text-app-text`         | zinc-900            | zinc-50             |
| `--color-app-text-2`   | `text-app-text-2`       | zinc-600            | zinc-400            |
| `--color-app-text-muted`| `text-app-text-muted`  | zinc-400            | zinc-500            |
| brand                  | `text-brand`            | #3b82f6 (blue-500)  | same                |
| brand-dark             | `text-brand-dark`       | #2563eb (blue-600)  | same                |
| brand-light            | `text-brand-light`      | #60a5fa (blue-400)  | same                |

---

## Gradient Convention

The app's primary brand gradient is **purple-500 to blue-500** at 135 degrees:

```scss
background: linear-gradient(135deg, #8b5cf6, #3b82f6);
```

Tailwind shorthand: `bg-gradient-to-br from-purple-500 to-blue-500`

Use this gradient for:
- Checked/on states in form controls (checkbox, switch dot, radio dot)
- Primary button fill on hover
- Info toast accent and progress bar
- Any "active/selected" highlight element

Never use raw purple or blue in isolation for interactive states — always pair them as the gradient.

---

## Focus Ring Convention

All interactive elements must use:

```scss
box-shadow: 0 0 0 2px #3b82f6, 0 0 0 4px rgb(var(--color-app-bg));
```

Or via Tailwind: `focus-visible:ring-2 focus-visible:ring-brand focus-visible:ring-offset-2 focus-visible:ring-offset-app-bg`

---

## Component Catalog

### Toast — `app-toast-container`

**File:** `src/app/shared/components/toast-container/`

**Service API** (unchanged, use `ToastService`):

```typescript
toastService.success('Profile saved.');
toastService.error('Network error, please retry.');
toastService.warning('Session expiring soon.');
toastService.info('New contest starts in 10 minutes.', 6000);
toastService.remove(id);
```

**Variants:** `success` | `error` | `info` | `warning`

**Appearance:**
- Slides in from the right (cubic-bezier spring)
- Rounded card (`border-radius: 0.875rem`) on `bg-app-surface` with `shadow-popover`
- Left accent bar: gradient strip colored per variant
  - success: green gradient
  - error: red gradient
  - warning: amber gradient
  - info: purple-to-blue brand gradient
- Icon bubble (colored bg circle) with SVG path icon
- Title (bold) + message (muted smaller text)
- Close button top-right
- Shrinking progress bar at the bottom (auto-dismiss timer visualization)

**Accent colors per variant:**

| Variant  | Accent             | Icon bg tint                        |
|----------|--------------------|-------------------------------------|
| success  | green-500/600      | rgba(34,197,94, 0.12)               |
| error    | red-500/600        | rgba(239,68,68, 0.12)               |
| warning  | amber-400/600      | rgba(245,158,11, 0.12)              |
| info     | purple-500/blue-500| rgba(139,92,246, 0.12)              |

---

### Checkbox — `tlp-checkbox`

**File:** `src/app/shared/ui/tlp-checkbox/`

**Import:** `import { TlpCheckboxComponent } from '@app/shared/ui'`

**Inputs:**

| Input     | Type     | Default                  | Description                         |
|-----------|----------|--------------------------|-------------------------------------|
| `label`   | `string` | `''`                     | Text label beside the box           |
| `inputId` | `string` | auto-generated           | `id` for the hidden `<input>`       |

**ControlValueAccessor:** works with `ngModel` and reactive `FormControl<boolean>`.

**Usage:**

```html
<!-- Template-driven -->
<tlp-checkbox label="I agree to the terms" [(ngModel)]="agreed" />

<!-- Reactive -->
<tlp-checkbox label="Remember me" [formControl]="rememberCtrl" />

<!-- Custom label via content projection -->
<tlp-checkbox [formControl]="ctrl">
  Accept <a href="/terms" class="text-brand">Terms of Service</a>
</tlp-checkbox>
```

**Checked state:** box fills with `linear-gradient(135deg, #8b5cf6, #3b82f6)`, SVG checkmark draws in with a stroke-dashoffset animation, box springs in with scale pop.

---

### Switch — `tlp-switch`

**File:** `src/app/shared/ui/tlp-switch/`

**Import:** `import { TlpSwitchComponent } from '@app/shared/ui'`

**Inputs:**

| Input           | Type                   | Default   | Description                            |
|-----------------|------------------------|-----------|----------------------------------------|
| `label`         | `string`               | `''`      | Text label                             |
| `labelPosition` | `'before' \| 'after'`  | `'after'` | Where the label renders relative to track |
| `inputId`       | `string`               | auto      | `id` for the hidden checkbox           |

**ControlValueAccessor:** works with `ngModel` and reactive `FormControl<boolean>`.

**Usage:**

```html
<tlp-switch label="Dark mode" [(ngModel)]="darkMode" />
<tlp-switch label="Notifications" labelPosition="before" [formControl]="notifCtrl" />
```

**On state:** track fills with brand gradient, thumb slides right with a spring animation.

---

### Radio — `tlp-radio`

**File:** `src/app/shared/ui/tlp-radio/`

**Import:** `import { TlpRadioComponent } from '@app/shared/ui'`

**Inputs:**

| Input     | Type      | Default   | Description                              |
|-----------|-----------|-----------|------------------------------------------|
| `value`   | `unknown` | `null`    | The value this radio option represents   |
| `label`   | `string`  | `''`      | Text label                               |
| `name`    | `string`  | `''`      | Native `name` attribute for grouping     |
| `inputId` | `string`  | auto      | `id` for the hidden `<input>`            |

**ControlValueAccessor:** the form model holds the selected value; `writeValue` compares against `this.value` to set the selected state. Use one `FormControl` bound to multiple `tlp-radio` components with different `value` inputs.

**Usage:**

```html
<!-- Reactive form group -->
<tlp-radio value="easy"   label="Easy"   name="diff" [formControl]="diffCtrl" />
<tlp-radio value="medium" label="Medium" name="diff" [formControl]="diffCtrl" />
<tlp-radio value="hard"   label="Hard"   name="diff" [formControl]="diffCtrl" />

<!-- Template-driven -->
<tlp-radio value="python" label="Python" name="lang" [(ngModel)]="lang" />
<tlp-radio value="cpp"    label="C++"    name="lang" [(ngModel)]="lang" />
```

**Selected state:** outer ring gets a gradient border, inner dot pops in with scale animation, filled with brand gradient.

---

### Buttons — `.btn` classes (styles.scss)

No separate component; use CSS classes on any element.

```html
<button class="btn-primary">Submit</button>
<button class="btn-secondary">Cancel</button>
<button class="btn-ghost">Learn more</button>
<button class="btn-danger">Delete</button>

<!-- Sizes -->
<button class="btn-primary btn-sm">Small</button>
<button class="btn-primary btn-lg">Large</button>

<!-- Icon-only -->
<button class="btn-icon btn-ghost"><lucide-icon name="x" [size]="16" /></button>
```

| Class           | Appearance                                                       |
|-----------------|------------------------------------------------------------------|
| `btn-primary`   | Gradient border ring at rest; fills with gradient on hover       |
| `btn-secondary` | `bg-app-surface-2` with border; darkens on hover                 |
| `btn-ghost`     | Transparent; subtle bg on hover                                  |
| `btn-danger`    | `bg-red-600`; darkens on hover                                   |
| `btn-sm`        | Smaller padding + `text-xs`                                      |
| `btn-lg`        | Larger padding + `text-base`                                     |
| `btn-icon`      | Square padded, no label                                          |

---

### Cards — `.card` classes (styles.scss)

```html
<div class="card">Default card</div>
<div class="card-sm">Compact card</div>
<div class="card-hover">Card with hover lift</div>
```

---

### Inputs — `.input` classes (styles.scss)

```html
<input class="input" placeholder="Search..." />
<input class="input-error" />
<label class="label">Email</label>
```

---

## Accessibility Checklist

- All interactive controls have a hidden native `<input>` for keyboard + form compat
- Focus ring: `box-shadow` 2px brand + 4px bg offset (passes WCAG 2.4.11)
- `aria-checked`, `aria-label`, `role="switch"` applied where appropriate
- `disabled` state: `opacity: 0.5`, `pointer-events: none`, `cursor: not-allowed`
- Toasts use `aria-live="polite"` + `role="alert"`
- `@media (prefers-reduced-motion)` in `styles.scss` strips animations from reveal/marquee

---

## File Locations

| File                                                              | Owns                              |
|-------------------------------------------------------------------|-----------------------------------|
| `frontend/src/styles.scss`                                        | Global tokens, btn/card/input classes, shared keyframes |
| `frontend/src/app/shared/components/toast-container/`            | Toast card HTML + SCSS + TS       |
| `frontend/src/app/core/services/toast.service.ts`                 | Toast service API (do not modify) |
| `frontend/src/app/shared/ui/tlp-checkbox/`                        | TlpCheckboxComponent              |
| `frontend/src/app/shared/ui/tlp-switch/`                          | TlpSwitchComponent                |
| `frontend/src/app/shared/ui/tlp-radio/`                           | TlpRadioComponent                 |
| `frontend/src/app/shared/ui/index.ts`                             | Barrel export                     |
| `frontend/src/app/app.config.ts`                                  | Lucide icon registration          |
| `frontend/tailwind.config.js`                                     | Tailwind theme extension          |
