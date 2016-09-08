import unittest
import SignalIntegrity as si
import math
import os
from TestHelpers import SParameterCompareHelper
from TestHelpers import CallbackTesterHelper

class TestSParameterFile(unittest.TestCase,SParameterCompareHelper,CallbackTesterHelper):
    def __init__(self, methodName='runTest'):
        CallbackTesterHelper.__init__(self)
        unittest.TestCase.__init__(self,methodName)

    def testSParameterFileFourPort(self):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        sf=si.sp.SParameterFile('TestDut.s4p',50.)
        #f=[i*100e6 for i in range(201)]
        #sf.Resample(f)
        #sf.WriteToFile('TestDut.s4p')
        f=sf.f()
        """
        import matplotlib.pyplot as plt
        for r in range(4):
            for c in range(4):
                responseVector=sf.Response(r+1,c+1)
                y=[20*math.log(abs(resp),10) for resp in responseVector]
                plt.subplot(4,4,r*4+c+1)
                plt.plot(f,y)
        plt.show()
        """
        # this is to test reading and writing, but also to ensure that
        # WriteToFile is always executed and covered
        sf.WriteToFile('TestDutCmp.s4p')
        sf2=si.sp.SParameterFile('TestDutCmp.s4p',50.)
        os.remove('TestDutCmp.s4p')
        self.assertTrue(self.SParametersAreEqual(sf2,sf,0.001),self.id()+'result not same')
    def testSParameterFileFourPortHzMA(self):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        sf=si.sp.SParameterFile('TestDut.s4p',50.)
        f=sf.f()
        """
        import matplotlib.pyplot as plt
        for r in range(4):
            for c in range(4):
                responseVector=sf.Response(r+1,c+1)
                y=[20*math.log(abs(resp),10) for resp in responseVector]
                plt.subplot(4,4,r*4+c+1)
                plt.plot(f,y)
        plt.show()
        """
        # this is to test reading and writing, but also to ensure that
        # WriteToFile is always executed and covered
        sf.WriteToFile('TestDutCmp.s4p','Hz MA')
        sf2=si.sp.SParameterFile('TestDutCmp.s4p',50.)
        os.remove('TestDutCmp.s4p')
        self.assertTrue(self.SParametersAreEqual(sf2,sf,0.001),self.id()+'result not same')
    def testSParameterFileFourPortKHzRI(self):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        sf=si.sp.SParameterFile('TestDut.s4p',50.)
        f=sf.f()
        """
        import matplotlib.pyplot as plt
        for r in range(4):
            for c in range(4):
                responseVector=sf.Response(r+1,c+1)
                y=[20*math.log(abs(resp),10) for resp in responseVector]
                plt.subplot(4,4,r*4+c+1)
                plt.plot(f,y)
        plt.show()
        """
        # this is to test reading and writing, but also to ensure that
        # WriteToFile is always executed and covered
        sf.WriteToFile('TestDutCmp.s4p','KHz RI')
        sf2=si.sp.SParameterFile('TestDutCmp.s4p',50.)
        os.remove('TestDutCmp.s4p')
        self.assertTrue(self.SParametersAreEqual(sf2,sf,0.001),self.id()+'result not same')
    def testSParameterFileFourPortMHzDB(self):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        sf=si.sp.SParameterFile('TestDut.s4p',50.)
        f=sf.f()
        """
        import matplotlib.pyplot as plt
        for r in range(4):
            for c in range(4):
                responseVector=sf.Response(r+1,c+1)
                y=[20*math.log(abs(resp),10) for resp in responseVector]
                plt.subplot(4,4,r*4+c+1)
                plt.plot(f,y)
        plt.show()
        """
        # this is to test reading and writing, but also to ensure that
        # WriteToFile is always executed and covered
        sf.WriteToFile('TestDutCmp.s4p','MHz DB')
        sf2=si.sp.SParameterFile('TestDutCmp.s4p',50.)
        os.remove('TestDutCmp.s4p')
        self.assertTrue(self.SParametersAreEqual(sf2,sf,0.001),self.id()+'result not same')
    def testSParameterFileFourPortGHzMA(self):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        sf=si.sp.SParameterFile('TestDut.s4p',50.)
        f=sf.f()
        """
        import matplotlib.pyplot as plt
        for r in range(4):
            for c in range(4):
                responseVector=sf.Response(r+1,c+1)
                y=[20*math.log(abs(resp),10) for resp in responseVector]
                plt.subplot(4,4,r*4+c+1)
                plt.plot(f,y)
        plt.show()
        """
        # this is to test reading and writing, but also to ensure that
        # WriteToFile is always executed and covered
        sf.WriteToFile('TestDutCmp.s4p','GHz MA')
        sf2=si.sp.SParameterFile('TestDutCmp.s4p',50.)
        os.remove('TestDutCmp.s4p')
        self.assertTrue(self.SParametersAreEqual(sf2,sf,0.001),self.id()+'result not same')
    def testSParameterFileFourPortNon50Write(self):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        sf=si.sp.SParameterFile('TestDut.s4p',50.)
        f=sf.f()
        """
        import matplotlib.pyplot as plt
        for r in range(4):
            for c in range(4):
                responseVector=sf.Response(r+1,c+1)
                y=[20*math.log(abs(resp),10) for resp in responseVector]
                plt.subplot(4,4,r*4+c+1)
                plt.plot(f,y)
        plt.show()
        """
        # this is to test reading and writing, but also to ensure that
        # WriteToFile is always executed and covered
        sf.WriteToFile('TestDutCmp.s4p','r 40')
        sf2=si.sp.SParameterFile('TestDutCmp.s4p',50.)
        os.remove('TestDutCmp.s4p')
        self.assertTrue(self.SParametersAreEqual(sf2,sf,0.001),self.id()+'result not same')
    def testSParameterFileFourPortNon50Read(self):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        sf=si.sp.SParameterFile('TestDut.s4p',Z0=40)
        f=sf.f()
        """
        import matplotlib.pyplot as plt
        for r in range(4):
            for c in range(4):
                responseVector=sf.Response(r+1,c+1)
                y=[20*math.log(abs(resp),10) for resp in responseVector]
                plt.subplot(4,4,r*4+c+1)
                plt.plot(f,y)
        plt.show()
        """
        # this is to test reading and writing, but also to ensure that
        # WriteToFile is always executed and covered
        sf.WriteToFile('TestDutCmp.s4p')
        sf2=si.sp.SParameterFile('TestDutCmp.s4p',Z0=40)
        os.remove('TestDutCmp.s4p')
        self.assertTrue(self.SParametersAreEqual(sf2,sf,0.001),self.id()+'result not same')
    def testSParameterFileFourPortNoSRead(self):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        sf=si.sp.SParameterFile('TestDut.s4p',50.)
        sf.m_sToken='Z' #switch the internal token to Z parameters to make them faulty
        sf.WriteToFile('TestDutCmp.s4p')
        sf2=si.sp.SParameterFile('TestDutCmp.s4p',50.)
        os.remove('TestDutCmp.s4p')
        self.assertTrue(len(sf2)==0,self.id()+'result not same')
    def testSParameterFileFourPortNonExistant(self):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        try:
            sf=si.sp.SParameterFile('TestDutcmp.s4p',50.)
        except si.PySIException as e:
            if e.parameter == 'SParameterFile':
                return
        self.fail(self.id()+'result not same')
    def testSParameterFileTwoPort(self):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        sf=si.sp.SParameterFile('cable.s2p',50.)
        f=sf.f()
        #f=[i*100e6 for i in range(201)]
        #sf2=sf
        #sf2.Resample(f)
        #sf2.WriteToFile('cable2.s2p')
        """
        import matplotlib.pyplot as plt
        for r in range(4):
            for c in range(4):
                responseVector=sf.Response(r+1,c+1)
                y=[20*math.log(abs(resp),10) for resp in responseVector]
                plt.subplot(4,4,r*4+c+1)
                plt.plot(f,y)
        plt.show()
        """
        # this is to test reading and writing, but also to ensure that
        # WriteToFile is always executed and covered
        sf.WriteToFile('cableCmp.s2p')
        sf2=si.sp.SParameterFile('cableCmp.s2p',50.)
        os.remove('cableCmp.s2p')
        self.assertTrue(self.SParametersAreEqual(sf2,sf,0.001),self.id()+'result not same')
    def testRLC(self):
        L1=1e-15
        C1=1e-9
        L2=1e-15
        freq=[100e6*(i+1) for i in range(100)]
        spc=[]
        spc.append(('L1',[si.dev.SeriesZ(1j*2.*math.pi*f*L1) for f in freq]))
        spc.append(('C1',[si.dev.SeriesZ(1./(1j*2.*math.pi*C1*f)) for f in freq]))
        spc.append(('L2',[si.dev.SeriesZ(1j*2.*math.pi*f*L2) for f in freq]))
        SD=si.sd.SystemDescription()
        SD.AddDevice('L1',2)
        SD.AddDevice('L2',2)
        SD.AddDevice('C1',2)
        SD.AddDevice('G',1,si.dev.Ground())
        SD.AddPort('L1',1,1)
        SD.AddPort('L2',2,2)
        SD.ConnectDevicePort('L1',2,'L2',1)
        SD.ConnectDevicePort('L1',2,'C1',1)
        SD.ConnectDevicePort('C1',2,'G',1)
        result=[]
        for n in range(len(freq)):
            for d in range(len(spc)):
                SD.AssignSParameters(spc[d][0],spc[d][1][n])
            result.append(si.sd.SystemSParametersNumeric(SD).SParameters())
        sf=si.sp.SParameters(freq,result)
        fileName='_'.join(self.id().split('.'))+'.s'+str(sf.m_P)+'p'
        if not os.path.exists(fileName):
            sf.WriteToFile('_'.join(self.id().split('.'))+'.s'+str(sf.m_P)+'p')
            self.assertTrue(False,fileName + 'does not exist')
        regression = si.sp.SParameterFile(fileName,50.)
        self.assertTrue(self.SParametersAreEqual(sf,regression,0.001),self.id()+'result not same')
        """
        import matplotlib.pyplot as plt
        f=sf.f()
        for r in range(2):
            for c in range(2):
                responseVector=sf.Response(r+1,c+1)
                y=[20*math.log(abs(resp),10) for resp in responseVector]
                plt.subplot(2,2,r*2+c+1)
                plt.plot(f,y)
        plt.show()
        """
    def testRLC2(self):
        L1=1e-15
        C1=1e-9
        L2=1e-15
        freq=[100e6*(i+1) for i in range(100)]
        spc=[]
        spc.append(('L1',si.sp.dev.SeriesL(freq,L1)))
        spc.append(('C1',si.sp.dev.SeriesC(freq,C1)))
        spc.append(('L2',si.sp.dev.SeriesL(freq,L2)))
        SD=si.sd.SystemDescription()
        SD.AddDevice('L1',2)
        SD.AddDevice('L2',2)
        SD.AddDevice('C1',2)
        SD.AddDevice('G',1,si.dev.Ground())
        SD.AddPort('L1',1,1)
        SD.AddPort('L2',2,2)
        SD.ConnectDevicePort('L1',2,'L2',1)
        SD.ConnectDevicePort('L1',2,'C1',1)
        SD.ConnectDevicePort('C1',2,'G',1)
        result=[]
        for n in range(len(freq)):
            for d in range(len(spc)):
                SD.AssignSParameters(spc[d][0],spc[d][1][n])
            result.append(si.sd.SystemSParametersNumeric(SD).SParameters())
        sf=si.sp.SParameters(freq,result)
        fileName='_'.join(self.id().split('.'))+'.s'+str(sf.m_P)+'p'
        if not os.path.exists(fileName):
            sf.WriteToFile('_'.join(self.id().split('.'))+'.s'+str(sf.m_P)+'p')
            self.assertTrue(False,fileName + 'does not exist')
        regression = si.sp.SParameterFile(fileName,50.)
        self.assertTrue(self.SParametersAreEqual(sf,regression,0.001),self.id()+'result not same')
        """
        import matplotlib.pyplot as plt
        f=sf.f()
        for r in range(2):
            for c in range(2):
                responseVector=sf.Response(r+1,c+1)
                y=[20*math.log(abs(resp),10) for resp in responseVector]
                plt.subplot(2,2,r*2+c+1)
                plt.plot(f,y)
        plt.show()
        """
    def testRes(self):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        newf=si.fd.EvenlySpacedFrequencyList(10e9,100)
        #newf=[100e6*n for n in range(100)]
        sf=si.sp.SParameterFile('TestDut.s4p',50.).Resample(si.fd.EvenlySpacedFrequencyList(10e9,10))
        sf2=si.sp.SParameterFile('TestDut.s4p',50.).Resample(si.fd.EvenlySpacedFrequencyList(10e9,10)).Resample(newf)
        if not os.path.exists('Test1.s4p'):
            sf.WriteToFile('Test1.s4p')
            self.assertTrue(False,'Test1.s4p' + ' does not exist')
        if not os.path.exists('Test2.s4p'):
            sf2.WriteToFile('Test2.s4p')
            self.assertTrue(False,'Test2.s4p' + ' does not exist')

        """
        import matplotlib.pyplot as plt
        f=sf.f()
        f2=sf2.f()
        plt.clf()
        for r in range(4):
            for c in range(4):
                plt.subplot(4,4,r*4+c+1)
                sffr=si.fd.FrequencyResponse(sf.f(),sf.Response(r+1,c+1))
                plt.plot(sffr.Frequencies(),sffr.Response('dB'),label='downsampled')
                sf2fr=si.fd.FrequencyResponse(sf2.f(),sf2.Response(r+1,c+1))
                plt.plot(sf2fr.Frequencies(),sf2fr.Response('dB'),label='upsampled')
                originalsp=si.sp.SParameterFile('TestDut.s4p',50.)
                originalFr=si.fd.FrequencyResponse(originalsp.f(),originalsp.Response(r+1, c+1))
                plt.plot(originalFr.Frequencies(),originalFr.Response('dB'),label='original')
        plt.show()
        """

        regression = si.sp.SParameterFile('Test1.s4p',50.)
        self.assertTrue(self.SParametersAreEqual(sf,regression,0.001),self.id()+'first result not same')
        regression = si.sp.SParameterFile('Test2.s4p',50.)
        self.assertTrue(self.SParametersAreEqual(sf2,regression,0.001),self.id()+'second result not same')

    def testRLC3(self):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        L1=1e-15
        C1=10e-12
        L2=1e-15
        freq=[10e6*i for i in range(1001)]
        spc=[]
        spc.append(('L1',si.sp.dev.SeriesL(freq,L1)))
        spc.append(('C1',si.sp.dev.SeriesC(freq,C1)))
        spc.append(('L2',si.sp.dev.SeriesL(freq,L2)))
        spc.append(('D1',si.sp.SParameterFile('TestDut.s4p',50.).Resample(freq)))
        SD=si.sd.SystemDescription()
        SD.AddDevice('D1',4)
        SD.AddDevice('L1',2)
        SD.AddDevice('L2',2)
        SD.AddDevice('C1',2)
        SD.AddDevice('G',1,si.dev.Ground())
        SD.AddPort('D1',1,1)
        SD.AddPort('D1',2,2)
        SD.AddPort('D1',3,3)
        SD.ConnectDevicePort('L1',2,'L2',1)
        SD.ConnectDevicePort('L1',2,'C1',1)
        SD.ConnectDevicePort('C1',2,'G',1)
        SD.ConnectDevicePort('D1',4,'L1',1)
        SD.AddPort('L2',2,4)
        result=[]
        for n in range(len(freq)):
            for d in range(len(spc)):
                SD.AssignSParameters(spc[d][0],spc[d][1][n])
            result.append(si.sd.SystemSParametersNumeric(SD).SParameters())
        sf=si.sp.SParameters(freq,result)
        fileName='_'.join(self.id().split('.'))+'.s'+str(sf.m_P)+'p'
        if not os.path.exists(fileName):
            sf.WriteToFile('_'.join(self.id().split('.'))+'.s'+str(sf.m_P)+'p')
            self.assertTrue(False,fileName + 'does not exist')
        regression = si.sp.SParameterFile(fileName,50.)
        """
        import matplotlib.pyplot as plt
        for r in range(2):
            for c in range(2):
                plt.subplot(2,2,r*2+c+1)
                currentFr=si.fd.FrequencyResponse(sf.f(),sf.Response(r+1,c+1))
                plt.plot(currentFr.Frequencies(),currentFr.Response('dB'),label='current')
                regressionFr=si.fd.FrequencyResponse(regression.f(),regression.Response(r+1, c+1))
                plt.plot(regressionFr.Frequencies(),regressionFr.Response('dB'),label='regression')
                plt.legend(loc='upper right')
        plt.show()

        plt.clf()
        for r in range(2):
            for c in range(2):
                plt.subplot(2,2,r*2+c+1)
                currentFr=si.fd.FrequencyResponse(sf.f(),sf.Response(r+1,c+1))
                plt.plot(currentFr.Frequencies(),currentFr.Response('deg'),label='current')
                regressionFr=si.fd.FrequencyResponse(regression.f(),regression.Response(r+1, c+1))
                plt.plot(regressionFr.Frequencies(),regressionFr.Response('deg'),label='regression')
                plt.legend(loc='upper right')
        plt.show()
        """
        self.assertTrue(self.SParametersAreEqual(sf,regression,0.001),self.id()+'result not same')

    def testRLC4(self):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        freq=[10e6*i for i in range(1001)]
        parser=si.p.SystemSParametersNumericParser(freq)
        parser.AddLine('device L1 2 L 1e-15')
        parser.AddLine('device C1 2 C 10e-12')
        parser.AddLine('device L2 2 L 1e-15')
        parser.AddLine('device D1 4 file TestDut.s4p')
        parser.AddLine('device G 1 ground')
        parser.AddLine('port 1 D1 1 2 D1 2 3 D1 3 4 L2 2')
        parser.AddLine('connect L1 2 L2 1 C1 1')
        parser.AddLine('connect C1 2 G 1')
        parser.AddLine('connect D1 4 L1 1')
        sf=si.sp.SParameters(freq,parser.SParameters())
        fileName='_'.join(self.id().split('.'))+'.s'+str(sf.m_P)+'p'
        if not os.path.exists(fileName):
            sf.WriteToFile('_'.join(self.id().split('.'))+'.s'+str(sf.m_P)+'p')
            self.assertTrue(False,fileName + 'does not exist')
        regression = si.sp.SParameterFile(fileName,50.)
        regression = si.sp.SParameterFile('_'.join(self.id().split('.'))+'.s'+str(sf.m_P)+'p',50.)
        self.assertTrue(self.SParametersAreEqual(sf,regression,0.001),self.id()+'result not same')
        """
        import matplotlib.pyplot as plt
        f=sf.f()
        for r in range(2):
            for c in range(2):
                responseVector=sf.Response(r+1,c+1)
                y=[20*math.log(abs(resp),10) for resp in responseVector]
                plt.subplot(2,2,r*2+c+1)
                plt.plot(f,y)
        plt.show()
        """
    def testRLC5(self):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        freq=[10e6*i for i in range(1001)]
        parser=si.p.SystemSParametersNumericParser(freq,'Lleft 1e-15 Cshunt 10e-12 Lright 1e-15')
        parser.AddLine('var $Lleft$ x $Cshunt$ x $Lright$ x')
        parser.AddLine('device L1 2 L $Lleft$')
        parser.AddLine('device C1 2 C $Cshunt$')
        parser.AddLine('device L2 2 L $Lright$')
        parser.AddLine('device D1 4 file TestDut.s4p')
        parser.AddLine('device G 1 ground')
        parser.AddLine('port 1 D1 1 2 D1 2 3 D1 3 4 L2 2')
        parser.AddLine('connect L1 2 L2 1 C1 1')
        parser.AddLine('connect C1 2 G 1')
        parser.AddLine('connect D1 4 L1 1')
        sf=si.sp.SParameters(freq,parser.SParameters())
        fileName='_'.join(self.id().split('.'))+'.s'+str(sf.m_P)+'p'
        if not os.path.exists(fileName):
            sf.WriteToFile('_'.join(self.id().split('.'))+'.s'+str(sf.m_P)+'p')
            self.assertTrue(False,fileName + 'does not exist')
        regression = si.sp.SParameterFile(fileName,50.)
        self.assertTrue(self.SParametersAreEqual(sf,regression,0.001),self.id()+'result not same')
        """
        import matplotlib.pyplot as plt
        f=sf.f()
        for r in range(2):
            for c in range(2):
                responseVector=sf.Response(r+1,c+1)
                y=[20*math.log(abs(resp),10) for resp in responseVector]
                plt.subplot(2,2,r*2+c+1)
                plt.plot(f,y)
        plt.show()
        """
    def testRLC6(self):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        freq=[100e6*(i+1) for i in range(100)]
        if not os.path.exists('rlc.txt'):
            parser=si.p.SystemDescriptionParser(freq)
            parser.AddLine('var $Ll$ x $Cs$ x $Lr$ x')
            parser.AddLine('device L1 2 L $Ll$')
            parser.AddLine('device C1 2 C $Cs$')
            parser.AddLine('device L2 2 L $Lr$')
            parser.AddLine('device G 1 ground')
            parser.AddLine('connect L1 2 L2 1 C1 1')
            parser.AddLine('connect C1 2 G 1')
            parser.AddLine('port 1 L1 1')
            parser.AddLine('port 2 L2 2')
            parser.WriteToFile('rlc.txt')
        if not os.path.exists('r.txt'):
            parser=si.p.SystemDescriptionParser(freq)
            parser.AddLine('var $Rs$ 50')
            parser.AddLine('device D1 2 R $Rs$')
            parser.AddLine('port 1 D1 1 2 D1 2')
            parser.WriteToFile('r.txt')
        parser=si.p.SystemSParametersNumericParser(freq)
        parser.AddLine('device RLC 2 subcircuit rlc.txt Ll 1e-15 Cs 10e-12 Lr 1e-15')
        parser.AddLine('device R1 2 subcircuit r.txt')
        parser.AddLine('device D1 4 file TestDut.s4p')
        parser.AddLine('port 1 D1 1 2 D1 2 3 D1 3 4 RLC 2')
        parser.AddLine('connect D1 4 R1 1')
        parser.AddLine('connect R1 2 RLC 1')
        sf=si.sp.SParameters(freq,parser.SParameters())
        fileName='_'.join(self.id().split('.'))+'.s'+str(sf.m_P)+'p'
        if not os.path.exists(fileName):
            sf.WriteToFile('_'.join(self.id().split('.'))+'.s'+str(sf.m_P)+'p')
            self.assertTrue(False,fileName + 'does not exist')
        regression = si.sp.SParameterFile(fileName,50.)
        self.assertTrue(self.SParametersAreEqual(sf,regression,0.001),self.id()+'result not same')
        """
        import matplotlib.pyplot as plt
        f=sf.f()
        for r in range(2):
            for c in range(2):
                responseVector=sf.Response(r+1,c+1)
                y=[20*math.log(abs(resp),10) for resp in responseVector]
                plt.subplot(2,2,r*2+c+1)
                plt.plot(f,y)
        plt.show()
        """
    def testRes2(self):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        freq=[100e6*(i+1) for i in range(10)]
        parser=si.p.SystemSParametersNumericParser(freq)
        parser.AddLine('device R1 2 R 0.001')
        parser.AddLine('port 1 R1 1 2 R1 2')
        sf=si.sp.SParameters(freq,parser.SParameters())
        fileName='_'.join(self.id().split('.'))+'.s'+str(sf.m_P)+'p'
        if not os.path.exists(fileName):
            sf.WriteToFile('_'.join(self.id().split('.'))+'.s'+str(sf.m_P)+'p')
            self.assertTrue(False,fileName + 'does not exist')
        regression = si.sp.SParameterFile(fileName,50.)
        self.assertTrue(self.SParametersAreEqual(sf,regression,0.001),self.id()+'result not same')
        """
        import matplotlib.pyplot as plt
        f=sf.f()
        for r in range(2):
            for c in range(2):
                responseVector=sf.Response(r+1,c+1)
                y=[20*math.log(abs(resp),10) for resp in responseVector]
                plt.subplot(2,2,r*2+c+1)
                plt.plot(f,y)
        plt.show()
        """
    def testS2P(self):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        freq=[0.1e9*i for i in range(201)]
        parser=si.p.SystemSParametersNumericParser(freq)
        parser.AddLine('device D1 2 file cable.s2p')
        parser.AddLine('port 1 D1 1 2 D1 2')
        sf=si.sp.SParameters(freq,parser.SParameters())
        fileName='_'.join(self.id().split('.'))+'.s'+str(sf.m_P)+'p'
        if not os.path.exists(fileName):
            sf.WriteToFile('_'.join(self.id().split('.'))+'.s'+str(sf.m_P)+'p')
            self.assertTrue(False,fileName + 'does not exist')
        regression = si.sp.SParameterFile(fileName,50.)
        self.assertTrue(self.SParametersAreEqual(sf,regression,0.001),self.id()+'result not same')
        """
        import matplotlib.pyplot as plt
        f=sf.f()
        for r in range(2):
            for c in range(2):
                responseVector=sf.Response(r+1,c+1)
                y=[20*math.log(abs(resp),10) for resp in responseVector]
                plt.subplot(2,2,r*2+c+1)
                plt.plot(f,y)
        plt.show()
        """
    def testSParameterCallback(self):
        self.InitCallbackTester()
        freq=[0.1e9*i for i in range(201)]
        parser=si.p.SystemSParametersNumericParser(freq,callback=self.CallbackTester)
        parser.AddLine('device D1 2 file cable.s2p')
        parser.AddLine('port 1 D1 1 2 D1 2')
        parser.SParameters()
        self.assertTrue(self.CheckCallbackTesterResults([201,0.,100.]),'S-parameter parser callback incorrect')
    def testSParameterCallbackAbort(self):
        self.InitCallbackTester(50)
        freq=[0.1e9*i for i in range(201)]
        parser=si.p.SystemSParametersNumericParser(freq,callback=self.CallbackTester)
        parser.AddLine('device D1 2 file cable.s2p')
        parser.AddLine('port 1 D1 1 2 D1 2')
        with self.assertRaises(si.PySIException) as cm:
            parser.SParameters()
        self.assertEqual(cm.exception.parameter,'S-Parameters')
        self.assertTrue(self.CheckCallbackTesterResults([50,0.,24.5]),'S-parameter parser callback abort incorrect')
    def testSParameterCallbackRemoval(self):
        self.InitCallbackTester()
        freq=[0.1e9*i for i in range(201)]
        parser=si.p.SystemSParametersNumericParser(freq,callback=self.CallbackTester)
        parser.AddLine('device D1 2 file cable.s2p')
        parser.AddLine('port 1 D1 1 2 D1 2')
        parser.RemoveCallback()
        parser.SParameters()
        self.assertTrue(self.CheckCallbackTesterResults([0,None,None]),'S-parameter parser callback removal incorrect')
    def testAreEqual(self):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        firstFileRead = si.sp.SParameterFile('TestDut.s4p',50.)
        secondFileRead = si.sp.SParameterFile('TestDut.s4p',50.)
        self.assertTrue(self.SParametersAreEqual(firstFileRead,secondFileRead,0.001),'same file read is not equal')
    def testDeembed(self):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        freq=[0.1e9*i for i in range(201)]
        parser=si.p.SystemSParametersNumericParser(freq)
        parser.AddLine('device D1 2 file cable.s2p')
        parser.AddLine('device D2 2 file cable.s2p')
        parser.AddLine('port 1 D1 1 2 D2 2')
        parser.AddLine('connect D1 2 D2 1')
        system=si.sp.SParameters(freq,parser.SParameters())
        systemSParametersFileName='_'.join(self.id().split('.'))+'.s'+str(system.m_P)+'p'
        if not os.path.exists(systemSParametersFileName):
            system.WriteToFile(systemSParametersFileName)
        del parser
        parser = si.p.DeembedderNumericParser(freq)
        parser.AddLine('device D1 2 file cable.s2p')
        parser.AddLine('unknown ? 2')
        parser.AddLine('port 1 D1 1 2 ? 2')
        parser.AddLine('connect D1 2 ? 1')
        parser.AddLine('system file '+systemSParametersFileName)
        de=si.sp.SParameters(freq,parser.Deembed())
        os.remove(systemSParametersFileName)
        self.assertTrue(self.SParametersAreEqual(de,si.sp.SParameterFile('cable.s2p',50.).Resample(freq),0.00001),self.id()+'result not same')
    def testDeembed2(self):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        freq=[0.1e9*i for i in range(201)]
        parser=si.p.SystemSParametersNumericParser(freq)
        parser.AddLine('device D1 2 file cable.s2p')
        parser.AddLine('device D2 2 file cable.s2p')
        parser.AddLine('port 1 D1 1 2 D2 2')
        parser.AddLine('connect D1 2 D2 1')
        system=si.sp.SParameters(freq,parser.SParameters())
        systemSParametersFileName='_'.join(self.id().split('.'))+'.s'+str(system.m_P)+'p'
        if not os.path.exists(systemSParametersFileName):
            system.WriteToFile(systemSParametersFileName)
        del parser
        parser = si.p.DeembedderNumericParser(freq)
        parser.AddLine('device D1 2 file cable.s2p')
        parser.AddLine('unknown ? 2')
        parser.AddLine('port 1 D1 1 2 ? 2')
        parser.AddLine('connect D1 2 ? 1')
        parser.AddLine('system file '+systemSParametersFileName)
        print systemSParametersFileName
        de=si.sp.SParameters(freq,parser.Deembed(system))
        self.assertTrue(self.SParametersAreEqual(de,si.sp.SParameterFile('cable.s2p',50.).Resample(freq),0.00001),self.id()+'result not same')
        os.remove(systemSParametersFileName)
    def testDeembedCallback(self):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        self.InitCallbackTester()
        freq=[0.1e9*i for i in range(201)]
        parser=si.p.SystemSParametersNumericParser(freq)
        parser.AddLine('device D1 2 file cable.s2p')
        parser.AddLine('device D2 2 file cable.s2p')
        parser.AddLine('port 1 D1 1 2 D2 2')
        parser.AddLine('connect D1 2 D2 1')
        system=si.sp.SParameters(freq,parser.SParameters())
        systemSParametersFileName='_'.join(self.id().split('.'))+'.s'+str(system.m_P)+'p'
        if not os.path.exists(systemSParametersFileName):
            system.WriteToFile(systemSParametersFileName)
        del parser
        parser = si.p.DeembedderNumericParser(freq,callback=self.CallbackTester)
        parser.AddLine('device D1 2 file cable.s2p')
        parser.AddLine('unknown ? 2')
        parser.AddLine('port 1 D1 1 2 ? 2')
        parser.AddLine('connect D1 2 ? 1')
        parser.AddLine('system file '+systemSParametersFileName)
        si.sp.SParameters(freq,parser.Deembed(system))
        os.remove(systemSParametersFileName)
        self.assertTrue(self.CheckCallbackTesterResults([201,0.,100.]),'Deembedder parser callback incorrect')
    def testDeembedCallbackAbort(self):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        self.InitCallbackTester(abortOn=50)
        freq=[0.1e9*i for i in range(201)]
        parser=si.p.SystemSParametersNumericParser(freq)
        parser.AddLine('device D1 2 file cable.s2p')
        parser.AddLine('device D2 2 file cable.s2p')
        parser.AddLine('port 1 D1 1 2 D2 2')
        parser.AddLine('connect D1 2 D2 1')
        system=si.sp.SParameters(freq,parser.SParameters())
        systemSParametersFileName='_'.join(self.id().split('.'))+'.s'+str(system.m_P)+'p'
        if not os.path.exists(systemSParametersFileName):
            system.WriteToFile(systemSParametersFileName)
        del parser
        parser = si.p.DeembedderNumericParser(freq,callback=self.CallbackTester)
        parser.AddLine('device D1 2 file cable.s2p')
        parser.AddLine('unknown ? 2')
        parser.AddLine('port 1 D1 1 2 ? 2')
        parser.AddLine('connect D1 2 ? 1')
        parser.AddLine('system file '+systemSParametersFileName)
        with self.assertRaises(si.PySIException) as cm:
            si.sp.SParameters(freq,parser.Deembed(system))
        self.assertEqual(cm.exception.parameter,'Deembedder')
        os.remove(systemSParametersFileName)
        self.assertTrue(self.CheckCallbackTesterResults([50,0.,24.5]),'Deembedder parser callback abort incorrect')
