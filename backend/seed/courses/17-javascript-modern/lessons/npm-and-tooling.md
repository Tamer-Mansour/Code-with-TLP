# npm, package.json, and Tooling

## package.json

The manifest at the root of every Node project:

```json
{
  "name": "my-app",
  "version": "1.0.0",
  "type": "module",
  "main": "./dist/index.js",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "test": "vitest"
  },
  "dependencies": {
    "react": "^18.3.0"
  },
  "devDependencies": {
    "vitest": "^1.6.0",
    "typescript": "^5.5.0"
  }
}
```

- `dependencies` — needed at runtime (deployed to prod).
- `devDependencies` — needed only at build/test time.

## Installing packages

```bash
npm install              # install everything in package.json
npm install react        # install + add to dependencies
npm install -D vitest    # add to devDependencies
npm uninstall lodash
npm outdated             # list packages with newer versions
npm update               # update within semver range
npm audit                # security advisories
npm ci                   # clean install from package-lock.json (CI use)
```

## package-lock.json

Pins **exact** versions of every transitive dependency. Commit it. Always use `npm ci` in CI for reproducible builds.

## Semver in version strings

```
"react": "18.3.1"     // exact
"react": "^18.3.1"    // compatible: ≥18.3.1 <19.0.0
"react": "~18.3.1"    // patch only: ≥18.3.1 <18.4.0
"react": "*"          // any (don't)
```

## npx — run packages without installing

```bash
npx create-vite my-app
npx eslint src/
```

Downloads on demand. Great for scaffolders.

## Scripts

`npm run X` runs the script named `X` in `package.json`. By convention:

```json
"scripts": {
  "dev": "vite",
  "build": "vite build",
  "preview": "vite preview",
  "test": "vitest",
  "test:ui": "vitest --ui",
  "lint": "eslint .",
  "format": "prettier --write ."
}
```

`pre-` and `post-` hooks auto-run:

```json
"prebuild": "npm run lint",
"build": "vite build"
```

## Alternatives to npm

| Tool   | Why                                                |
|--------|----------------------------------------------------|
| `pnpm` | Disk-efficient (hard-links), strict resolution.    |
| `yarn` | Faster than older npm; v4 has its own workspaces.  |
| `bun`  | All-in-one runtime + bundler + test runner. Fast.  |

`pnpm` is the most common choice in modern projects today. `npm` still works fine for most projects.

## Workspaces (monorepos)

Multiple packages in one repo with shared dev tooling:

```json
{
  "workspaces": ["packages/*", "apps/*"]
}
```

Tools that natively support workspaces: pnpm, npm 7+, yarn, Bun. Pair with **Turborepo** or **Nx** for task scheduling and remote caching.

## Tools you'll use daily

- **Vite** — dev server + bundler.
- **Vitest** — Jest-compatible test runner, fast.
- **ESLint** — linting.
- **Prettier** — formatting.
- **TypeScript** — types (next chapter's course covers this in depth).
- **tsx** / **bun** — run TS files directly.

## .gitignore must-haves

```
node_modules/
dist/
.env
.env.local
*.log
.DS_Store
```

Never commit `node_modules/`. Never commit `.env` files with secrets.
