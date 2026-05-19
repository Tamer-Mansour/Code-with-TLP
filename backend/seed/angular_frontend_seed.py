"""
Full seed for "Modern Frontend with Angular" course.
8 modules · 24 lessons · 9 exercises · 45+ test cases.

Prerequisites: run app/seed.py first — it creates the "web-development" subject
and the stub "modern-frontend-angular" course.

Run from the backend/ directory:
    python seed/angular_frontend_seed.py
"""
from __future__ import annotations
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import SessionLocal, engine
from app.models import (
    Base,
    Course,
    Difficulty,
    Exercise,
    Lesson,
    LessonType,
    Module,
    Subject,
    Tag,
    TestCase,
)

WEB_LANGS = ["python", "javascript", "typescript"]


# ─────────────────────────────────────────────
# Idempotent helpers
# ─────────────────────────────────────────────

def _subject(db: Session, slug: str) -> Subject:
    obj = db.scalar(select(Subject).where(Subject.slug == slug))
    return obj


def _course(db: Session, slug: str) -> Course:
    obj = db.scalar(select(Course).where(Course.slug == slug))
    return obj


def _module(db: Session, course: Course, title: str, order: int, summary: str = "") -> Module:
    obj = db.scalar(select(Module).where(Module.course_id == course.id, Module.title == title))
    if not obj:
        obj = Module(course_id=course.id, title=title, order_index=order, summary=summary)
        db.add(obj)
        db.flush()
    return obj


def _lesson(db: Session, mod: Module, slug: str, **kw) -> Lesson:
    obj = db.scalar(select(Lesson).where(Lesson.module_id == mod.id, Lesson.slug == slug))
    if not obj:
        obj = Lesson(module_id=mod.id, slug=slug, **kw)
        db.add(obj)
        db.flush()
    return obj


def _exercise(db: Session, lesson: Lesson, slug: str, **kw) -> tuple[Exercise, bool]:
    obj = db.scalar(select(Exercise).where(Exercise.slug == slug))
    if not obj:
        obj = Exercise(lesson_id=lesson.id, slug=slug, **kw)
        db.add(obj)
        db.flush()
        return obj, True
    return obj, False


def _cases(db: Session, ex: Exercise, cases: list) -> None:
    """Add (name, stdin, expected, hidden, weight) tuples if exercise is new."""
    if ex.test_cases:
        return
    for i, (name, stdin, expected, hidden, weight) in enumerate(cases):
        db.add(TestCase(
            exercise_id=ex.id,
            name=name,
            stdin=stdin,
            expected_stdout=expected,
            is_hidden=hidden,
            weight=weight,
            order_index=i,
        ))


# ════════════════════════════════════════════════════════════════
#  MODULE 1 — TypeScript Essentials
# ════════════════════════════════════════════════════════════════

M1_TYPES_MD = """\
# TypeScript Types and Interfaces

TypeScript adds a **static type system** on top of JavaScript. The compiler
catches type errors at build time — before code ever runs in a browser.

## Primitive Types

```typescript
let age: number = 30;
let name: string = "Angular";
let active: boolean = true;
let nothing: null = null;
let missing: undefined = undefined;
let anything: any = 42;        // escape hatch — avoid when possible
let safe: unknown = getData();  // safer than any — must narrow before use
```

## Type Inference

TypeScript infers types from assignments; you rarely need to annotate obvious
literals:

```typescript
let count = 0;         // inferred: number
let label = "hello";   // inferred: string
const PI = 3.14159;    // inferred: 3.14159 (literal type)
```

## Interfaces vs Type Aliases

| Feature | `interface` | `type` |
|---------|-------------|--------|
| Object shapes | Yes | Yes |
| Merging / extending | Declaration merging | Intersection `&` |
| Primitive aliases | No | Yes |
| Union types | No | Yes |
| Computed properties | No | Yes |

```typescript
// Interface — preferred for public API shapes
interface User {
  id: number;
  name: string;
  email?: string;  // optional field
}

// Type alias — needed for unions, tuples, primitives
type ID = string | number;
type Point = [number, number];
type Callback = (event: MouseEvent) => void;
```

## Union and Intersection Types

```typescript
// Union: value is one of the listed types
type Status = "loading" | "success" | "error";
type StringOrNumber = string | number;

// Intersection: value satisfies all listed types
type AdminUser = User & { role: "admin"; permissions: string[] };
```

## Generics Basics

Generics make code reusable without sacrificing type safety:

```typescript
function identity<T>(arg: T): T {
  return arg;
}

function firstItem<T>(arr: T[]): T | undefined {
  return arr[0];
}

// Usage
const result = identity<string>("hello");  // T = string
const first = firstItem([1, 2, 3]);        // T inferred as number
```

## Utility Types

TypeScript ships built-in mapped types for common transformations:

```typescript
interface Todo { title: string; done: boolean; priority: number; }

type PartialTodo  = Partial<Todo>;   // all fields optional
type ReadonlyTodo = Readonly<Todo>;  // all fields readonly
type TitleOnly    = Pick<Todo, "title">;
type NoTitle      = Omit<Todo, "title">;
type StringMap    = Record<string, string>;
```

Mastering these fundamentals is the foundation for writing idiomatic Angular
code where every service, component input, and API response is fully typed.
"""

M1_CLASSES_MD = """\
# Classes, Decorators, and Modules

## ES6 Classes in TypeScript

TypeScript classes extend ES6 with **access modifiers** and type annotations:

```typescript
class Animal {
  // Access modifiers: public (default), protected, private, readonly
  public  name: string;
  private _age: number;
  protected species: string;
  readonly id: number;

  constructor(name: string, age: number) {
    this.name = name;
    this._age = age;
    this.id = Math.random();
    this.species = "unknown";
  }

  // Shorthand: constructor parameter properties
  // constructor(public name: string, private _age: number) {}

  get age(): number { return this._age; }
  set age(v: number) {
    if (v < 0) throw new Error("Age cannot be negative");
    this._age = v;
  }
}
```

## Abstract Classes and Inheritance

```typescript
abstract class Shape {
  abstract area(): number;         // subclasses must implement
  describe(): string {
    return `This shape has area ${this.area().toFixed(2)}`;
  }
}

class Circle extends Shape {
  constructor(private radius: number) { super(); }
  area(): number { return Math.PI * this.radius ** 2; }
}

class Rectangle extends Shape {
  constructor(private w: number, private h: number) { super(); }
  area(): number { return this.w * this.h; }
}
```

## TypeScript Decorators

Decorators are a **metadata annotation** feature — they are functions applied
with `@` syntax to classes, methods, properties, or parameters. Angular uses
them extensively:

```typescript
// Class decorator
@Component({ selector: 'app-root', template: '<h1>Hello</h1>' })
class AppComponent {}

// Method decorator (example: timing decorator)
function Log(target: any, key: string, descriptor: PropertyDescriptor) {
  const original = descriptor.value;
  descriptor.value = function(...args: any[]) {
    console.time(key);
    const result = original.apply(this, args);
    console.timeEnd(key);
    return result;
  };
  return descriptor;
}

// Property decorator
@Input() title: string = '';
@Output() clicked = new EventEmitter<void>();
```

Decorators require `"experimentalDecorators": true` in `tsconfig.json`.
Angular's build pipeline handles this automatically.

## ES Modules

Modern Angular uses ES module `import`/`export` syntax throughout:

```typescript
// Named exports
export interface User { id: number; name: string; }
export function formatDate(d: Date): string { return d.toISOString(); }
export const VERSION = '17.0.0';

// Default export (use sparingly — harder to refactor)
export default class UserService { /* ... */ }

// Importing
import { User, formatDate } from './models/user';
import { Component, OnInit } from '@angular/core';
import type { HttpOptions } from '@angular/common/http'; // type-only import
```

## Barrel Files (index.ts)

Barrel files re-export from a folder to provide a clean public API:

```typescript
// src/app/models/index.ts
export { User } from './user.model';
export { Course } from './course.model';
export type { ApiResponse } from './api.types';

// Consuming code
import { User, Course } from './models';  // clean, no deep paths
```

This pattern is used heavily in Angular feature modules to keep import paths
short and refactoring surface small.
"""

M1_EXERCISE_MD = "Hands-on TypeScript exercises — type narrowing and generic data structures."


