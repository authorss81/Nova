# ⭐ Nova Programming Language — Master Roadmap

> A world-class, web-development focused programming language with built-in AI capabilities.
> **Phase 0.x.x.x** — Python implementation (design, prototype, spec)
> **Phase 1.x.x.x** — Rust rewrite (performance, WASM, production)

---

## Syntax Philosophy

Nova uses a **Python-inspired, English-leaning syntax** — indentation-based blocks, English keywords where they read naturally, and minimal punctuation. The goal: a non-programmer can read Nova code and roughly understand it; a web developer can learn it in a day.

**Core principles:**
- Indentation + `:` defines blocks — no `{ }` braces
- English keywords for logic: `not`, `and`, `or`, `is`, `where`, `as`
- Web-native keywords as first-class: `page`, `route`, `component`, `on`, `send`, `find`
- `->` for return types and navigation; `=>` for lambdas
- Operators `+`, `-`, `==`, `!=`, `?`, `??` kept (universal, unambiguous)
- No semicolons; newlines are meaningful

**What Nova code looks like:**
```nova
page Home:
  title "Welcome to Nova"

  component Greeting(name: text):
    heading "Hello, {name}!"
    button "Get Started" -> navigate("/app")

route GET "/users/:id":
  let user = find User where id is params.id
  if not user: send 404 "User not found"
  send user as json

fn greet(name: text) -> text:
  return "Hello, {name}!"

on button "#submit" click:
  let data = form("#signup").values()
  let result = await post("/api/signup", data)
  if result.ok: navigate("/welcome")
```

---

## Version Format: `a.x.y.z`

| Segment | Meaning |
|---|---|
| `a` | Major era: `0` = Python prototype, `1` = Rust production |
| `x` | Milestone group (lexer=0, parser=1, types=4, web=5, etc.) |
| `y` | Sub-milestone within a group |
| `z` | Micro-version: exactly 1–2 features per step |

---

## PHASE 0 — Python Implementation

---

## MILESTONE 0.0 — Project Foundation & Lexer

### `0.0.0.1` — Project Skeleton
- Directory layout: `/src`, `/tests`, `/examples`, `/docs`, `/stdlib`, `/tools`
- CLI entry point: `nova run <file.nv>`, `nova --version`, `nova --help`
- `NovaError` base class with `message`, `line`, `col`, `filename`, `hint` fields

### `0.0.0.2` — Source File Handling
- `SourceFile` class: reads `.nv` files, tracks UTF-8 encoding
- Line/column tracker built into file reader
- Shebang line support (`#!/usr/bin/env nova`)

### `0.0.0.3` — Tokenizer Core
- `TokenType` enum covering all token categories
- `Token` dataclass: `type`, `value`, `line`, `col`, `length`
- `Lexer` class: character-by-character scanner with lookahead

### `0.0.0.4` — Tokenizer: Keywords & Identifiers
- All reserved keywords: `let`, `const`, `fn`, `return`, `if`, `else`, `for`, `while`,
  `in`, `break`, `continue`, `true`, `false`, `null`, `import`, `export`, `from`,
  `class`, `extends`, `new`, `this`, `super`, `static`, `async`, `await`,
  `try`, `catch`, `finally`, `throw`, `match`, `case`, `type`, `interface`,
  `enum`, `as`, `is`, `of`, `yield`, `page`, `component`, `style`, `route`, `ai`,
  `not`, `and`, `or`, `where`, `on`, `send`, `find`, `show`, `give`, `with`
- Unicode identifiers support
- `_` (underscore) as valid identifier

### `0.0.0.5` — Tokenizer: Literals
- Integer literals: decimal (`123`), hex (`0xFF`), octal (`0o77`), binary (`0b1010`)
- Float literals: `3.14`, `1.5e10`, `1_000_000` (underscore separators)
- Boolean literals: `true`, `false`
- `null` literal

### `0.0.0.6` — Tokenizer: String Literals
- Single-line strings: `"hello"` and `'hello'`
- Escape sequences: `\n`, `\t`, `\r`, `\\`, `\"`, `\'`, `\0`, `\uXXXX`
- Template strings with backtick: `` `Hello {name}` `` (lex as parts)
- Raw strings: `r"no\escape"` — no escape processing

### `0.0.0.7` — Tokenizer: Operators & Delimiters
- Arithmetic: `+`, `-`, `*`, `/`, `%`, `**` (exponent)
- Comparison: `==`, `!=`, `<`, `>`, `<=`, `>=`
- Logical: `&&`, `||`, `!`
- Assignment: `=`, `+=`, `-=`, `*=`, `/=`, `%=`, `**=`, `&&=`, `||=`, `??=`
- Bitwise: `&`, `|`, `^`, `~`, `<<`, `>>`
- Special: `?.` (optional chain), `??` (nullish coalesce), `...` (spread), `->`, `=>`
- Delimiters: `(`, `)`, `[`, `]`, `{`, `}`, `,`, `;`, `:`, `.`

### `0.0.0.8` — Tokenizer: Comments & Whitespace
- Single-line `//` comments
- Multi-line `/* */` comments (nesting NOT supported)
- Doc comments: `///` — preserved as tokens for doc generation
- Whitespace and newline handling (significant newlines in some contexts)

### `0.0.0.9` — Tokenizer: Test Suite
- 100+ unit tests covering every token type
- Edge cases: empty file, only comments, very long identifiers, max integer values
- Unicode stress tests

---

## MILESTONE 0.1 — Parser & AST

### `0.1.0.1` — AST: Base Node Definitions
- `Node` base dataclass: `kind`, `span` (start/end position)
- `Program` node: list of top-level statements
- AST visitor base class with `visit(node)` dispatch
- AST pretty-printer (`dump_ast()`) for debugging

### `0.1.0.2` — AST: Literal & Primary Nodes
- `NumberLiteral`, `StringLiteral`, `BoolLiteral`, `NullLiteral`
- `Identifier`, `TemplateLiteral` (parts list), `RegexLiteral`
- `ArrayLiteral`, `ObjectLiteral` (key-value pairs)

### `0.1.0.3` — Parser: Pratt Expression Parser
- Recursive-descent Pratt parser for operator precedence
- Prefix parselets: unary `-`, `!`, `~`, `typeof`, `void`, `await`
- Infix parselets: all binary operators with correct precedence table
- Grouping: `(expr)`

### `0.1.0.4` — Parser: Advanced Expressions
- Optional chaining: `obj?.prop`, `obj?.[key]`, `fn?.(args)`
- Nullish coalescing: `a ?? b`
- Ternary: `cond ? a : b`
- `in` operator: `"key" in obj`
- `is` type check: `value is string`

### `0.1.0.5` — Parser: Spread & Rest
- Spread in arrays: `[...arr, 4, 5]`
- Spread in objects: `{ ...obj, key: val }`
- Spread in function calls: `fn(...args)`
- Rest in function params: `fn(a, b, ...rest)`

### `0.1.0.6` — Parser: Destructuring
- Array destructuring: `let [a, b, c] = arr`
- Object destructuring: `let { x, y: renamed } = obj`
- Nested destructuring: `let { a: { b } } = deep`
- Default values in destructuring: `let { x = 10 } = obj`
- Rest in destructuring: `let { a, ...rest } = obj`

### `0.1.0.7` — Parser: Variable Declarations
- `let name = value`, `const name = value`
- Destructuring declarations
- Multiple declarations: `let a = 1, b = 2`
- Uninitialized `let` (type must be inferred or annotated)

### `0.1.0.8` — Parser: Control Flow
- Indentation + `:` defines all blocks — no `{ }` braces anywhere
- `if cond:` / `else if cond:` / `else:` (no parentheses required)
- Inline single-statement form: `if not user: send 404 "Not found"`
- `while cond:`, `do: ... while cond`
- `for item in iterable:` (for-in)
- `for key, value in map:` (for-in with destructuring)
- `not`, `and`, `or` as keyword aliases for `!`, `&&`, `||`
- `break`, `continue`, labeled `break label`

