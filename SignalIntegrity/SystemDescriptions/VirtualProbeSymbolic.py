'''
 Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
 Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
 All Rights Reserved.

 Explicit license in accompanying README.txt file.  If you don't have that file
 or do not agree to the terms in that file, then you are not licensed to use
 this material whatsoever.
'''
from VirtualProbe import VirtualProbe
from SystemSParametersSymbolic import SystemSParametersSymbolic
from SignalIntegrity.Helpers import Matrix2LaTeX
from SignalIntegrity.Helpers import MatrixMultiply

class VirtualProbeSymbolic(SystemSParametersSymbolic, VirtualProbe):
    def __init__(self,sd=None,**args):
        SystemSParametersSymbolic.__init__(self,sd,**args)
        VirtualProbe.__init__(self, sd)
    def LaTeXTransferMatrix(self):
        self.Check()
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