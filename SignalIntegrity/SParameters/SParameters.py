"""
SParameters
"""
# Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
# Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
# All Rights Reserved.
#
# Explicit license in accompanying README.txt file.  If you don't have that file
# or do not agree to the terms in that file, then you are not licensed to use
# this material whatsoever.

from numpy import empty
from numpy import array
import cmath
import math
import string
import copy
import os

from SignalIntegrity.Conversions import ReferenceImpedance
from SignalIntegrity.FrequencyDomain.FrequencyList import FrequencyList
from SignalIntegrity.FrequencyDomain.FrequencyResponse import FrequencyResponse
from SParameterManipulation import SParameterManipulation
from SignalIntegrity.PySIException import PySIExceptionSParameterFile

## SParameters
#
# class containing s-parameters
#
class SParameters(SParameterManipulation):
    ## Constructor
    #
    # @param f list of frequencies
    # @param data list of list of list matrices were each element is a list of list s-parameter matrix.
    # @param Z0 (optional) real or complex reference impedance
    #
    def __init__(self,f,data,Z0=50.0):
        self.m_sToken='S'; self.m_d=data; self.m_Z0=Z0
        self.m_f=FrequencyList(f)
        if not data is None:
            if len(data)>0: self.m_P=len(data[0])
        else:
            mat=self[0]
            if not mat is None: self.m_P=len(mat[0])
    ## overloads [item]
    #
    # @param item integer index of list of list s-parameter matrix
    # @return list of list s-parameter matrix at index location
    #
    def __getitem__(self,item): return self.m_d[item]
    ## overloads len()
    #
    # @return the number of frequencies in the s-parameters
    #
    def __len__(self): return len(self.m_f)
    ## f
    #
    # @return list of frequencies
    #
    def f(self): return self.m_f
    ## Response
    #
    # @param ToP integer receive port
    # @param FromP integer driven port
    # @return list of complex as the frequency response at port ToP due to waves driven at FromP.
    #
    # @see FrequencyResponse()
    #
    def Response(self,ToP,FromP): return [mat[ToP-1][FromP-1] for mat in self]
    ## FrequencyResponse
    #
    # @param ToP integer receive port
    # @param FromP integer driven port
    # @return instance of class FrequencyResponse as the frequency response at port ToP due to waves driven at FromP.
    #
    def FrequencyResponse(self,ToP,FromP):
        return FrequencyResponse(self.f(),self.Response(ToP,FromP))
    ## WriteToFile
    #
    # @param name string filename to write to
    # @param formatString (optional) string containing the # format
    #
    # Writes the file in the Touchstone 1.0 format using the format string provided.
    #
    # If no format string is provided, uses '# MHz MA S R 50.0'
    #
    def WriteToFile(self,name,formatString=None):
        # pragma: silent exclude
        try:
            filename, file_extension = os.path.splitext(name)
            extensionCorrect=True
            if file_extension=='' or file_extension is None:
                name=name+'.s'+str(self.m_P)+'p'
            else:
                file_extension=file_extension.lower()
                if len(file_extension)<4:
                    extensionCorrect=False
                elif file_extension[1]!='s':
                    extensionCorrect=False
                elif file_extension[-1]!='p':
                    extensionCorrect=False
                elif int(string.lower(name).split('.')[-1].split('s')[1].split('p')[0]) != self.m_P:
                    extensionCorrect=False
            if not extensionCorrect:
                raise PySIExceptionSParameterFile('incorrect extension in s-parameter file name in '+name)
        except:
            raise PySIExceptionSParameterFile('incorrect extension in s-parameter file name in '+name)
        # pragma: include
        freqMul = 1e6; fToken = 'MHz'; cpxType = 'MA'; Z0 = 50.0
        if not formatString is None:
            lineList = string.lower(formatString).split('!')[0].split()
            if len(lineList)>0:
                if 'hz' in lineList: fToken = 'Hz'; freqMul = 1.0
                if 'khz' in lineList: fToken = 'KHz'; freqMul = 1e3
                if 'mhz' in lineList: fToken = 'MHz'; freqMul = 1e6
                if 'ghz' in lineList: fToken = 'GHz'; freqMul = 1e9
                if 'ma' in lineList: cpxType = 'MA'
                if 'ri' in lineList: cpxType = 'RI'
                if 'db' in lineList: cpxType = 'DB'
                if 'r' in lineList: Z0=float(lineList[lineList.index('r')+1])
        spfile=open(name,'w')
        spfile.write('# '+fToken+' '+cpxType+' '+self.m_sToken+' R '+str(Z0)+'\n')
        for n in range(len(self.m_f)):
            line=[str(self.m_f[n]/freqMul)]
            mat=self[n]
            if Z0 != self.m_Z0: mat=ReferenceImpedance(mat,Z0,self.m_Z0)
            if self.m_P == 2: mat=array(mat).transpose().tolist()
            for r in range(self.m_P):
                for c in range(self.m_P):
                    val = mat[r][c]
                    if cpxType == 'MA':
                        line.append(str(round(abs(val),6)))
                        line.append(str(round(cmath.phase(val)*180./math.pi,6)))
                    elif cpxType == 'RI':
                        line.append(str(round(val.real,6)))
                        line.append(str(round(val.imag,6)))
                    elif cpxType == 'DB':
                        line.append(str(round(20*math.log10(abs(val)),6)))
                        line.append(str(round(cmath.phase(val)*180./math.pi,6)))
            pline = ' '.join(line)+'\n'
            spfile.write(pline)
        spfile.close()
        return self
    ## Resample
    #
    # @param fl list of frequencies to resample to.
    # @return instance of class SParameters containing resampled s-parameters
    #
    def Resample(self,fl):
        if self.m_d is None:
            self.m_f=fl
            copy.deepcopy(self)
        fl=FrequencyList(fl)
        f=FrequencyList(self.f()); f.CheckEvenlySpaced()
        SR=[empty((self.m_P,self.m_P)).tolist() for n in range(fl.N+1)]
        for o in range(self.m_P):
            for i in range(self.m_P):
                res = FrequencyResponse(f,self.Response(o+1,i+1)).Resample(fl)
                for n in range(len(fl)):
                    SR[n][o][i]=res[n]
        return SParameters(fl,SR,self.m_Z0)
    ## SetReferenceImpedance
    #
    # @param Z0 real or complex reference impedance
    # @return self
    #
    # Transforms the reference impedance of self to the new reference impedance Z0.
    #
    def SetReferenceImpedance(self,Z0):
        if Z0 != self.m_Z0:
            for n in range(len(self.m_f)):
                self.m_d[n]=ReferenceImpedance(self.m_d[n],Z0,self.m_Z0)
        self.m_Z0=Z0
        return self