import JackTokenizer as Jt
import SymbolTable as St
import VMWriter as VMw

class CompilationEngine:
    '''Emits a structured printout of the code wrapped in XML tags'''

    def __init__(self, inputName):
        '''Creates a new compilation engine with the given input and output'''
        self.tokenizer = Jt.JackTokenizer(inputName)
        self.writer = VMw.VMWriter(inputName)
        self.classTable = St.SymbolTable()
        self.subroutineTable = St.SymbolTable()
        self.className = ""
        self.subroutineName = ""
        self.labelIndex = 1


    def compileClass(self):
        '''Compiles a complete class'''

        if self.tokenizer.hasMoreTokens():

            self.tokenizer.advance()
            self.classTable.reset()

            self._eat("class")
            self.className = self._eat(self.tokenizer.identifier())
            self._eat("{")

            while self.tokenizer.keyWord() == "static" or self.tokenizer.keyWord() == "field":
                self.compileClassVarDec()

            while self.tokenizer.keyWord() == "constructor" or self.tokenizer.keyWord() == "function" or self.tokenizer.keyWord() == "method":
                self.compileSubroutine()

            self._eat("}")

            self.writer.close()


    def compileClassVarDec(self):
        '''Compiles a static variable declaration or a field declaration'''

        kind = self._eat(self.tokenizer.keyWord())

        if self.tokenizer.tokenType() == "KEYWORD": # 'int', 'char' or 'boolean'
            type = self._eat(self.tokenizer.keyWord())
        elif self.tokenizer.tokenType() == "IDENTIFIER":    # className
            type = self._eat(self.tokenizer.identifier())

        name = self._eat(self.tokenizer.identifier())

        self.classTable.define(name, type, kind)

        while self.tokenizer.symbol() == ",":
            self._eat(",")
            name = self._eat(self.tokenizer.identifier())
            self.classTable.define(name, type, kind)

        self._eat(";")


    def compileSubroutine(self):
        '''Compiles a complete method, function, or constructor'''

        self.subroutineTable.reset()

        if self.tokenizer.keyWord() == "method":
            self.subroutineTable.define("this", self.className, "argument")
            self.writer.writePush("argument", 0)
            self.writer.writePop("pointer", 0)

        if self.tokenizer.keyWord() == "constructor" or self.tokenizer.keyWord() == "function" or self.tokenizer.keyWord() == "method":
            self._eat(self.tokenizer.keyWord())

        if self.tokenizer.tokenType() == "KEYWORD": # 'int', 'char', 'boolean' or 'void'
            returnType = self._eat(self.tokenizer.keyWord())
        elif self.tokenizer.tokenType() == "IDENTIFIER":    # className
            returnType = self._eat(self.tokenizer.identifier())

        self.subroutineName = self._eat(self.tokenizer.identifier())
        self._eat("(")
        self.compileParameterList()
        self._eat(")")
        self.compileSubroutineBody()

        # handle return type


    def compileParameterList(self):
        '''Compiles a (possibly empty) parameter list, not including the enclosing "()"'''

        if self.tokenizer.tokenType() != "SYMBOL":  # if the parameterList is not empty
            if self.tokenizer.tokenType() == "KEYWORD": # 'int', 'char', 'boolean'
                type = self._eat(self.tokenizer.keyWord())
            elif self.tokenizer.tokenType() == "IDENTIFIER":    # className
                type = self._eat(self.tokenizer.identifier())
            name = self._eat(self.tokenizer.identifier())
            self.subroutineTable.define(name, type, "argument")

            while self.tokenizer.symbol() == ",":
                self._eat(",")
            if self.tokenizer.tokenType() == "KEYWORD": # 'int', 'char', 'boolean'
                type = self._eat(self.tokenizer.keyWord())
            elif self.tokenizer.tokenType() == "IDENTIFIER":    # className
                type = self._eat(self.tokenizer.identifier())
            name = self._eat(self.tokenizer.identifier())
            self.subroutineTable.define(name, type, "argument")


    def compileSubroutineBody(self):
        '''Compiles a subroutine's body'''

        self._eat("{")

        while self.tokenizer.keyWord() == "var":
            self.compileVarDec()
        
        if not(self.tokenizer.tokenType() == "SYMBOL" and self.tokenizer.symbol() == "}"):
            self.compileStatements()

        self._eat("}")


    def compileVarDec(self):
        '''Compiles a var declaration'''

        self._eat("var")

        if self.tokenizer.tokenType() == "KEYWORD": # 'int', 'char' or 'boolean'
            type = self._eat(self.tokenizer.keyWord())
        elif self.tokenizer.tokenType() == "IDENTIFIER":    # className
            type = self._eat(self.tokenizer.identifier())

        name = self._eat(self.tokenizer.identifier())
        self.subroutineTable.define(name, type, "local")

        while self.tokenizer.symbol() == ",":
            self._eat(",")
            name = self._eat(self.tokenizer.identifier())
            self.subroutineTable.define(name, type, "local")

        self._eat(";")


    def compileStatements(self):
        '''Compiles a sequence of statements, not including the enclosing "{}"'''

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


    def compileLet(self):
        '''Compiles a let statement'''

        self._eat("let")
        varName = self._eat(self.tokenizer.identifier())
        segment = self.subroutineTable.kindOf(varName)
        if not segment:
            segment = self.classTable.kindOf(varName)
        index = self.subroutineTable.indexOf(varName)
        if not index:
            index = self.classTable.indexOf(varName)

        if self.tokenizer.symbol() == "[":
            self._eat("[")
            self.writer.writePush("that", 0)
            self.compileExpression()
            self.writer.writeArithmetic("add")
            self._eat("=")
            self.compileExpression()
            self.writer.writePop("temp", 0)
            self.writer.writePop("pointer", 1)
            self.writer.writePush("temp", 0)
            self.writer.writePop("that", 0)
            self._eat("]")

        else:
            self._eat("=")
            self.compileExpression()

        self._eat(";")

        self.writer.writePop(segment, index)


    def compileIf(self):
        '''Compiles an if statement, possibly with a trailing else clause'''

        self._eat("if")
        self._eat("(")
        self.compileExpression()
        self._eat(")")

        self.writer.writeArithmetic("not")

        firstLabel = f"L{self.labelIndex}"
        self.labelIndex += 1
        self.writer.writeIf(firstLabel)

        self._eat("{")
        self.compileStatements()
        self._eat("}")

        secondLabel = f"L{self.labelIndex}"
        self.labelIndex += 1
        self.writer.writeGoto(secondLabel)

        self.writer.writeLabel(firstLabel)

        if self.tokenizer.keyWord() == "else":
            self._eat("else")
            self._eat("{")
            self.compileStatements()
            self._eat("}")

        self.writer.writeLabel(secondLabel)


    def compileWhile(self):
        '''Compiles a while statement'''

        firstLabel = f"L{self.labelIndex}"
        self.labelIndex += 1
        self.writer.writeLabel(firstLabel)

        self._eat("while")
        self._eat("(")
        self.compileExpression()
        self._eat(")")

        self.writer.writeArithmetic("not")

        secondLabel = f"L{self.labelIndex}"
        self.labelIndex += 1
        self.writer.writeIf(secondLabel)

        self._eat("{")
        self.compileStatements()
        self._eat("}")

        self.writer.writeGoto(firstLabel)
        self.writer.writeLabel(secondLabel)


    def compileDo(self):
        '''Compiles a do statement'''

        self._eat("do")
        name = self._eat(self.tokenizer.identifier())

        # Compile subroutineCall
        if self.tokenizer.symbol() == "(":
            self._eat("(")
            nVars = self.compileExpressionList()
            self._eat(")")
        elif self.tokenizer.symbol() == ".":
            segment = self.subroutineTable.kindOf(name)
            if not segment:
                segment = self.classTable.kindOf(name)
            index = self.subroutineTable.indexOf(name)
            if not index:
                index = self.classTable.indexOf(name)
            self.writer.writePush(segment, index)
            self._eat(".")
            name = self._eat(self.tokenizer.identifier())
            self._eat("(")
            nVars = self.compileExpressionList() + 1
            self._eat(")")

        self.writer.writeCall(name, nVars)

        self._eat(";")


    def compileReturn(self):
        '''Compiles a return statement'''

        self._eat("return")

        if self.tokenizer.symbol() != ";":
            self.compileExpression()

        self.writer.writeReturn()

        self._eat(";")


    def compileExpression(self):
        '''Compiles an expression'''

        self.compileTerm()

        while self.tokenizer.tokenType() == "SYMBOL" and self.tokenizer.symbol() in ["+", "-", "*", "/", "&amp;", "|", "&lt;", "&gt;", "="]:    # adapted to comply with XML notations

            self.compileTerm()

            operator = self._eat(self.tokenizer.symbol())
            if operator == "+":
                self.writer.writeArithmetic("add")
            elif operator == "-":
                self.writer.writeArithmetic("sub")
            elif operator == "*":
                self.writer.writeCall("Math.multiply", 2)
            elif operator == "/":
                self.writer.writeCall("Math.divide", 2)
            elif operator == "/":
                self.writer.writeCall("Math.divide", 2)
            elif operator == "&amp;":
                self.writer.writeArithmetic("and")
            elif operator == "|":
                self.writer.writeArithmetic("or")
            elif operator == "&lt;":
                self.writer.writeArithmetic("lt")
            elif operator == "&gt;":
                self.writer.writeArithmetic("gt")
            elif operator == "=":
                self.writer.writeArithmetic("eq")


    def compileTerm(self):
        '''Compiles a term'''

        if self.tokenizer.tokenType() == "IDENTIFIER":
            name = self._eat(self.tokenizer.identifier())

            if self.tokenizer.tokenType() == "SYMBOL":
                if self.tokenizer.symbol() == "[":  # resolve into an array entry
                    self._eat("[")
                    segment = self.subroutineTable.kindOf(name)
                    if not segment:
                        segment = self.classTable.kindOf(name)
                    index = self.subroutineTable.indexOf(name)
                    if not index:
                        index = self.classTable.indexOf(name)
                    self.writer.writePush(segment, index)
                    self.compileExpression()
                    self.writer.writeArithmetic("add")
                    self.writer.writePop("pointer", 0)
                    self._eat("]")
                elif self.tokenizer.symbol() == "(":    # resolve into a subroutine call
                    self._eat("(")
                    self.compileExpressionList()
                    self._eat(")")
                elif self.tokenizer.symbol() == ".":    # # resolve into a subroutine call
                    self._eat(".")
                    name2 = self._eat(self.tokenizer.identifier())
                    self._eat("(")
                    self.compileExpressionList()
                    self._eat(")")

        elif self.tokenizer.tokenType() == "INT_CONST":
            number = self._eat(self.tokenizer.intVal())
            self.writer.writePush("constant", number)

        elif self.tokenizer.tokenType() == "STRING_CONST":
            self._eat(self.tokenizer.stringVal())

        elif self.tokenizer.tokenType() == "KEYWORD":
            self._eat(self.tokenizer.keyWord())

        elif self.tokenizer.tokenType() == "SYMBOL":
            if self.tokenizer.symbol() == "(":
                self._eat("(")
                self.compileExpression()
                self._eat(")")
            elif self.tokenizer.symbol() in ["-", "~"]:
                self._eat(self.tokenizer.symbol())
                self.compileTerm()


    def compileExpressionList(self):
        '''Compiles a (possibly empty) comma-seperated list of expressions. Returns the number of expressions in the list'''
        numberOfExpressions = 0

        self.output.write("<expressionList>\n")

        if self.tokenizer.tokenType() != "SYMBOL" or (self.tokenizer.tokenType() == "SYMBOL" and self.tokenizer.symbol() != ")"):   # if the list is not empty
            self.compileExpression()
            numberOfExpressions += 1

            while self.tokenizer.symbol() == ",":
                self._eat(",")
                self.compileExpression()
                numberOfExpressions += 1

        self.output.write("</expressionList>\n")

        return numberOfExpressions


    def _eat(self, str):
        '''Private function used to process the tokens with their matching XML tags'''

        currentTokenType = self.tokenizer.tokenType()

        # Set currentToken according to currentTokenType, and change the terms used to define the types
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

        if str != currentToken:
            raise Exception("Error")    # consider changing the message
        else:
            self.tokenizer.advance()
            return currentToken