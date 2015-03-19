from Deembedder import Deembedder
from Symbolic import Symbolic
from SignalIntegrity.SystemDescriptions import Device
from SignalIntegrity.Helpers import Matrix2LaTeX
from numpy import matrix

class DeembedderSymbolic(Deembedder,Symbolic):
    def __init__(self,sd,equationEnvironment=False,small=False):
        self.Data=sd
        Symbolic.__init__(self,equationEnvironment,small)
    def SymbolicSolution(self):
        Bmsd=self.PortANames()
        Amsd=self.PortBNames()
        Adut=self.DutANames()
        Bdut=self.DutBNames()
        Internals=self.OtherNames(Bmsd+Amsd+Adut+Bdut)
        nG14=(self.WeightsMatrix(Bmsd,Amsd))
        nG15=(self.WeightsMatrix(Bmsd,Bdut))
        nG24=(self.WeightsMatrix(Adut,Amsd))
        nG25=(self.WeightsMatrix(Adut,Bdut))
        if len(Internals)>0:# internal nodes
            nG13=(self.WeightsMatrix(Bmsd,Internals))
            nG23=(self.WeightsMatrix(Adut,Internals))
            nG34=(self.WeightsMatrix(Internals,Amsd))
            nG35=(self.WeightsMatrix(Internals,Bdut))
            Gi33Text='\\left['+self.Identity()+'-'+\
                self._LaTeXMatrix(self.WeightsMatrix(Internals,Internals))+\
                '\\right]^{-1}'
            self._AddEq('\\mathbf{Gi_{33}} = '+Gi33Text)
            sGi33=' \\cdot\\mathbf{Gi_{33}}\\cdot '
            sF11=self._LaTeXMatrix(nG13)+sGi33+\
                self._LaTeXMatrix(nG34) # F11=G13*G33I*G34-G14
            ending=self._LaTeXMatrix(nG14)
            if ending != '0': sF11 = sF11 + ' + '+ending
            sF12 = self._LaTeXMatrix(nG13)+sGi33+\
                self._LaTeXMatrix(nG35) # F12=G13*G33I*G35-G15
            ending = self._LaTeXMatrix(nG15)
            if ending != '0': sF12 = sF12 + ' + '+ending
            sF21 = self._LaTeXMatrix(nG23)+sGi33+\
                self._LaTeXMatrix(nG34) # F21=G23*G33I*G34-G24
            ending = self._LaTeXMatrix(nG24)
            if ending != '0': sF21=sF21+' + '+ending
            sF22 = self._LaTeXMatrix(nG23)+sGi33+\
                self._LaTeXMatrix(nG35) # F22=G23*G33I*G35-G25
            ending = self._LaTeXMatrix(nG25)
            if ending != '0': sF22=sF22+' + '+ending
        else:# no internal nodes
            sF11 = self._LaTeXMatrix(nG14) # F11=-G14
            sF12 = self._LaTeXMatrix(nG15) # F12=-G15
            sF21 = self._LaTeXMatrix(nG24) # F21=-G24
            sF22 = self._LaTeXMatrix(nG25) # F22=-G25
        self._AddEq('\\mathbf{F_{11}} = '+sF11)
        self._AddEq('\\mathbf{F_{12}} = '+sF12)
        self._AddEq('\\mathbf{F_{21}} = '+sF21)
        self._AddEq('\\mathbf{F_{22}} = '+sF22)
        sF12='\\mathbf{F_{12}}'
        if len(Bmsd)!=len(Bdut): #if long and skinny F12 then
            #F12.getI()=(F12.transpose()*F12).getI()*F12.transpose()
            sF12i='\\left[ '+sF12+'^H\\cdot '+sF12+\
             '\\right]^{-1}\\cdot' + sF12+'^H\\cdot'
            #sF12i = '\\mathbf{F_{12}}^\\dagger'
        else: #square F12
            sF12i=sF12+'^{-1}\\cdot'
        #B=F12.getI()*(Sk-F11)
        BText=sF12i+'\\left[\\mathbf{Sk}-\\mathbf{F_{11}}\\right]'
        self._AddEq('\\mathbf{B}='+BText)
        #A=F21+F22*B
        self._AddEq('\\mathbf{A}=\\mathbf{F_{21}}+\\mathbf{F_{22}}\\cdot\\mathbf{B}')
        #Su=[(BL[u]*AL[u].getI()).tolist() for u in range(len(AL))]
        A=Device.SymbolicMatrix('A',len(Bdut),len(Bmsd))
        B=Device.SymbolicMatrix('B',len(Bdut),len(Bmsd))
        AL=self.Partition(matrix(A))# partition for multiple unknown devices
        BL=self.Partition(matrix(B))
        AL=[AL[u].tolist() for u in range(len(AL))]
        BL=[BL[u].tolist() for u in range(len(BL))]
        if len(AL)==1: #only one unknown device
            if len(Bmsd)!=len(Bdut): #if short and fat A
                #A.getI()=A.transpose()*(A*A.transpose()).getI()
                sAi='\\cdot\\mathbf{A}^H\\cdot\\left[\\mathbf{A}\\cdot'+\
                '\\mathbf{A}^H\\right]^{-1}'
            else: #square A
                sAi='\\cdot\\mathbf{A}^{-1}'
            self._AddEq('\\mathbf{Su}=\\mathbf{B}'+sAi)
        else: #multiple unknown devices
            un=self.UnknownNames()
            up=self.UnknownPorts()
            for u in range(len(AL)):
                AText=self._LaTeXMatrix(AL[u])
                BText=self._LaTeXMatrix(BL[u])
                if un[u]==len(Bmsd): # square A and B
                    SuText=BText+'\\cdot '+AText+'^{-1}'
                else: #short and fat A and B
                    SuText=BText+'\\cdot '+AText+'^H\\cdot\\left[ '+AText+\
                    '\\cdot'+AText+'^H\\right]^{-1}'
                self._AddEq('\\mathbf{'+un[u]+'}= '+SuText)
        return self
