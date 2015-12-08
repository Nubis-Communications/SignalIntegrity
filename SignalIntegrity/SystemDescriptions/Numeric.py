from SignalIntegrity.Devices import TeeThreePortSafe

class Numeric(object):
    def InstallSafeTees(self,Z=0.00001):
        for d in range(len(self)):
            if '#' in self[d].Name:
                self[d].SParameters = TeeThreePortSafe(0.000000001)
