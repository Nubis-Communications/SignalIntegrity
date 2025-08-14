"""
PoleZeroGuess.py
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

class PoleZeroGuess(object):
    """generates guess for pole/zero fits"""
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
    @staticmethod
    def Guess4(fs,fe,num_zero_pairs,num_pole_pairs):
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
        log_fe=math.log2(fs)
        log_fs=math.log2(fe)
        twopi=2*math.pi
        num_pole_zero_pairs = num_zero_pairs+num_pole_pairs

        frequency_location = [2**((log_fe-log_fs)/(num_pole_zero_pairs-1)*npz + log_fs)
                                for npz in range(num_pole_zero_pairs)]

        # for each frequency location, determine whether it is a zero or a pole
        is_a_pole = [True for _ in frequency_location]
        if num_zero_pairs > 0:
            skip=num_pole_pairs/num_zero_pairs
            start=math.floor(num_pole_pairs/num_zero_pairs/2)
            start=0
            for zp in range(num_zero_pairs):
                is_a_pole[int(zp*(skip+1))+start]=False

        # if not is_a_pole[0]:
        #     is_a_pole=[is_a_pole[-1]]+is_a_pole[1:]

        # generate the pole frequency and Q for each frequency location
        pz = [-real_pole_frequency*twopi for real_pole_frequency in frequency_location]

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
        Td = 0.0
        result = [G,Td]+zero_list+pole_list
        return result

    @staticmethod
    def Guess5(fs,fe,num_zero_pairs,num_pole_pairs):
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
        log_fe=math.log2(fe)
        log_fs=math.log2(fs)
        twopi=2*math.pi

        num_pole_zeros = num_pole_zero_pairs*2

        frequency_location = [2**((log_fe-log_fs)/(num_pole_zeros-1)*npz + log_fs)
                                for npz in range(num_pole_zeros)]

        # generate the pole frequency and Q for each frequency location
        pz = [-real_pole_frequency*twopi for real_pole_frequency in frequency_location]

        pole_first=True

        # gather these into poles and zeros
        zero_frequency_list=[]
        pole_frequency_list=[]

        for pzp in range(len(pz)):
            if len(zero_frequency_list) == num_zero_pairs*2:
                is_a_pole = True
            else:
                is_a_pole = ((pzp + (3 if pole_first else 1))//2)%2 == 1
            if is_a_pole:
                pole_frequency_list.append(pz[pzp])
            else:
                zero_frequency_list.append(pz[pzp])

        zero_pole_frequency_list = zero_frequency_list + pole_frequency_list

        zero_pole_quadratic_list = []

        for pzp in range(num_pole_zero_pairs):
            w0=abs(np.sqrt(zero_pole_frequency_list[pzp*2]*zero_pole_frequency_list[pzp*2+1]))
            Q=abs(w0/(zero_pole_frequency_list[pzp*2]+zero_pole_frequency_list[pzp*2+1]))
            zero_pole_quadratic_list.extend([w0,Q])

        # stack the zero information on top of the pole information
        G = 1
        Td = 0.0
        result = [G,Td]+zero_pole_quadratic_list
        return result
    @staticmethod
    def Guess6(fs,fe,num_zero_pairs,num_pole_pairs):
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
        log_fe=math.log2(fe)
        log_fs=math.log2(fs)
        twopi=2*math.pi

        num_pole_zeros = num_pole_zero_pairs*2

        frequency_location = [2**((log_fe-log_fs)/(num_pole_zeros-1)*npz + log_fs)
                                for npz in range(num_pole_zeros)]

        # generate the pole frequency and Q for each frequency location
        pz = [-real_pole_frequency*twopi for real_pole_frequency in frequency_location]

        pole_first=True

        # gather these into poles and zeros
        zero_frequency_list=[]
        pole_frequency_list=[]

        for pzp in range(len(pz)):
            if len(zero_frequency_list) == num_zero_pairs*2:
                is_a_pole = True
            else:
                is_a_pole = ((pzp + (1 if pole_first else 0)))%2 == 1
            if is_a_pole:
                pole_frequency_list.append(pz[pzp])
            else:
                zero_frequency_list.append(pz[pzp])

        zero_pole_frequency_list = zero_frequency_list + pole_frequency_list

        zero_pole_quadratic_list = []

        for pzp in range(num_pole_zero_pairs):
            w0=abs(np.sqrt(zero_pole_frequency_list[pzp*2]*zero_pole_frequency_list[pzp*2+1]))
            Q=abs(w0/(zero_pole_frequency_list[pzp*2]+zero_pole_frequency_list[pzp*2+1]))
            zero_pole_quadratic_list.extend([w0,Q])

        # stack the zero information on top of the pole information
        G = 1
        Td = 0.0
        result = [G,Td]+zero_pole_quadratic_list
        return result
    @staticmethod
    def Guess7(fs,fe,num_zero_pairs,num_pole_pairs):
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
        log_fe=math.log2(fe*2)
        log_fs=math.log2(fs*5)
        twopi=2*math.pi

        num_pole_zeros = num_pole_zero_pairs*2
        num_poles=num_pole_pairs*2
        frequency_location = [2**((log_fe-log_fs)/(num_poles-1)*npz + log_fs)
                                for npz in range(num_poles)]

        # generate the pole frequency and Q for each frequency location
        pz = [-real_pole_frequency*twopi for real_pole_frequency in frequency_location]

        #pole_first=True

        # gather these into poles and zeros
        zero_frequency_list=[]
        pole_frequency_list=[]

        for pzp in range(len(pz)):
            if len(zero_frequency_list) == num_zero_pairs*2:
                is_a_pole = True
            else:
                is_a_pole = False
            if is_a_pole:
                pole_frequency_list.append(pz[pzp]*3)
            else:
                zero_frequency_list.append(-pz[pzp])
                pole_frequency_list.append(pz[pzp])

        zero_pole_frequency_list = zero_frequency_list + pole_frequency_list

        zero_pole_quadratic_list = []

        for pzp in range(num_pole_zero_pairs):
            w0=abs(np.sqrt(zero_pole_frequency_list[pzp*2]*zero_pole_frequency_list[pzp*2+1]))
            Q=-w0/(zero_pole_frequency_list[pzp*2]+zero_pole_frequency_list[pzp*2+1])
            zero_pole_quadratic_list.extend([w0,Q])

        # stack the zero information on top of the pole information
        G = 1
        Td = 0.0
        result = [G,Td]+zero_pole_quadratic_list
        return result