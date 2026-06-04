# Quiz: Decorators and Metadata

Test your understanding of TypeScript decorators, the two decorator systems, and their real-world use cases.

**Q1. Legacy decorators (`experimentalDecorators`) and TC39 Stage 3 decorators (TypeScript 5.0+) are:**
- [ ] The same system with slightly different syntax
- [x] Two incompatible systems — they cannot be mixed in the same project
- [ ] Equivalent; the flag just enables older tooling support
- [ ] Both stable standards

**Q2. Which tsconfig flag enables the legacy decorator system used by Angular and NestJS?**
- [x] `"experimentalDecorators": true`
- [ ] `"useDecorators": true`
- [ ] `"target": "ES2022"`
- [ ] `"strict": false`

**Q3. A decorator factory is:**
- [ ] A decorator applied to a class factory function
- [x] A function that returns a decorator, allowing the decorator to accept configuration arguments
- [ ] A built-in TypeScript utility for generating decorators
- [ ] A decorator that creates new class instances

**Q4. In which order are stacked decorators evaluated? Given `@A @B @C` on a method:**
- [ ] A, B, C (top to bottom)
- [x] C, B, A (bottom to top — innermost first)
- [ ] B, A, C (alphabetical)
- [ ] All simultaneously

**Q5. `emitDecoratorMetadata: true` enables:**
- [ ] Decorators to run at build time
- [x] Emission of type metadata via `Reflect.metadata`, used by DI frameworks like NestJS and Angular
- [ ] Stage 3 decorator support
- [ ] Decorator composition

**Q6. Which of the following is the best use case for decorators?**
- [ ] Core business logic
- [ ] Data transformations in service layers
- [x] Cross-cutting concerns: logging, retry, authentication, validation
- [ ] Replacing interfaces for type checking

**Q7. In TC39 Stage 3 decorators (TypeScript 5.0+), a class decorator receives:**
- [ ] The class constructor alone
- [x] The class constructor AND a context object with metadata about the decorated element
- [ ] The class prototype
- [ ] An array of all applied decorators
