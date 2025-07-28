"""
PoleZeroFitter.py
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

import cmath,math
import numpy as np

class Gain(object):
    def __init__(self,ω,G):
        self.ω=ω
        self.G=G
        self.H=G
        self.pHpG=1

class Delay(object):
    def __init__(self,ω,Td):
        self.ω=ω
        self.Td=Td
        self.H=cmath.exp(-1j*ω*Td)
        self.pHpTd=-1j*ω*cmath.exp(-1j*ω*Td)

class BiquadSection(object):
    def __init__(self,ω,ωz,Qz,ωp,Qp):
        """
            biquad section is expressed as H(s) = (s^2+ωz/Qz*s+ωz^2)/(s^2+ωp/Qp*s+ωp^2) = (α+jβ)/(γ+jδ)
        """
        self.ω=ω
        self.ωz=ωz
        self.Qz=Qz
        self.ωp=ωp
        self.Qp=Qp
        ωz2=ωz*ωz
        ω2=ω*ω
        ωp2=ωp*ωp
        Qp2=Qp*Qp
        Qz2=Qz*Qz
        α=(ωz2-ω2)*ωp2
        β=ωz/Qz*ω*ωp2
        γ=(ωp2-ω2)*ωz2
        δ=ωp/Qp*ω*ωz2
        γ2=γ*γ
        γ3=γ2*γ
        δ2=δ*δ
        δ3=δ2*δ
        self.H=(α+1j*β)/(γ+1j*δ)                # H(ω)
        pαpωz=2*ωz*ωp2                          # ∂α/∂ωz
        pαpQz=0                                 # ∂α/∂Qz
        pαpωp=2*(ωz2-ω2)*ωp                     # ∂α/∂ωp
        pαpQp=0                                 # ∂α/∂Qp
        pβpωz=1/Qz*ω*ωp2                        # ∂β/∂ωz
        pβpQz=-ωz/Qz2*ω*ωp2                     # ∂β/∂Qz
        pβpωp=2*ωz/Qz*ω*ωp                      # ∂β/∂ωp
        pβpQp=0                                 # ∂β/∂Qp
        pγpωz=2*(ωp2-ω2)*ωz                     # ∂γ/∂ωz
        pγpQz=0                                 # ∂γ/∂Qz
        pγpωp=2*ωp*ωz2                          # ∂γ/∂ωp
        pγpQp=0                                 # ∂γ/∂Qp
        pδpωz=2*ωp/Qp*ω*ωz                      # ∂δ/∂ωz
        pδpQz=0                                 # ∂δ/∂Qz
        pδpωp=1/Qp*ω*ωz2                        # ∂δ/∂ωp
        pδpQp=-ωp/Qp2*ω*ωz2                     # ∂δ/∂Qp
        denom=(γ2+δ2)*(γ2+δ2)
        RepHpα=(γ3+γ*δ2)/denom                  # Re(∂H/∂α)
        RepHpβ=(δ*γ2+δ3)/denom                  # Re(∂H/∂β)
        RepHpγ=(-2*β*δ*γ-α*γ2+α*δ2)/denom       # Re(∂H/∂γ)
        RePHpδ=(-2*α*γ*δ+β*γ2-β*δ2)/denom       # Re(∂H/∂δ)
        ImpHpα=(-δ*γ2-δ3)/denom                 # Im(∂H/∂α)
        ImpHpβ=(γ3+γ*δ2)/denom                  # Im(∂H/∂β)
        ImpHpγ=(2*α*δ*γ-β*γ2+β*δ2)/denom        # Im(∂H/∂γ)
        ImPHpδ=(-2*β*γ*δ-α*γ2+α*δ2)/denom       # Im(∂H/∂δ)

        RepHpωz=RepHpα*pαpωz+RepHpβ*pβpωz+RepHpγ*pγpωz+RePHpδ*pδpωz     # Re(∂H/∂ωz)
        RepHpQz=RepHpα*pαpQz+RepHpβ*pβpQz+RepHpγ*pγpQz+RePHpδ*pδpQz     # Re(∂H/∂Qz)
        RepHpωp=RepHpα*pαpωp+RepHpβ*pβpωp+RepHpγ*pγpωp+RePHpδ*pδpωp     # Re(∂H/∂ωp)
        RepHpQp=RepHpα*pαpQp+RepHpβ*pβpQp+RepHpγ*pγpQp+RePHpδ*pδpQp     # Re(∂H/∂Qp)
        ImpHpωz=ImpHpα*pαpωz+ImpHpβ*pβpωz+ImpHpγ*pγpωz+ImPHpδ*pδpωz     # Im(∂H/∂ωz)
        ImpHpQz=ImpHpα*pαpQz+ImpHpβ*pβpQz+ImpHpγ*pγpQz+ImPHpδ*pδpQz     # Im(∂H/∂Qz)
        ImpHpωp=ImpHpα*pαpωp+ImpHpβ*pβpωp+ImpHpγ*pγpωp+ImPHpδ*pδpωp     # Im(∂H/∂ωp)
        ImpHpQp=ImpHpα*pαpQp+ImpHpβ*pβpQp+ImpHpγ*pγpQp+ImPHpδ*pδpQp     # Im(∂H/∂Qp)

        self.pHpωz=RepHpωz+1j*ImpHpωz           # ∂H/∂ωz
        self.pHpQz=RepHpQz+1j*ImpHpQz           # ∂H/∂Qz
        self.pHpωp=RepHpωp+1j*ImpHpωp           # ∂H/∂ωp
        self.pHpQp=RepHpQp+1j*ImpHpQp           # ∂H/∂Qp

class TransferFunctionOneFrequency(object):
    def __init__(self,ω,variable_list):
        """
        The variable list is assumed to be in the following format:

        Gain G and time delay Td followed by four variables per biquad section in order
        of ωz, Qz, ωp, and Qp
        """
        self.ω=ω
        self.variable_list = variable_list.reshape(variable_list.shape[0],)
        num_biquads = (len(self.variable_list)-2)//4
        self.gain = Gain(ω,self.variable_list[0])
        self.delay = Delay(ω,self.variable_list[1])
        self.biquad_list = [BiquadSection(ω,
                                          self.variable_list[s*4+2+0], # ωz
                                          self.variable_list[s*4+2+1], # Qz
                                          self.variable_list[s*4+2+2], # ωp
                                          self.variable_list[s*4+2+3]) # Qp
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
            this_pd.append(biquad.pHpωz*gd_bq_product_others)
            this_pd.append(biquad.pHpQz*gd_bq_product_others)
            this_pd.append(biquad.pHpωp*gd_bq_product_others)
            this_pd.append(biquad.pHpQp*gd_bq_product_others)
            self.pd.extend(this_pd)

class TransferFunction(object):
    def __init__(self,ω_list,variable_list):
        self.fF=[]
        self.fJ=[]
        for ω in ω_list:
            tf=TransferFunctionOneFrequency(ω,variable_list)
            self.fF.append(tf.H)
            self.fJ.append(tf.pd)

from SignalIntegrity.Lib.Fit.LevMar import LevMar
class PoleZeroLevMar(LevMar):
    """fits a pole/zero model to a frequency response"""
    def __init__(self,fr,num_biquads,callback=None):
        """Constructor  
        Initializes the fit of a pole/zero model to a frequency response.
        @param fr instance of class FrequencyResponse to fit to.
        @param num_biquads int number of biquad sections to fit.
        """
        self.f=fr.Frequencies()
        self.w=[2.*math.pi*f for f in self.f]
        self.y=np.array(fr.Values()).reshape(-1, 1)
        guess=self.Guess(self.f[1]*10, self.f[-1], num_biquads)
        guess[0]=self.y[0][0]
        guess[1]=17e-12
        LevMar.__init__(self,callback)
        LevMar.Initialize(self, np.array(guess).reshape(-1,1), np.array(self.y))
        self.ccm.Initialize(tolerance=self.ccm._tolerance,
                            maxIterations=self.ccm._maxIterations*5,
                            lambdaTimeConstant=self.ccm._lambdaTimeConstant,
                            mseTimeConstant=self.ccm._mseTimeConstant*2,
                            mseUnchanging=self.ccm._mseUnchanging/1000000.,
                            lambdaUnchanging=self.ccm._lambdaUnchanging*0)
    @staticmethod
    def Guess(fs,fe,num_biquads):
        """constructs a reasonable guess  
        The guess is designed to be set of real poles and zeros.
        It starts with a zero, followed by two poles, followed by two zeros, and so on.
        This sequence of zppz zppz zppz ... where the zeros and poles are on an equal logarithmic
        spacing causes the guess to be bumpy.
        The gain is set to unity and the delay is set to zero initially.
        @param fs float start frequency
        @param fe float end frequency
        @param num_biquads int number of biquad sections
        """
        log_fe=math.log10(fe)
        log_fs=math.log10(fs)
        twopi=2*math.pi
        num_poles_zeros = num_biquads*4
        frequency_location = [10.0**((log_fe-log_fs)/(num_poles_zeros-1)*npz + log_fs)
                                for npz in range(num_poles_zeros)]
        wz = [math.sqrt(frequency_location[bq*4+0]*twopi*frequency_location[bq*4+3]*twopi)
                                for bq in range(num_biquads)]
        Qz = [wz[bq]/(frequency_location[bq*4+0]*twopi+frequency_location[bq*4+3]*twopi)
                                for bq in range(num_biquads)]
        wp = [math.sqrt(frequency_location[bq*4+1]*twopi*frequency_location[bq*4+2]*twopi)
                                for bq in range(num_biquads)]
        Qp = [wp[bq]/(frequency_location[bq*4+1]*twopi+frequency_location[bq*4+2]*twopi)
                                for bq in range(num_biquads)]
        G = 1
        Td = 0
        result = [G,Td]
        for bq in range(num_biquads):
            result.extend([wz[bq],Qz[bq],wp[bq],Qp[bq]])
        return result
    def fF(self,a):
        self.tf=TransferFunction(self.w,a)
        return np.array(self.tf.fF).reshape(-1, 1)
    def fJ(self,a,Fa=None):
        return np.array(self.tf.fJ)
    def AdjustVariablesAfterIteration(self,a):
        Qmax=20
        for r in range(len(a)):
            a[r][0]=a[r][0].real
        for r in range(3,len(a),2):
            a[r][0]=max(min(a[r][0],Qmax),-Qmax)
        return a
    def Results(self):
        return self.m_a
    def PrintResults(self):
        results=[self.m_a[r][0].real for r in range(self.m_a.shape[0])]
        from SignalIntegrity.Lib.ToSI import ToSI
        print(f"Gain: {results[0]} - {ToSI(20.*np.log10(results[0]),'dB',round=4)}")
        print(f"Delay: {ToSI(results[1],'s',round=4)}")
        num_biquads=(len(results)-2)//4
        for bq in range(num_biquads):
            print(f"biquad: {bq+1}")
            print(f"  fz: {ToSI(results[bq*4+2+0]/(2.*np.pi),'Hz',round=4)}")
            print(f"  Qz: {ToSI(results[bq*4+2+1],'',round=4)}")
            print(f"  fp: {ToSI(results[bq*4+2+2]/(2.*np.pi),'Hz',round=4)}")
            print(f"  Qp: {ToSI(results[bq*4+2+3],'',round=4)}")
        return self
    def WriteResultsToFile(self,filename):
        results=[self.m_a[r][0].real for r in range(self.m_a.shape[0])]
        with open(filename,'wt') as f:
            for result in results:
                f.write(str(result)+'\n')
        return self
    def WriteGoalToFile(self,filename):
        with open(filename,'wt') as f:
            for n in range(len(self.f)):
                f.write(str(self.f[n])+'\n')
                f.write(str(self.m_y[n][0].real)+'\n')
                f.write(str(self.m_y[n][0].imag)+'\n')
if __name__ == '__main__': # pragma: no cover
    #o=BiquadSection(0.147,0.989,0.119,0.602,0.532)
    
    pass