def seed_module1(db: Session, course: Course) -> None:
    mod = _module(db, course, "TypeScript Essentials", 1,
                  "Types, interfaces, generics, classes, decorators, and ES modules.")

    _lesson(db, mod, "typescript-types-interfaces",
            title="TypeScript Types and Interfaces",
            lesson_type=LessonType.reading,
            content_md=M1_TYPES_MD,
            duration_minutes=15,
            order_index=1)

    _lesson(db, mod, "classes-decorators-modules",
            title="Classes, Decorators, and Modules",
            lesson_type=LessonType.reading,
            content_md=M1_CLASSES_MD,
            duration_minutes=12,
            order_index=2)

    ex_lesson = _lesson(db, mod, "typescript-exercises",
                        title="TypeScript Exercises",
                        lesson_type=LessonType.exercise,
                        content_md=M1_EXERCISE_MD,
                        duration_minutes=20,
                        order_index=3)

    # ── Exercise 1.1: Type Narrowing ────────────────────────────────
    ex, _ = _exercise(db, ex_lesson, "ts-type-narrowing",
        title="Type Narrowing",
        prompt_md=(
            "# Type Narrowing\n\n"
            "Read a value that is either a **number** or a **string** and apply "
            "type-specific transformation:\n\n"
            "- If the token on the first line is `number`, read the second line as an "
            "integer and print `number: <doubled>`.\n"
            "- If the token is `string`, read the second line as text and print "
            "`string: <UPPERCASED>`.\n\n"
            "**Input:**\n```\ntype\nvalue\n```\n\n"
            "**Output:** one line following the rules above.\n\n"
            "**Examples**\n```\nInput:\nnumber\n5\nOutput:\nnumber: 10\n\n"
            "Input:\nstring\nhello\nOutput:\nstring: HELLO\n```"
        ),
        difficulty=Difficulty.easy,
        is_published=True,
        starter_code={
            "python": (
                "import sys\n\n"
                "lines = sys.stdin.read().splitlines()\n"
                "kind  = lines[0].strip()\n"
                "value = lines[1].strip()\n\n"
                "# TODO: if kind == 'number', print doubled; else print uppercased\n"
            ),
            "javascript": (
                "const lines = require('fs').readFileSync(0, 'utf8').trim().split('\\n');\n"
                "const kind  = lines[0].trim();\n"
                "const value = lines[1].trim();\n\n"
                "// TODO: narrow the type and apply the correct transformation\n"
            ),
            "typescript": (
                "import * as fs from 'fs';\n"
                "const lines = fs.readFileSync(0, 'utf8').trim().split('\\n');\n"
                "const kind  = lines[0].trim();\n"
                "const value = lines[1].trim();\n\n"
                "function transform(kind: string, value: string): string {\n"
                "    // TODO: return the correct output string\n"
                "    return '';\n"
                "}\n\n"
                "console.log(transform(kind, value));\n"
            ),
        },
        solution_code={
            "python": (
                "import sys\n"
                "lines = sys.stdin.read().splitlines()\n"
                "kind  = lines[0].strip()\n"
                "value = lines[1].strip()\n"
                "if kind == 'number':\n"
                "    print(f'number: {int(value) * 2}')\n"
                "else:\n"
                "    print(f'string: {value.upper()}')\n"
            ),
        },
        supported_languages=WEB_LANGS,
        time_limit_ms=3000,
        memory_limit_mb=256,
        points=10,
    )
    _cases(db, ex, [
        ("number-basic",    "number\n5\n",      "number: 10",    False, 1),
        ("string-basic",    "string\nhello\n",  "string: HELLO", False, 1),
        ("number-zero",     "number\n0\n",      "number: 0",     False, 1),
        ("string-mixed",    "string\nAngular\n","string: ANGULAR",False, 1),
        ("number-negative", "number\n-7\n",     "number: -14",   True,  2),
    ])

    # ── Exercise 1.2: Generic Stack ─────────────────────────────────
    ex, _ = _exercise(db, ex_lesson, "ts-generic-stack",
        title="Generic Stack",
        prompt_md=(
            "# Generic Stack\n\n"
            "Implement a stack that processes a sequence of commands:\n\n"
            "- `PUSH x` — push integer x onto the stack (no output)\n"
            "- `POP` — remove and print the top element, or `EMPTY` if stack is empty\n"
            "- `PEEK` — print the top element without removing it, or `EMPTY`\n"
            "- `SIZE` — print the current number of elements\n\n"
            "**Input:**\n```\nn\ncommand1\ncommand2\n...\n```\n"
            "First line is the number of commands n.\n\n"
            "**Output:** one line per non-PUSH command.\n\n"
            "**Example**\n```\nInput:\n5\nPUSH 3\nPUSH 7\nPEEK\nPOP\nSIZE\n\n"
            "Output:\n7\n7\n1\n```"
        ),
        difficulty=Difficulty.easy,
        is_published=True,
        starter_code={
            "python": (
                "import sys\n\n"
                "def main():\n"
                "    lines = sys.stdin.read().splitlines()\n"
                "    n = int(lines[0])\n"
                "    stack = []\n"
                "    for i in range(1, n + 1):\n"
                "        parts = lines[i].split()\n"
                "        cmd = parts[0]\n"
                "        if cmd == 'PUSH':\n"
                "            stack.append(int(parts[1]))\n"
                "        elif cmd == 'POP':\n"
                "            # TODO: pop and print, or EMPTY\n"
                "            pass\n"
                "        elif cmd == 'PEEK':\n"
                "            # TODO: peek and print, or EMPTY\n"
                "            pass\n"
                "        elif cmd == 'SIZE':\n"
                "            # TODO: print size\n"
                "            pass\n\n"
                "main()\n"
            ),
            "javascript": (
                "const lines = require('fs').readFileSync(0, 'utf8').trim().split('\\n');\n"
                "const n = parseInt(lines[0]);\n"
                "const stack = [];\n"
                "for (let i = 1; i <= n; i++) {\n"
                "    const parts = lines[i].trim().split(' ');\n"
                "    const cmd = parts[0];\n"
                "    if (cmd === 'PUSH') {\n"
                "        stack.push(parseInt(parts[1]));\n"
                "    } else if (cmd === 'POP') {\n"
                "        // TODO\n"
                "    } else if (cmd === 'PEEK') {\n"
                "        // TODO\n"
                "    } else if (cmd === 'SIZE') {\n"
                "        // TODO\n"
                "    }\n"
                "}\n"
            ),
            "typescript": (
                "import * as fs from 'fs';\n\n"
                "class Stack<T> {\n"
                "    private items: T[] = [];\n"
                "    push(item: T): void { this.items.push(item); }\n"
                "    pop(): T | undefined { return this.items.pop(); }\n"
                "    peek(): T | undefined { return this.items[this.items.length - 1]; }\n"
                "    get size(): number { return this.items.length; }\n"
                "}\n\n"
                "const lines = fs.readFileSync(0, 'utf8').trim().split('\\n');\n"
                "const n = parseInt(lines[0]);\n"
                "const stack = new Stack<number>();\n"
                "for (let i = 1; i <= n; i++) {\n"
                "    const parts = lines[i].trim().split(' ');\n"
                "    const cmd = parts[0];\n"
                "    if (cmd === 'PUSH') {\n"
                "        stack.push(parseInt(parts[1]));\n"
                "    } else if (cmd === 'POP') {\n"
                "        // TODO: print popped value or EMPTY\n"
                "    } else if (cmd === 'PEEK') {\n"
                "        // TODO: print top value or EMPTY\n"
                "    } else if (cmd === 'SIZE') {\n"
                "        // TODO: print size\n"
                "    }\n"
                "}\n"
            ),
        },
        solution_code={
            "python": (
                "import sys\n"
                "lines = sys.stdin.read().splitlines()\n"
                "n = int(lines[0])\n"
                "stack = []\n"
                "out = []\n"
                "for i in range(1, n + 1):\n"
                "    parts = lines[i].split()\n"
                "    cmd = parts[0]\n"
                "    if cmd == 'PUSH':\n"
                "        stack.append(int(parts[1]))\n"
                "    elif cmd == 'POP':\n"
                "        out.append(str(stack.pop()) if stack else 'EMPTY')\n"
                "    elif cmd == 'PEEK':\n"
                "        out.append(str(stack[-1]) if stack else 'EMPTY')\n"
                "    elif cmd == 'SIZE':\n"
                "        out.append(str(len(stack)))\n"
                "print('\\n'.join(out))\n"
            ),
        },
        supported_languages=WEB_LANGS,
        time_limit_ms=3000,
        memory_limit_mb=256,
        points=15,
    )
    _cases(db, ex, [
        ("basic",       "5\nPUSH 3\nPUSH 7\nPEEK\nPOP\nSIZE\n",            "7\n7\n1",       False, 1),
        ("empty-pop",   "2\nPOP\nSIZE\n",                                    "EMPTY\n0",      False, 1),
        ("empty-peek",  "1\nPEEK\n",                                         "EMPTY",         False, 1),
        ("multi-push",  "4\nPUSH 1\nPUSH 2\nPUSH 3\nSIZE\n",               "3",             False, 1),
        ("pop-all",     "6\nPUSH 10\nPUSH 20\nPOP\nPOP\nPOP\nSIZE\n",      "20\n10\nEMPTY\n0", True, 2),
    ])


# ════════════════════════════════════════════════════════════════
#  MODULE 2 — Angular Architecture
# ════════════════════════════════════════════════════════════════

M2_OVERVIEW_MD = """\
# Angular Architecture Overview

Angular is an **opinionated, full-featured** framework for building client-side
web applications. Understanding its architecture helps you write maintainable,
scalable code from day one.

## Core Building Blocks

| Concept | Role |
|---------|------|
| **Component** | View + logic — the fundamental UI unit |
| **Template** | HTML with Angular-specific syntax |
| **Directive** | Extend HTML with custom behavior |
| **Pipe** | Transform values in templates |
| **Service** | Shared business logic and data access |
| **Module / Standalone** | Groups related functionality |
| **Router** | Maps URLs to component trees |

## NgModules (Classic)

Historically Angular used `NgModule` to declare, import, and export components:

```typescript
@NgModule({
  declarations: [AppComponent, UserListComponent],
  imports:      [BrowserModule, HttpClientModule, RouterModule],
  providers:    [UserService],
  bootstrap:    [AppComponent],
})
export class AppModule {}
```

## Standalone Components (Angular 17+)

Modern Angular encourages **standalone** components — no NgModule required:

```typescript
@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, CommonModule],
  template: `<router-outlet />`,
})
export class AppComponent {}
```

`bootstrapApplication(AppComponent, appConfig)` replaces `platformBrowserDynamic().bootstrapModule()`.

## Dependency Injection

Angular's DI system is hierarchical:

1. **Platform injector** — singleton for the entire platform
2. **Root injector** — app-wide singletons (`providedIn: 'root'`)
3. **Module injector** — scoped to a lazy-loaded module
4. **Component injector** — one instance per component subtree

```typescript
@Injectable({ providedIn: 'root' })  // singleton for the whole app
export class AuthService {
  constructor(private http: HttpClient) {}
}
```

## Zone.js and Change Detection

Angular wraps browser async APIs (setTimeout, XHR, Promises) using **Zone.js**
to automatically trigger change detection after every async event.

The default strategy checks **every component** in the tree. With
`ChangeDetectionStrategy.OnPush`, Angular only re-renders a component when:
- An `@Input()` reference changes
- An event originates from the component
- An `async` pipe resolves
- `markForCheck()` is called manually

## Angular CLI

```bash
ng new my-app --standalone --routing --style=scss
ng generate component features/user-list
ng generate service core/services/auth
ng build --configuration production
ng serve --port 4200
```

The CLI generates consistent boilerplate, manages `angular.json` configuration,
and integrates the TypeScript + Webpack (or esbuild) build pipeline.
"""

M2_STRUCTURE_MD = """\
# Angular Project Structure

A well-organized Angular project is predictable and easy to navigate.

## Workspace Layout

```
my-app/
├── angular.json          # build/serve/test configuration
├── tsconfig.json         # TypeScript root config
├── package.json
└── src/
    ├── main.ts           # bootstraps the app
    ├── index.html        # shell HTML
    ├── styles.scss       # global styles
    └── app/
        ├── app.component.ts
        ├── app.routes.ts
        ├── core/         # singletons: auth, http interceptors, guards
        ├── shared/       # reusable components/pipes/directives
        └── features/     # one folder per feature (lazy-loadable)
            ├── user/
            │   ├── user-list/
            │   ├── user-detail/
            │   └── user.routes.ts
            └── admin/
```

## angular.json Key Sections

```json
{
  "projects": {
    "my-app": {
      "architect": {
        "build": {
          "options": {
            "outputPath": "dist/my-app",
            "index":      "src/index.html",
            "browser":    "src/main.ts",
            "styles":     ["src/styles.scss"],
            "assets":     ["src/assets"]
          },
          "configurations": {
            "production": { "optimization": true, "sourceMap": false }
          }
        }
      }
    }
  }
}
```

## Environments

```typescript
// src/environments/environment.ts (development)
export const environment = { production: false, apiUrl: 'http://localhost:3000' };

// src/environments/environment.prod.ts
export const environment = { production: true, apiUrl: 'https://api.example.com' };
```

The CLI swaps environment files via `fileReplacements` in angular.json.

## Lazy Loading

Feature routes are lazy-loaded to keep the initial bundle small:

```typescript
// app.routes.ts
export const routes: Routes = [
  { path: 'users', loadChildren: () =>
      import('./features/user/user.routes').then(m => m.USER_ROUTES) },
];
```

Angular loads the feature chunk only when the user navigates to `/users`,
dramatically improving first-paint performance for large apps.

## Barrel Files

Each feature directory should export a clean public surface via `index.ts`:

```typescript
// features/user/index.ts
export { UserListComponent } from './user-list/user-list.component';
export { UserDetailComponent } from './user-detail/user-detail.component';
export { UserService } from './user.service';
```

This prevents deep import paths from leaking into consuming modules.
"""

M2_SIGNALS_MD = """\
# Change Detection and Signals

## Default Change Detection

By default Angular runs **CheckAlways** — after every browser event, timer, or
HTTP response it traverses the entire component tree and re-renders anything
that changed. Fast for small apps; can become a bottleneck as apps grow.

## OnPush Strategy

```typescript
@Component({
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class UserCardComponent {
  @Input() user!: User;
}
```

With OnPush, Angular only checks this component when:
1. An `@Input()` **reference** changes (not just a mutation)
2. An event handler fires inside the component
3. An `async` pipe inside the template emits
4. `ChangeDetectorRef.markForCheck()` is called

**Implication:** always create new objects/arrays instead of mutating them.

## Angular Signals (17+)

Signals provide **fine-grained reactivity** without Zone.js overhead:

```typescript
import { signal, computed, effect } from '@angular/core';

@Component({ /* ... */ })
export class CounterComponent {
  // Writable signal — like reactive state
  count = signal(0);

  // Derived signal — recalculates when dependencies change
  doubled = computed(() => this.count() * 2);

  constructor() {
    // Side-effect that re-runs when count changes
    effect(() => console.log('count is now', this.count()));
  }

  increment() {
    this.count.update(n => n + 1);   // functional update
    // or: this.count.set(this.count() + 1);
  }
}
```

## Signals vs RxJS

| | Signals | RxJS Observable |
|-|---------|-----------------|
| Learning curve | Low | High |
| Synchronous by default | Yes | No (cold/hot) |
| Template integration | `{{ count() }}` | `{{ count$ \\| async }}` |
| Side effects | `effect()` | `subscribe()` / `tap()` |
| Composition | `computed()` | `pipe(map, filter, ...)` |
| Best for | UI state | Async event streams |

Both can coexist. Use signals for local UI state; keep RxJS for HTTP calls,
complex async pipelines, and WebSocket streams.

## ChangeDetectorRef

For manual control when using OnPush:

```typescript
constructor(private cdr: ChangeDetectorRef) {}

loadData() {
  this.service.fetch().subscribe(data => {
    this.data = data;
    this.cdr.markForCheck();  // notify Angular to re-check this component
  });
}
```
"""


def seed_module2(db: Session, course: Course) -> None:
    mod = _module(db, course, "Angular Architecture", 2,
                  "NgModules, standalone components, DI, project structure, change detection, and Signals.")

    _lesson(db, mod, "angular-architecture-overview",
            title="Angular Architecture Overview",
            lesson_type=LessonType.reading,
            content_md=M2_OVERVIEW_MD,
            duration_minutes=15,
            order_index=1)

    _lesson(db, mod, "angular-project-structure",
            title="Angular Project Structure",
            lesson_type=LessonType.reading,
            content_md=M2_STRUCTURE_MD,
            duration_minutes=10,
            order_index=2)

    _lesson(db, mod, "change-detection-signals",
            title="Change Detection and Signals",
            lesson_type=LessonType.reading,
            content_md=M2_SIGNALS_MD,
            duration_minutes=8,
            order_index=3)


