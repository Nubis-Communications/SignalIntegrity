from SignalIntegrity.Helpers.AllZeroMatrix import AllZeroMatrix
from SystemSParameters import SystemSParameters
from SystemDescriptionSymbolic import SystemDescriptionSymbolic
from Device import Device
from SignalIntegrity.Helpers.AllZeroMatrix import *

class SystemSParametersSymbolic(SystemSParameters,SystemDescriptionSymbolic):
    def __init__(self,sd,**args):
        SystemDescriptionSymbolic.__init__(self,sd,**args)
    def _LaTeXSi(self):
        sW=self._LaTeXMatrix(self.WeightsMatrix())
        self._AddEq('\mathbf{Si} = \\left[ '+self._Identity()+\
            ' - '+sW+' \\right]^{-1}')
        return self
    def LaTeXSolution(self,**args):
        type = args['type'] if 'type' in args else 'block'
        size = args['size'] if 'size' in args else 'normal'
        AN=self.PortBNames()
        BN=self.PortANames()
        if type=='direct':
            self._LaTeXSi()
            BN=self.PortANames()
            AN=self.PortBNames()
            n=self.NodeVector()
            SCI=Device.SymbolicMatrix('Si',len(n))
            B=[[0]*len(BN) for p in range(len(BN))]
            for r in range(len(BN)):
                for c in range(len(BN)):
                    B[r][c]=SCI[n.index(BN[r])][n.index(AN[c])]
            self._AddEq('\\mathbf{S} = '+self._LaTeXMatrix(B))
            return self
        XN=self.OtherNames(AN+BN)
        Wba=self.WeightsMatrix(BN,AN)
        sWba=self._LaTeXMatrix(Wba)
        Wxx=self.WeightsMatrix(XN,XN)
        if len(Wxx)==0:
            self._AddEq('\\mathbf{S} = '+sWba)
            return self
        Wbx=self.WeightsMatrix(BN,XN)
        Wxa=self.WeightsMatrix(XN,AN)
        if AllZeroMatrix(Wbx) or AllZeroMatrix(Wxa):
            self._AddEq('\\mathbf{S} = '+sWba)
            return self
        I=self._Identity()

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
        I11=[[1 if roele == coele else 0 for coele in XNnzcWbx] for roele in XNnzrWxa]
        I12=[[1 if roele == coele else 0 for coele in XNzcWbx] for roele in XNnzrWxa]
        I21=[[1 if roele == coele else 0 for coele in XNnzcWbx] for roele in XNzrWxa]
        I22=[[1 if roele == coele else 0 for coele in XNzcWbx] for roele in XNzrWxa]
        if XNzcWbx != []:
            if AllZeroMatrix(I12) and AllZeroMatrix(Wxx12):
                Wbx=Wbx1
                Wxa=Wxa1
                I=self._LaTeXMatrix(I11)
                Wxx=Wxx11
        if XNzrWxa != []:
            if AllZeroMatrix(I21) and AllZeroMatrix(Wxx21):
                Wbx=Wbx1
                Wxa=Wxa1
                I=self._LaTeXMatrix(I11)
                Wxx=Wxx11

        sWbx=self._LaTeXMatrix(Wbx)
        sWxa=self._LaTeXMatrix(Wxa)
        sWxx=self._LaTeXMatrix(Wxx)
        if size=='biggest':
            if len(Wba) != 0:
                self._AddEq('\\mathbf{W_{ba}} = '+sWba)
            if len(Wbx) != 0:
                self._AddEq('\\mathbf{W_{bx}} = '+sWbx)
            if len(Wxa) != 0:
                self._AddEq('\\mathbf{W_{xa}} = '+sWxa)
            if len(Wxx) != 0:
                self._AddEq('\\mathbf{W_{xx}} = '+sWxx)
            self._AddEq('\\mathbf{S}=\\mathbf{W_{ba}}+\\mathbf{W_{bx}}\\cdot'+\
                '\\left[ '+I+\
                ' -\\mathbf{W_{xx}}\\right]^{-1}\\cdot\\mathbf{W_{xa}}')
        elif size=='big':
            self._AddEq('\\mathbf{Wi} = '+' \\left[ '+I+\
                ' - '+sWxx+' \\right]^{-1} ')
            self._AddEq('\\mathbf{S} = '+sWba+' + '+sWbx+\
                ' \\cdot \\mathbf{Wi} \\cdot' +sWxa)
        else:
            self._AddEq('\\mathbf{S} = '+sWba+' + '+sWbx+' \\cdot \\left[ '+\
            I+' - '+sWxx+' \\right]^{-1} \\cdot'+sWxa)
        return self