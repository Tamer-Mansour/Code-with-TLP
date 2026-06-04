# Component Tree Renderer

React organizes every UI as a **tree of components**. Understanding how components nest, who owns whom, and how data flows down the tree is foundational to building React applications.

## Why the Tree Matters

React renders UI by recursively evaluating components from the root downward. Each component can render other components, forming a parent-child hierarchy. When a parent re-renders, all of its children re-render too (unless protected by `React.memo`).

Understanding the tree helps you:

- Reason about data flow (props go from parent to child only).
- Identify where to lift state so that sibling components can share it.
- Spot prop drilling — props passed through components that don't use them.

## Example Tree

```
App
├── Header
├── Main
│   ├── ArticleList
│   │   └── ArticleCard
│   └── Sidebar
└── Footer
```

In code this looks like:

```tsx
function App() {
  return (
    <>
      <Header />
      <Main />
      <Footer />
    </>
  );
}

function Main() {
  return (
    <main>
      <ArticleList />
      <Sidebar />
    </main>
  );
}
```

## Reconciliation and Keys

React identifies each node in the tree by its **position** and **type**. When a list of items is rendered, React needs a `key` prop on each item so it can match nodes across re-renders without relying on position:

```tsx
{articles.map(a => <ArticleCard key={a.id} article={a} />)}
```

Without keys, inserting a new item at the top of the list causes React to re-render every card and lose any local state they held.

## Component Composition vs Inheritance

React favors **composition** over inheritance. Instead of extending components, you pass components as props or children:

```tsx
function Layout({ sidebar, children }) {
  return (
    <div className="layout">
      <aside>{sidebar}</aside>
      <main>{children}</main>
    </div>
  );
}

<Layout sidebar={<Navigation />}>
  <ArticleList />
</Layout>
```

This pattern produces flexible, reusable building blocks without deep class hierarchies.

## Practice Exercise

In the exercise below, you are given a flat list of parent-child relationships and must reconstruct the indented component tree. This mirrors the mental model React uses when it builds and traverses its internal fiber tree.

> **Further reading:** [react.dev — Thinking in React](https://react.dev/learn/thinking-in-react) walks through decomposing a UI mockup into a component hierarchy step by step.