# ════════════════════════════════════════════════════════════════
#  MODULE 3 — Components and Templates
# ════════════════════════════════════════════════════════════════

M3_ANATOMY_MD = """\
# Component Anatomy

Components are the **fundamental building blocks** of Angular UIs. Each
component encapsulates a view (template), styling (SCSS/CSS), and logic
(TypeScript class).

## @Component Decorator

```typescript
@Component({
  selector:    'app-user-card',   // CSS selector used in templates
  standalone:  true,
  templateUrl: './user-card.component.html',
  styleUrl:    './user-card.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [CommonModule, RouterLink],
})
export class UserCardComponent implements OnInit, OnDestroy {
  // ...
}
```

## Template Binding Syntax

| Syntax | Type | Example |
|--------|------|---------|
| `{{ expr }}` | Interpolation | `{{ user.name }}` |
| `[prop]="expr"` | Property binding | `[disabled]="isLoading"` |
| `(event)="handler($event)"` | Event binding | `(click)="save()"` |
| `[(ngModel)]="prop"` | Two-way binding | `[(ngModel)]="search"` |
| `#ref` | Template reference | `#form="ngForm"` |

## @Input and @Output

```typescript
import { Component, Input, Output, EventEmitter } from '@angular/core';

@Component({ selector: 'app-button', /* ... */ })
export class ButtonComponent {
  @Input()  label: string = 'Click me';
  @Input()  disabled: boolean = false;
  @Output() clicked = new EventEmitter<void>();

  onClick() {
    if (!this.disabled) this.clicked.emit();
  }
}
```

Usage in parent template:
```html
<app-button
  [label]="'Save Changes'"
  [disabled]="isSaving"
  (clicked)="onSave()">
</app-button>
```

## Template Reference Variables

```html
<!-- reference to DOM element -->
<input #searchInput type="text" />
<button (click)="search(searchInput.value)">Search</button>

<!-- reference to component instance -->
<app-form #myForm></app-form>
<button (click)="myForm.reset()">Reset</button>
```

## ViewChild and ContentChild

```typescript
@Component({ /* ... */ })
export class ParentComponent implements AfterViewInit {
  @ViewChild(ChildComponent) child!: ChildComponent;
  @ViewChild('searchInput') inputEl!: ElementRef<HTMLInputElement>;

  ngAfterViewInit() {
    // DOM and child components are available here
    this.inputEl.nativeElement.focus();
  }
}
```

`@ContentChild` accesses projected content (`<ng-content>`) similarly.
Use `{ static: true }` only when you need the reference in `ngOnInit`.

## Component Lifecycle

```
constructor → ngOnChanges → ngOnInit → ngDoCheck
    → ngAfterContentInit → ngAfterContentChecked
    → ngAfterViewInit → ngAfterViewChecked
    → ngOnDestroy
```

Key hooks: `ngOnInit` (fetch data), `ngOnChanges` (react to input changes),
`ngOnDestroy` (clean up subscriptions to prevent memory leaks).
"""

M3_CONTROL_FLOW_MD = """\
# Template Control Flow

Angular 17 introduced a new **built-in control flow** syntax using `@if`,
`@for`, and `@switch` — replacing the legacy structural directives.

## Conditional Rendering

```html
<!-- Angular 17+ @if -->
@if (user) {
  <app-user-card [user]="user" />
} @else if (isLoading) {
  <app-spinner />
} @else {
  <p>No user found.</p>
}

<!-- Legacy (still works) -->
<app-user-card *ngIf="user; else loading" [user]="user" />
<ng-template #loading><app-spinner /></ng-template>
```

## List Rendering

```html
<!-- Angular 17+ @for (requires track) -->
@for (item of items; track item.id) {
  <li>{{ item.name }}</li>
} @empty {
  <li>No items.</li>
}

<!-- Legacy *ngFor -->
<li *ngFor="let item of items; trackBy: trackById">{{ item.name }}</li>
```

The `track` expression (or `trackBy`) tells Angular which property uniquely
identifies each item, enabling it to reuse DOM nodes efficiently.

## Switch / Match

```html
@switch (status) {
  @case ('loading')  { <app-spinner /> }
  @case ('error')    { <app-error [message]="error" /> }
  @case ('success')  { <app-data [data]="data" /> }
  @default           { <p>Unknown state</p> }
}
```

## ng-template and ng-container

```html
<!-- ng-template: defines a reusable template fragment -->
<ng-template #noData>
  <div class="empty-state">No results found.</div>
</ng-template>

<!-- ng-container: logical grouping without emitting a DOM element -->
<ng-container *ngIf="isAdmin">
  <button>Edit</button>
  <button>Delete</button>
</ng-container>
```

## Content Projection (ng-content)

```typescript
// Card component template
@Component({
  selector: 'app-card',
  template: `
    <div class="card">
      <div class="card-header">
        <ng-content select="[card-title]" />
      </div>
      <div class="card-body">
        <ng-content />
      </div>
    </div>
  `,
})
export class CardComponent {}
```

```html
<!-- Parent usage -->
<app-card>
  <h2 card-title>My Title</h2>
  <p>Card body content goes here.</p>
</app-card>
```

Named slots via CSS attribute selectors let you project content into
specific parts of a component's template — a powerful composition pattern.
"""

M3_EXERCISE_MD = "Practice component state logic — the TypeScript behind a counter component."


def seed_module3(db: Session, course: Course) -> None:
    mod = _module(db, course, "Components and Templates", 3,
                  "Component anatomy, template binding, @Input/@Output, control flow, and content projection.")

    _lesson(db, mod, "component-anatomy",
            title="Component Anatomy",
            lesson_type=LessonType.reading,
            content_md=M3_ANATOMY_MD,
            duration_minutes=18,
            order_index=1)

    _lesson(db, mod, "template-control-flow",
            title="Template Control Flow",
            lesson_type=LessonType.reading,
            content_md=M3_CONTROL_FLOW_MD,
            duration_minutes=12,
            order_index=2)

    ex_lesson = _lesson(db, mod, "component-logic-exercises",
                        title="Component Logic in TypeScript",
                        lesson_type=LessonType.exercise,
                        content_md=M3_EXERCISE_MD,
                        duration_minutes=20,
                        order_index=3)

    # ── Exercise 3.1: Component Counter ─────────────────────────────
    ex, _ = _exercise(db, ex_lesson, "angular-component-counter",
        title="Component Counter",
        prompt_md=(
            "# Component Counter\n\n"
            "Simulate the state logic of an Angular counter component by processing "
            "a sequence of commands and printing the current count after each one:\n\n"
            "- `INCREMENT` — add 1 to the counter\n"
            "- `DECREMENT n` — subtract n from the counter (n is a positive integer)\n"
            "- `RESET` — set the counter back to 0\n\n"
            "The counter starts at **0**.\n\n"
            "**Input:**\n```\nk\ncmd1\ncmd2\n...\n```\n"
            "First line k is the number of commands.\n\n"
            "**Output:** print the counter value after each command, one per line.\n\n"
            "**Example**\n```\nInput:\n4\nINCREMENT\nINCREMENT\nDECREMENT 1\nRESET\n\n"
            "Output:\n1\n2\n1\n0\n```"
        ),
        difficulty=Difficulty.easy,
        is_published=True,
        starter_code={
            "python": (
                "import sys\n\n"
                "lines = sys.stdin.read().splitlines()\n"
                "k = int(lines[0])\n"
                "count = 0\n"
                "for i in range(1, k + 1):\n"
                "    parts = lines[i].split()\n"
                "    cmd = parts[0]\n"
                "    if cmd == 'INCREMENT':\n"
                "        # TODO\n"
                "        pass\n"
                "    elif cmd == 'DECREMENT':\n"
                "        # TODO\n"
                "        pass\n"
                "    elif cmd == 'RESET':\n"
                "        # TODO\n"
                "        pass\n"
                "    print(count)\n"
            ),
            "javascript": (
                "const lines = require('fs').readFileSync(0, 'utf8').trim().split('\\n');\n"
                "const k = parseInt(lines[0]);\n"
                "let count = 0;\n"
                "for (let i = 1; i <= k; i++) {\n"
                "    const parts = lines[i].trim().split(' ');\n"
                "    const cmd = parts[0];\n"
                "    if (cmd === 'INCREMENT') {\n"
                "        // TODO\n"
                "    } else if (cmd === 'DECREMENT') {\n"
                "        // TODO\n"
                "    } else if (cmd === 'RESET') {\n"
                "        // TODO\n"
                "    }\n"
                "    console.log(count);\n"
                "}\n"
            ),
            "typescript": (
                "import * as fs from 'fs';\n\n"
                "const lines = fs.readFileSync(0, 'utf8').trim().split('\\n');\n"
                "const k = parseInt(lines[0]);\n"
                "let count = 0;\n"
                "for (let i = 1; i <= k; i++) {\n"
                "    const parts = lines[i].trim().split(' ');\n"
                "    const cmd = parts[0];\n"
                "    if (cmd === 'INCREMENT') {\n"
                "        count++;\n"
                "    } else if (cmd === 'DECREMENT') {\n"
                "        // TODO: subtract parseInt(parts[1])\n"
                "    } else if (cmd === 'RESET') {\n"
                "        // TODO\n"
                "    }\n"
                "    console.log(count);\n"
                "}\n"
            ),
        },
        solution_code={
            "python": (
                "import sys\n"
                "lines = sys.stdin.read().splitlines()\n"
                "k = int(lines[0])\n"
                "count = 0\n"
                "out = []\n"
                "for i in range(1, k + 1):\n"
                "    parts = lines[i].split()\n"
                "    if parts[0] == 'INCREMENT':\n"
                "        count += 1\n"
                "    elif parts[0] == 'DECREMENT':\n"
                "        count -= int(parts[1])\n"
                "    elif parts[0] == 'RESET':\n"
                "        count = 0\n"
                "    out.append(str(count))\n"
                "print('\\n'.join(out))\n"
            ),
        },
        supported_languages=WEB_LANGS,
        time_limit_ms=3000,
        memory_limit_mb=256,
        points=10,
    )
    _cases(db, ex, [
        ("basic",           "4\nINCREMENT\nINCREMENT\nDECREMENT 1\nRESET\n", "1\n2\n1\n0",   False, 1),
        ("only-inc",        "3\nINCREMENT\nINCREMENT\nINCREMENT\n",          "1\n2\n3",       False, 1),
        ("decrement-multi", "3\nINCREMENT\nINCREMENT\nDECREMENT 2\n",        "1\n2\n0",       False, 1),
        ("negative-count",  "2\nDECREMENT 5\nINCREMENT\n",                   "-5\n-4",        False, 1),
        ("reset-mid",       "5\nINCREMENT\nINCREMENT\nRESET\nINCREMENT\nINCREMENT\n", "1\n2\n0\n1\n2", False, 1),
        ("all-ops",         "4\nINCREMENT\nDECREMENT 3\nRESET\nDECREMENT 1\n", "1\n-2\n0\n-1", True, 2),
    ])


# ════════════════════════════════════════════════════════════════
#  MODULE 4 — Directives and Pipes
# ════════════════════════════════════════════════════════════════

