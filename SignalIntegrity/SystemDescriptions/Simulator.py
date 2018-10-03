"""
 Simulator Base Class for Housekeeping Functions for Simulation
"""
# Copyright (c) 2018 Teledyne LeCroy, all rights reserved worldwide.
#
# This file is part of PySI.
#
# PySI is free software: You can redistribute it and/or modify it under the terms of the
# GNU General Public License as published by the Free Software Foundation, either version
# 3 of the License, or any later version.
#
# This program is distrbuted in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this program.
# If not, see <https://www.gnu.org/licenses/>

from numpy import matrix
from numpy import identity

from SignalIntegrity.SystemDescriptions.SystemSParameters import SystemSParameters
from SignalIntegrity.SystemDescriptions.Device import Device
from SignalIntegrity.Devices import Open
from SignalIntegrity.Devices import Thru
from SignalIntegrity.Devices import Ground
from SignalIntegrity.PySIException import PySIExceptionSimulator

class Simulator(SystemSParameters,object):
    """Base class for dealing with housekeeping for simulations."""
    def __init__(self,sd=None):
        SystemSParameters.__init__(self,sd)
        self.m_ol = sd.m_ol if hasattr(sd, 'm_ol') else None
    def Check(self):
        if self.m_ol is None:
            raise PySIExceptionSimulator('no outputs')
        if len(self.StimsPrime()) == 0:
            raise PySIExceptionSimulator('no sources')
    @property
    def pOutputList(self):
        """property containing list of output waveforms
        @return the list of string names of the output waveforms
        """
        return self.m_ol
    @pOutputList.setter
    def pOutputList(self,ol=None):
        if not ol is None: self.m_ol = ol
        return self
    def AddVoltageSource(self,Name,Ports):
        """Adds a one or two port voltage source to the system.
        @param Name string name of voltage source device.
        @param Ports integer number of ports in the voltage source
        Ports can be 1 or 2."""
        if Ports == 1: self.AddDevice(Name,Ports,Ground(),'voltage source')
        elif Ports == 2: self.AddDevice(Name,Ports,Thru(),'voltage source')
        stimNumber=len(self.StimsPrime())+1
        for p in range(Ports): self.AssignM(Name,p+1,'m'+str(stimNumber+p))
    def AddCurrentSource(self,Name,Ports):
        """Adds a one or two port current source to the system.
        @param Name string name of current source device.
        @param Ports integer number of ports in the current source
        Ports can be 1 or 2."""
        if Ports == 1: self.AddDevice(Name,Ports,Open(),'current source')
        elif Ports == 2: self.AddDevice(Name,Ports,[[1.,0.],[0.,1.]],'current source')
        stimNumber=len(self.StimsPrime())+1
        for p in range(Ports): self.AssignM(Name,p+1,'m'+str(stimNumber+p))
    def SourceVector(self):
        sv=[]
        for d in self:
            if d.Type == 'current source' or d.Type == 'voltage source':
                sv.append(d.Name)
        return sv
    def SourceToStimsPrimeMatrix(self,symbolic=False):
        sv=self.SourceVector()
        sp=self.StimsPrime()
        Z0='Z0' if symbolic else 50.
        sm = [[0]*len(sv) for r in range(len(sp))]
        for s in sv:
            d=self[self.IndexOfDevice(s)]
            if d.Type == 'current source':
                if len(d) == 1:
                    sm[sp.index(d[0].M)][sv.index(s)] = Z0
                elif len(d) == 2:
                    sm[sp.index(d[0].M)][sv.index(s)] = Z0
                    sm[sp.index(d[1].M)][sv.index(s)] = Z0
            elif d.Type == 'voltage source':
                if len(d) == 1:
                    sm[sp.index(d[0].M)][sv.index(s)] = 1.
                elif len(d) == 2:
                    sm[sp.index(d[0].M)][sv.index(s)] = -1./2.
                    sm[sp.index(d[1].M)][sv.index(s)] = 1./2.
        return sm
    def StimsPrime(self):
        sv=self.StimulusVector()
        sp=[]
        for s in range(len(sv)):
            sn='m'+str(s+1)
            if sn in sv: sp.append(sn)
            else: return sp
    def SIPrime(self,symbolic=False):
        from numpy.linalg.linalg import LinAlgError
        n=self.NodeVector()
        m=self.StimulusVector()
        mprime=self.StimsPrime()
        if symbolic: SI=Device.SymbolicMatrix('Si',len(n))
        else:
            # pragma: silent exclude
            try:
            # pragma: include outdent
                SI=(matrix(identity(len(n)))-matrix(self.WeightsMatrix())).getI().tolist()
            # pragma: silent exclude indent
            except:
                raise PySIExceptionSimulator('numerical error - cannot invert matrix')
            # pragma: include
        SiPrime=[[0]*len(mprime) for r in range(len(n))]
        for c in range(len(mprime)):
            for r in range(len(n)):
                SiPrime[r][c]=SI[r][m.index('m'+str(c+1))]
        return SiPrime
    def VoltageExtractionMatrix(self,nl):
        n=self.NodeVector()
        result=[[0]*len(n) for r in range(len(nl))]
        for r in range(len(nl)):
            dp=self[self.DeviceNames().index(nl[r][0])][nl[r][1]-1]
            result[r][n.index(dp.A)]=1
            result[r][n.index(dp.B)]=1
        return result