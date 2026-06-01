# ES Modules and CommonJS

JavaScript has **two** module systems. ES Modules (ESM) is the modern, standard one. CommonJS (CJS) is the legacy Node format. You'll meet both.

## ES Modules (ESM)

```javascript
// math.js
export function add(a, b) { return a + b; }
export const PI = 3.14;
export default function multiply(a, b) { return a * b; }
```

```javascript
// app.js
import multiply, { add, PI } from "./math.js";
import * as math from "./math.js";

console.log(add(1, 2));
console.log(math.PI);
```

- Static — imports/exports must be at the top level; the engine analyzes them before executing.
- Lazy by default — values are bindings, not copies. Mutations to an exported variable are visible to importers.
- Top-level `await` is allowed in ES modules.

## CommonJS (CJS)

```javascript
// math.js
function add(a, b) { return a + b; }
const PI = 3.14;

module.exports = { add, PI };
module.exports.default = function multiply(a, b) { return a * b; };
```

```javascript
// app.js
const { add, PI } = require("./math");
const math = require("./math");
```

- Dynamic — you can `require()` anywhere, even conditionally.
- Synchronous load (only on the server).
- Single namespace (`module.exports`), no first-class default export.

## In Node: how to pick

A package's format is determined by `package.json`:

```json
{ "type": "module" }      // .js files are ESM
{ "type": "commonjs" }    // .js files are CJS (default if omitted)
```

You can mix:

- `*.mjs` is always ESM.
- `*.cjs` is always CJS.

## Interop

You can `import` a CJS module from ESM:

```javascript
import lodash from "lodash";   // CJS default = the whole module
```

The reverse — `require` an ESM module from CJS — is *not* supported (use dynamic `await import()`):

```javascript
const { default: chalk } = await import("chalk");
```

This is why packages have been slowly migrating to ESM-only or shipping dual builds.

## In browsers: ESM in `<script>`

```html
<script type="module" src="./app.js"></script>
```

- `import` works.
- `defer` is implicit.
- Cross-origin loads require CORS headers.
- File paths must be **fully-qualified URLs or relative paths starting with `./` or `/`** — bare specifiers like `import "lodash"` don't work without an import map.

## Bundlers

Webpack, Vite, esbuild, Rollup, Parcel — all read your source modules, walk the import graph, and produce one or a few bundled JS files for the browser. They also:

- Transform JSX/TS.
- Inline small assets.
- Tree-shake unused exports.
- Code-split per route.

**Vite** is the modern default for new projects — dev mode is native ESM (no bundling), production builds use Rollup.

## Tree shaking

Static imports let bundlers see which exports you actually use:

```javascript
import { add } from "./math.js";       // only `add` is included
```

Dynamic imports (`require` or `await import()`) hide this, so bundlers must include everything.

## Practical rules

- New projects: ESM, full stop.
- Library you publish: ship both for maximum compatibility (or pure ESM if your audience can handle it — most modern tools can).
- Don't mix `require` and `import` in the same file.
- Use Vite for browser projects, plain ESM for Node 18+.
