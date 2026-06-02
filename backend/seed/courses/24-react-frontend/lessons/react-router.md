# React Router — Client-Side Navigation

React Router (v6) is the standard routing library for React. It maps URL paths to components, enabling single-page application navigation without full page reloads.

## Installation

```bash
npm install react-router-dom
```

## Basic Setup

Wrap the application in `<BrowserRouter>` and declare routes with `<Routes>` + `<Route>`:

```tsx
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Home from "./pages/Home";
import About from "./pages/About";
import NotFound from "./pages/NotFound";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/"       element={<Home />} />
        <Route path="/about"  element={<About />} />
        <Route path="*"       element={<NotFound />} />
      </Routes>
    </BrowserRouter>
  );
}
```

## Navigation

Use `<Link>` instead of `<a>` to avoid full page reloads:

```tsx
import { Link } from "react-router-dom";

function Nav() {
  return (
    <nav>
      <Link to="/">Home</Link>
      <Link to="/about">About</Link>
    </nav>
  );
}
```

For programmatic navigation (e.g., after form submission), use the `useNavigate` hook:

```tsx
import { useNavigate } from "react-router-dom";

function LoginForm() {
  const navigate = useNavigate();

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    await loginUser(/* ... */);
    navigate("/dashboard");       // redirect after login
  }
  // ...
}
```

## URL Parameters

Dynamic segments use `:paramName` syntax:

```tsx
<Route path="/users/:userId" element={<UserDetail />} />
```

Read the parameter with `useParams`:

```tsx
import { useParams } from "react-router-dom";

function UserDetail() {
  const { userId } = useParams<{ userId: string }>();
  // fetch user with userId
  return <div>User {userId}</div>;
}
```

## Nested Routes and Layouts

Nested routes let you share a layout (e.g., sidebar, navbar) across multiple pages:

```tsx
function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index        element={<Home />} />
          <Route path="users" element={<UserList />} />
          <Route path="users/:id" element={<UserDetail />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
```

The `<Layout>` component renders `<Outlet />` where child routes mount:

```tsx
import { Outlet } from "react-router-dom";

function Layout() {
  return (
    <>
      <header><Nav /></header>
      <main><Outlet /></main>
      <footer>…</footer>
    </>
  );
}
```

## Query Strings

Use `useSearchParams` to read and update query parameters:

```tsx
import { useSearchParams } from "react-router-dom";

function ProductList() {
  const [searchParams, setSearchParams] = useSearchParams();
  const page = Number(searchParams.get("page") ?? "1");

  return (
    <>
      <Products page={page} />
      <button onClick={() => setSearchParams({ page: String(page + 1) })}>
        Next
      </button>
    </>
  );
}
```

## Protected Routes

Create a wrapper component that redirects unauthenticated users:

```tsx
import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "./hooks/useAuth";

function PrivateRoute() {
  const { user } = useAuth();
  return user ? <Outlet /> : <Navigate to="/login" replace />;
}

// In your routes:
<Route element={<PrivateRoute />}>
  <Route path="/dashboard" element={<Dashboard />} />
  <Route path="/settings"  element={<Settings />} />
</Route>
```

## Route Summary

| Feature | API |
|---------|-----|
| Declare routes | `<Routes>` + `<Route>` |
| Link navigation | `<Link to="...">` |
| Programmatic navigation | `useNavigate()` |
| URL parameters | `useParams()` |
| Query string | `useSearchParams()` |
| Shared layout | `<Outlet />` in parent |
| Protected routes | Wrapper with `<Navigate>` |

React Router v6 is declarative, composable, and TypeScript-friendly. Mastering it unlocks clean URL-driven architecture for any React application.
