class CalibrationConstants(object):
...
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
        line.append(str(self.shortL0/1e-12)+'\n')           # % L0 (pH) - SHORT
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
        with open(filename,'w') as f:
            f.writelines(line)
        return self