M4_DIRECTIVES_MD = """\
# Built-in Directives

Angular directives extend HTML with additional behavior. There are three kinds:
**components** (directives with a template), **structural** (alter the DOM
layout), and **attribute** (alter element appearance or behavior).

## Structural Directives

Angular 17 new control flow replaces these with `@if`/`@for`/`@switch`, but
the directive forms still work and appear in legacy code:

```html
<!-- *ngIf -->
<div *ngIf="isLoggedIn; else guestBlock">Welcome, {{ user.name }}</div>
<ng-template #guestBlock><a routerLink="/login">Login</a></ng-template>

<!-- *ngFor -->
<li *ngFor="let item of items; let i = index; trackBy: trackById">
  {{ i + 1 }}. {{ item.name }}
</li>

<!-- *ngSwitch -->
<div [ngSwitch]="role">
  <admin-panel  *ngSwitchCase="'admin'"></admin-panel>
  <user-panel   *ngSwitchCase="'user'"></user-panel>
  <guest-panel  *ngSwitchDefault></guest-panel>
</div>
```

## Attribute Directives

```html
<!-- ngClass: add/remove CSS classes -->
<div [ngClass]="{ active: isActive, 'text-red': hasError }">...</div>
<div [ngClass]="getClasses()">...</div>

<!-- ngStyle: inline styles -->
<div [ngStyle]="{ 'background-color': bgColor, fontSize: fontSize + 'px' }">...</div>

<!-- ngModel: two-way data binding (requires FormsModule) -->
<input [(ngModel)]="searchText" placeholder="Search..." />
```

## Custom Attribute Directive

```typescript
import { Directive, HostBinding, HostListener, Input } from '@angular/core';

@Directive({ selector: '[appHighlight]', standalone: true })
export class HighlightDirective {
  @Input() appHighlight = 'yellow';
  @Input() defaultColor = 'transparent';

  @HostBinding('style.backgroundColor') bgColor = this.defaultColor;

  @HostListener('mouseenter') onEnter() {
    this.bgColor = this.appHighlight;
  }

  @HostListener('mouseleave') onLeave() {
    this.bgColor = this.defaultColor;
  }
}
```

Usage: `<p appHighlight="lightblue">Hover me!</p>`

## ElementRef and Renderer2

For direct DOM manipulation, inject `ElementRef` (reference to host element)
and `Renderer2` (platform-agnostic DOM API, preferred over `nativeElement`
for SSR compatibility):

```typescript
constructor(private el: ElementRef, private renderer: Renderer2) {}

ngOnInit() {
  this.renderer.setStyle(this.el.nativeElement, 'border', '2px solid blue');
}
```
"""

M4_PIPES_MD = """\
# Built-in and Custom Pipes

Pipes transform values in templates using the `|` operator. They keep component
logic clean by moving display formatting into reusable, declarative functions.

## Built-in Pipes

```html
<!-- date -->
{{ order.createdAt | date:'mediumDate' }}
{{ order.createdAt | date:'yyyy-MM-dd HH:mm' }}

<!-- number / percent / currency -->
{{ price      | number:'1.2-2' }}       <!-- 1,234.56 -->
{{ ratio      | percent:'1.0-1' }}      <!-- 75.3% -->
{{ amount     | currency:'USD':'symbol':'1.2-2' }}  <!-- $1,234.56 -->

<!-- string -->
{{ title   | uppercase }}
{{ title   | lowercase }}
{{ title   | titlecase }}
{{ summary | slice:0:100 }}

<!-- objects/arrays -->
{{ data    | json }}
{{ map     | keyvalue }}    <!-- iterate Map/object key-value pairs -->

<!-- async (subscribes and unsubscribes automatically) -->
{{ user$ | async }}
@if (data$ | async; as data) { {{ data.name }} }
```

## Custom Pipe

```typescript
import { Pipe, PipeTransform } from '@angular/core';

@Pipe({ name: 'truncate', standalone: true, pure: true })
export class TruncatePipe implements PipeTransform {
  transform(value: string, limit: number = 50, ellipsis: string = '...'): string {
    if (!value) return '';
    return value.length > limit
      ? value.substring(0, limit) + ellipsis
      : value;
  }
}
```

```html
{{ description | truncate:80 }}
{{ description | truncate:80:'…' }}
```

## Pure vs Impure Pipes

| | Pure | Impure |
|-|------|--------|
| Re-executes when | Input reference changes | Every CD cycle |
| Performance | High | Can be slow |
| Use for | Stateless transformations | Async/filtering live data |
| Default | Yes | `pure: false` |

**Prefer pure pipes.** Only mark a pipe impure if it absolutely must react to
mutations inside objects (e.g., filtering a mutated array).

## Pipe Chaining

```html
{{ createdAt | date:'shortDate' | uppercase }}
{{ items.length | number | slice:0:3 }}
```

Pipes are evaluated left to right — the output of one pipe feeds into the next.
"""

M4_EXERCISE_MD = "Implement pipe transformation logic in plain code."


def seed_module4(db: Session, course: Course) -> None:
    mod = _module(db, course, "Directives and Pipes", 4,
                  "Built-in and custom structural/attribute directives, and pipe transformations.")

    _lesson(db, mod, "built-in-directives",
            title="Built-in Directives",
            lesson_type=LessonType.reading,
            content_md=M4_DIRECTIVES_MD,
            duration_minutes=15,
            order_index=1)

    _lesson(db, mod, "built-in-custom-pipes",
            title="Built-in and Custom Pipes",
            lesson_type=LessonType.reading,
            content_md=M4_PIPES_MD,
            duration_minutes=12,
            order_index=2)

    ex_lesson = _lesson(db, mod, "pipe-logic-exercises",
                        title="Pipe Logic",
                        lesson_type=LessonType.exercise,
                        content_md=M4_EXERCISE_MD,
                        duration_minutes=15,
                        order_index=3)

    # ── Exercise 4.1: Custom Pipe Transform ─────────────────────────
    ex, _ = _exercise(db, ex_lesson, "custom-pipe-transform",
        title="Custom Pipe Transform",
        prompt_md=(
            "# Custom Pipe Transform\n\n"
            "Implement two pipe operations:\n\n"
            "- `TITLECASE <text>` — convert text to Title Case "
            "(first letter of each word capitalised, rest lowercase)\n"
            "- `TRUNCATE <n> <text>` — if text length > n, return the first n characters "
            "followed by `...`; otherwise return text unchanged\n\n"
            "**Input:**\n```\nOPERATION args...\n```\n"
            "One operation per test.\n\n"
            "**Output:** the transformed string.\n\n"
            "**Examples**\n```\nInput:\nTITLECASE hello world\nOutput:\nHello World\n\n"
            "Input:\nTRUNCATE 10 Hello Angular World\nOutput:\nHello Angu...\n```"
        ),
        difficulty=Difficulty.easy,
        is_published=True,
        starter_code={
            "python": (
                "import sys\n\n"
                "line = sys.stdin.read().strip()\n"
                "parts = line.split(' ', 2)\n"
                "op = parts[0]\n\n"
                "if op == 'TITLECASE':\n"
                "    text = parts[1] if len(parts) > 1 else ''\n"
                "    # TODO: apply title case\n"
                "    print(text)\n"
                "elif op == 'TRUNCATE':\n"
                "    n = int(parts[1])\n"
                "    text = parts[2] if len(parts) > 2 else ''\n"
                "    # TODO: truncate at n chars with '...'\n"
                "    print(text)\n"
            ),
            "javascript": (
                "const line = require('fs').readFileSync(0, 'utf8').trim();\n"
                "const idx  = line.indexOf(' ');\n"
                "const op   = idx === -1 ? line : line.substring(0, idx);\n"
                "const rest = idx === -1 ? '' : line.substring(idx + 1);\n\n"
                "if (op === 'TITLECASE') {\n"
                "    // TODO: convert rest to title case\n"
                "    console.log(rest);\n"
                "} else if (op === 'TRUNCATE') {\n"
                "    const spIdx = rest.indexOf(' ');\n"
                "    const n    = parseInt(rest.substring(0, spIdx));\n"
                "    const text = rest.substring(spIdx + 1);\n"
                "    // TODO: truncate text at n chars with '...'\n"
                "    console.log(text);\n"
                "}\n"
            ),
            "typescript": (
                "import * as fs from 'fs';\n\n"
                "function titleCase(s: string): string {\n"
                "    // TODO: capitalise first letter of each word\n"
                "    return s;\n"
                "}\n\n"
                "function truncate(s: string, n: number): string {\n"
                "    // TODO: truncate at n, append '...' if needed\n"
                "    return s;\n"
                "}\n\n"
                "const line = fs.readFileSync(0, 'utf8').trim();\n"
                "const [op, ...rest] = line.split(' ');\n"
                "if (op === 'TITLECASE') {\n"
                "    console.log(titleCase(rest.join(' ')));\n"
                "} else if (op === 'TRUNCATE') {\n"
                "    const n = parseInt(rest[0]);\n"
                "    const text = rest.slice(1).join(' ');\n"
                "    console.log(truncate(text, n));\n"
                "}\n"
            ),
        },
        solution_code={
            "python": (
                "import sys\n"
                "line = sys.stdin.read().strip()\n"
                "parts = line.split(' ', 2)\n"
                "op = parts[0]\n"
                "if op == 'TITLECASE':\n"
                "    text = parts[1] if len(parts) > 1 else ''\n"
                "    # handle rest of string after first space\n"
                "    full = ' '.join(parts[1:]) if len(parts) > 1 else ''\n"
                "    print(' '.join(w.capitalize() for w in full.split()))\n"
                "elif op == 'TRUNCATE':\n"
                "    n = int(parts[1])\n"
                "    text = parts[2] if len(parts) > 2 else ''\n"
                "    print(text[:n] + '...' if len(text) > n else text)\n"
            ),
        },
        supported_languages=WEB_LANGS,
        time_limit_ms=3000,
        memory_limit_mb=256,
        points=10,
    )
    _cases(db, ex, [
        ("titlecase-basic",    "TITLECASE hello world\n",            "Hello World",         False, 1),
        ("titlecase-mixed",    "TITLECASE the quick BROWN fox\n",     "The Quick Brown Fox", False, 1),
        ("truncate-long",      "TRUNCATE 10 Hello Angular World\n",   "Hello Angu...",       False, 1),
        ("truncate-exact",     "TRUNCATE 5 Hello\n",                  "Hello",               False, 1),
        ("truncate-short",     "TRUNCATE 20 Hi\n",                    "Hi",                  True,  2),
    ])


# ════════════════════════════════════════════════════════════════
#  MODULE 5 — Services and Dependency Injection
# ════════════════════════════════════════════════════════════════

M5_SERVICES_MD = """\
# Services and Dependency Injection

## What Is a Service?

A service is a class that encapsulates **reusable business logic** or **shared
state** independent of any specific component. Common uses:

- HTTP communication with a backend API
- Application-wide state (authentication, user preferences)
- Utility functions (formatting, validation)
- Caching and memoization

## @Injectable Decorator

```typescript
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root',  // registered in the root injector — singleton app-wide
})
export class UserService {
  constructor(private http: HttpClient) {}

  getUsers(): Observable<User[]> {
    return this.http.get<User[]>('/api/users');
  }
}
```

## Hierarchical Injectors

Angular maintains a **tree of injectors** mirroring the module/component tree:

```
Platform Injector
  └─ Root Injector           ← providedIn: 'root'
       ├─ LazyModule Injector ← providers in lazy module
       └─ Component Injector  ← providers: [...] in @Component
```

A component first looks in its own injector, then walks up the tree.
This allows **scoped instances**: one service per component subtree.

## Provider Recipes

```typescript
// Standard class provider
providers: [UserService]

// useClass: swap implementation (useful for testing/mocking)
providers: [{ provide: UserService, useClass: MockUserService }]

// useValue: provide a constant
providers: [{ provide: API_URL, useValue: 'https://api.example.com' }]

// useFactory: create service with custom logic
providers: [{
  provide: Logger,
  useFactory: (env: Environment) => env.production
    ? new SilentLogger()
    : new ConsoleLogger(),
  deps: [Environment],
}]
```

## InjectionToken

Use `InjectionToken` for non-class dependencies (strings, configs, functions):

```typescript
import { InjectionToken } from '@angular/core';

export const API_BASE_URL = new InjectionToken<string>('API_BASE_URL');

// Provide
providers: [{ provide: API_BASE_URL, useValue: 'https://api.example.com' }]

// Inject
constructor(@Inject(API_BASE_URL) private apiUrl: string) {}
// or with inject() function:
private apiUrl = inject(API_BASE_URL);
```

## Singleton vs Scoped Services

| `providedIn: 'root'` | Single instance for the entire app |
| `providers:` in component | New instance per component subtree |
| `providers:` in lazy module | Single instance within that module |

Understanding scope is critical for avoiding bugs where shared state leaks
between feature modules or memory is wasted on unneeded instances.
"""

