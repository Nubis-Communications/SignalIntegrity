class CalibrationConstants(object):
    def __init__(self):
        self.openC0=0.              # % C0 (fF) - OPEN
        self.openC1=0.              # % C1 (1e-27 F/Hz) - OPEN
        self.openC2=0.              # % C2 (1e-36 F/Hz^2) - OPEN
        self.openC3=0.              # % C3 (1e-45 F/Hz^3) - OPEN
        self.openOffsetDelay=0.     # % offset delay (pS) - OPEN
        self.openOffsetZ0=50.       # % real(Zo) of offset length - OPEN
        self.openOffsetLoss=0.      # % offset loss (Gohm/s) - OPEN
        self.shortL0=0.             # % L0 (pH) - SHORT
        self.shortL1=0.             # % L1 (1e-24 H/Hz) - SHORT
        self.shortL2=0.             # % L2 (1e-33 H/Hz^2) - SHORT
        self.shortL3=0.             # % L3 (1e-42 H/Hz^3) - SHORT
        self.shortOffsetDelay=0.    # % offset delay (pS) - SHORT
        self.shortOffsetZ0=50.      # % real(Zo) of offset length - SHORT
        self.shortOffsetLoss=0.     # % offset loss (Gohm/s) - SHORT
        self.loadZ=50.              # % load resistance (ohm) - LOAD
        self.loadOffsetDelay=0.     # % offset delay (pS) - LOAD
        self.loadOffsetZ0=50.       # % real(Zo) of offset length - LOAD
        self.loadOffsetLoss=0.      # % offset loss (Gohm/s) - LOAD
        self.thruOffsetDelay=0.     # % offset delay (pS) - THRU
        self.thruOffsetZ0=50.       # % real(Zo) of offset length - THRU
        self.thruOffsetLoss=0.      # % offset loss (Gohm/s) - THRU
        self.f0=1e9
...
