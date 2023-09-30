import sys

class Parser:
    '''Encapsulates access to the input code.
       Reads an assembly language command, parses it, and provides convenient
       access to command's components (fields and symbols).
       In addition, removes all white space and comments.'''

    file = ""               # .asm file to process
    currentCommand = ""     # current line of the file

    def __init__(self, fileName):
        '''Opens the input file'''
        self.file = open(fileName, "r")
        self.currentCommand = ""

    def hasMoreLines(self):
        '''Checks if there are more commands in the input'''
        currentPos = self.file.tell()
        hasNextLine = bool(self.file.readline())
        self.file.seek(currentPos)
        return hasNextLine

    def advance(self):
        '''Reads the next command from the input (if exists) and makes it the current command'''
        if self.hasMoreLines():
            self.currentCommand = self.file.readline()

    def commandType(self):
        '''Returns the type of the current command'''
        self.currentCommand = self.currentCommand.partition("//")[0]    # remove comments
        self.currentCommand = self.currentCommand.strip()               # remove whitespaces before and after the string
        if not self.currentCommand:     # currentCommand is a comment or an empty line
            return ""
        elif "push" in self.currentCommand:
            return "C_PUSH"
        elif "pop" in self.currentCommand:
            return "C_POP"
        elif "label" in self.currentCommand:
            return "C_LABEL"
        elif "goto" in self.currentCommand:
            return "C_GOTO"
        elif "if" in self.currentCommand:
            return "C_IF"
        elif "function" in self.currentCommand:
            return "C_FUNCTION"
        elif "return" in self.currentCommand:
            return "C_RETURN"
        elif "call" in self.currentCommand:
            return "C_CALL"
        else:
            return "C_ARITHMETIC"

    def arg1(self):
        '''Return the symbol or decimal Xxx of the current @Xxx or (Xxx)'''
        if self.commandType() == "C_ARITHMETIC":
            return self.currentCommand.split()[0]
        elif not self.commandType() == "C_RETURN":
            return self.currentCommand.split()[1]

    def arg2(self):
        '''Returns the dest mnemonic in the current C-command'''
        if self.commandType() == "C_PUSH" or self.commandType() == "C_POP" or self.commandType() == "C_FUNCTION" or self.commandType() == "C_CALL":
            return self.currentCommand.split()[2]

