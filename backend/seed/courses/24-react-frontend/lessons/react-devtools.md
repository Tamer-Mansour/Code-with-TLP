# React Developer Tools

React DevTools is a browser extension that lets you inspect the component tree, view props and state, profile renders, and debug your application in real time. It is one of the most useful tools in a React developer's workflow.

## Installation

Install the extension from your browser's extension store:

- **Chrome**: Search "React Developer Tools" in the Chrome Web Store.
- **Firefox**: Search in Firefox Add-ons.
- **Edge**: Available in the Microsoft Edge Add-ons store.

After installation, open the browser DevTools (`F12`) and you will see two new tabs: **Components** and **Profiler**.

## The Components Tab

The Components tab shows the full component tree of your running React app.

```
App
├── Header
│   └── Nav
├── main
│   ├── UserList
│   │   ├── UserCard (id=1)
│   │   ├── UserCard (id=2)
│   │   └── UserCard (id=3)
└── Footer
```

Click any component to see its:
- **Props** — the values passed in by the parent.
- **State** — all `useState` values and their current contents.
- **Hooks** — a list of all hooks the component uses, with current values.

You can also **edit props and state** live from the panel — great for testing edge cases without changing code.

## The Profiler Tab

The Profiler records render timings. Use it to find which components re-render too often or too slowly.

1. Click **Record** (circle icon).
2. Interact with your app.
3. Click **Stop**.
4. Inspect the flame graph — each bar is a component, width represents render time.

| Color | Meaning |
|-------|---------|
| Grey  | Did not render |
| Green | Rendered quickly |
| Yellow/Red | Rendered slowly — investigate |

## Tips for Daily Use

- **Highlight updates** — Enable "Highlight updates when components render" in DevTools settings. Components flash a colour every time they re-render, making unnecessary renders obvious.
- **Find a component quickly** — Click the target icon and hover over any element in the page; DevTools jumps to the corresponding component.
- **Check context values** — Context providers appear in the tree; click them to see the current value.

## Common Debugging Patterns

**Why is this component re-rendering?**

Enable "Record why each component rendered while profiling" in DevTools settings. After profiling, click a component to see the reason (prop change, state change, context change, or parent re-render).

**Verifying `memo` works**

Wrap a component with `React.memo`, then use the Profiler to confirm it no longer re-renders when its props haven't changed.

```tsx
const UserCard = React.memo(function UserCard({ user }) {
  return <li>{user.name}</li>;
});
```

In the Profiler, greyed-out `UserCard` entries confirm it was skipped.

## Summary

| Feature | Use for |
|---------|---------|
| Components tab | Inspect props, state, hooks |
| Profiler tab | Find slow or excessive renders |
| Highlight updates | Spot unnecessary re-renders visually |
| Live editing | Test UI states without restarting |

Make React DevTools part of every debugging session — catching a performance issue early is far cheaper than fixing it in production.
