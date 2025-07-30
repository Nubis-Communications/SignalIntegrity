"""
TestPoleZeroFitter.py
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
import unittest

import SignalIntegrity.Lib as si
from SignalIntegrity.Utilities.PoleZero.PoleZeroFitter import PoleZeroLevMar

class TestPoleZeroFitterTest(unittest.TestCase):
    def __init__(self, methodName='runTest'):
        unittest.TestCase.__init__(self,methodName)
    def PrintProgress(self,iteration):
        print(self.m_fitter.ccm._IterationsTaken,self.m_fitter.m_mse)
    def PlotResult(self,iteration):
        # return
        self.PrintProgress(iteration)
        import matplotlib.pyplot as plt
        import numpy as np
        if not self.plotInitialized:
            self.skip_amount = 1
            plt.ion()
            self.fig,self.axs=plt.subplots(2,2)
            ax=self.fig.add_subplot(2,2,4,projection='polar')
            ax.set_rscale('log')
            self.axs[1,1]=ax
            #self.axs[0,0].ion()
            #self.axs[0,0].show()
            #self.fig.canvas.draw()
            #plt.gcf()
            # plt.title('fit compare')
            # plt.xlabel('frequency (GHz)')
            # plt.ylabel('magnitude (dB)')
            # plt.legend()
            # plt.grid(True,'both')
            self.plotInitialized=True
            self.skipper=0
        self.skipper=self.skipper+1
        if self.skipper<self.skip_amount:
            return
        #plt.clf()
        self.skipper=0
        self.skip_amount=min(500.0,self.skip_amount*1.05)

        self.axs[0,0].cla()
        self.axs[0,0].set_title('fit compare')
        self.axs[0,0].set_xlabel('frequency (GHz)')
        self.axs[0,0].set_ylabel('magnitude (dB)')
        self.axs[0,0].plot([f/1e9 for f in self.m_fitter.f],
                     [20.*np.log10(np.abs(v[0])) for v in self.m_fitter.m_y],label='goal')
        self.axs[0,0].plot([f/1e9 for f in self.m_fitter.f],
                     [20.*np.log10(np.abs(v[0])) for v in self.m_fitter.m_Fa],label='fit')
        self.axs[0,0].legend()
        self.axs[0,0].grid(True,'both')

        self.axs[0,1].cla()
        self.axs[0,1].set_title('fit compare')
        self.axs[0,1].set_xlabel('frequency (GHz)')
        self.axs[0,1].set_ylabel('magnitude (dB)')
        self.axs[0,1].plot([v[0].real for v in self.m_fitter.m_y],
                 [v[0].imag for v in self.m_fitter.m_y],label='goal')
        self.axs[0,1].plot([v[0].real for v in self.m_fitter.m_Fa],
                 [v[0].imag for v in self.m_fitter.m_Fa],label='fit')
        self.axs[0,1].legend()
        self.axs[0,1].grid(True,'both')

        self.axs[1,0].cla()
        self.axs[1,0].set_title('lamda and mse')
        self.axs[1,0].semilogy(self.m_fitter.ccm._FilteredLogDeltaLambdaTracker,label='log delta lambda')
        self.axs[1,0].semilogy(self.m_fitter.ccm._FilteredLogDeltaMseTracker,label='log delta mse')
        self.axs[1,0].set_xlabel('iteration #')
        self.axs[1,0].set_ylabel('log delta')
        self.axs[1,0].grid(True,'both')
        self.axs[1,0].legend()

        # self.axs[1,0].cla()
        # self.axs[1,0].set_title('pole/zero locations')
        results=self.m_fitter.Results()
        results=[result[0].real for result in results]
        num_zero_pairs=self.m_fitter.num_zero_pairs
        num_pole_pairs=self.m_fitter.num_pole_pairs
        zero_mag=[]
        zero_angle=[]
        pole_mag=[]
        pole_angle=[]
        zero_real=[]
        zero_imag=[]
        pole_real=[]
        pole_imag=[]
        for s in range(num_zero_pairs):
            wz=results[s*2+2+0]
            Qz=results[s*4+2+1]
            zeros = np.roots(np.array([1, wz/Qz, wz*wz]))/(2.*np.pi*1e9)
            zero_mag.extend([np.abs(z) for z in zeros])
            zero_angle.extend([np.angle(z) for z in zeros])
            zero_real.extend([z.real for z in zeros])
            zero_imag.extend([z.imag for z in zeros])
        for s in range(num_pole_pairs):
            wp=results[(s+num_zero_pairs)*2+2+0]
            Qp=results[(s+num_zero_pairs)*2+2+1]
            poles = np.roots(np.array([1, wp/Qp, wp*wp]))/(2.*np.pi*1e9)
            pole_mag.extend([np.abs(p) for p in poles])
            pole_angle.extend([np.angle(p) for p in poles])
            pole_real.extend([p.real for p in poles])
            pole_imag.extend([p.imag for p in poles])
        # self.axs[1,0].plot(zero_real,zero_imag,marker='o', linestyle='',markersize=10, markerfacecolor='none')
        # self.axs[1,0].plot(pole_real,pole_imag,marker='X', linestyle='',markersize=10)
        # self.axs[1,0].set_xlim(-30,0)
        # self.axs[1,0].set_ylim(-100,100)
        # self.axs[1,0].grid(True,'both')

        self.axs[1,1].cla()
        self.axs[1,1].set_rscale('log')
        self.axs[1,1].set_title('pole/zero locations')
        self.axs[1,1].plot(zero_angle,zero_mag,marker='o', linestyle='',markersize=10, markerfacecolor='none')
        self.axs[1,1].plot(pole_angle,pole_mag,marker='X', linestyle='',markersize=10)
        self.axs[1,1].grid(True,'both')
#        plt.grid(True,'both')

        self.fig.canvas.draw()
        plt.pause(0.001)
    def testFit(self):
        return
        filename='sw1varB_sparam_mc12_bias4_vga4_corner3_105C_3p1V_MM.s4p'
        sp = si.sp.SParameterFile(filename)
        s21=sp.FrequencyResponse(2,1).Resample(si.fd.EvenlySpacedFrequencyList(80e9,80))
        self.m_fitter=PoleZeroLevMar(s21,2,4,self.PlotResult)
        self.plotInitialized=False
        self.m_fitter.Solve()
        results=self.m_fitter.Results()
        self.m_fitter.PrintResults().WriteResultsToFile('test_result.txt').WriteGoalToFile('test_goal.txt')
    def testFit2(self):
        return
        filename='TF_main_lowQ_pex_typical_MM.s4p'
        sp = si.sp.SParameterFile(filename)
        s21=sp.FrequencyResponse(2,1).Resample(si.fd.EvenlySpacedFrequencyList(85e9,20))
        self.m_fitter=PoleZeroLevMar(s21,1,3,self.PlotResult)
        self.plotInitialized=False
        self.m_fitter.Solve()
        results=self.m_fitter.Results()
        self.m_fitter.PrintResults().WriteResultsToFile('test_result.txt').WriteGoalToFile('test_goal.txt')
    def testFit3(self):
        #return
        filename='TF_main_MM.s4p'
        sp = si.sp.SParameterFile(filename)
        s21=sp.FrequencyResponse(2,1).Resample(si.fd.EvenlySpacedFrequencyList(80e9,20))
        self.m_fitter=PoleZeroLevMar(s21,2,4,self.PlotResult)
        self.plotInitialized=False
        self.m_fitter.Solve()
        results=self.m_fitter.Results()
        self.m_fitter.PrintResults().WriteResultsToFile('test_result.txt').WriteGoalToFile('test_goal.txt')