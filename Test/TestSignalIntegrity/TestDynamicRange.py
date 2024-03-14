"""
TestExceptions.py
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

from math import log10,sqrt

import SignalIntegrity.Lib as si

class TestDynamicRangeTest(unittest.TestCase):

    @staticmethod
    def SNR(fbw,Fse,N,A,Fsa,Tw,Td,frac,Pf,Ff,step,f):
        return 10.*log10(fbw/(Fse/2.))-N+\
        (20.*log10(A/(f+1))-3. if step else 20.*log10(A)+13.)+\
        10*log10(Fsa*Tw/(Td*Td))-\
        10.*log10(frac)+\
        Pf+2*Ff
    def testDynamicRange(self):
        Fse=204.8e9
        fbw=Fse/2
        N=-44.3
        A=2e-12
        Fsa=100e6
        Tw=1
        Tse=1./Fse
        Td=20480*Tse
        frac=0.1
        Fe=40e9
        
        F=2
        C=1.6
        C=0
        NF=100
        fr=[(n+1.)/NF*Fe for n in range(NF)]
        CM=[-0.133*sqrt(f/1e9)-.00404*f/1e9 for f in fr]
        P=[f/Fe*-1 for f in fr]
        snrWpPreview=[self.SNR(fbw,Fse,N,A,Fsa,Tw,Td,frac,P[n],(F+C)*CM[n],False,fr[n]) for n in range(len(fr))]
        snrWpNormal=[self.SNR(fbw,Fse,N,A,Fsa,Tw*10,Td,frac,P[n],(F+C)*CM[n],False,fr[n]) for n in range(len(fr))]
        snrWpExtra=[self.SNR(fbw,Fse,N,A,Fsa,Tw*100,Td,frac,P[n],(F+C)*CM[n],False,fr[n]) for n in range(len(fr))]
        
        A=200e-3
        Fsa=10e6
        N=-46
        F=4.5
        C=1.6
        C=0
        P=[f/Fe*12. for f in fr]
        snrSpPreview=[self.SNR(fbw,Fse,N,A,Fsa,Tw,Td,frac,P[n],(F+C)*CM[n],True,fr[n]) for n in range(len(fr))]
        snrSpNormal=[self.SNR(fbw,Fse,N,A,Fsa,Tw*10,Td,frac,P[n],(F+C)*CM[n],True,fr[n]) for n in range(len(fr))]
        snrSpExtra=[self.SNR(fbw,Fse,N,A,Fsa,Tw*100,Td,frac,P[n],(F+C)*CM[n],True,fr[n]) for n in range(len(fr))]

        frGHz=[f/1e9 for f in fr]
        import matplotlib.pyplot as plt
        import matplotlib
#         plt.plot(frGHz,snrWpPreview)
#         plt.plot(frGHz,snrWpNormal)
#         plt.plot(frGHz,snrWpExtra)
#         plt.plot(frGHz,snrSpPreview)
#         plt.plot(frGHz,snrSpNormal)
#         plt.plot(frGHz,snrSpExtra)
#         plt.show()

        plt.semilogx(frGHz,snrWpPreview,linestyle='--',color='black',label='preview mode (0:04)')
        plt.semilogx(frGHz,snrWpNormal,linewidth=1,color='black',label='normal mode (0:40)')
        plt.semilogx(frGHz,snrWpExtra,linewidth=2,color='black',label='extra mode (6:40)')
        plt.xlabel('frequency (GHz)')
        plt.ylabel('dynamic range (dB)')
        plt.legend(loc='upper right')
        plt.gca().set_xlim(left=1,right=40)
        plt.gca().set_ylim(bottom=30,top=90)
        ax1=plt.gca()
        ax1.set_xticks([1, 10, 20, 30, 40])
        ax1.get_xaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
        plt.grid(True)
        si.test.PlotTikZ('WavePulserDynamicRangeLog.tex', plt)
        #plt.show()
        
        plt.semilogx(frGHz,snrSpPreview,linestyle='--',color='black',label='preview mode (0:12)')
        plt.semilogx(frGHz,snrSpNormal,linewidth=1,color='black',label='normal mode (2:00)')
        plt.semilogx(frGHz,snrSpExtra,linewidth=2,color='black',label='extra mode (20:00)')
        plt.xlabel('frequency (GHz)')
        plt.ylabel('dynamic range (dB)')
        plt.legend(loc='upper right')
        plt.gca().set_xlim(left=1,right=40)
        plt.gca().set_ylim(bottom=30,top=90)
        ax1=plt.gca()
        ax1.set_xticks([1, 10, 20, 30, 40])
        ax1.get_xaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
        plt.grid(True)
        si.test.PlotTikZ('SPARQDynamicRangeLog.tex', plt)
        #plt.show()

        plt.plot(frGHz,snrWpPreview,linestyle='--',color='black',label='preview mode (0:04)')
        plt.plot(frGHz,snrWpNormal,linewidth=1,color='black',label='normal mode (0:40)')
        plt.plot(frGHz,snrWpExtra,linewidth=2,color='black',label='extra mode (6:40)')
        plt.xlabel('frequency (GHz)')
        plt.ylabel('dynamic range (dB)')
        plt.legend(loc='upper right')
        plt.gca().set_xlim(left=1,right=40)
        plt.gca().set_ylim(bottom=30,top=90)
        ax1=plt.gca()
        ax1.set_xticks([1, 10, 20, 30, 40])
        ax1.get_xaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
        plt.grid(True)
        si.test.PlotTikZ('WavePulserDynamicRangeLinear.tex', plt)
        #plt.show()
        
        plt.plot(frGHz,snrSpPreview,linestyle='--',color='black',label='preview mode (0:12)')
        plt.plot(frGHz,snrSpNormal,linewidth=1,color='black',label='normal mode (2:00)')
        plt.plot(frGHz,snrSpExtra,linewidth=2,color='black',label='extra mode (20:00)')
        plt.xlabel('frequency (GHz)')
        plt.ylabel('dynamic range (dB)')
        plt.legend(loc='upper right')
        plt.gca().set_xlim(left=1,right=40)
        plt.gca().set_ylim(bottom=30,top=90)
        ax1=plt.gca()
        ax1.set_xticks([1, 10, 20, 30, 40])
        ax1.get_xaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
        plt.grid(True)
        si.test.PlotTikZ('SPARQDynamicRangeLinear.tex', plt)
        #plt.show()



if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()