import re

COMMENTS = [re.compile("//.*\n*"), re.compile("/\*.*?\*/", re.DOTALL)]
KEYWORD = re.compile("^\s*(class|constructor|function|method|static|field|var|int|char|boolean|void|true|false|null|this|let|do|if|else|while|return)[^A-Za-z0-9_]\s*")
SYMBOL = re.compile("^\s*([()\[\]\{\},;=./&-|*~<+>])\s*")
INTEGER = re.compile("^\s*(\d\d*)\s*")
STRING = re.compile("^\s*\"(.*?)\"\s*")
IDENTIFIER = re.compile("^\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*")

class JackTokenizer:

    def __init__(self, fileName):
        '''Opens the input file'''
        input = open(fileName, "r")
        self.currentToken = ""
        self.type = ""
        commentless = re.sub(COMMENTS[0], "", input.read())
        commentless = re.sub(COMMENTS[1], "", commentless)

        self.cleanInput = ""

        for line in commentless.splitlines():
            if line.strip() != "":
                self.cleanInput += line.strip() + " "

    def hasMoreTokens(self):
        '''Checks if there are more tokens in the input'''
        if re.fullmatch(re.compile("^\s*"), self.cleanInput):
            return False
        return True

    def advance(self):
        if self.hasMoreTokens():
            currentMatch = re.match(KEYWORD, self.cleanInput)
            if currentMatch:
                self.cleanInput = re.sub(re.compile("^\s*(class|constructor|function|method|static|field|var|int|char|boolean|void|true|false|null|this|let|do|if|else|while|return)\s*"), "", self.cleanInput) # make it prettier
                self.type = "KEYWORD"
                self.currentToken = currentMatch.group(1)
            else:
                currentMatch = re.match(IDENTIFIER, self.cleanInput)
                if currentMatch:
                    self.cleanInput = re.sub(IDENTIFIER, "", self.cleanInput)
                    self.type = "IDENTIFIER"
                    self.currentToken = currentMatch.group(1)
                else:
                    currentMatch = re.match(INTEGER, self.cleanInput)
                    if currentMatch:
                        self.cleanInput = re.sub(INTEGER, "", self.cleanInput)
                        self.type = "INT_CONST"
                        self.currentToken = currentMatch.group(1)
                    else:
                        currentMatch = re.match(STRING, self.cleanInput)
                        if currentMatch:
                            self.cleanInput = re.sub(STRING, "", self.cleanInput)
                            self.type = "STRING_CONST"
                            self.currentToken = currentMatch.group(1)
                        else:
                            currentMatch = re.match(SYMBOL, self.cleanInput)    # fix this shit, it always enters
                            if currentMatch:
                                self.cleanInput = re.sub(SYMBOL, "", self.cleanInput)
                                self.type = "SYMBOL"
                                self.currentToken = currentMatch.group(1)


    def tokenType(self):
        return self.type

    def keyWord(self):
        if self.type == "KEYWORD":
            return self.currentToken

    def symbol(self):
        if self.type == "SYMBOL":
            return self.currentToken

    def identifier(self):
        if self.type == "IDENTIFIER":
            return self.currentToken

    def intVal(self):
        if self.type == "INT_CONST":
            return int(self.currentToken)

    def stringVal(self):
        if self.type == "STRING_CONST":
            return self.currentToken

# if __name__ == "__main__":
#     a = JackTokenizer("ArrayTest/Main.jack")
#     while a.hasMoreTokens():
#         a.advance()
#         print(a.tokenType() + " " + a.currentToken)