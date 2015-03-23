from SystemSParameters import SystemSParameters
from SystemDescriptionSymbolic import SystemDescriptionSymbolic
from Device import Device

class SystemSParametersSymbolic(SystemSParameters,SystemDescriptionSymbolic):
    def __init__(self,sd,**args):
        SystemDescriptionSymbolic.__init__(self,sd,**args)
    def _LaTeXSi(self):
        sW=self._LaTeXMatrix(self.WeightsMatrix())
        self._AddEq('\mathbf{Si} = \\left[ '+self.Identity()+\
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
        Wbx=self.WeightsMatrix(BN,XN)
        Wxa=self.WeightsMatrix(XN,AN)
        Wxx=self.WeightsMatrix(XN,XN)
        sWba=self._LaTeXMatrix(Wba)
        if len(Wxx)==0:
            self._AddEq('\\mathbf{S} = '+sWba)
            return self
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
                '\\left[ '+self.Identity()+\
                ' -\\mathbf{W_{xx}}\\right]^{-1}\\cdot\\mathbf{W_{xa}}')
        elif size=='big':
            self._AddEq('\\mathbf{Wi} = '+' \\left[ '+self.Identity()+\
                ' - '+sWxx+' \\right]^{-1} ')
            self._AddEq('\\mathbf{S} = '+sWba+' + '+sWbx+\
                ' \\cdot \\mathbf{Wi} \\cdot' +sWxa)
        else:
            self._AddEq('\\mathbf{S} = '+sWba+' + '+sWbx+' \\cdot \\left[ '+\
            self.Identity()+' - '+sWxx+' \\right]^{-1} \\cdot'+sWxa)
        return self