"""
TestPID.py
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
import unittest
import SignalIntegrity as si
import math,cmath

class TestPIDTest(unittest.TestCase):

    @staticmethod
    def Frequencies(fs,fe,N):
        import math
        log10fs=math.log10(fs)
        log10fe=math.log10(fe)
        f=[10**((log10fe-log10fs)/N*n+log10fs) for n in range(N+1)]
        return f

    @staticmethod
    def Responses(P,I,D):
        app = si.App.SignalIntegrityAppHeadless()
        path='C:\\Users\\pete_\\Documents\\SignalIntegrity\\SignalIntegrity\\App\\Examples\\PID\\'
        app.OpenProjectFile(path+'Plant.si')
        pidNetList=app.NetListText()
        plantsnsp=si.p.SystemSParametersNumericParser(f).AddLines(pidNetList)
        plantsp=plantsnsp.SParameters()
        app = si.App.SignalIntegrityAppHeadless()
        app.OpenProjectFile(path+'PID.si')
        app.Device('GP')['gain']['Value']=P
        app.Device('GI')['gain']['Value']=I
        app.Device('GD')['gain']['Value']=D
        pidNetList=app.NetListText()
        pidsnsp=si.p.SystemSParametersNumericParser(f).AddLines(pidNetList)
        pidsp=pidsnsp.SParameters()

        knownSParameters={'6 file PID.si':pidsp,'2 file Plant.si':plantsp}
        app.OpenProjectFile('PIDSimulationOpenLoop.si')
        pidSimulationOpenLoopNetlist=app.NetListText()
        pidSOLsnp=si.p.SimulatorNumericParser(f).AddLines(pidSimulationOpenLoopNetlist)
        pidSOLsnp=pidSOLsnp.AddKnownDevices(knownSParameters)
        OpenLoopFrequencyResponses = pidOpenLoop=pidSOLsnp.TransferMatrices().FrequencyResponses()
        OpenLoopOutputList =  ['Vin','VPID','P','I','D']
        app.OpenProjectFile('PIDSimulation.si')
        pidSimulationNetlist=app.NetListText()
        pidSsnp=si.p.SimulatorNumericParser(f).AddLines(pidSimulationNetlist)
        pidSsnp=pidSsnp.AddKnownDevices(knownSParameters)
        ClosedLoopFrequencyResponses = pidSsnp.TransferMatrices().FrequencyResponses()
        ClosedLoopOutputList = ['Vin','VO','VPID','VU','P','I','D']
        ClosedLoopResults={'C':ClosedLoopFrequencyResponses[ClosedLoopOutputList.index('VO')][0],
                          'U':ClosedLoopFrequencyResponses[ClosedLoopOutputList.index('VU')][0],
                          'PID':ClosedLoopFrequencyResponses[ClosedLoopOutputList.index('VPID')][0],
                          'P':ClosedLoopFrequencyResponses[ClosedLoopOutputList.index('P')][0],
                          'I':ClosedLoopFrequencyResponses[ClosedLoopOutputList.index('I')][0],
                          'D':ClosedLoopFrequencyResponses[ClosedLoopOutputList.index('D')][0]
                          }
        OpenLoopResults={'PID':OpenLoopFrequencyResponses[OpenLoopOutputList.index('VPID')][0],
                          'P':OpenLoopFrequencyResponses[OpenLoopOutputList.index('P')][0],
                          'I':OpenLoopFrequencyResponses[OpenLoopOutputList.index('I')][0],
                          'D':OpenLoopFrequencyResponses[OpenLoopOutputList.index('D')][0]
                          }
        return {'ClosedLoop':ClosedLoopResults,'OpenLoop':OpenLoopResults,'Frequency':f}


    def testPID(self):
        results=self.Responses(P,I,D)
        B=results['OpenLoop']['PID']
        A=results['ClosedLoop']['U']

        import numpy as np
        import matplotlib.pyplot as plt

        results=self.Responses(P,I,D)
        fig = plt.figure()
        ax1 = fig.add_subplot(2,3, 1)
        PdB, = ax1.semilogx(f,results['OpenLoop']['P'].Response('dB'),color='blue',linestyle='--')
        IdB, = ax1.semilogx(f,results['OpenLoop']['I'].Response('dB'),color='blue',linestyle='--')
        DdB, = ax1.semilogx(f,results['OpenLoop']['D'].Response('dB'),color='blue',linestyle='--')
        PIDdB, = ax1.semilogx(f,results['OpenLoop']['PID'].Response('dB'),color='blue')
        ax1.grid()
        plt.ylabel('magnitude (dB)')
        ax2 = fig.add_subplot(2,3,1,sharex=ax1,frameon=False)
        Pdeg, = ax2.semilogx(f,results['OpenLoop']['P'].Response('deg'),color='red',linestyle='--')
        Ideg, = ax2.semilogx(f,results['OpenLoop']['I'].Response('deg'),color='red',linestyle='--')
        Ddeg, = ax2.semilogx(f,results['OpenLoop']['D'].Response('deg'),color='red',linestyle='--')
        PIDdeg, = ax2.semilogx(f,results['OpenLoop']['PID'].Response('deg'),color='red')
        ax2.yaxis.tick_right()
        ax2.yaxis.set_label_position('right')
        plt.ylabel('phase (deg)')
        plt.title('PID open-loop response (B)')
        ax2.grid()

        ABdBy=[20.*math.log10(abs(a*b)) for a,b in zip(A.Values(),B.Values())]
        ABdegy=[180./math.pi*cmath.phase(a*b) for a,b in zip(A.Values(),B.Values())]

        ax3 = fig.add_subplot(2,3,2)
        ABdB, = ax3.semilogx(f,ABdBy,color='blue')
        ax3.grid()
        plt.ylabel('magnitude (dB)')
        ax4 = fig.add_subplot(2,3,2,sharex=ax3,frameon=False)
        ABdeg, = ax4.semilogx(f,ABdegy,color='red')
        ax4.yaxis.tick_right()
        ax4.yaxis.set_label_position('right')
        plt.ylabel('phase (deg)')
        plt.title('A*B')
        ax4.grid()

        ABPlus1dBy=[20.*math.log10(abs(a*b+1)) for a,b in zip(A.Values(),B.Values())]
        ABPlus1degy=[180./math.pi*cmath.phase(a*b+1) for a,b in zip(A.Values(),B.Values())]

        ax5 = fig.add_subplot(2,3,3)
        ABPlus1dB, = ax5.semilogx(f,ABPlus1dBy,color='blue')
        ax5.grid()
        plt.ylabel('magnitude (dB)')
        ax6 = fig.add_subplot(2,3,3,sharex=ax5,frameon=False)
        ABPlus1deg, = ax6.semilogx(f,ABPlus1degy,color='red')
        ax6.yaxis.tick_right()
        ax6.yaxis.set_label_position('right')
        plt.ylabel('phase (deg)')
        plt.title('A*B+1')
        ax6.grid()

        InvABPlus1dBy=[20.*math.log10(abs(1./(a*b+1))) for a,b in zip(A.Values(),B.Values())]
        InvABPlus1degy=[180./math.pi*cmath.phase(1/(a*b+1)) for a,b in zip(A.Values(),B.Values())]

        ax7 = fig.add_subplot(2,3,4)
        InvABPlus1dB, = ax7.semilogx(f,InvABPlus1dBy,color='blue')
        ax7.grid()
        plt.ylabel('magnitude (dB)')
        ax8 = fig.add_subplot(2,3,4,sharex=ax7,frameon=False)
        InvABPlus1deg, = ax8.semilogx(f,InvABPlus1degy,color='red')
        ax8.yaxis.tick_right()
        ax8.yaxis.set_label_position('right')
        plt.ylabel('phase (deg)')
        plt.title('1/(A*B+1)')
        ax8.grid()

        BInvABPlus1dBy=[20.*math.log10(abs(b/(a*b+1))) for a,b in zip(A.Values(),B.Values())]
        BInvABPlus1degy=[180./math.pi*cmath.phase(b/(a*b+1)) for a,b in zip(A.Values(),B.Values())]

        ax9 = fig.add_subplot(2,3,5)
        BInvABPlus1dB, = ax9.semilogx(f,BInvABPlus1dBy,color='blue')
        ax9.grid()
        plt.ylabel('magnitude (dB)')
        ax10 = fig.add_subplot(2,3,5,sharex=ax9,frameon=False)
        BInvABPlus1deg, = ax10.semilogx(f,BInvABPlus1degy,color='red')
        ax10.yaxis.tick_right()
        ax10.yaxis.set_label_position('right')
        plt.ylabel('phase (deg)')
        plt.title('B/(A*B+1)')
        ax10.grid()

        ax11 = fig.add_subplot(2,3,6)
        ABInvABPlus1dB, = ax11.semilogx(f,results['ClosedLoop']['C'].Response('dB'),color='blue')
        ax11.grid()
        plt.ylabel('magnitude (dB)')
        ax12 = fig.add_subplot(2,3,6,sharex=ax11,frameon=False)
        ABInvABPlus1deg, = ax12.semilogx(f,results['ClosedLoop']['C'].Response('deg'),color='red')
        ax12.yaxis.tick_right()
        ax12.yaxis.set_label_position('right')
        plt.ylabel('phase (deg)')
        plt.title('A*B/(A*B+1) = closed loop response')
        ax12.grid()

        fig.show()
        pass

P=60.
I=500.
D=15.
fs=10e3
fe=100e6
N=40
f=TestPIDTest.Frequencies(fs,fe,N)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()