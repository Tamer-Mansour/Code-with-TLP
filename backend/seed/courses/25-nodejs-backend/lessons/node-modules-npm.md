# Node Modules and npm Ecosystem

Node.js ships with a rich standard library, but the real power comes from npm — the world's largest package registry with over two million packages. Understanding how modules work and how to manage dependencies cleanly is foundational for any Node project.

## CommonJS vs ESM

Node supports two module systems. Modern projects should use **ESM** (ECMAScript Modules):

```js
// ESM — file must have .mjs extension OR package.json "type": "module"
import path from "node:path";
import { readFile } from "node:fs/promises";
import myLib from "./lib/myLib.js";     // must include extension
export const PI = 3.14;
export default function greet(name) { return `Hello ${name}`; }
```

```js
// CommonJS — legacy, still common in older packages
const path = require("path");
module.exports = { greet };
```

Key differences:

| Feature | ESM | CommonJS |
|---------|-----|---------|
| Syntax | `import` / `export` | `require` / `module.exports` |
| Loading | Asynchronous, static | Synchronous, dynamic |
| Top-level `await` | Yes | No |
| Tree-shaking | Yes | No |
| `__dirname` available | No (use `import.meta.dirname`) | Yes |

## The node: Protocol

Always prefix built-in modules with `node:` to make intent explicit and avoid name collisions with npm packages:

```js
import fs from "node:fs/promises";
import path from "node:path";
import crypto from "node:crypto";
import { EventEmitter } from "node:events";
```

## package.json Essentials

```json
{
  "name": "my-api",
  "version": "1.0.0",
  "type": "module",
  "engines": { "node": ">=20" },
  "scripts": {
    "dev": "node --watch src/server.js",
    "start": "node src/server.js",
    "test": "node --test src/**/*.test.js",
    "lint": "eslint ."
  },
  "dependencies": {
    "express": "^5.0.0",
    "zod": "^3.22.0"
  },
  "devDependencies": {
    "eslint": "^9.0.0"
  }
}
```

- `dependencies` — runtime packages shipped with the app.
- `devDependencies` — tools only needed during development (linters, test runners).
- `engines` — documents which Node versions are supported (CI should enforce this).

## Semantic Versioning

npm uses **semver**: `MAJOR.MINOR.PATCH`.

| Range | Meaning |
|-------|---------|
| `^5.0.0` | Accepts `>=5.0.0 <6.0.0` (minor + patch) |
| `~5.0.0` | Accepts `>=5.0.0 <5.1.0` (patch only) |
| `5.0.0` | Exact version |

Always commit your `package-lock.json`. It pins exact resolved versions so every environment installs the same tree.

## Useful npm Commands

```bash
npm install                   # install from package-lock.json
npm install express           # add runtime dep
npm install -D eslint         # add dev dep
npm update                    # update within semver ranges
npm outdated                  # see what can be updated
npm audit                     # check for security vulnerabilities
npm audit fix                 # auto-fix safe vulnerabilities
npx <tool>                    # run a package without installing globally
```

## Structuring a Node Project

A clean layout keeps large apps navigable:

```
my-api/
  src/
    server.js        ← entry, boot logic
    app.js           ← Express app (no listen — easier to test)
    routes/
      users.js
      posts.js
    middleware/
      auth.js
      validate.js
    services/
      userService.js  ← business logic, no HTTP
    db/
      client.js       ← DB connection singleton
  tests/
  package.json
```

Separate HTTP concerns (routes, middleware) from business logic (services). Your services should be testable without spinning up a server.

## Avoiding Common pitfalls

- Do not use `require()` and `import` in the same file.
- Lock your Node version in `.nvmrc` or `package.json#engines` and match it in CI.
- Run `npm audit` in CI — fail the build on critical vulnerabilities.
- Prefer `node:` built-ins over third-party packages for simple tasks (file reading, hashing, URL parsing).
