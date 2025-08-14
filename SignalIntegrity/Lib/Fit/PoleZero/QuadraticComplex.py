"""
QuadraticComplex.py
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

class GainComplex(object):
    def __init__(self,ω,G,fix_gain=False):
        self.ω=ω
        self.G=G
        self.H=G
        # if gain is fixed, make partial derivative very high
        self.pHpG=10000 if fix_gain else 1

class DelayComplex(object):
    def __init__(self,ω,Td,fix_delay=False):
        self.ω=ω
        self.Td=Td
        self.H=np.exp(-1j*ω*Td)
        self.pHpTd=10000 if fix_delay else -1j*ω*self.H

class PolePairComplex(object):
    def __init__(self,ω,ωp,Qp):
        """
            pole pair expressed as H(s) = ωp^2/(s^2+ωp/Qp*s+ωp^2) = (α+jβ)/(γ+jδ)
        """
        self.ω=ω
        self.ωp=ωp
        self.Qp=Qp
        ω2=ω*ω
        ωp2=ωp*ωp
        Qp2=Qp*Qp
        α=ωp2
        β=0
        γ=ωp2-ω2
        δ=ωp/Qp*ω
        γ2=γ*γ
        δ2=δ*δ
        self.H=(α+1j*β)/(γ+1j*δ)                # H(ω)
        pαpωp=2*ωp                              # ∂α/∂ωp
        #pαpQp=0                                 # ∂α/∂Qp
        #pβpωp=0                                 # ∂β/∂ωp
        #pβpQp=0                                 # ∂β/∂Qp
        pγpωp=2*ωp                              # ∂γ/∂ωp
        #pγpQp=0                                 # ∂γ/∂Qp
        pδpωp=ω/Qp                              # ∂δ/∂ωp
        pδpQp=-ωp/Qp2*ω                         # ∂δ/∂Qp
        denom=(γ2+δ2)
        denom2=denom*denom
        RepHpα=γ/denom                          # Re(∂H/∂α)
        #RepHpβ=0                                # Re(∂H/∂β)
        RepHpγ=α*(δ2-γ2)/denom2                 # Re(∂H/∂γ)
        RepHpδ=-2*α*γ*δ/denom2                  # Re(∂H/∂δ)
        ImpHpα=-δ/denom                         # Im(∂H/∂α)
        #ImpHpβ=0                                # Im(∂H/∂β)
        ImpHpγ=2*α*δ*γ/denom2                   # Im(∂H/∂γ)
        ImpHpδ=α*(δ2-γ2)/denom2                 # Im(∂H/∂δ)

        RepHpωp=RepHpα*pαpωp+             RepHpγ*pγpωp+RepHpδ*pδpωp     # Re(∂H/∂ωp)
        RepHpQp=                                       RepHpδ*pδpQp     # Re(∂H/∂Qp)
        ImpHpωp=ImpHpα*pαpωp+             ImpHpγ*pγpωp+ImpHpδ*pδpωp     # Im(∂H/∂ωp)
        ImpHpQp=                                       ImpHpδ*pδpQp     # Im(∂H/∂Qp)

        self.pHpω0=RepHpωp+1j*ImpHpωp           # ∂H/∂ωp
        self.pHpQ=RepHpQp+1j*ImpHpQp            # ∂H/∂Qp

class ZeroPairComplex(object):
    def __init__(self,ω,ωz,Qz):
        """
            zero pair expressed as H(s) = (s^2+ωz/Qz*s+ωz^2)/ωz^2 = (α+jβ)/(γ+jδ)
        """
        self.ω=ω
        self.ωz=ωz
        self.Qz=Qz
        ωz2=ωz*ωz
        ω2=ω*ω
        Qz2=Qz*Qz
        α=ωz2-ω2
        β=ω*ωz/Qz
        γ=ωz2
        δ=0
        γ2=γ*γ
        self.H=(α+1j*β)/(γ+1j*δ)                # H(ω)
        pαpωz=2*ωz                              # ∂α/∂ωz
        #pαpQz=0                                 # ∂α/∂Qz
        pβpωz=ω/Qz                              # ∂β/∂ωz
        pβpQz=-ω*ωz/Qz2                         # ∂β/∂Qz
        pγpωz=2*ωz                              # ∂γ/∂ωz
        #pγpQz=0                                 # ∂γ/∂Qz
        #pδpωz=0                                 # ∂δ/∂ωz
        #pδpQz=0                                 # ∂δ/∂Qz
        RepHpα=1/γ                              # Re(∂H/∂α)
        #RepHpβ=0                                # Re(∂H/∂β)
        RepHpγ=-α/γ2                            # Re(∂H/∂γ)
        #RepHpδ=0                                # Re(∂H/∂δ)
        #ImpHpα=0                                # Im(∂H/∂α)
        ImpHpβ=1/γ                              # Im(∂H/∂β)
        ImpHpγ=-β/γ2                            # Im(∂H/∂γ)
        #ImpHpδ=0                                # Im(∂H/∂δ)

        RepHpωz=RepHpα*pαpωz+            +RepHpγ*pγpωz                  # Re(∂H/∂ωz)
        RepHpQz=0                                                       # Re(∂H/∂Qz)
        ImpHpωz=             ImpHpβ*pβpωz+ImpHpγ*pγpωz                  # Im(∂H/∂ωz)
        ImpHpQz=             ImpHpβ*pβpQz                               # Im(∂H/∂Qz)

        self.pHpω0=RepHpωz+1j*ImpHpωz           # ∂H/∂ωz
        self.pHpQ=RepHpQz+1j*ImpHpQz            # ∂H/∂Qz

class TransferFunctionOneFrequencyComplex(object):
    def __init__(self,
                 ω,
                 variable_list,
                 num_zero_pairs,
                 num_pole_pairs,
                 fix_gain=False,
                 fix_delay=False):
        """
        The variable list is assumed to be in the following format:

        Gain G and time delay Td followed by two variables per pole/zero pair
        of ωz, Qz or ωp, and Qp
        """
        self.ω=ω
        self.variable_list = variable_list.reshape(variable_list.shape[0],)
        self.gain = GainComplex(ω,self.variable_list[0],fix_gain)
        self.delay = DelayComplex(ω,self.variable_list[1],fix_delay)
        self.section_list = [ZeroPairComplex(ω,
                                        self.variable_list[s*2+2+0], # ωz
                                        self.variable_list[s*2+2+1]) # Qz
                                for s in range(num_zero_pairs)]
        self.section_list.extend([PolePairComplex(ω,
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

class TransferFunctionComplex(object):
    def __init__(self,
                 ω_list,
                 variable_list,
                 num_zero_pairs,
                 num_pole_pairs,
                 fix_gain=False,
                 fix_delay=False):
        self.fF=[]
        self.fJ=[]
        for ω in ω_list:
            tf=TransferFunctionOneFrequencyComplex(ω,
                                                   variable_list,
                                                   num_zero_pairs,
                                                   num_pole_pairs,
                                                   fix_gain,
                                                   fix_delay)
            self.fF.append(tf.H)
            self.fJ.append(tf.pd)

class TransferFunctionComplexVectorized(object):
    def __init__(self,
                 ω_list,
                 variable_list,
                 num_zero_pairs,
                 num_pole_pairs,
                 fix_gain=False,
                 fix_delay=False):
        """
        The variable list is assumed to be in the following format:

        Gain G and time delay Td followed by two variables per pole/zero pair
        of ωz, Qz or ωp, and Qp
        """
        self.ω_list = np.array(ω_list)
        self.variable_list = variable_list.reshape(variable_list.shape[0],)
        self.gain = GainComplex(self.ω_list,self.variable_list[0],fix_gain)
        self.delay = DelayComplex(self.ω_list,self.variable_list[1],fix_delay)
        self.section_list = [ZeroPairComplex(self.ω_list,
                                        self.variable_list[s*2+2+0], # ωz
                                        self.variable_list[s*2+2+1]) # Qz
                                for s in range(num_zero_pairs)]
        self.section_list.extend([PolePairComplex(self.ω_list,
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
    o=ZeroPairComplex(0.147,0.989,0.119)
    o=PolePairComplex(0.147,0.602,0.532)
    pass
