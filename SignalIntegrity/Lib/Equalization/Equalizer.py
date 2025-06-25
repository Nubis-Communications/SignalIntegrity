"""
Equalizer.py
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
import numpy as np

class Levels(list):
    def __init__(self,levels_list=[]):
        self.set_levels(levels_list)
    def set_levels(self,levels_list=[]):
        list.__init__(self,levels_list)
        return self

class LevelsRange(Levels):
    def __init__(self,min_level,max_level,num_levels):
        levels_list = [min_level + level_index * (max_level - min_level) / (num_levels - 1) for level_index in range(num_levels)]
        Levels.__init__(self,levels_list)

class Equalizer(object):
    def __init__(self,
                 num_ffe_taps=0,
                 num_dfe_taps=0,
                 num_precursor_taps=0,
                 levels_list=[]):
        self.set_taps(num_ffe_taps,
                      num_dfe_taps,
                      num_precursor_taps)
        self.set_levels(levels_list)

    def set_taps(self,
                 num_ffe_taps=0,
                 num_dfe_taps=0,
                 num_precursor_taps=0):
        self.num_ffe_taps = num_ffe_taps
        self.num_dfe_taps = num_dfe_taps
        self.num_precursor_taps = num_precursor_taps
        self.ffe_tap_values_list = []
        self.dfe_tap_values_list = []
        return self

    def initialize_tap_values_to_default(self):
        self.ffe_tap_values_list = [0 if i != self.num_precursor_taps else 1.0
                                    for i in range(self.num_ffe_taps)]
        self.dfe_tap_values_list = [0 for _ in range(self.num_dfe_taps)]
        return self

    def set_levels(self,
                   levels_list=[]):
        self.levels_list=levels_list
        return self

    @staticmethod
    def decode_value(value,levels_list):
        abs_diff_list=[abs(value-level) for level in levels_list]
        return levels_list[abs_diff_list.index(min(abs_diff_list))]

    @staticmethod
    def decode_values(value_list,levels_list):
        return [Equalizer.decode_value(v,levels_list) for v in value_list]

    def equalize_values(self,
                        values_list,
                        lamda=1,
                        num_iterations=20):
        LFFE=len(self.ffe_tap_values_list)
        LDFE=len(self.dfe_tap_values_list)
        # def index_ffe(pp,mffe): return LFFE - mffe - 1 + pp
        # def index_dfe(pp,mdfe): return LDFE - mdfe - 1 + pp
        def augment(A,B): return np.concatenate((A,B),axis=1)
        def stack(A,B): return np.concatenate((A,B),axis=0)
        def submatrix(A,ri,rf,ci,cf): return A[np.ix_(np.arange(ri,rf+1),np.arange(ci,cf+1))]
        def rows(A): return A.shape[0]
        def cols(A): return A.shape[1]

        xs=values_list
        xd=self.decode_values(xs,self.levels_list)
        S = np.array([[xs[LFFE - mffe - 1 + pp] for mffe in range(LFFE)]
            for pp in range(len(xs)-LFFE+1)])
        xe1 = S.dot(np.array(self.ffe_tap_values_list))
        xd1 = self.decode_values(xe1,self.levels_list)
        D = np.array([[xd1[LDFE - mdfe - 1 + pp] for mdfe in range(LDFE)]
             for pp in range(len(xd1)-LDFE)])
        SubS = submatrix(S, LDFE, rows(S)-1, 0, cols(S)-1)
        J = augment(SubS,D) if LDFE > 0 else SubS
        W = np.identity(rows(J))
        a = stack(np.array(self.ffe_tap_values_list),np.array(self.dfe_tap_values_list)) if LDFE > 0 else np.array(self.ffe_tap_values_list)
        xe = J.dot(a)
        xd = self.decode_values(xe,self.levels_list)
        r = xe - xd
        mse = r.transpose().dot(W).dot(r)/len(r)
        H = J.transpose().dot(W).dot(J)
        HH = H
        mse_list=[]
        lamda_list=[]
        for iteration in range(num_iterations):
            for rc in range(H.shape[0]):
                HH[rc][rc] = H[rc][rc] + lamda
            delta_a = np.linalg.inv(HH).dot(J.transpose()).dot(W).dot(r)
            a_new = a - delta_a
            xe_new = J.dot(a_new)
            xd_new = self.decode_values(xe,self.levels_list)
            r_new = xe_new - xd_new
            mse_new = r_new.transpose().dot(W).dot(r_new)/len(r_new)
            if mse_new < mse: # succeeded
                xe1_new = S.dot(a_new[np.ix_(np.arange(0,LFFE))])
                xd1_new = self.decode_values(xe1_new,self.levels_list)
                D_new = np.array([[xd1_new[LDFE - mdfe - 1 + pp] for mdfe in range(LDFE)]
                                  for pp in range(len(xd1_new)-LDFE)])
                J_new = augment(SubS,D_new) if LDFE > 0 else S

                D = D_new
                a = a_new
                xe = xe_new
                xd = xd_new
                r = r_new
                mse = mse_new

                J = J_new
                H = J.transpose().dot(W).dot(J)
                HH = H

                lamda = lamda / 10.
            else:
                HH = H
                lamda = lamda * 10.
            mse_list.append(mse)
            lamda_list.append(lamda)
        print(str(a.tolist()).replace(' ',''))
        import matplotlib.pyplot as plt
        plt.cla()
        plt.plot(mse_list)
        plt.grid()
        plt.show()

