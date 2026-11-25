"""
TestDeviceParser.py
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

import os
import SignalIntegrity.Lib as si

class TestDeviceParser(unittest.TestCase,si.test.ResponseTesterHelper):
    def __init__(self, methodName='runTest'):
        unittest.TestCase.__init__(self,methodName)
    def id(self):
        return '.'.join(unittest.TestCase.id(self).split('.')[-3:])
    def Tester(self,idName,deviceName,ports,pr=None,**args):
        fileNameBase='TestDeviceParser_'+self.id().split('.')[2]
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        spFileName = fileNameBase +'.s'+str(ports)+'p'
        ssnp=si.p.SystemSParametersNumericParser(si.fd.EvenlySpacedFrequencyList(10e9,100))
        devLine='device D '+str(ports)
        if not deviceName is None:
            devLine = devLine + ' '+deviceName
        if 'default' in args:
            devLine = devLine + ' '+args['default']
            del args['default']
        for key in args.keys():
            devLine = devLine + ' ' + key + ' ' + args[key]
        lines=[devLine]
        for p in range(ports):
            lines.append('port '+str(p+1)+' D '+str(p+1))
        ssnp.AddLines(lines)
        sp=ssnp.SParameters()
        if not pr is None:
            sp=sp.PortReorder(pr)
        self.CheckSParametersResult(sp,spFileName,spFileName+' incorrect')
    def testFile(self):
        self.Tester(self.id(),'file',2,default='../TestSParametersParser/filter.s2p')
    def testFileNotFound(self):
        with self.assertRaises(si.SignalIntegrityException) as cm:
            self.Tester(self.id(),'file',2,default='filterNonExistent.s2p')
        self.assertEqual(cm.exception.parameter,'DeviceParser')
    def testTerminationC(self):
        self.Tester(self.id(),'C',1,default='100e-12')
    def testSeriesC(self):
        self.Tester(self.id(),'C',2,default='100e-12')
    def testSeriesCExtraArguments(self):
        with self.assertRaises(si.SignalIntegrityException) as cm:
            self.Tester(self.id(),'C',2,default='100e-12',extra='whattheheck')
        self.assertEqual(cm.exception.parameter,'DeviceParser')
    def testCWrongPorts(self):
        with self.assertRaises(si.SignalIntegrityException) as cm:
            self.Tester(self.id(),'c',3,default='100e-12')
        self.assertEqual(cm.exception.parameter,'DeviceParser')
    def testTerminationL(self):
        self.Tester(self.id(),'L',1,default='100e-9')
    def testSeriesL(self):
        self.Tester(self.id(),'L',2,default='100e-9')
    def testLWrongPorts(self):
        with self.assertRaises(si.SignalIntegrityException) as cm:
            self.Tester(self.id(),'L',3,default='100e-9')
        self.assertEqual(cm.exception.parameter,'DeviceParser')
    def testTerminationR(self):
        self.Tester(self.id(),'R',1,default='50.')
    def testSeriesR(self):
        self.Tester(self.id(),'R',2,default='50.')
    def testRWrongPorts(self):
        with self.assertRaises(si.SignalIntegrityException) as cm:
            self.Tester(self.id(),'R',3,default='50.')
        self.assertEqual(cm.exception.parameter,'DeviceParser')
    def testShunt2(self):
        self.Tester(self.id(),'shunt',2,default='100.')
    def testShunt3(self):
        self.Tester(self.id(),'shunt',3,default='100.')
    def testShunt4(self):
        self.Tester(self.id(),'shunt',4,default='100.')
    def testShunt5(self):
        with self.assertRaises(si.SignalIntegrityException) as cm:
            self.Tester(self.id(),'shunt',5,default='100.')
        self.assertEqual(cm.exception.parameter,'DeviceParser')
    def testMutual(self):
        self.Tester(self.id(),'M',4,default='100e-9')
    def testGround(self):
        self.Tester(self.id(),'ground',1)
    def testGroundWrongPorts(self):
        with self.assertRaises(si.SignalIntegrityException) as cm:
            self.Tester(self.id(),'ground',2)
        self.assertEqual(cm.exception.parameter,'DeviceParser')
    def testOpen(self):
        self.Tester(self.id(),'open',1)
    def testThruWrongPorts(self):
        with self.assertRaises(si.SignalIntegrityException) as cm:
            self.Tester(self.id(),'thru',1)
        self.assertEqual(cm.exception.parameter,'DeviceParser')
    def testThru(self):
        self.Tester(self.id(),'thru',2)
    def testTermination2(self):
        self.Tester(self.id(),'termination',2)
    def testTermination3(self):
        self.Tester(self.id(),'termination',3)
    def testTermination4(self):
        self.Tester(self.id(),'termination',4)
    def testTee1(self):
        self.Tester(self.id(),'tee',1)
    def testTee2(self):
        self.Tester(self.id(),'tee',2)
    def testTee3(self):
        self.Tester(self.id(),'tee',3)
    def testTee4(self):
        self.Tester(self.id(),'tee',4)
    def testMixedModeVoltage(self):
        self.Tester(self.id(),'mixedmode',4,default='voltage')
    def testMixedModePower(self):
        self.Tester(self.id(),'mixedmode',4)
    def testIdealTransformer(self):
        self.Tester(self.id(),'idealtransformer',4)
    def testIdealTransformerTurnsRatio(self):
        self.Tester(self.id(),'idealtransformer',4,default='2')
    def testVoltageControlledVoltageSourceNoGain(self):
        with self.assertRaises(si.SignalIntegrityException) as cm:
            self.Tester(self.id(),'voltagecontrolledvoltagesource',4)
        self.assertEqual(cm.exception.parameter,'DeviceParser')
    def testVoltageControlledVoltageSourceGainDefault(self):
        self.Tester(self.id(),'voltagecontrolledvoltagesource',4,default='1.')
    def testVoltageControlledCurrentSourceNoGain(self):
        with self.assertRaises(si.SignalIntegrityException) as cm:
            self.Tester(self.id(),'voltagecontrolledcurrentsource',4)
        self.assertEqual(cm.exception.parameter,'DeviceParser')
    def testVoltageControlledCurrentSourceGainDefault(self):
        self.Tester(self.id(),'voltagecontrolledcurrentsource',4,default='1.')
    def testCurrentControlledCurrentSourceNoGain(self):
        with self.assertRaises(si.SignalIntegrityException) as cm:
            self.Tester(self.id(),'currentcontrolledcurrentsource',4)
        self.assertEqual(cm.exception.parameter,'DeviceParser')
    def testCurrentControlledCurrentSourceGainDefault(self):
        self.Tester(self.id(),'currentcontrolledcurrentsource',4,default='1.')
    def testCurrentControlledVoltageSourceNoGain(self):
        with self.assertRaises(si.SignalIntegrityException) as cm:
            self.Tester(self.id(),'currentcontrolledvoltagesource',4)
        self.assertEqual(cm.exception.parameter,'DeviceParser')
    def testCurrentControlledVoltageSourceGainDefault(self):
        self.Tester(self.id(),'currentcontrolledvoltagesource',4,default='1.')
    def testVoltageAmplifierNoGain1(self):
        with self.assertRaises(si.SignalIntegrityException) as cm:
            self.Tester(self.id(),'voltageamplifier',1)
        self.assertEqual(cm.exception.parameter,'DeviceParser')
    def testVoltageAmplifierGainDefault1(self):
        with self.assertRaises(si.SignalIntegrityException) as cm:
            self.Tester(self.id(),'voltageamplifier',1,default='1.')
        self.assertEqual(cm.exception.parameter,'DeviceParser')
    def testVoltageAmplifierGain1(self):
        with self.assertRaises(si.SignalIntegrityException) as cm:
            self.Tester(self.id(),'voltageamplifier',1,gain='1.')
        self.assertEqual(cm.exception.parameter,'DeviceParser')
    def testVoltageAmplifierNoGain2(self):
        with self.assertRaises(si.SignalIntegrityException) as cm:
            self.Tester(self.id(),'voltageamplifier',2)
        self.assertEqual(cm.exception.parameter,'DeviceParser')
    def testVoltageAmplifierGainDefault2(self):
        with self.assertRaises(si.SignalIntegrityException) as cm:
            self.Tester(self.id(),'voltageamplifier',2,default='1.')
        self.assertEqual(cm.exception.parameter,'DeviceParser')
    def testVoltageAmplifierGain2(self):
        self.Tester(self.id(),'voltageamplifier',2,gain='1.')
    def testVoltageAmplifierNoGain3(self):
        with self.assertRaises(si.SignalIntegrityException) as cm:
            self.Tester(self.id(),'voltageamplifier',3)
        self.assertEqual(cm.exception.parameter,'DeviceParser')
    def testVoltageAmplifierGainDefault3(self):
        with self.assertRaises(si.SignalIntegrityException) as cm:
            self.Tester(self.id(),'voltageamplifier',3,default='1.')
        self.assertEqual(cm.exception.parameter,'DeviceParser')
    def testVoltageAmplifierGain3(self):
        self.Tester(self.id(),'voltageamplifier',3,gain='1.')
    def testVoltageAmplifierNoGain4(self):
        with self.assertRaises(si.SignalIntegrityException) as cm:
            self.Tester(self.id(),'voltageamplifier',4)
        self.assertEqual(cm.exception.parameter,'DeviceParser')
    def testVoltageAmplifierGainDefault4(self):
        with self.assertRaises(si.SignalIntegrityException) as cm:
            self.Tester(self.id(),'voltageamplifier',4,default='1.')
        self.assertEqual(cm.exception.parameter,'DeviceParser')
    def testVoltageAmplifierGain4(self):
        self.Tester(self.id(),'voltageamplifier',4,gain='1.')
    def testVoltageAmplifierNoGain5(self):
        with self.assertRaises(si.SignalIntegrityException) as cm:
            self.Tester(self.id(),'voltageamplifier',5)
        self.assertEqual(cm.exception.parameter,'DeviceParser')
    def testVoltageAmplifierGainDefault5(self):
        with self.assertRaises(si.SignalIntegrityException) as cm:
            self.Tester(self.id(),'voltageamplifier',5,default='5.')
        self.assertEqual(cm.exception.parameter,'DeviceParser')
    def testVoltageAmplifierGain5(self):
        with self.assertRaises(si.SignalIntegrityException) as cm:
            self.Tester(self.id(),'voltageamplifier',5,gain='5.')
        self.assertEqual(cm.exception.parameter,'DeviceParser')
    def testCurrentAmplifierNoGain1(self):
        with self.assertRaises(si.SignalIntegrityException) as cm:
            self.Tester(self.id(),'currentamplifier',1)
        self.assertEqual(cm.exception.parameter,'DeviceParser')
    def testCurrentAmplifierGainDefault1(self):
        with self.assertRaises(si.SignalIntegrityException) as cm:
            self.Tester(self.id(),'currentamplifier',1,default='1.')
        self.assertEqual(cm.exception.parameter,'DeviceParser')
    def testCurrentAmplifierGain1(self):
        with self.assertRaises(si.SignalIntegrityException) as cm:
            self.Tester(self.id(),'currentamplifier',1,gain='1.')
        self.assertEqual(cm.exception.parameter,'DeviceParser')
    def testCurrentAmplifierNoGain2(self):
        with self.assertRaises(si.SignalIntegrityException) as cm:
            self.Tester(self.id(),'currentamplifier',2)
        self.assertEqual(cm.exception.parameter,'DeviceParser')
    def testCurrentAmplifierGainDefault2(self):
        with self.assertRaises(si.SignalIntegrityException) as cm:
            self.Tester(self.id(),'currentamplifier',2,default='1.')
        self.assertEqual(cm.exception.parameter,'DeviceParser')
    def testCurrentAmplifierGain2(self):
        self.Tester(self.id(),'currentamplifier',2,gain='1.')
    def testCurrentAmplifierNoGain3(self):
        with self.assertRaises(si.SignalIntegrityException) as cm:
            self.Tester(self.id(),'currentamplifier',3)
        self.assertEqual(cm.exception.parameter,'DeviceParser')
    def testCurrentAmplifierGainDefault3(self):
        with self.assertRaises(si.SignalIntegrityException) as cm:
            self.Tester(self.id(),'currentamplifier',3,default='1.')
        self.assertEqual(cm.exception.parameter,'DeviceParser')
    def testCurrentAmplifierGain3(self):
        self.Tester(self.id(),'currentamplifier',3,gain='1.')
    def testCurrentAmplifierNoGain4(self):
        with self.assertRaises(si.SignalIntegrityException) as cm:
            self.Tester(self.id(),'currentamplifier',4)
        self.assertEqual(cm.exception.parameter,'DeviceParser')
    def testCurrentAmplifierGainDefault4(self):
        with self.assertRaises(si.SignalIntegrityException) as cm:
            self.Tester(self.id(),'currentamplifier',4,default='1.')
        self.assertEqual(cm.exception.parameter,'DeviceParser')
    def testCurrentAmplifierGain4(self):
        self.Tester(self.id(),'currentamplifier',4,gain='1.')
    def testCurrentAmplifierNoGain5(self):
        with self.assertRaises(si.SignalIntegrityException) as cm:
            self.Tester(self.id(),'currentamplifier',5)
        self.assertEqual(cm.exception.parameter,'DeviceParser')
    def testCurrentAmplifierGainDefault5(self):
        with self.assertRaises(si.SignalIntegrityException) as cm:
            self.Tester(self.id(),'currentamplifier',5,default='5.')
        self.assertEqual(cm.exception.parameter,'DeviceParser')
    def testCurrentAmplifierGain5(self):
        with self.assertRaises(si.SignalIntegrityException) as cm:
            self.Tester(self.id(),'currentamplifier',5,gain='5.')
        self.assertEqual(cm.exception.parameter,'DeviceParser')
    def testTransresistanceAmplifierNoGain1(self):
        with self.assertRaises(si.SignalIntegrityException) as cm:
            self.Tester(self.id(),'transresistanceamplifier',1)
        self.assertEqual(cm.exception.parameter,'DeviceParser')
    def testTransresistanceAmplifierGainDefault1(self):
        with self.assertRaises(si.SignalIntegrityException) as cm:
            self.Tester(self.id(),'transresistanceamplifier',1,default='1.')
        self.assertEqual(cm.exception.parameter,'DeviceParser')
    def testTransresistanceAmplifierGain1(self):
        with self.assertRaises(si.SignalIntegrityException) as cm:
            self.Tester(self.id(),'transresistanceamplifier',1,gain='1.')
        self.assertEqual(cm.exception.parameter,'DeviceParser')
    def testTransresistanceAmplifierNoGain2(self):
        with self.assertRaises(si.SignalIntegrityException) as cm:
            self.Tester(self.id(),'transresistanceamplifier',2)
        self.assertEqual(cm.exception.parameter,'DeviceParser')
    def testTransresistanceAmplifierGainDefault2(self):
        with self.assertRaises(si.SignalIntegrityException) as cm:
            self.Tester(self.id(),'transresistanceamplifier',2,default='1.')
        self.assertEqual(cm.exception.parameter,'DeviceParser')
    def testTransresistanceAmplifierGain2(self):
        self.Tester(self.id(),'transresistanceamplifier',2,gain='1.')
    def testTransresistanceAmplifierNoGain3(self):
        with self.assertRaises(si.SignalIntegrityException) as cm:
            self.Tester(self.id(),'transresistanceamplifier',3)
        self.assertEqual(cm.exception.parameter,'DeviceParser')
    def testTransresistanceAmplifierGainDefault3(self):
        with self.assertRaises(si.SignalIntegrityException) as cm:
            self.Tester(self.id(),'transresistanceamplifier',3,default='1.')
        self.assertEqual(cm.exception.parameter,'DeviceParser')
    def testTransresistanceAmplifierGain3(self):
        self.Tester(self.id(),'transresistanceamplifier',3,gain='1.')
    def testTransresistanceAmplifierNoGain4(self):
        with self.assertRaises(si.SignalIntegrityException) as cm:
            self.Tester(self.id(),'transresistanceamplifier',4)
        self.assertEqual(cm.exception.parameter,'DeviceParser')
    def testTransresistanceAmplifierGainDefault4(self):
        with self.assertRaises(si.SignalIntegrityException) as cm:
            self.Tester(self.id(),'transresistanceamplifier',4,default='1.')
        self.assertEqual(cm.exception.parameter,'DeviceParser')
    def testTransresistanceAmplifierGain4(self):
        self.Tester(self.id(),'transresistanceamplifier',4,gain='1.')
    def testTransresistanceAmplifierNoGain5(self):
        with self.assertRaises(si.SignalIntegrityException) as cm:
            self.Tester(self.id(),'transresistanceamplifier',5)
        self.assertEqual(cm.exception.parameter,'DeviceParser')
    def testTransresistanceAmplifierGainDefault5(self):
        with self.assertRaises(si.SignalIntegrityException) as cm:
            self.Tester(self.id(),'transresistanceamplifier',5,default='5.')
        self.assertEqual(cm.exception.parameter,'DeviceParser')
    def testTransresistanceAmplifierGain5(self):
        with self.assertRaises(si.SignalIntegrityException) as cm:
            self.Tester(self.id(),'transresistanceamplifier',5,gain='5.')
        self.assertEqual(cm.exception.parameter,'DeviceParser')
    def testTransconductanceAmplifierNoGain1(self):
        with self.assertRaises(si.SignalIntegrityException) as cm:
            self.Tester(self.id(),'transconductanceamplifier',1)
        self.assertEqual(cm.exception.parameter,'DeviceParser')
    def testTransconductanceAmplifierGainDefault1(self):
        with self.assertRaises(si.SignalIntegrityException) as cm:
            self.Tester(self.id(),'transconductanceamplifier',1,default='1.')
        self.assertEqual(cm.exception.parameter,'DeviceParser')
    def testTransconductanceAmplifierGain1(self):
        with self.assertRaises(si.SignalIntegrityException) as cm:
            self.Tester(self.id(),'transconductanceamplifier',1,gain='1.')
        self.assertEqual(cm.exception.parameter,'DeviceParser')
    def testTransconductanceAmplifierNoGain2(self):
        with self.assertRaises(si.SignalIntegrityException) as cm:
            self.Tester(self.id(),'transconductanceamplifier',2)
        self.assertEqual(cm.exception.parameter,'DeviceParser')
    def testTransconductanceAmplifierGainDefault2(self):
        with self.assertRaises(si.SignalIntegrityException) as cm:
            self.Tester(self.id(),'transconductanceamplifier',2,default='1.')
        self.assertEqual(cm.exception.parameter,'DeviceParser')
    def testTransconductanceAmplifierGain2(self):
        self.Tester(self.id(),'transconductanceamplifier',2,gain='1.')
    def testTransconductanceAmplifierNoGain3(self):
        with self.assertRaises(si.SignalIntegrityException) as cm:
            self.Tester(self.id(),'transconductanceamplifier',3)
        self.assertEqual(cm.exception.parameter,'DeviceParser')
    def testTransconductanceAmplifierGainDefault3(self):
        with self.assertRaises(si.SignalIntegrityException) as cm:
            self.Tester(self.id(),'transconductanceamplifier',3,default='1.')
        self.assertEqual(cm.exception.parameter,'DeviceParser')
    def testTransconductanceAmplifierGain3(self):
        self.Tester(self.id(),'transconductanceamplifier',3,gain='1.')
    def testTransconductanceAmplifierNoGain4(self):
        with self.assertRaises(si.SignalIntegrityException) as cm:
            self.Tester(self.id(),'transconductanceamplifier',4)
        self.assertEqual(cm.exception.parameter,'DeviceParser')
    def testTransconductanceAmplifierGainDefault4(self):
        with self.assertRaises(si.SignalIntegrityException) as cm:
            self.Tester(self.id(),'transconductanceamplifier',4,default='1.')
        self.assertEqual(cm.exception.parameter,'DeviceParser')
    def testTransconductanceAmplifierGain4(self):
        self.Tester(self.id(),'transconductanceamplifier',4,gain='1.')
    def testTransconductanceAmplifierNoGain5(self):
        with self.assertRaises(si.SignalIntegrityException) as cm:
            self.Tester(self.id(),'transconductanceamplifier',5)
        self.assertEqual(cm.exception.parameter,'DeviceParser')
    def testTransconductanceAmplifierGainDefault5(self):
        with self.assertRaises(si.SignalIntegrityException) as cm:
            self.Tester(self.id(),'transconductanceamplifier',5,default='5.')
        self.assertEqual(cm.exception.parameter,'DeviceParser')
    def testTransconductanceAmplifierGain5(self):
        with self.assertRaises(si.SignalIntegrityException) as cm:
            self.Tester(self.id(),'transconductanceamplifier',5,gain='5.')
        self.assertEqual(cm.exception.parameter,'DeviceParser')
    def testTline2Default(self):
        self.Tester(self.id(),'tline',2)
    def testTline2zctd(self):
        self.Tester(self.id(),'tline',2,zc='100',td='100e-12')
    def testTline4Default(self):
        self.Tester(self.id(),'tline',4)
    def testTline4zctd(self):
        self.Tester(self.id(),'tline',4,zc='100',td='100e-12')
    def testMCB4Default(self):
        ssnp=si.p.SystemSParametersNumericParser(si.fd.EvenlySpacedFrequencyList(10e9,100))
        ssnp.AddLines(['device D 4 mcb',
                       'port 1 D 1',
                       'port 2 D 2',
                       'port 3 D 3',
                       'port 4 D 4'])
        sp=ssnp.SParameters()
        self.assertEqual(sp.m_P,4)
        self.assertTrue(abs(sp[-1][2][0]) < abs(sp[1][2][0]))
    def testMCB4ExplicitDefaultDelay(self):
        linesDefault=['device D 4 mcb',
                      'port 1 D 1',
                      'port 2 D 2',
                      'port 3 D 3',
                      'port 4 D 4']
        linesExplicit=['device D 4 mcb td 200e-12',
                       'port 1 D 1',
                       'port 2 D 2',
                       'port 3 D 3',
                       'port 4 D 4']
        ssnpDefault=si.p.SystemSParametersNumericParser(si.fd.EvenlySpacedFrequencyList(10e9,100))
        ssnpDefault.AddLines(linesDefault)
        spDefault=ssnpDefault.SParameters()
        ssnpExplicit=si.p.SystemSParametersNumericParser(si.fd.EvenlySpacedFrequencyList(10e9,100))
        ssnpExplicit.AddLines(linesExplicit)
        spExplicit=ssnpExplicit.SParameters()
        self.assertTrue(self.SParametersAreEqual(spDefault,spExplicit))
    def testMCBWrongPorts(self):
        with self.assertRaises(si.SignalIntegrityException) as cm:
            self.Tester(self.id(),'mcb',2)
        self.assertEqual(cm.exception.parameter,'DeviceParser')
    def testMCBZeroReturnLoss(self):
        fl=si.fd.EvenlySpacedFrequencyList(10e9,100)
        mcb=si.sp.dev.MCB(fl)
        m=mcb[50]
        for i in range(4):
            self.assertAlmostEqual(abs(m[i][i]),0.,places=12)
        # the two pairs (1<->3, 2<->4) are independent and reciprocal
        self.assertAlmostEqual(abs(m[0][1]),0.,places=12)
        self.assertAlmostEqual(abs(m[2][0]-m[0][2]),0.,places=12)
        self.assertTrue(abs(m[2][0])>0.)
    def testMCBUsesTwoTransmissionLines(self):
        fl=si.fd.EvenlySpacedFrequencyList(10e9,100)
        mcb=si.sp.dev.MCB(fl)
        self.assertTrue(isinstance(mcb.m_line1,si.sp.dev.TransmissionLineEquation))
        self.assertTrue(isinstance(mcb.m_line2,si.sp.dev.TransmissionLineEquation))
    def testTransmissionLineEquationDirect(self):
        fl=si.fd.EvenlySpacedFrequencyList(10e9,100)
        tle=si.sp.dev.TransmissionLineEquation(fl,'cmath.exp(-j*2*pi*f*100e-12)')
        self.assertTrue(isinstance(tle,si.sp.dev.Equation))
        m=tle[25]
        self.assertEqual(abs(m[0][0]),0.)
        self.assertEqual(abs(m[1][1]),0.)
        self.assertAlmostEqual(abs(m[0][1]-m[1][0]),0.,places=12)
        self.assertAlmostEqual(abs(m[1][0]),1.,places=9)
    def testTransmissionLineEquationIsEager(self):
        fl=si.fd.EvenlySpacedFrequencyList(10e9,100)
        tle=si.sp.dev.TransmissionLineEquation(fl,'cmath.exp(-j*2*pi*f*100e-12)')
        self.assertFalse(tle.m_d is None)
        self.assertEqual(len(tle.m_d),len(fl))
    def testLaplaceIsEquation(self):
        fl=si.fd.EvenlySpacedFrequencyList(10e9,100)
        lp=si.sp.dev.Laplace(fl,'1.0/(1+s/(2*pi*1e9))')
        self.assertTrue(isinstance(lp,si.sp.dev.Equation))
        m=lp[0]
        self.assertEqual(m[0][0],1.)
        self.assertEqual(m[0][1],0)
        self.assertEqual(m[1][1],-1.)
    def testTlineEquationMatched(self):
        fl=si.fd.EvenlySpacedFrequencyList(10e9,100)
        ssnp=si.p.SystemSParametersNumericParser(fl)
        ssnp.AddLines(['device D 2 tlineequation cmath.exp(-j*2*pi*f*100e-12) zc 50',
                       'port 1 D 1','port 2 D 2'])
        sp=ssnp.SParameters()
        m=sp[25]
        self.assertAlmostEqual(abs(m[0][0]),0.,places=9)
        self.assertAlmostEqual(abs(m[1][1]),0.,places=9)
        self.assertAlmostEqual(abs(m[1][0]),1.,places=6)
        self.assertAlmostEqual(abs(m[0][1]-m[1][0]),0.,places=9)
    def testTlineEquationDefaultZcMatched(self):
        fl=si.fd.EvenlySpacedFrequencyList(10e9,100)
        ssnp=si.p.SystemSParametersNumericParser(fl)
        ssnp.AddLines(['device D 2 tlineequation cmath.exp(-j*2*pi*f*100e-12)',
                       'port 1 D 1','port 2 D 2'])
        sp=ssnp.SParameters()
        self.assertAlmostEqual(abs(sp[25][0][0]),0.,places=9)
    def testTlineEquationMismatchedReflects(self):
        fl=si.fd.EvenlySpacedFrequencyList(10e9,100)
        ssnp=si.p.SystemSParametersNumericParser(fl)
        ssnp.AddLines(['device D 2 tlineequation cmath.exp(-j*2*pi*f*100e-12) zc 75',
                       'port 1 D 1','port 2 D 2'])
        sp=ssnp.SParameters()
        # quarter-wave (index 25) input impedance Zc**2/Z0=112.5 -> |S11|=0.3846
        self.assertAlmostEqual(abs(sp[25][0][0]),0.3846,places=3)
        # half-wave (index 50) is impedance transparent
        self.assertAlmostEqual(abs(sp[50][0][0]),0.,places=6)
        # reciprocity preserved through the reference impedance conversion
        self.assertAlmostEqual(abs(sp[25][0][1]-sp[25][1][0]),0.,places=9)
    def testTlineEquationWrongPorts(self):
        with self.assertRaises(si.SignalIntegrityException) as cm:
            self.Tester(self.id(),'tlineequation',4,default='cmath.exp(-j*2*pi*f*100e-12)')
        self.assertEqual(cm.exception.parameter,'DeviceParser')
    def testTelegrapher2Default(self):
        self.Tester(self.id(),'telegrapher',2)
    def testTelegrapher2LC(self):
        self.Tester(self.id(),'telegrapher',2,c='20e-12',l='50e-9',sect='10000')
    def testTelegrapher4Default(self):
        self.Tester(self.id(),'telegrapher',4,[1,3,2,4],sect='1')
    def testTelegrapher4LC(self):
        self.Tester(self.id(),'telegrapher',4,[1,3,2,4],lp='58.5e-9',cp='20e-12',ln='58.5e-9',cn='20e-12',lm='13.5e-9',cm='1.111e-12',sect='10000')
    def testDirectionalCoupler3(self):
        self.Tester(self.id(),'directionalcoupler',3)
    def testDirectionalCoupler4(self):
        self.Tester(self.id(),'directionalcoupler',4)
    def testShortStd(self):
        self.Tester(self.id(),'shortstd',1,od='31.785e-12',oz0='50.0',ol='2.36e9',l0='2.076',l1='-108.54',l2='2.171',l3='-0.1')
    def testOpenStd(self):
        self.Tester(self.id(),'openstd',1,od='29.243e-12',oz0='50.0',ol='2.2e9',c0='49.433',c1='-310.13',c2='23.168',c3='-0.16')
    def testLoadStd(self):
        self.Tester(self.id(),'loadstd',1,od='0.',oz0='50.0',ol='0.')
    def testThruStd(self):
        self.Tester(self.id(),'thrustd',2,od='94.75e-12',oz0='50.0',ol='2.51e9')
    def testBesselLp(self):
        self.Tester(self.id(),'bessellp',2,order='4',fc='1e9')
    def testButterworthLp(self):
        self.Tester(self.id(),'butterworthlp',2,order='4',fc='1e9')
    def testCTLE(self):
        self.Tester(self.id(),'ctle',2,gdc='-2',gdc2='0',fz='2.3e9',flf='70e6',fp1='2.3e9',fp2='5.6e9')
    def testFFE(self):
        self.Tester(self.id(),'ffe',2,default='[-0.1,1.3,-0.2]',td='100e-12',pre='1')
    def testCTLEStandard(self):
        import numpy as np

        f=[0.,1.e9,12.e9,28.e9,56.e9]
        for baud in [56.e9,112.e9]:
            for divisors,gains in [((2.5,80.,2.5,1.),(-2.,0.)),
                                   ((3.,100.,4.,1.5),(-6.,-1.))]:
                with self.subTest(baud=baud,divisors=divisors):
                    expected=si.sp.dev.CTLE(f,*gains,*(baud/d for d in divisors),Z0=75.)
                    if divisors==(2.5,80.,2.5,1.):
                        standard=si.sp.dev.CTLE_standard(f,baud,Z0=75.)
                        args=['ctle_std','br',str(baud)]
                    else:
                        standard=si.sp.dev.CTLE_standard(f,baud,*gains,*divisors,Z0=75.)
                        args=['ctle_std','br',str(baud),'gdc',str(gains[0]),'gdc2',str(gains[1])]
                        for keyword,value in zip(
                                ['fz_divisor','flf_divisor','fp1_divisor','fp2_divisor'],divisors):
                            args.extend([keyword,str(value)])
                    self.assertIsInstance(standard,si.sp.dev.CTLE)
                    np.testing.assert_allclose(list(standard),list(expected),rtol=1.e-13,atol=1.e-14)
                    parser=si.p.SystemSParametersNumericParser(f,Z0=75.)
                    parser.AddLines(['device E1 2 '+' '.join(args),'port 1 E1 1 2 E1 2'])
                    np.testing.assert_allclose(list(parser.SParameters()),list(expected),rtol=1.e-13,atol=1.e-14)
    def testFFEStandard(self):
        import numpy as np

        for f in [[0.,1.e9,12.e9,28.e9,56.e9],
                  si.fd.EvenlySpacedFrequencyList(56.e9,32)]:
            for baud in [56.e9,112.e9]:
                for taps,pre,tapsPerUI in [([1.],0,1),([-.1,1.3,-.2],1,1),
                                            ([.2,1.,-.1],1,2)]:
                    with self.subTest(baud=baud,taps=taps,tapsPerUI=tapsPerUI):
                        expected=si.sp.dev.FFE(f,1./baud/tapsPerUI,taps,pre,Z0=75.)
                        if taps==[1.]:
                            standard=si.sp.dev.FFE_standard(f,baud,Z0=75.)
                            args=['ffe_std','br',str(baud)]
                        else:
                            standard=si.sp.dev.FFE_standard(f,baud,taps,pre,tapsPerUI,Z0=75.)
                            args=['ffe_std',repr(taps).replace(' ',''),'br',str(baud),
                                  'pre',str(pre),'taps_per_ui',str(tapsPerUI)]
                        self.assertIsInstance(standard,si.sp.dev.FFE)
                        self.assertEqual(standard.Td,1./baud/tapsPerUI)
                        np.testing.assert_allclose(list(standard),list(expected),rtol=1.e-13,atol=1.e-14)
                        parser=si.p.SystemSParametersNumericParser(f,Z0=75.)
                        parser.AddLines(['device E1 2 '+' '.join(args),'port 1 E1 1 2 E1 2'])
                        np.testing.assert_allclose(list(parser.SParameters()),list(expected),rtol=1.e-13,atol=1.e-14)
    def testStandardEqualizersRejectInvalidParameters(self):
        for baud in [0.,-1.,float('inf'),float('nan')]:
            for equalizer in [si.sp.dev.CTLE_standard,si.sp.dev.FFE_standard]:
                with self.subTest(equalizer=equalizer,baud=baud):
                    with self.assertRaises(ValueError):
                        equalizer([0.],baud)
        for keyword in ['fz_divisor','flf_divisor','fp1_divisor','fp2_divisor']:
            for value in [0.,-1.,float('inf'),float('nan')]:
                with self.subTest(keyword=keyword,value=value):
                    with self.assertRaises(ValueError):
                        si.sp.dev.CTLE_standard([0.],56.e9,**{keyword:value})
        for tapsPerUI in [0,-1,1.5,1.,True]:
            with self.subTest(tapsPerUI=tapsPerUI):
                with self.assertRaises(ValueError):
                    si.sp.dev.FFE_standard([0.],56.e9,tapsPerUI=tapsPerUI)
        invalidArgs=[['ctle_std'],['ffe_std']]
        for name in ['ctle_std','ffe_std']:
            invalidArgs.extend([[name,'br',value] for value in ['0','-1','inf','nan']])
        invalidArgs.extend([['ffe_std','br','56e9','taps_per_ui',value]
                            for value in ['0','-1','1.5','1.0']])
        invalidArgs.extend([['ctle_std','br','56e9',keyword,'0']
                            for keyword in ['fz_divisor','flf_divisor','fp1_divisor','fp2_divisor']])
        for args in invalidArgs:
            with self.subTest(args=args):
                factory=si.p.dev.DeviceFactory()
                with self.assertRaises(si.SignalIntegrityException) as cm:
                    factory.MakeDevice(2,None,args,[0.])
                self.assertEqual(cm.exception.parameter,'DeviceParser')
    def testStandardEqualizerApplicationRoundTrip(self):
        import tempfile
        from unittest.mock import patch
        import numpy as np
        import SignalIntegrity.App.Preferences
        from SignalIntegrity.App.PreferencesFile import PreferencesFile
        from SignalIntegrity.App.ProjectFile import ProjectFile
        from SignalIntegrity.App.ProjectFileBase import ProjectFileBase
        from SignalIntegrity.App.Device import (
            DeviceCTLE,DeviceFFE,DeviceCTLEStandard,DeviceFFEStandard,DeviceFromProject,DeviceList)

        devices=[DeviceCTLE(),DeviceCTLEStandard(),DeviceFFE(),DeviceFFEStandard()]
        devices[1]['br']['Value']=56.e9
        devices[1]['gdc']['Value']=-5.
        devices[1]['fp2_divisor']['Value']=1.5
        devices[3]['br']['Value']=56.e9
        devices[3]['taps']['Value']='[-0.1,1.3,-0.2]'
        devices[3]['pre']['Value']=1
        devices[3]['taps_per_ui']['Value']=2
        devices[2]['td']['Value']=1./56.e9
        for index,device in enumerate(devices):
            device['ref']['Value']='E'+str(index+1)
            device.partPicture.current.SetOrigin((17,23))
            device.partPicture.current.ApplyOrientation('90',True,False)
        self.assertEqual(devices[1].partPicture.partPictureClassList,devices[0].partPicture.partPictureClassList)
        self.assertEqual(devices[3].partPicture.partPictureClassList,devices[2].partPicture.partPictureClassList)
        self.assertEqual(devices[3]['taps_per_ui']['Type'],'int')
        equalizers=[device for device in DeviceList if 'Equalizers' in device.Categories()]
        self.assertEqual([device['partname'].GetValue() for device in equalizers],
                         ['CTLE','CTLE (Standard)','FFE','FFE (Standard)'])
        legacy=[device for device in equalizers if type(device) in [DeviceCTLE,DeviceFFE]]
        enabled=[device.enabled for device in legacy]
        try:
            DeviceList.Enable('CTLE',False)
            DeviceList.Enable('FFE',False)
            self.assertEqual([device['desc'].GetValue() for device in equalizers if device.enabled],
                             ['Standard Defined CTLE','Standard Defined FFE'])
            with patch('SignalIntegrity.App.Preferences',PreferencesFile()),tempfile.TemporaryDirectory() as directory:
                project=ProjectFile()
                ProjectFile.WritePageDevices(project['Drawing'],devices)
                filename=os.path.join(directory,'StandardEqualizers.si')
                ProjectFileBase.Write(project,filename)
                loaded=ProjectFile().Read(filename)
                restored=[DeviceFromProject(device).result for device in loaded['Drawing.Schematic.Devices']]
            f=[0.,1.e9,12.e9,28.e9]
            for original,device in zip(devices,restored):
                self.assertIs(type(device),type(original))
                self.assertEqual(device.NetListLine(),original.NetListLine())
                self.assertEqual(device.partPicture.current.origin,(17,23))
                self.assertEqual(device.partPicture.current.orientation,'90')
                self.assertTrue(device.partPicture.current.mirroredHorizontally)
                if type(device) in [DeviceCTLEStandard,DeviceFFEStandard]:
                    parser=si.p.SystemSParametersNumericParser(f)
                    parser.AddLines([device.NetListLine(),'port 1 '+device['ref'].GetValue()+' 1 2 '+device['ref'].GetValue()+' 2'])
                    expected=(si.sp.dev.CTLE(f,-5.,0.,56.e9/2.5,56.e9/80.,56.e9/2.5,56.e9/1.5)
                              if type(device) is DeviceCTLEStandard else
                              si.sp.dev.FFE(f,1./56.e9/2,[-.1,1.3,-.2],1))
                    np.testing.assert_allclose(list(parser.SParameters()),list(expected),rtol=1.e-13,atol=1.e-14)
        finally:
            for device,enable in zip(legacy,enabled):
                device.enabled=enable
    def testRelay2OpenTermOpen(self):
        self.Tester(self.id(),'relay',2,default='0')
    def testRelay2ClosedTermOpen(self):
        self.Tester(self.id(),'relay',2,default='1')
    def testRelay2OpenTerm50(self):
        self.Tester(self.id(),'relay',2,default='0',term='50.')
    def testRelay2ClosedTerm50(self):
        self.Tester(self.id(),'relay',2,default='1',term='50.')
    def testRelay3Pos0(self):
        self.Tester(self.id(),'relay',3,default='0',term='50.')
    def testRelay3Pos1(self):
        self.Tester(self.id(),'relay',3,default='1',term='50.')
    def testRelay3Pos2(self):
        self.Tester(self.id(),'relay',3,default='2',term='50.')
    def testlen(self):
        L=len(si.p.dev.DeviceFactory())
        self.assertEqual(L,62)
    def testMakeDeviceNoArgs(self):
        df=si.p.dev.DeviceFactory()
        self.assertFalse(df.MakeDevice(2,None,[],[1,2,3]))
    def testMakeDeviceArgs(self):
        df=si.p.dev.DeviceFactory()
        self.assertTrue(df.MakeDevice(2,None,['r','50.'],[1,2,3]))

if __name__ == '__main__':
    unittest.main()
