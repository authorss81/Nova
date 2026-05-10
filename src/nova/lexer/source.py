"""
Source File Handler for Nova

Handles reading and tracking source code files with line/column tracking.
Supports UTF-8 encoding and shebang lines.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class SourcePosition:
    """Represents a position in the source code."""
    line: int
    col: int
    offset: int
    
    def __str__(self) -> str:
        return f"{self.line}:{self.col}"


@dataclass
class SourceSpan:
    """Represents a span of source code."""
    start: SourcePosition
    end: SourcePosition
    
    def __str__(self) -> str:
        return f"{self.start}..{self.end}"


class SourceFile:
    """Represents a Nova source file with position tracking."""
    
    def __init__(self, content: str, filename: str = "<unknown>"):
        self.content = content
        self.filename = filename
        self.lines = content.split('\n')
        self._line_offsets: list[int] = self._compute_line_offsets()
    
    @classmethod
    def from_file(cls, filepath: str) -> "SourceFile":
        """Read a .nv file with UTF-8 encoding."""
        path = Path(filepath)
        if not path.exists():
            from nova.errors import NovaError
            raise NovaError(f"File not found: {filepath}", filename=filepath)
        
        content = path.read_text(encoding='utf-8')
        return cls(content, str(path))
    
    @classmethod
    def from_string(cls, content: str, filename: str = "<string>") -> "SourceFile":
        """Create a SourceFile from a string."""
        return cls(content, filename)
    
    def _compute_line_offsets(self) -> list[int]:
        """Compute the byte offset for each line start."""
        offsets = [0]
        for i, line in enumerate(self.lines[:-1]):
            offsets.append(offsets[i] + len(line) + 1)
        return offsets
    
    def get_position(self, offset: int) -> SourcePosition:
        """Convert a byte offset to line/col position."""
        if offset < 0:
            offset = 0
        if offset > len(self.content):
            offset = len(self.content)
        
        line = 0
        for i, line_offset in enumerate(self._line_offsets):
            if line_offset > offset:
                break
            line = i
        
        col = offset - self._line_offsets[line]
        return SourcePosition(line + 1, col + 1, offset)
    
    def get_span(self, start: int, end: int) -> SourceSpan:
        """Get a span from start to end offset."""
        return SourceSpan(self.get_position(start), self.get_position(end))
    
    def get_line(self, line_num: int) -> str:
        """Get a specific line (1-indexed)."""
        if 1 <= line_num <= len(self.lines):
            return self.lines[line_num - 1]
        return ""
    
    def get_line_count(self) -> int:
        """Get total number of lines."""
        return len(self.lines)
    
    def has_shebang(self) -> bool:
        """Check if file starts with a shebang line."""
        return self.content.startswith('#!')
    
    def strip_shebang(self) -> str:
        """Remove shebang line if present."""
        if self.has_shebang():
            first_newline = self.content.find('\n')
            if first_newline != -1:
                return self.content[first_newline + 1:]
        return self.content
    
    def get_text(self, span: SourceSpan) -> str:
        """Extract text for a given span."""
        start_offset = span.start.offset
        end_offset = span.end.offset
        return self.content[start_offset:end_offset]
    
    def __len__(self) -> int:
        return len(self.content)
    
    def __repr__(self) -> str:
        return f"SourceFile(filename={self.filename!r}, lines={len(self.lines)})"