class CodeWriter:

    output = ""
    labelIndex = 0

    def __init__(self, fileName):
        self.output = open(fileName, "w")
        self.labelIndex = 0

    def writeArithmetic(self, command):
        match command:
            case "add":
                self.output.write("@SP\n")
                self.output.write("A=M-1\n")
                self.output.write("D=M\n")
                self.output.write("A=A-1\n")
                self.output.write("M=D+M\n")
                self.output.write("D=A+1\n")
                self.output.write("@SP\n")
                self.output.write("M=D\n")
            case "sub":
                self.output.write("@SP\n")
                self.output.write("A=M-1\n")
                self.output.write("D=M\n")
                self.output.write("A=A-1\n")
                self.output.write("M=M-D\n")
                self.output.write("D=A+1\n")
                self.output.write("@SP\n")
                self.output.write("M=D\n")
            case "neg":
                self.output.write("@SP\n")
                self.output.write("A=M-1\n")
                self.output.write("M=-M\n")
            case "eq":
                self.output.write("@SP\n")
                self.output.write("A=M-1\n")
                self.output.write("A=A-1\n")
                self.output.write("D=M\n")
                self.output.write("M=-1\n")
                self.output.write("A=A+1\n")
                self.output.write("D=D-M\n")
                self.output.write(f"@EQ{self.labelIndex}\n")
                self.output.write("D;JEQ\n")
                self.output.write("A=A-1\n")
                self.output.write("M=0\n")
                self.output.write(f"(EQ{self.labelIndex})\n")
                self.output.write("@SP\n")
                self.output.write("M=M-1\n")
                self.labelIndex += 1
            case "gt":
                self.output.write("@SP\n")
                self.output.write("A=M-1\n")
                self.output.write("A=A-1\n")
                self.output.write("D=M\n")
                self.output.write("M=-1\n")
                self.output.write("A=A+1\n")
                self.output.write("D=D-M\n")
                self.output.write(f"@GT{self.labelIndex}\n")
                self.output.write("D;JGT\n")
                self.output.write("A=A-1\n")
                self.output.write("M=0\n")
                self.output.write(f"(GT{self.labelIndex})\n")
                self.output.write("@SP\n")
                self.output.write("M=M-1\n")
                self.labelIndex += 1
            case "lt":
                self.output.write("@SP\n")
                self.output.write("A=M-1\n")
                self.output.write("A=A-1\n")
                self.output.write("D=M\n")
                self.output.write("M=-1\n")
                self.output.write("A=A+1\n")
                self.output.write("D=D-M\n")
                self.output.write(f"@LT{self.labelIndex}\n")
                self.output.write("D;JLT\n")
                self.output.write("A=A-1\n")
                self.output.write("M=0\n")
                self.output.write(f"(LT{self.labelIndex})\n")
                self.output.write("@SP\n")
                self.output.write("M=M-1\n")
                self.labelIndex += 1
            case "and":
                self.output.write("@SP\n")
                self.output.write("A=M-1\n")
                self.output.write("D=M\n")
                self.output.write("A=A-1\n")
                self.output.write("M=D&M\n")
                self.output.write("@SP\n")
                self.output.write("M=M-1\n")
            case "or":
                self.output.write("@SP\n")
                self.output.write("A=M-1\n")
                self.output.write("D=M\n")
                self.output.write("A=A-1\n")
                self.output.write("M=D|M\n")
                self.output.write("@SP\n")
                self.output.write("M=M-1\n")
            case "not":
                self.output.write("@SP\n")
                self.output.write("A=M-1\n")
                self.output.write("M=!M\n")

    def writePushPop(self, command, segment, index):
        match segment:
            case "constant":
                if command == "C_PUSH":
                    self.output.write(f"@{index}\n")
                    self.output.write("D=A\n")
                    self.output.write("@SP\n")
                    self.output.write("A=M\n")
                    self.output.write("M=D\n")
                    self.output.write("@SP\n")
                    self.output.write("M=M+1\n")
            case "local" | "argument" | "this" | "that":
                if segment == "local":
                    segment = "LCL"
                elif segment == "argument":
                    segment = "ARG"
                elif segment == "this" or segment == "that":
                    segment = segment.upper()
                if command == "C_PUSH":
                    self.output.write(f"@{segment}\n")
                    self.output.write("D=M\n")
                    self.output.write(f"@{index}\n")
                    self.output.write("A=D+A\n")
                    self.output.write("D=M\n")
                    self.output.write("@SP\n")
                    self.output.write("A=M\n")
                    self.output.write("M=D\n")
                    self.output.write("@SP\n")
                    self.output.write("M=M+1\n")
                elif command == "C_POP":
                    self.output.write(f"@{segment}\n")
                    self.output.write("D=M\n")
                    self.output.write(f"@{index}\n")
                    self.output.write("D=D+A\n")
                    self.output.write("@addr\n")
                    self.output.write("M=D\n")
                    self.output.write("@SP\n")
                    self.output.write("M=M-1\n")
                    self.output.write("A=M\n")
                    self.output.write("D=M\n")
                    self.output.write("@addr\n")
                    self.output.write("M=D\n")
            case "static":
                if command == "C_PUSH":
                    self.output.write(f"@{self.output.name.rpartition('.')[0]}.{index}\n")
                    self.output.write("D=A\n")
                    self.output.write("@SP\n")
                    self.output.write("A=M\n")
                    self.output.write("M=D\n")
                    self.output.write("@SP\n")
                    self.output.write("M=M+1\n")
                elif command == "C_POP":
                    self.output.write("@SP")
                    self.output.write("M=M-1\n")
                    self.output.write("A=M\n")
                    self.output.write("D=M\n")
                    self.output.write(f"@{self.output.name.rpartition('.')[0]}.{index}\n")
                    self.output.write("M=D\n")
            case "temp" | "pointer":
                if segment == "temp":
                    baseAddress = 5
                else:
                    baseAddress = 3
                if command == "C_PUSH":
                    self.output.write(f"@{baseAddress}\n")
                    self.output.write("D=A\n")
                    self.output.write(f"@{index}\n")
                    self.output.write("A=D+A\n")
                    self.output.write("D=M\n")
                    self.output.write("@SP\n")
                    self.output.write("A=M\n")
                    self.output.write("M=D\n")
                    self.output.write("@SP\n")
                    self.output.write("M=M+1\n")
                elif command == "C_POP":
                    self.output.write(f"@{baseAddress}\n")
                    self.output.write("D=A\n")
                    self.output.write(f"@{index}\n")
                    self.output.write("D=D+A\n")
                    self.output.write("@addr\n")
                    self.output.write("M=D\n")
                    self.output.write("@SP\n")
                    self.output.write("M=M-1\n")
                    self.output.write("A=M\n")
                    self.output.write("D=M\n")
                    self.output.write("@addr\n")
                    self.output.write("M=D\n")

    def close(self):
        self.output.write("(END)\n")
        self.output.write("@END\n")
        self.output.write("0;JMP\n")
        self.output.close()

if __name__ == "__main__":
    inputFileName = sys.argv[1]
    fileParser = Parser(inputFileName)
    outputFileName = inputFileName.rpartition('.')[0] + ".asm"
    fileCodeWriter = CodeWriter(outputFileName)
    while fileParser.hasMoreLines():
        fileParser.advance()
        commandType = fileParser.commandType()
        if commandType == "C_ARITHMETIC":
            command = fileParser.arg1()
            fileCodeWriter.writeArithmetic(command)
        elif commandType == "C_PUSH" or commandType == "C_POP":
            segment = fileParser.arg1()
            index = fileParser.arg2()
            fileCodeWriter.writePushPop(commandType, segment, index)
    fileCodeWriter.close()