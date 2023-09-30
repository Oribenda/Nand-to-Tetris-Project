ARGUMENT = "argument"
LOCAL = "local"
STATIC = "static"
THIS = "this"
THAT = "that"
POINTER = "pointer"
TEMP = "temp"
ADD = "add"
SUB = "sub"
NEG = "neg"
EQ = "eq"
GT = "gt"
LT = "lt"
AND = "and"
OR = "or"
NOT = "not"

class VMWriter:
    
    def __init__(self, fileName):
        self.output = open(fileName + ".vm", "w")

    def writePush(self, segment, index):
        self.output.write(f"push {segment} {index}\n")

    def writePop(self, segment, index):
        self.output.write(f"pop {segment} {index}\n")
    
    def writeArithmetic(self, command):
        self.output.write(f"{command}\n")

    def writeLabel(self, label):
        self.output.write(f"label {label}\n")

    def writeGoto(self, label):
        self.output.write(f"goto {label}\n")

    def writeIf(self, label):
        self.output.write(f"if-goto {label}\n")

    def writeCall(self, name, nVars):
        self.output.write(f"call {name} {nVars}\n")

    def writeFunction(self, name, nVars):
        self.output.write(f"function {name} {nVars}\n")

    def writeReturn(self):
        self.output.write("return\n")

    def close(self):
        self.output.close()