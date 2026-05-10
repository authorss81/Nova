class ASTBuilder:
    def __init__(self, tokens):
        self.tokens = tokens
    
    def build(self):
        from nova.ast.nodes import Program
        return Program(body=[])