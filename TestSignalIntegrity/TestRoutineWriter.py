import unittest

from TestHelpers import *

class TestRoutineWriter(unittest.TestCase,RoutineWriterTesterHelper):
    def __init__(self, methodName='runTest'):
        RoutineWriterTesterHelper.__init__(self)
        unittest.TestCase.__init__(self,methodName)
    def testExampleCode(self):
        self.WriteCode('TestSystemDescription.py','testSystemDescriptionExampleBlock(self)',self.standardHeader)
    def testSymbolicSolutionExample1Code(self):
        self.WriteCode('TestBook.py','testSymbolicSolutionExample1(self)',self.standardHeader)
    def testSymbolicSolutionParserExample2Code(self):
        self.WriteCode('TestBook.py','testSymbolicSolutionParserExample2(self)',self.standardHeader)
    def testSymbolicSolutionParserFileExample3Code(self):
        self.WriteCode('TestBook.py','testSymbolicSolutionParserFileExample3(self)',self.standardHeader)
    def testSystemDescriptionExampleCode(self):
        self.WriteCode('TestBook.py','testSystemDescriptionExample(self)',self.standardHeader)
    def testSymbolicDeembeddingExample1Code(self):
        self.WriteCode('TestBook.py','testSymbolicDeembeddingExample1(self)',self.standardHeader)
    def testSymbolicDeembeddingParserExample2Code(self):
        self.WriteCode('TestBook.py','testSymbolicDeembeddingParserExample2(self)',self.standardHeader)
    def testSymbolicDeembeddingParserFileExample3Code(self):
        self.WriteCode('TestBook.py','testSymbolicDeembeddingParserFileExample3(self)',self.standardHeader)
    def testSymbolicDeembeddingExample4Code(self):
        self.WriteCode('TestBook.py','testSymbolicDeembeddingExample4(self)',self.standardHeader)
    def testSymbolicDeembeddingExample5Code(self):
        self.WriteCode('TestBook.py','testSymbolicDeembeddingExample5(self)',self.standardHeader)
    def testSymbolicVirtualProbeExample1Code(self):
        self.WriteCode('TestBook.py','testSymbolicVirtualProbeExample1(self)',self.standardHeader)
    def testSymbolicVirtualProbeExample2Code(self):
        self.WriteCode('TestBook.py','testSymbolicVirtualProbeExample2(self)',self.standardHeader)
    def testSymbolicVirtualProbeExample3Code(self):
        self.WriteCode('TestBook.py','testSymbolicVirtualProbeExample3(self)',self.standardHeader)
    def testSymbolicVirtualProbeParserFileExample4Code(self):
        self.WriteCode('TestBook.py','testSymbolicVirtualProbeParserFileExample4(self)',self.standardHeader)

if __name__ == '__main__':
    unittest.main()