"""
TestTDRErrorTerms.py
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
import SignalIntegrity.App as siapp

import os

from numpy import matrix,identity
import math

#------------------------------------------------------------------------------ 
# this class tries to speed things up a bit using a pickle containing the simulation
# results from a simulation that is used for every test.  If the pickle 'simresults.p'
# exists, it will load this pickle as the complete set of simulation results - you must
# delete this pickle if you change any of the schematics and expect them to produce
# different results.  This pickle will get rewritten by one of the classes as the simulation
# results are produced only once by the first test to produce them so it doesn't really matter
# who writes the pickle.
# you must set usePickle to True for it to perform this caching.  It cuts the time from about
# 1 minute to about 20 seconds
#------------------------------------------------------------------------------ 
class TestTDRErrorTermsTest(unittest.TestCase,
        si.test.SParameterCompareHelper,si.test.SignalIntegrityAppTestHelper):
    resDict=None
    def __init__(self, methodName='runTest'):
        si.test.SParameterCompareHelper.__init__(self)
        unittest.TestCase.__init__(self,methodName)
        si.test.SignalIntegrityAppTestHelper.__init__(self,os.path.dirname(os.path.realpath(__file__)))
        self.g1=1.2
        self.g2=0.8
        self.V1=1.0
        self.V2=1.0
        self.fd=si.fd.EvenlySpacedFrequencyList(40e9,200)
    def setUp(self):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        self.DoSimulation()
    def testZZZDoThisLast(self):
        if os.path.exists('TDRSimulationShort.si'): os.remove('TDRSimulationShort.si')
        if os.path.exists('TDRSimulationOpen.si'): os.remove('TDRSimulationOpen.si')
        if os.path.exists('TDRSimulationLoad.si'): os.remove('TDRSimulationLoad.si')
        if os.path.exists('TDRSimulationThru1.si'): os.remove('TDRSimulationThru1.si')
        if os.path.exists('TDRSimulationThru2.si'): os.remove('TDRSimulationThru2.si')
    def buildSimulations(self):
        # @todo: currently, I set the risetime on the pulse to a tiny number just to make
        # sure it actually comes out, but the definition of the pulse source is that at
        # time 0, it is at the 50% point, so when I do this, tiny pulses come out half
        # the size.  so down below, you'll see the amplitude doubled if the size is not
        # zero.  I should fix this by creating an impulse generator, and letting the
        # pulse generator be the way it is.
        risetime=1e-21
        WaveformStartTime=-1e-9
        WaveformEndTime = 5e-9
        print('Building Simulations')
        simName=projName='Short'
        print(simName)
        tdrsim=siapp.SignalIntegrityAppHeadless()
        tdrsim.OpenProjectFile('TDRSimulation.si')
        siapp.Project['CalculationProperties.EndFrequency']=self.fd.Fe
        siapp.Project['CalculationProperties.FrequencyPoints']=self.fd.N
        siapp.Project['CalculationProperties'].CalculateOthersFromBaseInformation()
        siapp.Project['CalculationProperties.UserSampleRate']=siapp.Project['CalculationProperties.BaseSampleRate']
        siapp.Project['CalculationProperties'].CalculateOthersFromBaseInformation()
        tdrsim.Device('V1')['gain']['Value']=self.g1
        tdrsim.Device('V2')['gain']['Value']=self.g2
        tdrsim.Device('DUT')['file']['Value']=simName+'.si'
        tdrsim.Device('VG1')['a']['Value']=self.V1 * (1. if risetime == 0.0 else 2.)
        tdrsim.Device('VG1')['rt']['Value']=risetime
        tdrsim.Device('VG1')['fs']['Value']=siapp.Project['CalculationProperties.BaseSampleRate']
        HorizontalOffset=WaveformStartTime-siapp.Project['CalculationProperties.ImpulseResponseLength']/2.
        tdrsim.Device('VG1')['ho']['Value']=HorizontalOffset
        tdrsim.Device('VG1')['dur']['Value']=WaveformEndTime-HorizontalOffset+siapp.Project['CalculationProperties.ImpulseResponseLength']/2.
        tdrsim.Device('VG2')['a']['Value']=self.V2 * (1. if risetime == 0.0 else 2.)
        tdrsim.Device('VG2')['rt']['Value']=risetime
        tdrsim.Device('VG2')['fs']['Value']=siapp.Project['CalculationProperties.BaseSampleRate']
        HorizontalOffset=WaveformStartTime-siapp.Project['CalculationProperties.ImpulseResponseLength']/2.
        tdrsim.Device('VG2')['ho']['Value']=HorizontalOffset
        tdrsim.Device('VG2')['dur']['Value']=WaveformEndTime-HorizontalOffset+siapp.Project['CalculationProperties.ImpulseResponseLength']/2.
        tdrsim.SaveProjectToFile('TDRSimulation'+simName+'.si')
        simName=projName='Open'
        print(simName)
        tdrsim=siapp.SignalIntegrityAppHeadless()
        tdrsim.OpenProjectFile('TDRSimulation.si')
        siapp.Project['CalculationProperties.EndFrequency']=self.fd.Fe
        siapp.Project['CalculationProperties.FrequencyPoints']=self.fd.N
        siapp.Project['CalculationProperties'].CalculateOthersFromBaseInformation()
        siapp.Project['CalculationProperties.UserSampleRate']=siapp.Project['CalculationProperties.BaseSampleRate']
        siapp.Project['CalculationProperties'].CalculateOthersFromBaseInformation()        
        tdrsim.Device('V1')['gain']['Value']=self.g1
        tdrsim.Device('V2')['gain']['Value']=self.g2
        tdrsim.Device('DUT')['file']['Value']=simName+'.si'
        tdrsim.Device('VG1')['a']['Value']=self.V1 * (1. if risetime == 0.0 else 2.)
        tdrsim.Device('VG1')['rt']['Value']=risetime
        tdrsim.Device('VG1')['fs']['Value']=siapp.Project['CalculationProperties.BaseSampleRate']
        HorizontalOffset=WaveformStartTime-siapp.Project['CalculationProperties.ImpulseResponseLength']/2.
        tdrsim.Device('VG1')['ho']['Value']=HorizontalOffset
        tdrsim.Device('VG1')['dur']['Value']=WaveformEndTime-HorizontalOffset+siapp.Project['CalculationProperties.ImpulseResponseLength']/2.
        tdrsim.Device('VG2')['a']['Value']=self.V2 * (1. if risetime == 0.0 else 2.)
        tdrsim.Device('VG2')['rt']['Value']=risetime
        tdrsim.Device('VG2')['fs']['Value']=siapp.Project['CalculationProperties.BaseSampleRate']
        HorizontalOffset=WaveformStartTime-siapp.Project['CalculationProperties.ImpulseResponseLength']/2.
        tdrsim.Device('VG2')['ho']['Value']=HorizontalOffset
        tdrsim.Device('VG2')['dur']['Value']=WaveformEndTime-HorizontalOffset+siapp.Project['CalculationProperties.ImpulseResponseLength']/2.
        tdrsim.SaveProjectToFile('TDRSimulation'+simName+'.si')
        simName=projName='Load'
        print(simName)
        tdrsim=siapp.SignalIntegrityAppHeadless()
        tdrsim.OpenProjectFile('TDRSimulation.si')
        siapp.Project['CalculationProperties.EndFrequency']=self.fd.Fe
        siapp.Project['CalculationProperties.FrequencyPoints']=self.fd.N
        siapp.Project['CalculationProperties'].CalculateOthersFromBaseInformation()
        siapp.Project['CalculationProperties.UserSampleRate']=siapp.Project['CalculationProperties.BaseSampleRate']
        siapp.Project['CalculationProperties'].CalculateOthersFromBaseInformation()        
        tdrsim.Device('V1')['gain']['Value']=self.g1
        tdrsim.Device('V2')['gain']['Value']=self.g2
        tdrsim.Device('DUT')['file']['Value']=simName+'.si'
        tdrsim.Device('VG1')['a']['Value']=self.V1 * (1. if risetime == 0.0 else 2.)
        tdrsim.Device('VG1')['rt']['Value']=risetime
        tdrsim.Device('VG1')['fs']['Value']=siapp.Project['CalculationProperties.BaseSampleRate']
        HorizontalOffset=WaveformStartTime-siapp.Project['CalculationProperties.ImpulseResponseLength']/2.
        tdrsim.Device('VG1')['ho']['Value']=HorizontalOffset
        tdrsim.Device('VG1')['dur']['Value']=WaveformEndTime-HorizontalOffset+siapp.Project['CalculationProperties.ImpulseResponseLength']/2.
        tdrsim.Device('VG2')['a']['Value']=self.V2 * (1. if risetime == 0.0 else 2.)
        tdrsim.Device('VG2')['rt']['Value']=risetime
        tdrsim.Device('VG2')['fs']['Value']=siapp.Project['CalculationProperties.BaseSampleRate']
        HorizontalOffset=WaveformStartTime-siapp.Project['CalculationProperties.ImpulseResponseLength']/2.
        tdrsim.Device('VG2')['ho']['Value']=HorizontalOffset
        tdrsim.Device('VG2')['dur']['Value']=WaveformEndTime-HorizontalOffset+siapp.Project['CalculationProperties.ImpulseResponseLength']/2.
        tdrsim.SaveProjectToFile('TDRSimulation'+simName+'.si')
        simName='Thru'
        projName=simName+'1'
        print(simName)
        tdrsim=siapp.SignalIntegrityAppHeadless()
        tdrsim.OpenProjectFile('TDRSimulation.si')
        siapp.Project['CalculationProperties.EndFrequency']=self.fd.Fe
        siapp.Project['CalculationProperties.FrequencyPoints']=self.fd.N
        siapp.Project['CalculationProperties'].CalculateOthersFromBaseInformation()
        siapp.Project['CalculationProperties.UserSampleRate']=siapp.Project['CalculationProperties.BaseSampleRate']
        siapp.Project['CalculationProperties'].CalculateOthersFromBaseInformation()        
        tdrsim.Device('V1')['gain']['Value']=self.g1
        tdrsim.Device('V2')['gain']['Value']=self.g2
        tdrsim.Device('DUT')['file']['Value']=simName+'.si'
        tdrsim.Device('VG1')['a']['Value']=self.V1 * (1. if risetime == 0.0 else 2.)
        tdrsim.Device('VG1')['rt']['Value']=risetime
        tdrsim.Device('VG1')['fs']['Value']=siapp.Project['CalculationProperties.BaseSampleRate']
        HorizontalOffset=WaveformStartTime-siapp.Project['CalculationProperties.ImpulseResponseLength']/2.
        tdrsim.Device('VG1')['ho']['Value']=HorizontalOffset
        tdrsim.Device('VG1')['dur']['Value']=WaveformEndTime-HorizontalOffset+siapp.Project['CalculationProperties.ImpulseResponseLength']/2.
        tdrsim.Device('VG2')['a']['Value']=0.0
        tdrsim.Device('VG2')['rt']['Value']=risetime
        tdrsim.Device('VG2')['fs']['Value']=siapp.Project['CalculationProperties.BaseSampleRate']
        HorizontalOffset=WaveformStartTime-siapp.Project['CalculationProperties.ImpulseResponseLength']/2.
        tdrsim.Device('VG2')['ho']['Value']=HorizontalOffset
        tdrsim.Device('VG2')['dur']['Value']=WaveformEndTime-HorizontalOffset+siapp.Project['CalculationProperties.ImpulseResponseLength']/2.
        tdrsim.SaveProjectToFile('TDRSimulation'+projName+'.si')
        simName='Thru'
        projName=simName+'2'
        print(simName)
        tdrsim=siapp.SignalIntegrityAppHeadless()
        tdrsim.OpenProjectFile('TDRSimulation.si')
        siapp.Project['CalculationProperties.EndFrequency']=self.fd.Fe
        siapp.Project['CalculationProperties.FrequencyPoints']=self.fd.N
        siapp.Project['CalculationProperties'].CalculateOthersFromBaseInformation()
        siapp.Project['CalculationProperties.UserSampleRate']=siapp.Project['CalculationProperties.BaseSampleRate']
        siapp.Project['CalculationProperties'].CalculateOthersFromBaseInformation()        
        tdrsim.Device('V1')['gain']['Value']=self.g1
        tdrsim.Device('V2')['gain']['Value']=self.g2
        tdrsim.Device('DUT')['file']['Value']=simName+'.si'
        tdrsim.Device('VG1')['a']['Value']=0.0
        tdrsim.Device('VG1')['rt']['Value']=risetime
        tdrsim.Device('VG1')['fs']['Value']=siapp.Project['CalculationProperties.BaseSampleRate']
        HorizontalOffset=WaveformStartTime-siapp.Project['CalculationProperties.ImpulseResponseLength']/2.
        tdrsim.Device('VG1')['ho']['Value']=HorizontalOffset
        tdrsim.Device('VG1')['dur']['Value']=WaveformEndTime-HorizontalOffset+siapp.Project['CalculationProperties.ImpulseResponseLength']/2.
        tdrsim.Device('VG2')['a']['Value']=self.V2 * (1. if risetime == 0.0 else 2.)
        tdrsim.Device('VG2')['rt']['Value']=risetime
        tdrsim.Device('VG2')['fs']['Value']=siapp.Project['CalculationProperties.BaseSampleRate']
        HorizontalOffset=WaveformStartTime-siapp.Project['CalculationProperties.ImpulseResponseLength']/2.
        tdrsim.Device('VG2')['ho']['Value']=HorizontalOffset
        tdrsim.Device('VG2')['dur']['Value']=WaveformEndTime-HorizontalOffset+siapp.Project['CalculationProperties.ImpulseResponseLength']/2.
        tdrsim.SaveProjectToFile('TDRSimulation'+projName+'.si')
    def DoSimulation(self):
        resDict=TestTDRErrorTermsTest.resDict
        if not resDict is None:
            return
        self.buildSimulations()
        resDict={}
        print('S-Parameters')
        simName='Gamma1'
        print(simName)
        projName=simName+'.si'
        spProj=siapp.SignalIntegrityAppHeadless()
        spProj.OpenProjectFile(projName)
        siapp.Project['CalculationProperties.EndFrequency']=self.fd.Fe
        siapp.Project['CalculationProperties.FrequencyPoints']=self.fd.N
        siapp.Project['CalculationProperties'].CalculateOthersFromBaseInformation()
        spProj.SaveProjectToFile(projName)
        (sp,name)=spProj.CalculateSParameters()
        resDict[simName]=sp
        simName='Gamma2'
        print(simName)
        projName=simName+'.si'
        spProj=siapp.SignalIntegrityAppHeadless()
        spProj.OpenProjectFile(projName)
        siapp.Project['CalculationProperties.EndFrequency']=self.fd.Fe
        siapp.Project['CalculationProperties.FrequencyPoints']=self.fd.N
        siapp.Project['CalculationProperties'].CalculateOthersFromBaseInformation()
        spProj.SaveProjectToFile(projName)
        (sp,name)=spProj.CalculateSParameters()
        resDict[simName]=sp
        simName='Fixture1'
        print(simName)
        projName=simName+'.si'
        spProj=siapp.SignalIntegrityAppHeadless()
        spProj.OpenProjectFile(projName)
        siapp.Project['CalculationProperties.EndFrequency']=self.fd.Fe
        siapp.Project['CalculationProperties.FrequencyPoints']=self.fd.N
        siapp.Project['CalculationProperties'].CalculateOthersFromBaseInformation()
        spProj.SaveProjectToFile(projName)
        (sp,name)=spProj.CalculateSParameters()
        resDict[simName]=sp
        simName='Fixture2'
        print(simName)
        projName=simName+'.si'
        spProj=siapp.SignalIntegrityAppHeadless()
        spProj.OpenProjectFile(projName)
        siapp.Project['CalculationProperties.EndFrequency']=self.fd.Fe
        siapp.Project['CalculationProperties.FrequencyPoints']=self.fd.N
        siapp.Project['CalculationProperties'].CalculateOthersFromBaseInformation()
        spProj.SaveProjectToFile(projName)
        (sp,name)=spProj.CalculateSParameters()
        resDict[simName]=sp
        simName='Thru'
        print(simName)
        projName=simName+'.si'
        spProj=siapp.SignalIntegrityAppHeadless()
        spProj.OpenProjectFile(projName)
        siapp.Project['CalculationProperties.EndFrequency']=self.fd.Fe
        siapp.Project['CalculationProperties.FrequencyPoints']=self.fd.N
        siapp.Project['CalculationProperties'].CalculateOthersFromBaseInformation()
        spProj.SaveProjectToFile(projName)
        (sp,name)=spProj.CalculateSParameters()
        resDict[simName]=sp
        simName='Short'
        print(simName)
        projName=simName+'.si'
        spProj=siapp.SignalIntegrityAppHeadless()
        spProj.OpenProjectFile(projName)
        siapp.Project['CalculationProperties.EndFrequency']=self.fd.Fe
        siapp.Project['CalculationProperties.FrequencyPoints']=self.fd.N
        siapp.Project['CalculationProperties'].CalculateOthersFromBaseInformation()
        spProj.SaveProjectToFile(projName)
        (sp,name)=spProj.CalculateSParameters()
        resDict[simName+'1']=sp.PortReorder([0])
        resDict[simName+'2']=sp.PortReorder([1])
        simName='Open'
        print(simName)
        projName=simName+'.si'
        spProj=siapp.SignalIntegrityAppHeadless()
        spProj.OpenProjectFile(projName)
        siapp.Project['CalculationProperties.EndFrequency']=self.fd.Fe
        siapp.Project['CalculationProperties.FrequencyPoints']=self.fd.N
        siapp.Project['CalculationProperties'].CalculateOthersFromBaseInformation()
        spProj.SaveProjectToFile(projName)
        (sp,name)=spProj.CalculateSParameters()
        resDict[simName+'1']=sp.PortReorder([0])
        resDict[simName+'2']=sp.PortReorder([1])
        simName='Load'
        print(simName)
        projName=simName+'.si'
        spProj=siapp.SignalIntegrityAppHeadless()
        spProj.OpenProjectFile(projName)
        siapp.Project['CalculationProperties.EndFrequency']=self.fd.Fe
        siapp.Project['CalculationProperties.FrequencyPoints']=self.fd.N
        siapp.Project['CalculationProperties'].CalculateOthersFromBaseInformation()
        spProj.SaveProjectToFile(projName)
        (sp,name)=spProj.CalculateSParameters()
        resDict[simName+'1']=sp.PortReorder([0])
        resDict[simName+'2']=sp.PortReorder([1])
        print('TDR Simulations')
        tdrsim=siapp.SignalIntegrityAppHeadless()
        simName=projName='Short'
        tdrsim.OpenProjectFile('TDRSimulation'+simName+'.si')
        print(simName)
        (sourceNames,outputWaveformLabels,transferMatrices,outputWaveformList)=tdrsim.Simulate()
        resDict.update(dict(zip([simName+label for label in outputWaveformLabels],outputWaveformList)))
        tdrsim=siapp.SignalIntegrityAppHeadless()
        simName=projName='Open'
        tdrsim.OpenProjectFile('TDRSimulation'+simName+'.si')
        print(simName)
        (sourceNames,outputWaveformLabels,transferMatrices,outputWaveformList)=tdrsim.Simulate()
        resDict.update(dict(zip([simName+label for label in outputWaveformLabels],outputWaveformList)))
        simName=projName='Load'
        tdrsim.OpenProjectFile('TDRSimulation'+simName+'.si')
        print(simName)
        (sourceNames,outputWaveformLabels,transferMatrices,outputWaveformList)=tdrsim.Simulate()
        resDict.update(dict(zip([simName+label for label in outputWaveformLabels],outputWaveformList)))
        projName='Thru'
        simName=projName+'1'
        print(simName)
        tdrsim.OpenProjectFile('TDRSimulation'+simName+'.si')
        (sourceNames,outputWaveformLabels,transferMatrices,outputWaveformList)=tdrsim.Simulate()
        resDict.update(dict(zip([simName+label for label in outputWaveformLabels],outputWaveformList)))
        projName='Thru'
        simName=projName+'2'
        print(simName)
        tdrsim.OpenProjectFile('TDRSimulation'+simName+'.si')
        (sourceNames,outputWaveformLabels,transferMatrices,outputWaveformList)=tdrsim.Simulate()
        resDict.update(dict(zip([simName+label for label in outputWaveformLabels],outputWaveformList)))
        print('converting TDR')
        self.tdr=si.m.tdr.TDRWaveformToSParameterConverter(Step=False,fd=self.fd)

        cs=si.m.calkit.CalibrationKit(f=self.fd)

        resDict['Short1Measurement']=self.tdr.RawMeasuredSParameters(resDict['ShortV1'])
        resDict['Short2Measurement']=self.tdr.RawMeasuredSParameters(resDict['ShortV2'])
        resDict['Open1Measurement']=self.tdr.RawMeasuredSParameters(resDict['OpenV1'])
        resDict['Open2Measurement']=self.tdr.RawMeasuredSParameters(resDict['OpenV2'])
        resDict['Load1Measurement']=self.tdr.RawMeasuredSParameters(resDict['LoadV1'])
        resDict['Load2Measurement']=self.tdr.RawMeasuredSParameters(resDict['LoadV2'])
        resDict['ThruMeasurement']=self.tdr.RawMeasuredSParameters([[resDict['Thru1V1'],resDict['Thru1V2']],[resDict['Thru2V1'],resDict['Thru2V2']]])

        resDict['CalibrationTDR']=si.m.cal.Calibration(2,self.fd,[
            si.m.cal.ReflectCalibrationMeasurement(resDict['Short1Measurement'].FrequencyResponse(1,1),cs.shortStandard,0,'Short1'),
            si.m.cal.ReflectCalibrationMeasurement(resDict['Open1Measurement'].FrequencyResponse(1,1),cs.openStandard,0,'Open1'),
            si.m.cal.ReflectCalibrationMeasurement(resDict['Load1Measurement'].FrequencyResponse(1,1),cs.loadStandard,0,'Load1'),
            si.m.cal.ReflectCalibrationMeasurement(resDict['Short2Measurement'].FrequencyResponse(1,1),cs.shortStandard,1,'Short2'),
            si.m.cal.ReflectCalibrationMeasurement(resDict['Open2Measurement'].FrequencyResponse(1,1),cs.openStandard,1,'Open2'),
            si.m.cal.ReflectCalibrationMeasurement(resDict['Load2Measurement'].FrequencyResponse(1,1),cs.loadStandard,1,'Load2'),
            si.m.cal.ThruCalibrationMeasurement(resDict['ThruMeasurement'].FrequencyResponse(1,1),resDict['ThruMeasurement'].FrequencyResponse(2,1),cs.thruStandard,0,1,'Thru1'),
            si.m.cal.ThruCalibrationMeasurement(resDict['ThruMeasurement'].FrequencyResponse(2,2),resDict['ThruMeasurement'].FrequencyResponse(1,2),cs.thruStandard,1,0,'Thru2'),
            ])
        TestTDRErrorTermsTest.resDict=resDict
        resDict['CalibrationTDR'].WriteToFile('calibration.l12t').WriteFixturesToFiles('ErrorTermFixture')
    def convertTDR(self,fd,wfList,incidentIndex=0):
        tdr=si.m.tdr.TDRWaveformToSParameterConverter(Step=False,fd=fd)
        tdr.Convert(wfList,incidentIndex)
        return (tdr.IncidentWaveform,tdr.ReflectWaveforms,tdr.IncidentFrequencyContent,tdr.ReflectFrequencyContent)
    def testErrorTerms(self):
        resDict=TestTDRErrorTermsTest.resDict
        name='Short'
        tdr=si.m.tdr.TDRWaveformToSParameterConverter(Step=False,fd=self.fd)
        tdr.Convert(self.resDict[name+'V1'],0)
        self.resDict[name+'1_inc_wf']=tdr.IncidentWaveform
        self.resDict[name+'1_ref_wf']=tdr.ReflectWaveforms[0]
        self.resDict[name+'1_inc_fc']=tdr.IncidentFrequencyContent
        self.resDict[name+'1_ref_fc']=tdr.ReflectFrequencyContent[0]
        tdr.Convert(self.resDict[name+'V2'],0)
        (incwf,refwf,incfc,reffc)=self.convertTDR(self.fd,self.resDict[name+'V2'])
        self.resDict[name+'2_inc_wf']=tdr.IncidentWaveform
        self.resDict[name+'2_ref_wf']=tdr.ReflectWaveforms[0]
        self.resDict[name+'2_inc_fc']=tdr.IncidentFrequencyContent
        self.resDict[name+'2_ref_fc']=tdr.ReflectFrequencyContent[0]

        # this is the relationship between the time domain waveforms and the freqency content
        sp=si.sp.SParameters(self.resDict[name+'1_inc_fc'].Frequencies(),[[[v*self.fd.N]] for v in self.resDict[name+'1_inc_fc'].Values()])
        sp[0][0][0]=sp[0][0][0]*2
        sp[self.fd.N][0][0]=sp[self.fd.N][0][0]*2
        sp.WriteToFile('TestInc.s1p')
        sp=si.sp.SParameters(self.resDict[name+'1_ref_fc'].Frequencies(),[[[v*self.fd.N]] for v in self.resDict[name+'1_ref_fc'].Values()])
        sp[0][0][0]=sp[0][0][0]*2
        sp[self.fd.N][0][0]=sp[self.fd.N][0][0]*2
        sp.WriteToFile('TestRef.s1p')
    def testErrorTermsTDREquations(self):
        resDict=TestTDRErrorTermsTest.resDict
        # calculate the error terms using equations
        F1sp=self.resDict['Fixture1']
        rho1=si.ip.ImpedanceProfile(F1sp,1,1)[0]
        Gamma1sp=self.resDict['Gamma1']
        g1=self.g1
        F2sp=self.resDict['Fixture2']
        rho2=si.ip.ImpedanceProfile(F2sp,1,1)[0]
        Gamma2sp=self.resDict['Gamma2']
        g2=self.g2
        # m = (1/sqZ0)*(1-Gamma)/2*V
        ET=[si.m.cal.ErrorTerms().Initialize(2) for n in range(len(F1sp))]
        for n in range(len(F1sp)):
            F1=F1sp[n]
            F111=F1[0][0]
            F112=F1[0][1]
            F121=F1[1][0]
            F122=F1[1][1]
            dF1=F111*F122-F112*F121
            G1=Gamma1sp[n][0][0]
            F2=F2sp[n]
            F211=F2[0][0]
            F212=F2[0][1]
            F221=F2[1][0]
            F222=F2[1][1]
            dF2=F211*F222-F212*F221
            G2=Gamma2sp[n][0][0]
            ED1=(rho1-F111-F111*G1+rho1*G1)/((1+rho1)*(F111*G1-1))
            ES1=(G1*dF1-F122)/(F111*G1-1)
            ER1=(1+(1-rho1)*G1-rho1*G1*G1)/((1+rho1)*(F111*G1-1)**2)*F121*F112
            ED2=(rho2-F211-F211*G2+rho2*G2)/((1+rho2)*(F211*G2-1))
            ES2=(G2*dF2-F222)/(F211*G2-1)
            ER2=(1+(1-rho2)*G2-rho2*G2*G2)/((1+rho2)*(F211*G2-1)**2)*F221*F212
            EL21=ES2
            EL12=ES1
            ET21=F121*F212*g2/g1*(1+G2)/(1+rho1)*(1-rho1*G1)/((F211*G2-1)*(F111*G1-1))
            ET12=F221*F112*g1/g2*(1+G1)/(1+rho2)*(1-rho2*G2)/((F111*G1-1)*(F211*G2-1))            
            ET[n].ET=[[[ED1,ER1,ES1],[0,ET12,EL12]],[[0,ET21,EL21],[ED2,ER2,ES2]]]
        cmEq=si.m.cal.Calibration(2,self.fd)
        cmEq.ET=ET
        #cmEq.WriteFixturesToFiles('TwoPortCalEquations')

        FixturesActual=resDict['CalibrationTDR'].Fixtures()
        FixturesEquations=cmEq.Fixtures()

        for p in range(len(FixturesActual)):
            self.assertTrue(self.SParametersAreEqual(FixturesActual[p],FixturesEquations[p]),'Fixture '+str(p+1)+' not equal')

    def testTDRRawMeasuredPor1Short(self):
        resDict=TestTDRErrorTermsTest.resDict
        # confirm equation for raw measured s-parameters at port 1 with short connected
        Fsp=self.resDict['Fixture1']
        rho=si.ip.ImpedanceProfile(Fsp,1,1)[0]
        Gammasp=self.resDict['Gamma1']
        S11=-1
        Shat=[None for _ in range(len(Fsp))]
        for n in range(len(Fsp)):
            Fp=Fsp[n]
            Fp11=Fp[0][0]
            Fp12=Fp[0][1]
            Fp21=Fp[1][0]
            Fp22=Fp[1][1]
            dFp=Fp11*Fp22-Fp12*Fp21
            Gp=Gammasp[n][0][0]
            Shat[n]=(((rho*Fp22-dFp)*Gp+rho*Fp22-dFp)*S11+(Fp11-rho)*Gp+Fp11-rho)/((1+rho)*((dFp*Gp-Fp22)*S11-Gp*Fp11+1))
        Shatsp=si.sp.SParameters(Fsp.m_f,[[[s]] for s in Shat])
        #Shatsp.WriteToFile('Short1RawEquation.s1p')
        #resDict['Short1Measurement'].WriteToFile('Short1RawMeasured.s1p')
        self.assertTrue(self.SParametersAreEqual(Shatsp,resDict['Short1Measurement']),'raw short 1 measurement equation wrong')
    def testTDRRawMeasuredPort2Short(self):
        resDict=TestTDRErrorTermsTest.resDict
        # confirm equation for raw measured s-parameters at port 2 with short connected
        Fsp=self.resDict['Fixture2']
        rho=si.ip.ImpedanceProfile(Fsp,1,1)[0]
        Gammasp=self.resDict['Gamma2']
        S11=-1
        Shat=[None for _ in range(len(Fsp))]
        for n in range(len(Fsp)):
            Fp=Fsp[n]
            Fp11=Fp[0][0]
            Fp12=Fp[0][1]
            Fp21=Fp[1][0]
            Fp22=Fp[1][1]
            dFp=Fp11*Fp22-Fp12*Fp21
            Gp=Gammasp[n][0][0]
            Shat[n]=(((rho*Fp22-dFp)*Gp+rho*Fp22-dFp)*S11+(Fp11-rho)*Gp+Fp11-rho)/((1+rho)*((dFp*Gp-Fp22)*S11-Gp*Fp11+1))
        Shatsp=si.sp.SParameters(Fsp.m_f,[[[s]] for s in Shat])
        #Shatsp.WriteToFile('Short2RawEquation.s1p')
        #resDict['Short2Measurement'].WriteToFile('Short2RawMeasured.s1p')
        self.assertTrue(self.SParametersAreEqual(Shatsp,resDict['Short2Measurement']),'raw short 2 measurement equation wrong')
    def testTDRRawMeasuredPort1Open(self):
        resDict=TestTDRErrorTermsTest.resDict
        # confirm equation for raw measured s-parameters at port 1 with open connected
        Fsp=self.resDict['Fixture1']
        rho=si.ip.ImpedanceProfile(Fsp,1,1)[0]
        Gammasp=self.resDict['Gamma1']
        S11=1
        Shat=[None for _ in range(len(Fsp))]
        for n in range(len(Fsp)):
            Fp=Fsp[n]
            Fp11=Fp[0][0]
            Fp12=Fp[0][1]
            Fp21=Fp[1][0]
            Fp22=Fp[1][1]
            dFp=Fp11*Fp22-Fp12*Fp21
            Gp=Gammasp[n][0][0]
            Shat[n]=(((rho*Fp22-dFp)*Gp+rho*Fp22-dFp)*S11+(Fp11-rho)*Gp+Fp11-rho)/((1+rho)*((dFp*Gp-Fp22)*S11-Gp*Fp11+1))
        Shatsp=si.sp.SParameters(Fsp.m_f,[[[s]] for s in Shat])
        #Shatsp.WriteToFile('Open1RawEquation.s1p')
        #resDict['Open1Measurement'].WriteToFile('Open1RawMeasured.s1p')
        self.assertTrue(self.SParametersAreEqual(Shatsp,resDict['Open1Measurement']),'raw open 1 measurement equation wrong')
    def testTDRRawMeasuredPort2Open(self):
        resDict=TestTDRErrorTermsTest.resDict
        # confirm equation for raw measured s-parameters at port 2 with open connected
        Fsp=self.resDict['Fixture2']
        rho=si.ip.ImpedanceProfile(Fsp,1,1)[0]
        Gammasp=self.resDict['Gamma2']
        S11=1
        Shat=[None for _ in range(len(Fsp))]
        for n in range(len(Fsp)):
            Fp=Fsp[n]
            Fp11=Fp[0][0]
            Fp12=Fp[0][1]
            Fp21=Fp[1][0]
            Fp22=Fp[1][1]
            dFp=Fp11*Fp22-Fp12*Fp21
            Gp=Gammasp[n][0][0]
            Shat[n]=(((rho*Fp22-dFp)*Gp+rho*Fp22-dFp)*S11+(Fp11-rho)*Gp+Fp11-rho)/((1+rho)*((dFp*Gp-Fp22)*S11-Gp*Fp11+1))
        Shatsp=si.sp.SParameters(Fsp.m_f,[[[s]] for s in Shat])
        #Shatsp.WriteToFile('Open2RawEquation.s1p')
        #resDict['Open2Measurement'].WriteToFile('Open2RawMeasured.s1p')
        self.assertTrue(self.SParametersAreEqual(Shatsp,resDict['Open2Measurement']),'raw open 2 measurement equation wrong')
    def testTDRRawMeasuredPort1Load(self):
        resDict=TestTDRErrorTermsTest.resDict
        # confirm equation for raw measured s-parameters at port 1 with load connected
        Fsp=self.resDict['Fixture1']
        rho=si.ip.ImpedanceProfile(Fsp,1,1)[0]
        Gammasp=self.resDict['Gamma1']
        S11=0
        Shat=[None for _ in range(len(Fsp))]
        for n in range(len(Fsp)):
            Fp=Fsp[n]
            Fp11=Fp[0][0]
            Fp12=Fp[0][1]
            Fp21=Fp[1][0]
            Fp22=Fp[1][1]
            dFp=Fp11*Fp22-Fp12*Fp21
            Gp=Gammasp[n][0][0]
            Shat[n]=(((rho*Fp22-dFp)*Gp+rho*Fp22-dFp)*S11+(Fp11-rho)*Gp+Fp11-rho)/((1+rho)*((dFp*Gp-Fp22)*S11-Gp*Fp11+1))
        Shatsp=si.sp.SParameters(Fsp.m_f,[[[s]] for s in Shat])
        #Shatsp.WriteToFile('Load1RawEquation.s1p')
        #resDict['Load1Measurement'].WriteToFile('Load1RawMeasured.s1p')
        self.assertTrue(self.SParametersAreEqual(Shatsp,resDict['Load1Measurement']),'raw load 1 measurement equation wrong')
    def testTDRRawMeasuredPort2Load(self):
        resDict=TestTDRErrorTermsTest.resDict
        # confirm equation for raw measured s-parameters at port 2 with load connected
        Fsp=self.resDict['Fixture2']
        rho=si.ip.ImpedanceProfile(Fsp,1,1)[0]
        Gammasp=self.resDict['Gamma2']
        S11=0
        Shat=[None for _ in range(len(Fsp))]
        for n in range(len(Fsp)):
            Fp=Fsp[n]
            Fp11=Fp[0][0]
            Fp12=Fp[0][1]
            Fp21=Fp[1][0]
            Fp22=Fp[1][1]
            dFp=Fp11*Fp22-Fp12*Fp21
            Gp=Gammasp[n][0][0]
            Shat[n]=(((rho*Fp22-dFp)*Gp+rho*Fp22-dFp)*S11+(Fp11-rho)*Gp+Fp11-rho)/((1+rho)*((dFp*Gp-Fp22)*S11-Gp*Fp11+1))
        Shatsp=si.sp.SParameters(Fsp.m_f,[[[s]] for s in Shat])
        #Shatsp.WriteToFile('Load2RawEquation.s1p')
        #resDict['Load1Measurement'].WriteToFile('Load2RawMeasured.s1p')
        self.assertTrue(self.SParametersAreEqual(Shatsp,resDict['Load2Measurement']),'raw load 2 measurement equation wrong')
    def testTDRMeasuredVoltagePort1Short(self):
        resDict=TestTDRErrorTermsTest.resDict
        # confirm equation for measured voltage with short connected
        Fsp=self.resDict['Fixture1']
        rho=si.ip.ImpedanceProfile(Fsp,1,1)[0]
        Gammasp=self.resDict['Gamma1']
        S11=-1
        V1=self.V1
        g1=self.g1
        sqZ0=math.sqrt(50)
        # m = (1/sqZ0)*(1-Gamma)/2*V
        Vhat=[None for _ in range(len(Fsp))]
        for n in range(len(Fsp)):
            Fp=Fsp[n]
            Fp11=Fp[0][0]
            Fp12=Fp[0][1]
            Fp21=Fp[1][0]
            Fp22=Fp[1][1]
            dFp=Fp11*Fp22-Fp12*Fp21
            Gp=Gammasp[n][0][0]
            m1=(1-Gp)/(2*sqZ0)*V1/self.fd.N
            Vhat[n]=((Fp22+dFp)*S11-1-Fp11)/((Fp22-dFp*Gp)*S11-1+Fp11*Gp)*sqZ0*m1*g1
        # multiply by N if you want the s-parameter viewer to show the waveform
        #Vhatsp=si.sp.SParameters(Fsp.m_f,[[[vh*self.fd.N]] for vh in Vhat])
        #Vhatsp.WriteToFile('ShortV1RawEquation.s1p')
        fceq=si.fd.FrequencyDomain(self.fd,Vhat)
        # because the frequency content is the amplitude of a sinewave, I have to halve the
        # value at DC and Nyquist.  I would not have to do that if it were just the DFT
        fceq[0]=fceq[0]/2.
        fceq[self.fd.N]=fceq[self.fd.N]/2.
        fc=si.fd.FrequencyContent(resDict['ShortV1'],self.fd)
        # multiply frequency content by N if you want the s-parameter viewer to show the waveform
        #si.sp.SParameters(fc.m_f,[[[fc[n]*self.fd.N*(2. if ((n==0) or (n==self.fd.N)) else 1.)]] for n in range(len(fc))]).WriteToFile('ShortV1Correct.s1p')
        self.assertEquals(fceq,fc,'short 1 voltage frequency content equation incorrect')
    def testTDRIncidentVoltagePort1Short(self):
        resDict=TestTDRErrorTermsTest.resDict
        # confirm equation for incident voltage with short connected
        Fsp=resDict['Fixture1']
        rho=si.ip.ImpedanceProfile(Fsp,1,1)[0]
        Gammasp=resDict['Gamma1']
        S11=-1
        V1=self.V1
        g1=self.g1
        sqZ0=math.sqrt(50)
        # m = (1/sqZ0)*(1-Gamma)/2*V
        vhat=[None for _ in range(len(Fsp))]
        for n in range(len(Fsp)):
            Fp=Fsp[n]
            Fp11=Fp[0][0]
            Fp12=Fp[0][1]
            Fp21=Fp[1][0]
            Fp22=Fp[1][1]
            dFp=Fp11*Fp22-Fp12*Fp21
            Gp=Gammasp[n][0][0]
            m1=(1-Gp)/(2*sqZ0)*V1/self.fd.N
            vhat[n]=(1+rho)/(1-rho*Gp)*sqZ0*m1*g1
        fceq=si.fd.FrequencyDomain(self.fd,vhat)
        # because the frequency content is the amplitude of a sinewave, I have to halve the
        # value at DC and Nyquist.  I would not have to do that if it were just the DFT
        fceq[0]=fceq[0]/2.
        fceq[self.fd.N]=fceq[self.fd.N]/2.
        # multiply by N if you want the s-parameter viewer to show the waveform
        #vhatsp=si.sp.SParameters(Fsp.m_f,[[[vh*self.fd.N]] for vh in vhat])
        #vhatsp.WriteToFile('ShortV1IncEquation.s1p')
        tdr=si.m.tdr.TDRWaveformToSParameterConverter(Step=False,fd=self.fd)
        tdr.Convert(self.resDict['ShortV1'])
        incfc=tdr.IncidentFrequencyContent
        # multiply frequency content by N  and by 2 at DC and Nyquist if you want the s-parameter viewer to show the waveform
        #si.sp.SParameters(incfc.m_f,[[[incfc[n]*self.fd.N*(2. if ((n==0) or (n==self.fd.N)) else 1.)]] for n in range(len(incfc))]).WriteToFile('ShortV1IncCorrect.s1p')
        self.assertEquals(fceq,incfc,'short 1 incident voltage frequency content equation incorrect')
    def testTDRMeasuredVoltagePort2Thru(self):
        resDict=TestTDRErrorTermsTest.resDict
        # confirm equation for measured voltage at port 2 with thru connected
        Fpsp=self.resDict['Fixture1']
        Gammapsp=self.resDict['Gamma1']
        Vp=self.V1
        go=self.g2
        Fosp=self.resDict['Fixture2']
        Gammaosp=self.resDict['Gamma2']
        sqZ0=math.sqrt(50)
        # m = (1/sqZ0)*(1-Gamma)/2*V
        Vhat=[None for _ in range(len(Fpsp))]
        for n in range(len(Fpsp)):
            Fp=Fpsp[n]
            Fp11=Fp[0][0]
            Fp12=Fp[0][1]
            Fp21=Fp[1][0]
            Fp22=Fp[1][1]
            dFp=Fp11*Fp22-Fp12*Fp21
            Gp=Gammapsp[n][0][0]
            Fo=Fosp[n]
            Fo11=Fo[0][0]
            Fo12=Fo[0][1]
            Fo21=Fo[1][0]
            Fo22=Fo[1][1]
            dFo=Fo11*Fo22-Fo12*Fo21
            Go=Gammaosp[n][0][0]
            m1=(1-Gp)/(2*sqZ0)*Vp/self.fd.N
            Vhat[n]=(Fo12*Fp21*(1+Go))/((dFp*Fo22-Fp11+(Fo11*Fp11-dFp*dFo)*Go)*Gp+(Fp22*dFo-Fo11)*Go-Fp22*Fo22+1)*sqZ0*m1*go
# 
#             m1=(1-Gp)/2.*Vp
#             Vhat[n]=(go*matrix([[0,1,0,1,0,0,0,0,0,0,0,0]])*\
#             (identity(12)-matrix(
#                 [[0,0,0,0,1,0,0,0,0,0,0,0],
#                  [0,0,0,0,0,1,0,0,0,0,0,0],
#                  [0,0,0,0,0,0,1,0,0,0,0,0],
#                  [0,0,0,0,0,0,0,1,0,0,0,0],
#                  [0,0,0,0,0,0,Gp,0,0,0,0,0],
#                  [0,0,0,0,0,0,0,Go,0,0,0,0],
#                  [0,0,0,0,Fp11,0,0,0,0,0,Fp12,0],
#                  [0,0,0,0,0,Fo11,0,0,0,0,0,Fo12],
#                  [0,0,0,0,Fp21,0,0,0,0,0,Fp22,0],
#                  [0,0,0,0,0,Fo21,0,0,0,0,0,Fo22],
#                  [0,0,0,0,0,0,0,0,0,1,0,0],
#                  [0,0,0,0,0,0,0,0,1,0,0,0]])).getI()*\
#                  matrix([[0],
#                          [0],
#                          [0],
#                          [0],
#                          [m1],
#                          [0],
#                          [0],
#                          [0],
#                          [0],
#                          [0],
#                          [0],
#                          [0]])).tolist()[0][0]
#             pass
        # multiply by N if you want the s-parameter viewer to show the waveform
        #Vhatsp=si.sp.SParameters(Fpsp.m_f,[[[vh*self.fd.N]] for vh in Vhat])
        #Vhatsp.WriteToFile('ThruV2RawEquation.s1p')
        fceq=si.fd.FrequencyDomain(self.fd,Vhat)
        # because the frequency content is the amplitude of a sinewave, I have to halve the
        # value at DC and Nyquist.  I would not have to do that if it were just the DFT
        fceq[0]=fceq[0]/2.
        fceq[self.fd.N]=fceq[self.fd.N]/2.
        fc=si.fd.FrequencyContent(self.resDict['Thru1V2'],self.fd)
        # multiply frequency content by N if you want the s-parameter viewer to show the waveform
        #si.sp.SParameters(fc.m_f,[[[fc[n]*self.fd.N*(2. if ((n==0) or (n==self.fd.N)) else 1.)]] for n in range(len(fc))]).WriteToFile('ThruV2Correct.s1p')
        self.assertEquals(fceq,fc,'thru 2 voltage frequency content equation incorrect')

if __name__ == "__main__":
        unittest.main()