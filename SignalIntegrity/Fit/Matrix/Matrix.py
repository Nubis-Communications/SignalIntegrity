import cmath
import math
from numpy import kron
from numpy import matrix
from numpy import dot
import copy

from DiagonalMatrix import DiagonalMatrix
from BlockMatrix import BlockMatrix
from BlockDiagonalMatrix import BlockDiagonalMatrix
from IdentityMatrix import IdentityMatrix
from ZeroMatrix import ZeroMatrix

class Matrix(object):
    def __init__(self,other=None):
        if isinstance(other,Matrix):
            self.list=other.list
        else:
            self.list = other
    def __getitem__(self,k):
        return self.list[k]
    def __setitem__(self,k,v):
        self.list[k] = v
    def __mul__(self,other):
        if isinstance(other,(float,int,complex)):
            return Matrix((matrix(self.list)*other).tolist())
        elif isinstance(other,DiagonalMatrix):
            return Matrix([[self[r][c]*other[c] for c in range(len(other.list))] for r in range(len(self.list))])
        elif isinstance(other,(BlockMatrix,BlockDiagonalMatrix)):
            return self*other.Full()
        elif isinstance(other,Matrix):
            return Matrix((matrix(self.list)*matrix(other.list)).tolist())
            #return Matrix([[sum([self[r][i]*other[i][c] for i in range(self.cols())]) for c in range(other.cols())] for r in range(self.rows())])
        elif isinstance(other,IdentityMatrix):
            return self
        elif isinstance(other,ZeroMatrix):
            return ZeroMatrix(self.rows(),other.cols())
    def __sub__(self,other):
        return Matrix((matrix(self.list)-matrix(other.list)).tolist())
    def __add__(self,other):
        return Matrix((matrix(self.list)+matrix(other.list)).tolist())
    def __radd__(self, other):
        if other == 0:
            return self
        else:
            return self.__add__(other)
    def __div__(self,other):
        if isinstance(other,(float,int,complex)):
            return Matrix((matrix(self.list)/other).tolist())
        else:
            return Matrix((matrix(self.list)/matrix(other.list)).tolist())
    def dagger(self):
        return Matrix(matrix(self.list).getI().tolist())
    def submatrix(self,rs,re,cs,ce):
        R=re-rs+1
        C=ce-cs+1
        S=Matrix.initialized(0,R,C)
        for r in range(0,R):
            for c in range(0,C):
                S[r][c]=self[rs+r][cs+c]
        return S
    def I(self):
        return Matrix(matrix(self.list).getI().tolist())
    @staticmethod
    def identity(K):
        A=Matrix.initialized(0,K,K)
        for k in range(K):
            A[k][k]=1
        return A
    @staticmethod
    def initialized(v,R,C):
        return Matrix([[v for c in range(C)] for r in range(R)])
    def tolist(self):
        return self.list
    def T(self):
        return Matrix(matrix(self.list).transpose().tolist())
    def kron(self,other):
        return Matrix(kron(matrix(self.list),matrix(other.list)).tolist())
    def norm(self):
        R=self.rows()
        C=self.cols()
        acc=0
        for r in range(R):
            for c in range(C):
                acc=acc+abs(self[r][c])*abs(self[r][c])
        return math.sqrt(acc)
    def col(self,c):
        return self.submatrix(0,self.rows()-1,c,c)
    def row(self,r):
        return Matrix(self.list[r])
    def aug(self,other):
        A = self.list
        B = other.list
        if A is None:
            return Matrix(B)
        for r in range(len(A)):
            for c in range(len(B[r])):
                A[r].append(B[r][c])
        return Matrix(A)
    def rows(self):
        return len(self.list)
    def cols(self):
        return len(self.list[0])
    @staticmethod
    def diag(R):
        K=R.rows()
        I=R.cols()
        A=Matrix.initialized(0,K*I,K*I)
        for k in range(K):
            for i in range(I):
                A[k+K*i][k+K*i]=R[k][i]
        return A
    def real(self):
        return Matrix(matrix(self.list).real.tolist())
    def int(self):
        RF = Matrix(self.list)
        for r in range(RF.rows()):
            for c in range(RF.cols()):
                RF[r][c]=int(RF[r][c])
        return RF
    def conjugate(self):
        RF = Matrix(self.list)
        for r in range(RF.rows()):
            for c in range(RF.cols()):
                RF[r][c]=RF[r][c].conjugate()
        return RF
    def H(self):
        return Matrix(matrix(self.list).getH().tolist())
    def __lt__(self, other):
        return self.list < other.list
    def __le__(self, other):
        return self.list <= other.list
    def __eq__(self, other):
        return self.list == other.list
    def __ne__(self, other):
        return self.list != other.list
    def __gt__(self, other):
        return self.list > other.list
    def __ge__(self, other):
        return self.list >= other.list
    def copy(self):
        return Matrix(copy.deepcopy(self.list))
    def vectorize(self):
        R=self.rows()
        C=self.cols()
        th=0
        v=Matrix.initialized(0.0,R*C,1)
        for c in range(C):
            for r in range(R):
                v[th][0]=self[r][c]
                th=th+1
        return v
    def Partition(self,RC):
        if isinstance(RC,tuple):
            (R,C)=RC
        elif isinstance(RC,int):
            R=RC
            C=RC
        RB=self.rows()/R
        CB=self.cols()/C
        return BlockMatrix([[self.submatrix(r*R, r*R+R-1, c*C, c*C+C-1) for c in range(CB)] for r in range(RB)])
    def Full(self):
        return self
    def PartitionDiag(self,RC):
        if isinstance(RC,tuple):
            (R,C)=RC
        elif isinstance(RC,int):
            R=RC
            C=RC
        RB=self.rows()/R
        CB=self.cols()/C
        if RB != CB:
            raise
        return BlockDiagonalMatrix([self.submatrix(rc*R, rc*R+R-1, rc*C, rc*C+C-1) for rc in range(CB)])


