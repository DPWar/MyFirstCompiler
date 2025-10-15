

class Emitter():
    def __init__(self, fullpath):
        self.fullpath = fullpath # Output file
        self.header = "" # Initialise header 
        self.code = "" # Initialise code

    # Used to emit code, when more code is expected after
    def emit(self, code):
        self.code += code

    # Used to emit code that is expected to be one line
    def emitLine(self, code):
        self.code += code + "\n"

    # Used to emit a header such as libraries 
    def headerLine(self, code):
        self.header += code + "\n"

    # Writes the lines to full path
    def writeFile(self):
        with open(self.fullpath, "w") as outputFile:
            outputFile.write(self.header + self.code)
