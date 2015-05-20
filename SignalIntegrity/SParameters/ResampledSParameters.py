from SignalIntegrity.SParameters.SParameters import SParameters
from SignalIntegrity.Splines import Spline
from SignalIntegrity.ChirpZTransform import CZT
from SignalIntegrity.SParameters.FrequencyList import *
from SignalIntegrity.SParameters.FrequencyResponse import FrequencyResponse

from numpy import fft
import cmath
import math
from numpy import empty

class ResampledSParameters(SParameters):
    def __init__(self,S,fl,**args):
        fl=FrequencyList(fl)
        SppR=[empty((S.m_P,S.m_P)).tolist() for n in range(fl.N+1)]
        for o in range(S.m_P):
            for i in range(S.m_P):
                res = FrequencyResponse(S.f(),S.Response(o+1,i+1)).Resample(fl,**args)
                for n in range(len(fl)):
                    SppR[n][o][i]=res[n]
        SParameters.__init__(self,fl,SppR,S.m_Z0)