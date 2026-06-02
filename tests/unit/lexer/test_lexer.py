import pytest
from nova.lexer.lexer import Lexer
from nova.lexer.source import SourceFile
from nova.lexer.tokens import Token, TokenType, KEYWORDS
from nova.errors import LexerError


def make_lexer(code: str, filename: str = "<test>") -> Lexer:
    source = SourceFile.from_string(code, filename)
    return Lexer(source)


def tokenize(code: str, filename: str = "<test>") -> list[Token]:
    lexer = make_lexer(code, filename)
    return lexer.tokenize()


def types(code: str | list[Token]) -> list[TokenType]:
    if isinstance(code, list):
        return [t.type for t in code if t.type not in (TokenType.NEWLINE, TokenType.EOF)]
    return [t.type for t in tokenize(code) if t.type not in (TokenType.NEWLINE, TokenType.EOF)]


class TestLexerInit:
    def test_empty_source(self):
        lexer = make_lexer("")
        assert lexer.content == ""
        assert lexer.pos == 0
        assert lexer.line == 1
        assert lexer.col == 1
        assert lexer.current_char is None
        assert lexer.is_at_end is True

    def test_single_char_source(self):
        lexer = make_lexer("a")
        assert lexer.current_char == "a"
        assert lexer.is_at_end is False

    def test_source_file_ref(self):
        source = SourceFile.from_string("test", "test.nv")
        lexer = Lexer(source)
        assert lexer.source is source
        assert lexer.source.filename == "test.nv"


class TestLexerProperties:
    def test_is_at_end(self):
        lexer = make_lexer("abc")
        assert lexer.is_at_end is False
        lexer.pos = 3
        assert lexer.is_at_end is True

    def test_current_offset(self):
        lexer = make_lexer("hello")
        assert lexer.current_offset == 0
        lexer.pos = 3
        assert lexer.current_offset == 3

    def test_remaining(self):
        lexer = make_lexer("hello world")
        assert lexer.remaining == "hello world"
        lexer.pos = 6
        assert lexer.remaining == "world"

    def test_remaining_empty_at_end(self):
        lexer = make_lexer("hi")
        lexer.pos = 2
        assert lexer.remaining == ""


class TestLexerEOF:
    def test_tokenize_empty_yields_eof(self):
        tokens = tokenize("")
        assert len(tokens) == 1
        assert tokens[0].type == TokenType.EOF
        assert tokens[0].value == ""

    def test_tokenize_whitespace_only_yields_eof(self):
        tokens = tokenize("   \t  ")
        assert len(tokens) == 1
        assert tokens[0].type == TokenType.EOF

    def test_tokenize_comment_only_yields_eof(self):
        tokens = tokenize("// just a comment")
        assert len(tokens) == 1
        assert tokens[0].type == TokenType.EOF

    def test_eof_position(self):
        tokens = tokenize("x")
        assert tokens[-1].type == TokenType.EOF


class TestLexerNewlines:
    def test_single_newline(self):
        toks = tokenize("\n")
        assert [t.type for t in toks] == [TokenType.NEWLINE, TokenType.EOF]

    def test_multiple_newlines(self):
        toks = tokenize("\n\n\n")
        assert [t.type for t in toks] == [TokenType.NEWLINE, TokenType.NEWLINE, TokenType.NEWLINE, TokenType.EOF]

    def test_newline_after_identifier(self):
        toks = tokenize("x\n")
        assert [t.type for t in toks if t.type != TokenType.EOF] == [TokenType.IDENTIFIER, TokenType.NEWLINE]

    def test_newline_positions(self):
        lexer = make_lexer("a\nb")
        toks = lexer.tokenize()
        id_tokens = [t for t in toks if t.type == TokenType.IDENTIFIER]
        assert id_tokens[0].line == 1
        assert id_tokens[1].line == 2


class TestLexerWhitespace:
    def test_spaces_skipped(self):
        toks = tokenize("a   b")
        assert types(toks) == [TokenType.IDENTIFIER, TokenType.IDENTIFIER]

    def test_tabs_skipped(self):
        toks = tokenize("a\t\tb")
        assert types(toks) == [TokenType.IDENTIFIER, TokenType.IDENTIFIER]

    def test_carriage_return_skipped(self):
        toks = tokenize("a\rb")
        assert types(toks) == [TokenType.IDENTIFIER, TokenType.IDENTIFIER]

    def test_mixed_whitespace_skipped(self):
        toks = tokenize("a \t\r b")
        assert types(toks) == [TokenType.IDENTIFIER, TokenType.IDENTIFIER]


