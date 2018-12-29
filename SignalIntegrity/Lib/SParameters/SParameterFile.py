"""
 s-parameter file
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
import os
import sys

from SignalIntegrity.Lib.SParameters.SParameters import SParameters
from SignalIntegrity.Lib.Conversions import ReferenceImpedance
from SignalIntegrity.Lib.FrequencyDomain.FrequencyList import GenericFrequencyList
from SignalIntegrity.Lib.Exception import SignalIntegrityExceptionSParameterFile

class SParameterFile(SParameters):
    """class for s-parameters read from a file"""
    def __init__(self,name,Z0=None):
        """Constructor
        @param name string file name of s-parameter file to read.
        @param Z0 (optional) real or complex reference impedance desired (defaults to 50 Ohms).
        Reads the s-parameter file and produces an instance of its base class SParameters.

        If the reference impedance of the Touchstone 1.0 file read is not the reference
        impedance specified, then the reference impedance of the s-parameters are converted
        to the reference impedance specified."""
        self.m_sToken='S'
        self.m_Z0=Z0
        # pragma: silent exclude
        ext=str.lower(name).split('.')[-1]
        if ext == 'si':
            from SignalIntegrity.App.SignalIntegrityAppHeadless import ProjectSParameters
            sp=ProjectSParameters(name)
            if not sp is None:
                SParameters.__init__(self,sp.m_f,sp.m_d,sp.m_Z0)
                return
            else:
                raise SignalIntegrityExceptionSParameterFile('s-parameters could not be produced by '+name)
        else:
            try:
            # pragma: include outdent outdent
                self.m_P=int(str.lower(name).split('.')[-1].split('s')[1].split('p')[0])
            # pragma: silent exclude indent indent
            except:
                raise SignalIntegrityExceptionSParameterFile('incorrect extension in s-parameter file name in '+name)
        # pragma: include
        freqMul = 1e6
        complexType = 'MA'
        Z0=50.
        sp=True
        f=[]
        self.m_f=[]
        numbersList=[]
        # pragma: silent exclude
        try:
        # pragma: include outdent
            spfile=open(name,'rU' if sys.version_info.major < 3 else 'r')
        # pragma: silent exclude indent
        except IOError:
            raise SignalIntegrityExceptionSParameterFile(name+' not found')
        # pragma: include
        for line in spfile:
            lineList = str.lower(line).split('!')[0].split()
            if len(lineList)>0:
                if lineList[0] == '#':
                    if 'hz' in lineList: freqMul = 1.0
                    if 'khz' in lineList: freqMul = 1e3
                    if 'mhz' in lineList: freqMul = 1e6
                    if 'ghz' in lineList: freqMul = 1e9
                    if 'ma' in lineList: complexType = 'MA'
                    if 'ri' in lineList: complexType = 'RI'
                    if 'db' in lineList: complexType = 'DB'
                    if 'r' in lineList:
                        Z0=float(lineList[lineList.index('r')+1])
                    if not self.m_sToken.lower() in lineList:
                        sp=False
                else: numbersList.extend(lineList)
        spfile.close()
        if not sp: return
        if self.m_Z0==None: self.m_Z0=Z0
        frequencies = len(numbersList)//(1+self.m_P*self.m_P*2)
        P=self.m_P
        self.m_d=[empty([P,P]).tolist() for fi in range(frequencies)]
        for fi in range(frequencies):
            f.append(float(numbersList[(1+P*P*2)*fi])*freqMul)
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
        self.m_f=GenericFrequencyList(f)
# pragma: silent exclude
if __name__ == "__main__": # pragma: no cover
    runProfiler=True

    if runProfiler:
        import cProfile
        cProfile.run('SParameterFile(\'/home/peterp/Work/PySI/PowerIntegrity/ReversePulseMode/CurrentDelayLine1p65us.s4p\')','stats')

        import pstats
        p = pstats.Stats('stats')
        p.strip_dirs().sort_stats('cumulative').print_stats(30)
    else:
        SParameterFile('/home/peterp/Work/PySI/PowerIntegrity/ReversePulseMode/CurrentDelayLine1p65us.s4p')