### `0.1.0.9` — Parser: Function Declarations
- `fn name(params) -> ReturnType:` with indented body
- Arrow (lambda): `fn(x) => x + 1` (single expression, no block needed)
- Default parameters: `fn greet(name = "World"):`
- Async functions: `async fn fetch():`
- Generator functions: `fn* gen(): yield 1`
- `give back value` as English alias for `return value`

### `0.1.1.0` — Parser: Class Declarations
- `class Name extends Base { }`
- `init()` constructor, `this` keyword
- Instance methods, static methods
- Getters/setters: `get prop() { }` / `set prop(v) { }`
- Private fields: `#privateField`

### `0.1.1.1` — Parser: Import & Export
- Named imports: `import { a, b } from "./module"`
- Default import: `import Foo from "./foo"`
- Namespace import: `import * as utils from "./utils"`
- Named/default export, re-export
- Dynamic import: `await import("./lazy")`

### `0.1.1.2` — Parser: Pattern Matching
- `match expr { case pat => expr, ... }`
- Literal, identifier, wildcard `_`, guard `case x if x > 0`
- Array patterns: `case [a, b, ...rest]`
- Object patterns: `case { name, age }`
- Enum variant patterns: `case Some(x)`, `case None`

### `0.1.1.3` — Parser: Error Handling Syntax
- `try { } catch (e) { } finally { }`
- Typed catch: `catch (e: NetworkError) { }`
- `throw expression`
- `?` propagation operator: `let val = risky()?`
- `Result<T, E>` and `Option<T>` as built-in parser constructs

### `0.1.1.4` — Parser: Type Annotations
- Inline: `let x: int = 5`, function: `fn(int): bool`
- Array: `int[]`, Object: `{ name: string }`
- Union: `int | string`, Optional: `int?`
- Generics: `<T>`, `<T: Constraint>`
- `type` alias: `type UserId = int`

### `0.1.1.5` — Parser: Enums
- Basic: `enum Color { Red, Green, Blue }`
- With values: `enum Status { Active = 1 }`
- Algebraic: `enum Result<T, E> { Ok(T), Err(E) }`
- Enum methods block

### `0.1.1.6` — Parser: Decorators & Annotations
- `@decorator` and `@decorator(args)` before class, function, method
- Stacked decorators
- Reserved names: `@ai`, `@route`, `@auth`, `@validate`, `@memo`, `@deprecated`

### `0.1.1.7` — Parser: Misc Syntax
- Tagged template literals: `` sql`SELECT {table}` ``
- Pipeline operator: `value |> fn`
- Range: `1..10` (exclusive), `1..=10` (inclusive)
- `with` context manager: `with resource as r { }`
- Block expressions: `{ let x = 1; x + 1 }` as value

### `0.1.1.8` — Parser: Error Recovery
- Synchronize on `;`, `}`, `fn`, `class`, `let`, `const` after an error
- Report all errors in one pass
- Parser error with `hint`: "Did you mean X?"

### `0.1.1.9` — Parser: Test Suite
- 200+ parser tests covering all syntax forms
- Round-trip: parse → print AST → re-parse → compare
- Fuzz: random token sequences must never crash

---

## MILESTONE 0.2 — Core Interpreter

### `0.2.0.1` — Interpreter Skeleton & Value Types
- `Value` sealed class: `IntVal`, `FloatVal`, `StringVal`, `BoolVal`, `NullVal`
- `Interpreter` class with `eval(node)` dispatch
- `Environment`: `get`, `set`, `define`, parent chain
- Global scope with built-in identifiers

### `0.2.0.2` — Arithmetic, Logic, Coercion
- All arithmetic including `**` (power), integer vs float division
- Comparison returning `BoolVal`
- Short-circuit `&&`, `||`; nullish `??`; unary `-`, `+`, `!`, `~`
- `typeof val` → `"string"`, `"int"`, etc.

### `0.2.0.3` — Control Flow Execution
- `if/else if/else` with proper scoping
- `while`, `do-while`, C-style `for`
- `for item in iterable`, `for (k, v) in map`
- `break`/`continue` via Python exceptions, labeled break

### `0.2.0.4` — Functions & Closures
- `FunctionValue` captures declaring environment
- Parameter binding: defaults, rest args
- `return` via exception, recursion, call stack depth limit
- First-class: assign, pass, return functions

### `0.2.0.5` — Arrays (Full)
- Index access, negative indexing, slices
- Mutation: push, pop, splice
- Spread `[...a, ...b]`, destructuring assignment
- Iterator protocol over arrays

### `0.2.0.6` — Maps / Objects (Full)
- Dot + bracket access, mutation, delete
- Spread `{ ...a, key: val }`, destructuring
- Computed keys `{ [varName]: value }`, shorthand `{ x, y }`

### `0.2.0.7` — Iterators & Generators
- `Symbol.iterator` protocol; `for-of` over any iterable
- Generator functions: `fn* gen() { yield val }`
- `yield*` delegation; `.next()`, `.return()`, `.throw()`

### `0.2.0.8` — Pattern Matching Execution
- Tree-walk pattern matcher against values
- Guard evaluation, capture binding into scope
- Exhaustiveness warning (non-enforced at this stage)

### `0.2.0.9` — Error Handling Execution
- `try/catch/finally` execution
- `throw` any value; built-in error types hierarchy
- `Result` and `Option` enum built-ins
- `?` operator desugars to early-return on `Err`/`None`

### `0.2.1.0` — Classes (OOP)
- `ClassValue` with method table
- `new Foo(args)` calls `init()`, returns instance
- `this` binding, prototype method lookup, `super`, `instanceof`
- Static methods and fields

### `0.2.1.1` — Operator Overloading
- `__add__`, `__sub__`, `__mul__`, `__div__`, `__mod__` on classes
- `__eq__`, `__lt__`, `__gt__`, `__str__`, `__repr__`
- `__iter__`, `__len__`, `__get__`, `__set__`

### `0.2.1.2` — Symbols & Proxy
- `Symbol(description)` — unique opaque value
- Well-known: `Symbol.iterator`, `Symbol.toPrimitive`
- `Proxy(target, handler)` — intercept get/set/has/delete
- `Reflect.*` methods

### `0.2.1.3` — Async / Await Execution
- `AsyncFunctionValue` returning `Future`
- `await future` via Python asyncio
- `Promise.all`, `Promise.race`, `Promise.allSettled`
- Top-level `await`

### `0.2.1.4` — Module System Execution
- Load and cache module files on first `import`
- Circular dependency detection (error)
- Module scope isolation; live export bindings
- Dynamic `import()` returns `Promise<Module>`

---

## MILESTONE 0.3 — Advanced Language Features

### `0.3.0.1` — Enums (Full Execution)
- Plain enums as frozen constants, algebraic enums as sealed class hierarchy
- Enum methods, pattern matching on variants

### `0.3.0.2` — Decorators (Execution)
- Class, method, parameter decorators
- Decorator = function applied at definition time
- Composition applied bottom-up

### `0.3.0.3` — Computed Properties & Accessors
- Getter/setter execution, lazy properties

### `0.3.0.4` — Tagged Template Literals
- `` sql`SELECT {table}` `` passes template to `sql` function
- `html`, `css`, `i18n` built-in tags with escaping

### `0.3.0.5` — Range Expressions
- `1..10` exclusive, `1..=10` inclusive
- `Range` type with `.map()`, `.filter()`, `.collect()`
- Range in `for` loops

### `0.3.0.6` — Pipeline Operator
- `value |> fn` passes value as first argument
- `value |> fn(a, ?, b)` — `?` placeholder
- Chainable: `data |> filter(?) |> map(?)`

### `0.3.0.7` — Immutability & Freeze
- `freeze(obj)` deep-freeze, throws on mutation
- `readonly` modifier on type properties
- `Immutable<T>` type wrapper

### `0.3.0.8` — Weak References & Collections
- `WeakRef(obj)`, `WeakMap`, `WeakSet`

### `0.3.0.9` — Metaprogramming
- `Reflect.ownKeys(obj)`, `Reflect.defineProperty()`
- `Object.keys()`, `Object.values()`, `Object.entries()`, `Object.assign()`
- `Object.freeze()`, `Object.seal()`, `Object.create(proto)`

