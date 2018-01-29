'''
Created on Nov 1, 2016

@author: Peter.Pupalaikis
'''
class BlockMatrix(object):
    def __init__(self,other=None):
        if isinstance(other,BlockMatrix):
            self.list=other.list
        else:
            self.list = other
    def __getitem__(self,k):
        return self.list[k]
    def __setitem__(self,k,v):
        self.list[k] = v
    def Full(self):
        from Interleave.Matrix.Matrix import Matrix
        from Interleave.Matrix.DiagonalMatrix import DiagonalMatrix
        from Interleave.Matrix.IdentityMatrix import IdentityMatrix
        R=sum([self[r][0].rows() for r in range(self.rows())])
        C=sum([self[0][c].cols() for c in range(self.cols())])
        M=Matrix.initialized(0.,R,C)
        Ro=0
        for rb in range(self.rows()):
            Co=0
            for cb in range(self.cols()):
                for r in range(self[rb][cb].rows()):
                    if isinstance(self[rb][cb],(DiagonalMatrix,IdentityMatrix)):
                        M[Ro+r][Co+r]=self[rb][cb][r]
                    else:
                        for c in range(self[rb][cb].cols()):
                            M[Ro+r][Co+c]=self[rb][cb][r][c]
                Co=Co+self[rb][cb].cols()
            Ro=Ro+self[rb][0].rows()
        return M      
    def __mul__(self,other):
        from Interleave.Matrix.DiagonalMatrix import DiagonalMatrix
        from Interleave.Matrix.BlockDiagonalMatrix import BlockDiagonalMatrix
        from Interleave.Matrix.Matrix import Matrix
        if isinstance(other,(float,int,complex)):
            return BlockMatrix([[self[r][c]*other for c in range(self.cols())] for r in range(self.rows())])
        elif isinstance(other,DiagonalMatrix):
            return self.Full()*other
        elif isinstance(other,BlockMatrix):
            return BlockMatrix([[sum([self[r][i]*other[i][c] for i in range(self.cols())]) for c in range(other.cols())] for r in range(self.rows())])
        elif isinstance(other,BlockDiagonalMatrix):
            return BlockMatrix(([[self[r][c]*other[c] for c in range(other.cols())] for r in range(self.rows())]))
        elif isinstance(other,Matrix):
            return self.Full()*other
    def rows(self):
        return len(self.list)
    def cols(self):
        return len(self.list[0])
    def diag(self):
        from Interleave.Matrix.BlockDiagonalMatrix import BlockDiagonalMatrix
        return BlockDiagonalMatrix([self[r][r] for r in range(self.rows())])
    def Partition(self,RC):
        if isinstance(RC,tuple):
            (R,C)=RC
        elif isinstance(RC,int):
            R=RC
            C=RC
        for r in range(self.rows()):
            for c in range(self.cols()):
                if (self[r][c].rows() != R) or (self[r][c].cols() != C):
                    return self.Full().Partition((R,C))
        return self
    def PartitionDiag(self,RC):
        if isinstance(RC,tuple):
            (R,C)=RC
        elif isinstance(RC,int):
            R=RC
            C=RC
        for r in range(self.rows()):
            for c in range(self.cols()):
                if (self[r][c].rows() != R) or (self[r][c].cols() != C):
                    return self.Full().PartitionDiag((R,C))
        return self.diag()