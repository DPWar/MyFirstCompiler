import sys
from src.lex import *
from src.emit import *

# Parser objects keeps track of tokens an validates the grammer
class Parser():
    def __init__(self, lexer, emitter):
        self.lexer = lexer
        self.emitter = emitter
        
        self.symbols = set() # Variables declared so far
        self.labelsDeclared = set() # Labels declared so far
        self.labelsGoToed = set() # Labels goto'ed so far
        
        self.curToken = None
        self.peekToken = None
        self.nextToken()
        self.nextToken() # Call twice because in nextToken, the current token is not got on the first iteration

    # Returns true if the current token matches
    def checkToken(self, kind):
        return kind == self.curToken.kind

    # Returns true if the next token matches
    def checkPeek(self, kind):
        return kind == self.peekToken.kind

    # Tries to match the current tokent, if not an error advance to next token
    # This is used if there is an expected token in a statement, if there is not, throw a syntax error
    def match(self, kind):
        # Try to match the current token
        if not self.checkToken(kind):
            self.abort("Expected " + kind.name + " got " + self.curToken.kind.name)
        self.nextToken()

    # Advances to the next token
    def nextToken(self):
        self.curToken = self.peekToken
        self.peekToken = self.lexer.getToken()

    # Aborts the program if there is an error
    def abort(self, message):
        sys.exit("[Error]" + message)


    # Production Rules
    # program ::= {statement}
    # --- PROGRAM ---
    def program(self):
        # Write headers
        self.emitter.headerLine("#include <stdio.h>")
        self.emitter.headerLine("int main(void){")

        # Skip new lines
        while self.checkToken(TokenType.NEWLINE):
            self.nextToken()

        while not self.checkToken(TokenType.EOF):
            self.statement()

        # After all code has been parsed return - 
        self.emitter.emitLine("return 0")
        self.emitter.emitLine("}")

        # After parsing is complete ensure that all labels in goto'ed list have been declared
        for label in self.labelsGoToed:
            if label not in self.labelsDeclared:
                self.abort("Attempting to GOTO an undeclared label " + label)

    # One of the following statements
    def statement(self):
        # Check the first token to see what kind of statement it is 
        
        # --- PRINT ---
        if self.checkToken(TokenType.PRINT):
            self.nextToken()

            # Check if the next token is either a string or an expression
            if self.checkToken(TokenType.STRING):
                # Translate to C code
                self.emitter.emitLine("printf(\"" + self.curToken.text + "\\n\");")
                # Is a String
                self.nextToken()
            
            else:
                # Translate to C code, expecting an expression after
                self.emitter.emit("printf(\"%" + ".2f\\n\", (float)(")
                # Expect an expression (case where neither will be handled in expression)
                self.expression()
                self.emitter.emitLine("));")

        # --- IF ---
        elif self.checkToken(TokenType.IF):
            self.nextToken()
            self.emitter.emit("if(")
            self.comparison() # Expecting the comparison grammar rule
            
            # If comparison is successful
            self.match(TokenType.THEN) # THEN must be next
            self.nl() # Followed by a new line
            self.emitter.emitLine(")}")

            # Zero or more statements in the body
            while not self.checkToken(TokenType.ENDIF): # until we reach the ENDIF keyword
                self.statement() # Must be a statement

            self.match(TokenType.ENDIF) # ENDIF Token must be there
            self.emitter.emitLine("}")

        # --- WHILE ---
        elif self.checkToken(TokenType.WHILE):
            self.nextToken()
            self.emitter.emit("while(")
            self.comparison() # Expecting the comparison grammar rule

            self.match(TokenType.REPEAT) # Must contain keyword REPEAT
            self.nl() # go to the next line
            self.emitter.emitLine("){")

            # Zero or more statements in the while loop
            while not self.checkToken(TokenType.ENDWHILE): 
                self.statement()
            
            self.match(TokenType.ENDWHILE) # Must include ENDWHILE keyword
            self.emitter.emitLine("}")

        # "LABEL" ident
        elif self.checkToken(TokenType.LABEL):
            self.nextToken()

            # Make sure the label does not exists already
            if self.curToken.text in self.labelsDeclared:
                self.abort("Label already exists")
            # if not exist add to set
            self.labelsDeclared.add(self.curToken.text)

            self.emitter.emitLine(self.curToken.text + ":")
            self.emitter.emitLine("goto " + self.curToken.text + ";")
            self.match(TokenType.IDENT)

        # "GOTO" ident
        elif self.checkToken(TokenType.GOTO):
            print("STATEMENT-GOTO")
            self.nextToken()
            # Track the labels that have been goto'ed
            self.labelsGoToed.add(self.curToken.text)
            self.match(TokenType.IDENT)

        # "LET" ident "=" expression
        elif self.checkToken(TokenType.LET):
            self.nextToken()

            # Check if already declared, if not add it
            if self.curToken.text not in self.symbols:
                self.emitter.headerLine("float " + self.curToken.text + ";")
                self.symbols.add(self.curToken.text)

            self.emitter.emit(self.curToken.text + " = ")
            self.match(TokenType.IDENT)
            self.match(TokenType.EQ)

            self.expression()
            self.emitter.emitLine(";")

        # "INPUT" ident
        elif self.checkToken(TokenType.INPUT):
            self.nextToken()

            # If variable does not already exist, declare it
            if self.curToken.text not in self.symbols:
                self.symbols.add(self.curToken.text)
                self.emitter.headerLine("float " + self.curToken.text + ";")
            
            self.emitter.emitLine("if(0 == scanf(\"%" + "f\", &" + self.curToken.text + ")) {")
            self.emitter.emitLine(self.curToken.text + " = 0;")
            self.emitter.emit("scanf(\"%")
            self.emitter.emitLine("*s\");")
            self.emitter.emitLine("}")
            self.match(TokenType.IDENT)

        # This is not a valid statement. Error!
        else:
            self.abort("Invalid statement at " + self.curToken.text + " (" + self.curToken.kind.name + ")")

        self.nl()

    def isComparisonOperator(self):
        return self.checkToken(TokenType.GT) or self.checkToken(TokenType.GTEQ) or self.checkToken(TokenType.LT) or self.checkToken(TokenType.LTEQ) or self.checkToken(TokenType.EQEQ) or self.checkToken(TokenType.NOTEQ)
    # comparison ::= expression (("==" | "!=" | ">" | ">=" | "<" | "<=") expression)+
    def comparison(self):
        self.expression() # Expection expression first

        if self.isComparisonOperator(): # Must be atleast one comparison operator
            self.emitter.emit(self.curToken.text)
            self.nextToken()
            self.expression() # Expecting expression after comparison operator
        else:
            self.abort("Expecting comparison operator at: " + self.curToken.text)

        # Can have 0 or more comparison operator and expression e.g. 1 + 2 - 3 * 8
        while self.isComparisonOperator():
            self.emitter.emit(self.curToken.text)
            self.nextToken()
            self.expression()

    # expression ::= term {( "-" | "+" ) term}
    def expression(self):
        # Expecting term first
        self.term()

        # Can have 0 or more +- and expression
        while self.checkToken(TokenType.PLUS) or self.checkToken(TokenType.MINUS):
            self.emitter.emit(self.curToken.text)
            self.nextToken()
            self.term() # Expecting term after +-

    # term ::= unary {( "/" | "*" ) unary}
    def term(self):
        self.unary() # Expecting unary first

        # Can have 0 or more */ and expressions
        while self.checkToken(TokenType.ASTERISK ) or self.checkToken(TokenType.SLASH):
            self.emitter.emit(self.curToken.text)
            self.nextToken()
            self.unary()

    # unary ::= ["+" | "-"] primary
    def unary(self):
        # Optional unary +/-
        if self.checkToken(TokenType.PLUS) or self.checkToken(TokenType.MINUS):
            self.emitter.emit(self.curToken.text)
            self.nextToken()
        
        self.primary() # always go to primary at the end

     # primary ::= number | ident
    def primary(self):
        if self.checkToken(TokenType.NUMBER):
            self.emitter.emit(self.curToken.text)
            self.nextToken()

        elif self.checkToken(TokenType.IDENT):
            if self.curToken.text not in self.symbols:
                self.abort("Referencing variable before assignment " + self.curToken.text)
            self.emitter.emit(self.curToken.text)
            self.nextToken()
        else:
            self.abort("Unexpected token at " + self.curToken.text)

    # nl ::= "\n"+
    def nl(self):        
        # Require atleast one new line
        self.match(TokenType.NEWLINE)

        # Allow for multiple new lines
        while self.checkToken(TokenType.NEWLINE):
            self.nextToken()