---

## MILESTONE 0.4 — Type System

### `0.4.0.1` — Type Checker Architecture
- Multi-pass: parse → type-check → interpret
- `TypeEnv` parallel to runtime `Environment`
- Error accumulation (all type errors in one pass)

### `0.4.0.2` — Primitive Type Checking
- Literal type inference, arithmetic type rules
- String + any = string; comparisons always return bool
- Assignment compatibility checking

### `0.4.0.3` — Type Inference: Variables & Expressions
- `let x = 5` → `x: int`; infer from complex expressions
- `if`-branch unification (must agree or become union)

### `0.4.0.4` — Type Inference: Functions
- Infer return type from all `return` statements
- Infer param types from usage; recursive functions require annotation

### `0.4.0.5` — Union & Intersection Types
- `string | int`; discriminated unions
- `A & B` intersection for interface merging
- Type narrowing inside `if (typeof x === "string")`

### `0.4.0.6` — Optional & Nullable Types
- `T?` = `T | null`; non-null assertion `x!`
- Optional chaining returns `T?`
- Nullish coalescing widens to `T`

### `0.4.0.7` — Structural Typing & Interfaces
- Interface = shape description; structural compatibility
- `extends` for interface inheritance
- `readonly` properties, index signatures `[key: string]: int`

### `0.4.0.8` — Generic Types
- Generic functions, classes, interfaces
- Constraints: `<T: Numeric>`, multiple `<T: Comparable & Hashable>`
- Default type params: `class Map<K = string, V = any>`

### `0.4.0.9` — Advanced Generics
- Conditional types: `T extends string ? "yes" : "no"`
- Mapped types: `{ [K in keyof T]: T[K]? }`
- Template literal types: `` type E = `on${string}` ``
- `infer` in conditional types

### `0.4.1.0` — Built-in Utility Types
- `Partial<T>`, `Required<T>`, `Readonly<T>`
- `Pick<T,K>`, `Omit<T,K>`, `Record<K,V>`
- `Exclude<T,U>`, `Extract<T,U>`, `NonNullable<T>`
- `ReturnType<F>`, `Parameters<F>`, `InstanceType<C>`

### `0.4.1.1` — Type Guards & Narrowing
- `is` predicates: `fn isString(x: any): x is string`
- `typeof`, `instanceof`, truthiness, assignment narrowing
- Control-flow analysis: dead code detection

### `0.4.1.2` — Tuple Types
- Fixed-length typed: `[string, int, bool]`
- Named tuples, optional elements, rest tuples
- Destructuring with tuple types

### `0.4.1.3` — Opaque & Newtype
- `opaque type Password = string` — cannot mix with plain string
- `newtype Email(string)` — wrapper with same runtime representation
- Nominal typing opt-in

### `0.4.1.4` — Enum Type Checking
- Exhaustiveness check in `match` on enums
- Enum variant type narrowing in `case` branches

### `0.4.1.5` — Type Error Diagnostics
- Rich messages: "Expected `string`, got `int`"
- "Did you forget to handle `null`?"
- Error codes `NV-T001`; `// @ts-ignore` escape hatch

---

## MILESTONE 0.5 — Web: HTML, CSS & Components

### `0.5.0.1` — HTML Element Primitives
- All HTML5 elements as built-in functions: `div(attrs, ...children)`
- Void elements: `img`, `input`, `br`, `hr`
- Type-checked attributes against HTML spec
- `dangerouslySetInnerHTML` escape hatch

### `0.5.0.2` — HTML Document & Meta
- `page` block → full HTML5 document
- Meta helpers: charset, viewport, description, robots
- Open Graph + Twitter Card tags
- Favicon, canonical URL

### `0.5.0.3` — HTML Semantic & Accessibility
- All semantic HTML5: `header`, `footer`, `nav`, `main`, `article`, `aside`
- ARIA attributes: `role`, `aria-label`, `aria-hidden`, `aria-live`
- `tabindex`, `accesskey` support

### `0.5.0.4` — CSS: Style Block Syntax
- `style { }` block inside `page` or `component`
- camelCase → kebab-case conversion
- Scoped styles with auto-hashed class names
- Pseudo-classes `:hover`, `:focus`; pseudo-elements `::before`

### `0.5.0.5` — CSS: Variables & Theming
- CSS custom properties: `--primary-color`
- `theme { colors { primary: "#..." } }` object
- Light/dark mode: `@dark { ... }` block
- `theme.extend()` for per-page overrides

### `0.5.0.6` — CSS: Layout Helpers
- Flexbox helper: `flex(direction, justify, align, gap)`
- Grid helper: `grid(cols, rows, gap)`
- Container queries: `@container (min-width: 400px)`
- Responsive: `@mobile`, `@tablet`, `@desktop` blocks

### `0.5.0.7` — CSS: Animations & Transitions
- `@keyframes name { from { ... } to { ... } }`
- `transition(property, duration, easing)`
- Pre-built: `animate.fadeIn`, `animate.slideUp`, `animate.bounce`
- `will-change` hints

### `0.5.0.8` — CSS: Typography & Reset
- Font loading: `@font "Inter" from "..."`
- Font stack presets: `font.sans`, `font.serif`, `font.mono`
- Fluid typography: `clamp(1rem, 2.5vw, 2rem)`
- Modern CSS reset built-in: `@reset modern`

### `0.5.0.9` — Component: Declaration & Props
- `component Name(props: PropsType) { return element }`
- Props type inference, default props `props.count ?? 0`
- `children` prop: `props.children: Element[]`

### `0.5.1.0` — Component: Composition & JSX-like Syntax
- `<Button label="Click" />` usage syntax
- Children slot: `<Card><p>Hello</p></Card>`
- Named slots: `<Layout header={<Nav/>} footer={<Footer/>}>`
- Conditional: `{flag && <Component/>}`
- List: `{items.map(item => <Row key={item.id} item={item}/>)}`

### `0.5.1.1` — Component: Lifecycle
- `onMount(fn)`, `onUnmount(fn)`, `onUpdate(fn)`
- Server lifecycle: `onRequest(fn)` before SSR
- `async component Page() { }` — async components

### `0.5.1.2` — Component: Slots & Portals
- Named slots with fallbacks
- `portal(target, element)` — render outside component tree
- `forwardRef` — pass ref through component boundary

### `0.5.1.3` — Built-in Layout Components
- `<Stack>`, `<Cluster>`, `<Center>`, `<Sidebar>`
- `<Grid cols gap>`, `<GridItem colSpan>`
- `<Container maxWidth>`, `<Divider>`
- Responsive props: `direction={{ mobile: "col", desktop: "row" }}`

---

## MILESTONE 0.6 — Reactivity & State

### `0.6.0.1` — Signals (Fine-grained Reactivity)
- `signal(init)` — reactive primitive
- `.get()`, `.set(val)`, `.update(fn)`
- Dependency tracking inside reactive contexts

### `0.6.0.2` — Computed Signals
- `computed(() => a.get() + b.get())` — derived reactive value
- Lazy, memoized, auto-tracked dependencies

### `0.6.0.3` — Effects & Watchers
- `effect(() => { log(count.get()) })` — runs on change
- `watch(signal, (newVal, oldVal) => { })` — explicit watcher
- Cleanup: return fn from effect; `watchEffect` runs immediately

### `0.6.0.4` — Reactive Store
- `store({ count: 0 })` — reactive object
- `batch(() => { })` — group mutations, single re-render
- Immutable update helpers

### `0.6.0.5` — Context & Dependency Injection
- `context<T>(default)` — create context
- `<Provider ctx value>` — provide to subtree
- `useContext(ctx)` — consume nearest value

### `0.6.0.6` — Refs & DOM Access
- `ref<HTMLElement>()` — reactive DOM reference
- `<div ref={myRef}>` — bind on mount
- `ref.current` — underlying element

