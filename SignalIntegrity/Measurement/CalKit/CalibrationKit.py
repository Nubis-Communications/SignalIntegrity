'''
 Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
 Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
 All Rights Reserved.

 Explicit license in accompanying README.txt file.  If you don't have that file
 or do not agree to the terms in that file, then you are not licensed to use
 this material whatsoever.
'''
from SignalIntegrity.Measurement.CalKit.Standards.ShortStandard import ShortStandard
from SignalIntegrity.Measurement.CalKit.Standards.OpenStandard import OpenStandard
from SignalIntegrity.Measurement.CalKit.Standards.LoadStandard import LoadStandard
from SignalIntegrity.Measurement.CalKit.Standards.ThruStandard import ThruStandard
from SignalIntegrity.SParameters.SParameterFile import SParameterFile

# Calibration Kit File Format
#
# % DESCRIPTION [Enter manufacturer and model number of calkit]
# % 
# % C0 (fF) - OPEN
# % C1 (1e-27 F/Hz) - OPEN
# % C2 (1e-36 F/Hz^2) - OPEN
# % C3 (1e-45 F/Hz^3) - OPEN
# % offset delay (pS) - OPEN
# % real(Zo) of offset length - OPEN
# % offset loss (GOhm/s) - OPEN
# % L0 (pH) - SHORT
# % L1 (1e-24 H/Hz) - SHORT
# % L2 (1e-33 H/Hz^2) - SHORT
# % L3 (1e-42 H/Hz^3) - SHORT
# % offset delay (pS) - SHORT
# % real(Zo) of offset length - SHORT
# % offset loss (GOhm/s) - SHORT
# % load resistance (Ohm) - LOAD
# % offset delay (pS) - LOAD
# % real(Zo) of offset length - LOAD
# % offset loss (GOhm/s) - LOAD
# % offset delay (pS) - THRU
# % real(Zo) of offset length - THRU
# % offset loss (GOhm/s) - THRU
# 63.170000 
# -1178.000000
# 109.600000
# -2.146000
# 14.490000
# 50.000000
# 1.300000
# 0.000000
# 0.000000
# 0.000000
# 0.000000
# 16.684000
# 50.000000
# 1.300000
# 50.000000
# 0.000000
# 50.000000
# 1.300000
# 57.960000
# 50.000000
# 0.000000
class CalibrationConstants(object):
    def __init__(self):
        self.openC0=0.              # % C0 (fF) - OPEN
        self.openC1=0.              # % C1 (1e-27 F/Hz) - OPEN
        self.openC2=0.              # % C2 (1e-36 F/Hz^2) - OPEN
        self.openC3=0.              # % C3 (1e-45 F/Hz^3) - OPEN
        self.openOffsetDelay=0.     # % offset delay (pS) - OPEN
        self.openOffsetZ0=50.       # % real(Zo) of offset length - OPEN
        self.openOffsetLoss=0.      # % offset loss (GOhm/s) - OPEN
        self.shortLO=0.             # % L0 (pH) - SHORT
        self.shortL1=0.             # % L1 (1e-24 H/Hz) - SHORT
        self.shortL2=0.             # % L2 (1e-33 H/Hz^2) - SHORT
        self.shortL3=0.             # % L3 (1e-42 H/Hz^3) - SHORT
        self.shortOffsetDelay=0.    # % offset delay (pS) - SHORT
        self.shortOffsetZ0=50.      # % real(Zo) of offset length - SHORT
        self.shortOffsetLoss=0.     # % offset loss (GOhm/s) - SHORT
        self.loadZ=50.              # % load resistance (Ohm) - LOAD
        self.loadOffsetDelay=0.     # % offset delay (pS) - LOAD
        self.loadOffsetZ0=50.       # % real(Zo) of offset length - LOAD
        self.loadOffsetLoss=0.      # % offset loss (GOhm/s) - LOAD
        self.thruOffsetDelay=0.     # % offset delay (pS) - THRU
        self.thruOffsetZ0=50.       # % real(Zo) of offset length - THRU
        self.thruOffsetLoss=0.      # % offset loss (GOhm/s) - THRU

    def ReadFromFile(self,filename):
        with open(filename) as f:
            lines=f.readlines()
        actualLines=[]
        for line in lines:
            if line.strip()[0]!='%':
                actualLines.append(line)
        self.openC0=float(actualLines[0]*1e-15)             # % C0 (fF) - OPEN
        self.openC1=float(actualLines[1]*1e-27)             # % C1 (1e-27 F/Hz) - OPEN
        self.openC2=float(actualLines[2]*1e-36)             # % C2 (1e-36 F/Hz^2) - OPEN
        self.openC3=float(actualLines[3]*1e-45)             # % C3 (1e-45 F/Hz^3) - OPEN
        self.openOffsetDelay=float(actualLines[4]*1e-12)    # % offset delay (pS) - OPEN
        self.openOffsetZ0=float(actualLines[5])             # % real(Zo) of offset length - OPEN
        self.openOffsetLoss=float(actualLines[6]*1e9)       # % offset loss (GOhm/s) - OPEN
        self.shortLO=float(actualLines[7]*1e-12)            # % L0 (pH) - SHORT
        self.shortL1=float(actualLines[8]*1e-24)            # % L1 (1e-24 H/Hz) - SHORT
        self.shortL2=float(actualLines[9]*1e-33)            # % L2 (1e-33 H/Hz^2) - SHORT
        self.shortL3=float(actualLines[10]*1e-42)           # % L3 (1e-42 H/Hz^3) - SHORT
        self.shortOffsetDelay=float(actualLines[11]*1e-12)  # % offset delay (pS) - SHORT
        self.shortOffsetZ0=float(actualLines[12])           # % real(Zo) of offset length - SHORT
        self.shortOffsetLoss=float(actualLines[13]*1e9)      # % offset loss (GOhm/s) - SHORT
        self.loadZ=float(actualLines[14])                   # % load resistance (Ohm) - LOAD
        self.loadOffsetDelay=float(actualLines[15]*1e-12)   # % offset delay (pS) - LOAD
        self.loadOffsetZ0=float(actualLines[16])            # % real(Zo) of offset length - LOAD
        self.loadOffsetLoss=float(actualLines[17]*1e9)      # % offset loss (GOhm/s) - LOAD
        self.thruOffsetDelay=float(actualLines[18]*1e-12)   # % offset delay (pS) - THRU
        self.thruOffsetZ0=float(actualLines[19])            # % real(Zo) of offset length - THRU
        self.thruOffsetLoss=float(actualLines[20]*1e9)      # % offset loss (GOhm/s) - THRU
        return self
    def WriteToFile(self,filename,calkitname=None):
        line=[]
        if not calkitname is None:
            line.append('% DESCRIPTION: '+calkitname+'\n')
        else:
            line.append('% DESCRIPTION [Enter manufacturer and model number of calkit]\n')
        line.append('%\n')
        line.append('% C0 (fF) - OPEN\n')
        line.append('% C1 (1e-27 F/Hz) - OPEN\n')
        line.append('% C2 (1e-36 F/Hz^2) - OPEN\n')
        line.append('% C3 (1e-45 F/Hz^3) - OPEN\n')
        line.append('% offset delay (pS) - OPEN\n')
        line.append('% real(Zo) of offset length - OPEN\n')
        line.append('% offset loss (GOhm/s) - OPEN\n')
        line.append('% L0 (pH) - SHORT\n')
        line.append('% L1 (1e-24 H/Hz) - SHORT\n')
        line.append('% L2 (1e-33 H/Hz^2) - SHORT\n')
        line.append('% L3 (1e-42 H/Hz^3) - SHORT\n')
        line.append('% offset delay (pS) - SHORT\n')
        line.append('% real(Zo) of offset length - SHORT\n')
        line.append('% offset loss (GOhm/s) - SHORT\n')
        line.append('% load resistance (Ohm) - LOAD\n')
        line.append('% offset delay (pS) - LOAD\n')
        line.append('% real(Zo) of offset length - LOAD\n')
        line.append('% offset loss (GOhm/s) - LOAD\n')
        line.append('% offset delay (pS) - THRU\n')
        line.append('% real(Zo) of offset length - THRU\n')
        line.append('% offset loss (GOhm/s) - THRU\n')
        line.append(str(self.openC0/1e-15)+'\n')            # % C0 (fF) - OPEN
        line.append(str(self.openC1/1e-27)+'\n')            # % C1 (1e-27 F/Hz) - OPEN
        line.append(str(self.openC2/1e-36)+'\n')            # % C2 (1e-36 F/Hz^2) - OPEN
        line.append(str(self.openC3/1e-45)+'\n')            # % C3 (1e-45 F/Hz^3) - OPEN
        line.append(str(self.openOffsetDelay/1e-12)+'\n')   # % offset delay (pS) - OPEN
        line.append(str(self.openOffsetZ0)+'\n')            # % real(Zo) of offset length - OPEN
        line.append(str(self.openOffsetLoss/1e9)+'\n')      # % offset loss (GOhm/s) - OPEN
        line.append(str(self.shortLO/1e-12)+'\n')           # % L0 (pH) - SHORT
        line.append(str(self.shortL1/1e-24)+'\n')           # % L1 (1e-24 H/Hz) - SHORT
        line.append(str(self.shortL2/1e-33)+'\n')           # % L2 (1e-33 H/Hz^2) - SHORT
        line.append(str(self.shortL3/1e-42)+'\n')           # % L3 (1e-42 H/Hz^3) - SHORT
        line.append(str(self.shortOffsetDelay/1e-12)+'\n')  # % offset delay (pS) - SHORT
        line.append(str(self.shortOffsetZ0)+'\n')           # % real(Zo) of offset length - SHORT
        line.append(str(self.shortOffsetLoss/1e9)+'\n')      # % offset loss (GOhm/s) - SHORT
        line.append(str(self.loadZ)+'\n')                   # % load resistance (Ohm) - LOAD
        line.append(str(self.loadOffsetDelay/1e-12)+'\n')   # % offset delay (pS) - LOAD
        line.append(str(self.loadOffsetZ0)+'\n')            # % real(Zo) of offset length - LOAD
        line.append(str(self.loadOffsetLoss/1e9)+'\n')      # % offset loss (GOhm/s) - LOAD
        line.append(str(self.thruOffsetDelay/1e-12)+'\n')   # % offset delay (pS) - THRU
        line.append(str(self.thruOffsetZ0)+'\n')            # % real(Zo) of offset length - THRU
        line.append(str(self.thruOffsetLoss/1e9)+'\n')      # % offset loss (GOhm/s) - THRU
        return self

