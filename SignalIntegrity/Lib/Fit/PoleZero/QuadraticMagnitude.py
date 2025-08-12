"""
QuadraticMagnitude.py
"""
# Copyright (c) 2021 Nubis Communications, Inc.
# Copyright (c) 2018-2020 Teledyne LeCroy, Inc.
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

import math
import numpy as np

class GainMagnitude(object):
    def __init__(self,ω,G):
        self.ω=ω
        self.G=G
        self.H=G
        self.pHpG=1
        self.pHpG=10000

class DelayMagnitude(object):
    def __init__(self,ω,Td):
        self.ω=ω
        self.Td=Td
        self.H=1
        self.pHpTd=10000


class PolePairMagnitude(object):
    def __init__(self,ω,ωp,Qp):
        """
            pole pair expressed as H(s) = ωp^2/(s^2+ωp/Qp*s+ωp^2) = α/(γ+jδ)
        """
        self.ω=ω
        self.ωp=ωp
        self.Qp=Qp
        ω2=ω*ω
        ωp2=ωp*ωp
        Qp2=Qp*Qp
        α=ωp2
        γ=ωp2-ω2
        δ=ωp/Qp*ω
        γ2=γ*γ
        δ2=δ*δ
        γ2pδ2=γ2+δ2
        αγ=α*γ
        αδ=α*δ
        self.H=np.sqrt(αγ*αγ+αδ*αδ)/γ2pδ2       # H(ω)
        pαpωp=2*ωp                              # ∂α/∂ωp
        #pαpQp=0                                 # ∂α/∂Qp
        pγpωp=2*ωp                              # ∂γ/∂ωp
        #pγpQp=0                                 # ∂γ/∂Qp
        pδpωp=ω/Qp                              # ∂δ/∂ωp
        pδpQp=-ωp/Qp2*ω                         # ∂δ/∂Qp

        γ2pδ2_2=γ2pδ2*γ2pδ2
        self.pHpω0= α*(γ2pδ2*pαpωp-αγ*pγpωp-αδ*pδpωp)/(self.H*γ2pδ2_2)      # ∂H/∂ωp
        self.pHpQ=  α*(                    -αδ*pδpQp)/(self.H*γ2pδ2_2)      # ∂H/∂Qp
        pass

class ZeroPairMagnitude(object):
    def __init__(self,ω,ωz,Qz):
        """
            zero pair expressed as H(s) = (s^2+ωz/Qz*s+ωz^2)/ωz^2 = (α+jβ)/γ
        """
        self.ω=ω
        self.ωz=ωz
        self.Qz=Qz
        ωz2=ωz*ωz
        ω2=ω*ω
        Qz2=Qz*Qz
        α=ωz2-ω2
        α2=α*α
        β=ω*ωz/Qz
        β2=β*β
        γ=ωz2
        γ2=γ*γ
        γ3=γ2*γ
        αγ=α*γ
        βγ=β*γ

        α2pβ2=α2+β2
        self.H=np.sqrt(α2pβ2)/γ                 # |H(ω)|

        pαpωz=2*ωz                              # ∂α/∂ωz
        #pαpQz=0                                 # ∂α/∂Qz
        pβpωz=ω/Qz                              # ∂β/∂ωz
        pβpQz=-ω*ωz/Qz2                         # ∂β/∂Qz
        pγpωz=2*ωz                              # ∂γ/∂ωz
        #pγpQz=0                                 # ∂γ/∂Qz

        self.pHpω0= (αγ*pαpωz+βγ*pβpωz-α2pβ2*pγpωz)/(self.H*γ3)         # ∂H/∂ωz
        self.pHpQ=  (         βγ*pβpQz            )/(self.H*γ3)         # ∂H/∂Qz
        pass