### `0.6.0.7` — Memoization & Lazy Loading
- `memo(fn, deps)` — cache result until deps change
- `@memo` decorator on component — skip re-render if props unchanged
- `lazy(() => import("./Heavy"))` — lazy component

### `0.6.0.8` — Built-in State Machines
- `machine({ initial, states })` — finite state machine
- Transitions, actions (`entry`, `exit`), guards
- Integrates with signals for reactive state

---

## MILESTONE 0.7 — Server & Routing

### `0.7.0.1` — HTTP Server Bootstrap
- `server.listen(port, cb)`, `server.close()`
- HTTPS: `server.https({ cert, key })`
- HTTP/2: `server.listen({ http2: true })`
- Graceful shutdown with connection draining

### `0.7.0.2` — Request Object (Full)
- `method`, `url`, `path`, `query` (parsed map)
- `headers`, `body` (raw + parsed JSON/form)
- `params` (route params), `cookies`, `session`
- `ip`, `hostname`, `protocol`, `accepts(type)`, `is(type)`

### `0.7.0.3` — Response Object (Full)
- `status(code)`, `send(body)`, `json(data)`, `html(str)`, `text(str)`
- `redirect(url, code?)`, `setHeader()`, `getHeader()`
- `cookie()`, `clearCookie()`, `download()`, `sendFile()`
- `stream(readable)` — streaming response; `end()`

### `0.7.0.4` — Router (Core)
- `router.get/post/put/patch/delete/all(path, ...handlers)`
- `router.use(path?, middleware)` — mount middleware
- Route groups with shared prefix and middleware
- Sub-router mounting: `router.group("/api/v1", apiRouter)`

### `0.7.0.5` — Route Path Matching
- Static, named params `:id`, optional `:id?`, wildcard `*`
- Regex segments `/items/:id(\\d+)`
- Multiple params `/users/:userId/posts/:postId`

### `0.7.0.6` — Middleware Pipeline
- Signature: `fn(req, res, next)`; `next(error)` triggers error handler
- Error middleware: `fn(err, req, res, next)`
- Global and route-level middleware

### `0.7.0.7` — Built-in Middleware
- `cors(options)`, `json()`, `urlencoded()`, `multipart()`
- `compress()`, `logger(format)`, `timeout(ms)`, `rateLimit(opts)`
- `static(dir)` — serve static files with ETag + cache headers

### `0.7.0.8` — File Uploads
- `req.files` — parsed multipart; file object: `{ name, size, type, stream }`
- Size limit, type whitelist validation
- Storage adapters: `disk(dest)`, `memory()`, `s3(config)`

### `0.7.0.9` — Cookies & Sessions
- `res.cookie(name, val, { httpOnly, secure, sameSite, maxAge })`
- `req.cookies` — parsed cookie map; signed cookies
- Session middleware: `middleware.session({ secret, store })`
- Session stores: `MemoryStore`, `RedisStore`, `DatabaseStore`

### `0.7.1.0` — WebSockets
- `ws.upgrade(req)` — upgrade HTTP to WebSocket
- `socket.send()`, `socket.close()`, `socket.ping()`
- Room/namespace: `io.room("chat").broadcast(msg)`
- Reconnection + heartbeat built-in

### `0.7.1.1` — Server-Sent Events (SSE)
- `res.sse()` — start SSE stream
- `res.sendEvent({ event, data, id, retry })`
- Client-side `EventSource` helper built-in

### `0.7.1.2` — GraphQL Support
- `graphql.schema(typeDefs, resolvers)` + `router.graphql("/graphql", schema)`
- DataLoader pattern for N+1 prevention
- Subscriptions over WebSocket

### `0.7.1.3` — gRPC Support (Experimental)
- `.proto` file import → typed Nova stubs
- Server: `grpc.listen(port, serviceImpl)`; Client: `grpc.connect(url)`
- Streaming RPCs (unary, server-stream, client-stream, bidirectional)

---

## MILESTONE 0.8 — Database & Storage

### `0.8.0.1` — Database Connection Abstraction
- `db.connect(driver, url)` — unified API
- Drivers: `postgres`, `mysql`, `sqlite`, `mongodb`
- Connection pooling: min/max, idle timeout, health checks

### `0.8.0.2` — Query Builder: Reads
- `.from("users").select("id","name")`
- `.where()`, `.join()`, `.orderBy()`, `.limit()`, `.offset()`
- `.count()`, `.sum()`, `.avg()`, `.min()`, `.max()`
- Parameterized queries (SQL-injection safe)

### `0.8.0.3` — Query Builder: Mutations
- `.insert()`, `.insertMany()`, `.update()`, `.delete()`, `.upsert()`
- `.returning("id")` clause

### `0.8.0.4` — ORM: Model Definition
- `model User { id: int @pk @autoincrement, name: string }`
- Field decorators: `@pk`, `@unique`, `@default`, `@nullable`, `@index`
- Timestamps: `@createdAt`, `@updatedAt`; soft delete: `@deletedAt`

### `0.8.0.5` — ORM: Relations
- `@hasOne`, `@hasMany`, `@belongsTo`, `@manyToMany(through: "...")` 
- Eager loading: `User.find().include("posts")`
- Lazy loading via accessor property

### `0.8.0.6` — ORM: Active Record Queries
- `find`, `findBy`, `findOrFail`, `all`, `where`, `create`, `save`, `destroy`
- Named scopes: `User.scope("active", q => q.where({ active: true }))`

### `0.8.0.7` — Database Migrations
- `migration.create("name", fn(schema) { ... })` with schema builder
- Column types, `addColumn`, `dropColumn`, `renameColumn`
- `migration.run()`, `.rollback()`, `.status()`
- Seed files: `seed.run(fn(db) { ... })`

### `0.8.0.8` — Transactions & Savepoints
- `db.transaction(async fn(trx) { ... })` — auto-rollback on error
- `trx.commit()`, `trx.rollback()`, savepoints
- Isolation levels

### `0.8.0.9` — Caching Layer
- `cache.get/set/delete/flush(key, val, ttl?)`
- Adapters: `MemoryCache`, `RedisCache`, `FileCache`
- `cache.remember(key, ttl, fn)` — fetch-or-compute
- Tag-based invalidation: `cache.tag("users").flush()`

### `0.8.1.0` — Key-Value & Document Stores
- `kv.get/set/scan` — simple K-V interface
- `docs.collection("name").insert/find/update/delete`
- Full-text search index: `docs.index("content")`

---

## MILESTONE 0.9 — Security & Authentication

### `0.9.0.1` — Input Validation
- `validate(schema, data)` — validate against schema
- Schema DSL: `v.string().email().maxLength(255)`
- `.min()`, `.max()`, `.pattern()`, `.enum()`, `.url()`, `.uuid()`
- Nested + array schemas; coercion: `v.int().coerce()`

### `0.9.0.2` — Input Sanitization
- `sanitize.html(str)` — strip dangerous HTML (XSS prevention)
- `sanitize.sql(str)`, `sanitize.path(str)`, `sanitize.email(str)`
- `sanitize.strip(str)` — remove all HTML tags

### `0.9.0.3` — CSRF Protection
- `middleware.csrf()` — CSRF token per session
- Auto token injection into forms: `<form csrf />`
- Double-submit cookie pattern; `req.csrfToken()` accessor

### `0.9.0.4` — Security Headers
- `middleware.helmet()`:
  - `Content-Security-Policy`, `X-Frame-Options: DENY`
  - `X-Content-Type-Options: nosniff`
  - `Strict-Transport-Security`, `Referrer-Policy`, `Permissions-Policy`

### `0.9.0.5` — Rate Limiting
- `middleware.rateLimit({ windowMs, max })`
- Per-IP, per-user, per-route limits
- `RateLimitInfo` on `req`: `.remaining`, `.resetTime`
- Stores: `MemoryStore`, `RedisStore`

### `0.9.0.6` — Authentication: JWT
- `jwt.sign(payload, secret, opts)`, `jwt.verify()`, `jwt.decode()`
- `middleware.jwtAuth(secret)` — auto-verify `Authorization: Bearer`
- Refresh token rotation pattern