class TestLexerComments:
    def test_line_comment(self):
        toks = tokenize("// comment")
        assert types(toks) == []

    def test_line_comment_with_code(self):
        toks = tokenize("x // comment")
        assert types(toks) == [TokenType.IDENTIFIER]

    def test_block_comment(self):
        toks = tokenize("/* comment */")
        assert types(toks) == []

    def test_block_comment_multiline(self):
        toks = tokenize("/*\nmulti\nline\n*/")
        assert types(toks) == []

    def test_block_comment_with_code(self):
        toks = tokenize("a /* block */ b")
        assert types(toks) == [TokenType.IDENTIFIER, TokenType.IDENTIFIER]

    def test_unclosed_block_comment(self):
        lexer = make_lexer("/* unclosed")
        lexer.tokenize()
        # should not crash; scan reaches EOF

    def test_comment_does_not_consume_newline(self):
        toks = tokenize("// comment\nx")
        assert types(toks) == [TokenType.IDENTIFIER]
        newlines = [t for t in toks if t.type == TokenType.NEWLINE]
        assert len(newlines) == 1


class TestLexerIdentifiers:
    def test_basic_identifier(self):
        toks = tokenize("hello")
        assert types(toks) == [TokenType.IDENTIFIER]
        assert toks[0].value == "hello"

    def test_identifier_with_underscore(self):
        toks = tokenize("my_var")
        assert toks[0].value == "my_var"

    def test_identifier_with_dollar(self):
        toks = tokenize("$value")
        assert toks[0].value == "$value"

    def test_identifier_with_numbers(self):
        toks = tokenize("var123")
        assert toks[0].value == "var123"

    def test_identifier_positions(self):
        lexer = make_lexer("  abc")
        toks = lexer.tokenize()
        tok = toks[0]
        assert tok.line == 1
        assert tok.col == 3

    def test_multiple_identifiers(self):
        toks = tokenize("foo bar baz")
        assert [t.value for t in toks if t.type == TokenType.IDENTIFIER] == ["foo", "bar", "baz"]


class TestLexerKeywords:
    def test_let_keyword(self):
        toks = tokenize("let")
        assert types(toks) == [TokenType.KEYWORD]
        assert toks[0].value == "let"

    def test_fn_keyword(self):
        toks = tokenize("fn")
        assert toks[0].type == TokenType.KEYWORD
        assert toks[0].value == "fn"

    def test_return_keyword(self):
        toks = tokenize("return")
        assert toks[0].type == TokenType.KEYWORD
        assert toks[0].value == "return"

    def test_identifier_not_keyword(self):
        toks = tokenize("customName")
        assert toks[0].type == TokenType.IDENTIFIER
        assert toks[0].value == "customName"

    def test_keyword_case_sensitive(self):
        toks = tokenize("Let")
        assert toks[0].type == TokenType.IDENTIFIER
        assert toks[0].value == "Let"


class TestLexerNumbers:
    def test_integer(self):
        toks = tokenize("42")
        assert types(toks) == [TokenType.INTEGER]
        assert toks[0].value == "42"

    def test_float(self):
        toks = tokenize("3.14")
        assert types(toks) == [TokenType.FLOAT]
        assert toks[0].value == "3.14"

    def test_float_leading_dot(self):
        toks = tokenize(".5")
        assert types(toks) == [TokenType.DOT, TokenType.INTEGER]
        # .5 is parsed as DOT + INTEGER because the scan starts with '.' not digit

    def test_hex_number(self):
        toks = tokenize("0xFF")
        assert types(toks) == [TokenType.INTEGER]
        assert toks[0].value == "0xFF"

    def test_octal_number(self):
        toks = tokenize("0o77")
        assert types(toks) == [TokenType.INTEGER]
        assert toks[0].value == "0o77"

    def test_binary_number(self):
        toks = tokenize("0b1010")
        assert types(toks) == [TokenType.INTEGER]
        assert toks[0].value == "0b1010"

    def test_number_with_underscore(self):
        toks = tokenize("1_000_000")
        assert types(toks) == [TokenType.INTEGER]
        assert toks[0].value == "1000000"

    def test_float_with_underscore(self):
        toks = tokenize("1_000.5_0")
        assert types(toks) == [TokenType.FLOAT]
        assert toks[0].value == "1000.50"

    def test_scientific_notation(self):
        toks = tokenize("1.5e10")
        assert types(toks) == [TokenType.FLOAT]
        assert toks[0].value == "1.5e10"

    def test_scientific_notation_positive_exponent(self):
        toks = tokenize("2e+5")
        assert types(toks) == [TokenType.FLOAT]
        assert toks[0].value == "2e+5"

    def test_scientific_notation_negative_exponent(self):
        toks = tokenize("2e-5")
        assert types(toks) == [TokenType.FLOAT]
        assert toks[0].value == "2e-5"

    def test_zero(self):
        toks = tokenize("0")
        assert types(toks) == [TokenType.INTEGER]
        assert toks[0].value == "0"


