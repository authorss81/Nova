# Contributing to Nova

Thank you for your interest in contributing to Nova! This document provides guidelines and instructions for contributing.

## Ways to Contribute

1. **Implement Milestone Features** — Follow the roadmap and implement assigned versions
2. **Write Tests** — Expand test coverage for lexer, parser, interpreter
3. **Bug Reports** — Report issues with detailed reproduction steps
4. **Documentation** — Improve docs, examples, and guides
5. **Code Review** — Help review pull requests
6. **Feedback** — Provide feedback on syntax and language design

## Development Setup

### Prerequisites

- Python 3.10+
- Git

### Initial Setup

```bash
# Clone the repository
git clone https://github.com/authorss81/Nova.git
cd Nova

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate  # Windows

# Install in development mode
pip install -e .
pip install -r requirements-dev.txt

# Run tests
pytest tests/
```

## Project Structure

```
Nova/
├── src/nova/              # Main source code
│   ├── lexer/             # Lexical analysis
│   │   ├── source.py      # Source file handling
│   │   ├── lexer.py       # Tokenizer
│   │   └── tokens.py      # Token types
│   ├── parser/            # Parsing
│   ├── ast/               # AST definitions
│   ├── interpreter/       # Runtime interpreter
│   ├── codegen/           # Code generation
│   └── errors/            # Error definitions
├── tests/                 # Test suite
│   ├── unit/              # Unit tests
│   └── integration/       # Integration tests
├── examples/              # Example .nv programs
├── docs/                  # Documentation
└── tools/                 # Development tools
```

## Coding Standards

### Python Code

- Follow PEP 8 style guide
- Use type hints for all function signatures
- Maximum line length: 100 characters
- Use meaningful variable and function names
- Add docstrings for public APIs

### Nova Language Code

- Use indentation + `:` for blocks (no braces)
- English keywords: `not`, `and`, `or`, `is`, `where`
- Web keywords: `page`, `route`, `component`, `send`, `find`
- No semicolons; newlines are meaningful

## Version Implementation Process

### For Each Version (e.g., 0.0.0.2)

1. **Create a branch**:
   ```bash
   git checkout -b feat/0.0.0.2-source-file-handling
   ```

2. **Implement the version** per ROADMAP specifications

3. **Write tests**:
   ```bash
   pytest tests/unit/lexer/test_source.py -v
   ```

4. **Run the full test suite**:
   ```bash
   pytest tests/ -v
   ```

5. **Update version in** `src/nova/__init__.py`

6. **Commit with message**:
   ```
   feat(version): implement v0.0.0.2 - Source File Handling
   
   - Add SourceFile class for reading .nv files
   - Track UTF-8 encoding
   - Support shebang lines
   ```

7. **Create a GitHub Release** with version tag

## Version Format

Nova versions follow `a.x.y.z`:

| Segment | Meaning |
|---------|---------|
| `a` | Major era (0=Python, 1=Rust) |
| `x` | Milestone group |
| `y` | Sub-milestone |
| `z` | Micro-version (1-2 features) |

## Testing Guidelines

### Test Structure

```python
def test_lexer_integer_literals():
    """Test integer literal tokenization."""
    source = SourceFile.from_string("42 0xFF 0o77 0b1010")
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    
    assert len(tokens) == 4
    assert tokens[0].type == TokenType.INTEGER
    assert tokens[0].value == "42"
```

### Test Categories

1. **Unit Tests** — Test individual components in isolation
2. **Integration Tests** — Test component interactions
3. **Property Tests** — Verify properties across many inputs
4. **Fuzz Tests** — Random inputs to find edge cases

## Error Handling

All Nova errors should include:
- Clear error message
- Line and column number
- Filename (if applicable)
- Helpful hint for fixing

```python
raise LexerError(
    "Unterminated string literal",
    line=self.line, 
    col=self.col, 
    filename=self.source.filename,
    hint="Did you forget to close the string?"
)
```

## Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

Example:
```
feat(lexer): implement v0.0.0.4 - Keywords & Identifiers

- Add all reserved keywords: let, const, fn, return, if, else...
- Support unicode identifiers
- Support underscore as valid identifier

Closes #12
```

## Pull Request Process

1. Fork the repository
2. Create a feature branch from `main`
3. Implement your feature/fix
4. Add/update tests
5. Ensure all tests pass
6. Update documentation if needed
7. Submit a pull request with description

## Communication

- **Issues**: Use GitHub Issues for bug reports and feature requests
- **Discussions**: Use GitHub Discussions for questions and ideas
- **Reviews**: Be respectful and constructive in code reviews

## Recognition

All contributors will be recognized in:
- The project's README (if significant contribution)
- Release notes
- The commit history

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing to Nova!**