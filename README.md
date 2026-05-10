# Nova Programming Language

<p align="center">
  <img src="https://img.shields.io/badge/Version-0.0.0.1-orange" alt="Version">
  <img src="https://img.shields.io/badge/Phase-Python%20Prototype-blue" alt="Phase">
  <img src="https://img.shields.io/badge/License-MIT-green" alt="License">
  <a href="https://github.com/authorss81/Nova"><img src="https://img.shields.io/badge/GitHub-Nova-success" alt="GitHub"></a>
</p>

> A world-class, web-development focused programming language with built-in AI capabilities.

## Overview

Nova is a modern, expressive programming language designed for web development. It features a **Python-inspired, English-leaning syntax** that makes code readable and approachable while maintaining the power and flexibility needed for production applications.

## Key Features

- **English-like Syntax**: Code that reads like natural language
- **Indentation-based Blocks**: Clean, consistent formatting without braces
- **Built-in AI Integration**: First-class AI capabilities via Minimax API
- **Web-Native Keywords**: `page`, `route`, `component`, `send`, `find`
- **Type Safety**: Optional static typing with full inference
- **Multiple Rendering Modes**: SSR, SSG, ISR, Islands Architecture

## Quick Start

### Installation

```bash
git clone https://github.com/authorss81/Nova.git
cd Nova
pip install -e .
```

### Run Your First Nova Program

Create a file `hello.nv`:

```nova
page Home:
  title "Welcome to Nova"
  
  component Greeting(name: text):
    heading "Hello, {name}!"
    button "Get Started" -> navigate("/app")

fn greet(name: text) -> text:
  return "Hello, {name}!"

on button "#submit" click:
  let data = form("#signup").values()
  let result = await post("/api/signup", data)
  if result.ok: navigate("/welcome")
```

Run it:

```bash
nova run hello.nv
```

## Syntax Philosophy

Nova uses indentation + `:` to define blocks — no curly braces:

```nova
if user.isAuthenticated:
  showDashboard()
else:
  showLogin()
```

English keywords for logic: `not`, `and`, `or`, `is`, `where`

```nova
if not user and hasPermission:
  allowAccess()
```

## Versioning

Nova follows **Phase-based versioning**:

| Segment | Meaning |
|---------|---------|
| `0.x.x.x` | Python implementation (design, prototype, spec) |
| `1.x.x.x` | Rust rewrite (performance, WASM, production) |

Current: **v0.0.0.1** (Project Skeleton)

## Project Structure

```
Nova/
├── src/nova/           # Source code
│   ├── lexer/          # Tokenizer
│   ├── parser/         # Parser
│   ├── ast/            # AST nodes
│   ├── interpreter/    # Runtime interpreter
│   ├── codegen/        # Code generation
│   └── ...
├── tests/              # Test suite
├── examples/           # Example programs
├── docs/               # Documentation
├── stdlib/             # Standard library
└── tools/              # Development tools
```

## Roadmap

See [ROADMAP(nova).md](ROADMAP(nova).md) for the complete implementation plan.

Phase 0 covers Python implementation milestones:
- **0.0** — Project Foundation & Lexer
- **0.1** — Parser & AST
- **0.2** — Core Interpreter
- **0.3** — Advanced Language Features
- **0.4** — Type System
- **0.5** — Web: HTML, CSS & Components
- ...through 0.19 — Spec Freeze

Phase 1 covers Rust rewrite starting at v1.0.0.0.

## Development Status

| Milestone | Status |
|-----------|--------|
| 0.0 - Project Foundation & Lexer | In Progress |
| 0.1 - Parser & AST | Pending |
| 0.2 - Core Interpreter | Pending |
| ... | ... |
| 0.19 - Spec Freeze | Pending |
| 1.0 - Rust Rewrite | Pending |

## Documentation

- [ROADMAP(nova).md](ROADMAP(nova).md) — Full implementation roadmap
- [CONTRIBUTING.md](CONTRIBUTING.md) — How to contribute
- [docs/](./docs/) — Documentation directory

## License

MIT License - see [LICENSE](LICENSE) for details.

## Contributing

Contributions welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

**Phase 0.x.x.x** — Python implementation (design, prototype, spec)