class TestLexerStrings:
    def test_double_quoted_string(self):
        toks = tokenize('"hello"')
        assert types(toks) == [TokenType.STRING]
        assert toks[0].value == '"hello"'

    def test_single_quoted_string(self):
        toks = tokenize("'hello'")
        assert types(toks) == [TokenType.STRING]
        assert toks[0].value == "'hello'"

    def test_empty_string(self):
        toks = tokenize('""')
        assert types(toks) == [TokenType.STRING]
        assert toks[0].value == '""'

    def test_string_with_escape(self):
        toks = tokenize(r'"hello\nworld"')
        assert types(toks) == [TokenType.STRING]
        assert toks[0].value == '"hello\\nworld"'

    def test_string_with_escaped_quote(self):
        toks = tokenize(r'"he said \"hi\""')
        assert types(toks) == [TokenType.STRING]
        assert toks[0].value == '"he said \\"hi\\""'

    def test_unterminated_string_double(self):
        lexer = make_lexer('"unterminated')
        with pytest.raises(LexerError, match="Unterminated string"):
            lexer.tokenize()

    def test_unterminated_string_single(self):
        lexer = make_lexer("'unterminated")
        with pytest.raises(LexerError, match="Unterminated string"):
            lexer.tokenize()

    def test_unterminated_string_newline(self):
        lexer = make_lexer('"hello\nworld"')
        with pytest.raises(LexerError, match="Unterminated string"):
            lexer.tokenize()


class TestLexerOperators:
    def test_plus(self):
        assert types("+") == [TokenType.PLUS]

    def test_minus(self):
        assert types("-") == [TokenType.MINUS]

    def test_star(self):
        assert types("*") == [TokenType.STAR]

    def test_slash(self):
        assert types("/") == [TokenType.SLASH]

    def test_percent(self):
        assert types("%") == [TokenType.PERCENT]

    def test_equality(self):
        assert types("==") == [TokenType.EQ_EQ]

    def test_not_equal(self):
        assert types("!=") == [TokenType.BANG_EQ]

    def test_bang(self):
        assert types("!") == [TokenType.BANG]

    def test_less_than(self):
        assert types("<") == [TokenType.LT]

    def test_greater_than(self):
        assert types(">") == [TokenType.GT]

    def test_less_equal(self):
        assert types("<=") == [TokenType.LT_EQ]

    def test_greater_equal(self):
        assert types(">=") == [TokenType.GT_EQ]

    def test_bitwise_shift_left(self):
        assert types("<<") == [TokenType.LT_LT]

    def test_bitwise_shift_right(self):
        assert types(">>") == [TokenType.GT_GT]

    def test_logical_and(self):
        assert types("&&") == [TokenType.AMPER_AMPER]

    def test_logical_or(self):
        assert types("||") == [TokenType.PIPE_PIPE]

    def test_null_coalesce(self):
        assert types("??") == [TokenType.QUESTION_QUESTION]

    def test_optional_chain(self):
        assert types("?.") == [TokenType.QUESTION_DOT]

    def test_arrow(self):
        assert types("->") == [TokenType.ARROW]

    def test_fat_arrow(self):
        assert types("=>") == [TokenType.FAT_ARROW]

    def test_range(self):
        assert types("..") == [TokenType.DOT_DOT]

    def test_range_inclusive(self):
        assert types("..=") == [TokenType.DOT_DOT_EQ]

    def test_spread(self):
        assert types("...") == [TokenType.DOT_DOT_DOT]

    def test_dot(self):
        assert types(".") == [TokenType.DOT]

    def test_comma(self):
        assert types(",") == [TokenType.COMMA]

    def test_semicolon(self):
        assert types(";") == [TokenType.SEMICOLON]

    def test_colon(self):
        assert types(":") == [TokenType.COLON]

    def test_parens(self):
        assert types("()") == [TokenType.LPAREN, TokenType.RPAREN]

    def test_brackets(self):
        assert types("[]") == [TokenType.LBRACKET, TokenType.RBRACKET]

    def test_braces(self):
        assert types("{}") == [TokenType.LBRACE, TokenType.RBRACE]

    def test_at(self):
        assert types("@") == [TokenType.AT]

    def test_tilde(self):
        assert types("~") == [TokenType.TILDE]

    def test_caret(self):
        assert types("^") == [TokenType.CARET]

    def test_ampersand(self):
        assert types("&") == [TokenType.AMPERSAND]

    def test_pipe(self):
        assert types("|") == [TokenType.PIPE]

    def test_question(self):
        assert types("?") == [TokenType.QUESTION]

    def test_assign(self):
        assert types("=") == [TokenType.EQ]

    def test_plus_assign(self):
        assert types("+=") == [TokenType.PLUS_EQ]

    def test_minus_assign(self):
        assert types("-=") == [TokenType.MINUS_EQ]

    def test_star_assign(self):
        assert types("*=") == [TokenType.STAR_EQ]

    def test_slash_assign(self):
        assert types("/=") == [TokenType.SLASH_EQ]

    def test_percent_assign(self):
        assert types("%=") == [TokenType.PERCENT_EQ]

    def test_star_star(self):
        assert types("**") == [TokenType.STAR_STAR]

    def test_star_star_assign(self):
        assert types("**=") == [TokenType.STAR_STAR_EQ]

    def test_ampersand_assign(self):
        assert types("&=") == [TokenType.AMPER_EQ]

    def test_pipe_assign(self):
        assert types("|=") == [TokenType.PIPE_EQ]

    def test_caret_assign(self):
        assert types("^=") == [TokenType.CARET_EQ]

    def test_and_assign(self):
        assert types("&&=") == [TokenType.AMPER_AMPER]

    def test_or_assign(self):
        assert types("||=") == [TokenType.PIPE_PIPE]

    def test_null_coalesce_assign(self):
        assert types("??=") == [TokenType.QUESTION_QUESTION_EQ]


