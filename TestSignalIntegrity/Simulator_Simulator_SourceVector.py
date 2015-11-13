class Simulator(SystemSParameters,object):
...
    def SourceVector(self):
        sv=[]
        for d in self:
            if d.pType == 'current source' or d.pType == 'voltage source':
                sv.append(d.pName)
        return sv
    def SourceToStimsPrimeMatrix(self,symbolic=False):
        sv=self.SourceVector()
        sp=self.StimsPrime()
        Z0='Z0' if symbolic else 50.
        sm = [[0]*len(sv) for r in range(len(sp))]
        for s in sv:
            d=self[self.IndexOfDevice(s)]
            if d.pType == 'current source':
                if len(d) == 1:
                    sm[sp.index(d[0].pM)][sv.index(s)] = Z0
                elif len(d) == 2:
                    sm[sp.index(d[0].pM)][sv.index(s)] = Z0
                    sm[sp.index(d[1].pM)][sv.index(s)] = Z0
            elif d.pType == 'voltage source':
                if len(d) == 1:
                    sm[sp.index(d[0].pM)][sv.index(s)] = 1.
                elif len(d) == 2:
                    sm[sp.index(d[0].pM)][sv.index(s)] = -1./2.
                    sm[sp.index(d[1].pM)][sv.index(s)] = 1./2.
        return sm
    def StimsPrime(self):
        sv=self.StimulusVector()
        sp=[]
        for s in range(len(sv)):
            sn='m'+str(s+1)
            if sn in sv: sp.append(sn)
            else: return sp
    def SIPrime(self,symbolic=False):
        from numpy.linalg.linalg import LinAlgError
        n=self.NodeVector()
        m=self.StimulusVector()
        mprime=self.StimsPrime()
        if symbolic: SI=Device.SymbolicMatrix('Si',len(n))
        else:
            try:
                SI=(matrix(identity(len(n)))-matrix(self.WeightsMatrix())).getI().tolist()
            except LinAlgError:
                raise PySIExceptionSimulator('numerical error - cannot invert matrix')
        SiPrime=[[0]*len(mprime) for r in range(len(n))]
        for c in range(len(mprime)):
            for r in range(len(n)):
                SiPrime[r][c]=SI[r][m.index('m'+str(c+1))]
        return SiPrime
    def VoltageExtractionMatrix(self,nl):
        n=self.NodeVector()
        result=[[0]*len(n) for r in range(len(nl))]
        for r in range(len(nl)):
            dp=self[self.DeviceNames().index(nl[r][0])][nl[r][1]-1]
            result[r][n.index(dp.pA)]=1
            result[r][n.index(dp.pB)]=1
        return result