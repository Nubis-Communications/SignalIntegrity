"""
SParameters
"""

# Copyright (c) 2018 Teledyne LeCroy, Inc.
# All rights reserved worldwide.
#
# This file is part of SignalIntegrity.
#
# SignalIntegrity is free software: You can redistribute it and/or modify it under the terms
# of the GNU General Public License as published by the Free Software Foundation, either
# version 3 of the License, or any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this program.
# If not, see <https://www.gnu.org/licenses/>

from numpy import empty
from numpy import array
import cmath
import math
import string
import copy
import os

from SignalIntegrity.Lib.Conversions import ReferenceImpedance
from SignalIntegrity.Lib.FrequencyDomain.FrequencyList import FrequencyList
from SignalIntegrity.Lib.FrequencyDomain.FrequencyResponse import FrequencyResponse
from SignalIntegrity.Lib.SParameters.SParameterManipulation import SParameterManipulation
from SignalIntegrity.Lib.Exception import SignalIntegrityExceptionSParameterFile
from SignalIntegrity.__about__ import __project__,__version__,__description__,__url__

class SParameters(SParameterManipulation):
    """Class containing s-parameters"""
    header=['File created by '+__project__+' v'+ __version__+': '+__description__,
        __url__]
    def __init__(self,f,data,Z0=50.0):
        """Constructor
        @param f list of frequencies
        @param data list of list of list matrices were each element is a list of list s-parameter matrix.
        @param Z0 (optional) real or complex reference impedance
        """
        self.m_sToken='S'; self.m_d=data; self.m_Z0=Z0
        self.m_f=FrequencyList(f)
        if not data is None:
            if len(data)>0: self.m_P=len(data[0])
        else:
            mat=self[0]
            if not mat is None: self.m_P=len(mat[0])
    def __getitem__(self,item): return self.m_d[item]
    """overloads [item]
    @param item integer index of list of list s-parameter matrix
    @return list of list s-parameter matrix at index location
    """
    def __len__(self): return len(self.m_f)
    """overloads len()
    @return the number of frequencies in the s-parameters
    """
    def f(self): return self.m_f
    """returns the frequencies of the s-parameters
    @return list of frequencies"""
    def Response(self,ToP,FromP): return [mat[ToP-1][FromP-1] for mat in self]
    """Response
    @param ToP integer receive port
    @param FromP integer driven port
    @return list of complex as the frequency response at port ToP due to waves driven at FromP.
    @see FrequencyResponse()
    """
    def FrequencyResponse(self,ToP,FromP):
        """FrequencyResponse
        @param ToP integer receive port
        @param FromP integer driven port
        @return instance of class FrequencyResponse as the frequency response at port ToP due to waves driven at FromP.
        """
        return FrequencyResponse(self.f(),self.Response(ToP,FromP))
    def WriteToFile(self,name,formatString=None):
        """Writes the s-parameters to a file
        @param name string filename to write to
        @param formatString (optional) string containing the  format
        Writes the file in the Touchstone 1.0 format using the format string provided.

        If no format string is provided, uses ' MHz MA S R 50.0'
        """
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
                elif int(str.lower(name).split('.')[-1].split('s')[1].split('p')[0]) != self.m_P:
                    extensionCorrect=False
            if not extensionCorrect:
                raise SignalIntegrityExceptionSParameterFile('incorrect extension in s-parameter file name in '+name)
        except:
            raise SignalIntegrityExceptionSParameterFile('incorrect extension in s-parameter file name in '+name)
        # pragma: include
        freqMul = 1e6; fToken = 'MHz'; cpxType = 'MA'; Z0 = 50.0
        if not formatString is None:
            lineList = str.lower(formatString).split('!')[0].split()
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
        for lin in self.header: spfile.write(('! '+lin if lin[0] != '!' else lin)+'\n')
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
    def Resample(self,fl):
        """Resamples the s-parameters onto a new frequency scale
        @param fl list of frequencies to resample to.
        @return instance of class SParameters containing resampled s-parameters
        """
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
    def SetReferenceImpedance(self,Z0):
        """Sets the reference impedance as specified
        @param Z0 real or complex reference impedance
        @return self
        Transforms the reference impedance of self to the new reference impedance Z0.
        """
        if Z0 != self.m_Z0:
            for n in range(len(self.m_f)):
                self.m_d[n]=ReferenceImpedance(self.m_d[n],Z0,self.m_Z0)
        self.m_Z0=Z0
        return self
    ##
    # @var header
    # list of strings that form the default header written whenever files are written
    # the default is the project, version, and description and a link to the SignalIntegrity
    # website.