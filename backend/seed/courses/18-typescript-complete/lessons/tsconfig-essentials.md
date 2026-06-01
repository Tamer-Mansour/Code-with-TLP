# tsconfig Essentials

`tsconfig.json` controls the TypeScript compiler. Get a few flags right and your project is set for years.

## A solid starting tsconfig

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "Bundler",
    "lib": ["ES2022", "DOM"],
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "exactOptionalPropertyTypes": true,
    "noImplicitOverride": true,
    "noFallthroughCasesInSwitch": true,

    "esModuleInterop": true,
    "skipLibCheck": true,
    "isolatedModules": true,
    "verbatimModuleSyntax": true,
    "forceConsistentCasingInFileNames": true,

    "resolveJsonModule": true,
    "allowImportingTsExtensions": false,

    "outDir": "dist",
    "sourceMap": true,
    "declaration": true
  },
  "include": ["src"],
  "exclude": ["node_modules", "dist"]
}
```

## The non-negotiables

- **`strict: true`** — enables `strictNullChecks`, `noImplicitAny`, `strictFunctionTypes`, and more. The reason to use TypeScript.
- **`noUncheckedIndexedAccess`** — `arr[i]` is `T | undefined`. Catches array-bounds bugs.
- **`exactOptionalPropertyTypes`** — `{ x?: number }` doesn't let you assign `undefined` explicitly. Less surprising.
- **`isolatedModules`** — required by Vite, esbuild, swc. Disallows features they can't transpile.
- **`skipLibCheck`** — skip type-checking inside `node_modules`. Massive build speedup; almost everyone wants it.

## target

JS version to emit. With modern Node and modern browsers, `ES2022` (or `ES2023`) is safe.

## module / moduleResolution

- `module: "ESNext"` + `moduleResolution: "Bundler"` — for Vite, Webpack, esbuild, modern Node.
- `module: "NodeNext"` + `moduleResolution: "NodeNext"` — for pure Node projects without a bundler.

If you're publishing a library, pick `NodeNext`.

## Path aliases

```json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"]
    }
  }
}
```

```ts
import { foo } from "@/utils/foo";
```

Your bundler (Vite, Webpack) needs matching config — TS aliases don't affect runtime.

## Project references

Big monorepos? Split into projects:

```json
{
  "references": [{ "path": "../shared" }]
}
```

`tsc -b` builds them in dependency order incrementally.

## Watching

```bash
tsc --noEmit --watch
```

Type-check continuously without producing output. Pair with a dev server that handles transpilation (Vite, tsx).

## tsc --noEmit in CI

The standard CI check:

```yaml
- run: tsc --noEmit
```

Catches type errors without producing build artifacts.

## Mistakes to avoid

- **Disabling `strict`** "to get going quickly" — you'll regret it within a month.
- **`any` to silence errors** — usually hides a real bug. Use `unknown` and narrow.
- **`@ts-ignore` / `@ts-expect-error`** without a comment — leave a note for the next person.
- **Mixing CommonJS and ESM in the same project without intention** — pick one, configure once.