class TestLexerLongestMatch:
    def test_range_before_dot(self):
        toks = tokenize("..")
        assert len(toks) >= 2
        assert toks[0].value == ".."
        assert toks[0].type == TokenType.DOT_DOT

    def test_spread_before_range(self):
        toks = tokenize("...")
        assert toks[0].value == "..."
        assert toks[0].type == TokenType.DOT_DOT_DOT

    def test_range_inclusive(self):
        toks = tokenize("..=")
        assert toks[0].value == "..="
        assert toks[0].type == TokenType.DOT_DOT_EQ

    def test_star_star_before_star(self):
        toks = tokenize("**")
        assert toks[0].value == "**"
        assert toks[0].type == TokenType.STAR_STAR

    def test_star_star_eq_longest(self):
        toks = tokenize("**=")
        assert toks[0].value == "**="
        assert toks[0].type == TokenType.STAR_STAR_EQ

    def test_and_and_before_and(self):
        toks = tokenize("&&")
        assert toks[0].value == "&&"

    def test_and_and_assign(self):
        toks = tokenize("&&=")
        assert toks[0].value == "&&="

    def test_or_or_assign(self):
        toks = tokenize("||=")
        assert toks[0].value == "||="

    def test_arrow_not_greater(self):
        toks = tokenize("->")
        assert toks[0].value == "->"
        assert toks[0].type == TokenType.ARROW


class TestLexerIllegalCharacter:
    def test_illegal_char(self):
        toks = tokenize("#")
        assert types(toks) == [TokenType.ILLEGAL]
        assert toks[0].value == "#"

    def test_illegal_char_position(self):
        lexer = make_lexer(" #")
        toks = lexer.tokenize()
        illegal = [t for t in toks if t.type == TokenType.ILLEGAL]
        assert len(illegal) == 1
        assert illegal[0].col == 2

    def test_multiple_illegal(self):
        toks = tokenize("@#")
        # @ is valid (AT), # is illegal
        assert toks[0].type == TokenType.AT
        assert toks[1].type == TokenType.ILLEGAL


class TestLexerTokenizeInteractive:
    def test_interactive_single_token(self):
        lexer = make_lexer("hello")
        tok = lexer.tokenize_interactive()
        assert tok.type == TokenType.IDENTIFIER
        assert tok.value == "hello"

    def test_interactive_skips_whitespace(self):
        lexer = make_lexer("   hello")
        tok = lexer.tokenize_interactive()
        assert tok.value == "hello"

    def test_interactive_eof(self):
        lexer = make_lexer("")
        tok = lexer.tokenize_interactive()
        assert tok.type == TokenType.EOF

    def test_interactive_comment_returns_eof(self):
        lexer = make_lexer("// comment")
        tok = lexer.tokenize_interactive()
        assert tok.type == TokenType.EOF