class CalibrationKit(object):
    def __init__(self,f):
        self.m_f=f
    def ReadFromFile(self,filename):
        c=CalibrationConstants().ReadFromFile(filename)
        self.openStandard=OpenStandard(
            self.m_f,c.openOffsetDelay,c.openOffsetZ0,c.openOffsetLoss,
            self.openC0,self.openC1,self.openC2,self.openC3)
        self.shortStandard=ShortStandard(
            self.m_f,c.shortOffsetDelay,c.shortOffsetZ0,c.shortOffsetLoss,
            self.shortL0,c.shortL1,c.shortL2,c.shortL3)
        self.loadStandard=LoadStandard(
            self.m_f,c.loadOffsetDelay,c.loadOffsetZ0,c.loadOffsetLoss,c.loadZ)
        self.thruStandard=ThruStandard(
            self.m_f,c.thruOffsetDelay,c.thruOffsetZ0,c.thruOffsetLoss)
        return self
    def WriteToFile(self,filenamePrefix):
        self.shortStandard.WriteToFile(filenamePrefix+'Short')
        self.openStandard.WriteToFile(filenamePrefix+'Open')
        self.loadStandard.WriteToFile(filenamePrefix+'Load')
        self.thruStandard.WriteToFile(filenamePrefix+'Thru')
        return self
    def ReadStandardsFromSParameterFiles(self,filenamePrefix):
        self.shortStandard=SParameterFile(filenamePrefix+'Short.s1p')
        self.openStandard=SParameterFile(filenamePrefix+'Open.s1p')
        self.loadStandard=SParameterFile(filenamePrefix+'Load.s1p')
        self.thruStandard=SParameterFile(filenamePrefix+'Thru.s1p')
