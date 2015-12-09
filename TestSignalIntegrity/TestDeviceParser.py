#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      peter.pupalaikis
#
# Created:     09/12/2015
# Copyright:   (c) peter.pupalaikis 2015
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import unittest

from TestHelpers import *

import SignalIntegrity as si

class TestDeviceParser(unittest.TestCase,ResponseTesterHelper):
    def __init__(self, methodName='runTest'):
        unittest.TestCase.__init__(self,methodName)
    def Tester(self,idName,deviceName,ports,**args):
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
        self.CheckSParametersResult(sp,spFileName,spFileName+' incorrect')
    def testFile(self):
        self.Tester(self.id(),'file',2,default='filter.s2p')
    def testFileNotFound(self):
        with self.assertRaises(si.PySIException) as cm:
            self.Tester(self.id(),'file',2,default='filterNonExistent.s2p')
        self.assertEqual(cm.exception.parameter,'DeviceParser')
    def testTerminationC(self):
        self.Tester(self.id(),'C',1,default='100e-12')
    def testSeriesC(self):
        self.Tester(self.id(),'C',2,default='100e-12')
    def testSeriesCExtraArguments(self):
        with self.assertRaises(si.PySIException) as cm:
            self.Tester(self.id(),'C',2,default='100e-12',extra='whattheheck')
        self.assertEqual(cm.exception.parameter,'DeviceParser')
    def testCWrongPorts(self):
        with self.assertRaises(si.PySIException) as cm:
            self.Tester(self.id(),'c',3,default='100e-12')
        self.assertEqual(cm.exception.parameter,'DeviceParser')
    def testTerminationL(self):
        self.Tester(self.id(),'L',1,default='100e-9')
    def testSeriesL(self):
        self.Tester(self.id(),'L',2,default='100e-9')
    def testLWrongPorts(self):
        with self.assertRaises(si.PySIException) as cm:
            self.Tester(self.id(),'L',3,default='100e-9')
        self.assertEqual(cm.exception.parameter,'DeviceParser')
    def testTerminationR(self):
        self.Tester(self.id(),'R',1,default='50.')
    def testSeriesR(self):
        self.Tester(self.id(),'R',2,default='50.')
    def testRWrongPorts(self):
        with self.assertRaises(si.PySIException) as cm:
            self.Tester(self.id(),'R',3,default='50.')
        self.assertEqual(cm.exception.parameter,'DeviceParser')
    def testShunt2(self):
        self.Tester(self.id(),'shunt',2,default='100.')
    def testShunt3(self):
        self.Tester(self.id(),'shunt',3,default='100.')
    def testShunt4(self):
        self.Tester(self.id(),'shunt',4,default='100.')
    def testShunt5(self):
        with self.assertRaises(si.PySIException) as cm:
            self.Tester(self.id(),'shunt',5,default='100.')
        self.assertEqual(cm.exception.parameter,'DeviceParser')
    def testMutual(self):
        self.Tester(self.id(),'M',4,default='100e-9')
    def testGround(self):
        self.Tester(self.id(),'ground',1)
    def testGroundWrongPorts(self):
        with self.assertRaises(si.PySIException) as cm:
            self.Tester(self.id(),'ground',2)
        self.assertEqual(cm.exception.parameter,'DeviceParser')
    def testOpen(self):
        self.Tester(self.id(),'open',1)
    def testThruWrongPorts(self):
        with self.assertRaises(si.PySIException) as cm:
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
        with self.assertRaises(si.PySIException) as cm:
            self.Tester(self.id(),'voltagecontrolledvoltagesource',4)
        self.assertEqual(cm.exception.parameter,'DeviceParser')
    def testVoltageControlledVoltageSourceGainDefault(self):
        self.Tester(self.id(),'voltagecontrolledvoltagesource',4,default='1.')
    def testVoltageControlledCurrentSourceNoGain(self):
        with self.assertRaises(si.PySIException) as cm:
            self.Tester(self.id(),'voltagecontrolledcurrentsource',4)
        self.assertEqual(cm.exception.parameter,'DeviceParser')
    def testVoltageControlledCurrentSourceGainDefault(self):
        self.Tester(self.id(),'voltagecontrolledcurrentsource',4,default='1.')
    def testCurrentControlledCurrentSourceNoGain(self):
        with self.assertRaises(si.PySIException) as cm:
            self.Tester(self.id(),'currentcontrolledcurrentsource',4)
        self.assertEqual(cm.exception.parameter,'DeviceParser')
    def testCurrentControlledCurrentSourceGainDefault(self):
        self.Tester(self.id(),'currentcontrolledcurrentsource',4,default='1.')
    def testCurrentControlledVoltageSourceNoGain(self):
        with self.assertRaises(si.PySIException) as cm:
            self.Tester(self.id(),'currentcontrolledvoltagesource',4)
        self.assertEqual(cm.exception.parameter,'DeviceParser')
    def testCurrentControlledVoltageSourceGainDefault(self):
        self.Tester(self.id(),'currentcontrolledvoltagesource',4,default='1.')
    def testVoltageAmplifierNoGain1(self):
        with self.assertRaises(si.PySIException) as cm:
            self.Tester(self.id(),'voltageamplifier',1)
        self.assertEqual(cm.exception.parameter,'DeviceParser')
    def testVoltageAmplifierGainDefault1(self):
        with self.assertRaises(si.PySIException) as cm:
            self.Tester(self.id(),'voltageamplifier',1,default='1.')
        self.assertEqual(cm.exception.parameter,'DeviceParser')
    def testVoltageAmplifierGain1(self):
        with self.assertRaises(si.PySIException) as cm:
            self.Tester(self.id(),'voltageamplifier',1,gain='1.')
        self.assertEqual(cm.exception.parameter,'DeviceParser')
    def testVoltageAmplifierNoGain2(self):
        with self.assertRaises(si.PySIException) as cm:
            self.Tester(self.id(),'voltageamplifier',2)
        self.assertEqual(cm.exception.parameter,'DeviceParser')
    def testVoltageAmplifierGainDefault2(self):
        with self.assertRaises(si.PySIException) as cm:
            self.Tester(self.id(),'voltageamplifier',2,default='1.')
        self.assertEqual(cm.exception.parameter,'DeviceParser')
    def testVoltageAmplifierGain2(self):
        self.Tester(self.id(),'voltageamplifier',2,gain='1.')
    def testVoltageAmplifierNoGain3(self):
        with self.assertRaises(si.PySIException) as cm:
            self.Tester(self.id(),'voltageamplifier',3)
        self.assertEqual(cm.exception.parameter,'DeviceParser')
    def testVoltageAmplifierGainDefault3(self):
        with self.assertRaises(si.PySIException) as cm:
            self.Tester(self.id(),'voltageamplifier',3,default='1.')
        self.assertEqual(cm.exception.parameter,'DeviceParser')
    def testVoltageAmplifierGain3(self):
        self.Tester(self.id(),'voltageamplifier',3,gain='1.')
    def testVoltageAmplifierNoGain4(self):
        with self.assertRaises(si.PySIException) as cm:
            self.Tester(self.id(),'voltageamplifier',4)
        self.assertEqual(cm.exception.parameter,'DeviceParser')
    def testVoltageAmplifierGainDefault4(self):
        with self.assertRaises(si.PySIException) as cm:
            self.Tester(self.id(),'voltageamplifier',4,default='1.')
        self.assertEqual(cm.exception.parameter,'DeviceParser')
    def testVoltageAmplifierGain4(self):
        self.Tester(self.id(),'voltageamplifier',4,gain='1.')
    def testVoltageAmplifierNoGain5(self):
        with self.assertRaises(si.PySIException) as cm:
            self.Tester(self.id(),'voltageamplifier',5)
        self.assertEqual(cm.exception.parameter,'DeviceParser')
    def testVoltageAmplifierGainDefault5(self):
        with self.assertRaises(si.PySIException) as cm:
            self.Tester(self.id(),'voltageamplifier',5,default='5.')
        self.assertEqual(cm.exception.parameter,'DeviceParser')
    def testVoltageAmplifierGain5(self):
        with self.assertRaises(si.PySIException) as cm:
            self.Tester(self.id(),'voltageamplifier',5,gain='5.')
        self.assertEqual(cm.exception.parameter,'DeviceParser')
    def testCurrentAmplifierNoGain1(self):
        with self.assertRaises(si.PySIException) as cm:
            self.Tester(self.id(),'currentamplifier',1)
        self.assertEqual(cm.exception.parameter,'DeviceParser')
    def testCurrentAmplifierGainDefault1(self):
        with self.assertRaises(si.PySIException) as cm:
            self.Tester(self.id(),'currentamplifier',1,default='1.')
        self.assertEqual(cm.exception.parameter,'DeviceParser')
    def testCurrentAmplifierGain1(self):
        with self.assertRaises(si.PySIException) as cm:
            self.Tester(self.id(),'currentamplifier',1,gain='1.')
        self.assertEqual(cm.exception.parameter,'DeviceParser')
    def testCurrentAmplifierNoGain2(self):
        with self.assertRaises(si.PySIException) as cm:
            self.Tester(self.id(),'currentamplifier',2)
        self.assertEqual(cm.exception.parameter,'DeviceParser')
    def testCurrentAmplifierGainDefault2(self):
        with self.assertRaises(si.PySIException) as cm:
            self.Tester(self.id(),'currentamplifier',2,default='1.')
        self.assertEqual(cm.exception.parameter,'DeviceParser')
    def testCurrentAmplifierGain2(self):
        self.Tester(self.id(),'currentamplifier',2,gain='1.')
    def testCurrentAmplifierNoGain3(self):
        with self.assertRaises(si.PySIException) as cm:
            self.Tester(self.id(),'currentamplifier',3)
        self.assertEqual(cm.exception.parameter,'DeviceParser')
    def testCurrentAmplifierGainDefault3(self):
        with self.assertRaises(si.PySIException) as cm:
            self.Tester(self.id(),'currentamplifier',3,default='1.')
        self.assertEqual(cm.exception.parameter,'DeviceParser')
    def testCurrentAmplifierGain3(self):
        self.Tester(self.id(),'currentamplifier',3,gain='1.')
    def testCurrentAmplifierNoGain4(self):
        with self.assertRaises(si.PySIException) as cm:
            self.Tester(self.id(),'currentamplifier',4)
        self.assertEqual(cm.exception.parameter,'DeviceParser')
    def testCurrentAmplifierGainDefault4(self):
        with self.assertRaises(si.PySIException) as cm:
            self.Tester(self.id(),'currentamplifier',4,default='1.')
        self.assertEqual(cm.exception.parameter,'DeviceParser')
    def testCurrentAmplifierGain4(self):
        self.Tester(self.id(),'currentamplifier',4,gain='1.')
    def testCurrentAmplifierNoGain5(self):
        with self.assertRaises(si.PySIException) as cm:
            self.Tester(self.id(),'currentamplifier',5)
        self.assertEqual(cm.exception.parameter,'DeviceParser')
    def testCurrentAmplifierGainDefault5(self):
        with self.assertRaises(si.PySIException) as cm:
            self.Tester(self.id(),'currentamplifier',5,default='5.')
        self.assertEqual(cm.exception.parameter,'DeviceParser')
    def testCurrentAmplifierGain5(self):
        with self.assertRaises(si.PySIException) as cm:
            self.Tester(self.id(),'currentamplifier',5,gain='5.')
        self.assertEqual(cm.exception.parameter,'DeviceParser')
    def testTransresistanceAmplifierNoGain1(self):
        with self.assertRaises(si.PySIException) as cm:
            self.Tester(self.id(),'transresistanceamplifier',1)
        self.assertEqual(cm.exception.parameter,'DeviceParser')
    def testTransresistanceAmplifierGainDefault1(self):
        with self.assertRaises(si.PySIException) as cm:
            self.Tester(self.id(),'transresistanceamplifier',1,default='1.')
        self.assertEqual(cm.exception.parameter,'DeviceParser')
    def testTransresistanceAmplifierGain1(self):
        with self.assertRaises(si.PySIException) as cm:
            self.Tester(self.id(),'transresistanceamplifier',1,gain='1.')
        self.assertEqual(cm.exception.parameter,'DeviceParser')
    def testTransresistanceAmplifierNoGain2(self):
        with self.assertRaises(si.PySIException) as cm:
            self.Tester(self.id(),'transresistanceamplifier',2)
        self.assertEqual(cm.exception.parameter,'DeviceParser')
    def testTransresistanceAmplifierGainDefault2(self):
        with self.assertRaises(si.PySIException) as cm:
            self.Tester(self.id(),'transresistanceamplifier',2,default='1.')
        self.assertEqual(cm.exception.parameter,'DeviceParser')
    def testTransresistanceAmplifierGain2(self):
        self.Tester(self.id(),'transresistanceamplifier',2,gain='1.')
    def testTransresistanceAmplifierNoGain3(self):
        with self.assertRaises(si.PySIException) as cm:
            self.Tester(self.id(),'transresistanceamplifier',3)
        self.assertEqual(cm.exception.parameter,'DeviceParser')
    def testTransresistanceAmplifierGainDefault3(self):
        with self.assertRaises(si.PySIException) as cm:
            self.Tester(self.id(),'transresistanceamplifier',3,default='1.')
        self.assertEqual(cm.exception.parameter,'DeviceParser')
    def testTransresistanceAmplifierGain3(self):
        self.Tester(self.id(),'transresistanceamplifier',3,gain='1.')
    def testTransresistanceAmplifierNoGain4(self):
        with self.assertRaises(si.PySIException) as cm:
            self.Tester(self.id(),'transresistanceamplifier',4)
        self.assertEqual(cm.exception.parameter,'DeviceParser')
    def testTransresistanceAmplifierGainDefault4(self):
        with self.assertRaises(si.PySIException) as cm:
            self.Tester(self.id(),'transresistanceamplifier',4,default='1.')
        self.assertEqual(cm.exception.parameter,'DeviceParser')
    def testTransresistanceAmplifierGain4(self):
        self.Tester(self.id(),'transresistanceamplifier',4,gain='1.')
    def testTransresistanceAmplifierNoGain5(self):
        with self.assertRaises(si.PySIException) as cm:
            self.Tester(self.id(),'transresistanceamplifier',5)
        self.assertEqual(cm.exception.parameter,'DeviceParser')
    def testTransresistanceAmplifierGainDefault5(self):
        with self.assertRaises(si.PySIException) as cm:
            self.Tester(self.id(),'transresistanceamplifier',5,default='5.')
        self.assertEqual(cm.exception.parameter,'DeviceParser')
    def testTransresistanceAmplifierGain5(self):
        with self.assertRaises(si.PySIException) as cm:
            self.Tester(self.id(),'transresistanceamplifier',5,gain='5.')
        self.assertEqual(cm.exception.parameter,'DeviceParser')
    def testTransconductanceAmplifierNoGain1(self):
        with self.assertRaises(si.PySIException) as cm:
            self.Tester(self.id(),'transconductanceamplifier',1)
        self.assertEqual(cm.exception.parameter,'DeviceParser')
    def testTransconductanceAmplifierGainDefault1(self):
        with self.assertRaises(si.PySIException) as cm:
            self.Tester(self.id(),'transconductanceamplifier',1,default='1.')
        self.assertEqual(cm.exception.parameter,'DeviceParser')
    def testTransconductanceAmplifierGain1(self):
        with self.assertRaises(si.PySIException) as cm:
            self.Tester(self.id(),'transconductanceamplifier',1,gain='1.')
        self.assertEqual(cm.exception.parameter,'DeviceParser')
    def testTransconductanceAmplifierNoGain2(self):
        with self.assertRaises(si.PySIException) as cm:
            self.Tester(self.id(),'transconductanceamplifier',2)
        self.assertEqual(cm.exception.parameter,'DeviceParser')
    def testTransconductanceAmplifierGainDefault2(self):
        with self.assertRaises(si.PySIException) as cm:
            self.Tester(self.id(),'transconductanceamplifier',2,default='1.')
        self.assertEqual(cm.exception.parameter,'DeviceParser')
    def testTransconductanceAmplifierGain2(self):
        self.Tester(self.id(),'transconductanceamplifier',2,gain='1.')
    def testTransconductanceAmplifierNoGain3(self):
        with self.assertRaises(si.PySIException) as cm:
            self.Tester(self.id(),'transconductanceamplifier',3)
        self.assertEqual(cm.exception.parameter,'DeviceParser')
    def testTransconductanceAmplifierGainDefault3(self):
        with self.assertRaises(si.PySIException) as cm:
            self.Tester(self.id(),'transconductanceamplifier',3,default='1.')
        self.assertEqual(cm.exception.parameter,'DeviceParser')
    def testTransconductanceAmplifierGain3(self):
        self.Tester(self.id(),'transconductanceamplifier',3,gain='1.')
    def testTransconductanceAmplifierNoGain4(self):
        with self.assertRaises(si.PySIException) as cm:
            self.Tester(self.id(),'transconductanceamplifier',4)
        self.assertEqual(cm.exception.parameter,'DeviceParser')
    def testTransconductanceAmplifierGainDefault4(self):
        with self.assertRaises(si.PySIException) as cm:
            self.Tester(self.id(),'transconductanceamplifier',4,default='1.')
        self.assertEqual(cm.exception.parameter,'DeviceParser')
    def testTransconductanceAmplifierGain4(self):
        self.Tester(self.id(),'transconductanceamplifier',4,gain='1.')
    def testTransconductanceAmplifierNoGain5(self):
        with self.assertRaises(si.PySIException) as cm:
            self.Tester(self.id(),'transconductanceamplifier',5)
        self.assertEqual(cm.exception.parameter,'DeviceParser')
    def testTransconductanceAmplifierGainDefault5(self):
        with self.assertRaises(si.PySIException) as cm:
            self.Tester(self.id(),'transconductanceamplifier',5,default='5.')
        self.assertEqual(cm.exception.parameter,'DeviceParser')
    def testTransconductanceAmplifierGain5(self):
        with self.assertRaises(si.PySIException) as cm:
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
    def testTelegrapher2Default(self):
        self.Tester(self.id(),'telegrapher',2)
    def testTelegrapher2LC(self):
        self.Tester(self.id(),'telegrapher',2,c='20e-12',l='50e-9',sect='10000')
    def testTelegrapher4Default(self):
        self.Tester(self.id(),'telegrapher',4)
    def testTelegrapher4LC(self):
        self.Tester(self.id(),'telegrapher',4,lp='58.5e-9',cp='20e-12',ln='58.5e-9',cn='20e-12',lm='13.5e-9',cm='1.111e-12',sect='10000')
    def testlen(self):
        L=len(si.p.dev.DeviceFactory())
        self.assertEqual(L,27)
    def testMakeDeviceNoArgs(self):
        df=si.p.dev.DeviceFactory()
        self.assertFalse(df.MakeDevice(2,[],[1,2,3]))
    def testMakeDeviceArgs(self):
        df=si.p.dev.DeviceFactory()
        self.assertTrue(df.MakeDevice(2,['r','50.'],[1,2,3]))

if __name__ == '__main__':
    unittest.main()