M5_STATE_MD = """\
# State Management Patterns

## Component State vs Service State

Not all state needs to be global. Choose the right scope:

| State type | Location |
|-----------|----------|
| UI-only (tooltip open, tab index) | Component property |
| Shared within a feature | Feature service |
| App-wide (auth, preferences) | Root service |
| Complex, DevTools needed | NgRx store |

## BehaviorSubject Pattern

The classic Angular service state pattern uses `BehaviorSubject` from RxJS:

```typescript
@Injectable({ providedIn: 'root' })
export class CartService {
  private _items$ = new BehaviorSubject<CartItem[]>([]);

  // Public read-only observable
  readonly items$ = this._items$.asObservable();
  readonly count$ = this.items$.pipe(map(items => items.length));

  addItem(item: CartItem): void {
    const current = this._items$.getValue();
    this._items$.next([...current, item]);   // immutable update
  }

  removeItem(id: number): void {
    this._items$.next(
      this._items$.getValue().filter(i => i.id !== id)
    );
  }
}
```

In the template: `{{ cartService.count$ | async }}` — the `async` pipe
subscribes and unsubscribes automatically.

## Angular Signals Store Pattern

With Angular 17+ signals, you can build a lightweight store:

```typescript
@Injectable({ providedIn: 'root' })
export class CounterStore {
  readonly count   = signal(0);
  readonly doubled = computed(() => this.count() * 2);

  increment() { this.count.update(n => n + 1); }
  decrement() { this.count.update(n => n - 1); }
  reset()     { this.count.set(0); }
}
```

Templates use `{{ store.count() }}` — no `async` pipe needed.

## NgRx for Large Apps

NgRx implements the Redux pattern: **Actions → Reducers → Store → Selectors**.

```typescript
// Action
export const increment = createAction('[Counter] Increment');

// Reducer
export const counterReducer = createReducer(
  { count: 0 },
  on(increment, state => ({ ...state, count: state.count + 1 })),
);

// Selector
export const selectCount = createSelector(
  (state: AppState) => state.counter,
  counter => counter.count,
);

// Component
this.count$ = this.store.select(selectCount);
this.store.dispatch(increment());
```

Use NgRx when you need: time-travel debugging, complex derived state,
cross-feature communication, or strict unidirectional data flow enforcement.
"""

M5_EXERCISE_MD = "Implement a publish-subscribe event bus — the core pattern behind Angular's service layer."


def seed_module5(db: Session, course: Course) -> None:
    mod = _module(db, course, "Services and Dependency Injection", 5,
                  "Injectable services, DI hierarchy, provider recipes, and state management patterns.")

    _lesson(db, mod, "services-and-di",
            title="Services and Dependency Injection",
            lesson_type=LessonType.reading,
            content_md=M5_SERVICES_MD,
            duration_minutes=18,
            order_index=1)

    _lesson(db, mod, "state-management-patterns",
            title="State Management Patterns",
            lesson_type=LessonType.reading,
            content_md=M5_STATE_MD,
            duration_minutes=12,
            order_index=2)

    ex_lesson = _lesson(db, mod, "service-logic-exercises",
                        title="Service Logic",
                        lesson_type=LessonType.exercise,
                        content_md=M5_EXERCISE_MD,
                        duration_minutes=20,
                        order_index=3)

    # ── Exercise 5.1: Event Bus ──────────────────────────────────────
    ex, _ = _exercise(db, ex_lesson, "service-event-bus",
        title="Service Event Bus",
        prompt_md=(
            "# Service Event Bus\n\n"
            "Simulate a publish-subscribe event bus with the following commands:\n\n"
            "- `SUBSCRIBE topic subscriber` — add subscriber to topic\n"
            "- `PUBLISH topic message` — print `topic: [s1, s2, ...]` listing all "
            "current subscribers in insertion order, then `message: <message>`. "
            "If no subscribers, print `topic: []` and `message: <message>`.\n"
            "- `UNSUBSCRIBE topic subscriber` — remove subscriber from topic "
            "(no output; ignore if not subscribed)\n"
            "- `LIST_SUBS topic` — print the current subscribers list: "
            "`topic: [s1, s2, ...]` or `topic: []`\n\n"
            "**Input:**\n```\nn\ncmd1\ncmd2\n...\n```\n\n"
            "**Output:** output lines for PUBLISH and LIST_SUBS commands only.\n\n"
            "**Example**\n```\nInput:\n5\nSUBSCRIBE news alice\nSUBSCRIBE news bob\n"
            "PUBLISH news breaking\nUNSUBSCRIBE news alice\nLIST_SUBS news\n\n"
            "Output:\nnews: [alice, bob]\nmessage: breaking\nnews: [bob]\n```"
        ),
        difficulty=Difficulty.medium,
        is_published=True,
        starter_code={
            "python": (
                "import sys\n"
                "from collections import defaultdict\n\n"
                "lines = sys.stdin.read().splitlines()\n"
                "n = int(lines[0])\n"
                "bus = defaultdict(list)  # topic -> list of subscribers\n\n"
                "for i in range(1, n + 1):\n"
                "    parts = lines[i].split()\n"
                "    cmd = parts[0]\n"
                "    if cmd == 'SUBSCRIBE':\n"
                "        topic, sub = parts[1], parts[2]\n"
                "        # TODO: add sub to bus[topic] if not already there\n"
                "    elif cmd == 'PUBLISH':\n"
                "        topic = parts[1]\n"
                "        message = ' '.join(parts[2:])\n"
                "        # TODO: print subscribers then message\n"
                "    elif cmd == 'UNSUBSCRIBE':\n"
                "        topic, sub = parts[1], parts[2]\n"
                "        # TODO: remove sub from bus[topic]\n"
                "    elif cmd == 'LIST_SUBS':\n"
                "        topic = parts[1]\n"
                "        # TODO: print subscribers\n"
            ),
            "javascript": (
                "const lines = require('fs').readFileSync(0, 'utf8').trim().split('\\n');\n"
                "const n = parseInt(lines[0]);\n"
                "const bus = {};\n\n"
                "for (let i = 1; i <= n; i++) {\n"
                "    const parts = lines[i].trim().split(' ');\n"
                "    const cmd = parts[0];\n"
                "    if (cmd === 'SUBSCRIBE') {\n"
                "        const [, topic, sub] = parts;\n"
                "        if (!bus[topic]) bus[topic] = [];\n"
                "        if (!bus[topic].includes(sub)) bus[topic].push(sub);\n"
                "    } else if (cmd === 'PUBLISH') {\n"
                "        const topic = parts[1];\n"
                "        const message = parts.slice(2).join(' ');\n"
                "        // TODO: print subscribers list and message\n"
                "    } else if (cmd === 'UNSUBSCRIBE') {\n"
                "        const [, topic, sub] = parts;\n"
                "        // TODO: remove sub\n"
                "    } else if (cmd === 'LIST_SUBS') {\n"
                "        const topic = parts[1];\n"
                "        // TODO: print subscribers\n"
                "    }\n"
                "}\n"
            ),
            "typescript": (
                "import * as fs from 'fs';\n\n"
                "const lines = fs.readFileSync(0, 'utf8').trim().split('\\n');\n"
                "const n = parseInt(lines[0]);\n"
                "const bus: Record<string, string[]> = {};\n\n"
                "for (let i = 1; i <= n; i++) {\n"
                "    const parts = lines[i].trim().split(' ');\n"
                "    const cmd = parts[0];\n"
                "    if (cmd === 'SUBSCRIBE') {\n"
                "        const topic = parts[1], sub = parts[2];\n"
                "        if (!bus[topic]) bus[topic] = [];\n"
                "        if (!bus[topic].includes(sub)) bus[topic].push(sub);\n"
                "    } else if (cmd === 'PUBLISH') {\n"
                "        const topic = parts[1];\n"
                "        const message = parts.slice(2).join(' ');\n"
                "        const subs = bus[topic] ?? [];\n"
                "        // TODO: print subs and message\n"
                "    } else if (cmd === 'UNSUBSCRIBE') {\n"
                "        const topic = parts[1], sub = parts[2];\n"
                "        if (bus[topic]) bus[topic] = bus[topic].filter(s => s !== sub);\n"
                "    } else if (cmd === 'LIST_SUBS') {\n"
                "        const topic = parts[1];\n"
                "        const subs = bus[topic] ?? [];\n"
                "        // TODO: print subs\n"
                "    }\n"
                "}\n"
            ),
        },
        solution_code={
            "python": (
                "import sys\n"
                "from collections import defaultdict\n"
                "lines = sys.stdin.read().splitlines()\n"
                "n = int(lines[0])\n"
                "bus = defaultdict(list)\n"
                "out = []\n"
                "for i in range(1, n + 1):\n"
                "    parts = lines[i].split()\n"
                "    cmd = parts[0]\n"
                "    if cmd == 'SUBSCRIBE':\n"
                "        topic, sub = parts[1], parts[2]\n"
                "        if sub not in bus[topic]: bus[topic].append(sub)\n"
                "    elif cmd == 'PUBLISH':\n"
                "        topic = parts[1]; msg = ' '.join(parts[2:])\n"
                "        subs = bus[topic]\n"
                "        out.append(f'{topic}: [{', '.join(subs)}]')\n"
                "        out.append(f'message: {msg}')\n"
                "    elif cmd == 'UNSUBSCRIBE':\n"
                "        topic, sub = parts[1], parts[2]\n"
                "        if sub in bus[topic]: bus[topic].remove(sub)\n"
                "    elif cmd == 'LIST_SUBS':\n"
                "        topic = parts[1]\n"
                "        subs = bus[topic]\n"
                "        out.append(f'{topic}: [{', '.join(subs)}]')\n"
                "print('\\n'.join(out))\n"
            ),
        },
        supported_languages=WEB_LANGS,
        time_limit_ms=3000,
        memory_limit_mb=256,
        points=20,
    )
    _cases(db, ex, [
        ("basic",
         "5\nSUBSCRIBE news alice\nSUBSCRIBE news bob\nPUBLISH news breaking\nUNSUBSCRIBE news alice\nLIST_SUBS news\n",
         "news: [alice, bob]\nmessage: breaking\nnews: [bob]",
         False, 1),
        ("empty-topic",
         "2\nPUBLISH weather rain\nLIST_SUBS weather\n",
         "weather: []\nmessage: rain\nweather: []",
         False, 1),
        ("no-dup-subscribe",
         "4\nSUBSCRIBE alerts carol\nSUBSCRIBE alerts carol\nLIST_SUBS alerts\nPUBLISH alerts fire\n",
         "alerts: [carol]\nalerts: [carol]\nmessage: fire",
         False, 1),
        ("unsub-nonexistent",
         "3\nSUBSCRIBE chat dave\nUNSUBSCRIBE chat unknown\nLIST_SUBS chat\n",
         "chat: [dave]",
         False, 1),
        ("multi-topic",
         "6\nSUBSCRIBE sports alice\nSUBSCRIBE sports bob\nSUBSCRIBE finance carol\nPUBLISH sports goal\nPUBLISH finance stocks\nLIST_SUBS sports\n",
         "sports: [alice, bob]\nmessage: goal\nfinance: [carol]\nmessage: stocks\nsports: [alice, bob]",
         True, 2),
    ])


# ════════════════════════════════════════════════════════════════
#  MODULE 6 — Routing and Navigation
# ════════════════════════════════════════════════════════════════

M6_ROUTER_MD = """\
# Angular Router

The Angular Router maps URL paths to components, enabling Single Page Application
(SPA) navigation without full page reloads.

## Basic Route Configuration

```typescript
// app.routes.ts
import { Routes } from '@angular/router';

export const routes: Routes = [
  { path: '',           component: HomeComponent },
  { path: 'users',      component: UserListComponent },
  { path: 'users/:id',  component: UserDetailComponent },
  { path: 'admin',      loadChildren: () =>
        import('./features/admin/admin.routes').then(m => m.ADMIN_ROUTES) },
  { path: '**',         component: NotFoundComponent },  // wildcard
];
```

## RouterOutlet and RouterLink

```html
<!-- Shell template -->
<nav>
  <a routerLink="/"      routerLinkActive="active" [routerLinkActiveOptions]="{exact:true}">Home</a>
  <a routerLink="/users" routerLinkActive="active">Users</a>
</nav>
<router-outlet />
```

## Reading Route Parameters

```typescript
@Component({ /* ... */ })
export class UserDetailComponent implements OnInit {
  user$!: Observable<User>;

  constructor(
    private route: ActivatedRoute,
    private userService: UserService,
  ) {}

  ngOnInit() {
    // Snapshot (for one-time reads)
    const id = this.route.snapshot.paramMap.get('id')!;

    // Observable (reactive — reacts to navigation between same route)
    this.user$ = this.route.paramMap.pipe(
      map(params => params.get('id')!),
      switchMap(id => this.userService.getUser(id)),
    );
  }
}
```

## Route Guards

```typescript
// Functional guard (Angular 15+)
export const authGuard: CanActivateFn = (route, state) => {
  const auth = inject(AuthService);
  if (auth.isLoggedIn()) return true;
  return inject(Router).createUrlTree(['/login'], {
    queryParams: { returnUrl: state.url },
  });
};

// Apply to route
{ path: 'dashboard', component: DashboardComponent, canActivate: [authGuard] }
```

Class-based guards (`implements CanActivate`) still work but are deprecated
in favour of functional guards.

## Route Resolvers

Resolvers pre-fetch data before the component activates:

```typescript
export const userResolver: ResolveFn<User> = (route) =>
  inject(UserService).getUser(route.paramMap.get('id')!);

// In routes:
{ path: 'users/:id', resolve: { user: userResolver }, component: UserDetailComponent }

// In component:
ngOnInit() {
  this.user = this.route.snapshot.data['user'];
}
```

## Lazy Loading

Lazy loading splits the bundle into feature chunks loaded on demand:

```typescript
{ path: 'admin', canActivate: [adminGuard],
  loadChildren: () => import('./features/admin/admin.routes')
    .then(m => m.ADMIN_ROUTES) }
```

Angular's build tool creates a separate `admin.chunk.js` only downloaded when
the user first navigates to `/admin`.
"""

