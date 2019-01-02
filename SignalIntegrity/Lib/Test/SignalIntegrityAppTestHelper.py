"""
SignalIntegrityAppTestHelper.py
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
import os

class SignalIntegrityAppTestHelper:
    relearn=True
    plotErrors=False
    forceWritePictures=False
    def __init__(self,path):
        self.path=path
    def FileNameForTest(self,filename):
        return filename.replace('..', 'Up').replace('/','_').split('.')[0]
    def PictureChecker(self,pysi,filename):
        if not self.checkPictures:
            return
        currentDirectory=os.getcwd()
        os.chdir(self.path)
        testFilename=self.FileNameForTest(filename)+'.TpX'
        try:
            from SignalIntegrity.App.TpX import TpX
            from SignalIntegrity.App.TikZ import TikZ
            tpx=pysi.Drawing.DrawSchematic(TpX()).Finish()
            tikz=pysi.Drawing.DrawSchematic(TikZ()).Finish()
            tpx.lineList=tpx.lineList+tikz.lineList
        except:
            self.assertTrue(False,filename + ' couldnt be drawn')
        if not os.path.exists(testFilename) or self.forceWritePictures:
            tpx.WriteToFile(testFilename)
            if not self.relearn:
                self.assertTrue(False, testFilename + ' not found')
        with open(testFilename) as f:
            regression=f.readlines()
        if tpx.lineList==regression:
            os.chdir(currentDirectory)
            return
        # if we get here, we need a more complicated test because ordering may have changed
        self.assertTrue(len(tpx.lineList)==len(regression),testFilename + ' incorrect')
        itemsToCheck=[True for _ in range(len(regression))]
        for tpxline in tpx.lineList:
            foundOne=False
            for k in range(len(regression)):
                if itemsToCheck[k] and not foundOne:
                    if tpxline==regression[k]:
                        itemsToCheck[k] = False
                        foundOne=True
                if foundOne:
                    continue
            self.assertTrue(foundOne,testFilename + ' incorrect')
        print(testFilename+' okay, but in different order')
        os.chdir(currentDirectory)
    def NetListChecker(self,pysi,filename):
        currentDirectory=os.getcwd()
        os.chdir(self.path)
        testFilename=self.FileNameForTest(filename)+'.net'
        try:
            netlist=pysi.Drawing.schematic.NetList().Text()
        except:
            self.assertTrue(False,filename + ' couldnt produce netlist')
        netlist=[line+'\n' for line in netlist]
        if not os.path.exists(testFilename):
            with open(testFilename,"w") as f:
                for line in netlist:
                    f.write(line)
                if not self.relearn:
                    self.assertTrue(False, testFilename + ' not found')
        with open(testFilename) as f:
            regression=f.readlines()
        self.assertTrue(len(netlist)==len(regression),testFilename + ' incorrect')
        for netline,regressionline in zip(netlist,regression):
            if netline != regressionline:
                if (netline[:len('connect')]=='connect') and (regression[:len('connect')]=='connect'):
                    netconnecttokens=netline[len('connect'):]
                    regressiontokens=regressionline[len('connect'):]
                    if len(netconnecttokens)//2*2!=len(netconnecttokens):
                        self.fail(testFilename + ' incorrect')
                    if len(regressiontokens)//2*2!=len(regressiontokens):
                        self.fail(testFilename + ' incorrect')
                    if len(netconnecttokens)!=len(regressiontokens):
                        self.fail(testFilename + ' incorrect')
                    nets=[(netconnecttokens[i],netconnecttokens[i+1]) for i in range(len(netconnecttokens)/2)]
                    regs=[(regressiontokens[i],regressiontokens[i+1]) for i in range(len(regressiontokens)/2)]
                    itemsToCheck=[True for _ in range(len(regs))]
                    for net in nets:
                        foundOne=False
                        for k in range(len(regs)):
                            if itemsToCheck[k] and not foundOne:
                                if net==regs[k]:
                                    itemsToCheck[k] = False
                                    foundOne=True
                            if foundOne:
                                continue
                        self.assertTrue(foundOne,testFilename + ' incorrect')
                    print(testFilename+' okay, but connections in different order')
        os.chdir(currentDirectory)
    def SParameterRegressionChecker(self,sp,spfilename):
        from SignalIntegrity.Lib.SParameters.SParameterFile import SParameterFile
        currentDirectory=os.getcwd()
        os.chdir(self.path)
        if not os.path.exists(spfilename):
            sp.WriteToFile(spfilename)
            if not self.relearn:
                self.assertTrue(False, spfilename + ' not found')
        regression=SParameterFile(spfilename)
        SpAreEqual=self.SParametersAreEqual(sp, regression,1e-3)
        if not SpAreEqual:
            if SignalIntegrityAppTestHelper.plotErrors:
                import matplotlib.pyplot as plt
                plt.clf()
                plt.title(spfilename)
                plt.xlabel('frequency (Hz)')
                plt.ylabel('amplitude')
                for r in range(regression.m_P):
                    for c in range(regression.m_P):
                        plt.semilogy(regression.f(),[abs(sp[n][r][c]-regression[n][r][c]) for n in range(len(regression))],label='S'+str(r+1)+str(c+1))
                plt.legend(loc='upper right')
                plt.grid(True)
                plt.show()

                for r in range(regression.m_P):
                    for c in range(regression.m_P):
                        plt.clf()
                        plt.title('S'+str(r+1)+str(c+1)+' Magnitude')
                        plt.plot(sp.FrequencyResponse(r+1,c+1).Frequencies(),sp.FrequencyResponse(r+1,c+1).Values('dB'),label='calculated')
                        plt.plot(regression.FrequencyResponse(r+1,c+1).Frequencies(),regression.FrequencyResponse(r+1,c+1).Values('dB'),label='regression')
                        plt.xlabel('frequency (Hz)')
                        plt.ylabel('amplitude (dB)')
                        plt.legend(loc='upper right')
                        plt.grid(True)
                        plt.show()

                        plt.clf()
                        plt.title('S'+str(r+1)+str(c+1)+' Phase')
                        plt.plot(sp.FrequencyResponse(r+1,c+1).Frequencies(),sp.FrequencyResponse(r+1,c+1).Values('deg'),label='calculated')
                        plt.plot(regression.FrequencyResponse(r+1,c+1).Frequencies(),regression.FrequencyResponse(r+1,c+1).Values('deg'),label='regression')
                        plt.xlabel('frequency (Hz)')
                        plt.ylabel('amplitude (dB)')
                        plt.legend(loc='upper right')
                        plt.grid(True)
                        plt.show()

        self.assertTrue(SpAreEqual,spfilename + ' incorrect')
        os.chdir(currentDirectory)

    def WaveformRegressionChecker(self,wf,wffilename):
        from SignalIntegrity.Lib.TimeDomain.Waveform import Waveform
        currentDirectory=os.getcwd()
        os.chdir(self.path)     
        if not os.path.exists(wffilename):
            wf.WriteToFile(wffilename)
            if not self.relearn:
                self.assertTrue(False, wffilename + ' not found')
        regression=Waveform().ReadFromFile(wffilename)
        self.assertTrue(wf==regression,wffilename + ' incorrect')
        os.chdir(currentDirectory)
    def Preliminary(self,filename,checkPicture=True,checkNetlist=True):
        os.chdir(self.path)
        from SignalIntegrity.App.SignalIntegrityAppHeadless import SignalIntegrityAppHeadless
        pysi=SignalIntegrityAppHeadless()
        self.assertTrue(pysi.OpenProjectFile(os.path.realpath(filename)),filename + ' couldnt be opened')
        if checkPicture:
            self.PictureChecker(pysi,filename)
        if checkNetlist:
            self.NetListChecker(pysi,filename)
        return pysi
    def SParameterResultsChecker(self,filename,checkPicture=True,checkNetlist=True):
        pysi=self.Preliminary(filename, checkPicture, checkNetlist)
        result=pysi.CalculateSParameters()
        self.assertIsNotNone(result, filename+' produced none')
        os.chdir(self.path)
        spfilename=result[1]
        spfilename=self.FileNameForTest(filename)+'.'+spfilename.split('.')[-1]
        sp=result[0]
        self.SParameterRegressionChecker(sp, spfilename)
        return result
    def SimulationResultsChecker(self,filename,checkPicture=True,checkNetlist=True):
        pysi=self.Preliminary(filename, checkPicture, checkNetlist)
        result=pysi.Simulate()
        self.assertIsNotNone(result, filename+' produced none')
        os.chdir(self.path)
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
        spfilename=self.FileNameForTest(filename)+'.s'+str(ports)+'p'
        self.SParameterRegressionChecker(sp, spfilename)
        for i in range(len(outputNames)):
            wf=outputWaveforms[i]
            wffilename=self.FileNameForTest(filename)+'_'+outputNames[i]+'.txt'
            self.WaveformRegressionChecker(wf, wffilename)
        return result
    def VirtualProbeResultsChecker(self,filename,checkPicture=True,checkNetlist=True):
        pysi=self.Preliminary(filename, checkPicture, checkNetlist)
        result=pysi.VirtualProbe()
        self.assertIsNotNone(result, filename+' produced none')
        os.chdir(self.path)
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
        spfilename=self.FileNameForTest(filename)+'.s'+str(ports)+'p'
        self.SParameterRegressionChecker(sp, spfilename)
        for i in range(len(outputNames)):
            wf=outputWaveforms[i]
            wffilename=self.FileNameForTest(filename)+'_'+outputNames[i]+'.txt'
            self.WaveformRegressionChecker(wf, wffilename)
    def DeembeddingResultsChecker(self,filename,checkPicture=True,checkNetlist=True):
        pysi=self.Preliminary(filename, checkPicture, checkNetlist)
        result=pysi.Deembed()
        self.assertIsNotNone(result, filename+' produced none')
        os.chdir(self.path)
        spfilenames=result[0]
        spfilenames=[self.FileNameForTest(filename)+'_'+spf for spf in spfilenames]
        sps=result[1]
        for i in range(len(spfilenames)):
            sp=sps[i]
            spfilename=spfilenames[i]+'.s'+str(sp.m_P)+'p'
            self.SParameterRegressionChecker(sp, spfilename)
        return result
