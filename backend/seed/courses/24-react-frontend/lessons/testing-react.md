# Testing React Components

A tested React component is one you can refactor confidently. The standard testing stack is **Vitest** (or Jest) + **React Testing Library (RTL)**.

## Philosophy: Test Behaviour, Not Implementation

React Testing Library intentionally avoids exposing component internals. Instead, it queries the DOM the same way a user would:

> "The more your tests resemble the way your software is used, the more confidence they can give you." — Kent C. Dodds

Do **not** test:
- Which hooks are called
- Internal state values
- Which child components are rendered

**Do** test:
- What the user sees
- What happens when the user interacts

## Setup

```bash
npm install --save-dev vitest @testing-library/react @testing-library/user-event jsdom
```

In `vite.config.ts`:

```ts
test: { environment: "jsdom", globals: true, setupFiles: "./src/setupTests.ts" }
```

## Writing Your First Test

Component under test:

```tsx
// Counter.tsx
import { useState } from "react";
export function Counter() {
  const [count, setCount] = useState(0);
  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={() => setCount(c => c + 1)}>Increment</button>
    </div>
  );
}
```

Test:

```tsx
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { Counter } from "./Counter";

test("renders initial count of 0", () => {
  render(<Counter />);
  expect(screen.getByText("Count: 0")).toBeInTheDocument();
});

test("increments count when button is clicked", async () => {
  const user = userEvent.setup();
  render(<Counter />);
  await user.click(screen.getByRole("button", { name: /increment/i }));
  expect(screen.getByText("Count: 1")).toBeInTheDocument();
});
```

## Common Queries

| Query | Use when |
|-------|----------|
| `getByRole` | Accessible role exists (button, heading, textbox…) — **prefer this** |
| `getByText` | Element with visible text |
| `getByLabelText` | Form input with a label |
| `getByPlaceholderText` | Input with placeholder (fallback) |
| `findByRole` | Async — element appears after loading |
| `queryByRole` | Expect element to be absent (`null` if missing) |

## Testing Async Behaviour

```tsx
test("shows user name after loading", async () => {
  // Mock fetch
  global.fetch = vi.fn().mockResolvedValue({
    ok: true,
    json: async () => ({ id: 1, name: "Alice" }),
  });

  render(<UserProfile userId={1} />);

  expect(screen.getByText(/loading/i)).toBeInTheDocument();

  // Wait for async update
  expect(await screen.findByText("Alice")).toBeInTheDocument();
});
```

## Testing with Context

Wrap the component in the required providers:

```tsx
function renderWithProviders(ui: React.ReactElement) {
  return render(<AuthProvider>{ui}</AuthProvider>);
}

test("shows logout button when authenticated", () => {
  renderWithProviders(<Nav />);
  // ...
});
```

Create a `test-utils.tsx` file that exports a custom `render` that wraps with all providers — then import from that file instead of `@testing-library/react`.

## What to Test

| Priority | Test type |
|----------|-----------|
| High | User-visible interactions (click, type, submit) |
| High | Conditional rendering (loading / error / success states) |
| Medium | Edge cases (empty list, long text, missing optional props) |
| Low | Style or className assertions |
| Never | Internal state, implementation details |

## Summary

- Use `@testing-library/react` + `userEvent` — they simulate real user interaction.
- Query by role first, then by label, then by text.
- Mock `fetch` (or use MSW) for async tests.
- Write a custom `renderWithProviders` helper for context-dependent components.
- Aim for confidence, not coverage metrics.
