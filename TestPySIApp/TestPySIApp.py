'''
Created on Sep 7, 2017

@author: pete
'''
import unittest
from PySIApp import PySIAppHeadless
from PySIApp.TpX import TpX
from PySIApp.TikZ import TikZ
import SignalIntegrity as si
import os

class SParameterCompareHelper(object):
    def SParametersAreEqual(self,lhs,rhs,epsilon=0.00001):
        if lhs.m_P != rhs.m_P: return False
        if lhs.m_Z0 != rhs.m_Z0: return False
        if len(lhs) != len(rhs): return False
        for n in range(len(lhs)):
            if abs(lhs.m_f[n] - rhs.m_f[n]) > epsilon: return False
            lhsn=lhs[n]
            rhsn=rhs[n]
            for r in range(lhs.m_P):
                for c in range(lhs.m_P):
                    if abs(lhsn[r][c] - rhsn[r][c]) > epsilon:
                        return False
        return True

class Test(unittest.TestCase,SParameterCompareHelper):
    relearn=False
    def PictureChecker(self,pysi):
        currentDirectory=os.getcwd()
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        filename=pysi.fileparts.filename+'.TpX'
        try:
            tpx=pysi.Drawing.DrawSchematic(TpX()).Finish()
            tikz=pysi.Drawing.DrawSchematic(TikZ()).Finish()
            tpx.lineList=tpx.lineList+tikz.lineList
        except:
            self.assertTrue(False,filename + ' couldnt be drawn')
        if not os.path.exists(filename):
            tpx.WriteToFile(filename)
            if not self.relearn:
                self.assertTrue(False, filename + ' not found')
        with open(filename) as f:
            regression=f.readlines()
        self.assertTrue(tpx.lineList==regression,filename + ' incorrect')
        os.chdir(currentDirectory)
    def NetListChecker(self,pysi):
        currentDirectory=os.getcwd()
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        filename=pysi.fileparts.filename+'.net'
        try:
            netlist=pysi.Drawing.schematic.NetList().Text()
        except:
            self.assertTrue(False,filename + ' couldnt produce netlist')
        netlist=[line+'\n' for line in netlist]
        if not os.path.exists(filename):
            with open(filename,"w") as f:
                for line in netlist:
                    f.write(line)
                if not self.relearn:
                    self.assertTrue(False, filename + ' not found')
        with open(filename) as f:
            regression=f.readlines()
        self.assertTrue(netlist==regression,filename + ' incorrect')
        os.chdir(currentDirectory)
    def SParameterRegressionChecker(self,sp,spfilename):
        currentDirectory=os.getcwd()
        os.chdir(os.path.dirname(os.path.realpath(__file__)))        
        if not os.path.exists(spfilename):
            sp.WriteToFile(spfilename)
            if not self.relearn:
                self.assertTrue(False, spfilename + ' not found')
        regression=si.sp.SParameterFile(spfilename)
        self.assertTrue(self.SParametersAreEqual(sp, regression),spfilename + ' incorrect')
        os.chdir(currentDirectory)
    def WaveformRegressionChecker(self,wf,wffilename):
        currentDirectory=os.getcwd()
        os.chdir(os.path.dirname(os.path.realpath(__file__)))        
        if not os.path.exists(wffilename):
            wf.WriteToFile(wffilename)
            if not self.relearn:
                self.assertTrue(False, wffilename + ' not found')
        regression=si.td.wf.Waveform().ReadFromFile(wffilename)
        self.assertTrue(wf==regression,wffilename + ' incorrect')
        os.chdir(currentDirectory)
    def Preliminary(self,filename,checkPicture=True,checkNetlist=True):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        pysi=PySIAppHeadless()
        self.assertTrue(pysi.OpenProjectFile(os.path.realpath(filename)),filename + ' couldnt be opened')
        if checkPicture:
            self.PictureChecker(pysi)
        if checkNetlist:
            self.NetListChecker(pysi)
        return pysi
    def SParameterResultsChecker(self,filename,checkPicture=True,checkNetlist=True):
        pysi=self.Preliminary(filename, checkPicture, checkNetlist)
        result=pysi.CalculateSParameters()
        self.assertIsNotNone(result, filename+' produced none')
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        spfilename=result[1]
        sp=result[0]
        self.SParameterRegressionChecker(sp, spfilename)
    def SimulationResultsChecker(self,filename,checkPicture=True,checkNetlist=True):
        pysi=self.Preliminary(filename, checkPicture, checkNetlist)
        result=pysi.Simulate()
        self.assertIsNotNone(result, filename+' produced none')
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        sourceNames=result[0]
        outputNames=result[1]
        transferMatrices=result[2]
        outputWaveforms=result[3]
        try:
            sp=transferMatrices.SParameters()
            ports=sp.m_P
            if ports == 0:
                raise
        except:
            self.assertTrue(False, filename + 'has no transfer matrices')
        spfilename=pysi.fileparts.filename+'.s'+str(ports)+'p'
        self.SParameterRegressionChecker(sp, spfilename)
        for i in range(len(outputNames)):
            wf=outputWaveforms[i]
            wffilename=pysi.fileparts.filename+'_'+outputNames[i]+'.txt'
            self.WaveformRegressionChecker(wf, wffilename)
    def VirtualProbeResultsChecker(self,filename,checkPicture=True,checkNetlist=True):
        pysi=self.Preliminary(filename, checkPicture, checkNetlist)
        result=pysi.VirtualProbe()
        self.assertIsNotNone(result, filename+' produced none')
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        measNames=result[0]
        outputNames=result[1]
        transferMatrices=result[2]
        outputWaveforms=result[3]
        try:
            sp=transferMatrices.SParameters()
            ports=sp.m_P
            if ports == 0:
                raise
        except:
            self.assertTrue(False, filename + 'has no transfer matrices')
        spfilename=pysi.fileparts.filename+'.s'+str(ports)+'p'
        self.SParameterRegressionChecker(sp, spfilename)
        for i in range(len(outputNames)):
            wf=outputWaveforms[i]
            wffilename=pysi.fileparts.filename+'_'+outputNames[i]+'.txt'
            self.WaveformRegressionChecker(wf, wffilename)
    def DeembeddingResultsChecker(self,filename,checkPicture=True,checkNetlist=True):
        pysi=self.Preliminary(filename, checkPicture, checkNetlist)
        result=pysi.Deembed()
        self.assertIsNotNone(result, filename+' produced none')
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        spfilenames=result[0]
        sps=result[1]
        for i in range(len(spfilenames)):
            sp=sps[i]
            spfilename=spfilenames[i]+'.s'+str(sp.m_P)+'p'
            self.SParameterRegressionChecker(sp, spfilename)
    def testFourPortTLineTest(self):
        self.SimulationResultsChecker('FourPortTLineTest.xml')
    def testFilterTest(self):
        self.SimulationResultsChecker('FilterTest.xml')
    def testPySIAppExamplesRLCTest2(self):
        self.SimulationResultsChecker('../PySIApp/Examples/RLCTest2.xml')
    def testPySIAppDeembedCableFilter(self):
        self.DeembeddingResultsChecker('../PySIApp/Examples/DeembedCableFilter.xml')
    def testPySIAppExampleSparameterExampleSParameterGenerationExample(self):
        self.SParameterResultsChecker('../PySIApp/Examples/SParameterExample/SParameterGenerationExample.xml')
    def testPySIAppExampleVirtualProbingExampleVirtualProbeExample(self):
        self.VirtualProbeResultsChecker('../PySIApp/Examples/VirtualProbingExample/VirtualProbeExample.xml')
    def testOpenStub(self):
        self.SParameterResultsChecker('OpenStub.xml')
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()