class TestLexerCheckpoint:
    def test_checkpoint_restore(self):
        lexer = make_lexer("hello world")
        cp = lexer.checkpoint()
        tok1 = lexer.tokenize_interactive()
        assert tok1.value == "hello"
        lexer.restore(cp)
        tok2 = lexer.tokenize_interactive()
        assert tok2.value == "hello"

    def test_checkpoint_restore_middle(self):
        lexer = make_lexer("a b c")
        lexer.tokenize_interactive()
        lexer.tokenize_interactive()
        cp = lexer.checkpoint()
        tok1 = lexer.tokenize_interactive()
        assert tok1.value == "c"
        lexer.restore(cp)
        tok2 = lexer.tokenize_interactive()
        assert tok2.value == "c"

    def test_checkpoint_returns_state(self):
        lexer = make_lexer("test")
        cp = lexer.checkpoint()
        assert len(cp) == 3
        pos, line, col = cp
        assert pos == 0
        assert line == 1
        assert col == 1

    def test_checkpoint_restore_after_advance(self):
        lexer = make_lexer("abc")
        lexer._advance()
        cp = lexer.checkpoint()
        lexer._advance()
        lexer._advance()
        lexer.restore(cp)
        assert lexer.pos == 1
        assert lexer.current_char == 'b'


class TestLexerPeekToken:
    def test_peek_next_token(self):
        lexer = make_lexer("a b")
        peeked = lexer.peek_token(0)
        assert peeked is not None
        assert peeked.value == "a"
        toks = lexer.tokenize()
        assert toks[0].value == "a"

    def test_peek_offset(self):
        lexer = make_lexer("a b c")
        peeked = lexer.peek_token(1)
        assert peeked is not None
        assert peeked.value == "b"

    def test_peek_does_not_consume(self):
        lexer = make_lexer("hello world")
        p1 = lexer.peek_token(0)
        p2 = lexer.peek_token(0)
        assert p1 == p2
        assert lexer.pos == 0

    def test_peek_eof(self):
        lexer = make_lexer("")
        tok = lexer.peek_token(0)
        assert tok is not None
        assert tok.type == TokenType.EOF

    def test_peek_past_end(self):
        lexer = make_lexer("a")
        tok = lexer.peek_token(5)
        assert tok is not None
        assert tok.type == TokenType.EOF


class TestLexerReset:
    def test_reset_restores_state(self):
        lexer = make_lexer("hello world")
        lexer.tokenize()
        lexer.reset()
        assert lexer.pos == 0
        assert lexer.line == 1
        assert lexer.col == 1
        assert lexer.current_char == 'h'
        assert lexer.tokens == []
        assert lexer.errors == []

    def test_reset_allows_retokenize(self):
        lexer = make_lexer("hello")
        t1 = lexer.tokenize()
        lexer.reset()
        t2 = lexer.tokenize()
        assert len(t1) == len(t2)
        assert t1[0] == t2[0]


class TestLexerErrors:
    def test_add_error(self):
        lexer = make_lexer("test")
        lexer.add_error("Something went wrong", "Check your syntax")
        assert lexer.has_errors() is True
        errs = lexer.get_errors()
        assert len(errs) == 1
        assert errs[0].message == "Something went wrong"

    def test_get_errors_returns_copy(self):
        lexer = make_lexer("test")
        lexer.add_error("err")
        errs = lexer.get_errors()
        errs.clear()
        assert lexer.has_errors() is True

    def test_no_errors_initially(self):
        lexer = make_lexer("test")
        assert lexer.has_errors() is False
        assert lexer.get_errors() == []

    def test_error_includes_position(self):
        lexer = make_lexer("test")
        lexer.pos = 5
        lexer.line = 2
        lexer.col = 3
        lexer.add_error("msg")
        err = lexer.get_errors()[0]
        assert err.line == 2
        assert err.col == 3

    def test_errors_cleared_on_reset(self):
        lexer = make_lexer("test")
        lexer.add_error("err")
        lexer.reset()
        assert lexer.has_errors() is False


class TestLexerSourcePosition:
    def test_get_source_span(self):
        lexer = make_lexer("hello")
        lexer._scan_token()
        start, end = lexer.get_source_span()
        assert start == 0
        assert end == 5

    def test_get_source_position(self):
        lexer = make_lexer("hello\nworld")
        lexer.pos = 8
        lexer.line = 2
        lexer.col = 3
        pos = lexer.get_source_position()
        assert pos == (8, 2, 3)

    def test_token_positions(self):
        lexer = make_lexer("  hello\n  world")
        toks = [t for t in lexer.tokenize() if t.type not in (TokenType.EOF,)]
        hello = toks[0]
        world = toks[2]
        assert hello.line == 1
        assert hello.col == 3
        assert world.line == 2
        assert world.col == 3


