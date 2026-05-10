class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
    
    def parse(self):
        from nova.ast.builder import ASTBuilder
        builder = ASTBuilder(self.tokens)
        return builder.build()