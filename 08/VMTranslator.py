import sys
import os

class Parser:
    '''Handles the parsing of a single .vm file, and encapsulates access to the input code.
       It reads VM commands, parses them, and provides convenient access to their components.
       In addition, it removes all white space and comments.'''

    file = ""               # .vm file to process
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
        '''Returns the type of the current VM command'''
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
        elif "if-goto" in self.currentCommand:
            return "C_IF"
        elif "goto" in self.currentCommand:
            return "C_GOTO"
        elif "function" in self.currentCommand:
            return "C_FUNCTION"
        elif "return" in self.currentCommand:
            return "C_RETURN"
        elif "call" in self.currentCommand:
            return "C_CALL"
        else:
            return "C_ARITHMETIC"

    def arg1(self):
        '''Returns the first argument of the current command'''
        if self.commandType() == "C_ARITHMETIC":    # return the command itself
            return self.currentCommand.split()[0]
        elif not self.commandType() == "C_RETURN":
            return self.currentCommand.split()[1]

    def arg2(self):
        '''Returns the second argument of the current command'''
        if self.commandType() == "C_PUSH" or self.commandType() == "C_POP" or self.commandType() == "C_FUNCTION" or self.commandType() == "C_CALL":
            return self.currentCommand.split()[2]


class CodeWriter:
    '''Translates VM commands into Hack assembly code'''

    output = ""
    labelIndex = 0      # used to create different labels
    returnIndex = 0
    currentFileName = ""
    isFolder =1

    def __init__(self, fileName):
        '''Opens the output file'''
        self.output = open(fileName, "w")
        self.labelIndex = 0
        self.returnIndex = 0
        self.currentFileName = fileName
        self.output.write("@256\n")
        self.output.write("D=A\n")
        self.output.write("@SP\n")
        self.output.write("M=D\n")
        if (isFolder):
            self.writeCall("Sys.init", "0")

    def setFileName(self, fileName):
        self.currentFileName = os.path.basename(fileName).rpartition(".")[0]

    def writeArithmetic(self, command):
        '''Writes the assembly code that is the translation of the given arithmetic command'''
        if command == "add":
            # RAM[SP-2] <-- RAM[SP-1]+RAM[SP-2]
            self.output.write("@SP\n")
            self.output.write("A=M-1\n")
            self.output.write("D=M\n")
            self.output.write("A=A-1\n")
            self.output.write("M=D+M\n")
            self.output.write("D=A+1\n")
            # SP--
            self.output.write("@SP\n")
            self.output.write("M=D\n")

        elif command == "sub":
            # RAM[SP-2] <-- RAM[SP-2]-RAM[SP-1]
            self.output.write("@SP\n")
            self.output.write("A=M-1\n")
            self.output.write("D=M\n")
            self.output.write("A=A-1\n")
            self.output.write("M=M-D\n")
            self.output.write("D=A+1\n")
            # SP--
            self.output.write("@SP\n")
            self.output.write("M=D\n")

        elif command == "neg":
            # RAM[SP-1] <-- -RAM[SP-1]
            self.output.write("@SP\n")
            self.output.write("A=M-1\n")
            self.output.write("M=-M\n")

        elif command == "eq":
            # D <-- RAM[SP-1] - RAM[SP-2]
            self.output.write("@SP\n")
            self.output.write("AM=M-1\n")
            self.output.write("D=M\n")
            self.output.write("A=A-1\n")
            self.output.write("D=D-M\n")
            self.output.write("M=-1\n")     # default value is True (-1)
            self.output.write(f"@EQ{self.labelIndex}\n")
            self.output.write("D;JEQ\n")
            # If not equal
            self.output.write("@SP\n")
            self.output.write("A=M-1\n")
            self.output.write("M=0\n")      # change to False (0)
            self.output.write(f"(EQ{self.labelIndex})\n")

            self.labelIndex += 1

        elif command == "gt":
            # D <-- RAM[SP-2] - RAM[SP-1]
            self.output.write("@SP\n")
            self.output.write("AM=M-1\n")
            self.output.write("D=M\n")
            self.output.write("A=A-1\n")
            self.output.write("D=M-D\n")
            self.output.write("M=-1\n")     # default value is True (-1)
            self.output.write(f"@GT{self.labelIndex}\n")
            self.output.write("D;JGT\n")
            # If not greater than
            self.output.write("@SP\n")
            self.output.write("A=M-1\n")
            self.output.write("M=0\n")      # change to False (0)
            self.output.write(f"(GT{self.labelIndex})\n")

            self.labelIndex += 1

        elif command == "lt":
            # D <-- RAM[SP-2] - RAM[SP-1]
            self.output.write("@SP\n")
            self.output.write("AM=M-1\n")
            self.output.write("D=M\n")
            self.output.write("A=A-1\n")
            self.output.write("D=M-D\n")
            self.output.write("M=-1\n")     # default value is True (-1)
            self.output.write(f"@LT{self.labelIndex}\n")
            self.output.write("D;JLT\n")
            # If not less than
            self.output.write("@SP\n")
            self.output.write("A=M-1\n")
            self.output.write("M=0\n")      # change to False (0)
            self.output.write(f"(LT{self.labelIndex})\n")

            self.labelIndex += 1

        elif command == "and":
            # RAM[SP-2] <-- RAM[SP-1]&RAM[SP-2]
            self.output.write("@SP\n")
            self.output.write("A=M-1\n")
            self.output.write("D=M\n")
            self.output.write("A=A-1\n")
            self.output.write("M=D&M\n")
            # SP--
            self.output.write("@SP\n")
            self.output.write("M=M-1\n")

        elif command == "or":
            # RAM[SP-2] <-- RAM[SP-1]|RAM[SP-2]
            self.output.write("@SP\n")
            self.output.write("A=M-1\n")
            self.output.write("D=M\n")
            self.output.write("A=A-1\n")
            self.output.write("M=D|M\n")
            # SP--
            self.output.write("@SP\n")
            self.output.write("M=M-1\n")

        elif command == "not":
            # RAM[SP-1] <-- !RAM[SP-1]
            self.output.write("@SP\n")
            self.output.write("A=M-1\n")
            self.output.write("M=!M\n")

    def writePushPop(self, command, segment, index):
        '''Writes the assembly code that is the translation of the given command, where command is either C_PUSH or C_POP'''

        if segment == "constant":
            if command == "C_PUSH":
                # RAM[SP] <-- i
                self.output.write(f"@{index}\n")
                self.output.write("D=A\n")
                self.output.write("@SP\n")
                self.output.write("A=M\n")
                self.output.write("M=D\n")
                # SP++
                self.output.write("@SP\n")
                self.output.write("M=M+1\n")

        elif segment == "local" or segment == "argument" or segment == "this" or segment == "that":
            # Translate segment to RAM label
            if segment == "local":
                segment = "LCL"
            elif segment == "argument":
                segment = "ARG"
            elif segment == "this" or segment == "that":
                segment = segment.upper()

            if command == "C_PUSH":
                # RAM[SP] <-- RAM[segment+i]
                self.output.write(f"@{segment}\n")
                self.output.write("D=M\n")
                self.output.write(f"@{index}\n")
                self.output.write("A=D+A\n")
                self.output.write("D=M\n")
                self.output.write("@SP\n")
                self.output.write("A=M\n")
                self.output.write("M=D\n")
                # SP++
                self.output.write("@SP\n")
                self.output.write("M=M+1\n")

            elif command == "C_POP":
                # R13 <-- segment+1
                self.output.write(f"@{segment}\n")
                self.output.write("D=M\n")
                self.output.write(f"@{index}\n")
                self.output.write("D=D+A\n")
                self.output.write("@R13\n")
                self.output.write("M=D\n")
                # SP--
                self.output.write("@SP\n")
                self.output.write("M=M-1\n")
                # RAM[R13] <-- RAM[SP]
                self.output.write("A=M\n")
                self.output.write("D=M\n")
                self.output.write("@R13\n")
                self.output.write("A=M\n")
                self.output.write("M=D\n")

        elif segment == "static":

            if command == "C_PUSH":
                # RAM[SP] <-- RAM["fileName.index"]
                self.output.write(f"@{self.currentFileName}.{index}\n")
                self.output.write("D=M\n")
                self.output.write("@SP\n")
                self.output.write("A=M\n")
                self.output.write("M=D\n")
                # SP++
                self.output.write("@SP\n")
                self.output.write("M=M+1\n")

            elif command == "C_POP":
                # SP--
                self.output.write("@SP\n")
                self.output.write("M=M-1\n")
                # RAM["fileName.index"] <-- RAM[SP]
                self.output.write("A=M\n")
                self.output.write("D=M\n")
                self.output.write(f"@{self.currentFileName}.{index}\n")
                self.output.write("M=D\n")

        elif segment == "temp" or segment == "pointer":

            if segment == "temp":
                baseAddress = 5
            else:   # segment == "pointer"
                baseAddress = 3

            if command == "C_PUSH":
                # D <-- RAM[baseAddress+index]
                self.output.write(f"@{baseAddress}\n")
                self.output.write("D=A\n")
                self.output.write(f"@{index}\n")
                self.output.write("A=D+A\n")
                self.output.write("D=M\n")
                # RAM[SP] <-- D
                self.output.write("@SP\n")
                self.output.write("A=M\n")
                self.output.write("M=D\n")
                # SP++
                self.output.write("@SP\n")
                self.output.write("M=M+1\n")

            elif command == "C_POP":
                # R13 <-- baseAddress+i
                self.output.write(f"@{baseAddress}\n")
                self.output.write("D=A\n")
                self.output.write(f"@{index}\n")
                self.output.write("D=D+A\n")
                self.output.write("@R13\n")
                self.output.write("M=D\n")
                # SP--
                self.output.write("@SP\n")
                self.output.write("M=M-1\n")
                # RAM[R13] <-- RAM[SP]
                self.output.write("A=M\n")
                self.output.write("D=M\n")
                self.output.write("@R13\n")
                self.output.write("A=M\n")
                self.output.write("M=D\n")

    def writeLabel(self, label):
        self.output.write(f"({label})\n")

    def writeGoto(self, label):
        self.output.write(f"@{label}\n")
        self.output.write("0;JMP\n")

    def writeIf(self, label):
        self.output.write("@SP\n")
        self.output.write("AM=M-1\n")
        self.output.write("D=M\n")
        self.output.write(f"@{label}\n")
        self.output.write("D;JNE\n")

    def writeFunction(self, functionName, nVars):
        self.output.write(f"({functionName})\n")
        nVarsINT = int(nVars)
        for i in range(0, nVarsINT):
            self.output.write("@LCL\n")
            self.output.write("D=M\n")
            self.output.write(f"@{i}\n")
            self.output.write("A=D+A\n")
            self.output.write("M=0\n")
            self.output.write("@SP\n")
            self.output.write("M=M+1\n")
            
            
       
    def writeCall(self, functionName, nVars):
        # push returnAddress
        self.output.write(f"@{functionName}$ret.{self.returnIndex}\n")
        self.output.write("D=A\n")
        self.output.write("@SP\n")
        self.output.write("A=M\n")
        self.output.write("M=D\n")
        self.output.write("@SP\n")
        self.output.write("M=M+1\n")

        # push LCL
        self.output.write("@LCL\n")
        self.output.write("D=M\n")
        self.output.write("@SP\n")
        self.output.write("A=M\n")
        self.output.write("M=D\n")
        self.output.write("@SP\n")
        self.output.write("M=M+1\n")

        # push ARG
        self.output.write("@ARG\n")
        self.output.write("D=M\n")
        self.output.write("@SP\n")
        self.output.write("A=M\n")
        self.output.write("M=D\n")
        self.output.write("@SP\n")
        self.output.write("M=M+1\n")

        # push THIS
        self.output.write("@THIS\n")
        self.output.write("D=M\n")
        self.output.write("@SP\n")
        self.output.write("A=M\n")
        self.output.write("M=D\n")
        self.output.write("@SP\n")
        self.output.write("M=M+1\n")

        # push THAT
        self.output.write("@THAT\n")
        self.output.write("D=M\n")
        self.output.write("@SP\n")
        self.output.write("A=M\n")
        self.output.write("M=D\n")
        self.output.write("@SP\n")
        self.output.write("M=M+1\n")

        # ARG=SP–5–nVars
        self.output.write("@5\n")
        self.output.write("D=A\n")
        self.output.write(f"@{nVars}\n")
        self.output.write("D=D+A\n")
        self.output.write("@SP\n")
        self.output.write("D=M-D\n")
        self.output.write("@ARG\n")
        self.output.write("M=D\n")

        # LCL=SP
        self.output.write("@SP\n")
        self.output.write("D=M\n")
        self.output.write("@LCL\n")
        self.output.write("M=D\n")

        # goto functionName
        self.output.write(f"@{functionName}\n")
        self.output.write("0;JMP\n")

        # (returnAddress)
        self.output.write(f"({functionName}$ret.{self.returnIndex})\n")

        self.returnIndex += 1

    def writeReturn(self):
        # endFrame=LCL
        self.output.write("@LCL\n")
        self.output.write("D=M\n")
        self.output.write("@endFrame\n")
        self.output.write("M=D\n")

        # retAddr=*(endFrame-5)
        self.output.write("D=M\n")
        self.output.write("@5\n")
        self.output.write("A=D-A\n")
        self.output.write("D=M\n")
        self.output.write("@retAddr\n")
        self.output.write("M=D\n")

        # *ARG=pop()
        self.output.write("@SP\n")
        self.output.write("M=M-1\n")
        self.output.write("A=M\n")
        self.output.write("D=M\n")
        self.output.write("@ARG\n")
        self.output.write("A=M\n")
        self.output.write("M=D\n")

        # SP=ARG+1
        self.output.write("@ARG\n")
        self.output.write("D=M+1\n")
        # self.output.write("M=M+1\n") # consider replacing the above line by these two
        # self.output.write("D=M\n")
        self.output.write("@SP\n")
        self.output.write("M=D\n")

        # THAT = *(endFrame-1)
        self.output.write("@endFrame\n")
        self.output.write("D=M\n")
        self.output.write("A=D-1\n")
        self.output.write("D=M\n")
        self.output.write("@THAT\n")
        self.output.write("M=D\n")

        # THIS = *(endFrame-2)
        self.output.write("@endFrame\n")
        self.output.write("D=M\n")
        self.output.write("@2\n")
        self.output.write("A=D-A\n")
        self.output.write("D=M\n")
        self.output.write("@THIS\n")
        self.output.write("M=D\n")

        # ARG = *(endFrame-3)
        self.output.write("@endFrame\n")
        self.output.write("D=M\n")
        self.output.write("@3\n")
        self.output.write("A=D-A\n")
        self.output.write("D=M\n")
        self.output.write("@ARG\n")
        self.output.write("M=D\n")

        # LCL = *(endFrame-4)
        self.output.write("@endFrame\n")
        self.output.write("D=M\n")
        self.output.write("@4\n")
        self.output.write("A=D-A\n")
        self.output.write("D=M\n")
        self.output.write("@LCL\n")
        self.output.write("M=D\n")

        # goto retAddr
        self.output.write("@retAddr\n")
        self.output.write("A=M\n")
        self.output.write("0;JMP\n")

    def close(self):
        '''Ends the file with a vacant infinite loop and closes it'''
        self.output.write("(END)\n")
        self.output.write("@END\n")
        self.output.write("0;JMP\n")
        self.output.close()

