import sys
import os
import CompilationEngine as Ce

class JackAnalyzer:
    '''Creates a CompilationEngine object from the input file and calls compileClass to start the compilation'''

    def run(inputPath):
        '''Determines wheter the input path is a file or a directiory and creates XML file/s accordingly'''

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


    if __name__ == "__main__":
        run(sys.argv[1])