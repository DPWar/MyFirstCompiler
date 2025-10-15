import enum
import sys

class Lexer:
    def __init__(self, source):
        self.source = source + "\n" # Source code to lex as string. Append a new line to simplify lexing/parsing the last statement
        self.curChar = "" # Current charater in the string
        self.curPos = -1 # Current position in the string
        self.nextChar()


    # Process the next character
    def nextChar(self):
        self.curPos += 1 # Increment the position
        
        if self.curPos >= len(self.source): # If position is longer than input code, end of file
            self.curChar = "\0" # EOF (End of file)
        else:
            self.curChar = self.source[self.curPos] # Else current char equal to the char in the current position

    # Return the look ahead character
    def peek(self):
        if self.curPos + 1 >= len(self.source):
            return '\0'
        return self.source[self.curPos+1]
    
    # Invalid token found, print error message and exit
    def abort(self, message):
        sys.exit("Lexing Error" + message)

    # Skip white spaces, except newlines, which will be used to indicate the end of a statement
    def skipWhiteSpaces(self):
        while self.curChar == " " or self.curChar == "\t" or self.curChar == "\r": # While current char is a white space/tab/etc.
            self.nextChar() # go to next char

    # Skip comments in code
    def skipComments(self):
        if self.curChar == "#": # "#" is comment identifier
            while self.curChar != "\n": # Do not throw away \n 
                self.nextChar()

    # Return the next token
    def getToken(self):
        # Check the first character of this token, to see if it can be decided what it is
        # If it is a syntax character, process the rest of the token

        self.skipWhiteSpaces() # Make sure to ignore any white spaces in source code
        self.skipComments() # Make sure to ignore any comments
        token = None # Initialise token to None for consistency

        # --- PLUS ---
        if self.curChar == "+":
            token = Token(self.curChar, TokenType.PLUS)

        # --- MINUS ---
        elif self.curChar == "-":
            token = Token(self.curChar, TokenType.MINUS)

        # --- ASTERISK ---
        elif self.curChar == "*":
            token = Token(self.curChar, TokenType.ASTERISK)

        # --- SLASH ---
        elif self.curChar == "/":
            token = Token(self.curChar, TokenType.SLASH)

        # --- NEWLINE ---
        elif self.curChar == "\n":
            token = Token(self.curChar, TokenType.NEWLINE)

        # --- EOF ---
        elif self.curChar == "\0":
            token = Token(self.curChar, TokenType.EOF)

        # --- EQEQ / EQ ---
        elif self.curChar == "=":
            # Check whether this token is = or ==
            if self.peek() == "=":
                lastChar = self.curChar
                self.nextChar()
                token = Token(lastChar + self.curChar, TokenType.EQEQ)
            else:
                token = Token(self.curChar, TokenType.EQ)

        # --- GTEQ / GT ---
        elif self.curChar == '>':
            # Check whether this is token is > or >=
            if self.peek() == '=':
                lastChar = self.curChar
                self.nextChar()
                token = Token(lastChar + self.curChar, TokenType.GTEQ)
            else:
                token = Token(self.curChar, TokenType.GT)

        # --- LTEQ / LT ---
        elif self.curChar == '<':
                # Check whether this is token is < or <=
                if self.peek() == '=':
                    lastChar = self.curChar
                    self.nextChar()
                    token = Token(lastChar + self.curChar, TokenType.LTEQ)
                else:
                    token = Token(self.curChar, TokenType.LT)

        # --- NOTEQ ---
        elif self.curChar == '!':
            if self.peek() == '=':
                lastChar = self.curChar
                self.nextChar()
                token = Token(lastChar + self.curChar, TokenType.NOTEQ)
            else:
                self.abort("Expected !=, got !" + self.peek())

        # --- STRING ---
        elif self.curChar == "\"":
            # get characters between quotations
            self.nextChar()
            startPos = self.curPos

            while self.curChar != "\"":
                # Do not allow special characters for simplicity reasons
                if self.curChar == '\r' or self.curChar == '\n' or self.curChar == '\t' or self.curChar == '\\' or self.curChar == '%':
                    self.abort("Illegal Characters In String!")
                self.nextChar()

            # Do not need to track end position because the loop is exited at end position
            tokText = self.source[startPos : self.curPos] # Get sub string
            
            token = Token(tokText, TokenType.STRING)

        # -- NUMBERS ---
        elif self.curChar.isdigit(): # 
            # Leading char is a digit so must be a number
            # Check for more digits or decimel points
            startPos = self.curPos

            while self.peek().isdigit():
                self.nextChar()

            if self.peek() == ".": # look to see if a decimal
                self.nextChar()

                if not self.peek().isdigit(): # if after the decimal is not a digit
                    self.abort("Illegal Character in Number")

                while self.peek().isdigit():
                    self.nextChar()

            tokText = self.source[startPos : self.curPos + 1]
            token = Token(tokText, TokenType.NUMBER)
        
        # --- IDENTIFIERS ---
        elif self.curChar.isalpha():
            # Character is a letter, so is either identifer or keyword
            # Get all consectutive alphanumberic characters
            startPos = self.curPos
            
            while self.peek().isalnum():
                self.nextChar()
            
            # Check if the token is in the list of keywords
            tokText = self.source[startPos : self.curPos + 1] # Get the substring
            keyword = Token.checkIfKeyword(tokText)

            if keyword == None:
                token = Token(tokText, TokenType.IDENT)
            else:
                token = Token(tokText, keyword)


        # --- NOT TOKEN ---
        else:
            self.abort("Unknown Token" + self.curChar)

        self.nextChar() # process the next character in the string
        
        return token # RETURN TOKEN!!!
    

class Token:
    def __init__(self, tokenText, tokenKind):
        self.text = tokenText # Tokens actual text
        self.kind = tokenKind # The TokenType that the token is classified as
        
    @staticmethod
    def checkIfKeyword(tokText):
        for kind in TokenType: # For all token kinds defined in enum TokenType
            # If the name == TokText input, and the value is between 100 and 200
            # Relies on all identifiers having a value between 100 and 200
            if kind.name == tokText and kind.value > 100 and kind.value < 200: 
                # Return kind (or tokText since they're equal)
                return kind
        return None
    
# Specifies every token type that TeenyTiny Language allows
class TokenType(enum.Enum):
	EOF = -1
	NEWLINE = 0
	NUMBER = 1
	IDENT = 2
	STRING = 3

	# Keywords.
	LABEL = 101
	GOTO = 102
	PRINT = 103
	INPUT = 104
	LET = 105
	IF = 106
	THEN = 107
	ENDIF = 108
	WHILE = 109
	REPEAT = 110
	ENDWHILE = 111

	# Operators.
	EQ = 201  
	PLUS = 202
	MINUS = 203
	ASTERISK = 204
	SLASH = 205
	EQEQ = 206
	NOTEQ = 207
	LT = 208
	LTEQ = 209
	GT = 210
	GTEQ = 211
    

