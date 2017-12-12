class CalibrationConstants(object):
...
    def ReadFromFile(self,filename):
        with open(filename) as f:
            lines=f.readlines()
        actualLines=[]
        for line in lines:
            if line.strip()[0]!='%':
                actualLines.append(line.strip())
        self.openC0=float(actualLines[0])*1e-15             # % C0 (fF) - OPEN
        self.openC1=float(actualLines[1])*1e-27             # % C1 (1e-27 F/Hz) - OPEN
        self.openC2=float(actualLines[2])*1e-36             # % C2 (1e-36 F/Hz^2) - OPEN
        self.openC3=float(actualLines[3])*1e-45             # % C3 (1e-45 F/Hz^3) - OPEN
        self.openOffsetDelay=float(actualLines[4])*1e-12    # % offset delay (pS) - OPEN
        self.openOffsetZ0=float(actualLines[5])             # % real(Zo) of offset length - OPEN
        self.openOffsetLoss=float(actualLines[6])*1e9       # % offset loss (GOhm/s) - OPEN
        self.shortL0=float(actualLines[7])*1e-12            # % L0 (pH) - SHORT
        self.shortL1=float(actualLines[8])*1e-24            # % L1 (1e-24 H/Hz) - SHORT
        self.shortL2=float(actualLines[9])*1e-33            # % L2 (1e-33 H/Hz^2) - SHORT
        self.shortL3=float(actualLines[10])*1e-42           # % L3 (1e-42 H/Hz^3) - SHORT
        self.shortOffsetDelay=float(actualLines[11])*1e-12  # % offset delay (pS) - SHORT
        self.shortOffsetZ0=float(actualLines[12])           # % real(Zo) of offset length - SHORT
        self.shortOffsetLoss=float(actualLines[13])*1e9     # % offset loss (GOhm/s) - SHORT
        self.loadZ=float(actualLines[14])                   # % load resistance (Ohm) - LOAD
        self.loadOffsetDelay=float(actualLines[15])*1e-12   # % offset delay (pS) - LOAD
        self.loadOffsetZ0=float(actualLines[16])            # % real(Zo) of offset length - LOAD
        self.loadOffsetLoss=float(actualLines[17])*1e9      # % offset loss (GOhm/s) - LOAD
        self.thruOffsetDelay=float(actualLines[18])*1e-12   # % offset delay (pS) - THRU
        self.thruOffsetZ0=float(actualLines[19])            # % real(Zo) of offset length - THRU
        self.thruOffsetLoss=float(actualLines[20])*1e9      # % offset loss (GOhm/s) - THRU
        return self
...
