from numpy import matrix
from numpy import identity

from SignalIntegrity.Helpers.AllZeroMatrix import AllZeroMatrix
from SignalIntegrity.SystemDescriptions import SystemSParameters
from Numeric import Numeric

class SystemSParametersNumeric(SystemSParameters,Numeric):
    def __init__(self,sd):
        SystemSParameters.__init__(self,sd)
    def SParameters(self,**args):
        type = args['type'] if 'type' in args else 'block'
        AN=self.PortBNames()
        BN=self.PortANames()
        if type == 'direct':
            n=self.NodeVector()
            SCI=((matrix(identity(len(n)))-\
                matrix(self.WeightsMatrix())).getI()).tolist()
            B=[[0]*len(BN) for p in range(len(BN))]
            for r in range(len(BN)):
                for c in range(len(BN)):
                    B[r][c]=SCI[n.index(BN[r])][n.index(AN[c])]
            return B
        # else type assumed to be 'block'
        XN=self.OtherNames(AN+BN)
        Wba=self.WeightsMatrix(BN,AN)
        Wbx=self.WeightsMatrix(BN,XN)
        Wxa=self.WeightsMatrix(XN,AN)
        Wxx=self.WeightsMatrix(XN,XN)
        I=matrix(identity(len(Wxx)))
        if len(Wxx)==0:
            result = matrix(Wba)
        else:
            if AllZeroMatrix(Wbx) or AllZeroMatrix(Wxa):
                result = matrix(Wba)
            else:
                result = matrix(Wba)+matrix(Wbx)*(I-matrix(Wxx)).getI()*matrix(Wxa)
        return result.tolist()