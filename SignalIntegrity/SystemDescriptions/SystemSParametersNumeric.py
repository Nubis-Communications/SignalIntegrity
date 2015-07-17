from numpy import matrix
from numpy import identity

from SignalIntegrity.Helpers.AllZeroMatrix import *
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
        Wxx=self.WeightsMatrix(XN,XN)
        if len(Wxx)==0:
            return matrix(Wba).tolist()
        Wbx=self.WeightsMatrix(BN,XN)
        Wxa=self.WeightsMatrix(XN,AN)
        if AllZeroMatrix(Wbx) or AllZeroMatrix(Wxa):
            return matrix(Wba).tolist()

        XNnzcWbx=[XN[nzcWbx] for nzcWbx in NonZeroColumns(Wbx)]
        XNzcWbx=[XN[zcWbx] for zcWbx in ZeroColumns(Wbx)]
        XNnzrWxa=[XN[nzrWxa] for nzrWxa in NonZeroRows(Wxa)]
        XNzrWxa=[XN[zrWxa] for zrWxa in ZeroRows(Wxa)]

        Wxx11=self.WeightsMatrix(XNnzrWxa,XNnzcWbx)
        Wxx12=self.WeightsMatrix(XNnzrWxa,XNzcWbx)
        Wxx21=self.WeightsMatrix(XNzrWxa,XNnzcWbx)
        Wxx22=self.WeightsMatrix(XNzrWxa,XNzcWbx)
        Wbx1=self.WeightsMatrix(BN,XNnzcWbx)
        Wbx2=self.WeightsMatrix(BN,XNzcWbx)
        Wxa1=self.WeightsMatrix(XNnzrWxa,AN)
        Wxa2=self.WeightsMatrix(XNzrWxa,AN)

        I11 = [[1 if roele == coele else 0 for coele in XNnzcWbx] for roele in XNnzrWxa]
        I12 = [[1 if roele == coele else 0 for coele in XNzcWbx] for roele in XNnzrWxa]
        I21 = [[1 if roele == coele else 0 for coele in XNnzcWbx] for roele in XNzrWxa]
        I22 = [[1 if roele == coele else 0 for coele in XNzcWbx] for roele in XNzrWxa]

        if XNzcWbx != []:
            if AllZeroMatrix((matrix(I12)-matrix(Wxx12)).tolist()):
                result=matrix(Wba)+matrix(Wbx1)*(I11-matrix(Wxx11)).getI()*matrix(Wxa1)
                return result.tolist()

        if XNzrWxa != []:
            if AllZeroMatrix((matrix(I21)-matrix(Wxx21)).tolist()):
                I = matrix(identity(len(Wxx11)))
                result=matrix(Wba)+matrix(Wbx1)*(I11-matrix(Wxx11)).getI()*matrix(Wxa1)
                return result.tolist()

        I=matrix(identity(len(Wxx)))
        result = matrix(Wba)+matrix(Wbx)*(I-matrix(Wxx)).getI()*matrix(Wxa)
        return result.tolist()