M6_ADVANCED_ROUTING_MD = """\
# Advanced Routing

## Route Parameters vs Query Parameters

```typescript
// Route parameter — part of the path: /products/42
this.route.paramMap.pipe(map(p => p.get('id')))

// Query parameter — after ?: /products?sort=price&page=2
this.route.queryParamMap.pipe(map(p => p.get('sort')))

// Navigate programmatically
this.router.navigate(['/products', productId]);
this.router.navigate(['/products'], { queryParams: { sort: 'price', page: 2 } });
```

## Child Routes

```typescript
export const PRODUCTS_ROUTES: Routes = [
  {
    path: '',
    component: ProductsLayoutComponent,
    children: [
      { path: '',    component: ProductListComponent },
      { path: ':id', component: ProductDetailComponent,
        children: [
          { path: 'reviews', component: ReviewsComponent },
          { path: 'specs',   component: SpecsComponent },
        ]},
    ],
  },
];
```

The parent template must include a `<router-outlet />` for child routes.

## Named Router Outlets

```typescript
{ path: 'chat', component: ChatComponent, outlet: 'sidebar' }

// Navigate to a named outlet
this.router.navigate([{ outlets: { sidebar: ['chat'] } }]);
```

```html
<router-outlet name="sidebar" />
```

## Title Strategy

Angular 14+ supports automatic page title management:

```typescript
{ path: 'users', title: 'Users — MyApp', component: UserListComponent }

// Or a dynamic title resolver:
{ path: 'users/:id', title: userTitleResolver, component: UserDetailComponent }
```

## Route Animations

```typescript
@Component({
  animations: [
    trigger('routeAnimation', [
      transition(':enter', [
        style({ opacity: 0 }),
        animate('200ms ease-in', style({ opacity: 1 })),
      ]),
    ]),
  ],
})
export class AppComponent {
  getRouteAnimation(outlet: RouterOutlet) {
    return outlet.activatedRouteData['animation'];
  }
}
```
"""

M6_EXERCISE_MD = "Implement URL path matching — the logic at the heart of the Angular Router."


def seed_module6(db: Session, course: Course) -> None:
    mod = _module(db, course, "Routing and Navigation", 6,
                  "Router configuration, lazy loading, guards, resolvers, and advanced routing.")

    _lesson(db, mod, "angular-router",
            title="Angular Router",
            lesson_type=LessonType.reading,
            content_md=M6_ROUTER_MD,
            duration_minutes=18,
            order_index=1)

    _lesson(db, mod, "advanced-routing",
            title="Advanced Routing",
            lesson_type=LessonType.reading,
            content_md=M6_ADVANCED_ROUTING_MD,
            duration_minutes=10,
            order_index=2)

    ex_lesson = _lesson(db, mod, "routing-exercises",
                        title="Route Path Matching",
                        lesson_type=LessonType.exercise,
                        content_md=M6_EXERCISE_MD,
                        duration_minutes=15,
                        order_index=3)

    # ── Exercise 6.1: URL Path Matcher ──────────────────────────────
    ex, _ = _exercise(db, ex_lesson, "url-path-matcher",
        title="URL Path Matcher",
        prompt_md=(
            "# URL Path Matcher\n\n"
            "Given a list of route patterns and a URL, determine which pattern "
            "matches and extract the parameters.\n\n"
            "Route patterns use `:param` for dynamic segments, e.g. `/users/:id` "
            "or `/posts/:year/:month`.\n\n"
            "**Input:**\n```\nn\npattern1\npattern2\n...\nurl\n```\n"
            "n patterns followed by the URL to match (all paths start with `/`).\n"
            "Match patterns in order — use the **first** match.\n\n"
            "**Output:**\n"
            "- If matched: `MATCH: <pattern>` on one line, then each extracted "
            "param as `<name>=<value>` sorted alphabetically by name.\n"
            "- If no match: `NO MATCH`\n\n"
            "**Example**\n```\nInput:\n3\n/users/:id\n/posts/:year/:month\n/about\n"
            "/posts/2024/03\n\nOutput:\nMATCH: /posts/:year/:month\nmonth=03\nyear=2024\n```"
        ),
        difficulty=Difficulty.medium,
        is_published=True,
        starter_code={
            "python": (
                "import sys\n\n"
                "def match_route(pattern, url):\n"
                "    \"\"\"Return dict of params if pattern matches url, else None.\"\"\"\n"
                "    p_parts = pattern.split('/')\n"
                "    u_parts = url.split('/')\n"
                "    if len(p_parts) != len(u_parts):\n"
                "        return None\n"
                "    params = {}\n"
                "    for p, u in zip(p_parts, u_parts):\n"
                "        if p.startswith(':'):\n"
                "            params[p[1:]] = u\n"
                "        elif p != u:\n"
                "            return None\n"
                "    return params\n\n"
                "lines = sys.stdin.read().splitlines()\n"
                "n = int(lines[0])\n"
                "patterns = [lines[i+1] for i in range(n)]\n"
                "url = lines[n + 1]\n\n"
                "# TODO: find the first matching pattern and print result\n"
            ),
            "javascript": (
                "const lines = require('fs').readFileSync(0, 'utf8').trim().split('\\n');\n"
                "const n = parseInt(lines[0]);\n"
                "const patterns = lines.slice(1, n + 1);\n"
                "const url = lines[n + 1].trim();\n\n"
                "function matchRoute(pattern, url) {\n"
                "    const pParts = pattern.split('/');\n"
                "    const uParts = url.split('/');\n"
                "    if (pParts.length !== uParts.length) return null;\n"
                "    const params = {};\n"
                "    for (let i = 0; i < pParts.length; i++) {\n"
                "        if (pParts[i].startsWith(':')) {\n"
                "            params[pParts[i].slice(1)] = uParts[i];\n"
                "        } else if (pParts[i] !== uParts[i]) return null;\n"
                "    }\n"
                "    return params;\n"
                "}\n\n"
                "// TODO: iterate patterns, find first match, print result\n"
            ),
            "typescript": (
                "import * as fs from 'fs';\n\n"
                "const lines = fs.readFileSync(0, 'utf8').trim().split('\\n');\n"
                "const n = parseInt(lines[0]);\n"
                "const patterns = lines.slice(1, n + 1);\n"
                "const url = lines[n + 1].trim();\n\n"
                "function matchRoute(pattern: string, url: string): Record<string,string> | null {\n"
                "    const pParts = pattern.split('/');\n"
                "    const uParts = url.split('/');\n"
                "    if (pParts.length !== uParts.length) return null;\n"
                "    const params: Record<string,string> = {};\n"
                "    for (let i = 0; i < pParts.length; i++) {\n"
                "        if (pParts[i].startsWith(':')) {\n"
                "            params[pParts[i].slice(1)] = uParts[i];\n"
                "        } else if (pParts[i] !== uParts[i]) return null;\n"
                "    }\n"
                "    return params;\n"
                "}\n\n"
                "// TODO: find first matching pattern and output result\n"
            ),
        },
        solution_code={
            "python": (
                "import sys\n"
                "def match_route(pattern, url):\n"
                "    p_parts = pattern.split('/')\n"
                "    u_parts = url.split('/')\n"
                "    if len(p_parts) != len(u_parts): return None\n"
                "    params = {}\n"
                "    for p, u in zip(p_parts, u_parts):\n"
                "        if p.startswith(':'): params[p[1:]] = u\n"
                "        elif p != u: return None\n"
                "    return params\n"
                "lines = sys.stdin.read().splitlines()\n"
                "n = int(lines[0])\n"
                "patterns = [lines[i+1] for i in range(n)]\n"
                "url = lines[n + 1]\n"
                "for pat in patterns:\n"
                "    params = match_route(pat, url)\n"
                "    if params is not None:\n"
                "        print(f'MATCH: {pat}')\n"
                "        for k in sorted(params):\n"
                "            print(f'{k}={params[k]}')\n"
                "        break\n"
                "else:\n"
                "    print('NO MATCH')\n"
            ),
        },
        supported_languages=WEB_LANGS,
        time_limit_ms=3000,
        memory_limit_mb=256,
        points=20,
    )
    _cases(db, ex, [
        ("match-two-params",
         "3\n/users/:id\n/posts/:year/:month\n/about\n/posts/2024/03\n",
         "MATCH: /posts/:year/:month\nmonth=03\nyear=2024",
         False, 1),
        ("match-one-param",
         "2\n/users/:id\n/about\n/users/42\n",
         "MATCH: /users/:id\nid=42",
         False, 1),
        ("match-static",
         "2\n/about\n/contact\n/about\n",
         "MATCH: /about",
         False, 1),
        ("no-match",
         "2\n/users/:id\n/about\n/posts/42\n",
         "NO MATCH",
         False, 1),
        ("first-match-wins",
         "3\n/items/:id\n/items/special\n/items/:slug\n/items/special\n",
         "MATCH: /items/:id\nid=special",
         True, 2),
    ])


# ════════════════════════════════════════════════════════════════
#  MODULE 7 — Forms
# ════════════════════════════════════════════════════════════════

M7_TEMPLATE_FORMS_MD = """\
# Template-Driven Forms

Template-driven forms use Angular directives in the template to build forms
declaratively. They are ideal for **simple forms** with straightforward validation.

## Setup

Import `FormsModule` in your component (standalone) or module:

```typescript
@Component({
  standalone: true,
  imports: [FormsModule],
  template: `...`,
})
export class LoginComponent {}
```

## ngModel and Two-Way Binding

```html
<form #loginForm="ngForm" (ngSubmit)="onSubmit(loginForm)">

  <input
    name="email"
    type="email"
    [(ngModel)]="formData.email"
    required
    email
    #emailField="ngModel"
  />
  <div *ngIf="emailField.invalid && emailField.touched">
    <span *ngIf="emailField.errors?.['required']">Email is required.</span>
    <span *ngIf="emailField.errors?.['email']">Invalid email format.</span>
  </div>

  <input
    name="password"
    type="password"
    [(ngModel)]="formData.password"
    required
    minlength="8"
    #passwordField="ngModel"
  />
  <div *ngIf="passwordField.invalid && passwordField.touched">
    <span *ngIf="passwordField.errors?.['minlength']">
      Min {{ passwordField.errors?.['minlength'].requiredLength }} chars.
    </span>
  </div>

  <button type="submit" [disabled]="loginForm.invalid">Login</button>
</form>
```

## CSS Classes

Angular automatically adds CSS classes to form controls:

| Class | Condition |
|-------|-----------|
| `ng-valid` / `ng-invalid` | Passes / fails validation |
| `ng-pristine` / `ng-dirty` | Not modified / modified |
| `ng-untouched` / `ng-touched` | Never blurred / blurred |

```scss
input.ng-invalid.ng-touched { border-color: red; }
input.ng-valid.ng-dirty      { border-color: green; }
```

## ngModelGroup

```html
<div ngModelGroup="address" #addrGroup="ngModelGroup">
  <input name="street" ngModel required />
  <input name="city"   ngModel required />
  <input name="zip"    ngModel pattern="\\d{5}" />
</div>
```

Groups related fields — useful for nested objects and reusable form sections.

## Accessing Form Value

```typescript
onSubmit(form: NgForm) {
  if (form.valid) {
    console.log(form.value);  // { email: '...', password: '...' }
    this.authService.login(form.value).subscribe(/* ... */);
  }
}
```
"""

