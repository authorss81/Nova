"""
Source File Handler for Nova

Handles reading and tracking source code files with line/column tracking.
Supports UTF-8 encoding, shebang detection, and various file operations.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, List, Callable
from enum import Enum


class Encoding(Enum):
    UTF8 = "utf-8"
    UTF8_BOM = "utf-8-sig"
    UTF16 = "utf-16"
    ASCII = "ascii"


@dataclass(frozen=True)
class SourcePosition:
    """Immutable position in source code."""
    line: int
    col: int
    offset: int
    
    def __str__(self) -> str:
        return f"{self.line}:{self.col}"
    
    def __repr__(self) -> str:
        return f"SourcePosition(line={self.line}, col={self.col}, offset={self.offset})"
    
    def __lt__(self, other: "SourcePosition") -> bool:
        if self.line != other.line:
            return self.line < other.line
        return self.col < other.col
    
    def __le__(self, other: "SourcePosition") -> bool:
        return self == other or self < other
    
    def __gt__(self, other: "SourcePosition") -> bool:
        return other < self
    
    def __ge__(self, other: "SourcePosition") -> bool:
        return self == other or other < self


@dataclass(frozen=True)
class SourceSpan:
    """Immutable span from start to end position."""
    start: SourcePosition
    end: SourcePosition
    
    def __str__(self) -> str:
        return f"{self.start}..{self.end}"
    
    def __repr__(self) -> str:
        return f"SourceSpan(start={self.start!r}, end={self.end!r})"
    
    @property
    def length(self) -> int:
        return self.end.offset - self.start.offset


class SourceChange:
    """Represents a change to the source file."""
    
    def __init__(
        self,
        span: SourceSpan,
        old_text: str,
        new_text: str,
        change_type: str = "edit"
    ):
        self.span = span
        self.old_text = old_text
        self.new_text = new_text
        self.change_type = change_type
    
    def __repr__(self) -> str:
        return f"SourceChange({self.change_type}, {self.span})"


@dataclass
class SourceLine:
    """Represents a single line in source code."""
    number: int
    content: str
    start_offset: int
    end_offset: int
    indentation: str = ""
    is_blank: bool = False
    
    def __post_init__(self):
        if self.content:
            self.indentation = self.content[:len(self.content) - len(self.content.lstrip())]
            self.is_blank = not self.content.strip()
        else:
            self.is_blank = True
    
    @property
    def length(self) -> int:
        return self.end_offset - self.start_offset
    
    def get_span(self) -> SourceSpan:
        return SourceSpan(
            SourcePosition(self.number, 1, self.start_offset),
            SourcePosition(self.number, self.length + 1, self.end_offset)
        )


@dataclass
class SourceFile:
    """Represents a Nova source file with full position tracking and metadata."""
    
    content: str
    filename: str
    lines: List[SourceLine] = field(default_factory=list)
    _line_offsets: List[int] = field(default_factory=list)
    _dirty: bool = False
    _encoding: Encoding = Encoding.UTF8
    _hash: Optional[str] = None
    
    @classmethod
    def from_file(
        cls,
        filepath: str,
        encoding: Optional[str] = None,
        detect_encoding: bool = True
    ) -> "SourceFile":
        """
        Read a .nv file with encoding detection and validation.
        
        Args:
            filepath: Path to the Nova source file
            encoding: Explicit encoding (auto-detected if None)
            detect_encoding: Whether to detect encoding from BOM/file
            
        Returns:
            SourceFile instance with full metadata
            
        Raises:
            FileNotFoundError: If file doesn't exist
            PermissionError: If file cannot be read
            UnicodeDecodeError: If file cannot be decoded
        """
        path = Path(filepath)
        
        if not path.exists():
            raise FileNotFoundError(f"Nova source file not found: {filepath}")
        
        if not path.is_file():
            raise IsADirectoryError(f"Expected file, got directory: {filepath}")
        
        if path.suffix.lower() not in ('.nv', '.nova'):
            import warnings
            warnings.warn(f"File {filepath} does not have .nv extension")
        
        if detect_encoding and encoding is None:
            encoding = cls._detect_encoding(path)
        
        if encoding is None:
            encoding = "utf-8"
        
        content = path.read_text(encoding=encoding)
        
        return cls(
            content=content,
            filename=str(path.absolute()),
            _encoding=Encoding(encoding) if encoding in [e.value for e in Encoding] else Encoding.UTF8
        )
    
    @classmethod
    def from_string(
        cls,
        content: str,
        filename: str = "<string>"
    ) -> "SourceFile":
        """Create a SourceFile from a string with optional filename."""
        return cls(content=content, filename=filename)
    
    @classmethod
    def from_lines(
        cls,
        lines: List[str],
        filename: str = "<lines>"
    ) -> "SourceFile":
        """Create a SourceFile from a list of lines."""
        content = '\n'.join(lines)
        return cls(content=content, filename=filename)
    
    @staticmethod
    def _detect_encoding(path: Path) -> str:
        """Detect file encoding from BOM or content."""
        with open(path, 'rb') as f:
            raw = f.read(4)
        
        if raw.startswith(b'\xef\xbb\xbf'):
            return 'utf-8-sig'
        elif raw.startswith(b'\xff\xfe'):
            return 'utf-16'
        elif raw.startswith(b'\xfe\xff'):
            return 'utf-16'
        
        try:
            raw.decode('utf-8')
            return 'utf-8'
        except UnicodeDecodeError:
            return 'latin-1'
    
    def __post_init__(self, lines=None, _line_offsets=None, _dirty=False, _encoding=None, _hash=None):
        if lines is None:
            self._compute_lines()
        if _line_offsets is None:
            self._line_offsets = self._compute_line_offsets()
        if _hash is None and self.content:
            self._hash = self._compute_hash()
    
    def _compute_lines(self) -> None:
        """Compute line information from content."""
        self.lines = []
        offset = 0
        for i, line_text in enumerate(self.content.split('\n'), start=1):
            line = SourceLine(
                number=i,
                content=line_text,
                start_offset=offset,
                end_offset=offset + len(line_text)
            )
            self.lines.append(line)
            offset += len(line_text) + 1
    
    def _compute_line_offsets(self) -> List[int]:
        """Compute the byte offset for each line start."""
        offsets = [0]
        for i, line in enumerate(self.lines[:-1] if self.lines else []):
            offsets.append(line.end_offset + 1)
        return offsets
    
    def _compute_hash(self) -> str:
        """Compute content hash for caching."""
        import hashlib
        return hashlib.sha256(self.content.encode('utf-8')).hexdigest()
    
    def get_hash(self) -> str:
        """Get content hash for change detection."""
        if self._hash is None:
            self._hash = self._compute_hash()
        return self._hash
    
    def get_position(self, offset: int) -> SourcePosition:
        """
        Convert a character offset to line/col position.
        
        Args:
            offset: Character offset in the source (0-indexed)
            
        Returns:
            SourcePosition with line (1-indexed), col (1-indexed), and offset
        """
        if offset < 0:
            offset = 0
        if offset > len(self.content):
            offset = len(self.content)
        
        line = 0
        for i, line_obj in enumerate(self.lines):
            if line_obj.start_offset <= offset < line_obj.end_offset + 1:
                line = i
                break
            if offset < line_obj.end_offset + 1:
                line = i
                break
        else:
            line = len(self.lines) - 1 if self.lines else 0
        
        line_obj = self.lines[line] if line < len(self.lines) else self.lines[-1] if self.lines else None
        
        if line_obj:
            col = offset - line_obj.start_offset + 1
            return SourcePosition(line + 1, max(1, col), offset)
        
        return SourcePosition(line + 1, 1, offset)
    
    def get_offset(self, line: int, col: int) -> int:
        """
        Convert line/col to character offset.
        
        Args:
            line: Line number (1-indexed)
            col: Column number (1-indexed)
            
        Returns:
            Character offset
        """
        if line < 1:
            line = 1
        if line > len(self.lines):
            line = len(self.lines)
        
        line_obj = self.lines[line - 1]
        offset = line_obj.start_offset + col - 1
        
        return max(line_obj.start_offset, min(offset, line_obj.end_offset))
    
    def get_span(self, start: int, end: int) -> SourceSpan:
        """Get a span from start to end offset."""
        return SourceSpan(self.get_position(start), self.get_position(end))
    
    def get_span_from_lines(
        self,
        start_line: int,
        start_col: int,
        end_line: int,
        end_col: int
    ) -> SourceSpan:
        """Get a span from line/col coordinates."""
        start = SourcePosition(start_line, start_col, self.get_offset(start_line, start_col))
        end = SourcePosition(end_line, end_col, self.get_offset(end_line, end_col))
        return SourceSpan(start, end)
    
    def get_line(self, line_num: int) -> str:
        """Get a specific line (1-indexed)."""
        if 1 <= line_num <= len(self.lines):
            return self.lines[line_num - 1].content
        return ""
    
    def get_line_object(self, line_num: int) -> Optional[SourceLine]:
        """Get a SourceLine object for a specific line."""
        if 1 <= line_num <= len(self.lines):
            return self.lines[line_num - 1]
        return None
    
    def get_lines(self, start: int = 1, end: Optional[int] = None) -> List[str]:
        """Get a range of lines."""
        if end is None:
            end = len(self.lines)
        return [self.get_line(i) for i in range(start, min(end + 1, len(self.lines) + 1))]
    
    def get_line_count(self) -> int:
        """Get total number of lines."""
        return len(self.lines)
    
    def get_indentation(self, line_num: int) -> str:
        """Get the indentation of a specific line."""
        line = self.get_line_object(line_num)
        return line.indentation if line else ""
    
    def get_indent_level(self, line_num: int) -> int:
        """Get indentation level (assuming 2 spaces per level)."""
        indent = self.get_indentation(line_num)
        return len(indent) // 2
    
    def has_shebang(self) -> bool:
        """Check if file starts with a shebang line."""
        return self.content.startswith('#!')
    
    def get_shebang(self) -> Optional[str]:
        """Get the shebang line if present."""
        if self.has_shebang():
            first_newline = self.content.find('\n')
            if first_newline != -1:
                return self.content[2:first_newline]
            return self.content[2:]
        return None
    
    def strip_shebang(self) -> str:
        """Remove shebang line if present."""
        if self.has_shebang():
            first_newline = self.content.find('\n')
            if first_newline != -1:
                if first_newline + 1 < len(self.content) and self.content[first_newline + 1] == '\r':
                    return self.content[first_newline + 2:]
                return self.content[first_newline + 1:]
        return self.content
    
    def is_valid_shebang(self) -> bool:
        """Check if shebang is valid for Nova."""
        shebang = self.get_shebang()
        if shebang is None:
            return True
        
        valid_interpreters = ['nova', 'env nova', '/usr/bin/env nova']
        return any(shebang.startswith(vi) for vi in valid_interpreters)
    
    def get_text(self, span: SourceSpan) -> str:
        """Extract text for a given span."""
        start_offset = span.start.offset
        end_offset = span.end.offset
        if start_offset < 0:
            start_offset = 0
        if end_offset > len(self.content):
            end_offset = len(self.content)
        return self.content[start_offset:end_offset]
    
    def get_text_slice(self, start: int, end: int) -> str:
        """Get text between two offsets."""
        return self.content[start:end]
    
    def find(
        self,
        pattern: str,
        start: Optional[int] = None,
        end: Optional[int] = None,
        case_sensitive: bool = True
    ) -> Optional[SourceSpan]:
        """
        Find a pattern in the source.
        
        Returns SourceSpan if found, None otherwise.
        """
        search_start = start or 0
        search_end = end or len(self.content)
        
        search_content = self.content[search_start:search_end]
        
        if not case_sensitive:
            search_content = search_content.lower()
            pattern = pattern.lower()
        
        idx = search_content.find(pattern)
        if idx == -1:
            return None
        
        actual_start = search_start + idx
        actual_end = actual_start + len(pattern)
        
        return self.get_span(actual_start, actual_end)
    
    def find_all(
        self,
        pattern: str,
        case_sensitive: bool = True
    ) -> List[SourceSpan]:
        """Find all occurrences of a pattern."""
        spans = []
        search_content = self.content.lower() if not case_sensitive else self.content
        pattern_lower = pattern.lower() if not case_sensitive else pattern
        
        start = 0
        while True:
            idx = search_content.find(pattern_lower, start)
            if idx == -1:
                break
            span = self.get_span(idx, idx + len(pattern))
            spans.append(span)
            start = idx + 1
        
        return spans
    
    def lines_with_pattern(self, pattern: str) -> List[tuple[int, str]]:
        """Get lines containing a pattern."""
        results = []
        for line in self.lines:
            if pattern in line.content:
                results.append((line.number, line.content))
        return results
    
    def get_context(
        self,
        position: SourcePosition,
        context_lines: int = 2
    ) -> List[tuple[int, str]]:
        """Get lines around a position."""
        start_line = max(1, position.line - context_lines)
        end_line = min(len(self.lines), position.line + context_lines)
        return [(i, self.get_line(i)) for i in range(start_line, end_line + 1)]
    
    def get_snippet(
        self,
        span: SourceSpan,
        max_width: int = 80,
        marker: str = ">>>"
    ) -> str:
        """Get a code snippet with position marker."""
        lines = self.get_text(span).split('\n')
        
        if len(lines) == 1:
            line = lines[0]
            if len(line) > max_width:
                line = line[:max_width - 3] + "..."
            return f"{marker} {line}"
        
        result = [f"{marker} (line {span.start.line})"]
        for line in lines[:5]:
            if len(line) > max_width:
                line = line[:max_width - 3] + "..."
            result.append(f"    {line}")
        
        if len(lines) > 5:
            result.append("    ...")
        
        return '\n'.join(result)
    
    def apply_change(self, change: SourceChange) -> "SourceFile":
        """Apply a change to create a new SourceFile."""
        old_text = self.get_text(change.span)
        
        if old_text != change.old_text:
            import warnings
            warnings.warn("Change old_text doesn't match actual text")
        
        before = self.content[:change.span.start.offset]
        after = self.content[change.span.end.offset:]
        new_content = before + change.new_text + after
        
        return SourceFile(
            content=new_content,
            filename=self.filename,
            _dirty=True
        )
    
    def words(self) -> List[str]:
        """Split content into words (identifiers, operators, literals as tokens)."""
        import re
        pattern = r'\w+|[^\w\s]|\s+'
        return [w for w in re.findall(pattern, self.content) if w.strip()]
    
    def __len__(self) -> int:
        return len(self.content)
    
    def __repr__(self) -> str:
        return f"SourceFile(filename={self.filename!r}, lines={len(self.lines)}, size={len(self.content)} bytes)"
    
    def __str__(self) -> str:
        return f"SourceFile({self.filename}:{len(self.lines)} lines)"