class TestLexerComplexPrograms:
    def test_simple_let_statement(self):
        code = "let x = 42"
        toks = tokenize(code)
        vals = [(t.type, t.value) for t in toks if t.type not in (TokenType.EOF,)]
        assert vals == [
            (TokenType.KEYWORD, "let"),
            (TokenType.IDENTIFIER, "x"),
            (TokenType.EQ, "="),
            (TokenType.INTEGER, "42"),
        ]

    def test_function_declaration(self):
        code = "fn add(a, b) -> a + b"
        toks = tokenize(code)
        vals = [(t.type, t.value) for t in toks if t.type not in (TokenType.EOF,)]
        expected = [
            (TokenType.KEYWORD, "fn"),
            (TokenType.IDENTIFIER, "add"),
            (TokenType.LPAREN, "("),
            (TokenType.IDENTIFIER, "a"),
            (TokenType.COMMA, ","),
            (TokenType.IDENTIFIER, "b"),
            (TokenType.RPAREN, ")"),
            (TokenType.ARROW, "->"),
            (TokenType.IDENTIFIER, "a"),
            (TokenType.PLUS, "+"),
            (TokenType.IDENTIFIER, "b"),
        ]
        assert vals == expected

    def test_if_else(self):
        code = "if x > 0 { return x }"
        toks = tokenize(code)
        vals = [(t.type, t.value) for t in toks if t.type not in (TokenType.EOF,)]
        expected = [
            (TokenType.KEYWORD, "if"),
            (TokenType.IDENTIFIER, "x"),
            (TokenType.GT, ">"),
            (TokenType.INTEGER, "0"),
            (TokenType.LBRACE, "{"),
            (TokenType.KEYWORD, "return"),
            (TokenType.IDENTIFIER, "x"),
            (TokenType.RBRACE, "}"),
        ]
        assert vals == expected

    def test_arithmetic_with_comments(self):
        code = """// this computes the answer
let result = 42 + 3  /* add three */
"""
        toks = tokenize(code)
        vals = [(t.type, t.value) for t in toks if t.type not in (TokenType.EOF, TokenType.NEWLINE)]
        expected = [
            (TokenType.KEYWORD, "let"),
            (TokenType.IDENTIFIER, "result"),
            (TokenType.EQ, "="),
            (TokenType.INTEGER, "42"),
            (TokenType.PLUS, "+"),
            (TokenType.INTEGER, "3"),
        ]
        assert vals == expected

    def test_string_and_number_mix(self):
        code = 'print("value: " + 123)'
        toks = tokenize(code)
        vals = [(t.type, t.value) for t in toks if t.type not in (TokenType.EOF,)]
        expected = [
            (TokenType.IDENTIFIER, "print"),
            (TokenType.LPAREN, "("),
            (TokenType.STRING, '"value: "'),
            (TokenType.PLUS, "+"),
            (TokenType.INTEGER, "123"),
            (TokenType.RPAREN, ")"),
        ]
        assert vals == expected

    def test_complex_operators(self):
        code = "a **= b ?? c &&= d ||= e"
        toks = tokenize(code)
        vals = [(t.type, t.value) for t in toks if t.type not in (TokenType.EOF,)]
        expected = [
            (TokenType.IDENTIFIER, "a"),
            (TokenType.STAR_STAR_EQ, "**="),
            (TokenType.IDENTIFIER, "b"),
            (TokenType.QUESTION_QUESTION, "??"),
            (TokenType.IDENTIFIER, "c"),
            (TokenType.AMPER_AMPER, "&&="),
            (TokenType.IDENTIFIER, "d"),
            (TokenType.PIPE_PIPE, "||="),
            (TokenType.IDENTIFIER, "e"),
        ]
        assert vals == expected

    def test_range_and_spread(self):
        code = "let r = 0..10\nlet arr = [1, 2, 3...]"
        toks = tokenize(code)
        vals = [(t.type, t.value) for t in toks if t.type not in (TokenType.EOF, TokenType.NEWLINE)]
        expected = [
            (TokenType.KEYWORD, "let"),
            (TokenType.IDENTIFIER, "r"),
            (TokenType.EQ, "="),
            (TokenType.INTEGER, "0"),
            (TokenType.DOT_DOT, ".."),
            (TokenType.INTEGER, "10"),
            (TokenType.KEYWORD, "let"),
            (TokenType.IDENTIFIER, "arr"),
            (TokenType.EQ, "="),
            (TokenType.LBRACKET, "["),
            (TokenType.INTEGER, "1"),
            (TokenType.COMMA, ","),
            (TokenType.INTEGER, "2"),
            (TokenType.COMMA, ","),
            (TokenType.INTEGER, "3"),
            (TokenType.DOT_DOT_DOT, "..."),
            (TokenType.RBRACKET, "]"),
        ]
        assert vals == expected