### `0.9.0.7` — Authentication: Sessions & Passwords
- `password.hash(raw)` — bcrypt/argon2; `password.verify(raw, hash)`
- `password.strength(raw)` → score + suggestions

### `0.9.0.8` — Authentication: OAuth2 / OIDC
- `oauth.provider("google" | "github" | "discord", { clientId, clientSecret })`
- `router.get("/auth/:provider", oauth.redirect())`
- Callback handler, PKCE support for public clients

### `0.9.0.9` — Authorization (RBAC/ABAC)
- `policy.define("edit-post", (user, post) => ...)`
- `middleware.authorize("edit-post", resourceFn)`
- `user.hasRole("admin")`, `user.can("edit-post")`

### `0.9.1.0` — Cryptography Module
- `crypto.hash`, `crypto.hmac`, `crypto.randomBytes`, `crypto.uuid`
- `crypto.encrypt`/`decrypt` (AES-GCM)
- `crypto.sign`/`verify` (RSA/ECDSA)
- `crypto.argon2`, `crypto.bcrypt`

---

## MILESTONE 0.10 — Standard Library

### `0.10.0.1` — String Module (Full)
- Case: `.upper()`, `.lower()`, `.title()`, `.capitalize()`
- Trim: `.trim()`, `.trimStart()`, `.trimEnd()`
- Split/join, replace/replaceAll, startsWith/endsWith/includes/indexOf
- Pad, repeat, slice, normalize (Unicode)
- `.codePointAt()`, `String.fromCodePoint()`, `.match()`, `.matchAll()`

### `0.10.0.2` — Array Module (Full)
- Transform: `.map()`, `.filter()`, `.reduce()`, `.flatMap()`
- Search: `.find()`, `.findIndex()`, `.findLast()`, `.some()`, `.every()`, `.includes()`
- Mutate: `.sort()`, `.reverse()`, `.splice()`, `.fill()`, `.copyWithin()`
- Access: `.at()`, `.with()`, `.slice()`, `.concat()`
- Iterate: `.entries()`, `.keys()`, `.values()`
- Extras: `.unique()`, `.groupBy()`, `.partition()`, `.zip()`
- Numeric shortcuts: `.sum()`, `.average()`, `.min()`, `.max()`

### `0.10.0.3` — Map & Set Modules
- `Map`: full CRUD + `.entries()`, `.keys()`, `.values()`, `.forEach()`
- `Set`: `.add()`, `.has()`, `.delete()` + `.union()`, `.intersection()`, `.difference()`
- `WeakMap`, `WeakSet`

### `0.10.0.4` — Math Module (Full)
- Constants: `PI`, `E`, `SQRT2`, `INFINITY`, `NaN`
- Rounding, power, log, trig, hyperbolic functions
- `.random()`, `.randomInt(min,max)`, `.clamp()`, `.lerp()`
- `.gcd()`, `.lcm()`, `.factorial()`; `BigInt` support

### `0.10.0.5` — Date/Time Module (Full)
- Constructors, getters, `toISOString()`, `toLocaleString()`, `format(pattern)`
- Arithmetic: `.add(duration)`, `.subtract()`, `.diff(other, unit)`
- `.startOf()`, `.endOf()`, `.isBefore()`, `.isAfter()`
- Timezone via `Intl.DateTimeFormat`; `Duration` type; `.fromNow()` relative

### `0.10.0.6` — HTTP Client Module
- `fetch(url, opts)` — Fetch API compatible
- `http.create({ baseURL, timeout, headers })`
- Request/response interceptors
- `.retry(n, delay)`, `.abort()`, streaming response
- Progress events for uploads/downloads

### `0.10.0.7` — File System Module
- `fs.read/write/append`, `fs.readBytes/writeBytes`
- `fs.exists/stat/mkdir/rmdir/delete/move/copy`
- `fs.list(dir)`, `fs.glob(pattern)`, `fs.watch(path, fn)`
- `path.join/resolve/dirname/basename/ext`

### `0.10.0.8` — Stream Module
- `ReadableStream`, `WritableStream`, `TransformStream`
- `.pipe()`, `.pipeTo()`, `.from(array)`, `.fromFile(path)`
- `.map()`, `.filter()`, `.chunk()`, `.collect()`, `.text()`

### `0.10.0.9` — Serialization: JSON, YAML, TOML, CSV
- `JSON.parse/stringify` with reviver/replacer
- `JSON.parseStream(readable)` — NDJSON streaming parse
- `YAML.parse/stringify`, `TOML.parse/stringify`, `CSV.parse/stringify`

### `0.10.1.0` — URL Module
- `URL.parse(str)` → `{ protocol, host, pathname, search, hash }`
- `URL.resolve(base, relative)`
- `URLSearchParams`: full CRUD + `.toString()`
- `URL.encode()`, `URL.decode()`

### `0.10.1.1` — Process & Environment
- `env.get()`, `env.require()`, `env.all()`, `.env` file loader
- `process.exit()`, `.pid`, `.platform`, `.args`, `.cwd()`, `.chdir()`
- `process.memoryUsage()`, `process.cpuUsage()`

### `0.10.1.2` — Logging Module
- `log.info/warn/error/debug/trace()`
- Structured: `log.info({ userId, action })`
- Formatters: JSON, pretty, compact
- Transports: console, file, HTTP (Loki, Datadog, Papertrail)

### `0.10.1.3` — Queue & Jobs Module
- `queue.add("task", data, { delay, retries, priority })`
- `queue.worker("task", async fn(job) { ... })`
- Retry with exponential backoff
- `cron.schedule("0 9 * * *", fn)` — cron jobs

### `0.10.1.4` — Email Module
- `mail.send({ to, from, subject, html, text, attachments })`
- `mail.template("welcome", { name })` — template files
- Adapters: SMTP, SendGrid, Resend, AWS SES
- Dev preview: `mail.preview(msg)` — opens in browser

### `0.10.1.5` — i18n & Localization
- `i18n.locale("en", { messages })`, `t("key", { vars })`
- Pluralization, number/date/currency formatting per locale
- `<I18nProvider locale="en">` context component

### `0.10.1.6` — Regex Module
- Literal `/pattern/flags`, `re.match/matchAll/test/replace/split`
- Named groups `(?<n>...)`, regex composition helpers

---

## MILESTONE 0.11 — AI Integration (Minimax)

### `0.11.0.1` — Minimax API Client
- Async HTTP with retry, rate-limit backoff
- Config: `nova.config.nv`; streaming via SSE
- Request/response logging in debug mode

### `0.11.0.2` — `@ai` Annotation (Compile-time Code Gen)
- `@ai("Generate a login form")` → calls Minimax, injects AST nodes
- `.ai_cache/` by prompt hash; `--no-ai-cache` flag

### `0.11.0.3` — AI Error Explanation
- `nova run --explain` — on error, sends to Minimax for explanation
- Returns: problem, cause, fix, code example — color-coded in terminal

### `0.11.0.4` — AI Type Inference Assist
- `// @ai-infer-type` → sends context to Minimax, writes annotation to source

### `0.11.0.5` — AI Code Generation CLI
- `nova ai gen "description"` → generates `.nv` file
- `nova ai refine file.nv "instruction"` → refactors in-place
- `nova ai explain file.nv` → plain-English explanation

### `0.11.0.6` — AI Component & Scaffold
- `nova ai scaffold component "Dashboard with charts"`
- `nova ai scaffold page "..."`, `nova ai scaffold model "..."`
- Iterative refinement loop

### `0.11.0.7` — AI Test Generator
- `nova ai test file.nv` → generates test file
- Covers edge cases, happy paths, error paths

### `0.11.0.8` — AI Code Review
- `nova ai review file.nv` → security, perf, a11y findings
- Structured: severity, location, description, suggested fix
- `--fix` flag: auto-apply safe fixes

### `0.11.0.9` — `ai` Built-in Object (Runtime)
- `ai.complete(prompt)`, `ai.chat(messages)`, `ai.stream(prompt, onChunk)`
- `ai.embed(text)` — get embedding vector
- `ai.usage()` — token count tracking

