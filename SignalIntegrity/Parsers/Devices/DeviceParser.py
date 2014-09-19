from SignalIntegrity.SParameterFiles import File
from SignalIntegrity.SubCircuits import SubCircuit
from SignalIntegrity.Devices import Open
from SignalIntegrity.Devices import Ground
from SignalIntegrity.Devices import SeriesZ
from SignalIntegrity.Devices import MixedModeConverter
import math
from FrequencyDependent import SeriesLf
from FrequencyDependent import SeriesCf
from FrequencyDependent import Mutualf

class DeviceParser():
    def __init__(self,f,argsList):
        self.m_f=f
        self.m_sp=None
        self.m_spf=None
        if argsList is None:
            return
        if len(argsList) == 0:
            return
        if argsList[0] == 'file':
            self.m_spf=File(argsList[1]).Resample(self.m_f)
        elif argsList[0] == 'C':
            self.m_spf=SeriesCf(self.m_f,float(argsList[1]))
        elif argsList[0] == 'L':
            self.m_spf=SeriesLf(self.m_f,float(argsList[1]))
        elif argsList[0] == 'R':
            self.m_sp=SeriesZ(float(argsList[1]))
        elif argsList[0] == 'M':
            self.m_sp=Mutualf(self.m_f,float(argsList[1]))
        elif argsList[0] == 'ground':
            self.m_sp=Ground()
        elif argsList[0] == 'open':
            self.m_sp=Open()
        elif argsList[0] == 'termination':
            self.m_sp=[[0]]
        elif argsList[0] == 'subcircuit':
            self.m_spf=SubCircuit(self.m_f,argsList[1],
                ' '.join([argsList[i] for i in range(2,len(argsList))]))
        elif argsList[0] == 'mixedmode':
            self.m_sp=MixedModeConverter()
