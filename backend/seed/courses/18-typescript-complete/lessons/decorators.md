# Decorators in TypeScript

TypeScript has **two incompatible decorator systems** that cannot coexist in the same project. Knowing which one you are using matters because the APIs are different and tooling support varies.

| System | How to enable | Status |
|---|---|---|
| **Legacy decorators** | `"experimentalDecorators": true` in tsconfig | Stable in Angular, NestJS, TypeORM |
| **TC39 Stage 3 decorators** | No flag needed (TypeScript 5.0+) | ECMAScript standard; different API |

> **Key difference:** Legacy decorators pre-date the TC39 standard. A legacy class decorator receives the constructor alone. A Stage 3 class decorator receives the constructor **and a context object** with metadata about the decorated element. The two systems are mutually exclusive — enabling `experimentalDecorators` disables Stage 3 support.

This lesson covers **legacy decorators** first (the system used by most real-world frameworks today), then shows the Stage 3 API.

## Enabling legacy decorators

```json
// tsconfig.json
{
  "compilerOptions": {
    "experimentalDecorators": true,
    "emitDecoratorMetadata": true
  }
}
```

`emitDecoratorMetadata` is optional but required by dependency injection frameworks that introspect constructor parameter types via `Reflect.metadata`.

## Using TC39 Stage 3 decorators (TypeScript 5.0+, no flag)

```json
{
  "compilerOptions": {
    "target": "ES2022"
  }
}
```

## Class decorators

A class decorator receives the constructor and can return a new one:

```ts
function Singleton<T extends { new(...args: any[]): {} }>(Base: T) {
  let instance: InstanceType<T>;
  return class extends Base {
    constructor(...args: any[]) {
      if (instance) return instance;
      super(...args);
      instance = this as any;
    }
  };
}

@Singleton
class Database {
  connected = false;
}

const a = new Database();
const b = new Database();
console.log(a === b);  // true
```

## Method decorators

A method decorator receives the target (prototype), property name, and descriptor:

```ts
function log(
  target: any,
  propertyKey: string,
  descriptor: PropertyDescriptor
) {
  const original = descriptor.value;
  descriptor.value = function (...args: any[]) {
    console.log(`[${propertyKey}] called with`, args);
    const result = original.apply(this, args);
    console.log(`[${propertyKey}] returned`, result);
    return result;
  };
  return descriptor;
}

class Calculator {
  @log
  add(a: number, b: number): number {
    return a + b;
  }
}

new Calculator().add(2, 3);
// [add] called with [2, 3]
// [add] returned 5
```

## Property decorators

Property decorators receive the target and property name. They cannot directly affect the property value but are used to record metadata:

```ts
const required = new Set<string>();

function Required(target: any, propertyKey: string) {
  required.add(propertyKey);
}

class UserDto {
  @Required
  name!: string;

  @Required
  email!: string;

  age?: number;
}

console.log(required);  // Set { 'name', 'email' }
```

## Parameter decorators

Used primarily by dependency injection frameworks (e.g., NestJS, Angular):

```ts
import "reflect-metadata";

function Inject(token: symbol) {
  return function (
    target: any,
    propertyKey: string | undefined,
    parameterIndex: number
  ) {
    // record token -> param index mapping
    const existing: Map<number, symbol> =
      Reflect.getOwnMetadata("di:params", target) ?? new Map();
    existing.set(parameterIndex, token);
    Reflect.defineMetadata("di:params", existing, target);
  };
}
```

## Decorator factories

A decorator factory is a function that returns a decorator — allowing configuration:

```ts
function Retry(times: number) {
  return function (
    target: any,
    key: string,
    descriptor: PropertyDescriptor
  ) {
    const original = descriptor.value;
    descriptor.value = async function (...args: any[]) {
      for (let attempt = 1; attempt <= times; attempt++) {
        try {
          return await original.apply(this, args);
        } catch (e) {
          if (attempt === times) throw e;
          console.warn(`Retrying ${key} (${attempt}/${times})`);
        }
      }
    };
    return descriptor;
  };
}

class ApiService {
  @Retry(3)
  async fetchData(url: string): Promise<Response> {
    return fetch(url);
  }
}
```

## Common real-world decorators

| Decorator | Framework | Purpose |
|---|---|---|
| `@Component` | Angular | Marks a class as an Angular component |
| `@Injectable` | Angular / NestJS | Registers a class for DI |
| `@Controller` | NestJS | HTTP route controller |
| `@Get`, `@Post` | NestJS | HTTP method handler |
| `@Column`, `@Entity` | TypeORM | Database ORM mapping |
| `@IsEmail` | class-validator | Runtime validation |

## Stage 3 class decorator API (TypeScript 5.0+)

The new standard decorator receives two arguments: the value being decorated and a context object:

```ts
// Stage 3 — no experimentalDecorators flag
function sealed(target: Function, context: ClassDecoratorContext) {
  context.addInitializer(function () {
    Object.seal(this);
  });
}

@sealed
class Config {
  apiUrl = "https://api.example.com";
}
```

Stage 3 method decorators:

```ts
function logged(
  target: (this: unknown, ...args: unknown[]) => unknown,
  context: ClassMethodDecoratorContext
) {
  return function (this: unknown, ...args: unknown[]) {
    console.log(`[${String(context.name)}] called`);
    return target.apply(this, args);
  };
}

class Service {
  @logged
  fetchData(url: string) { /* ... */ }
}
```

> The context object provides `context.name`, `context.kind` (`"class"`, `"method"`, `"field"`, etc.), `context.static`, and `context.private`. This is fundamentally different from the legacy three-argument `(target, propertyKey, descriptor)` API.

## Further reading

- [TypeScript Handbook — Decorators](https://www.typescriptlang.org/docs/handbook/decorators.html) — covers legacy decorators in depth
- [TypeScript 5.0 release notes](https://devblogs.microsoft.com/typescript/announcing-typescript-5-0/) — Stage 3 decorator introduction
- *TypeScript Deep Dive* by Basarat Ali Syed ([basarat.gitbook.io/typescript](https://basarat.gitbook.io/typescript)) — practical decorator patterns

## Key takeaways

- TypeScript has **two incompatible decorator systems**: legacy (`experimentalDecorators`) and TC39 Stage 3 (TypeScript 5.0+, no flag).
- Legacy decorators are what Angular, NestJS, TypeORM, and class-validator use today.
- Stage 3 decorators use a new API: `(target, context)` instead of `(target, key, descriptor)`.
- Method decorators are the most flexible — they can fully replace a method.
- Avoid overusing decorators for business logic; prefer them for cross-cutting concerns (logging, retry, auth).
