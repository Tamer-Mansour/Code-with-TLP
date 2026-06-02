# Gradual Migration from JavaScript to TypeScript

You rarely convert a whole codebase overnight. TypeScript is designed for incremental adoption: you can add it file-by-file while the rest remains JavaScript.

## Step 1 — Install TypeScript and create tsconfig

```bash
npm install --save-dev typescript
npx tsc --init
```

Start with a permissive config:

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "commonjs",
    "allowJs": true,           // compile .js files
    "checkJs": false,          // don't type-check .js yet
    "strict": false,           // turn on gradually
    "outDir": "dist",
    "rootDir": "src",
    "skipLibCheck": true
  },
  "include": ["src"]
}
```

`allowJs: true` lets TypeScript process both `.ts` and `.js` files in the same build.

## Step 2 — Rename files one at a time

Convert modules in dependency order (leaves first, then the modules that import them):

```
src/
  utils/format.js   →  utils/format.ts   (rename, fix errors)
  models/user.js    →  models/user.ts    (rename, add types)
  routes/auth.js    (still JS — untouched)
```

Run `tsc --noEmit` to type-check without producing output. Fix the errors in the converted file before moving on.

## Step 3 — Enable `checkJs` for remaining `.js` files

Once the `.ts` files are clean, add JSDoc types to critical `.js` files and enable `checkJs`:

```js
// utils/legacy.js
/**
 * @param {string} name
 * @returns {string}
 */
function greet(name) {
  return `Hello, ${name}!`;
}
```

```json
{
  "compilerOptions": {
    "checkJs": true
  }
}
```

JSDoc annotations give you type checking without renaming the file.

## Step 4 — Turn on strict flags incrementally

Enable flags one at a time rather than all at once:

| Flag | What it catches |
|---|---|
| `"strict": true` | All strict flags at once |
| `"noImplicitAny"` | Parameters inferred as `any` |
| `"strictNullChecks"` | `null`/`undefined` not assignable to other types |
| `"strictFunctionTypes"` | Contravariant function parameter checking |
| `"noUncheckedIndexedAccess"` | Array/object index access returns `T \| undefined` |

A common order: `strictNullChecks` → `noImplicitAny` → `strict: true` → `noUncheckedIndexedAccess`.

## Step 5 — Handle third-party JavaScript libraries

Install `@types/` packages for libraries that don't ship their own types:

```bash
npm install --save-dev @types/lodash @types/express @types/node
```

If no `@types/` package exists, write a minimal declaration file:

```ts
// types/untyped-lib.d.ts
declare module "untyped-lib" {
  export function doThing(input: string): void;
}
```

## Dealing with legacy patterns

### Dynamic property access

```ts
// Before: obj[key] where key is any string
const value = (obj as Record<string, unknown>)[key];
if (typeof value === "string") { /* use value */ }
```

### Callback-heavy code

Use `Parameters` and `ReturnType` to derive types from existing functions instead of rewriting them:

```ts
type OnDone = Parameters<typeof legacyFunction>[1];
```

### Third-party JS with unknown shape

```ts
const raw: unknown = JSON.parse(input);
// validate with Zod or a manual type guard before use
```

## Tracking progress

A good metric is the ratio of files converted and the TypeScript error count:

```bash
npx tsc --noEmit 2>&1 | grep "error TS" | wc -l
```

Set a goal (e.g., zero `noImplicitAny` errors) and track it in CI to prevent regressions.

## Key takeaways

- `allowJs` + `checkJs` + `strict: false` lets you migrate one file at a time.
- Convert dependency leaves first so each converted file's imports are already typed.
- Enable strict flags incrementally — `strictNullChecks` first gives the most value per effort.
- Use `@types/` packages and minimal `.d.ts` files for untyped dependencies.
- Automate error-count tracking in CI to measure progress.