### `0.11.1.0` — AI-Powered Validation & Transform
- `@ai.validate("must be a valid US address")` — natural language validation
- `@ai.transform("normalize phone to E.164")` — AI field transform
- Parallel batch execution

---

## MILESTONE 0.12 — Build System & JS Compilation

### `0.12.0.1` — JS Codegen: Expressions & Functions
- Lower all expressions, closures, rest/spread, destructuring
- Optional chain `?.` → safe JS; template literals → JS template strings

### `0.12.0.2` — JS Codegen: Classes & Modules
- Classes → native JS `class`; `import/export` → ES modules
- Enums → frozen objects; decorators → JS stage-3 decorators

### `0.12.0.3` — JS Codegen: Async & Generators
- `async/await` → JS async; generators → JS generators
- `Promise` methods passthrough

### `0.12.0.4` — JS Codegen: Type Erasure
- Strip all type annotations (TypeScript-style)
- Runtime type guards kept in debug mode; `opaque/newtype` → nothing

### `0.12.0.5` — Bundler: Dependency Graph & Tree-shaking
- Resolve all imports to a DAG; detect circular deps
- Remove unused exports from bundle

### `0.12.0.6` — Bundler: Output Formats
- ESM (default), CJS (`--target cjs`), IIFE, UMD
- Chunk splitting: dynamic `import()` → separate chunk
- Shared vendor chunk

### `0.12.0.7` — Bundler: Asset Handling
- Import images → URL or inlined base64
- Import CSS → injected `<style>` tag
- Import JSON → typed object; public directory copy

### `0.12.0.8` — Bundler: Minification
- Whitespace removal, local variable renaming, dead code elimination
- Constant folding: `2 + 3` → `5` at compile time

### `0.12.0.9` — Source Maps
- `.nv.map` linking JS output → `.nv` source
- Inline source maps, stack trace integration

### `0.12.1.0` — Dev Server & HMR
- `nova dev` — dev server with Hot Module Replacement
- File watcher + instant recompile; WebSocket-based HMR client
- Error overlay in browser; port auto-selection

### `0.12.1.1` — Production Build
- `nova build` — optimized build with fingerprinted filenames
- HTML template injection; build size report

### `0.12.1.2` — npm Interop
- `import lodash from "npm:lodash"` — use npm packages
- Auto-install on first run; type stubs for popular packages

---

## MILESTONE 0.13 — Rendering Modes

### `0.13.0.1` — Server-Side Rendering (SSR)
- `renderToString(element)` and `renderToStream(element)`
- Hydration marker injection; `req` context available inside `page`

### `0.13.0.2` — Client-Side Hydration
- `hydrate(element, domNode)` — attach reactivity to SSR HTML
- Signal state serialized from server + restored on client
- `useIsomorphic(fn)` — same code, server + client

### `0.13.0.3` — Static Site Generation (SSG)
- `nova build --ssg` — pre-render all pages at build time
- `getStaticPaths()`, `getStaticProps()` — data fetching at build time

### `0.13.0.4` — Incremental Static Regeneration (ISR)
- `page.revalidate = 60` — re-render every N seconds
- Stale-while-revalidate; on-demand: `cache.invalidate("/path")`

### `0.13.0.5` — Islands Architecture
- Default: server-rendered HTML
- `<Island component={Counter}>` — hydrate only that component
- `client:load`, `client:idle`, `client:visible` strategies

### `0.13.0.6` — Streaming SSR
- `<Suspense fallback={<Spinner/>}>` — suspend components
- Server streams initial HTML, deferred content appended as resolved
- `defer(promise)` marks data as deferrable

### `0.13.0.7` — View Transitions
- `<ViewTransition>` wrapper — CSS View Transitions API
- Named transitions, morphing between pages
- `navigate(url, { transition: "slide" })`

### `0.13.0.8` — Edge Runtime
- `page.runtime = "edge"` → compile for Cloudflare Workers / Vercel Edge
- `EdgeRequest`, `EdgeResponse`; `env.edge()` bindings

---

## MILESTONE 0.14 — Testing Framework

### `0.14.0.1` — Test Runner Core
- `test("name", fn)`, `suite("name", fn)`, lifecycle hooks
- `nova test` runs all `*.test.nv`; `--watch` for continuous testing
- Parallel test execution

### `0.14.0.2` — Assertions
- `expect(val).toBe/toEqual/toBeTruthy/toBeNull/toBeGreaterThan...`
- `.toContain/toMatch/toThrow/toHaveLength/toHaveProperty`
- `.not.*` negation

### `0.14.0.3` — Async Testing
- `test("name", async fn)`
- `expect(promise).resolves.toBe(val)` / `.rejects.toThrow(Error)`
- Test timeout option

### `0.14.0.4` — Mocking & Spying
- `mock.fn(impl?)` — mock function with `.calls` history
- `spy.on(obj, "method")`, `mock.module("./api", { ... })`
- `mock.timer()` — control `Date.now()`, `setTimeout`

### `0.14.0.5` — Snapshot Testing
- `expect(val).toMatchSnapshot()`
- `expect(component).toMatchHTMLSnapshot()`
- `nova test --update-snapshots`

### `0.14.0.6` — Component Testing
- `render(<Button/>)`, `screen.getBy*`, `fireEvent.*`
- `waitFor(() => expect(...))` — async DOM assertion

### `0.14.0.7` — Coverage Reporting
- `nova test --coverage` — line, branch, function, statement
- Threshold enforcement for CI; HTML + LCOV report output

### `0.14.0.8` — Integration Test Helpers
- `testServer()` — in-process server + HTTP client
- `fixture.seed("users", rows)` — DB fixtures
- `testBrowser()` — Playwright integration for E2E

---

## MILESTONE 0.15 — Developer Experience

### `0.15.0.1` — REPL
- `nova repl` — multi-line input, `.help/.exit/.load` commands
- History persisted to `~/.nova_history`; color-coded type output

### `0.15.0.2` — Formatter (`nova fmt`)
- Canonical style; `--check` for CI; `// fmt-off` escape hatch

### `0.15.0.3` — Linter (`nova lint`)
- Unused vars/imports, unreachable code, missing `return`, prefer `const`
- No-`any` rule; a11y lint for HTML components; custom rules via plugin API

### `0.15.0.4` — LSP: Diagnostics & Hover
- Incremental parse + type-check on every keystroke
- Hover shows type + doc comment; `workspace/symbol` search

### `0.15.0.5` — LSP: Completion & Signatures
- Auto-complete identifiers, methods, imports; snippet completions
- Signature help tooltip; auto-insert import on completion

### `0.15.0.6` — LSP: Navigation & Refactoring
- Go-to definition, find references, rename across workspace
- Code actions: quick fix, add import, add type annotation

### `0.15.0.7` — VS Code Extension
- `.tmLanguage` grammar, snippet pack, inlay hints
- Error squiggles via LSP; run/debug launch config
- Published to VS Code Marketplace

### `0.15.0.8` — Config & Environment Management
- `nova.config.nv` — typed project config
- `.env`, `.env.local`, `.env.production` hierarchy
- `env.schema({ PORT: v.int().default(3000) })` — validated env vars

### `0.15.0.9` — Documentation Generator
- `/// Doc comment` with `@param`, `@returns`, `@example`
- `nova docs ./src --out ./docs` → HTML docs site with search

### `0.15.1.0` — Package Manager
- `nova.pkg.nv` manifest; `install/uninstall/update/publish` commands
- Lockfile: `nova.lock`; scoped packages `@org/pkg`

### `0.15.1.1` — Project Scaffolding
- `nova new my-app` — interactive creator
- Templates: `web-app`, `api-server`, `static-site`, `fullstack`, `library`
- Git init + initial commit included

### `0.15.1.2` — Debugging
- `debugger` statement; `nova debug file.nv` starts DAP server
- Source-mapped stack traces; `console.trace/table/group`

---

## MILESTONE 0.16 — Advanced Web Features

### `0.16.0.1` — SEO Module
- `<Head>` component for title, meta, links; `seo.*` helpers
- JSON-LD structured data; sitemap + robots.txt generation

