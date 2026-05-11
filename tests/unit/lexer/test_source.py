import pytest
from nova.lexer.source import SourceFile, SourcePosition, SourceSpan, SourceLine


class TestSourceFile:
    def test_from_string_basic(self):
        source = SourceFile.from_string("hello world")
        assert source.content == "hello world"
        assert source.filename == "<string>"
        assert len(source) == 11

    def test_from_string_with_filename(self):
        source = SourceFile.from_string("test content", "test.nv")
        assert source.filename == "test.nv"

    def test_get_position_basic(self):
        source = SourceFile.from_string("hello\nworld\ntest")
        pos = source.get_position(0)
        assert pos.line == 1
        assert pos.col == 1
        assert pos.offset == 0

    def test_get_position_newline(self):
        source = SourceFile.from_string("hello\nworld")
        pos = source.get_position(6)
        assert pos.line == 2
        assert pos.col == 1

    def test_get_line(self):
        source = SourceFile.from_string("line1\nline2\nline3")
        assert source.get_line(1) == "line1"
        assert source.get_line(2) == "line2"
        assert source.get_line(3) == "line3"
        assert source.get_line(99) == ""

    def test_get_line_count(self):
        source = SourceFile.from_string("a\nb\nc")
        assert source.get_line_count() == 3

    def test_has_shebang(self):
        source = SourceFile.from_string("#!/usr/bin/env nova\ncode")
        assert source.has_shebang() is True
        assert source.get_shebang() == "/usr/bin/env nova"

    def test_no_shebang(self):
        source = SourceFile.from_string("normal code")
        assert source.has_shebang() is False
        assert source.get_shebang() is None

    def test_strip_shebang(self):
        source = SourceFile.from_string("#!/usr/bin/env nova\ncode")
        content = source.strip_shebang()
        assert content == "code"

    def test_get_span(self):
        source = SourceFile.from_string("hello world")
        span = source.get_span(0, 5)
        assert span.start.line == 1
        assert span.start.col == 1
        assert source.get_text(span) == "hello"

    def test_lines(self):
        source = SourceFile.from_string("a\nb\nc")
        assert len(source.lines) == 3
        assert source.lines[0].content == "a"
        assert source.lines[0].number == 1

    def test_get_offset(self):
        source = SourceFile.from_string("hello\nworld")
        assert source.get_offset(1, 1) == 0
        assert source.get_offset(1, 3) == 2
        assert source.get_offset(2, 1) == 6

    def test_get_text_slice(self):
        source = SourceFile.from_string("hello world")
        assert source.get_text_slice(0, 5) == "hello"

    def test_empty_file(self):
        source = SourceFile.from_string("")
        assert len(source) == 0
        assert source.get_line_count() == 0
        assert source.get_position(0) == SourcePosition(1, 1, 0)


class TestSourcePosition:
    def test_position_creation(self):
        pos = SourcePosition(line=1, col=5, offset=4)
        assert str(pos) == "1:5"

    def test_position_comparison(self):
        p1 = SourcePosition(1, 1, 0)
        p2 = SourcePosition(2, 1, 10)
        assert p1 < p2

    def test_position_equality(self):
        p1 = SourcePosition(1, 5, 4)
        p2 = SourcePosition(1, 5, 4)
        assert p1 == p2


class TestSourceSpan:
    def test_span_creation(self):
        start = SourcePosition(1, 1, 0)
        end = SourcePosition(1, 6, 5)
        span = SourceSpan(start, end)
        assert span.length == 5
        assert str(span) == "1:1..1:6"


class TestSourceFileFileOperations:
    def test_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            SourceFile.from_file("nonexistent.nv")

    def test_from_lines(self):
        source = SourceFile.from_lines(["line1", "line2"])
        assert source.get_line(1) == "line1"
        assert source.get_line(2) == "line2"

    def test_indentation(self):
        source = SourceFile.from_string("  indented\n    double")
        assert source.get_indentation(1) == "  "
        assert source.get_indentation(2) == "    "

    def test_indent_level(self):
        source = SourceFile.from_string("  level1\n    level2\nnot")
        assert source.get_indent_level(1) == 1
        assert source.get_indent_level(2) == 2
        assert source.get_indent_level(3) == 0

    def test_lines_with_pattern(self):
        source = SourceFile.from_string("hello\nworld\nhello again")
        matches = source.lines_with_pattern("hello")
        assert len(matches) == 2
        assert matches[0] == (1, "hello")

    def test_context(self):
        source = SourceFile.from_string("line1\nline2\nline3\nline4\nline5")
        context = source.get_context(SourcePosition(3, 1, 10), context_lines=1)
        assert len(context) == 3
        assert context[0] == (2, "line2")
        assert context[1] == (3, "line3")
        assert context[2] == (4, "line4")