# Incorrect S-parameter file extensions on write
    def testMissingExtension(self):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        sf=si.sp.SParameterFile('TestDut.s4p',50.)
        # this is to test writing without an extension
        if os.path.exists('TestDutCmp.s4p'):
            os.remove('TestDutCmp.s4p')
        sf.WriteToFile('TestDutCmp')
        sf2=si.sp.SParameterFile('TestDutCmp.s4p',50.)
        self.assertTrue(self.SParametersAreEqual(sf2,sf,0.001),self.id()+'result not same')
    def testExtensionNoS(self):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        sf=si.sp.SParameterFile('TestDut.s4p',50.)
        # this is to test writing without an extension
        if os.path.exists('TestDutCmp.s4p'):
            os.remove('TestDutCmp.s4p')
        with self.assertRaises(si.PySIException) as cm:
            sf.WriteToFile('TestDutCmp.45p')
        self.assertEqual(cm.exception,si.PySIExceptionSParameterFile())
    def testExtensionNo4(self):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        sf=si.sp.SParameterFile('TestDut.s4p',50.)
        # this is to test writing without an extension
        if os.path.exists('TestDutCmp.s4p'):
            os.remove('TestDutCmp.s4p')
        with self.assertRaises(si.PySIException) as cm:
            sf.WriteToFile('TestDutCmp.sXp')
        self.assertEqual(cm.exception,si.PySIExceptionSParameterFile())
    def testExtensionNoP(self):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        sf=si.sp.SParameterFile('TestDut.s4p',50.)
        # this is to test writing without an extension
        if os.path.exists('TestDutCmp.s4p'):
            os.remove('TestDutCmp.s4p')
        with self.assertRaises(si.PySIException) as cm:
            sf.WriteToFile('TestDutCmp.s45')
        self.assertEqual(cm.exception,si.PySIExceptionSParameterFile)
    def testExtensionNotLongEnough(self):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        sf=si.sp.SParameterFile('TestDut.s4p',50)
        # this is to test writing without an extension
        if os.path.exists('TestDutCmp.s4p'):
            os.remove('TestDutCmp.s4p')
        with self.assertRaises(si.PySIException) as cm:
            sf.WriteToFile('TestDutCmp.x')
        self.assertEqual(cm.exception,si.PySIExceptionSParameterFile())
    def testExtensionWrongPorts(self):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        sf=si.sp.SParameterFile('TestDut.s4p',50.)
        # this is to test writing without an extension
        if os.path.exists('TestDutCmp.s4p'):
            os.remove('TestDutCmp.s4p')
        with self.assertRaises(si.PySIException) as cm:
            sf.WriteToFile('TestDutCmp.s3p')
        self.assertEqual(cm.exception,si.PySIExceptionSParameterFile())
    def testSParameterFileFourPortReferenceImpedance(self):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        sf=si.sp.SParameterFile('TestDut.s4p',30.)
        #f=[i*100e6 for i in range(201)]
        #sf.Resample(f)
        #sf.WriteToFile('TestDut.s4p')
        f=sf.f()
        """
        import matplotlib.pyplot as plt
        for r in range(4):
            for c in range(4):
                responseVector=sf.Response(r+1,c+1)
                y=[20*math.log(abs(resp),10) for resp in responseVector]
                plt.subplot(4,4,r*4+c+1)
                plt.plot(f,y)
        plt.show()
        """
        # this is to test reading and writing, but also to ensure that
        # WriteToFile is always executed and covered
        sf.WriteToFile('TestDutCmp.s4p')
        sf2=si.sp.SParameterFile('TestDutCmp.s4p',50.)
        os.remove('TestDutCmp.s4p')
        self.assertTrue(self.SParametersAreEqual(sf2,sf.SetReferenceImpedance(50.),0.001),self.id()+'result not same')

if __name__ == '__main__':
    unittest.main()
