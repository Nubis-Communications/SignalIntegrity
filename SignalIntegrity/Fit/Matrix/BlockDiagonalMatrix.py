'''
Created on Nov 1, 2016

@author: Peter.Pupalaikis
'''
class BlockDiagonalMatrix(object):
    def __init__(self,other=None):
        if isinstance(other,BlockDiagonalMatrix):
            self.list=other.list
        else:
            self.list = other
    def __getitem__(self,k):
        return self.list[k]
    def __setitem__(self,k,v):
        self.list[k] = v
    def BlockMatrix(self):
        from Interleave.Matrix.ZeroMatrix import ZeroMatrix
        from Interleave.Matrix.BlockMatrix import BlockMatrix
        RC=self.rows()
        ML=[[ZeroMatrix(self[r].rows(),self[r].cols()) for c in range(RC)] for r in range(RC)]
        for r in self.rows():
            ML[r][r]=self[r]
        return BlockMatrix(ML)
    def Full(self):
        from Interleave.Matrix.Matrix import Matrix
        from Interleave.Matrix.DiagonalMatrix import DiagonalMatrix
        from Interleave.Matrix.IdentityMatrix import IdentityMatrix
        R=sum([self[r].rows() for r in range(self.rows())])
        C=sum([self[c].cols() for c in range(self.cols())])
        M=Matrix.initialized(0.,R,C)
        Ro=0
        Co=0
        for rc in range(self.rows()):
                for r in range(self[rc].rows()):
                    if isinstance(self[rc],(DiagonalMatrix,IdentityMatrix)):
                        M[Ro+r][Co+r]=self[rc][r]
                    else:
                        for c in range(self[rc].cols()):
                            M[Ro+r][Co+c]=self[rc][r][c]
                Co=Co+self[rc].cols()
                Ro=Ro+self[rc].rows()
        return M      
    def __mul__(self,other):
        from Interleave.Matrix.DiagonalMatrix import DiagonalMatrix
        from Interleave.Matrix.Matrix import Matrix
        from Interleave.Matrix.BlockMatrix import BlockMatrix
        if isinstance(other,(float,int,complex)):
            return BlockDiagonalMatrix([self[rc]*other for rc in range(self.rows())])
        elif isinstance(other,DiagonalMatrix):
            # BEGS FOR OPTIMIZATION
            return self.Full()*other
        elif isinstance(other,BlockDiagonalMatrix):
            return BlockDiagonalMatrix([self[rc]*other[rc] for rc in range(self.rows())])
        elif isinstance(other,BlockMatrix):
            # potential optimization
            return self.BlockMatrix()*other
        elif isinstance(other,Matrix):
            return self.Full()*other
    def rows(self):
        return len(self.list)
    def cols(self):
        return len(self.list)

