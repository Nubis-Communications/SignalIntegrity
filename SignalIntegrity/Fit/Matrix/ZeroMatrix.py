'''
Created on Nov 1, 2016

@author: Peter.Pupalaikis
'''
class ZeroMatrix(object):
    def __init__(self,R,C=None):
        if C==None:
            C=R
        self.R = R
        self.C = C
    def Full(self):
        from Interleave.Matrix.Matrix import Matrix
        A=Matrix.initialized(0.,self.R,self.C)
        return A
    def rows(self):
        return self.R
    def cols(self):
        return self.C
    def __getitem__(self,k):
        return 0.