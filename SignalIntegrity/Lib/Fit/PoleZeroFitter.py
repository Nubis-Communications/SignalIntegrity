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

class PolePair(object):
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
        pαpQp=0                                 # ∂α/∂Qp
        pβpωp=0                                 # ∂β/∂ωp
        pβpQp=0                                 # ∂β/∂Qp
        pγpωp=2*ωp                              # ∂γ/∂ωp
        pγpQp=0                                 # ∂γ/∂Qp
        pδpωp=ω/Qp                              # ∂δ/∂ωp
        pδpQp=-ωp/Qp2*ω                         # ∂δ/∂Qp
        denom=(γ2+δ2)
        denom2=denom*denom
        RepHpα=γ/denom                          # Re(∂H/∂α)
        RepHpβ=0                                # Re(∂H/∂β)
        RepHpγ=α*(δ2-γ2)/denom2                 # Re(∂H/∂γ)
        RepHpδ=-2*α*γ*δ/denom2                  # Re(∂H/∂δ)
        ImpHpα=-δ/denom                         # Im(∂H/∂α)
        ImpHpβ=0                                # Im(∂H/∂β)
        ImpHpγ=2*α*δ*γ/denom2                   # Im(∂H/∂γ)
        ImpHpδ=α*(δ2-γ2)/denom2                 # Im(∂H/∂δ)

        RepHpωp=RepHpα*pαpωp+RepHpβ*pβpωp+RepHpγ*pγpωp+RepHpδ*pδpωp     # Re(∂H/∂ωp)
        RepHpQp=RepHpα*pαpQp+RepHpβ*pβpQp+RepHpγ*pγpQp+RepHpδ*pδpQp     # Re(∂H/∂Qp)
        ImpHpωp=ImpHpα*pαpωp+ImpHpβ*pβpωp+ImpHpγ*pγpωp+ImpHpδ*pδpωp     # Im(∂H/∂ωp)
        ImpHpQp=ImpHpα*pαpQp+ImpHpβ*pβpQp+ImpHpγ*pγpQp+ImpHpδ*pδpQp     # Im(∂H/∂Qp)

        self.pHpω0=RepHpωp+1j*ImpHpωp           # ∂H/∂ωp
        self.pHpQ=RepHpQp+1j*ImpHpQp            # ∂H/∂Qp

class ZeroPair(object):
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
        pαpQz=0                                 # ∂α/∂Qz
        pβpωz=ω/Qz                              # ∂β/∂ωz
        pβpQz=-ω*ωz/Qz2                         # ∂β/∂Qz
        pγpωz=2*ωz                              # ∂γ/∂ωz
        pγpQz=0                                 # ∂γ/∂Qz
        pδpωz=0                                 # ∂δ/∂ωz
        pδpQz=0                                 # ∂δ/∂Qz
        RepHpα=1/γ                              # Re(∂H/∂α)
        RepHpβ=0                                # Re(∂H/∂β)
        RepHpγ=-α/γ2                            # Re(∂H/∂γ)
        RepHpδ=0                                # Re(∂H/∂δ)
        ImpHpα=0                                # Im(∂H/∂α)
        ImpHpβ=1/γ                              # Im(∂H/∂β)
        ImpHpγ=-β/γ2                            # Im(∂H/∂γ)
        ImpHpδ=0                                # Im(∂H/∂δ)

        RepHpωz=RepHpα*pαpωz+RepHpβ*pβpωz+RepHpγ*pγpωz+RepHpδ*pδpωz     # Re(∂H/∂ωz)
        RepHpQz=RepHpα*pαpQz+RepHpβ*pβpQz+RepHpγ*pγpQz+RepHpδ*pδpQz     # Re(∂H/∂Qz)
        ImpHpωz=ImpHpα*pαpωz+ImpHpβ*pβpωz+ImpHpγ*pγpωz+ImpHpδ*pδpωz     # Im(∂H/∂ωz)
        ImpHpQz=ImpHpα*pαpQz+ImpHpβ*pβpQz+ImpHpγ*pγpQz+ImpHpδ*pδpQz     # Im(∂H/∂Qz)

        self.pHpω0=RepHpωz+1j*ImpHpωz           # ∂H/∂ωz
        self.pHpQ=RepHpQz+1j*ImpHpQz            # ∂H/∂Qz

