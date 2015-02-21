from SystemSParameters import SystemSParameters
from SystemDescriptionSymbolic import SystemDescriptionSymbolic
from Device import Device
from SignalIntegrity.Helpers import Matrix2LaTeX

class SystemSParametersSymbolic(SystemSParameters,SystemDescriptionSymbolic):
    def __init__(self,sd,equationEnvironment=False,small=False):
        SystemDescriptionSymbolic.__init__(self, sd, equationEnvironment, small)
    def LaTeXSi(self):
        W=self.WeightsMatrix()
        self.AddLine(self.BeginEq() + '\mathbf{Si} = \\left[ ' + self.Identity() + ' - ' +\
            Matrix2LaTeX(W,self.SmallMatrix()) + ' \\right]^{-1}' + self.EndEq())
        return self
    def LaTeXDirectSolution(self):
        self.LaTeXSi()
        BN=self.PortANames()
        AN=self.PortBNames()
        n=self.NodeVector()
        SCI=Device.SymbolicMatrix('Si',len(n))
        B=[[0]*len(BN) for p in range(len(BN))]
        for r in range(len(BN)):
            for c in range(len(BN)):
                B[r][c]=SCI[n.index(BN[r])][n.index(AN[c])]
        self.AddLine(self.BeginEq() + '\\mathbf{S} = ' + Matrix2LaTeX(B,self.SmallMatrix()) + self.EndEq())
        return self
    def LaTeXBlockSolutionBig(self):
        AN=self.PortBNames()
        BN=self.PortANames()
        XN=self.OtherNames(AN+BN)
        Wba=self.WeightsMatrix(BN,AN)
        Wbx=self.WeightsMatrix(BN,XN)
        Wxa=self.WeightsMatrix(XN,AN)
        Wxx=self.WeightsMatrix(XN,XN)
        if len(Wxx)==0:
            self.AddLine(self.BeginEq() + '\\mathbf{S} = ' + Matrix2LaTeX(Wba,self.SmallMatrix()) + self.EndEq())
        else:
            self.AddLine(self.BeginEq() + '\\mathbf{Wi} = ' + ' \\left[ ' + self.Identity() +\
                ' - ' + Matrix2LaTeX(Wxx,self.SmallMatrix()) +' \\right]^{-1} ' + self.EndEq())
            self.AddLine(self.BeginEq() + '\\mathbf{S} = ' + Matrix2LaTeX(Wba,self.SmallMatrix())+ ' + ' +\
                Matrix2LaTeX(Wbx,self.SmallMatrix()) + ' \\cdot \\mathbf{Wi} \\cdot' +\
                Matrix2LaTeX(Wxa,self.SmallMatrix()) + self.EndEq())
        return self
    def LaTeXBlockSolutionBiggest(self):
        AN=self.PortBNames()
        BN=self.PortANames()
        XN=self.OtherNames(AN+BN)
        Wba=self.WeightsMatrix(BN,AN)
        Wbx=self.WeightsMatrix(BN,XN)
        Wxa=self.WeightsMatrix(XN,AN)
        Wxx=self.WeightsMatrix(XN,XN)
        if len(Wxx)==0:
            self.AddLine(self.BeginEq() + '\\mathbf{S} = ' + Matrix2LaTeX(Wba,self.SmallMatrix()) + self.EndEq())
        else:
            if len(Wba) != 0:
                self.AddLine(self.BeginEq() + '\\mathbf{W_{ba}} = ' + Matrix2LaTeX(Wba,self.SmallMatrix()) + self.EndEq())
            if len(Wbx) != 0:
                self.AddLine(self.BeginEq() + '\\mathbf{W_{bx}} = ' + Matrix2LaTeX(Wbx,self.SmallMatrix()) + self.EndEq())
            if len(Wxa) != 0:
                self.AddLine(self.BeginEq() + '\\mathbf{W_{xa}} = ' + Matrix2LaTeX(Wxa,self.SmallMatrix()) + self.EndEq())
            if len(Wxx) != 0:
                self.AddLine(self.BeginEq() + '\\mathbf{W_{xx}} = ' + Matrix2LaTeX(Wxx,self.SmallMatrix()) + self.EndEq())
            self.AddLine(self.BeginEq() + '\\mathbf{S}=\\mathbf{W_{ba}}+\\mathbf{W_{bx}}\\cdot' +\
                '\\left[ ' + self.Identity() + ' -\\mathbf{W_{xx}}\\right]^{-1}\\cdot\\mathbf{W_{xa}}' + self.EndEq())
        return self
    def LaTeXBlockSolution(self):
        AN=self.PortBNames()
        BN=self.PortANames()
        XN=self.OtherNames(AN+BN)
        Wba=self.WeightsMatrix(BN,AN)
        Wbx=self.WeightsMatrix(BN,XN)
        Wxa=self.WeightsMatrix(XN,AN)
        Wxx=self.WeightsMatrix(XN,XN)
        #I=matrix(identity(len(Wxx)))
        if len(Wxx)==0:
            self.AddLine(self.BeginEq() + '\\mathbf{S} = ' + Matrix2LaTeX(Wba,self.SmallMatrix()) + self.EndEq())
        else:
            self.AddLine(self.BeginEq() + '\\mathbf{S} = ' + Matrix2LaTeX(Wba,self.SmallMatrix())+ ' + ' +\
                Matrix2LaTeX(Wbx,self.SmallMatrix()) + ' \\cdot \\left[ ' + self.Identity() +\
                ' - ' + Matrix2LaTeX(Wxx,self.SmallMatrix()) +' \\right]^{-1} \\cdot' +\
                Matrix2LaTeX(Wxa,self.SmallMatrix()) + self.EndEq())
        return self
    def LaTeXEquations(self):
        self.LaTeXSystemEquation()
        self.LaTeXDirectSolution()
        self.LaTeXBlockSolution()
        return self