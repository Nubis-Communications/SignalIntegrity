from VirtualProbe import VirtualProbe
from SystemSParametersSymbolic import SystemSParametersSymbolic
from SignalIntegrity.Helpers import Matrix2LaTeX
from SignalIntegrity.Helpers import MatrixMultiply

class VirtualProbeSymbolic(SystemSParametersSymbolic, VirtualProbe):
    def __init__(self,sd,**args):
        # self.Data=sd
        SystemSParametersSymbolic.__init__(self,sd,**args)
        VirtualProbe.__init__(self, sd)
    def LaTeXTransferFunctions(self):
        self._LaTeXSi()
        vemsi = MatrixMultiply(
            self.VoltageExtractionMatrix(self.pMeasurementList), self.SIPrime(True))
        oneElementVemsi = False
        if len(vemsi) == 1:
            if len(vemsi[0]) == 1:
                oneElementVemsi = True
        vemsi = Matrix2LaTeX(vemsi, self.SmallMatrix())
        veosi = MatrixMultiply(
            self.VoltageExtractionMatrix(self.pOutputList), self.SIPrime(True))
        oneElementVeosi = False
        if len(veosi) == 1:
            if len(veosi[0]) == 1:
                oneElementVeosi = True
        veosi = Matrix2LaTeX(veosi, self.SmallMatrix())
        line = ''
        if self.pStimDef is None:
            if oneElementVemsi:
                if oneElementVeosi:  # veosi/vemsi
                    line = '\\frac{ '+veosi+' }{ '+vemsi+' } '
                else:  # (veosi)*1/vemsi
                    line = veosi+' \\frac{1}{ '+vemsi+' } '
            else:
                if oneElementVeosi:  # veosi*(vemsi)^-1
                    line = '\\left( '+veosi+'\\right)\\cdot '+vemsi+'^{-1}'
                else:  # (veosi)*(vemsi)^-1
                    line = veosi+'\\cdot '+vemsi+'^{-1}'
        else:
            D = Matrix2LaTeX(self.pStimDef, self.SmallMatrix())

            if oneElementVemsi:
                if oneElementVeosi:  # (veosi*D)*(vemsi*D)^-1
                    line = '\\left[\\left( '+veosi+'\\right)\\cdot '+D+' \\right]\\cdot'+\
                        '\\left[\\left( '+vemsi+' \\right)\\cdot '+D+' \\right]^{-1}'
                else:  # ((veosi)*D)*(vemsi*D)^-1
                    line = '\\left[ '+veosi+' \\cdot '+D+' \\right]\\cdot'+\
                        '\\left[\\left( '+vemsi+' \\right)\\cdot '+D+' \\right]^{-1}'
            else:
                if oneElementVeosi:
                    line = '\\left[\\left( '+veosi+'\\right)\\cdot '+D+' \\right]\\cdot'+\
                        '\\left[ '+vemsi+' \\cdot '+D+' \\right]^{-1}'
                else:
                    line = '\\left[ '+veosi+' \\cdot '+D+' \\right]\\cdot'+\
                        '\\left[ '+vemsi+' \\cdot '+D+' \\right]^{-1}'
        if len(self.pMeasurementList) == 1 and len(self.pOutputList) == 1:
            H = 'H'
        else:
            H = '\\mathbf{H}'
        self.AddLine(self.BeginEq()+H+' = '+line+self.EndEq())
        return self
    def LaTeXTransferFunctions2(self):
        self._LaTeXSi()
        sipr = Matrix2LaTeX(self.SIPrime(True), self.SmallMatrix())
        vem = Matrix2LaTeX(
            self.VoltageExtractionMatrix(self.pMeasurementList), self.SmallMatrix())
        veo = Matrix2LaTeX(
            self.VoltageExtractionMatrix(self.pOutputList), self.SmallMatrix())
        if self.pStimDef is None:
            line = self.BeginEq()+'\\left[ '+veo+' \\cdot '+sipr+' \\right]'+\
                ' \\left[ '+vem+' \\cdot '+sipr+' \\right]^{-1}'+self.EndEq()
        else:
            D = Matrix2LaTeX(self.pStimDef, self.SmallMatrix())
            line = self.BeginEq()+'\\left[ '+veo+' \\cdot '+sipr+' \\cdot '+D+' \\right]'+\
                '\\left[ '+vem+' \\cdot '+sipr+' \\cdot '+D+' \\right]^{-1}'+self.EndEq()
        self.AddLine(line)
        return self
    def LaTeXEquations(self):
        self.LaTeXSystemEquation()
        self.LaTeXTransferFunctions()
        return self
