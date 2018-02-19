"""
 Virtual Probe Base Class for Housekeeping Functions
"""
# Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
# Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
# All Rights Reserved.
# 
# Explicit license in accompanying README.txt file.  If you don't have that file
# or do not agree to the terms in that file, then you are not licensed to use
# this material whatsoever.

from SignalIntegrity.SystemDescriptions.Simulator import Simulator
from SignalIntegrity.PySIException import PySIExceptionSimulator
from SignalIntegrity.PySIException import PySIExceptionVirtualProbe

class VirtualProbe(Simulator,object):
    """Base class for virtual probing"""
    def __init__(self,sd):
        Simulator.__init__(self,sd)
        self.m_ml = sd.m_ml if hasattr(sd, 'm_ml') else None
        self.m_D = sd.m_D if hasattr(sd, 'm_D') else None
    def Check(self):
        if self.m_ml is None:
            raise PySIExceptionVirtualProbe('no measures')
        try:
            Simulator.Check(self)
        except PySIExceptionSimulator as e:
            raise PySIExceptionVirtualProbe(e.message)
    @property
    def pMeasurementList(self):
        """property containing the list of measurements
        @return list of measurement (input waveforms)
        """
        return self.m_ml
    @pMeasurementList.setter
    def pMeasurementList(self,ml=None):
        if not ml is None: self.m_ml = ml
        return self
    @property
    def pStimDef(self):
        return self.m_D
    @pStimDef.setter
    def pStimDef(self,D=None):
        """property containing the stimdef
        @param D (optional) list of list matrix defining a stimdef
        @return self
        Sets a stimdef to the matrix provided.
        """
        if not D is None: self.m_D = D
        return self
