# Nova Programming Language

A world-class, web-development focused programming language with built-in AI capabilities.

## Version

**v0.0.0.5** — Tokenizer: Literals

- `true`/`false`/`null` now tokenize as `TRUE`/`FALSE`/`NULL` (not `KEYWORD`)
- Added `LITERAL_KEYWORDS` dict mapping `{"true": TRUE, "false": FALSE, "null": NULL}`
- Removed `true`, `false`, `null` from `KEYWORDS` set (now 50 keywords)
- `is_keyword("true")` / `is_keyword("false")` / `is_keyword("null")` return `False`
- Added `TestLexerLiterals` test class (10 tests)
- 220 unit tests — all passing

**v0.0.0.4** — Tokenizer: Keywords & Identifiers

- Trimmed `KEYWORDS` set to exact roadmap reserved keywords (53 keywords)
- Added Unicode identifier support (accented, Cyrillic, CJK, mixed scripts)
- Confirmed `_` (underscore) as valid identifier both standalone and within
- Verified keywords are case-sensitive (`let` vs `Let`)
- Added `KeywordCompleteness` test class — all 53 keywords tokenize as KEYWORD
- Added `UnicodeIdentifiers` test class — accented, Cyrillic, Chinese, Japanese, mixed
- Added `UnderscoreIdentifier` test class — standalone `_`, `__init__`, in expressions
- 210 unit tests — all passing

**v0.0.0.3** — Tokenizer Core

- `Lexer` class with character-by-character scanning
- Full token type enum (`TokenType`) with 70+ token types
- `Token` dataclass with position tracking
- Operator scanning with longest-match-first (`..`, `...`, `..=`, `**`, `**=`, etc.)
- String literal scanning (double and single quotes, escape sequences)
- Number literal scanning (integers, floats, hex/octal/binary, underscores, scientific notation)
- Identifier and keyword scanning with keyword set
- Comment scanning (`//` line, `/* */` block)
- Newline, whitespace, and shebang handling
- `checkpoint()`/`restore()` for backtracking
- `peek_token(offset)` for lookahead without consuming
- `reset()` for re-tokenization
- Error collection (`add_error`, `get_errors`, `has_errors`)
- Interactive mode (`tokenize_interactive`)
- 167 unit tests — all passing

**v0.0.0.2** — Source File Handling

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