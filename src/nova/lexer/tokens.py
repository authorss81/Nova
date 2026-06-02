"""
Token Types for Nova

All token categories supported by the Nova lexer.
"""

from enum import Enum, auto
from typing import Optional


class TokenType(Enum):
    EOF = 0
    
    IDENTIFIER = auto()
    KEYWORD = auto()
    RESERVED = auto()
    
    INTEGER = auto()
    FLOAT = auto()
    STRING = auto()
    TEMPLATE_START = auto()
    TEMPLATE_MID = auto()
    TEMPLATE_END = auto()
    RAW_STRING = auto()
    
    TRUE = auto()
    FALSE = auto()
    NULL = auto()
    
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    PERCENT = auto()
    STAR_STAR = auto()
    
    EQ = auto()
    EQ_EQ = auto()
    BANG = auto()
    BANG_EQ = auto()
    LT = auto()
    GT = auto()
    LT_EQ = auto()
    GT_EQ = auto()
    
    AMPERSAND = auto()
    AMPER_AMPER = auto()
    PIPE = auto()
    PIPE_PIPE = auto()
    CARET = auto()
    TILDE = auto()
    LT_LT = auto()
    GT_GT = auto()
    
    QUESTION = auto()
    QUESTION_DOT = auto()
    DOT_DOT = auto()
    DOT_DOT_EQ = auto()
    DOT = auto()
    COLON = auto()
    SEMICOLON = auto()
    COMMA = auto()
    AT = auto()
    ARROW = auto()
    FAT_ARROW = auto()
    
    LPAREN = auto()
    RPAREN = auto()
    LBRACKET = auto()
    RBRACKET = auto()
    LBRACE = auto()
    RBRACE = auto()
    
    AMPER_EQ = auto()
    PIPE_EQ = auto()
    CARET_EQ = auto()
    PLUS_EQ = auto()
    MINUS_EQ = auto()
    STAR_EQ = auto()
    SLASH_EQ = auto()
    PERCENT_EQ = auto()
    STAR_STAR_EQ = auto()
    
    QUESTION_QUESTION = auto()
    QUESTION_QUESTION_EQ = auto()
    
    DOT_DOT_DOT = auto()
    
    COMMENT = auto()
    DOC_COMMENT = auto()
    WHITESPACE = auto()
    NEWLINE = auto()
    
    ERROR = auto()
    ILLEGAL = auto()


KEYWORDS = {
    "let", "const", "fn", "return", "if", "else", "for", "while",
    "in", "break", "continue", "true", "false", "null", "import",
    "export", "from", "class", "extends", "new", "this", "super",
    "static", "async", "await", "try", "catch", "finally", "throw",
    "match", "case", "type", "interface", "enum", "as", "is", "of",
    "yield", "page", "component", "style", "route", "ai", "not",
    "and", "or", "where", "on", "send", "find", "show", "give", "with",
}


def is_keyword(text: str) -> bool:
    return text in KEYWORDS


class Token:
    """Represents a token in Nova source code."""
    
    __slots__ = ('type', 'value', 'line', 'col', 'length', 'filename')
    
    def __init__(
        self,
        type: TokenType,
        value: str,
        line: int = 0,
        col: int = 0,
        length: int = 0,
        filename: str = ""
    ):
        self.type = type
        self.value = value
        self.line = line
        self.col = col
        self.length = length
        self.filename = filename
    
    @property
    def span(self):
        from nova.lexer.source import SourceSpan, SourcePosition
        start = SourcePosition(self.line, self.col, 0)
        end = SourcePosition(self.line, self.col + self.length, 0)
        return SourceSpan(start, end)
    
    def __repr__(self) -> str:
        return f"Token({self.type.name}, {self.value!r}, {self.line}:{self.col})"
    
    def __str__(self) -> str:
        return f"{self.type.name}({self.value!r})"
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Token):
            return NotImplemented
        return self.type == other.type and self.value == other.value
    
    def __hash__(self) -> int:
        return hash((self.type, self.value))
    
    def is_keyword(self) -> bool:
        return self.type == TokenType.IDENTIFIER and is_keyword(self.value)
    
    def is_operator(self) -> bool:
        return self.type in {
            TokenType.PLUS, TokenType.MINUS, TokenType.STAR, TokenType.SLASH,
            TokenType.PERCENT, TokenType.STAR_STAR, TokenType.EQ, TokenType.EQ_EQ,
            TokenType.BANG, TokenType.BANG_EQ, TokenType.LT, TokenType.GT,
            TokenType.LT_EQ, TokenType.GT_EQ, TokenType.AMPER_AMPER, TokenType.PIPE_PIPE,
            TokenType.QUESTION, TokenType.QUESTION_DOT, TokenType.QUESTION_QUESTION,
            TokenType.DOT_DOT, TokenType.DOT_DOT_EQ
        }
    
    def is_comparison(self) -> bool:
        return self.type in {
            TokenType.EQ_EQ, TokenType.BANG_EQ, TokenType.LT, TokenType.GT,
            TokenType.LT_EQ, TokenType.GT_EQ
        }
    
    def is_assignment(self) -> bool:
        return self.type in {
            TokenType.EQ, TokenType.PLUS_EQ, TokenType.MINUS_EQ, TokenType.STAR_EQ,
            TokenType.SLASH_EQ, TokenType.PERCENT_EQ, TokenType.STAR_STAR_EQ,
            TokenType.AMPER_EQ, TokenType.PIPE_EQ, TokenType.CARET_EQ,
            TokenType.QUESTION_QUESTION_EQ
        }
    
    def to_dict(self) -> dict:
        return {
            "type": self.type.name,
            "value": self.value,
            "line": self.line,
            "column": self.col,
            "length": self.length
        }