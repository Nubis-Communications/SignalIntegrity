class Simulator(SystemSParameters,object):
...
    def SourceVector(self):
        sv=[]
        for d in self:
            if d.Type == 'current source' or d.Type == 'voltage source':
                sv.append(d.Name)
        return sv
    def SourceToStimsPrimeMatrix(self,symbolic=False,Z0=50.):
        sv=self.SourceVector()
        sp=self.StimsPrime()
        Z0='Z0' if symbolic else Z0
        nZ0='-Z0' if symbolic else -Z0
        sm = [[0]*len(sv) for r in range(len(sp))]
        for s in sv:
            d=self[self.IndexOfDevice(s)]
            if d.Type == 'current source':
                if len(d) == 1:
                    sm[sp.index(d[0].M)][sv.index(s)] = Z0
                elif len(d) == 2:
                    sm[sp.index(d[0].M)][sv.index(s)] = nZ0
                    sm[sp.index(d[1].M)][sv.index(s)] = Z0
            elif d.Type == 'voltage source':
                if len(d) == 1:
                    sm[sp.index(d[0].M)][sv.index(s)] = 1.
                elif len(d) == 2:
                    sm[sp.index(d[0].M)][sv.index(s)] = -1./2.
                    sm[sp.index(d[1].M)][sv.index(s)] = 1./2.
        return sm
    def StimsPrime(self):
        sv=self.StimulusVector()
        sp=[]
        for s in range(len(sv)):
            sn='m'+str(s+1)
            if sn in sv: sp.append(sn)
            else: return sp
        return sp
    def SIPrime(self,symbolic=False,Left=None,Right=None):
        from numpy.linalg.linalg import LinAlgError
        n=self.NodeVector()
        m=self.StimulusVector()
        mprime=self.StimsPrime()
        if symbolic: SI=Device.SymbolicMatrix('Si',len(n))
        else:
            PR=array(self.PermutationMatrix([m.index('m'+str(c+1))
                        for c in range(len(mprime))], len(n))).transpose()
            if Right is None: Right = PR
            else: Right = array(PR).dot(array(Right))
            SI=self.Dagger(
                array(identity(len(n)))-array(self.WeightsMatrix()),
                Left=Left,Right=Right).tolist()
              SiPrime2=(SI*PR).tolist()
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
            result[r][n.index(dp.A)]=1; result[r][n.index(dp.B)]=1
        return result
...
