# Decorators in TypeScript

Decorators are a stage-3 ECMAScript proposal (enabled with `"experimentalDecorators": true` in older TS, or natively in TS 5.0+ with the new standard decorator syntax). They add metadata or behaviour to classes, methods, properties, and parameters with a clean `@` syntax.

## Enabling decorators

For **legacy decorators** (most Angular / NestJS projects):

```json
// tsconfig.json
{
  "compilerOptions": {
    "experimentalDecorators": true,
    "emitDecoratorMetadata": true
  }
}
```

For **TC39 stage-3 decorators** (TS 5.0+, no flag needed):

```json
{
  "compilerOptions": {
    "target": "ES2022"
  }
}
```

This lesson uses the legacy syntax (most common in real codebases today).

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

## Key takeaways

- Decorators are syntactic sugar for wrapping or annotating class-related constructs.
- Legacy decorators (`experimentalDecorators`) are stable in real frameworks today.
- Method decorators are the most flexible — they can fully replace a method.
- Avoid overusing decorators for business logic; prefer them for cross-cutting concerns (logging, retry, auth).
