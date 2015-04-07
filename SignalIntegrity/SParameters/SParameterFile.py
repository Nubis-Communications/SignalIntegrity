from numpy import empty
from numpy import array
import cmath
import math
import string
from SignalIntegrity.SParameters.SParameters import SParameters
from SignalIntegrity.Conversions import ReferenceImpedance

class File(SParameters):
    def __init__(self,name,Z0=50.0):
        self.m_sToken='S'
        self.m_Z0=Z0
        self.m_P = int(string.lower(name).split('.')[-1].split('s')[1].split('p')[0])
        freqMul = 1e6
        complexType = 'MA'
        Z0=50.
        sp=True
        self.m_f=[]
        self.m_d=[]
        numbersList=[]
        try:
            spfile=open(name,'rU')
        except IOError:
            return
        for line in spfile:
            lineList = string.lower(line).split('!')[0].split()
            if len(lineList)>0:
                if lineList[0] == '#':
                    if 'hz' in lineList:
                        freqMul = 1.0
                    if 'khz' in lineList:
                        freqMul = 1e3
                    if 'mhz' in lineList:
                        freqMul = 1e6
                    if 'ghz' in lineList:
                        freqMul = 1e9
                    if 'ma' in lineList:
                        complexType = 'MA'
                    if 'ri' in lineList:
                        complexType = 'RI'
                    if 'db' in lineList:
                        complexType = 'DB'
                    if 'r' in lineList:
                        Z0=float(lineList[lineList.index('r')+1])
                    if not self.m_sToken.lower() in lineList:
                        sp=False
                else:
                    numbersList = numbersList + lineList
        spfile.close()
        if not sp:
            return
        frequencies = len(numbersList)/(1+self.m_P*self.m_P*2)
        P=self.m_P
        self.m_d=[empty([P,P]).tolist() for fi in range(frequencies)]
        for fi in range(frequencies):
            self.m_f.append(float(numbersList[(1+P*P*2)*fi])*freqMul)
            for r in range(P):
                for c in range(P):
                    n1=float(numbersList[(1+P*P*2)*fi+1+(r*P+c)*2])
                    n2=float(numbersList[(1+P*P*2)*fi+1+(r*P+c)*2+1])
                    if complexType == 'RI':
                        self.m_d[fi][r][c]=n1+1j*n2
                    else:
                        expangle=cmath.exp(1j*math.pi/180.*n2)
                        if complexType == 'MA':
                            self.m_d[fi][r][c]=n1*expangle
                        elif complexType == 'DB':
                            self.m_d[fi][r][c]=math.pow(10.,n1/20)*expangle
            if P == 2:
                self.m_d[fi]=array(self.m_d[fi]).transpose().tolist()
            if Z0 != self.m_Z0:
                self.m_d[fi]=ReferenceImpedance(self.m_d[fi],self.m_Z0,Z0)