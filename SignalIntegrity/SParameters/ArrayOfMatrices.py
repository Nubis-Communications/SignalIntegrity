'''
 Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
 Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
 All Rights Reserved.

 Explicit license in accompanying README.txt file.  If you don't have that file
 or do not agree to the terms in that file, then you are not licensed to use
 this material whatsoever.
'''
class ArrayOfMatrices(object):
    def __init__(self,d):
        from SignalIntegrity.SParameters.MatrixOfArrays import MatrixOfArrays
        if isinstance(d,ArrayOfMatrices):
            self.data=d
        elif isinstance(d,MatrixOfArrays):
            self.data=d.ArrayOfMatrices()
        else: self.data=d
    def __getitem__(self,item): return self.data[item]
    def __len__(self): return len(self.data)
    def MatrixOfArrays(self):
        from SignalIntegrity.SParameters.MatrixOfArrays import MatrixOfArrays
        return MatrixOfArrays([[[self.data[n][r][c] for n in range(len(self.data))] for c in range(len(self.data[0][0]))] for r in range(len(self.data[0]))])
    def ArrayOfMatrices(self):
        return self
    def NumMatrices(self):
        return len(self.data)
    def NumRows(self):
        return len(self.data[0])
    def NumCols(self):
        return len(self.data[0][0])
    def ArrayLength(self):
        return NumMatrices(self)
    def GetMatrix(self,n):
        return self.data[n]
    def SetMatrix(self,n,m):
        self.data[n]=m
        return self
    def GetArray(self,r,c):
        return [self.data[n][r][c] for n in range(len(self.data))]
    def SetArray(self,r,c,a):
        for n in range(len(self.data)):
            self.data[n][r][c] = a[n]
        return self

class EmptyArrayOfMatrices(ArrayOfMatrices):
    def __init__(self,R,C,N):
        ArrayOfMatrices.__init__(self,[[[0 for c in range(C)] for r in range(R)] for n in range(N)])

