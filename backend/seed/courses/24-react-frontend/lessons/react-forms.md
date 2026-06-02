# Forms in React

Forms are one of the most common UI patterns. React gives you two approaches — **controlled** and **uncontrolled** inputs — and a growing ecosystem of form libraries on top.

## Controlled Inputs

A controlled input stores its value in React state and receives it back via the `value` prop:

```tsx
import { useState } from "react";

function LoginForm() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    console.log({ email, password });
  }

  return (
    <form onSubmit={handleSubmit}>
      <label>
        Email
        <input
          type="email"
          value={email}
          onChange={e => setEmail(e.target.value)}
        />
      </label>
      <label>
        Password
        <input
          type="password"
          value={password}
          onChange={e => setPassword(e.target.value)}
        />
      </label>
      <button type="submit">Log in</button>
    </form>
  );
}
```

Every keystroke triggers `onChange`, updates state, and causes a re-render. The DOM value is always in sync with React state — this is the "single source of truth" principle.

## Managing Multiple Fields with One State Object

For larger forms, one state object is cleaner than many `useState` calls:

```tsx
type FormData = { name: string; email: string; age: string };

function SignupForm() {
  const [form, setForm] = useState<FormData>({ name: "", email: "", age: "" });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setForm(f => ({ ...f, [name]: value }));
  };

  return (
    <form>
      <input name="name"  value={form.name}  onChange={handleChange} placeholder="Name" />
      <input name="email" value={form.email} onChange={handleChange} placeholder="Email" />
      <input name="age"   value={form.age}   onChange={handleChange} placeholder="Age" />
    </form>
  );
}
```

The `name` attribute on each input maps directly to the state key — a clean, scalable pattern.

## Validation

Basic inline validation — show errors only after the user has touched the field:

```tsx
function EmailField() {
  const [value, setValue] = useState("");
  const [touched, setTouched] = useState(false);

  const error = touched && !value.includes("@") ? "Invalid email" : "";

  return (
    <div>
      <input
        type="email"
        value={value}
        onChange={e => setValue(e.target.value)}
        onBlur={() => setTouched(true)}
      />
      {error && <span className="error">{error}</span>}
    </div>
  );
}
```

| Event | When to use |
|-------|-------------|
| `onChange` | Validate incrementally (e.g., password strength) |
| `onBlur` | Show error only after user leaves the field |
| `onSubmit` | Final validation gate before sending |

## Select and Checkbox

```tsx
// Select (dropdown)
const [role, setRole] = useState("viewer");
<select value={role} onChange={e => setRole(e.target.value)}>
  <option value="viewer">Viewer</option>
  <option value="editor">Editor</option>
  <option value="admin">Admin</option>
</select>

// Checkbox
const [agreed, setAgreed] = useState(false);
<input
  type="checkbox"
  checked={agreed}
  onChange={e => setAgreed(e.target.checked)}
/>
```

Note: use `checked` (not `value`) for checkboxes, and `e.target.checked`.

## Using React Hook Form

For production forms, **React Hook Form** reduces boilerplate and improves performance by using uncontrolled inputs internally:

```tsx
import { useForm } from "react-hook-form";

type Inputs = { email: string; password: string };

function LoginForm() {
  const { register, handleSubmit, formState: { errors } } = useForm<Inputs>();

  const onSubmit = (data: Inputs) => console.log(data);

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <input {...register("email", { required: "Email is required", pattern: { value: /\S+@\S+/, message: "Invalid email" } })} />
      {errors.email && <p>{errors.email.message}</p>}

      <input type="password" {...register("password", { minLength: { value: 8, message: "Min 8 chars" } })} />
      {errors.password && <p>{errors.password.message}</p>}

      <button type="submit">Log in</button>
    </form>
  );
}
```

Key benefits: minimal re-renders, built-in validation rules, easy integration with Zod via `@hookform/resolvers`.

## Summary

- Use controlled inputs for most forms — React state is the single source of truth.
- Use a single state object + dynamic `name` key for multi-field forms.
- Validate on `onBlur` for a good UX (not too eager, not too late).
- Reach for React Hook Form when forms get complex — it handles validation, submission, and error states cleanly.
