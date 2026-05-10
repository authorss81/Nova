"""
Nova Lexer

Character-by-character scanner with lookahead for tokenizing Nova source code.
"""

from typing import Optional
from nova.lexer.source import SourceFile
from nova.lexer.tokens import Token, TokenType
from nova.errors import LexerError


class Lexer:
    """Tokenizes Nova source code."""
    
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
        if self._peek() == expected:
            self._advance()
            return True
        return False
    
    def _skip_whitespace(self) -> bool:
        ch = self._peek()
        if ch is None or ch == '\n':
            return False
        
        if ch in ' \t\r':
            while self._peek() in ' \t\r':
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
        
        if self._peek() == '0' and self._peek(1) in 'xXoObB':
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
        
        if self._peek() in 'eE':
            has_exponent = True
            result.append(self._advance())
            if self._peek() in '+-':
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
        if TokenType.is_keyword(identifier):
            type = TokenType.KEYWORD
        return self._make_token(type, identifier)
    
    def _scan_number(self) -> Token:
        num = self._read_number()
        type = TokenType.INTEGER
        if '.' in num or 'e' in num.lower():
            type = TokenType.FLOAT
        return self._make_token(type, num)
    
    def _scan_operator_or_delimiter(self) -> Token:
        ch = self._peek()
        
        if self._match('..'):
            if self._match('='):
                return self._make_token(TokenType.DOT_DOT_EQ, '..=')
            return self._make_token(TokenType.DOT_DOT, '..')
        
        if self._match('=='):
            return self._make_token(TokenType.EQ_EQ, '==')
        if self._match('!='):
            if self._match('='):
                return self._make_token(TokenType.BANG_EQ, '!=')
            return self._make_token(TokenType.BANG, '!')
        
        if self._match('<='):
            return self._make_token(TokenType.LT_EQ, '<=')
        if self._match('>='):
            return self._make_token(TokenType.GT_EQ, '>=')
        if self._match('<<'):
            return self._make_token(TokenType.LT_LT, '<<')
        if self._match('>>'):
            return self._make_token(TokenType.GT_GT, '>>')
        
        if self._match('&&'):
            if self._match('='):
                return self._make_token(TokenType.AMPER_AMPER, '&&=')
            return self._make_token(TokenType.AMPER_AMPER, '&&')
        if self._match('||'):
            if self._match('='):
                return self._make_token(TokenType.PIPE_PIPE, '||=')
            return self._make_token(TokenType.PIPE_PIPE, '||')
        
        if self._match('??'):
            if self._match('='):
                return self._make_token(TokenType.QUESTION_QUESTION_EQ, '??=')
            return self._make_token(TokenType.QUESTION_QUESTION, '??')
        
        if self._match('?.'):
            return self._make_token(TokenType.QUESTION_DOT, '?.')
        
        if self._match('->'):
            return self._make_token(TokenType.ARROW, '->')
        if self._match('=>'):
            return self._make_token(TokenType.FAT_ARROW, '=>')
        
        if self._match('+='):
            return self._make_token(TokenType.PLUS_EQ, '+=')
        if self._match('-='):
            return self._make_token(TokenType.MINUS_EQ, '-=')
        if self._match('*='):
            if self._match('*'):
                if self._match('='):
                    return self._make_token(TokenType.STAR_STAR_EQ, '**=')
                return self._make_token(TokenType.STAR_STAR, '**')
            return self._make_token(TokenType.STAR_EQ, '*=')
        if self._match('/='):
            return self._make_token(TokenType.SLASH_EQ, '/=')
        if self._match('%='):
            return self._make_token(TokenType.PERCENT_EQ, '%=')
        if self._match('&='):
            return self._make_token(TokenType.AMPER_EQ, '&=')
        if self._match('|='):
            return self._make_token(TokenType.PIPE_EQ, '|=')
        if self._match('^='):
            return self._make_token(TokenType.CARET_EQ, '^=')
        
        if self._match('...'):
            return self._make_token(TokenType.DOT_DOT_DOT, '...')
        
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
        token = self._scan_token()
        return token if token else Token(TokenType.EOF, '', self.line, self.col)