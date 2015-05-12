class MatrixOfArrays(object):
    def __init__(self,d):
        from SignalIntegrity.SParameters.ArrayOfMatrices import ArrayOfMatrices
        if isinstance(d,ArrayOfMatrices):
            self.data=d.MatrixOfArrays()
        elif isinstance(d,MatrixOfArrays):
            self.data=d
        else: self.data=d
    def __getitem__(self,item): return self.data[item]
    def __len__(self): return len(self.data)
    def ArrayOfMatrices(self):
        from SignalIntegrity.SParameters.ArrayOfMatrices import ArrayOfMatrices
        return ArrayOfMatrices([[[self.data[r][c][n] for c in range(len(self.data[0]))] for r in range(len(self.data))] for n in range(len(self.data[0][0]))])
    def MatrixOfArrays(self):
        return self
    def NumMatrices(self):
        return len(self.data[0][0])
    def NumRows(self):
        return len(self.data)
    def NumCols(self):
        return len(self.data[0])
    def ArrayLength(self):
        return NumMatrices(self)
    def GetMatrix(self,n):
        return [[self.data[r][c][n] for c in range(len(self.data[0]))] for r in range(len(self.data))]
    def SetMatrix(self,n,m):
        for r in range(len(self.data)):
            for c in range(len(self.data[0])):
                self.data[n]=m[r][c]
        return self
    def GetArray(self,r,c):
        return self.data[r][c]
    def SetArray(self,r,c,a):
        self.data[r][c] = a
        return self

class EmptyMatrixOfArrays(MatrixOfArrays):
    def __init__(self,R,C,N):
        MatrixOfArrays.__init__(self,[[[0 for n in range(N)] for c in range(C)] for r in range(R)])