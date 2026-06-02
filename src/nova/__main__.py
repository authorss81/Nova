"""
Nova Programming Language CLI

A world-class, web-development focused programming language with built-in AI capabilities.
Phase 0.x.x.x — Python implementation (design, prototype, spec)
"""

import sys
import argparse
from pathlib import Path

from nova.errors import NovaError, LexerError, ParserError, TypeError, RuntimeError, NovaExit

__version__ = "0.0.0.6"
__author__ = "Nova Language Team"
__license__ = "MIT"


def get_version() -> str:
    return __version__


def get_full_version() -> str:
    return f"Nova Programming Language v{__version__}\nPhase: 0.x.x.x (Python Implementation)"


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="nova",
        description="Nova Programming Language - A world-class, web-development focused programming language with built-in AI capabilities.",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument("--version", "-v", action="version", version=get_full_version())
    parser.add_argument("--help", "-h", action="help", help="Show this help message and exit")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    run_parser = subparsers.add_parser("run", help="Run a Nova program")
    run_parser.add_argument("file", help="Path to the Nova file to run")
    run_parser.add_argument("--debug", action="store_true", help="Enable debug output")
    
    build_parser = subparsers.add_parser("build", help="Compile Nova to JavaScript")
    build_parser.add_argument("file", help="Path to the Nova file")
    build_parser.add_argument("-o", "--output", help="Output file path")
    build_parser.add_argument("--target", default="esm", choices=["esm", "cjs", "iife", "umd"])
    
    fmt_parser = subparsers.add_parser("fmt", help="Format Nova source code")
    fmt_parser.add_argument("file", help="Path to the Nova file")
    fmt_parser.add_argument("--check", action="store_true")
    fmt_parser.add_argument("--write", action="store_true")
    
    lint_parser = subparsers.add_parser("lint", help="Lint Nova source code")
    lint_parser.add_argument("file", help="Path to the Nova file")
    lint_parser.add_argument("--fix", action="store_true")
    
    subparsers.add_parser("repl", help="Start the Nova REPL")
    
    ai_parser = subparsers.add_parser("ai", help="AI-powered commands")
    ai_subparsers = ai_parser.add_subparsers(dest="ai_command")
    gen_parser = ai_subparsers.add_parser("gen", help="Generate code with AI")
    gen_parser.add_argument("prompt", help="Description of code to generate")
    gen_parser.add_argument("-o", "--output", help="Output file path")
    explain_parser = ai_subparsers.add_parser("explain", help="Explain Nova code")
    explain_parser.add_argument("file", help="Path to the Nova file")
    
    test_parser = subparsers.add_parser("test", help="Run Nova tests")
    test_parser.add_argument("path", nargs="?", default="tests", help="Path to test directory")
    test_parser.add_argument("--watch", action="store_true")
    test_parser.add_argument("--coverage", action="store_true")
    
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        return 0
    
    if args.command == "run":
        return run_file(args.file, args.debug)
    elif args.command == "build":
        return build_file(args.file, args.output, args.target)
    elif args.command == "fmt":
        return fmt_file(args.file, args.check, args.write)
    elif args.command == "lint":
        return lint_file(args.file, args.fix)
    elif args.command == "repl":
        return start_repl()
    elif args.command == "ai":
        if args.ai_command == "gen":
            return ai_gen(args.prompt, args.output)
        elif args.ai_command == "explain":
            return ai_explain(args.file)
        ai_parser.print_help()
        return 1
    elif args.command == "test":
        return run_tests(args.path, args.watch, args.coverage)
    
    return 0


def run_file(filepath: str, debug: bool = False) -> int:
    from nova.lexer.source import SourceFile
    from nova.lexer.lexer import Lexer
    from nova.parser.parser import Parser
    from nova.interpreter.interpreter import Interpreter
    
    try:
        source = SourceFile.from_file(filepath)
        if debug:
            print(f"[DEBUG] Parsing: {filepath}")
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        if debug:
            print(f"[DEBUG] Generated {len(tokens)} tokens")
        parser = Parser(tokens)
        ast = parser.parse()
        if debug:
            print(f"[DEBUG] Parsed AST with {len(ast.body)} statements")
        interpreter = Interpreter()
        result = interpreter.evaluate(ast)
        if debug:
            print(f"[DEBUG] Execution completed")
        return 0
    except NovaError as e:
        print(e, file=sys.stderr)
        return 1
    except Exception as e:
        print(f"NovaError: Unexpected error: {e}", file=sys.stderr)
        if debug:
            import traceback
            traceback.print_exc()
        return 1


def build_file(filepath: str, output: str = None, target: str = "esm") -> int:
    from nova.lexer.source import SourceFile
    from nova.lexer.lexer import Lexer
    from nova.parser.parser import Parser
    from nova.codegen.js_codegen import JSCodegen
    
    try:
        source = SourceFile.from_file(filepath)
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        codegen = JSCodegen(target=target)
        js_code = codegen.generate(ast)
        if output:
            Path(output).write_text(js_code)
            print(f"Compiled to {output}")
        else:
            print(js_code)
        return 0
    except NovaError as e:
        print(e, file=sys.stderr)
        return 1


def fmt_file(filepath: str, check: bool = False, write: bool = False) -> int:
    from nova.formatter.formatter import Formatter
    try:
        source = SourceFile.from_file(filepath)
        formatter = Formatter()
        formatted = formatter.format(source)
        if check:
            original = Path(filepath).read_text()
            if original != formatted:
                print(f"Would reformat {filepath}")
                return 1
            print(f"Correctly formatted {filepath}")
            return 0
        elif write:
            Path(filepath).write_text(formatted)
            print(f"Formatted {filepath}")
            return 0
        print(formatted)
        return 0
    except NovaError as e:
        print(e, file=sys.stderr)
        return 1


def lint_file(filepath: str, fix: bool = False) -> int:
    from nova.linter.linter import Linter
    try:
        source = SourceFile.from_file(filepath)
        linter = Linter()
        issues = linter.lint(source)
        if issues:
            for issue in issues:
                print(issue)
            return 1
        print(f"No issues found in {filepath}")
        return 0
    except NovaError as e:
        print(e, file=sys.stderr)
        return 1


def start_repl() -> int:
    from nova.repl.repl import REPL
    print(f"Nova Programming Language v{__version__}")
    print("Type '.help' for more information, '.exit' to exit")
    print()
    repl = REPL()
    try:
        repl.run()
    except NovaExit as e:
        return e.code
    return 0


def ai_gen(prompt: str, output: str = None) -> int:
    print(f"Generating code: {prompt}")
    print("(AI generation requires Minimax API configuration)")
    return 1


def ai_explain(filepath: str) -> int:
    print(f"Explaining code in: {filepath}")
    print("(AI explanation requires Minimax API configuration)")
    return 1


def run_tests(path: str, watch: bool = False, coverage: bool = False) -> int:
    print(f"Running tests in: {path}")
    print("(Test runner not yet implemented)")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nInterrupted", file=sys.stderr)
        sys.exit(130)