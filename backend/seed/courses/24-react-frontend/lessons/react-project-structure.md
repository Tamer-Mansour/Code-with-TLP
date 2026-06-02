# Project Structure and Best Practices

A clear folder structure and set of conventions keeps React projects maintainable as they grow. There is no single "correct" structure, but these patterns are widely adopted and scale well.

## Feature-First Structure (Recommended)

Group files by feature rather than by type. Everything related to a feature lives together:

```
src/
├── components/          # Truly shared, generic UI (Button, Modal, Input)
│   ├── Button.tsx
│   └── Modal.tsx
├── features/            # Self-contained feature modules
│   ├── auth/
│   │   ├── AuthProvider.tsx
│   │   ├── LoginForm.tsx
│   │   ├── useAuth.ts
│   │   └── auth.types.ts
│   ├── products/
│   │   ├── ProductList.tsx
│   │   ├── ProductCard.tsx
│   │   ├── useProducts.ts
│   │   └── products.api.ts
├── hooks/               # Cross-feature custom hooks
│   ├── useFetch.ts
│   └── useDebounce.ts
├── pages/               # Route-level components
│   ├── HomePage.tsx
│   ├── ProductsPage.tsx
│   └── NotFoundPage.tsx
├── lib/                 # Third-party wrappers, clients
│   ├── queryClient.ts
│   └── axiosClient.ts
├── types/               # Shared TypeScript types
│   └── api.types.ts
└── App.tsx
```

**Rule of thumb:** If a component is used in only one feature, it lives in that feature folder. If it's used in two or more features, it moves to `components/`.

## Naming Conventions

| Item | Convention | Example |
|------|-----------|---------|
| Component file | PascalCase | `UserCard.tsx` |
| Hook file | camelCase | `useUserData.ts` |
| Context file | PascalCase | `AuthContext.tsx` |
| Type/interface file | camelCase with `.types.ts` | `user.types.ts` |
| Test file | Same name + `.test.tsx` | `UserCard.test.tsx` |
| API function file | camelCase with `.api.ts` | `users.api.ts` |

## Component Design Principles

**1. Single Responsibility**
A component does one thing. If it handles data fetching *and* rendering *and* formatting, split it.

```tsx
// ❌ Too many responsibilities
function UserPage({ userId }) {
  const [user, setUser] = useState(null);
  useEffect(() => { fetch(`/api/users/${userId}`).then(…); }, [userId]);
  const formatted = formatUser(user);
  return <div>…complex JSX…</div>;
}

// ✓ Separated
function UserPage({ userId }) {
  const { data: user } = useQuery({ queryKey: ["user", userId], queryFn: … });
  return user ? <UserDetail user={user} /> : <Spinner />;
}
```

**2. Prefer Composition Over Configuration**

Pass children or render props instead of boolean flags that control internal layout:

```tsx
// ❌ Configuration flags
<Card showHeader showFooter footerContent={<Buttons />} />

// ✓ Composition
<Card>
  <Card.Header>Title</Card.Header>
  <Card.Body>Content</Card.Body>
  <Card.Footer><Buttons /></Card.Footer>
</Card>
```

**3. Co-locate State**
Keep state as close to where it's used as possible. Only lift state up when two sibling components genuinely need to share it.

## Environment Variables

Use `.env` files for configuration that changes between environments:

```bash
# .env.local  (never commit this)
VITE_API_URL=http://localhost:3000

# .env.production
VITE_API_URL=https://api.example.com
```

Access with `import.meta.env.VITE_API_URL` (all Vite env vars must start with `VITE_`).

## Performance Checklist

- [ ] Long lists use virtualization (`react-window` or `@tanstack/react-virtual`)
- [ ] Images are lazy-loaded (`loading="lazy"`)
- [ ] Code-split routes with `React.lazy` + `Suspense`
- [ ] Heavy components are memoized with `React.memo` only after profiling confirms a benefit
- [ ] No unnecessary `useEffect` for derived state — compute inline instead

## Code-Splitting with React.lazy

```tsx
import { lazy, Suspense } from "react";

const Dashboard = lazy(() => import("./pages/Dashboard"));

function App() {
  return (
    <Suspense fallback={<PageSpinner />}>
      <Routes>
        <Route path="/dashboard" element={<Dashboard />} />
      </Routes>
    </Suspense>
  );
}
```

Each lazily imported page becomes its own JS bundle, loaded only when the user navigates to that route — dramatically reducing the initial bundle size.

## Summary

- Feature-first folder structure scales better than type-first.
- Consistent naming (PascalCase components, camelCase hooks) reduces cognitive load.
- Keep state local; lift only when necessary.
- Code-split at the route level for fast initial loads.
- Measure before memoizing — React DevTools Profiler is your guide.
