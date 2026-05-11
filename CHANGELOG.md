# Nova Programming Language

A world-class, web-development focused programming language with built-in AI capabilities.

## Version

**v0.0.0.2** — Source File Handling

- `SourceFile` class with UTF-8 encoding support
- Line/column tracking with `SourcePosition` and `SourceSpan`
- Shebang line support (`#!/usr/bin/env nova`)
- `from_file()`, `from_string()`, `from_lines()` factories
- File encoding detection (UTF-8, UTF-8-BOM, UTF-16, ASCII)
- Position-to-offset and offset-to-position conversion
- Line and text retrieval with context helpers
- Pattern finding (`find`, `find_all`, `lines_with_pattern`)
- Content hash for caching
- 30+ unit tests

## Installation

```bash
pip install -e .
```

## Usage

```bash
nova run hello.nv
nova --version
nova --help
```