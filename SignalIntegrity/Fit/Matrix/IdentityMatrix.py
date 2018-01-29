'''
Created on Nov 1, 2016

@author: Peter.Pupalaikis
'''
class IdentityMatrix(object):
    def __init__(self,RC):
        self.RC = RC
    def Full(self):
        from Interleave.Matrix.Matrix import Matrix
        A=Matrix.initialized(0,self.RC,self.RC)
        for k in range(self.RC):
            A[k][k]=1
        return A
    def rows(self):
        return self.RC
    def cols(self):
        return self.RC
    def __getitem__(self,k):
        return 1.
    def kron(self,M):
        from Interleave.Matrix.BlockDiagonalMatrix import BlockDiagonalMatrix
        return BlockDiagonalMatrix([M for i in range(self.RC)])
    def __mul__(self,other):
        if isinstance(other,(float,int,complex)):
            return DiagonalMatrix([other for r in self.rows()])
        else:
            return other