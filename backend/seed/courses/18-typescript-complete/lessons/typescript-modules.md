# TypeScript Modules and Namespaces

TypeScript uses the ES module system (`import`/`export`) as its primary module format and adds declaration files (`.d.ts`) for interoperability with JavaScript libraries.

## ES module syntax

```ts
// math.ts — named exports
export function add(a: number, b: number): number {
  return a + b;
}

export const PI = 3.14159;

export type Point = { x: number; y: number };
```

```ts
// main.ts — named imports
import { add, PI, type Point } from "./math";

const p: Point = { x: PI, y: add(1, 2) };
```

`import type` (or `import { type X }`) is a type-only import erased at compile time — useful for avoiding circular runtime dependencies.

## Default exports

```ts
// logger.ts
export default class Logger {
  log(msg: string) { console.log(msg); }
}

// app.ts
import Logger from "./logger";
new Logger().log("hello");
```

Prefer named exports in libraries — default exports can't be re-exported under their original name without aliasing.

## Re-exporting

```ts
// index.ts — public API barrel
export { add, PI } from "./math";
export type { Point } from "./math";
export { default as Logger } from "./logger";
```

Barrel files aggregate a module's public API, letting consumers import from one path instead of many.

## Module resolution

TypeScript uses `moduleResolution` in `tsconfig.json`:

| Setting | Works with |
|---|---|
| `"node"` | CommonJS (Node 12 and below) |
| `"node16"` / `"nodenext"` | ESM in Node 16+ (requires `.js` extensions in imports) |
| `"bundler"` | Vite, webpack, esbuild (no extension required) |

For Node ESM projects you must write `import { x } from "./math.js"` (`.js` even for `.ts` source files). The `"bundler"` setting is more permissive.

## Declaration files (`.d.ts`)

When consuming a plain-JS library, TypeScript needs a `.d.ts` file describing its types:

```ts
// types/my-lib.d.ts
declare module "my-lib" {
  export function greet(name: string): string;
  export const version: string;
}
```

Most popular libraries ship types automatically or via `@types/` packages:

```bash
npm install --save-dev @types/lodash
```

## Ambient declarations

For globals injected by a bundler or runtime (e.g., `__DEV__`, `process.env`):

```ts
// global.d.ts
declare const __DEV__: boolean;

declare namespace NodeJS {
  interface ProcessEnv {
    NODE_ENV: "development" | "production" | "test";
    DATABASE_URL: string;
  }
}
```

Place `global.d.ts` anywhere included by `tsconfig.json`; no import needed.

## Namespaces (legacy)

Namespaces (formerly "internal modules") were the pre-ES-modules solution for organising code:

```ts
namespace Geometry {
  export interface Point { x: number; y: number }
  export function distance(a: Point, b: Point): number {
    return Math.hypot(a.x - b.x, a.y - b.y);
  }
}

const d = Geometry.distance({ x: 0, y: 0 }, { x: 3, y: 4 });  // 5
```

Prefer ES modules in new code. Namespaces still appear in older codebases and in some `.d.ts` files for global APIs (e.g., `lib.dom.d.ts`).

## `paths` and path aliases

`tsconfig.json` `paths` maps import aliases to directories:

```json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@app/*": ["src/*"],
      "@utils/*": ["src/utils/*"]
    }
  }
}
```

```ts
import { formatDate } from "@utils/date";  // resolves to src/utils/date.ts
```

Your bundler (Vite, webpack, etc.) needs a matching alias configured separately — `paths` only affects type-checking.

## Key takeaways

- Use ES module `import`/`export` for all new code.
- `import type` avoids circular runtime dependencies and reduces bundle size.
- Barrel files (`index.ts`) simplify public API surfaces.
- `moduleResolution: "bundler"` is the easiest setting for modern front-end projects.
- Namespaces are largely superseded by ES modules but still appear in `.d.ts` files.