def mainLoop(inputFile, fileCodeWriter):
    '''Marches through the VM commands in the input file and generate assembly code for each one of them'''
    fileParser = Parser(inputFile)
    fileCodeWriter.setFileName(inputFile)

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

        elif commandType == "C_LABEL":
            label = fileParser.arg1()
            fileCodeWriter.writeLabel(label)

        elif commandType == "C_GOTO":
            label = fileParser.arg1()
            fileCodeWriter.writeGoto(label)

        elif commandType == "C_IF":
            label = fileParser.arg1()
            fileCodeWriter.writeIf(label)

        elif commandType == "C_FUNCTION":
            functionName = fileParser.arg1()
            nVars = fileParser.arg2()
            fileCodeWriter.writeFunction(functionName, nVars)

        elif commandType == "C_RETURN":
            fileCodeWriter.writeReturn()

        elif commandType == "C_CALL":
            functionName = fileParser.arg1()
            nVars = fileParser.arg2()
            fileCodeWriter.writeCall(functionName, nVars)

if __name__ == "__main__":
    inputPath = sys.argv[1]
    
    # If the input is a directory, translate each .vm file in it
    if os.path.isdir(inputPath):
        isFolder = 1
        folder_name = os.path.basename(inputPath)
        outputFile = os.path.join(inputPath, folder_name + '.asm' )
        fileCodeWriter = CodeWriter(outputFile)
        for file in os.listdir(inputPath):
            if file.endswith(".vm"):
                inputFile = os.path.join(inputPath, file)
                mainLoop(inputFile, fileCodeWriter)

    else:
        isFolder = 0
        outputFile = inputPath.rpartition('.')[0] + ".asm"
        fileCodeWriter = CodeWriter(outputFile)
        mainLoop(inputPath, fileCodeWriter)

    fileCodeWriter.close()