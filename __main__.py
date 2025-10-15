from src.lex import *
from src.parser import *
from src.emit import *
import sys

def main():
    print("My Compliler")

    # Ensure that there are 2 system arguments
    if len(sys.argv) != 2:
        sys.exit("[Error] Compiler needs source file as argument")

    # Open the source file and read it
    with open(sys.argv[1], "r") as inputFile:
        source = inputFile.read()
    
    # Initialise lexer and parser
    lexer = Lexer(source)
    emitter = Emitter("files/out.c")
    parser = Parser(lexer, emitter)

    parser.program()
    emitter.writeFile()
    print("Parsing is complete") 

if __name__ == "__main__":
    main()

