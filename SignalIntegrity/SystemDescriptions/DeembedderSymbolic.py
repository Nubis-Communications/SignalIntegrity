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
        F11Text=''
        F12Text=''
        F21Text=''
        F22Text=''
        if len(Internals)>0:# internal nodes
            nG13=(self.WeightsMatrix(Bmsd,Internals))
            nG23=(self.WeightsMatrix(Adut,Internals))
            nG34=(self.WeightsMatrix(Internals,Amsd))
            nG35=(self.WeightsMatrix(Internals,Bdut))
            """
            G33I=((identity(len(Internals)))-
                  (self.WeightsMatrix(Internals,Internals))).getI()
            """
            Gi33Text = '\\left[' + self.Identity() + '-' +\
                Matrix2LaTeX((self.WeightsMatrix(Internals,Internals)),self.SmallMatrix()) +\
                '\\right]^{-1}'
            self.AddLine(self.BeginEq() + '\\mathbf{Gi_{33}} = ' + Gi33Text + self.EndEq())
            F11Text = Matrix2LaTeX(nG13,self.SmallMatrix()) + ' \\cdot\\mathbf{Gi_{33}}\\cdot ' +\
                Matrix2LaTeX(nG34,self.SmallMatrix()) # F11=G13*G33I*G34-G14
            ending = Matrix2LaTeX(nG14,self.SmallMatrix())
            if ending != '0':
                F11Text = F11Text + ' + ' + ending
            F12Text = Matrix2LaTeX(nG13,self.SmallMatrix()) + ' \\cdot\\mathbf{Gi_{33}}\\cdot ' +\
                Matrix2LaTeX(nG35,self.SmallMatrix()) # F12=G13*G33I*G35-G15
            ending = Matrix2LaTeX(nG15,self.SmallMatrix())
            if ending != '0':
                F12Text = F12Text + ' + ' +  ending
            F21Text = Matrix2LaTeX(nG23,self.SmallMatrix()) + ' \\cdot\\mathbf{Gi_{33}}\\cdot ' +\
                Matrix2LaTeX(nG34,self.SmallMatrix()) # F21=G23*G33I*G34-G24
            ending = Matrix2LaTeX(nG24,self.SmallMatrix())
            if ending != '0':
                F21Text = F21Text + ' + ' + ending
            F22Text = Matrix2LaTeX(nG23,self.SmallMatrix()) + ' \\cdot\\mathbf{Gi_{33}}\\cdot ' +\
                Matrix2LaTeX(nG35,self.SmallMatrix()) # F22=G23*G33I*G35-G25
            ending = Matrix2LaTeX(nG25,self.SmallMatrix())
            if ending != '0':
                F22Text = F22Text + ' + ' + ending
        else:# no internal nodes
            F11Text = Matrix2LaTeX(nG14,self.SmallMatrix()) # F11=-G14
            F12Text = Matrix2LaTeX(nG15,self.SmallMatrix()) # F12=-G15
            F21Text = Matrix2LaTeX(nG24,self.SmallMatrix()) # F21=-G24
            F22Text = Matrix2LaTeX(nG25,self.SmallMatrix()) # F22=-G25
        self.AddLine(self.BeginEq() + '\\mathbf{F_{11}} = ' + F11Text + self.EndEq())
        self.AddLine(self.BeginEq() + '\\mathbf{F_{12}} = ' + F12Text + self.EndEq())
        self.AddLine(self.BeginEq() + '\\mathbf{F_{21}} = ' + F21Text + self.EndEq())
        self.AddLine(self.BeginEq() + '\\mathbf{F_{22}} = ' + F22Text + self.EndEq())
        F12iText = ''
        F12Text='\\mathbf{F_{12}}'
        if len(Bmsd)!=len(Bdut): #if long and skinny F12 then
            #F12.getI()=(F12.transpose()*F12).getI()*F12.transpose()
            F12iText = '\\left[ '+F12Text + '^H\\cdot ' + F12Text + '\\right]^{-1}\\cdot' + F12Text +'^H\\cdot'
            #F12iText = '\\mathbf{F_{12}}^\\dagger'
        else: #square F12
            F12iText = F12Text + '^{-1}\\cdot'
        #B=F12.getI()*(Sk-F11)
        BText = F12iText + '\\left[\\mathbf{Sk}-\\mathbf{F_{11}}\\right]'
        self.AddLine(self.BeginEq() + '\\mathbf{B}=' + BText + self.EndEq())
        #A=F21+F22*B
        self.AddLine(self.BeginEq() +\
            '\\mathbf{A}=\\mathbf{F_{21}}+\\mathbf{F_{22}}\\cdot\\mathbf{B}' +\
            self.EndEq())
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
                AiText = '\\cdot\\mathbf{A}^H\\cdot\\left[\\mathbf{A}\\cdot\\mathbf{A}^H\\right]^{-1}'
            else: #square A
                AiText = '\\cdot\\mathbf{A}^{-1}'
            self.AddLine(self.BeginEq() + '\\mathbf{Su}=\\mathbf{B}' + AiText + self.EndEq())
        else: #multiple unknown devices
            un = self.UnknownNames()
            up = self.UnknownPorts()
            for u in range(len(AL)):
                AText = Matrix2LaTeX(AL[u],self.SmallMatrix())
                BText = Matrix2LaTeX(BL[u],self.SmallMatrix())
                if un[u]==len(Bmsd): # square A and B
                    SuText = BText + '\\cdot ' + AText + '^{-1}'
                else: #short and fat A and B
                    SuText = BText + '\\cdot ' + AText + '^H\\cdot\\left[ '+ AText + '\\cdot' + AText + '^H\\right]^{-1}'
                self.AddLine(self.BeginEq() + '\\mathbf{' + un[u] + '}= ' + SuText + self.EndEq())
        return self
