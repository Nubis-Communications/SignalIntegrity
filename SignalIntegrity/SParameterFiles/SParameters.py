from numpy import empty
from numpy import array
import cmath
import math

class SParameters():
    def __init__(self,f,data,Z0=50.0):
        self.m_f=f
        self.m_d=data
        self.m_Z0=Z0
        if not data is None:
            if len(data)>0:
                self.m_P=len(data[0])
    def __getitem__(self,item):
        return self.m_d[item]
    def __len__(self):
        return len(self.m_f)
    def f(self):
        return self.m_f
    def Data(self):
        return self.m_d
    def Response(self,ToP,FromP):
        return [mat[ToP-1][FromP-1] for mat in self.m_d]
    def Resample(self,f):
        from SignalIntegrity.Splines import Spline
        res=[]
        x=self.m_f
        for r in range(self.m_P):
            resr=[]
            for c in range(self.m_P):
                y=self.Response(r+1,c+1)
                P=Spline(x,y)
                resr.append([P.Evaluate(fi) for fi in f])
            res.append(resr)
        resd = []
        for n in range(len(f)):
            mat=empty(shape=(self.m_P,self.m_P)).tolist()
            for r in range(self.m_P):
                for c in range(self.m_P):
                    mat[r][c]=res[r][c][n]
            resd.append(mat)
        self.m_d=resd
        self.m_f=f
        return self
    def WriteToFile(self,name):
        spfile=open(name,'w')
        spfile.write('# MHz MA S R 50\n')
        for n in range(len(self.m_f)):
            line=[str(self.m_f[n]/1e6)]
            mat=self.m_d[n]
            if self.m_P == 2:
                mat=array(mat).transpose().tolist()
            for r in range(self.m_P):
                for c in range(self.m_P):
                    val = mat[r][c]
                    mag = abs(val)
                    ang = cmath.phase(val)*180./math.pi
                    line.append(str(mag))
                    line.append(str(ang))
            pline = ' '.join(line)+'\n'
            spfile.write(pline)
        spfile.close()
    def AreEqual(self,sp,epsilon):
        if len(self) != len(sp):
            return False
        if len(self.m_d) != len(sp.m_d):
            return False
        for n in range(len(self.Data())):
            if abs(self.m_f[n] - sp.m_f[n]) > epsilon:
                return False
            for r in range(self.m_P):
                for c in range(self.m_P):
                    if abs(self.m_d[n][r][c] - sp.m_d[n][r][c]) > epsilon:
                        return False
        return True

