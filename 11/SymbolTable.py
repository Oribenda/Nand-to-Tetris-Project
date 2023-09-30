STATIC = "static"
FIELD = "field"
ARG = "argument"
VAR = "local"

class SymbolTable:

    def __init__(self):
        self.table = {}
        self.fieldCounter = 0
        self.staticCounter = 0
        self.argumentCounter = 0
        self.localCounter = 0

    def reset(self):
        self.table = {}
        self.fieldCounter = 0
        self.staticCounter = 0
        self.argumentCounter = 0
        self.localCounter = 0

    def define(self, name, type, kind):
        if kind == STATIC:
            self.table[f"{name}"] = [type, STATIC, self.staticCounter]
            self.staticCounter += 1
        elif kind == FIELD:
            self.table[f"{name}"] = [type, FIELD, self.fieldCounter]
            self.fieldCounter += 1
        elif kind == ARG:
            self.table[f"{name}"] = [type, ARG, self.argumentCounter]
            self.argumentCounter += 1
        elif kind == VAR:
            self.table[f"{name}"] = [type, VAR, self.localCounter]
            self.localCounter += 1

    def varCount(self, kind):
        if kind == "STATIC":
            return self.staticCounter
        elif kind == "FIELD":
            return self.fieldCounter
        elif kind == "ARG":
            return self.argumentCounter
        elif kind == "VAR":
            return self.localCounter
        
    def kindOf(self, name):
        value = self.table.get(name)
        if value:
            return value[1]
        return value
    
    def typeOf(self, name):
        return self.table[name][0]
        
    def indexOf(self, name):
        return self.table[name][2]
    
# st = SymbolTable()
# st.define("x", "int", FIELD)
# print(st.table)
# print(st.typeOf("x"))
# print(st.kindOf("x"))
# print(st.indexOf("x"))
# st.define("y", "int", FIELD)
# print(st.typeOf("y"))
# print(st.kindOf("y"))
# print(st.indexOf("y"))