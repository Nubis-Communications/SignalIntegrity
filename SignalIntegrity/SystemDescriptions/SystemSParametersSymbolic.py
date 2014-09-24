from SystemSParameters import SystemSParameters
from Symbolic import Symbolic
from Device import Device
from SignalIntegrity.Helpers import Matrix2LaTeX

class SystemSParametersSymbolic(SystemSParameters,Symbolic):
    def __init__(self,sd,equationEnvironment=False,small=False):
        self.Data=sd
        Symbolic.__init__(self,equationEnvironment,small)
    def LaTeXSystemEquation(self):
        W=self.WeightsMatrix()
        n=self.SubscriptedVector(self.NodeVector())
        m=self.SubscriptedVector(self.StimulusVector())
        self.AddLine(self.BeginEq() + '\\left[ ' + self.Identity() + ' - ' +\
            Matrix2LaTeX(W,self.SmallMatrix()) + '\\right] \\cdot '+ Matrix2LaTeX(n,self.SmallMatrix()) +\
            ' = '+ Matrix2LaTeX(m,self.SmallMatrix()) + self.EndEq())
        return self
    def LaTeXSi1(self):
        W=self.WeightsMatrix()
        self.AddLine(self.BeginEq() + '\mathbf{Si} = \\left[ ' + self.Identity() + ' - ' +\
            Matrix2LaTeX(W,self.SmallMatrix()) + ' \\right]^{-1}' + self.EndEq())
        return self
    def LaTeXSi2(self):
        W=self.WeightsMatrix()
        Si=Device.SymbolicMatrix('Si',len(W))
        self.AddLine(self.BeginEq() + Matrix2LaTeX(Si,self.SmallMatrix()) + '= \\left[ ' + self.Identity() +\
            ' - ' + Matrix2LaTeX(W,self.SmallMatrix()) +'\\right]^{-1}' + self.EndEq())
        return self
    def LaTeXSolutionDirect(self):
        BN=self.PortANames()
        AN=self.PortBNames()
        n=self.NodeVector()
        SCI=Si=Device.SymbolicMatrix('Si',len(n))
        B=[[0]*len(BN) for p in range(len(BN))]
        for r in range(len(BN)):
            for c in range(len(BN)):
                B[r][c]=SCI[n.index(BN[r])][n.index(AN[c])]
        self.AddLine(self.BeginEq() + '\\mathbf{S} = ' + Matrix2LaTeX(B,self.SmallMatrix()) + self.EndEq())
        return self
    def LaTeXBigSolution(self):
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
            self.AddLine(self.BeginEq() + '\\mathbf{Si} = ' + ' \\left[ ' + self.Identity() +\
                ' - ' + Matrix2LaTeX(Wxx,self.SmallMatrix()) +' \\right]^{-1} ' + self.EndEq())
            self.AddLine(self.BeginEq() + '\\mathbf{S} = ' + Matrix2LaTeX(Wba,self.SmallMatrix())+ ' + ' +\
                Matrix2LaTeX(Wbx,self.SmallMatrix()) + ' \\cdot \\mathbf{Si} \\cdot' +\
                Matrix2LaTeX(Wxa,self.SmallMatrix()) + self.EndEq())
        return self
    def LaTeXSolution(self):
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
        self.LaTeXSi1()
        #self.LaTeXSi2()
        self.LaTeXSolutionDirect()
        self.LaTeXSolution()
        return self