M7_REACTIVE_FORMS_MD = """\
# Reactive Forms

Reactive forms define the form model in the component class using
`FormControl`, `FormGroup`, and `FormArray`. They are **more explicit**,
easier to test, and better suited for **complex validation** and dynamic forms.

## FormGroup and FormControl

```typescript
import { FormBuilder, FormGroup, Validators } from '@angular/forms';

@Component({ imports: [ReactiveFormsModule], /* ... */ })
export class RegisterComponent {
  form: FormGroup;

  constructor(private fb: FormBuilder) {
    this.form = this.fb.group({
      name:     ['', [Validators.required, Validators.minLength(2)]],
      email:    ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required, Validators.minLength(8)]],
      age:      [null, [Validators.required, Validators.min(18), Validators.max(120)]],
    });
  }

  get email() { return this.form.get('email')!; }

  onSubmit() {
    if (this.form.valid) {
      console.log(this.form.value);
    }
  }
}
```

```html
<form [formGroup]="form" (ngSubmit)="onSubmit()">
  <input formControlName="email" />
  <div *ngIf="email.invalid && email.touched">
    <span *ngIf="email.errors?.['required']">Required</span>
    <span *ngIf="email.errors?.['email']">Invalid email</span>
  </div>
  <button [disabled]="form.invalid">Register</button>
</form>
```

## Custom Validators

```typescript
// Synchronous validator
export function noSpaces(control: AbstractControl): ValidationErrors | null {
  return /\\s/.test(control.value) ? { noSpaces: true } : null;
}

// Password-match cross-field validator
export function passwordMatch(group: AbstractControl): ValidationErrors | null {
  const pw  = group.get('password')?.value;
  const cpw = group.get('confirmPassword')?.value;
  return pw === cpw ? null : { passwordMismatch: true };
}
```

## Async Validators

```typescript
export function uniqueEmailValidator(svc: UserService): AsyncValidatorFn {
  return (control: AbstractControl): Observable<ValidationErrors | null> =>
    timer(300).pipe(
      switchMap(() => svc.checkEmailExists(control.value)),
      map(exists => exists ? { emailTaken: true } : null),
    );
}
```

## FormArray — Dynamic Fields

```typescript
this.form = this.fb.group({
  tags: this.fb.array([this.fb.control('angular')]),
});

get tags() { return this.form.get('tags') as FormArray; }

addTag() {
  this.tags.push(this.fb.control('', Validators.required));
}

removeTag(i: number) {
  this.tags.removeAt(i);
}
```

```html
<div formArrayName="tags">
  @for (tag of tags.controls; track $index) {
    <input [formControlName]="$index" />
    <button (click)="removeTag($index)">-</button>
  }
</div>
<button (click)="addTag()">+ Add tag</button>
```

## Observing Changes

```typescript
this.form.get('email')!.valueChanges.pipe(
  debounceTime(300),
  distinctUntilChanged(),
).subscribe(value => this.checkEmail(value));

this.form.statusChanges.subscribe(status => {
  this.isValid = status === 'VALID';
});
```
"""

M7_EXERCISE_MD = "Implement form validation logic — replicate what Angular's Validators do under the hood."


def seed_module7(db: Session, course: Course) -> None:
    mod = _module(db, course, "Forms", 7,
                  "Template-driven and reactive forms with validation, FormArray, and custom validators.")

    _lesson(db, mod, "template-driven-forms",
            title="Template-Driven Forms",
            lesson_type=LessonType.reading,
            content_md=M7_TEMPLATE_FORMS_MD,
            duration_minutes=20,
            order_index=1)

    _lesson(db, mod, "reactive-forms",
            title="Reactive Forms",
            lesson_type=LessonType.reading,
            content_md=M7_REACTIVE_FORMS_MD,
            duration_minutes=20,
            order_index=2)

    ex_lesson = _lesson(db, mod, "form-validation-exercises",
                        title="Form Validation Logic",
                        lesson_type=LessonType.exercise,
                        content_md=M7_EXERCISE_MD,
                        duration_minutes=20,
                        order_index=3)

    # ── Exercise 7.1: Form Validator ─────────────────────────────────
    ex, _ = _exercise(db, ex_lesson, "form-validator",
        title="Form Validator",
        prompt_md=(
            "# Form Validator\n\n"
            "Validate a form submission with these rules:\n\n"
            "- `email` — must contain exactly one `@` character\n"
            "- `password` — must be at least 8 characters long\n"
            "- `age` — must be an integer between 18 and 120 (inclusive)\n\n"
            "**Input:** field=value lines (one per field), terminated by a blank line.\n"
            "Only the three fields above will appear. Each field appears exactly once.\n\n"
            "**Output:**\n"
            "- `VALID` if all fields pass\n"
            "- Otherwise print each failing field error on its own line in "
            "alphabetical order by field name:\n"
            "  - `age: must be between 18 and 120`\n"
            "  - `email: invalid format`\n"
            "  - `password: must be at least 8 characters`\n\n"
            "**Example**\n```\nInput:\nemail=user@example.com\npassword=secret\nage=25\n\n"
            "Output:\npassword: must be at least 8 characters\n```"
        ),
        difficulty=Difficulty.easy,
        is_published=True,
        starter_code={
            "python": (
                "import sys\n\n"
                "data = {}\n"
                "for line in sys.stdin:\n"
                "    line = line.rstrip('\\n')\n"
                "    if not line:\n"
                "        break\n"
                "    key, _, val = line.partition('=')\n"
                "    data[key] = val\n\n"
                "errors = []\n"
                "# TODO: validate email, password, age\n"
                "# Append error strings to errors list in alphabetical order\n"
                "if errors:\n"
                "    print('\\n'.join(errors))\n"
                "else:\n"
                "    print('VALID')\n"
            ),
            "javascript": (
                "const input = require('fs').readFileSync(0, 'utf8');\n"
                "const lines = input.split('\\n');\n"
                "const data = {};\n"
                "for (const line of lines) {\n"
                "    if (!line.trim()) break;\n"
                "    const [key, ...rest] = line.split('=');\n"
                "    data[key.trim()] = rest.join('=');\n"
                "}\n\n"
                "const errors = [];\n"
                "// TODO: validate email, password, age\n"
                "if (errors.length) console.log(errors.join('\\n'));\n"
                "else console.log('VALID');\n"
            ),
            "typescript": (
                "import * as fs from 'fs';\n\n"
                "const lines = fs.readFileSync(0, 'utf8').split('\\n');\n"
                "const data: Record<string, string> = {};\n"
                "for (const line of lines) {\n"
                "    if (!line.trim()) break;\n"
                "    const eqIdx = line.indexOf('=');\n"
                "    data[line.substring(0, eqIdx).trim()] = line.substring(eqIdx + 1);\n"
                "}\n\n"
                "const errors: string[] = [];\n"
                "// Validate email\n"
                "const emailVal = data['email'] ?? '';\n"
                "// TODO: check for exactly one '@'\n"
                "// Validate password\n"
                "const pwVal = data['password'] ?? '';\n"
                "// TODO: check length >= 8\n"
                "// Validate age\n"
                "const ageVal = parseInt(data['age'] ?? '');\n"
                "// TODO: check 18 <= age <= 120\n\n"
                "if (errors.length) console.log(errors.join('\\n'));\n"
                "else console.log('VALID');\n"
            ),
        },
        solution_code={
            "python": (
                "import sys\n"
                "data = {}\n"
                "for line in sys.stdin:\n"
                "    line = line.rstrip('\\n')\n"
                "    if not line: break\n"
                "    key, _, val = line.partition('=')\n"
                "    data[key] = val\n"
                "errors = []\n"
                "email = data.get('email', '')\n"
                "if email.count('@') != 1:\n"
                "    errors.append('email: invalid format')\n"
                "pw = data.get('password', '')\n"
                "if len(pw) < 8:\n"
                "    errors.append('password: must be at least 8 characters')\n"
                "try:\n"
                "    age = int(data.get('age', ''))\n"
                "    if not (18 <= age <= 120):\n"
                "        errors.append('age: must be between 18 and 120')\n"
                "except ValueError:\n"
                "    errors.append('age: must be between 18 and 120')\n"
                "errors.sort()\n"
                "print('\\n'.join(errors) if errors else 'VALID')\n"
            ),
        },
        supported_languages=WEB_LANGS,
        time_limit_ms=3000,
        memory_limit_mb=256,
        points=15,
    )
    _cases(db, ex, [
        ("all-valid",
         "email=user@example.com\npassword=securepass\nage=25\n\n",
         "VALID",
         False, 1),
        ("short-password",
         "email=user@example.com\npassword=secret\nage=25\n\n",
         "password: must be at least 8 characters",
         False, 1),
        ("invalid-email",
         "email=notanemail\npassword=securepass\nage=25\n\n",
         "email: invalid format",
         False, 1),
        ("age-too-young",
         "email=a@b.com\npassword=securepass\nage=16\n\n",
         "age: must be between 18 and 120",
         False, 1),
        ("multiple-errors",
         "email=bademail\npassword=short\nage=200\n\n",
         "age: must be between 18 and 120\nemail: invalid format\npassword: must be at least 8 characters",
         False, 1),
        ("all-valid-boundary",
         "email=admin@corp.org\npassword=12345678\nage=18\n\n",
         "VALID",
         True, 2),
    ])


# ════════════════════════════════════════════════════════════════
#  MODULE 8 — HTTP Client and RxJS
# ════════════════════════════════════════════════════════════════

M8_HTTP_MD = """\
# HttpClient and Interceptors

## Setting Up HttpClient

In standalone Angular 17+:

```typescript
// app.config.ts
import { provideHttpClient, withInterceptors } from '@angular/common/http';

export const appConfig: ApplicationConfig = {
  providers: [
    provideHttpClient(
      withInterceptors([authInterceptor, loadingInterceptor]),
    ),
  ],
};
```

## Making HTTP Requests

```typescript
@Injectable({ providedIn: 'root' })
export class ProductService {
  private apiUrl = inject(API_BASE_URL);
  private http   = inject(HttpClient);

  getProducts(page = 1, sort = 'name'): Observable<Product[]> {
    const params = new HttpParams()
      .set('page', page)
      .set('sort', sort);
    return this.http.get<Product[]>(`${this.apiUrl}/products`, { params });
  }

  createProduct(dto: CreateProductDto): Observable<Product> {
    const headers = new HttpHeaders({ 'Content-Type': 'application/json' });
    return this.http.post<Product>(`${this.apiUrl}/products`, dto, { headers });
  }

  updateProduct(id: number, dto: Partial<Product>): Observable<Product> {
    return this.http.put<Product>(`${this.apiUrl}/products/${id}`, dto);
  }

  deleteProduct(id: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/products/${id}`);
  }
}
```

## Error Handling

```typescript
import { catchError, throwError } from 'rxjs';

getProduct(id: number): Observable<Product> {
  return this.http.get<Product>(`/api/products/${id}`).pipe(
    catchError(err => {
      if (err.status === 404) return throwError(() => new Error('Not found'));
      return throwError(() => err);
    }),
  );
}
```

## HTTP Interceptors (Functional)

```typescript
// Auth interceptor — attaches bearer token
export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const token = inject(AuthService).getToken();
  if (!token) return next(req);

  const authReq = req.clone({
    headers: req.headers.set('Authorization', `Bearer ${token}`),
  });
  return next(authReq);
};

// Loading indicator interceptor
export const loadingInterceptor: HttpInterceptorFn = (req, next) => {
  const loading = inject(LoadingService);
  loading.show();
  return next(req).pipe(
    finalize(() => loading.hide()),
  );
};
```

## HttpContext

Pass arbitrary data through the interceptor chain without modifying the request:

```typescript
export const SKIP_AUTH = new HttpContextToken<boolean>(() => false);

// In service — skip auth for this specific request
this.http.get('/api/public', {
  context: new HttpContext().set(SKIP_AUTH, true),
});

// In interceptor
if (req.context.get(SKIP_AUTH)) return next(req);
```
"""