class TestLexerEdgeCases:
    def test_only_newlines(self):
        toks = tokenize("\n\n\n")
        assert len([t for t in toks if t.type == TokenType.NEWLINE]) == 3

    def test_identifier_starting_with_dollar(self):
        toks = tokenize("$")
        assert types(toks) == [TokenType.IDENTIFIER]
        assert toks[0].value == "$"

    def test_identifier_dollar_followed_by_alpha(self):
        toks = tokenize("$foo")
        assert toks[0].value == "$foo"

    def test_block_comment_immediately_closed(self):
        toks = tokenize("/**/")
        assert types(toks) == []

    def test_line_comment_at_eof(self):
        toks = tokenize("//")
        assert types(toks) == []

    def test_string_with_escaped_backslash(self):
        toks = tokenize(r'"hello\\world"')
        assert toks[0].value == '"hello\\\\world"'

    def test_keyword_list(self):
        assert "let" in KEYWORDS
        assert "fn" in KEYWORDS
        assert "return" in KEYWORDS
        assert "if" in KEYWORDS
        assert "else" in KEYWORDS
        assert "for" in KEYWORDS
        assert "while" in KEYWORDS
        assert "true" in KEYWORDS
        assert "false" in KEYWORDS
        assert "null" in KEYWORDS


class TestLexerRepr:
    def test_repr(self):
        lexer = make_lexer("hello")
        r = repr(lexer)
        assert "Lexer" in r
        assert "1:1" in r


class TestLexerTokenProperties:
    def test_is_keyword(self):
        t = Token(TokenType.IDENTIFIER, "fn", 1, 1, 2)
        assert t.is_keyword() is True

    def test_is_keyword_non_keyword(self):
        t = Token(TokenType.IDENTIFIER, "foo", 1, 1, 3)
        assert t.is_keyword() is False

    def test_is_operator(self):
        t = Token(TokenType.PLUS, "+", 1, 1, 1)
        assert t.is_operator() is True

    def test_is_operator_non_operator(self):
        t = Token(TokenType.IDENTIFIER, "x", 1, 1, 1)
        assert t.is_operator() is False

    def test_is_comparison(self):
        t = Token(TokenType.EQ_EQ, "==", 1, 1, 2)
        assert t.is_comparison() is True

    def test_is_assignment(self):
        t = Token(TokenType.PLUS_EQ, "+=", 1, 1, 2)
        assert t.is_assignment() is True

    def test_to_dict(self):
        t = Token(TokenType.INTEGER, "42", 1, 5, 2)
        d = t.to_dict()
        assert d["type"] == "INTEGER"
        assert d["value"] == "42"
        assert d["line"] == 1
        assert d["column"] == 5
        assert d["length"] == 2

    def test_token_equality(self):
        t1 = Token(TokenType.IDENTIFIER, "x", 1, 1, 1)
        t2 = Token(TokenType.IDENTIFIER, "x", 2, 5, 1)
        assert t1 == t2
        assert t1 is not t2

    def test_token_inequality(self):
        t1 = Token(TokenType.IDENTIFIER, "x", 1, 1, 1)
        t2 = Token(TokenType.IDENTIFIER, "y", 1, 1, 1)
        assert t1 != t2

    def test_token_hash(self):
        t1 = Token(TokenType.INTEGER, "42", 1, 1, 2)
        t2 = Token(TokenType.INTEGER, "42", 2, 5, 2)
        assert hash(t1) == hash(t2)