### `0.16.0.2` — PWA Support
- Web App Manifest: `pwa.manifest({ name, icon, themeColor })`
- Service Worker scaffold; offline page; push notifications
- Install prompt: `pwa.onInstallPrompt(fn)`

### `0.16.0.3` — Web Workers
- `worker(fn)` — run in Web Worker; `.postMessage()`, `.onMessage()`
- Comlink-style transparent proxy API; worker pool

### `0.16.0.4` — WebAssembly Interop
- `wasm.load(url)` → typed module; auto-generate Nova type bindings

### `0.16.0.5` — Canvas & WebGL
- `canvas(w, h)` — 2D context; paths, shapes, text, images
- `webgl(canvas)` — WebGL2 context; shader compilation helpers

### `0.16.0.6` — Browser APIs
- Typed `storage.local/session`, `navigator.geolocation/clipboard/share`
- `intersectionObserver`, `resizeObserver`, `mutationObserver`
- `Notification.request()`, `Notification.send()`

### `0.16.0.7` — Accessibility (a11y) Module
- `a11y.announce()`, `a11y.trapFocus()`, `a11y.restoreFocus()`
- `a11y.colorContrast(fg, bg)` → WCAG grade
- `a11y.audit(el)` — runtime a11y check; lint rules

### `0.16.0.8` — i18n Routing
- Locale in URL: `/en/about`, `/fr/about`; auto-redirect
- `hreflang` tags auto-generated; RTL layout: `i18n.dir()`

### `0.16.0.9` — Image Optimization
- `<Image src alt width height/>` — auto WebP/AVIF, responsive srcset
- Lazy loading + blur placeholder
- `image.optimize(path, { width, format, quality })` programmatic API

### `0.16.1.0` — Analytics & Telemetry
- `analytics.event("name", props)`, adapters: GA, Plausible, PostHog
- Server-side: `req.analytics.event()`; `perf.mark/measure()`

### `0.16.1.1` — Error Monitoring
- Sentry-compatible: `monitoring.init({ dsn })`
- Auto capture, breadcrumbs, `monitoring.captureException()`
- Source map upload via `nova monitoring upload-sourcemaps`

### `0.16.1.2` — Feature Flags
- `flags.define("name", { default: false })`, `flags.isEnabled(name, ctx)`
- LaunchDarkly-compatible remote evaluation
- `<FeatureFlag name fallback>` component; A/B testing support

---

## MILESTONE 0.17 — Performance & Optimization

### `0.17.0.1` — Profiler
- `nova profile file.nv` — CPU profiling with flame chart
- `profile.start/stop()`, heap snapshot; performance budget in build

### `0.17.0.2` — Benchmarking
- `bench("name", fn, { iterations })` — micro-benchmark
- `nova bench *.bench.nv` — statistical analysis (mean, p50, p95, p99)
- `--compare main` flag for cross-branch comparison

### `0.17.0.3` — Response Caching & HTTP Cache
- `route.cache({ ttl, key: req => req.url })`
- `res.cacheFor(seconds)` — sets `Cache-Control`; ETag generation
- `res.noCache()`, `res.noStore()`

### `0.17.0.4` — Database Query Optimization
- `db.explain(query)` — query plan output
- N+1 detection warning in dev mode
- Query result caching with cache invalidation hooks

---

## MILESTONE 0.18 — Plugin & Extension System

### `0.18.0.1` — Compiler Plugin API
- `plugin.onParse(ast => ast)`, `plugin.onTypeCheck(types => types)`
- `plugin.onCodegen(ir => ir)` — hook into code generation
- Plugin as `.nv` file or npm package

### `0.18.0.2` — Bundler Plugin API
- `plugin.resolveId(id, importer)` — custom module resolution
- `plugin.load(id)` — custom module loader
- `plugin.transform(code, id)` — transform before bundle (Vite-compatible format)

### `0.18.0.3` — Runtime Plugin API
- `app.use(plugin)` — register server plugin
- Plugin lifecycle: `install(app)`, `uninstall(app)`
- Plugin can add routes, middleware, custom decorators

---

## MILESTONE 0.19 — Spec Freeze & Stabilization

### `0.19.0.1` — Comprehensive Test Suite
- 500+ tests across all modules; fuzz testing (never crash)
- Property-based testing; regression tests for every bug fixed

### `0.19.0.2` — Performance Baseline & Security Audit
- Benchmark vs Node.js for representative workloads
- Review all user-input, file I/O, exec paths; dependency vulnerability scan

### `0.19.0.3` — Documentation (Full)
- Language reference: every syntax form; stdlib API docs
- Guides: Getting Started, Full-stack App, API Server, SSG Blog
- Migration guide from JS/TS

### `0.19.0.4` — Example Projects
- `todo-fullstack`, `blog-ssg`, `api-server`, `realtime-chat`, `ecommerce`
- Each uses a representative mix of language features

### `0.19.0.5` — VS Code Extension v1.0 Polish
- Semantic token highlighting; full LSP integration
- AI-powered inline completions; marketplace release

### `0.19.0.6` — Language Specification Freeze
- `SPEC.md` — formal EBNF grammar, type system rules, execution semantics
- Open RFC process for future changes
- **No new Python-phase syntax after this point**

---

---

## PHASE 1 — Rust Rewrite

> Starting at `v1.0.0.0`, Nova is reimplemented in Rust for production-grade
> performance, WASM compilation, and native binary targets.
> Language spec does NOT change — only the implementation.

---

## MILESTONE 1.0 — Rust Foundation

### `1.0.0.1` — Cargo Workspace Setup
- Crates: `nova-lexer`, `nova-parser`, `nova-ast`, `nova-types`, `nova-interpreter`,
  `nova-codegen-js`, `nova-bundler`, `nova-lsp`, `nova-cli`, `nova-stdlib`
- CI: `cargo test`, `cargo clippy --deny warnings`, `cargo fmt --check`
- Benchmark harness with `criterion`

### `1.0.0.2` — Lexer (`logos` crate)
- `Token` enum with `#[logos]` derive; all token types
- Span tracking: `(start, end)` byte offsets
- Target: 100MB/s+ throughput

### `1.0.0.3` — AST (Rust)
- Node enums: `Expr`, `Stmt`, `TypeExpr`, `Pattern`
- `Box<Expr>` for recursion; `Span` on every node
- `#[derive(Debug, Clone, PartialEq)]` on all nodes

### `1.0.0.4` — Parser (`chumsky` crate)
- Full Pratt parser; all statement/expression forms
- Error recovery via `chumsky recover_with`
- Target: parse 1MB source in < 50ms

### `1.0.0.5` — Type Checker (Rust)
- `TypeEnv` with `HashMap<NodeId, Type>`
- All type rules from 0.4 milestone ported
- Salsa-style incremental re-checking; zero panics on valid programs

### `1.0.0.6` — Interpreter (Rust)
- `Value` enum with `Arc<Mutex<>>` for shared objects
- `Environment` with `Rc<RefCell<Env>>` chain
- All runtime semantics from 0.2 ported

### `1.0.0.7` — JS Codegen & Bundler (Rust)
- `JsEmitter` with `String` buffer; module graph via `petgraph`
- Tree-shaking, chunk splitting ported to Rust

### `1.0.0.8` — Parity Test Pass
- All 500+ Python-era tests pass on Rust implementation
- Must be ≥ 20× faster than Python on all benchmarks

---

## MILESTONE 1.1 — Incremental Compilation

### `1.1.0.1` — Salsa Incremental Framework
- Every compiler pass as a `salsa` query
- File change → only affected queries re-run

### `1.1.0.2` — Persistent Build Cache
- `.nv-cache/` using `sled` embedded DB, keyed by file hash + compiler version
- `nova build --cold` for full rebuild

### `1.1.0.3` — Parallel Compilation
- `rayon` for parallel file processing
- Type check + JS codegen per-module in parallel

---

## MILESTONE 1.2 — WebAssembly Target