M8_RXJS_MD = """\
# RxJS Essentials

RxJS (Reactive Extensions for JavaScript) is Angular's default library for
handling asynchronous data streams. Mastering RxJS is key to writing clean,
composable async code.

## Observable vs Promise

| | Observable | Promise |
|-|-----------|---------|
| Values | 0..∞ values over time | Exactly 1 value |
| Lazy | Yes — nothing until subscribe | Eager — starts immediately |
| Cancellable | Yes (unsubscribe) | No |
| Operators | Rich (100+) | `.then()` / `.catch()` only |
| Use for | Streams, retries, complex async | One-shot async ops |

## Creation Operators

```typescript
of(1, 2, 3)                // sync: emit 1, 2, 3 then complete
from([1, 2, 3])            // sync: same but from iterable/promise
interval(1000)             // emit 0, 1, 2... every second
timer(2000, 1000)          // after 2s, emit every 1s
fromEvent(button, 'click') // emit on DOM events
EMPTY                      // complete immediately
NEVER                      // never complete or emit
```

## Transformation Operators

```typescript
// map — transform each value
of(1, 2, 3).pipe(map(x => x * 2))  // 2, 4, 6

// switchMap — cancel previous inner observable on new emission
searchInput$.pipe(
  debounceTime(300),
  switchMap(query => this.http.get(`/api/search?q=${query}`)),
)

// mergeMap — run all inner observables concurrently
requests$.pipe(mergeMap(req => this.http.post('/api', req)))

// concatMap — queue inner observables, run sequentially
actions$.pipe(concatMap(action => this.processAction(action)))

// exhaustMap — ignore new source emissions while inner is active
loginBtn$.pipe(exhaustMap(() => this.authService.login(creds)))
```

## Filtering Operators

```typescript
filter(x => x > 0)           // only pass values that satisfy predicate
take(3)                       // complete after 3 emissions
takeUntil(destroy$)           // complete when destroy$ emits (clean unsubscribe)
debounceTime(300)             // wait 300ms after last emission
distinctUntilChanged()        // skip duplicate consecutive emissions
throttleTime(1000)            // emit max once per second
```

## Combination Operators

```typescript
// combineLatest — emit when any source emits (using latest from all)
combineLatest([user$, settings$]).pipe(
  map(([user, settings]) => ({ user, settings })),
)

// forkJoin — wait for all to complete, emit last values as array
forkJoin([this.http.get('/api/user'), this.http.get('/api/settings')])
  .subscribe(([user, settings]) => { /* both loaded */ });

// zip — emit tuples pairing nth emission from each source
zip(ids$, names$)  // [id1, name1], [id2, name2], ...
```

## Error Handling

```typescript
this.http.get('/api/data').pipe(
  retry(3),                           // retry up to 3 times on error
  catchError(err => of({ error: true, message: err.message })),
)

// retryWhen with exponential backoff
retryWhen(errors => errors.pipe(
  delayWhen((_, i) => timer(Math.pow(2, i) * 1000)),
  take(3),
))
```

## Memory Leak Prevention

Always unsubscribe from observables that outlive the component:

```typescript
// Approach 1: takeUntilDestroyed (Angular 16+, cleanest)
data$ = this.service.getData().pipe(takeUntilDestroyed());

// Approach 2: Subject + takeUntil
private destroy$ = new Subject<void>();
ngOnDestroy() { this.destroy$.next(); this.destroy$.complete(); }
// In subscriptions:
.pipe(takeUntil(this.destroy$)).subscribe(...)
```
"""

M8_EXERCISE_MD = "Implement reactive stream processing logic — the foundation of RxJS pipelines."


def seed_module8(db: Session, course: Course) -> None:
    mod = _module(db, course, "HTTP Client and RxJS", 8,
                  "HttpClient, interceptors, and RxJS operators for reactive data streams.")

    _lesson(db, mod, "httpclient-interceptors",
            title="HttpClient and Interceptors",
            lesson_type=LessonType.reading,
            content_md=M8_HTTP_MD,
            duration_minutes=22,
            order_index=1)

    _lesson(db, mod, "rxjs-essentials",
            title="RxJS Essentials",
            lesson_type=LessonType.reading,
            content_md=M8_RXJS_MD,
            duration_minutes=20,
            order_index=2)

    ex_lesson = _lesson(db, mod, "rxjs-stream-exercises",
                        title="Reactive Streams Logic",
                        lesson_type=LessonType.exercise,
                        content_md=M8_EXERCISE_MD,
                        duration_minutes=25,
                        order_index=3)

    # ── Exercise 8.1: RxJS Stream Processor ─────────────────────────
    ex, _ = _exercise(db, ex_lesson, "rxjs-stream-processor",
        title="RxJS Stream Processor",
        prompt_md=(
            "# RxJS Stream Processor\n\n"
            "Simulate an RxJS-style stream pipeline by processing commands that "
            "build up and transform a list of emitted values:\n\n"
            "- `EMIT value` — add integer value to the current stream\n"
            "- `FILTER min max` — keep only values where min <= value <= max "
            "(applied to current stream values)\n"
            "- `MAP multiply` — multiply every value in the stream by the integer multiply\n"
            "- `TAKE n` — keep only the first n values in the stream\n"
            "- `PRINT` — print the current stream values space-separated on one line. "
            "If the stream is empty, print `(empty)`\n\n"
            "Commands are processed in order. The stream starts empty.\n\n"
            "**Input:**\n```\nm\ncmd1\ncmd2\n...\n```\n\n"
            "**Output:** one line per PRINT command.\n\n"
            "**Example**\n```\nInput:\n7\nEMIT 1\nEMIT 2\nEMIT 3\nEMIT 4\nEMIT 5\n"
            "FILTER 2 4\nPRINT\n\nOutput:\n2 3 4\n```"
        ),
        difficulty=Difficulty.medium,
        is_published=True,
        starter_code={
            "python": (
                "import sys\n\n"
                "lines = sys.stdin.read().splitlines()\n"
                "m = int(lines[0])\n"
                "stream = []\n\n"
                "for i in range(1, m + 1):\n"
                "    parts = lines[i].split()\n"
                "    cmd = parts[0]\n"
                "    if cmd == 'EMIT':\n"
                "        stream.append(int(parts[1]))\n"
                "    elif cmd == 'FILTER':\n"
                "        lo, hi = int(parts[1]), int(parts[2])\n"
                "        # TODO: keep only values in [lo, hi]\n"
                "    elif cmd == 'MAP':\n"
                "        factor = int(parts[1])\n"
                "        # TODO: multiply each value by factor\n"
                "    elif cmd == 'TAKE':\n"
                "        n = int(parts[1])\n"
                "        # TODO: keep only first n values\n"
                "    elif cmd == 'PRINT':\n"
                "        # TODO: print stream or '(empty)'\n"
                "        pass\n"
            ),
            "javascript": (
                "const lines = require('fs').readFileSync(0, 'utf8').trim().split('\\n');\n"
                "const m = parseInt(lines[0]);\n"
                "let stream = [];\n\n"
                "for (let i = 1; i <= m; i++) {\n"
                "    const parts = lines[i].trim().split(' ');\n"
                "    const cmd = parts[0];\n"
                "    if (cmd === 'EMIT') {\n"
                "        stream.push(parseInt(parts[1]));\n"
                "    } else if (cmd === 'FILTER') {\n"
                "        const lo = parseInt(parts[1]), hi = parseInt(parts[2]);\n"
                "        stream = stream.filter(v => v >= lo && v <= hi);\n"
                "    } else if (cmd === 'MAP') {\n"
                "        const factor = parseInt(parts[1]);\n"
                "        // TODO: map stream\n"
                "    } else if (cmd === 'TAKE') {\n"
                "        // TODO: slice stream\n"
                "    } else if (cmd === 'PRINT') {\n"
                "        // TODO: print stream or '(empty)'\n"
                "    }\n"
                "}\n"
            ),
            "typescript": (
                "import * as fs from 'fs';\n\n"
                "const lines = fs.readFileSync(0, 'utf8').trim().split('\\n');\n"
                "const m = parseInt(lines[0]);\n"
                "let stream: number[] = [];\n\n"
                "for (let i = 1; i <= m; i++) {\n"
                "    const parts = lines[i].trim().split(' ');\n"
                "    const cmd = parts[0];\n"
                "    if (cmd === 'EMIT') {\n"
                "        stream.push(parseInt(parts[1]));\n"
                "    } else if (cmd === 'FILTER') {\n"
                "        const lo = parseInt(parts[1]), hi = parseInt(parts[2]);\n"
                "        stream = stream.filter(v => v >= lo && v <= hi);\n"
                "    } else if (cmd === 'MAP') {\n"
                "        const factor = parseInt(parts[1]);\n"
                "        stream = stream.map(v => v * factor);\n"
                "    } else if (cmd === 'TAKE') {\n"
                "        const n = parseInt(parts[1]);\n"
                "        stream = stream.slice(0, n);\n"
                "    } else if (cmd === 'PRINT') {\n"
                "        console.log(stream.length ? stream.join(' ') : '(empty)');\n"
                "    }\n"
                "}\n"
            ),
        },
        solution_code={
            "python": (
                "import sys\n"
                "lines = sys.stdin.read().splitlines()\n"
                "m = int(lines[0])\n"
                "stream = []\n"
                "out = []\n"
                "for i in range(1, m + 1):\n"
                "    parts = lines[i].split()\n"
                "    cmd = parts[0]\n"
                "    if cmd == 'EMIT':\n"
                "        stream.append(int(parts[1]))\n"
                "    elif cmd == 'FILTER':\n"
                "        lo, hi = int(parts[1]), int(parts[2])\n"
                "        stream = [v for v in stream if lo <= v <= hi]\n"
                "    elif cmd == 'MAP':\n"
                "        factor = int(parts[1])\n"
                "        stream = [v * factor for v in stream]\n"
                "    elif cmd == 'TAKE':\n"
                "        n = int(parts[1])\n"
                "        stream = stream[:n]\n"
                "    elif cmd == 'PRINT':\n"
                "        out.append(' '.join(map(str, stream)) if stream else '(empty)')\n"
                "print('\\n'.join(out))\n"
            ),
        },
        supported_languages=WEB_LANGS,
        time_limit_ms=3000,
        memory_limit_mb=256,
        points=20,
    )
    _cases(db, ex, [
        ("filter-basic",
         "7\nEMIT 1\nEMIT 2\nEMIT 3\nEMIT 4\nEMIT 5\nFILTER 2 4\nPRINT\n",
         "2 3 4",
         False, 1),
        ("map-basic",
         "4\nEMIT 1\nEMIT 2\nEMIT 3\nMAP 10\nPRINT\n",
         "10 20 30",
         False, 1),
        ("take-basic",
         "5\nEMIT 10\nEMIT 20\nEMIT 30\nTAKE 2\nPRINT\n",
         "10 20",
         False, 1),
        ("empty-stream",
         "3\nEMIT 1\nFILTER 5 10\nPRINT\n",
         "(empty)",
         False, 1),
        ("combined-pipeline",
         "9\nEMIT 1\nEMIT 2\nEMIT 3\nEMIT 4\nEMIT 5\nFILTER 2 5\nMAP 3\nTAKE 2\nPRINT\n",
         "6 9",
         True, 2),
    ])


# ════════════════════════════════════════════════════════════════
#  Entry point
# ════════════════════════════════════════════════════════════════

def seed() -> None:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        # Require that app/seed.py has already run
        web = _subject(db, "web-development")
        if web is None:
            raise RuntimeError(
                "Subject 'web-development' not found. "
                "Run app/seed.py first to create the subject and stub course."
            )

        course = _course(db, "modern-frontend-angular")
        if course is None:
            raise RuntimeError(
                "Course 'modern-frontend-angular' not found. "
                "Run app/seed.py first to create the stub course."
            )

        print(f"Seeding course: {course.title!r} (subject: {web.name!r})")

        seed_module1(db, course)
        print("  Module 1: TypeScript Essentials — done")

        seed_module2(db, course)
        print("  Module 2: Angular Architecture — done")

        seed_module3(db, course)
        print("  Module 3: Components and Templates — done")

        seed_module4(db, course)
        print("  Module 4: Directives and Pipes — done")

        seed_module5(db, course)
        print("  Module 5: Services and Dependency Injection — done")

        seed_module6(db, course)
        print("  Module 6: Routing and Navigation — done")

        seed_module7(db, course)
        print("  Module 7: Forms — done")

        seed_module8(db, course)
        print("  Module 8: HTTP Client and RxJS — done")

        db.commit()
        print("\nDone! 8 modules seeded for 'Modern Frontend with Angular'.")
        print("  24 lessons total (16 reading + 8 exercise)")
        print("  9 exercises with 45 test cases")


if __name__ == "__main__":
    seed()
