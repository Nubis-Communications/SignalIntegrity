"""
TestDeembedding.py
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

import SignalIntegrity.Lib as si
from numpy import linalg
from numpy import array
from numpy.linalg import inv
import os

class TestDeembedding(unittest.TestCase,si.test.ResponseTesterHelper):
    def __init__(self, methodName='runTest'):
        unittest.TestCase.__init__(self,methodName)
    def testOnePortFixtureDeembedding(self):
        Su=si.dev.TerminationZ(30)
        D=[[1.,2.],[3.,4.]]
        # first build something that we know
        SD=si.sd.Deembedder()
        SD.AddDevice('D',2,D)
        SD.AddUnknown('?',1)
        SD.AssignSParameters('?',Su)
        SD.ConnectDevicePort('D',2,'?',1)
        SD.AddPort('D',1,1,True)
        Sk=si.sd.SystemSParametersNumeric(SD).SParameters()
        SuCalc=si.sd.DeembedderNumeric(SD).CalculateUnknown(Sk)
        difference = linalg.norm(array(Su)-array(SuCalc))
        self.assertTrue(difference<1e-10,'One Port Fixture Deembedding incorrect')
        #Now test according to the simple one port equation in the book
        GammaDut=(Sk[1-1][1-1]-D[1-1][1-1])/(Sk[1-1][1-1]*D[2-1][2-1]-linalg.det(array(D)))
        difference = linalg.norm(GammaDut-array(SuCalc))
        self.assertTrue(difference<1e-10,'One Port Fixture Deembedding equation incorrect')
    def testTwoPortThreeDevicesFixtureDeembedding(self):
        SL=[[5.,6.],[7.,8.]]
        Su=[[1.,2.],[3.,4.]]
        SR=[[9.,10.],[11.,12.]]
        # first build something that we know
        SD=si.sd.Deembedder()
        SD.AddDevice('DL',2,SL)
        SD.AddUnknown('?',2)
        SD.AssignSParameters('?',Su)
        SD.AddDevice('DR',2,SR)
        SD.ConnectDevicePort('DL',2,'?',1)
        SD.ConnectDevicePort('?',2,'DR',2)
        SD.AddPort('DL',1,1,True)
        SD.AddPort('DR',1,2,True)
        Sk=si.sd.SystemSParametersNumeric(SD).SParameters()
        SuCalc=si.sd.DeembedderNumeric(SD).CalculateUnknown(Sk)
        difference = linalg.norm(array(Su)-array(SuCalc))
        self.assertTrue(difference<1e-10,'Two Port Three Devices Fixture Deembedding incorrect')
        #Now test according to the two port equation in the book
        Sk11=Sk[1-1][1-1]
        Sk12=Sk[1-1][2-1]
        Sk21=Sk[2-1][1-1]
        Sk22=Sk[2-1][2-1]
        SL11=SL[1-1][1-1]
        SL12=SL[1-1][2-1]
        SL21=SL[2-1][1-1]
        SL22=SL[2-1][2-1]
        SR11=SR[1-1][1-1]
        SR12=SR[1-1][2-1]
        SR21=SR[2-1][1-1]
        SR22=SR[2-1][2-1]
        B=inv(array([[SL12,0.],[0.,SR12]])).dot(array([[Sk11,Sk12],[Sk21,Sk22]])-array([[SL11,0.],[0.,SR11]]))
        A=array([[SL21,0.],[0.,SR21]])+array([[SL22,0.],[0.,SR22]]).dot(B)
        SuCalc1=B.dot(inv(A))
        difference = linalg.norm(array(Su)-array(SuCalc1))
        self.assertTrue(difference<1e-10,'Two Port Three Devices Fixture Deembedding Matrix equation incorrect')
        SuCalc2=array([[(Sk11-SL11)/SL12,Sk12/SL12],[Sk21/SR12,(Sk22-SR11)/SR12]])
        SuCalc2=SuCalc2.dot(inv([[(SL22*Sk11-linalg.det(array(SL)))/SL12,SL22*Sk12/SL12],[SR22*Sk21/SR12,(SR22*Sk22-linalg.det(array(SR)))/SR12]]))
        difference = linalg.norm(array(SuCalc1)-array(SuCalc2))
        self.assertTrue(difference<1e-10,'Two Port Three Devices Fixture Deembedding Final equation incorrect')
    def testTwoPortTwoDevicesSRUnknownFixtureDeembedding(self):
        SL=[[5.,6.],[7.,8.]]
        SR=[[1.,2.],[3.,4.]]
        # first build something that we know
        SD=si.sd.Deembedder()
        SD.AddDevice('DL',2,SL)
        SD.AddUnknown('?R',2)
        SD.AssignSParameters('?R',SR)
        SD.ConnectDevicePort('DL',2,'?R',1)
        SD.AddPort('DL',1,1,True)
        SD.AddPort('?R',2,2,True)
        Sk=si.sd.SystemSParametersNumeric(SD).SParameters()
        SuCalc=si.sd.DeembedderNumeric(SD).CalculateUnknown(Sk)
        difference = linalg.norm(array(SuCalc)-array(SR))
        self.assertTrue(difference<1e-10,'Two Port Two Devices SR unknown Fixture Deembedding incorrect')
        #Now test according to the two port equation in the book
        Sk11=Sk[1-1][1-1]
        Sk12=Sk[1-1][2-1]
        Sk21=Sk[2-1][1-1]
        Sk22=Sk[2-1][2-1]
        SL11=SL[1-1][1-1]
        SL12=SL[1-1][2-1]
        SL21=SL[2-1][1-1]
        SL22=SL[2-1][2-1]
        SRcalc=1./(SL22*Sk11-linalg.det(SL))
        SRcalc=SRcalc*array([[Sk11-SL11,SL21*Sk12],[SL12*Sk21,SL22*linalg.det(Sk)-Sk22*linalg.det(SL)]])
        difference = linalg.norm(array(SRcalc)-array(SR))
        self.assertTrue(difference<1e-10,'Two Port Two Devices SR Unknown Fixture Deembedding equation incorrect')
    def testTwoPortTwoDevicesSLUnknownFixtureDeembedding(self):
        SL=[[5.,6.],[7.,8.]]
        SR=[[1.,2.],[3.,4.]]
        # first build something that we know
        SD=si.sd.Deembedder()
        SD.AddUnknown('?L',2)
        SD.AssignSParameters('?L',SL)
        SD.AddDevice('DR',2,SR)
        SD.ConnectDevicePort('?L',2,'DR',1)
        SD.AddPort('?L',1,1,True)
        SD.AddPort('DR',2,2,True)
        Sk=si.sd.SystemSParametersNumeric(SD).SParameters()
        SuCalc=si.sd.DeembedderNumeric(SD).CalculateUnknown(Sk)
        difference = linalg.norm(array(SuCalc)-array(SL))
        self.assertTrue(difference<1e-10,'Two Port Two Devices SL unknown Fixture Deembedding incorrect')
        #Now test according to the two port equation in the book
        Sk11=Sk[1-1][1-1]
        Sk12=Sk[1-1][2-1]
        Sk21=Sk[2-1][1-1]
        Sk22=Sk[2-1][2-1]
        SR11=SR[1-1][1-1]
        SR12=SR[1-1][2-1]
        SR21=SR[2-1][1-1]
        SR22=SR[2-1][2-1]
        SLcalc=1./(Sk22*SR11-linalg.det(SR))
        SLcalc=SLcalc*array([[SR11*linalg.det(Sk)-Sk11*linalg.det(SR),Sk12*SR21],[Sk21*SR12,Sk22-SR22]])
        difference = linalg.norm(array(SLcalc)-array(SL))
        self.assertTrue(difference<1e-10,'Two Port Two Devices SL Unknown Fixture Deembedding equation incorrect')
    def testOnePortOverConstrainedFixtureDeembeddingNoInternal(self):
        Su=si.dev.TerminationZ(30+20.*1j)
        D=[[1.,2.,3.],[4.,5.,6.],[7.,8.,9.]]
        # first build something that we know
        SD=si.sd.Deembedder()
        SD.AddDevice('D',3,D)
        SD.AddUnknown('?',1)
        SD.AssignSParameters('?',Su)
        SD.ConnectDevicePort('D',3,'?',1)
        SD.AddPort('D',1,1,False)
        SD.AddPort('D',2,2,False)
        Sk=si.sd.SystemSParametersNumeric(SD).SParameters()
        SuCalc=si.sd.DeembedderNumeric(SD).CalculateUnknown(Sk)
        difference = linalg.norm(array(Su)-array(SuCalc))
        self.assertTrue(difference<1e-10,'One Port OverConstrained Deembedding with no internal ports (U=None) incorrect')
    def testOnePortOverConstrainedFixtureDeembedding(self):
        Su=si.dev.TerminationZ(30+20.*1j)
        D=[[1.,2.,3.],[4.,5.,6.],[7.,8.,9.]]
        # first build something that we know
        SD=si.sd.Deembedder()
        SD.AddDevice('D',3,D)
        SD.AddUnknown('?',1)
        SD.AssignSParameters('?',Su)
        SD.ConnectDevicePort('D',3,'?',1)
        SD.AddPort('D',1,1,True)
        SD.AddPort('D',2,2,True)
        Sk=si.sd.SystemSParametersNumeric(SD).SParameters()
        SuCalc=si.sd.DeembedderNumeric(SD).CalculateUnknown(Sk)
        difference = linalg.norm(array(Su)-array(SuCalc))
        self.assertTrue(difference<1e-10,'One Port OverConstrained Deembedding with internal ports incorrect')
    def testTwoOnePortsMultipleUnknownsFixtureDeembedding(self):
        Su1=si.dev.TerminationZ(30+20.*1j)
        Su2=si.dev.TerminationZ(15-5.*1j)
        D=[[1.,2.,5.,6.],[3.,4.,7.,8.],[9.,8.,7.,6.],[5.,4.,3.,2.]]
        # first build something that we know
        SD=si.sd.Deembedder()
        SD.AddDevice('D',4,D)
        SD.AddUnknown('?1',1)
        SD.AssignSParameters('?1',Su1)
        SD.AddUnknown('?2',1)
        SD.AssignSParameters('?2',Su2)
        SD.ConnectDevicePort('D',3,'?1',1)
        SD.ConnectDevicePort('D',4,'?2',1)
        SD.AddPort('D',1,1,True)
        SD.AddPort('D',2,2,True)
        Sk=si.sd.SystemSParametersNumeric(SD).SParameters()
        SuCalc=si.sd.DeembedderNumeric(SD).CalculateUnknown(Sk)
        UnknownNames=si.sd.Deembedder(SD).UnknownNames()
        difference1 = linalg.norm(array(Su1)-array(SuCalc[UnknownNames.index('?1')]))
        self.assertTrue(difference1<1e-10,'Multiple Unknowns Deembedding - first unknown incorrect')
        difference2 = linalg.norm(array(Su2)-array(SuCalc[UnknownNames.index('?2')]))
        self.assertTrue(difference2<1e-10,'Multiple Unknowns Deembedding - second unknown incorrect')
    def testTwoPortTwoDevicesSLUnknownThruDeembedding(self):
        SL=si.dev.Thru()
        SR=si.dev.Thru()
        # first build something that we know
        SD=si.sd.Deembedder()
        SD.AddUnknown('?L',2)
        SD.AssignSParameters('?L',SL)
        SD.AddDevice('DR',2,SR)
        SD.ConnectDevicePort('?L',2,'DR',1)
        SD.AddPort('?L',1,1,True)
        SD.AddPort('DR',2,2,True)
        Sk=si.sd.SystemSParametersNumeric(SD).SParameters()
        SuCalc=si.sd.DeembedderNumeric(SD).CalculateUnknown(Sk)
        difference = linalg.norm(array(SuCalc)-array(SL))
        self.assertTrue(difference<1e-10,'Two Port Two Devices SL unknown Fixture Deembedding incorrect')
        #Now test according to the two port equation in the book
        Sk11=Sk[1-1][1-1]
        Sk12=Sk[1-1][2-1]
        Sk21=Sk[2-1][1-1]
        Sk22=Sk[2-1][2-1]
        SR11=SR[1-1][1-1]
        SR12=SR[1-1][2-1]
        SR21=SR[2-1][1-1]
        SR22=SR[2-1][2-1]
        SLcalc=1./(Sk22*SR11-linalg.det(SR))
        SLcalc=SLcalc*array([[SR11*linalg.det(Sk)-Sk11*linalg.det(SR),Sk12*SR21],[Sk21*SR12,Sk22-SR22]])
        difference = linalg.norm(array(SLcalc)-array(SL))
        self.assertTrue(difference<1e-10,'Two Port Two Devices SL Unknown Fixture Deembedding equation incorrect')
    def testUnderconstrained(self):
        f=si.fd.EvenlySpacedFrequencyList(20e9,20)
        si.p.SystemSParametersNumericParser(f).AddLines(['device R1 2 R 50.0','device R2 2 R 50.0',
            'device R3 2 R 50.0','port 1 R1 1','connect R1 2 R2 1','connect R3 1 R2 2',
            'port 2 R3 2']).SParameters().WriteToFile('system.s2p')
        with self.assertRaises(si.SignalIntegrityException) as cm:
            si.p.DeembedderNumericParser(f).AddLines(['unknown U1 2','unknown U2 2',
                'system file system.s2p','device R1 2 R 50.0','port 1 U1 1','connect U1 2 R1 1',
                'connect R1 2 U2 1','port 2 U2 2']).Deembed()
        self.assertEqual(cm.exception.parameter,'Numeric')
        self.assertEqual(cm.exception.message,'under-constrained system')
        os.remove('system.s2p')
    def testF12(self):
        f=si.fd.EvenlySpacedFrequencyList(20e9,20)
        with self.assertRaises(si.SignalIntegrityException) as cm:
            si.p.DeembedderNumericParser(f).AddLines(['system file cable.s2p',
                'unknown U1 2','device T1 2 tline zc 50.0 td 0.0','device O1 1 open','device O2 1 open',
                'port 1 U1 1','connect T1 1 U1 2','connect O2 1 T1 2','port 2 O1 1']).Deembed()
        self.assertEqual(cm.exception.parameter,'Numeric')
        self.assertEqual(cm.exception.message,'cannot invert F12')    
    def testMultipleParser(self):
        f=si.fd.EvenlySpacedFrequencyList(20e9,20)
        res=si.p.DeembedderNumericParser(f).AddLines(['system file cable.s2p','unknown U1 1','unknown U2 1',
                                                      'port 1 U1 1','port 2 U2 1']).Deembed()
        self.assertTrue(isinstance(res,list),'test should have provided multiple results - it did not')
        self.assertTrue(len(res)==2,'test should have provided exactly two results - it did not')
        filenamePrefix='_'.join(self.id().split('.')[-2:])
        self.CheckSParametersResult(res[0],filenamePrefix+'_0.s1p','first result incorrect')
        self.CheckSParametersResult(res[0],filenamePrefix+'_1.s1p','second result incorrect')

if __name__ == '__main__':
    unittest.main()
