import math
import cmath

from SignalIntegrity.SParameters.FrequencyList import *
from SignalIntegrity.SParameters.FrequencyResponse import *
from SignalIntegrity.SParameters.ImpulseResponse import *
from SignalIntegrity.Splines import Spline
from SignalIntegrity.ChirpZTransform import CZT

class ResampledFrequencyResponse(FrequencyResponse):
    """Resamples a frequency response onto a new frequency axis.

    Attributes:
        none
    """
    def __init__(self,fr,fl,**args):
        """Produces a new resampled FrequencyResponse from a given
        FrequencyResponse resampled onto a new Frequency scale given
        by the FrequencyList according to the args.

        Args:
            fr (FrequencyResponse) a frequency response to be resampled.
            fl (FrequencyList) a frequency list containing the new scale.
            args (dict): valid arguments are:
                method: 'spline' or 'czt' - defaults to 'spline'
                    the response will be resampled using either splines or
                    the chirp z-transform method.
                truncate: True or False - defaults to True
                    the response will be truncated above the frequency information
                    in the original frequency list contained in the frequency response
                    provided.
                speed: 'high' or 'low' - defaults to 'high'
                    for debugging.  Determines whether the very simple but slow
                    or the complicated but fast definition of the chirp z-transform
                    is used if method=='czt'
                adjustDelay: True or False - defaults to True
                    when using method=='czt', a delay is employed to enforce realness
                    of the last frequency response point during calculation.
        Notes:

        """
        fl=FrequencyList(fl)
        method = args['method'] if 'method' in args else 'spline'
        truncate = args['truncate'] if 'truncate' in args else True
        frf=fr.FrequencyList()
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
            SppPrime=CZT(frd.ImpulseResponse(),frf[-1]*2.,0.,fl.Fe,fl.N,highSpeed)
            SppPrime = [SppPrime[n]*cmath.exp(1j*2.*math.pi*fl[n]*(TD+frf.N/(frf[-1]*2.)))
                if fl[n] <= frf[-1] or not truncate else 0.001
                    for n in range(fl.N+1)]
        FrequencyResponse.__init__(self,fl,SppPrime)