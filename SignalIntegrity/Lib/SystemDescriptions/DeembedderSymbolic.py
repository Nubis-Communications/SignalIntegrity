"""
Symbolic Deembedder
@see [US patent 8,566,058 B2](https://patents.google.com/patent/US8566058B2)
"""

# Copyright (c) 2018 Teledyne LeCroy, Inc.
# All rights reserved worldwide.
#
# This file is part of SignalIntegrity.
#
# SignalIntegrity is free software: You can redistribute it and/or modify it under the terms
# of the GNU General Public License as published by the Free Software Foundation, either
# version 3 of the License, or any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this program.
# If not, see <https://www.gnu.org/licenses/>

from SignalIntegrity.Lib.SystemDescriptions.Deembedder import Deembedder
from SignalIntegrity.Lib.SystemDescriptions.Symbolic import Symbolic
from SignalIntegrity.Lib.SystemDescriptions.Device import Device

from numpy import matrix

class DeembedderSymbolic(Deembedder,Symbolic):
    """
    Produces symbolic solutions to deembedding problems.
    @see [US patent 8,566,058 B2](https://patents.google.com/patent/US8566058B2)
    """
    def __init__(self,sd=None,**args):
        """Constructor

        @param sd (optional) instance of class SystemDescription
        @param args (optional) named arguments (name = value)

        Named arguments passed to the Symbolic class

        @see Symbolic
        """
        Deembedder.__init__(self,sd)
        Symbolic.__init__(self,**args)
        self.m_Sk = args['known'] if 'known' in args else 'Sk'
    def SymbolicSolution(self):
        """Generates a symbolic solution to a deembedding problem described
        in a Deembedder class.

        @return self

        The solution is held in the Symbolic class.

        @see Symbolic
        """
        Bmsd=self.PortANames(); Amsd=self.PortBNames()
        Adut=self.DutANames(); Bdut=self.DutBNames()
        Internals=self.OtherNames(Bmsd+Amsd+Adut+Bdut)
        sF11=snG14=self._LaTeXMatrix(self.WeightsMatrix(Bmsd,Amsd))
        sF12=snG15=self._LaTeXMatrix(self.WeightsMatrix(Bmsd,Bdut))
        sF21=snG24=self._LaTeXMatrix(self.WeightsMatrix(Adut,Amsd))
        sF22=snG25=self._LaTeXMatrix(self.WeightsMatrix(Adut,Bdut))
        if len(Internals)>0:# internal nodes
            snG13=self._LaTeXMatrix(self.WeightsMatrix(Bmsd,Internals))
            snG23=self._LaTeXMatrix(self.WeightsMatrix(Adut,Internals))
            snG34=self._LaTeXMatrix(self.WeightsMatrix(Internals,Amsd))
            snG35=self._LaTeXMatrix(self.WeightsMatrix(Internals,Bdut))
            snG33=self._LaTeXMatrix(self.WeightsMatrix(Internals,Internals))
            sGi33='\\left['+self._Identity()+'-'+snG33+'\\right]^{-1}'
            self._AddEq('\\mathbf{Gi_{33}} = '+sGi33)
            sGi33=' \\cdot\\mathbf{Gi_{33}}\\cdot '
            sF11=snG13+sGi33+snG34+((' + '+snG14) if snG14!='0' else '')
            sF12=snG13+sGi33+snG35+((' + '+snG15) if snG15!='0' else '')
            sF21=snG23+sGi33+snG34+((' + '+snG24) if snG24!='0' else '')
            sF22=snG23+sGi33+snG35+((' + '+snG25) if snG25!='0' else '')
        self._AddEq('\\mathbf{F_{11}} = '+sF11)
        self._AddEq('\\mathbf{F_{12}} = '+sF12)
        self._AddEq('\\mathbf{F_{21}} = '+sF21)
        self._AddEq('\\mathbf{F_{22}} = '+sF22)
        sF12='\\mathbf{F_{12}}'
        if len(Bmsd)!=len(Bdut): #if long and skinny F12 then
            sF12i='\\left[ '+sF12+'^H \\cdot '+sF12+\
             '\\right]^{-1} \\cdot' + sF12+'^H \\cdot'
        else: #square F12
            sF12i=sF12+'^{-1}\\cdot'
        BText=sF12i+'\\left[ \\mathbf{'+self.m_Sk+'} - \\mathbf{F_{11}} \\right] '
        self._AddEq('\\mathbf{B}='+BText)
        self._AddEq('\\mathbf{A}=\\mathbf{F_{21}}+ \\mathbf{F_{22}}\\cdot\\mathbf{B}')
        A=Device.SymbolicMatrix('A',len(Bdut),len(Bmsd))
        B=Device.SymbolicMatrix('B',len(Bdut),len(Bmsd))
        AL=self.Partition(matrix(A)); BL=self.Partition(matrix(B))
        AL=[AL[u].tolist() for u in range(len(AL))]
        BL=[BL[u].tolist() for u in range(len(BL))]
        un=self.UnknownNames(); up=self.UnknownPorts()
        if len(AL)==1: #only one unknown device
            if len(Bmsd)!=len(Bdut): #if short and fat A
                sAi='\\cdot \\mathbf{A}^H \\cdot\\left[ \\mathbf{A} \\cdot'+\
                '\\mathbf{A}^H \\right]^{-1}'
            else: #square A
                sAi='\\cdot \\mathbf{A}^{-1}'
            self._AddEq('\\mathbf{'+un[0]+'} = \\mathbf{B} '+sAi)
        else: #multiple unknown devices
            for u in range(len(AL)):
                AText=self._LaTeXMatrix(AL[u])
                BText=self._LaTeXMatrix(BL[u])
                if un[u]==len(Bmsd): # square A and B
                    SuText=BText+'\\cdot '+AText+'^{-1}'
                else: #short and fat A and B
                    SuText=BText+'\\cdot '+AText+'^H \\cdot \\left[ '+AText+\
                    '\\cdot'+AText+'^H \\right]^{-1}'
                self._AddEq('\\mathbf{'+un[u]+'}= '+SuText)
        return self