class TransferFunctionOneFrequency(object):
    def __init__(self,ω,variable_list,num_zero_pairs,num_pole_pairs):
        """
        The variable list is assumed to be in the following format:

        Gain G and time delay Td followed by two variables per pole/zero pair
        of ωz, Qz or ωp, and Qp
        """
        self.ω=ω
        self.variable_list = variable_list.reshape(variable_list.shape[0],)
        self.gain = Gain(ω,self.variable_list[0])
        self.delay = Delay(ω,self.variable_list[1])
        self.section_list = [ZeroPair(ω,
                                        self.variable_list[s*2+2+0], # ωz
                                        self.variable_list[s*2+2+1]) # Qz
                                for s in range(num_zero_pairs)]
        self.section_list.extend([PolePair(ω,
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

class TransferFunction(object):
    def __init__(self,ω_list,variable_list,num_zero_pairs,num_pole_pairs):
        self.fF=[]
        self.fJ=[]
        for ω in ω_list:
            tf=TransferFunctionOneFrequency(ω,variable_list,num_zero_pairs,num_pole_pairs)
            self.fF.append(tf.H)
            self.fJ.append(tf.pd)

from SignalIntegrity.Lib.Fit.LevMar import LevMar
class PoleZeroLevMar(LevMar):
    """fits a pole/zero model to a frequency response"""
    def __init__(self,fr,num_zero_pairs,num_pole_pairs,
                 guess=None,
                 max_delay=None,
                 min_delay=0,
                 max_Q=5.,
                 initial_delay=0,
                 LHP_zeros=True,
                 real_zeros=False,
                 max_iterations=100000,
                 mse_unchanging_threshold=1e-6,
                 callback=None):
        """Constructor  
        Initializes the fit of a pole/zero model to a frequency response.
        @param fr instance of class FrequencyResponse to fit to.
        @param num_zero_pairs int number of zero pairs.
        @param num_pole_pairs in number of pole pairs.
        """
        self.num_zero_pairs=num_zero_pairs
        self.num_pole_pairs=num_pole_pairs
        self.min_delay=min_delay
        self.max_delay=max_delay
        self.initial_delay=initial_delay
        self.max_Q=max_Q
        self.LHP_zeros=LHP_zeros
        self.real_zeros=real_zeros
        self.f=fr.Frequencies()
        # determine the right scaling factor for frequencies
        # it's the best engineering exponent
        self.mul=math.pow(10,math.floor(math.log10(self.f[-1])/3)*3)
        # scale all of the frequencies by this multiplier
        self.f=[v/self.mul for v in self.f]
        self.w=[2.*math.pi*f for f in self.f]
        self.y=np.array(fr.Values()).reshape(-1, 1)
        if guess is None:
            guess=self.Guess2(self.f[1], self.f[-1], num_zero_pairs,num_pole_pairs)
            guess[0]=self.y[0][0]
            guess[1]=self.initial_delay*self.mul
        else:
            guess[1]=guess[1]*self.mul
            for s in range(self.num_pole_pairs+self.num_zero_pairs):
                guess[s*2+2+0] = guess[s*2+2+0]/self.mul
        LevMar.__init__(self,callback)
        LevMar.Initialize(self, np.array(guess).reshape(-1,1), np.array(self.y))
        self.ccm.Initialize(tolerance=self.ccm._tolerance,
                            maxIterations=max_iterations,
                            lambdaTimeConstant=self.ccm._lambdaTimeConstant,
                            mseTimeConstant=self.ccm._mseTimeConstant,
                            mseUnchanging=mse_unchanging_threshold,
                            lambdaUnchanging=self.ccm._lambdaUnchanging)
        #self.m_lambdaMultiplier=1.01
    @staticmethod
    def Guess(fs,fe,num_zero_pairs,num_pole_pairs):
        """constructs a reasonable guess  
        The guess is designed to be set of real poles and zeros.
        It starts with a zero, followed by two poles, followed by two zeros, and so on.
        This sequence of zppz zppz zppz ... where the zeros and poles are on an equal logarithmic
        spacing causes the guess to be bumpy.
        The gain is set to unity and the delay is set to zero initially.
        @param fs float start frequency
        @param fe float end frequency
        @param num_zero_pairs int number of pairs of zeros
        @param num_pole_pairs int number of pairs of poles
        @remark there must be more pole pairs than zero pairs
        """
        minQ=0.5
        maxQ=20
        log_fe=math.log10(fe)
        log_fs=math.log10(fs)
        twopi=2*math.pi
        num_pole_zero_pairs = num_zero_pairs+num_pole_pairs

        frequency_location = [10.0**((log_fe-log_fs)/(num_pole_zero_pairs-1)*npz + log_fs)
                                for npz in range(num_pole_zero_pairs)]

        # for each frequency location, determine whether it is a zero or a pole
        is_a_pole = [True for _ in frequency_location]
        if num_zero_pairs > 0:
            skip=math.ceil(num_pole_pairs/num_zero_pairs)
            start=math.ceil(num_pole_pairs/num_zero_pairs/2)
            for zp in range(num_zero_pairs):
                is_a_pole[zp*(skip+1)+start]=False

        # if not is_a_pole[0]:
        #     is_a_pole=[is_a_pole[-1]]+is_a_pole[1:]

        BW=fe
        # generate the pole frequency and Q for each frequency location
        w0 = [fl*twopi for fl in frequency_location]
        Q = [min(max(fl/BW,minQ),maxQ) for fl in frequency_location]

        # gather these into poles and zeros
        zero_list=[]
        pole_list=[]

        for pzi in range(len(frequency_location)):
            if is_a_pole[pzi]:
                pole_list.extend([w0[pzi],Q[pzi]])
            else:
                zero_list.extend([w0[pzi],Q[pzi]])

        # stack the zero information on top of the pole information
        G = 1
        Td = 0
        result = [G,Td]+zero_list+pole_list
        return result
    @staticmethod
    def Guess2(fs,fe,num_zero_pairs,num_pole_pairs):
        """constructs a reasonable guess  
        The guess is designed to be set of real poles and zeros.
        It starts with a zero, followed by two poles, followed by two zeros, and so on.
        This sequence of zppz zppz zppz ... where the zeros and poles are on an equal logarithmic
        spacing causes the guess to be bumpy.
        The gain is set to unity and the delay is set to zero initially.
        @param fs float start frequency
        @param fe float end frequency
        @param num_zero_pairs int number of pairs of zeros
        @param num_pole_pairs int number of pairs of poles
        @remark there must be more pole pairs than zero pairs
        """
        minQ=0.5
        maxQ=20
        log_fe=math.log10(fe)
        log_fs=math.log10(fs)
        twopi=2*math.pi
        num_pole_zero_pairs = num_zero_pairs+num_pole_pairs

        frequency_location = [10.0**((log_fe-log_fs)/(num_pole_zero_pairs-1)*npz + log_fs)
                                for npz in range(num_pole_zero_pairs)]

        # for each frequency location, determine whether it is a zero or a pole
        is_a_pole = [True for _ in frequency_location]
        if num_zero_pairs > 0:
            skip=num_pole_pairs/num_zero_pairs
            start=math.floor(num_pole_pairs/num_zero_pairs/2)
            for zp in range(num_zero_pairs):
                is_a_pole[int(zp*(skip+1))+start]=False

        # if not is_a_pole[0]:
        #     is_a_pole=[is_a_pole[-1]]+is_a_pole[1:]

        BW=fe/4
        # generate the pole frequency and Q for each frequency location
        pz = [(-BW+1j*fl)*twopi for fl in frequency_location]

        # gather these into poles and zeros
        zero_list=[]
        pole_list=[]

        for pzi in range(len(frequency_location)):
            w0=abs(pz[pzi])
            Q=abs(w0/(2*pz[pzi].real))
            if is_a_pole[pzi]:
                pole_list.extend([w0,Q])
            else:
                zero_list.extend([w0,Q])

        # stack the zero information on top of the pole information
        G = 1
        Td = 0.012
        result = [G,Td]+zero_list+pole_list
        return result
    @staticmethod
    def Guess3(fs,fe,num_zero_pairs,num_pole_pairs):
        """constructs a reasonable guess  
        The guess is designed to be set of real poles and zeros.
        It starts with a zero, followed by two poles, followed by two zeros, and so on.
        This sequence of zppz zppz zppz ... where the zeros and poles are on an equal logarithmic
        spacing causes the guess to be bumpy.
        The gain is set to unity and the delay is set to zero initially.
        @param fs float start frequency
        @param fe float end frequency
        @param num_zero_pairs int number of pairs of zeros
        @param num_pole_pairs int number of pairs of poles
        @remark there must be more pole pairs than zero pairs
        """
        num_pole_zero_pairs = num_zero_pairs+num_pole_pairs

        # for each frequency location, determine whether it is a zero or a pole
        is_a_pole = [True for _ in range(num_pole_zero_pairs)]
        if num_zero_pairs > 0:
            skip=num_pole_pairs/num_zero_pairs
            start=math.floor(num_pole_pairs/num_zero_pairs/2)
            for zp in range(num_zero_pairs):
                is_a_pole[int(zp*(skip+1))+start]=False

        # angles for each pole in the guess off the negative access
        theta_list=[(pz+1)/num_pole_zero_pairs*80 for pz in range(num_pole_zero_pairs)]
        zeta_list=[math.cos(t*math.pi/180) for t in theta_list]
        Q_list=[1/(2*z) for z in zeta_list]

        # gather these into poles and zeros
        zero_list=[]
        pole_list=[]

        for pzi in range(num_pole_zero_pairs):
            w0=abs(fe/4*2*math.pi)
            Q=Q_list[pzi]
            if is_a_pole[pzi]:
                pole_list.extend([w0,Q])
            else:
                zero_list.extend([w0,Q])

        # stack the zero information on top of the pole information
        G = 1
        Td = 0.012
        result = [G,Td]+zero_list+pole_list
        return result

    def fF(self,a):
        self.tf=TransferFunction(self.w,a,self.num_zero_pairs,self.num_pole_pairs)
        return np.array(self.tf.fF).reshape(-1, 1)
    def fJ(self,a,Fa=None):
        # self.tf=TransferFunction(self.w,a,self.num_zero_pairs,self.num_pole_pairs)
        return np.array(self.tf.fJ)
    def AdjustVariablesAfterIteration(self,a):
        from random import random
        wmax=self.f[-1]*2.*np.pi*5
        # variables must be real
        for r in range(len(a)):
            a[r][0]=a[r][0].real
        # for r in range(len(a)):
        #     a[r][0]=a[r][0]+random()/1000000
        # delay greater than minimum
        if self.min_delay != None:
            a[1][0]=max(a[1][0],self.min_delay*self.mul)
        # delay must less than maximum
        if self.max_delay != None:
            a[1][0]=min(a[1][0],self.max_delay*self.mul)
        # Q cant be too high
        for r in range(3,len(a),2):
            a[r][0]=max(min(a[r][0],self.max_Q+random()/100),-self.max_Q-random()/100)
        # poles must be in the LHP
        for r in range(self.num_pole_pairs):
            a[r*2+2+self.num_zero_pairs*2+1][0]=abs(a[r*2+2+self.num_zero_pairs*2+1][0])
        if self.LHP_zeros == True:
            # zeros must be in the LHP
            for r in range(self.num_zero_pairs):
                a[r*2+2+1][0]=abs(a[r*2+2+1][0])
        if self.real_zeros:
            # zeros must be real
            for r in range(self.num_zero_pairs):
                a[r*2+2+1][0]=min(a[r*2+2+1][0],0.5+random()/100)
        # w0 can't be too high
        for r in range(2,len(a),2):
            a[r][0]=abs(a[r][0])
            a[r][0]=min(a[r][0],wmax+random()/100)
        a[0][0]=self.y[0][0].real
        return a
    def Results(self):
        results=[self.m_a[r][0].real for r in range(self.m_a.shape[0])]
        results[1]=results[1]/self.mul
        for s in range(self.num_pole_pairs+self.num_zero_pairs):
            results[s*2+2+0]=results[s*2+2+0]*self.mul
        return results
    def PrintResults(self):
        results=[self.m_a[r][0].real for r in range(self.m_a.shape[0])]
        from SignalIntegrity.Lib.ToSI import ToSI
        print(f"Gain: {results[0]} - {ToSI(20.*np.log10(results[0]),'dB',round=4)}")
        print(f"Delay: {ToSI(results[1]/self.mul,'s',round=4)}")
        num_zero_pairs=self.num_zero_pairs
        print(f"Number of zero pairs: {num_zero_pairs}")
        for s in range(num_zero_pairs):
            print(f"zero pair: {s+1}")
            print(f"  fz: {ToSI(results[s*2+2+0]*self.mul/(2.*np.pi),'Hz',round=4)}")
            print(f"  Qz: {ToSI(results[s*2+2+1],'',round=4)}")
        num_pole_pairs=self.num_pole_pairs
        print(f"Number of pole pairs: {num_pole_pairs}")
        for s in range(num_pole_pairs):
            print(f"pole pair: {s+1}")
            print(f"  fp: {ToSI(results[(s+num_zero_pairs)*2+2+0]*self.mul/(2.*np.pi),'Hz',round=4)}")
            print(f"  Qp: {ToSI(results[(s+num_zero_pairs)*2+2+1],'',round=4)}")
        return self
    def WriteResultsToFile(self,filename):
        results=[self.m_a[r][0].real for r in range(self.m_a.shape[0])]
        for s in range(self.num_pole_pairs+self.num_zero_pairs):
            results[s*2+2]=results[s*2+2]*self.mul
        results=[self.num_zero_pairs,self.num_pole_pairs]+[self.m_a[r][0].real for r in range(self.m_a.shape[0])]
        with open(filename,'wt') as f:
            for result in results:
                f.write(str(result)+'\n')
        return self
    @staticmethod
    def ReadResultsFile(filename):
        with open(filename,'rt') as f:
            result=f.readlines()
        return [int(result[0]),int(result[1])]+[float(res) for res in result[2:]]
    def WriteGoalToFile(self,filename):
        with open(filename,'wt') as f:
            for n in range(len(self.f)):
                f.write(str(self.f[n])+'\n')
                f.write(str(self.m_y[n][0].real)+'\n')
                f.write(str(self.m_y[n][0].imag)+'\n')
if __name__ == '__main__': # pragma: no cover
    #o=BiquadSection(0.147,0.989,0.119,0.602,0.532)
    #o=ZeroPair(0.147,0.989,0.119)
    o=PolePair(0.147,0.602,0.532)
    pass