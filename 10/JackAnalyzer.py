import sys
import os
import CompilationEngine as Ce

class JackAnalyzer:

    if __name__ == "__main__":

        #inputPath = sys.argv[1]
        inputPath = '/Users/ori/nand2tetris/projects/10/Square/Square.jack'

        # If the input is a directory, translate each .vm file in it under one .asm file
        if os.path.isdir(inputPath):

            for file in os.listdir(inputPath):
                if file.endswith(".jack"):
                    inputFile = os.path.join(inputPath, file)
                    outputFile = inputFile.rpartition('.')[0]
                    compilationEngine = Ce.CompilationEngine(inputFile, outputFile)
                    compilationEngine.compileClass()

        else:
            outputFile = inputPath.rpartition('.')[0]
            compilationEngine = Ce.CompilationEngine(inputPath, outputFile)
            compilationEngine.compileClass()