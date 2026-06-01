# Why TypeScript?

TypeScript is JavaScript with a powerful static type system. Source is `.ts` / `.tsx`; the TypeScript compiler (`tsc`) **erases** the types and emits plain JS. The types live only at build time — there's no runtime cost.

## What TS buys you

- **Catches bugs earlier.** `Cannot read properties of undefined` shows up in your editor, not your error log.
- **Refactoring confidence.** Rename a field, see every caller break.
- **Self-documenting APIs.** Hover any function to see its types — no `@param` JSDoc rot.
- **Better autocomplete.** Editors know what fields exist on what objects.

## A first taste

```ts
function greet(name: string, greeting: string = "Hello"): string {
  return `${greeting}, ${name}`;
}

greet("Alice");           // OK
greet(42);                // Error: number not assignable to string
```

## Inference is doing a lot of the work

You don't need to annotate everything. TS infers most types:

```ts
const x = 5;              // x: 5 (literal!) or number, depending on context
const xs = [1, 2, 3];     // xs: number[]
const user = { name: "Alice", age: 30 };   // {name: string, age: number}
```

You typically annotate **function parameters and return types**, **public API surfaces**, and **state in classes/stores**. The rest is inferred.

## Strict mode is the only mode

```json
{ "compilerOptions": { "strict": true } }
```

This enables `noImplicitAny`, `strictNullChecks`, and friends. **Never start a project with strict off.** Disabling it later is hellish.

## TypeScript vs JSDoc

Modern JS has JSDoc comment-based types that VSCode can check. For tiny scripts, it's enough. For real codebases, TS gives you:

- More expressive types (generics, conditionals, mapped).
- Better refactor support.
- Faster checking.

## The ecosystem just speaks TypeScript

React, Vue, Angular, Next.js, Express, Vite, Vitest, Drizzle, Prisma, all major npm libraries — types either bundled in the package or in DefinitelyTyped (`@types/x`).

## Limitations to know

- Types don't exist at runtime. You can't `if (x instanceof Foo)` for an interface.
- Generics are erased.
- Bad types in 3rd-party packages can lead you astray (`any` propagates).
- The type system is **structural** (shape-based), not nominal — two interfaces with the same fields are interchangeable.

## When to skip TS

- Throwaway scripts.
- Prototype < 200 lines.
- Tutorial code that uses dynamic patterns to make a point.

For anything you'll maintain, TypeScript pays for itself within a week.
