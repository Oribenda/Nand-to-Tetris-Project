import JackTokenizer as Jt

class CompilationEngine:

    def __init__(self, inputName, outputName):
        self.tokenizer = Jt.JackTokenizer(inputName)
        self.output = open(f"{outputName}.xml", "w")

    def compileClass(self):
        if self.tokenizer.hasMoreTokens():
            self.tokenizer.advance()

            self.output.write("<class>\n")
            self._eat("class")

            self._eat(self.tokenizer.identifier())

            self._eat("{")

            self.compileClassVarDec()

            while self.tokenizer.keyWord() == "constructor" or self.tokenizer.keyWord() == "function" or self.tokenizer.keyWord() == "method":
                self.compileSubroutine()

            self._eat("}")

            self.output.write("</class>\n")
            self.output.close()

    def compileClassVarDec(self):
        self.output.write("<classVarDec>\n")

        while self.tokenizer.keyWord() == "static" or self.tokenizer.keyWord() == "field":

            self._eat(self.tokenizer.keyWord())

            if self.tokenizer.tokenType() == "KEYWORD":
                self._eat(self.tokenizer.keyWord())
            elif self.tokenizer.tokenType() == "IDENTIFIER":
                self._eat(self.tokenizer.identifier())

            self._eat(self.tokenizer.identifier())

            while self.tokenizer.symbol() == ",":
                self._eat(",")
                self._eat(self.tokenizer.identifier())

            self._eat(";")

        self.output.write("</classVarDec>\n")

    def compileSubroutine(self):
        self.output.write("<subroutibeDec>\n")

        if self.tokenizer.keyWord() == "constructor" or self.tokenizer.keyWord() == "function" or self.tokenizer.keyWord() == "method": # redundant
            self._eat(self.tokenizer.keyWord())

        if self.tokenizer.tokenType() == "KEYWORD":
            self._eat(self.tokenizer.keyWord())
        elif self.tokenizer.tokenType() == "IDENTIFIER":
            self._eat(self.tokenizer.identifier())

        self._eat(self.tokenizer.identifier())

        self._eat("(")

        if self.tokenizer.tokenType() != "SYMBOL":  # move this condition inside the function
            self.compileParameterList()

        self._eat(")")

        self.compileSubroutineBody()

        self.output.write("</subroutibeDec>\n")

    def compileParameterList(self):
        self.output.write("<parameterList>\n")
        self._eat(self.tokenizer.keyWord())
        self._eat(self.tokenizer.identifier())

        while self.tokenizer.symbol() == ",":
            self._eat(",")
            self._eat(self.tokenizer.keyWord())
            self._eat(self.tokenizer.identifier())

        self.output.write("</parameterList>\n")

    def compileSubroutineBody(self):
        self.output.write("<subroutineBody>\n")
        self._eat("{")
        while self.tokenizer.keyWord() == "var":
            self.compileVarDec()
        
        if not(self.tokenizer.tokenType() == "SYMBOL" and self.tokenizer.symbol() == ";"):
            self.compileStatements()

        self._eat(";")
        self.output.write("</subroutineBody>\n")

    def compileVarDec(self):
        self.output.write("<varDec>\n")
        self._eat("var")
        self._eat(self.tokenizer.keyWord())
        self._eat(self.tokenizer.identifier())

        while self.tokenizer.symbol() == ",":
            self._eat(",")
            self._eat(self.tokenizer.identifier())

        self._eat(";")
        self.output.write("</varDec>\n")

    def compileStatements(self):
        self.output.write("<statements>\n")
        statement = self.tokenizer.keyWord()
        while statement == "let" or statement == "if" or statement == "while" or statement == "do" or statement == "return":
            if statement == "let":
                self.compileLet()
            elif statement == "if":
                self.compileIf()
            elif statement == "while":
                self.compileWhile()
            elif statement == "do":
                self.compileDo()
            elif statement == "return":
                self.compileReturn()
            statement = self.tokenizer.keyWord()
        self.output.write("</statements>\n")

    def compileLet(self):
        self.output.write("<letStatement>\n")
        self._eat("let")
        self._eat(self.tokenizer.identifier())
        if self.tokenizer.symbol() == "[":
            self._eat("[")
            self.compileExpression()
            self._eat("]")
        self._eat("=")
        self.compileExpression()
        self._eat(";")
        self.output.write("</letStatement>\n")

    def compileIf(self):
        self.output.write("<ifStatement>\n")
        self._eat("if")
        self._eat("(")
        self.compileExpression()
        self._eat(")")
        self._eat("{")
        self.compileStatements()
        self._eat("}")
        if self.tokenizer.keyWord() == "else":
            self._eat("else")
            self._eat("{")
            self.compileStatements()
            self._eat("}")
        self.output.write("</ifStatement>\n")

    def compileWhile(self):
        self.output.write("<whileStatement>\n")
        self._eat("while")
        self._eat("(")
        self.compileExpression()
        self._eat(")")
        self._eat("{")
        self.compileStatements()
        self._eat("}")
        self.output.write("</whileStatement>\n")

    def compileDo(self):
        self.output.write("<doStatement>\n")
        self._eat("do")
        self.compileExpression()
        self._eat(";")
        self.output.write("</doStatement>\n")

    def compileReturn(self):
        self.output.write("<returnStatement>\n")
        self._eat("return")
        if self.tokenizer.symbol() != ";":
            self.compileExpression()
        self._eat(";")
        self.output.write("</returnStatement>\n")

    def compileExpression(self):
        self.output.write("<expression>\n")
        self.compileTerm()
        while self.tokenizer.tok enType() == "SYMBOL":
            if self.tokenizer.symbol() in ["+", "-", "*", "/", "&", "|", "<", ">", "="]:
                self._eat(self.tokenizer.symbol())
                self.compileTerm()
        self.output.write("</expression>\n")

    def compileTerm(self):
        self.output.write("<term>\n")
        if self.tokenizer.tokenType() == "IDENTIFIER":
            self._eat(self.tokenizer.identifier())
            if self.tokenizer.tokenType() == "SYMBOL":
                if self.tokenizer.symbol() == "[":
                    self._eat("[")
                    self.compileExpression()
                    self._eat("]")
                elif self.tokenizer.symbol() == "(":
                    self._eat("(")
                    self.compileExpressionList()
                    self._eat(")")
                elif self.tokenizer.symbol() == ".":
                    self._eat(".")
                    self._eat(self.tokenizer.identifier())
                    self._eat("(")
                    self.compileExpressionList()
                    self._eat(")")
        elif self.tokenizer.tokenType() == "INT_CONST":
            self._eat(self.tokenizer.intVal())
        elif self.tokenizer.tokenType() == "STRING_CONST":
            self._eat(self.tokenizer.stringVal())
        elif self.tokenizer.tokenType() == "KEYWORD":
            self._eat(self.tokenizer.keyWord())
        elif self.tokenizer.tokenType() == "SYMBOL":
            if self.tokenizer.symbol() == "(":
                self._eat("(")
                self.compileExpression()
                self._eat(")")
            if self.tokenizer.symbol() in ["-", "~"]:
                self._eat(self.tokenizer.symbol())
                self.compileTerm()
        self.output.write("</term>\n")

    def compileExpressionList(self):
        self.output.write("<expressionList>\n")
        if self.tokenizer.tokenType() != "SYMBOL" or (self.tokenizer.tokenType() == "SYMBOL" and self.tokenizer.symbol() != ")"):
            self.compileExpression()
            while self.tokenizer.symbol() == ",":
                self._eat(",")
                self.compileExpression()
        self.output.write("</expressionList>\n")


    def _eat(self, str):
        currentTokenType = self.tokenizer.tokenType()
        if currentTokenType == "KEYWORD":
            currentToken = self.tokenizer.keyWord()
        elif currentTokenType == "SYMBOL":
            currentToken = self.tokenizer.symbol()
        elif currentTokenType == "IDENTIFIER":
            currentToken = self.tokenizer.identifier()
        elif currentTokenType == "INT_CONST":
            currentToken = self.tokenizer.intVal()
        elif currentTokenType == "STRING_CONST":
            currentToken = self.tokenizer.stringVal()
        # if str != currentToken:
        #     raise Exception("Error")    # consider changing the message
        # else:
        self.output.write(f"<{currentTokenType}> {currentToken} </{currentTokenType}>\n")
        self.tokenizer.advance()