class TransferFunctionOneFrequencyMagnitude(object):
    def __init__(self,ω,variable_list,num_zero_pairs,num_pole_pairs):
        """
        The variable list is assumed to be in the following format:

        Gain G and time delay Td followed by two variables per pole/zero pair
        of ωz, Qz or ωp, and Qp
        """
        self.ω=ω
        self.variable_list = variable_list.reshape(variable_list.shape[0],)
        self.gain = GainMagnitude(ω,self.variable_list[0])
        self.delay = DelayMagnitude(ω,self.variable_list[1])
        self.section_list = [ZeroPairMagnitude(ω,
                                        self.variable_list[s*2+2+0], # ωz
                                        self.variable_list[s*2+2+1]) # Qz
                                for s in range(num_zero_pairs)]
        self.section_list.extend([PolePairMagnitude(ω,
                                        self.variable_list[(s+num_zero_pairs)*2+2+0],  # ωp
                                        self.variable_list[(s+num_zero_pairs)*2+2+1])   # Qp
                                for s in range(num_pole_pairs)])

        all_sections=math.prod([self.section_list[s].H for s in range(len(self.section_list))])
        gd=self.gain.H*self.delay.H
        self.H=gd*all_sections
        self.pd=[]
        self.pd.append(self.gain.pHpG*self.delay.H*all_sections)
        # self.pd[0]=1e9
        self.pd.append(self.gain.H*self.delay.pHpTd*all_sections)
        # self.pd[0]=1e9
        for section in self.section_list:
            this_pd=[]
            gd_section_product_others=self.H/section.H # the product of all other sections with gain and delay
            this_pd.append(section.pHpω0*gd_section_product_others)
            this_pd.append(section.pHpQ*gd_section_product_others)
            self.pd.extend(this_pd)

class TransferFunctionMagnitude(object):
    def __init__(self,ω_list,variable_list,num_zero_pairs,num_pole_pairs):
        self.fF=[]
        self.fJ=[]
        for ω in ω_list:
            tf=TransferFunctionOneFrequencyMagnitude(ω,variable_list,num_zero_pairs,num_pole_pairs)
            self.fF.append(tf.H)
            self.fJ.append(tf.pd)

class TransferFunctionMagnitudeVectorized(object):
    def __init__(self,ω_list,variable_list,num_zero_pairs,num_pole_pairs):
        """
        The variable list is assumed to be in the following format:

        Gain G and time delay Td followed by two variables per pole/zero pair
        of ωz, Qz or ωp, and Qp
        """
        self.ω_list = np.array(ω_list)
        self.variable_list = variable_list.reshape(variable_list.shape[0],)
        self.gain = GainMagnitude(self.ω_list,self.variable_list[0])
        self.delay = DelayMagnitude(self.ω_list,self.variable_list[1])
        self.section_list = [ZeroPairMagnitude(self.ω_list,
                                        self.variable_list[s*2+2+0], # ωz
                                        self.variable_list[s*2+2+1]) # Qz
                                for s in range(num_zero_pairs)]
        self.section_list.extend([PolePairMagnitude(self.ω_list,
                                        self.variable_list[(s+num_zero_pairs)*2+2+0],  # ωp
                                        self.variable_list[(s+num_zero_pairs)*2+2+1])   # Qp
                                for s in range(num_pole_pairs)])

        self.H=self.gain.H*self.delay.H*math.prod([self.section_list[s].H for s in range(len(self.section_list))])
        self.pd=[]
        self.pd.append(self.gain.pHpG/self.gain.H*self.H)
        self.pd.append(self.delay.pHpTd/self.delay.H*self.H)
        for section in self.section_list:
            this_pd=[]
            this_pd.append(section.pHpω0/section.H*self.H)
            this_pd.append(section.pHpQ/section.H*self.H)
            self.pd.extend(this_pd)
        self.fF=self.H.tolist()
        self.fJ=np.array(self.pd).T.tolist()

if __name__ == '__main__': # pragma: no cover
    #o=BiquadSection(0.147,0.989,0.119,0.602,0.532)
    o=ZeroPairMagnitude(0.147,0.989,0.119)
    o=PolePairMagnitude(0.147,0.602,0.532)
    pass
