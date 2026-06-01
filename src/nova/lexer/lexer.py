"""
Nova Lexer

Character-by-character scanner with lookahead for tokenizing Nova source code.
"""

from typing import Optional
from nova.lexer.source import SourceFile
from nova.lexer.tokens import Token, TokenType, is_keyword
from nova.errors import LexerError


class Lexer:
    """Tokenizes Nova source code with full position tracking."""
    
    def __init__(self, source: SourceFile):
        self.source = source
        self.content = source.content
        self.pos = 0
        self.line = 1
        self.col = 1
        self.start_pos = 0
        self.start_line = 1
        self.start_col = 1
        self.tokens: list[Token] = []
        self.current_char: Optional[str] = self._peek(0)
        self.errors: list[LexerError] = []
        self._token_cache: dict[int, list[Token]] = {}
        self._checkpoint_pos = 0
        self._checkpoint_line = 1
        self._checkpoint_col = 1
    
    def _peek(self, offset: int = 0) -> Optional[str]:
        idx = self.pos + offset
        if idx >= len(self.content):
            return None
        return self.content[idx]
    
    def _advance(self) -> Optional[str]:
        ch = self._peek()
        self.pos += 1
        if ch == '\n':
            self.line += 1
            self.col = 1
        else:
            self.col += 1
        self.current_char = self._peek()
        return ch
    
    def _match(self, expected: str) -> bool:
        for i, ch in enumerate(expected):
            if self._peek(i) != ch:
                return False
        for _ in expected:
            self._advance()
        return True
    
    def _skip_whitespace(self) -> bool:
        ch = self._peek()
        if ch is None or ch == '\n':
            return False

        if ch in ' \t\r':
            while True:
                next_ch = self._peek()
                if next_ch is None or next_ch not in ' \t\r':
                    break
                self._advance()
            return True
        return False
    
    def _skip_comment(self) -> bool:
        if self._peek() == '/' and self._peek(1) == '/':
            while self._peek() and self._peek() != '\n':
                self._advance()
            return True
        if self._peek() == '/' and self._peek(1) == '*':
            self._advance()
            self._advance()
            while self._peek() and not (self._peek() == '*' and self._peek(1) == '/'):
                self._advance()
            if self._peek():
                self._advance()
                self._advance()
            return True
        return False
    
    def _read_identifier(self) -> str:
        result = []
        while self._peek() and (self._peek().isalnum() or self._peek() in '_$'):
            result.append(self._advance())
        return ''.join(result)
    
    def _read_number(self) -> str:
        result = []
        has_decimal = False
        has_exponent = False
        
        peek1 = self._peek(1)
        if self._peek() == '0' and peek1 is not None and peek1 in 'xXoObB':
            result.append(self._advance())
            prefix = self._peek().lower()
            result.append(self._advance())
            while self._peek() and (self._peek().isalnum() or self._peek() == '_'):
                result.append(self._advance())
            return ''.join(result)
        
        while self._peek() and (self._peek().isdigit() or self._peek() == '_'):
            if self._peek() != '_':
                result.append(self._advance())
            else:
                self._advance()
        
        if self._peek() == '.' and self._peek(1) and self._peek(1).isdigit():
            has_decimal = True
            result.append(self._advance())
            while self._peek() and (self._peek().isdigit() or self._peek() == '_'):
                if self._peek() != '_':
                    result.append(self._advance())
                else:
                    self._advance()
        
        ch = self._peek()
        if ch is not None and ch in 'eE':
            has_exponent = True
            result.append(self._advance())
            ch = self._peek()
            if ch is not None and ch in '+-':
                result.append(self._advance())
            while self._peek() and (self._peek().isdigit() or self._peek() == '_'):
                if self._peek() != '_':
                    result.append(self._advance())
                else:
                    self._advance()
        
        return ''.join(result)
    
    def _read_string(self, quote: str) -> str:
        result = [self._advance()]
        while self._peek() and self._peek() != quote:
            ch = self._peek()
            if ch == '\\':
                result.append(self._advance())
                if self._peek():
                    result.append(self._advance())
            elif ch == '\n':
                raise LexerError(
                    "Unterminated string literal",
                    line=self.line, col=self.col, filename=self.source.filename,
                    hint="Did you forget to close the string with a matching quote?"
                )
            else:
                result.append(self._advance())
        
        if not self._peek():
            raise LexerError(
                "Unterminated string literal",
                line=self.line, col=self.col, filename=self.source.filename,
                hint="Expected closing quote"
            )
        
        result.append(self._advance())
        return ''.join(result)
    
    def _scan_token(self) -> Optional[Token]:
        self._save_start()
        
        if self._skip_comment():
            return None
        
        if self._skip_whitespace():
            return None
        
        if self._peek() == '\n':
            ch = self._advance()
            return self._make_token(TokenType.NEWLINE, '\n')
        
        if self._peek() is None:
            return self._make_token(TokenType.EOF, '')
        
        ch = self._peek()
        
        if ch.isalpha() or ch in '_$':
            return self._scan_identifier_or_keyword()
        
        if ch.isdigit():
            return self._scan_number()
        
        if ch in '"\'':
            return self._scan_string()
        
        return self._scan_operator_or_delimiter()
    
    def _save_start(self):
        self.start_pos = self.pos
        self.start_line = self.line
        self.start_col = self.col
    
    def _make_token(self, type: TokenType, value: str) -> Token:
        length = len(value)
        return Token(
            type=type,
            value=value,
            line=self.start_line,
            col=self.start_col,
            length=length,
            filename=self.source.filename
        )
    
    def _scan_identifier_or_keyword(self) -> Token:
        identifier = self._read_identifier()
        type = TokenType.IDENTIFIER
        if is_keyword(identifier):
            type = TokenType.KEYWORD
        return self._make_token(type, identifier)
    
    def _scan_string(self) -> Token:
        quote = self._peek()
        string = self._read_string(quote)
        return self._make_token(TokenType.STRING, string)

    def _scan_number(self) -> Token:
        num = self._read_number()
        type = TokenType.INTEGER
        if '.' in num or 'e' in num.lower():
            type = TokenType.FLOAT
        return self._make_token(type, num)
    
    def _scan_operator_or_delimiter(self) -> Token:
        if self._match('...'):
            return self._make_token(TokenType.DOT_DOT_DOT, '...')
        if self._match('..='):
            return self._make_token(TokenType.DOT_DOT_EQ, '..=')
        if self._match('..'):
            return self._make_token(TokenType.DOT_DOT, '..')

        if self._match('=='):
            return self._make_token(TokenType.EQ_EQ, '==')
        if self._match('!='):
            return self._make_token(TokenType.BANG_EQ, '!=')
        if self._match('<='):
            return self._make_token(TokenType.LT_EQ, '<=')
        if self._match('>='):
            return self._make_token(TokenType.GT_EQ, '>=')
        if self._match('<<'):
            return self._make_token(TokenType.LT_LT, '<<')
        if self._match('>>'):
            return self._make_token(TokenType.GT_GT, '>>')

        if self._match('&&='):
            return self._make_token(TokenType.AMPER_AMPER, '&&=')
        if self._match('&&'):
            return self._make_token(TokenType.AMPER_AMPER, '&&')
        if self._match('||='):
            return self._make_token(TokenType.PIPE_PIPE, '||=')
        if self._match('||'):
            return self._make_token(TokenType.PIPE_PIPE, '||')

        if self._match('??='):
            return self._make_token(TokenType.QUESTION_QUESTION_EQ, '??=')
        if self._match('??'):
            return self._make_token(TokenType.QUESTION_QUESTION, '??')
        if self._match('?.'):
            return self._make_token(TokenType.QUESTION_DOT, '?.')

        if self._match('->'):
            return self._make_token(TokenType.ARROW, '->')
        if self._match('=>'):
            return self._make_token(TokenType.FAT_ARROW, '=>')

        if self._match('**='):
            return self._make_token(TokenType.STAR_STAR_EQ, '**=')
        if self._match('**'):
            return self._make_token(TokenType.STAR_STAR, '**')
        if self._match('*='):
            return self._make_token(TokenType.STAR_EQ, '*=')
        if self._match('/='):
            return self._make_token(TokenType.SLASH_EQ, '/=')
        if self._match('%='):
            return self._make_token(TokenType.PERCENT_EQ, '%=')
        if self._match('+='):
            return self._make_token(TokenType.PLUS_EQ, '+=')
        if self._match('-='):
            return self._make_token(TokenType.MINUS_EQ, '-=')
        if self._match('&='):
            return self._make_token(TokenType.AMPER_EQ, '&=')
        if self._match('|='):
            return self._make_token(TokenType.PIPE_EQ, '|=')
        if self._match('^='):
            return self._make_token(TokenType.CARET_EQ, '^=')

        ch = self._peek()
        single_char_tokens = {
            '+': TokenType.PLUS,
            '-': TokenType.MINUS,
            '*': TokenType.STAR,
            '/': TokenType.SLASH,
            '%': TokenType.PERCENT,
            '=': TokenType.EQ,
            '<': TokenType.LT,
            '>': TokenType.GT,
            '&': TokenType.AMPERSAND,
            '|': TokenType.PIPE,
            '^': TokenType.CARET,
            '~': TokenType.TILDE,
            '?': TokenType.QUESTION,
            ':': TokenType.COLON,
            ';': TokenType.SEMICOLON,
            ',': TokenType.COMMA,
            '.': TokenType.DOT,
            '(': TokenType.LPAREN,
            ')': TokenType.RPAREN,
            '[': TokenType.LBRACKET,
            ']': TokenType.RBRACKET,
            '{': TokenType.LBRACE,
            '}': TokenType.RBRACE,
            '@': TokenType.AT,
            '!': TokenType.BANG,
        }

        if ch in single_char_tokens:
            self._advance()
            return self._make_token(single_char_tokens[ch], ch)

        self._advance()
        return self._make_token(TokenType.ILLEGAL, ch)
    
    def tokenize(self) -> list[Token]:
        """Tokenize the entire source file."""
        while True:
            token = self._scan_token()
            if token is None:
                continue
            if token.type == TokenType.EOF:
                self.tokens.append(token)
                break
            self.tokens.append(token)
        
        return self.tokens
    
    def tokenize_interactive(self) -> Token:
        """Tokenize a single token for interactive mode."""
        while True:
            token = self._scan_token()
            if token is not None:
                return token

    def checkpoint(self) -> tuple[int, int, int]:
        """Save lexer state for potential backtracking."""
        self._checkpoint_pos = self.pos
        self._checkpoint_line = self.line
        self._checkpoint_col = self.col
        return (self._checkpoint_pos, self._checkpoint_line, self._checkpoint_col)
    
    def restore(self, checkpoint: tuple[int, int, int]) -> None:
        """Restore lexer state from checkpoint."""
        self.pos, self.line, self.col = checkpoint
        self.current_char = self._peek()
    
    def get_source_span(self) -> tuple[int, int]:
        """Get current token source span as (start, end) offsets."""
        return (self.start_pos, self.pos)
    
    def get_source_position(self) -> tuple[int, int, int]:
        """Get current position as (offset, line, col)."""
        return (self.pos, self.line, self.col)
    
    def peek_token(self, offset: int = 0) -> Optional[Token]:
        """Look ahead at a future token without consuming it."""
        saved_pos = self.pos
        saved_line = self.line
        saved_col = self.col
        saved_start_pos = self.start_pos
        saved_start_line = self.start_line
        saved_start_col = self.start_col
        saved_current = self.current_char

        temp_tokens = []
        while len(temp_tokens) <= offset:
            token = self._scan_token()
            if token is None:
                continue
            temp_tokens.append(token)
            if token.type == TokenType.EOF:
                break

        result = temp_tokens[-1] if temp_tokens else None

        self.pos = saved_pos
        self.line = saved_line
        self.col = saved_col
        self.start_pos = saved_start_pos
        self.start_line = saved_start_line
        self.start_col = saved_start_col
        self.current_char = saved_current

        return result
    
    def reset(self) -> None:
        """Reset the lexer to the beginning."""
        self.pos = 0
        self.line = 1
        self.col = 1
        self.start_pos = 0
        self.start_line = 1
        self.start_col = 1
        self.current_char = self._peek(0) if self.content else None
        self.tokens = []
        self.errors = []
    
    @property
    def is_at_end(self) -> bool:
        """Check if lexer has consumed all input."""
        return self.pos >= len(self.content)
    
    @property
    def current_offset(self) -> int:
        """Get current offset in source."""
        return self.pos
    
    @property
    def remaining(self) -> str:
        """Get remaining unparsed content."""
        return self.content[self.pos:]
    
    def add_error(self, message: str, hint: str = "") -> None:
        """Record a non-fatal lexer error."""
        error = LexerError(
            message=message,
            line=self.line,
            col=self.col,
            filename=self.source.filename,
            hint=hint
        )
        self.errors.append(error)
    
    def get_errors(self) -> list[LexerError]:
        """Get all recorded lexer errors."""
        return self.errors.copy()
    
    def has_errors(self) -> bool:
        """Check if any errors were recorded."""
        return len(self.errors) > 0
    
    def __repr__(self) -> str:
        return f"<Lexer at {self.line}:{self.col} pos={self.pos}/{len(self.content)}>"