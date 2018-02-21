"""
numeric virtual probing solutions from netlists
"""
# Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
# Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
# All Rights Reserved.
#
# Explicit license in accompanying README.txt file.  If you don't have that file
# or do not agree to the terms in that file, then you are not licensed to use
# this material whatsoever.
from SignalIntegrity.Parsers.VirtualProbeParser import VirtualProbeParser
from SignalIntegrity.SystemDescriptions import VirtualProbeNumeric
from SignalIntegrity.FrequencyDomain.TransferMatrices import TransferMatrices
from SignalIntegrity.PySIException import PySIExceptionVirtualProbe
from SignalIntegrity.CallBacker import CallBacker

class VirtualProbeNumericParser(VirtualProbeParser,CallBacker):
    """performs numeric virtual probing from netlists"""
    def __init__(self, f=None, args=None, callback=None):
        """constructor

        frequencies may be provided at construction time (or not for symbolic solutions).

        @param f (optional) list of frequencies
        @param args (optional) string arguments for the circuit.
        @param callback (optional) function taking one argument as a callback

        Arguments are provided on a line as pairs of names and values separated by a space.

        The optional callback is used as described in the class CallBacker.

        """
        VirtualProbeParser.__init__(self, f, args)
        self.m_tm=None
        # pragma: silent exclude
        CallBacker.__init__(self,callback)
        # pragma: include
    def TransferMatrices(self):
        """calculates transfer matrices for virtual probing

        Virtual probing, insofar as this class is concerned means generating transfer matrices for
        processing waveforms with.

        @return instance of class TransferMatrices

        @remark
        TransferMatrices are used with a TransferMatricesProcessor to process waveforms for
        virtual probing.
        """
        self.SystemDescription()
        self.m_sd.CheckConnections()
        spc=self.m_spc
        result=[]
        for n in range(len(self.m_f)):
            for d in range(len(self.m_spc)):
                self.m_sd.AssignSParameters(spc[d][0],spc[d][1][n])
            tm=VirtualProbeNumeric(self.m_sd).TransferMatrix()
            result.append(tm)
            # pragma: silent exclude
            if self.HasACallBack():
                progress=self.m_f[n]/self.m_f[-1]*100.0
                if not self.CallBack(progress):
                    raise PySIExceptionVirtualProbe('calculation aborted')
            # pragma: include
        return TransferMatrices(self.m_f,result)