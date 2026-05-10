from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Node:
    kind: str
    span: Optional[tuple] = None


@dataclass
class Program(Node):
    body: List[Node]
    
    def __post_init__(self):
        self.kind = "Program"


@dataclass
class Identifier(Node):
    name: str
    
    def __post_init__(self):
        self.kind = "Identifier"


@dataclass
class Literal(Node):
    value: any
    raw: str
    
    def __post_init__(self):
        self.kind = "Literal"