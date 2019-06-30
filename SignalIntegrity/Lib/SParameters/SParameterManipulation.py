"""
 s-parameter manipulations base class
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

from numpy import linalg,dot,diag,matrix
import math

class SParameterManipulation(object):
    """Class for manipulations on s-parameters involving passivity, causality, etc."""
    # locations where the largest singular value exceeds 1 are locations
    # where there are passivity violations
    def _LargestSingularValues(self):
        return [linalg.svd(m,full_matrices=False,compute_uv=False)[0]
            for m in self.m_d]
    def EnforcePassivity(self,maxSingularValue=1.):
        """Enforces passivity on the s-parameters.
        @param maxSingularValue (optional) float maximum singular value allowed
        Enforces passivity by clipping all singular values to a maximum value.

        the optional maximum value allows for adjusting devices with gain to a maximum
        value.  For passive devices, the maximum singular value is the default value of 1.
        """
        for n in range(len(self.m_d)):
            (u,s,vh)=linalg.svd(self.m_d[n],full_matrices=1,compute_uv=1)
            for si in range(len(s)):
                s[si]=min(maxSingularValue,s[si])
            self.m_d[n]=dot(u,dot(diag(s),vh)).tolist()
        return self
    def IsCausal(self,threshold=0.):
        """Checks whether the s-parameters are causal.
        @param threshold positive float threshold for causality detection
        @return boolean True if the absolute value of all values in the impulse response
        of each s-parameter before time zero are less
        than the threshold provided otherwise returns False.
        
        This is checked by generating the impulse response corresponding to the frequency
        response of each s-parameter from and to port combination.
        """
        for toPort in range(self.m_P):
            for fromPort in range(self.m_P):
                fr=self.FrequencyResponse(toPort,fromPort)
                ir=fr.ImpulseResponse()
                if ir is None: return False
                else:
                    t=ir.td
                    Ts=1./ir.td.Fs
                    for k in range(len(t)):
                        if t[k]<=-Ts:
                            if abs(ir[k])>threshold:
                                return False
        return True
    def EnforceCausality(self):
        """Enforces causality by setting all of the values before time zero in the impulse
        responses of the s-parameters to zero."""
        for toPort in range(self.m_P):
            for fromPort in range(self.m_P):
                fr=self.FrequencyResponse(toPort+1,fromPort+1)
                ir=fr.ImpulseResponse()
                if ir is not None:
                    t=ir.td; Ts=1./ir.td.Fs
                    for k in range(len(t)):
                        if t[k]<=-Ts: ir[k]=0.
                    fr=ir.FrequencyResponse()
                    frv=fr.Response()
                    for n in range(len(frv)): self.m_d[n][toPort][fromPort]=frv[n]
        return self
    def WaveletDenoise(self,threshold=0.0001):
        """Denoises the s-parameters
        @param threshold (optional) float threshold for the wavelets (defaults to 0.0001).
        Denoises the s-parameter by computing the wavelet transform of the impulse response
        for each s-parameter from and to port combination and keeping only the wavelets whoe
        absolute value is above the threshold."""
        from SignalIntegrity.Lib.Wavelets import WaveletDaubechies4
        w=WaveletDaubechies4()
        for toPort in range(self.m_P):
            for fromPort in range(self.m_P):
                fr=self.FrequencyResponse(toPort+1,fromPort+1)
                ir=fr.ImpulseResponse()
                if ir is not None:
                    irl=len(ir)
                    nirl=int(pow(2.,math.ceil(math.log(float(irl))/math.log(2.))))
                    ir=ir._Pad(nirl)
                    y=ir.Values()
                    Y=w.DWT(y)
                    Y=[0. if abs(Yv) <= threshold else Yv for Yv in Y]
                    y=w.IDWT(Y)
                    #ir.x=y
                    # @todo get rid of this hack
                    ir.__init__(ir.TimeDescriptor(),y)
                    ir=ir._Pad(irl)
                    fr=ir.FrequencyResponse()
                    frv=fr.Response()
                    for n in range(len(frv)):
                        self.m_d[n][toPort][fromPort]=frv[n]
        return self
    def PortReorder(self,pr):
        """Reorders the ports to port ordering of the port numbers supplied.
        @param pr list of integer one-based port numbers
        @return new instance of reordered s-parameters
        """
        import copy
        sp=copy.deepcopy(self)
        pr=[p-1 for p in pr] # convert to 0 based indices
        sp.m_d=[[[sp.m_d[n][pr[r]][pr[c]]
                for c in range(len(pr))]
                    for r in range(len(pr))]
                        for n in range(len(sp.m_d))]
        return sp
    def DetermineImpulseResponseLength(self,epsilon=1e-6,allLengths=False):
        """determines the impulse response lengths of the ports by comparing impulse response to threshold.
        @param epsilon (optional, defaults to 1e-6) absolute threshold on impulse response.
        @param allLengths (optional, defaults to False) whether to return the lengths of each port combination
        @return returns a tuple containining (negativeTime,positiveTime) if allLengths is false (default) containing
        the most negative time and most positive time for all impulse responses, otherwise if allLengths is true, it returns
        a list of list of tuples as stated for each impulse response.
        """
        lengths=[[(None,None) for _ in range(self.m_P)] for _ in range(self.m_P)]
        for toPort in range(self.m_P):
            for fromPort in range(self.m_P):
                (negativeTimeLimit,positiveTimeLimit)=(None,None)
                fr=self.FrequencyResponse(toPort+1,fromPort+1)
                ir=fr.ImpulseResponse()
                if ir is not None:
                    t=ir.td
                    for k in range(len(t)):
                        if t[k]<0.:
                            if negativeTimeLimit is None:
                                if abs(ir[k])>epsilon:
                                    negativeTimeLimit=t[k]
                        else:
                            if abs(ir[k])>epsilon:
                                positiveTimeLimit=t[k]
                    if negativeTimeLimit is None:
                        negativeTimeLimit=0.0
                    if positiveTimeLimit is None:
                        positiveTimeLimit=0.0
                    maxlength=ir.td.K/ir.td.Fs/2.
                    negativeTimeLimit=max(-maxlength,math.floor(negativeTimeLimit*ir.td.Fs)/ir.td.Fs)
                    positiveTimeLimit=min(maxlength,math.ceil(positiveTimeLimit*ir.td.Fs)/ir.td.Fs)
                    lengths[toPort][fromPort]=(negativeTimeLimit,positiveTimeLimit)
        if allLengths: return lengths
        negativeLengths=[lengths[toPort][fromPort][0] for toPort in range(self.m_P) for fromPort in range(self.m_P)]
        positiveLengths=[lengths[toPort][fromPort][1] for toPort in range(self.m_P) for fromPort in range(self.m_P)]
        if all(length is None for length in negativeLengths): minNegativeLengths = None
        else:
            negativeLengths=[length if length is not None else 0.0 for length in negativeLengths]
            minNegativeLengths = min(negativeLengths)
        if all(length is None for length in positiveLengths): maxPositiveLengths = None
        else:
            positiveLengths=[length if length is not None else 0.0 for length in positiveLengths]
            maxPositiveLengths = max(positiveLengths)
        return (minNegativeLengths,maxPositiveLengths)
    def LimitImpulseResponseLength(self,lengths):
        """limits the impulse response length of the ports
        @param lengths tuple or list of list of tuple impulse response lengths where the
        tuple contains the negative time limit and the positive time limit.
        @return self (with impulse responses limited)
        @remark if the lengths are a single number, it is assumed to be the single
        length, otherwise if the lengths is a list of list, it is length to be enforced
        for each port-port connection.
        """
        if lengths is None: return self
        if not isinstance(lengths,list):
            lengths=[[lengths for _ in range(self.m_P)] for _ in range(self.m_P)]
        for toPort in range(self.m_P):
            for fromPort in range(self.m_P):
                (negativeTimeLimit,positiveTimeLimit)=lengths[toPort][fromPort]
                fr=self.FrequencyResponse(toPort+1,fromPort+1)
                ir=fr.ImpulseResponse()
                if ir is not None:
                    t=ir.td
                    for k in range(len(t)):
                        if t[k]<=negativeTimeLimit:
                            ir[k]=0.
                        if t[k]>=positiveTimeLimit:
                            ir[k]=0.
                    fr=ir.FrequencyResponse()
                    frv=fr.Response()
                    for n in range(len(frv)):
                        self.m_d[n][toPort][fromPort]=frv[n]
        return self
    def EnforceReciprocity(self):
        for n in range(len(self.m_d)):
            for r in range(len(self.m_d[n])):
                for c in range(r,len(self.m_d[n])):
                    if c>r:
                        self.m_d[n][r][c]=(self.m_d[n][r][c]+self.m_d[n][c][r])/2.
                        self.m_d[n][c][r]=self.m_d[n][r][c]
        return self