class JSCodegen:
    def __init__(self, target: str = "esm"):
        self.target = target
    
    def generate(self, ast):
        return "// Nova JavaScript output\nconsole.log('Hello from Nova!');"