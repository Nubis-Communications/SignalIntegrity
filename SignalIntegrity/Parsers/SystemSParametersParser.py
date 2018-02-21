"""
 s-parameters of netlists
"""
# Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
# Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
# All Rights Reserved.
#
# Explicit license in accompanying README.txt file.  If you don't have that file
# or do not agree to the terms in that file, then you are not licensed to use
# this material whatsoever.

from SignalIntegrity.SystemDescriptions import SystemSParametersNumeric
from SignalIntegrity.Parsers.SystemDescriptionParser import SystemDescriptionParser
from SignalIntegrity.SParameters import SParameters
from SignalIntegrity.PySIException import PySIExceptionSParameters
from SignalIntegrity.CallBacker import CallBacker
from copy_reg import constructor

class SystemSParametersNumericParser(SystemDescriptionParser,CallBacker):
    """generates system s-parameters from a netlist"""
    def __init__(self,f=None,args=None,callback=None):
        """constructor

        frequencies may be provided at construction time (or not for symbolic solutions).

        @param f (optional) list of frequencies
        @param args (optional) string arguments for the circuit.
        @param callback (optional) function taking one argument as a callback

        Arguments are provided on a line as pairs of names and values separated by a space.

        The optional callback is used as described in the class CallBacker.

        """
        SystemDescriptionParser.__init__(self,f,args)
        # pragma: silent exclude
        CallBacker.__init__(self,callback)
        # pragma: include
    def SParameters(self,solvetype='block'):
        """compute the s-parameters of the netlist.
        @param solvetype (optional) string how to solve it. (defaults to 'block').
        @return instance of class SParameters as the solution of the network.
        valid solvetype strings are:
        - 'block' - use the block matrix solution method.
        - 'direct' - use the direct method.
        'block' is faster and preferred, but direct is provided as an alternative and
        for testing. (Previously, instances were found where the block method failed,
        but the direct method did not - but this possibility is thought to be impossible
        now.
        """
        self.SystemDescription()
        self.m_sd.CheckConnections()
        spc=self.m_spc
        result = []
        for n in range(len(self.m_f)):
            for d in range(len(spc)):
                self.m_sd.AssignSParameters(spc[d][0],spc[d][1][n])
            result.append(SystemSParametersNumeric(self.m_sd).SParameters(
                solvetype=solvetype))
            # pragma: silent exclude
            if self.HasACallBack():
                progress=self.m_f[n]/self.m_f[-1]*100.0
                if not self.CallBack(progress):
                    raise PySIExceptionSParameters('calculation aborted')
            # pragma: include
        sf = SParameters(self.m_f, result)
        return sf