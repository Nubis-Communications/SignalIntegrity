import math
import cmath

from SignalIntegrity.SParameters.FrequencyList import *
from SignalIntegrity.SParameters.FrequencyResponse import *
from SignalIntegrity.SParameters.ImpulseResponse import *
from SignalIntegrity.Splines import Spline
from SignalIntegrity.ChirpZTransform import CZT

class ResampledFrequencyResponse(FrequencyResponse):
    def __init__(self,fr,fl,**args):
        fl=FrequencyList(fl)
        method = args['method'] if 'method' in args else 'spline'
        truncate = args['truncate'] if 'truncate' in args else True
        frf=fr.Frequency()
        if method == 'czt' and not frf.CheckEvenlySpaced():
                method = 'spline'
        highSpeed = args['speed']=='high' if 'speed' in args else True
        adjustDelay = args['adjustDelay'] if 'adjustDelay' in args else True
        if method == 'spline':
            Poly=Spline(frf,fr.Response())
            SppPrime=[Poly.Evaluate(f)
                if f <= frf[-1] or not truncate else 0.0001
                    for f in fl]
        elif method == 'czt':
            TD = cmath.phase(fr[-1])/(2.*math.pi*frf[-1]) if adjustDelay else 0.
            frd=FrequencyResponse(frf,[fr.Response()[n]*cmath.exp(-1j*2.*math.pi*frf[n]*TD) for n in range(len(fr))])
            SppPrime=CZT(frd.ImpulseResponse(),frf[-1]*2.,0.,fl.m_Fe,fl.m_Np,highSpeed)
            SppPrime = [SppPrime[np]*cmath.exp(1j*2.*math.pi*fl[np]*(TD+frf.m_Np/(frf[-1]*2.)))
                if fl[np] <= frf[-1] or not truncate else 0.001
                    for np in range(fl.m_Np+1)]
        FrequencyResponse.__init__(self,fl,SppPrime)