### `1.2.0.1` — WASM Codegen Skeleton
- `nova-codegen-wasm` crate; `wasm-bindgen` for JS interop
- `nova compile file.nv --target wasm` → `.wasm` + JS glue

### `1.2.0.2` — WASM: Type Mapping
- Nova types → WASM types (i32, f64, externref)
- Strings via UTF-8 `Uint8Array`; objects via `externref`

### `1.2.0.3` — WASM: Browser Runtime
- DOM bindings via `web-sys`; event handlers from WASM
- Signals/reactivity loop in WASM; `window`, `document`, `console`

### `1.2.0.4` — WASM: Optimization
- `wasm-opt -O3` post-processing; lazy route-based module loading
- Target: < 50KB gzipped base bundle

### `1.2.0.5` — WASM: SIMD & Threads
- SIMD instructions for math-heavy operations
- `SharedArrayBuffer` + `Atomics` for WASM threads

---

## MILESTONE 1.3 — Bytecode VM

### `1.3.0.1` — Intermediate Representation (IR)
- `NovaIR` — typed stack-based bytecode
- AST → IR lowering; IR dump: `nova compile --emit-ir`

### `1.3.0.2` — Bytecode Compiler
- IR → binary `.nvc` format with constant pool, function table, debug info
- `nova compile file.nv --target bytecode`

### `1.3.0.3` — Bytecode VM (Register-based)
- 256 virtual registers per frame
- Computed goto dispatch; inline caching for property + method access
- Target: within 5× of V8 for hot loops

### `1.3.0.4` — JIT Compilation (Experimental)
- Hot-function detection via invocation counter
- Cranelift JIT for hot functions; deoptimization fallback
- `--jit` flag to enable

---

## MILESTONE 1.4 — Native Binary Target

### `1.4.0.1` — LLVM Backend (`inkwell`)
- `NovaIR` → LLVM IR; `-O2` pass pipeline
- `nova compile file.nv --target native` → standalone binary

### `1.4.0.2` — Native Runtime
- Mark-and-sweep GC (generational planned)
- Green threads / async runtime; native stdlib for fs, net, crypto

### `1.4.0.3` — Cross-Compilation
- `--target x86_64-linux`, `aarch64-macos`, `wasm32`
- `--static` for fully self-contained binary

---

## MILESTONE 1.5 — Full LSP Server (Rust)

### `1.5.0.1` — LSP Core (`tower-lsp`)
- Incremental parse + type-check on every keystroke
- Workspace-wide symbol table; AI-augmented completions

### `1.5.0.2` — Semantic Tokens
- Type-colored identifiers; mutable vs immutable binding differentiation

### `1.5.0.3` — Refactoring Operations
- Extract function/variable, inline variable, convert let→const
- Auto-import; rename across workspace with preview

### `1.5.0.4` — Debug Adapter Protocol (DAP)
- Breakpoints, step-over/into/out, variable inspection
- Conditional breakpoints, logpoints; VS Code debugger integration

---

## MILESTONE 1.6 — AI Layer v2 (Rust)

### `1.6.0.1` — Async Minimax Client (Rust)
- `tokio` + `reqwest`; streaming via SSE
- Connection pooling, retry with jitter, circuit breaker

### `1.6.0.2` — AI Cache (`sled`)
- Key: `SHA256(prompt + model + version)`; TTL expiry, LRU eviction

### `1.6.0.3` — AI-Powered LSP Completions
- Minimax-augmented completion items; context = current file + types
- Ghost text streaming completions

### `1.6.0.4` — AI Code Actions
- "Fix with AI", "Generate test", "Explain" code actions
- Inline chat: `// @ai: make this async` → AI refactors inline

### `1.6.0.5` — AI Fine-tuning (Self-hosted)
- `nova ai finetune ./examples` — fine-tune on your codebase
- Export GGUF for local inference (Ollama-compatible)

---

## MILESTONE 1.7 — Package Registry & Ecosystem

### `1.7.0.1` — Central Registry (API)
- Search, publish, download, deprecate; semantic version resolution + lockfile

### `1.7.0.2` — Registry: Security
- Automated vulnerability scan; SLSA build provenance; verified publisher badges

### `1.7.0.3` — Registry: Web UI
- Search with filters; package page: README, changelog, API docs, versions
- Built entirely in Nova (dogfooding)

### `1.7.0.4` — Official First-Party Packages
- `@nova/ui` — component library (buttons, forms, modals, tables)
- `@nova/auth` — auth helpers (JWT, OAuth, sessions)
- `@nova/db` — database ORM integrations
- `@nova/icons` — icon library; `@nova/charts` — data visualization
- `@nova/markdown` — Markdown parser + renderer
- `@nova/testing` — extra testing utilities

---

## MILESTONE 1.8 — v1 Stable Release

### `1.8.0.1` — Final Security Audit
- External pentest; 100M+ fuzz inputs (zero crashes); all CVEs resolved

### `1.8.0.2` — Performance Targets
- Compiler: < 100ms for 10,000-line project
- Server: > 100,000 req/s on simple JSON (single core)
- Bundle: < 10KB gzipped for hello-world page

### `1.8.0.3` — Official Website
- `nova-lang.dev` — built in Nova
- Interactive playground (WASM); full language reference + API docs

### `1.8.0.4` — `v1.0.0.0-stable` Tag
- Stable ABI for native binary; backward-compat guarantee for `1.x`
- Full changelog from `0.0.0.1`; contributor credits; `CONTRIBUTING.md`

---

## Full Timeline Summary

```
Phase 0 — Python Implementation
────────────────────────────────────────────────────
0.0.x.x   Foundation, Tokenizer                         (9 versions)
0.1.x.x   Parser, AST — all syntax forms               (19 versions)
0.2.x.x   Core interpreter, values, closures, async     (14 versions)
0.3.x.x   Advanced features: enums, decorators, meta    (9 versions)
0.4.x.x   Type system: inference, generics, utilities   (15 versions)
0.5.x.x   HTML, CSS, components, layout                 (14 versions)
0.6.x.x   Reactivity: signals, store, context, FSM      (8 versions)
0.7.x.x   HTTP server, routing, WS, SSE, GraphQL, gRPC (13 versions)
0.8.x.x   Database, ORM, migrations, cache, K-V         (10 versions)
0.9.x.x   Security: validation, CSRF, JWT, OAuth, crypto(10 versions)
0.10.x.x  Standard library (string→regex, 16 modules)   (16 versions)
0.11.x.x  AI integration: Minimax, @ai, review, runtime (10 versions)
0.12.x.x  Build system, JS codegen, bundler, dev server (12 versions)
0.13.x.x  SSR, SSG, ISR, Islands, Streaming, Edge       (8 versions)
0.14.x.x  Testing framework: runner, mocks, coverage    (8 versions)
0.15.x.x  DX: REPL, fmt, lint, LSP, VS Code, pkg mgr   (12 versions)
0.16.x.x  SEO, PWA, workers, a11y, analytics, flags     (12 versions)
0.17.x.x  Profiler, benchmarks, caching, DB optimizer   (4 versions)
0.18.x.x  Plugin & extension system                     (3 versions)
0.19.x.x  Stabilization, test suite, spec freeze        (6 versions)

  ✦ v1.0.0.0: RUST REWRITE BEGINS ✦

Phase 1 — Rust Implementation
────────────────────────────────────────────────────
1.0.x.x   Rust foundation: lexer, parser, AST, types   (8 versions)
1.1.x.x   Incremental compilation, parallel builds      (3 versions)
1.2.x.x   WebAssembly target + WASM runtime             (5 versions)
1.3.x.x   Bytecode VM + JIT (experimental)              (4 versions)
1.4.x.x   Native LLVM backend + cross-compilation       (3 versions)
1.5.x.x   Full LSP + DAP debugger                       (4 versions)
1.6.x.x   AI layer v2: streaming, cache, fine-tuning    (5 versions)
1.7.x.x   Package registry + first-party packages       (4 versions)
1.8.x.x   v1 stable: audit, perf targets, website       (4 versions)

              🎉 v1.0.0.0-stable 🎉
```

---

> **Nova** — *Build the web. Born from the stars.*
