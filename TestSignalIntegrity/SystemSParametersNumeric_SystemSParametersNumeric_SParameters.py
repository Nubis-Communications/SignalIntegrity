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
            SCI=((matrix(identity(len(n)))-\
                matrix(self.WeightsMatrix())).getI()).tolist()
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
...
        I=matrix(identity(len(Wxx)))
        result = matrix(Wba)+matrix(Wbx)*(I-matrix(Wxx)).getI()*matrix(Wxa)
        return result.tolist()