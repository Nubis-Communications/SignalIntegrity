"""
BiquadComplex.py
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

class Gain(object):
    def __init__(self,ω,G,fix_gain=True):
        self.ω=ω
        self.G=G
        self.H=G
        # if gain is fixed, make partial derivative very high
        self.pHpG=10000 if fix_gain else 1

class Delay(object):
    def __init__(self,ω,Td,fix_delay=False):
        self.ω=ω
        self.Td=Td
        self.H=np.exp(-1j*ω*Td)
        self.pHpTd=10000 if fix_delay else -1j*ω*self.H

class AllPassBiquadSection(object):
    def __init__(self,ω,ω0,Q):
        """
            biquad section is expressed as H(s) = (s^2+ω0/-Q*s+ω0^2)/(s^2+ω0/Q*s+ω0^2) = (α+jβ)/(α-jβ)
        """
        self.ω=ω
        self.ω0=ω0
        self.Q=Q
        ω02=ω0*ω0
        ω2=ω*ω
        Q2=Q*Q
        α=ω02-ω2
        α2=α*α
        β=-ω0/Q*ω
        β2=β*β
        α2pβ2=α2+β2
        β2mα2=β2-α2
        α2pβ22=α2pβ2*α2pβ2
        self.H=(α+1j*β)/(α-1j*β)                # H(ω)
        pαpω0=2*ω0                              # ∂α/∂ωz
        pαpQ=0                                  # ∂α/∂Qz
        pβpω0=-ω/Q                              # ∂β/∂ωz
        pβpQ=ω*ω0/Q2                            # ∂β/∂Qz
        RepHpα=4*α*β2/α2pβ22                    # Re(∂H/∂α)
        RepHpβ=-4*α2*β/α2pβ22                   # Re(∂H/∂β)
        ImpHpα=2*β*β2mα2/α2pβ22                 # Im(∂H/∂α)
        ImpHpβ=-2*α*β2mα2/α2pβ22                # Im(∂H/∂β)

        RepHpω0=RepHpα*pαpω0+RepHpβ*pβpω0       # Re(∂H/∂ωz)
        RepHpQ=RepHpα*pαpQ+RepHpβ*pβpQ          # Re(∂H/∂Qz)
        ImpHpω0=ImpHpα*pαpω0+ImpHpβ*pβpω0       # Im(∂H/∂ωz)
        ImpHpQ=ImpHpα*pαpQ+ImpHpβ*pβpQ          # Im(∂H/∂Qz)

        self.pHpω0=RepHpω0+1j*ImpHpω0           # ∂H/∂ωz
        self.pHpQ=RepHpQ+1j*ImpHpQ              # ∂H/∂Qz

class TransferFunctionOneFrequency(object):
    def __init__(self,ω,variable_list):
        """
        The variable list is assumed to be in the following format:

        Gain G and time delay Td followed by two variables per allpass biquad section in order
        of ω0, Q.
        """
        self.ω=ω
        self.variable_list = variable_list.reshape(variable_list.shape[0],)
        num_biquads = (len(self.variable_list)-2)//4
        self.gain = Gain(ω,self.variable_list[0])
        self.delay = Delay(ω,self.variable_list[1])
        self.biquad_list = [AllPassBiquadSection(ω,
                                          self.variable_list[s*2+2+0], # ω0
                                          self.variable_list[s*2+2+1]) # Q
                                for s in range(num_biquads)]
        bq=math.prod([self.biquad_list[s].H for s in range(len(self.biquad_list))])
        gd=self.gain.H*self.delay.H
        self.H=gd*bq
        self.pd=[]
        self.pd.append(self.gain.pHpG*self.delay.H*bq)
        # self.pd[0]=1e9
        self.pd.append(self.gain.H*self.delay.pHpTd*bq)
        # self.pd[0]=1e9
        for biquad in self.biquad_list:
            this_pd=[]
            gd_bq_product_others=self.H/biquad.H # the product of all other biquad sections with gain and delay
            this_pd.append(biquad.pHpω0*gd_bq_product_others)
            this_pd.append(biquad.pHpQ*gd_bq_product_others)
            self.pd.extend(this_pd)

class TransferFunction(object):
    def __init__(self,ω_list,variable_list):
        self.fF=[]
        self.fJ=[]
        for ω in ω_list:
            tf=TransferFunctionOneFrequency(ω,variable_list)
            self.fF.append(tf.H)
            self.fJ.append(tf.pd)

class TransferFunctionBiquadVectorized(object):
    def __init__(self,ω_list,variable_list):
        """
        The variable list is assumed to be in the following format:

        Gain G and time delay Td followed by two variables per allpass biquad section in order
        of ω0, Q.
        """
        self.ω_list = np.array(ω_list)
        self.variable_list = variable_list.reshape(variable_list.shape[0],)
        num_biquads = (len(self.variable_list)-2)//4
        self.gain = Gain(self.ω_list,self.variable_list[0])
        self.delay = Delay(self.ω_list,self.variable_list[1])
        self.biquad_list = [AllPassBiquadSection(ω_list,
                                          self.variable_list[s*2+2+0], # ωz
                                          self.variable_list[s*2+2+1]) # Qz
                                for s in range(num_biquads)]

        self.H=self.gain.H*self.delay.H*math.prod([bq.H for bq in self.biquad_list])
        self.pd=[]
        self.pd.append(self.gain.pHpG/self.gain.H*self.H)
        self.pd.append(self.delay.pHpTd/self.delay.H*self.H)
        for bq in self.biquad_list:
            this_pd=[]
            this_pd.append(bq.pHpω0/bq.H*self.H)
            this_pd.append(bq.pHpQ/bq.H*self.H)
            self.pd.extend(this_pd)
        self.fF=self.H.tolist()
        self.fJ=np.array(self.pd).T.tolist()

if __name__ == '__main__': # pragma: no cover
    o=BiquadSection(0.147,0.989,0.119,0.602,0.532)
    pass