class TestKeywordCompleteness:
    def test_all_roadmap_keywords(self):
        roadmap_keywords = {
            "let", "const", "fn", "return", "if", "else", "for", "while",
            "in", "break", "continue", "true", "false", "null", "import",
            "export", "from", "class", "extends", "new", "this", "super",
            "static", "async", "await", "try", "catch", "finally", "throw",
            "match", "case", "type", "interface", "enum", "as", "is", "of",
            "yield", "page", "component", "style", "route", "ai", "not",
            "and", "or", "where", "on", "send", "find", "show", "give", "with",
        }
        assert KEYWORDS == roadmap_keywords

    def test_each_keyword_tokenizes_as_keyword(self):
        for kw in KEYWORDS:
            toks = tokenize(kw)
            assert toks[0].type == TokenType.KEYWORD, f"{kw!r} should be KEYWORD, got {toks[0].type}"
            assert toks[0].value == kw

    def test_keyword_case_sensitive_all(self):
        for kw in KEYWORDS:
            upper = kw.upper()
            if upper != kw:
                toks = tokenize(upper)
                assert toks[0].type == TokenType.IDENTIFIER, f"{upper!r} should be IDENTIFIER, got {toks[0].type}"
            title = kw.title()
            if title != kw and title.isidentifier():
                toks = tokenize(title)
                assert toks[0].type == TokenType.IDENTIFIER, f"{title!r} should be IDENTIFIER, got {toks[0].type}"

    def test_is_keyword_function(self):
        from nova.lexer.tokens import is_keyword
        assert is_keyword("let") is True
        assert is_keyword("fn") is True
        assert is_keyword("not_a_keyword") is False
        assert is_keyword("") is False
        assert is_keyword("Let") is False  # case sensitive

    def test_keyword_in_expression(self):
        code = "let x = if + return - true * false / null"
        toks = tokenize(code)
        types_list = [t.type for t in toks if t.type != TokenType.EOF]
        for t in toks:
            if t.type == TokenType.KEYWORD:
                assert t.value in KEYWORDS
        keyword_tokens = [t for t in toks if t.type == TokenType.KEYWORD]
        assert len(keyword_tokens) == 6
        assert keyword_tokens[0].value == "let"
        assert keyword_tokens[1].value == "if"
        assert keyword_tokens[2].value == "return"
        assert keyword_tokens[3].value == "true"
        assert keyword_tokens[4].value == "false"
        assert keyword_tokens[5].value == "null"


class TestUnicodeIdentifiers:
    def test_accented_identifier(self):
        toks = tokenize("café")
        assert types(toks) == [TokenType.IDENTIFIER]
        assert toks[0].value == "café"

    def test_unicode_identifier_with_underscore(self):
        toks = tokenize("über_ cool")
        assert types(toks) == [TokenType.IDENTIFIER, TokenType.IDENTIFIER]
        assert toks[0].value == "über_"
        assert toks[1].value == "cool"

    def test_cyrillic_identifier(self):
        toks = tokenize("привет")
        assert types(toks) == [TokenType.IDENTIFIER]
        assert toks[0].value == "привет"

    def test_chinese_identifier(self):
        toks = tokenize("变量")
        assert types(toks) == [TokenType.IDENTIFIER]
        assert toks[0].value == "变量"

    def test_japanese_identifier(self):
        toks = tokenize("変数名")
        assert types(toks) == [TokenType.IDENTIFIER]
        assert toks[0].value == "変数名"

    def test_unicode_with_numbers(self):
        toks = tokenize("πr²")
        assert types(toks) == [TokenType.IDENTIFIER]
        assert toks[0].value == "πr²"

    def test_mixed_unicode_ascii_identifier(self):
        toks = tokenize("get_naïve_value")
        assert types(toks) == [TokenType.IDENTIFIER]
        assert toks[0].value == "get_naïve_value"

    def test_unicode_identifier_dollar_prefix(self):
        toks = tokenize("$über")
        assert types(toks) == [TokenType.IDENTIFIER]
        assert toks[0].value == "$über"

    def test_unicode_identifier_positions(self):
        lexer = make_lexer("  ñoño")
        toks = lexer.tokenize()
        tok = toks[0]
        assert tok.line == 1
        assert tok.col == 3
        assert tok.value == "ñoño"


class TestUnderscoreIdentifier:
    def test_standalone_underscore(self):
        toks = tokenize("_")
        assert types(toks) == [TokenType.IDENTIFIER]
        assert toks[0].value == "_"

    def test_underscore_in_expression(self):
        toks = tokenize("_ = 42")
        assert [t.type for t in toks if t.type != TokenType.EOF] == [
            TokenType.IDENTIFIER, TokenType.EQ, TokenType.INTEGER
        ]
        assert toks[0].value == "_"

    def test_underscore_with_alphanum(self):
        toks = tokenize("_my_var_1")
        assert types(toks) == [TokenType.IDENTIFIER]
        assert toks[0].value == "_my_var_1"

    def test_double_underscore(self):
        toks = tokenize("__init__")
        assert types(toks) == [TokenType.IDENTIFIER]
        assert toks[0].value == "__init__"

    def test_underscore_between_keywords(self):
        toks = tokenize("let _ = fn")
        assert [t.type for t in toks if t.type != TokenType.EOF] == [
            TokenType.KEYWORD, TokenType.IDENTIFIER, TokenType.EQ, TokenType.KEYWORD
        ]
        assert toks[1].value == "_"
