"""
Nova Error Types
"""


class NovaError(Exception):
    """Base exception for all Nova errors."""

    def __init__(
        self,
        message: str,
        line: int = 0,
        col: int = 0,
        filename: str = "",
        hint: str = ""
    ):
        self.message = message
        self.line = line
        self.col = col
        self.filename = filename
        self.hint = hint
        super().__init__(self._format_message())

    def _format_message(self) -> str:
        location = ""
        if self.filename:
            location += f" in '{self.filename}'"
        if self.line > 0:
            location += f" at line {self.line}"
            if self.col > 0:
                location += f", column {self.col}"

        msg = f"NovaError{location}: {self.message}"
        if self.hint:
            msg += f"\n  Hint: {self.hint}"
        return msg

    def to_dict(self) -> dict:
        return {
            "error": "NovaError",
            "message": self.message,
            "line": self.line,
            "column": self.col,
            "filename": self.filename,
            "hint": self.hint
        }


class LexerError(NovaError):
    """Error raised during lexical analysis."""
    pass


class ParserError(NovaError):
    """Error raised during parsing."""
    pass


class TypeError(NovaError):
    """Error raised during type checking."""
    pass


class RuntimeError(NovaError):
    """Error raised during execution."""
    pass


class NovaExit(NovaError):
    """Error raised to exit the Nova runtime."""
    def __init__(self, code: int = 0, message: str = ""):
        self.code = code
        super().__init__(message=f"Exit code {code}" if not message else message)


__all__ = ["NovaError", "LexerError", "ParserError", "TypeError", "RuntimeError", "NovaExit"]