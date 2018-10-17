class SystemSParametersNumeric(SystemSParameters,Numeric):
    def __init__(self,sd=None):
        SystemSParameters.__init__(self,sd)
    def SParameters(self,**args):
        from numpy.linalg.linalg import LinAlgError
        solvetype = args['solvetype'] if 'solvetype' in args else 'block'
        AN=self.PortBNames()
        BN=self.PortANames()
        if solvetype == 'direct':
            n=self.NodeVector()
            PL=self.PermutationMatrix([n.index(BN[r])
                for r in range(len(BN))], len(n))
            PR=matrix(self.PermutationMatrix([n.index(AN[r])
                for r in range(len(AN))], len(n))).transpose()
            SCI=self.Dagger(matrix(identity(len(n)))-matrix(self.WeightsMatrix()),
                Left=PL,Right=PR).tolist()
            B=[[0]*len(BN) for p in range(len(BN))]
            for r in range(len(BN)):
                for c in range(len(BN)):
                    B[r][c]=SCI[n.index(BN[r])][n.index(AN[c])]
            return B
        # else solvetype assumed to be 'block'
        XN=self.OtherNames(AN+BN)
        Wba=self.WeightsMatrix(BN,AN)
        Wxx=self.WeightsMatrix(XN,XN)
        if len(Wxx)==0:
            return matrix(Wba).tolist()
        Wbx=self.WeightsMatrix(BN,XN)
        Wxa=self.WeightsMatrix(XN,AN)
        if AllZeroMatrix(Wbx) or AllZeroMatrix(Wxa):
            return matrix(Wba).tolist()
        I=matrix(identity(len(Wxx)))
        # Wba+Wbx*[(I-Wxx)^-1]*Wxa
        result = matrix(Wba)+self.Dagger(I-matrix(Wxx),Left=Wbx,Right=Wxa,Mul=True)
        return result.tolist()