'''
Created on Nov 1, 2016

@author: Peter.Pupalaikis
'''

class DiagonalMatrix(object):
    def __init__(self,other=None):
        if isinstance(other,DiagonalMatrix):
            self.list=other.list
        else:
            self.list = other
    def __getitem__(self,k):
        return self.list[k]
    def __setitem__(self,k,v):
        self.list[k] = v
    @staticmethod
    def initialized(v,RC):
        return DiagonalMatrix([v for rc in range(RC)])
    def Full(self):
        from Interleave.Matrix.Matrix import Matrix
        M=Matrix.initialized(0., len(self.list), len(self.list))
        for r in range(len(self.list)):
            M[r][r]=self.list[r]
        return M
    def rows(self):
        return len(self.list)
    def cols(self):
        return len(self.list)


