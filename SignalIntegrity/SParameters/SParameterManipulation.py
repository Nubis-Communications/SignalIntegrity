'''
 Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
 Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
 All Rights Reserved.

 Explicit license in accompanying README.txt file.  If you don't have that file
 or do not agree to the terms in that file, then you are not licensed to use
 this material whatsoever.
'''
from numpy import linalg
from numpy import dot
from numpy import diag
import math

class SParameterManipulation(object):
    # locations where the largest singular value exceeds 1 are locations
    # where there are passivity violations
    def _LargestSingularValues(self):
        return [linalg.svd(m,full_matrices=False,compute_uv=False)[0]
            for m in self.m_d]
    # enforces passivity by clipping all singular values to a maximum value
    def EnforcePassivity(self,minSingularValue=1.):
        for n in range(len(self.m_d)):
            (u,s,vh)=linalg.svd(self.m_d[n],full_matrices=1,compute_uv=1)
            for si in range(len(s)):
                s[si]=min(minSingularValue,s[si])
            self.m_d[n]=dot(u,dot(diag(s),vh)).tolist()
    def IsCausal(self,threshold=0.):
        for toPort in range(self.m_P):
            for fromPort in range(self.m_P):
                fr=self.FrequencyResponse(toPort,fromPort)
                ir=fr.ImpulseResponse()
                if ir is None:
                    return False
                else:
                    x=ir.Times()
                    Ts=1./ir.TimeDescriptor().Fs
                    for k in range(len(x)):
                        if x[k]<=-Ts:
                            if abs(ir.m_y[k])>threshold:
                                return False
        return True
    def EnforceCausality(self):
        for toPort in range(self.m_P):
            for fromPort in range(self.m_P):
                fr=self.FrequencyResponse(toPort,fromPort)
                ir=fr.ImpulseResponse()
                if ir is not None:
                    x=ir.Times()
                    Ts=1./ir.TimeDescriptor().Fs
                    for k in range(len(x)):
                        if x[k]<=-Ts:
                            ir.m_y[k]=0.
                    fr=ir.FrequencyResponse()
                    frv=fr.Response()
                    for n in range(len(frv)):
                        self.m_d[n][toPort][fromPort]=frv[n]
    def WaveletDenoise(self,threshold=0.0001):
        from SignalIntegrity.Wavelets import WaveletDaubechies4
        w=WaveletDaubechies4()
        for toPort in range(self.m_P):
            for fromPort in range(self.m_P):
                fr=self.FrequencyResponse(toPort,fromPort)
                ir=fr.ImpulseResponse()
                if ir is not None:
                    irl=len(ir)
                    nirl=int(pow(2.,math.ceil(math.log(float(irl))/math.log(2.))))
                    ir=ir._Pad(nirl)
                    y=ir.Values()
                    Y=w.DWT(y)
                    Y=[0. if abs(Yv) <= threshold else Yv for Yv in Y]
                    y=w.IDWT(Y)
                    ir.m_y=y
                    ir=ir._Pad(irl)
                    fr=ir.FrequencyResponse()
                    frv=fr.Response()
                    for n in range(len(frv)):
                        self.m_d[n][toPort][fromPort]=frv[n]