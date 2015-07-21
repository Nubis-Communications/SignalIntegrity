from VirtualProbe import VirtualProbe
from SystemSParametersSymbolic import SystemSParametersSymbolic
from SignalIntegrity.Helpers import Matrix2LaTeX
from SignalIntegrity.Helpers import MatrixMultiply

class VirtualProbeSymbolic(SystemSParametersSymbolic, VirtualProbe):
    def __init__(self,sd,**args):
        # self.Data=sd
        SystemSParametersSymbolic.__init__(self,sd,**args)
        VirtualProbe.__init__(self, sd)
    def LaTeXTransferMatrix(self):
        self._LaTeXSi()
        vemsi = MatrixMultiply(
            self.VoltageExtractionMatrix(self.pMeasurementList), self.SIPrime(True))
        oneElementVemsi = False
        if len(vemsi) == 1:
            if len(vemsi[0]) == 1: oneElementVemsi = True
        vemsi = Matrix2LaTeX(vemsi, self._SmallMatrix())
        veosi = MatrixMultiply(
            self.VoltageExtractionMatrix(self.pOutputList), self.SIPrime(True))
        oneElementVeosi = False
        if len(veosi) == 1:
            if len(veosi[0]) == 1: oneElementVeosi = True
        veosi = Matrix2LaTeX(veosi, self._SmallMatrix())
        if self.pStimDef is None:
            if oneElementVemsi and oneElementVeosi:
                line = '\\frac{ '+veosi+' }{ '+vemsi+' } '
            elif oneElementVemsi and not oneElementVeosi:
                line = veosi+' \\frac{1}{ '+vemsi+' } '
            elif not oneElementVemsi and oneElementVeosi:
                line = '\\left( '+veosi+'\\right)\\cdot '+vemsi+'^{-1}'
            elif not oneElementVemsi and not oneElementVeosi:
                line = veosi+'\\cdot '+vemsi+'^{-1}'
        else:
            D = Matrix2LaTeX(self.pStimDef, self._SmallMatrix())
            fveosi='\\left( '+veosi+'\\right)' if oneElementVeosi else veosi
            fvemsi='\\left( '+vemsi+'\\right)' if oneElementVemsi else vemsi
            line = '\\left[ '+fveosi+'\\cdot '+D+'\\right]\\cdot'+\
                '\\left[ '+fvemsi+'\\cdot '+D+'\\right]^{-1}'
        if len(self.pMeasurementList) == 1 and len(self.pOutputList) == 1: H = 'H'
        else: H = '\\mathbf{H}'
        return self._AddEq(H+' = '+line)
    def LaTeXEquations(self):
        self.LaTeXSystemEquation()
        self.LaTeXTransferMatrix()
        return self