from nova.errors import NovaExit

class REPL:
    def run(self):
        while True:
            try:
                line = input("nova> ")
                if line == ".exit":
                    break
                if line == ".help":
                    print("Nova REPL help")
                    continue
                print(f"REPL: {line}")
            except EOFError:
                break