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

from numpy import matrix
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
    def __init__(self, methodName='runTest'):
        si.test.SParameterCompareHelper.__init__(self)
        unittest.TestCase.__init__(self,methodName)
        si.test.SignalIntegrityAppTestHelper.__init__(self,os.path.dirname(os.path.realpath(__file__)))
    def setRefProperty(self,project,ref,propertyname,value):
        devices=project.Drawing.schematic.deviceList
        for device in devices:
            partproperties=device.propertiesList
            for property in partproperties:
                if property['Keyword']=='ref' and property['Value']==ref:
                    for refproperty in partproperties:
                        if refproperty['Keyword']==propertyname:
                            #refproperty.SetValueFromString(str(value))
                            refproperty['Value']=value
                            return
        raise ValueError
    def setDevice(self,project,ref,name):
        self.setRefProperty(project,ref,'file',name+'.si')
    def setPulser(self,project,ref,value):
        self.setRefProperty(project,ref,'a',value)
    def convertTDR(self,fd,wfList,incidentIndex=0):
        tdr=si.m.tdr.TDRWaveformToSParameterConverter(Step=False,fd=fd)
        tdr.Convert(wfList,incidentIndex)
        return (tdr.IncidentWaveform,tdr.ReflectWaveforms,tdr.IncidentFrequencyContent,tdr.ReflectFrequencyContent)
    def testErrorTermsOld(self):
        return
        resDict={}
        print('S-Parameters')
        simName='Gamma1'
        print(simName)
        projName=simName+'.si'
        spProj=siapp.SignalIntegrityAppHeadless()
        spProj.OpenProjectFile(projName)
        (sp,name)=spProj.CalculateSParameters()
        resDict[simName]=sp
        simName='Gamma2'
        print(simName)
        projName=simName+'.si'
        spProj=siapp.SignalIntegrityAppHeadless()
        spProj.OpenProjectFile(projName)
        (sp,name)=spProj.CalculateSParameters()
        resDict[simName]=sp
        simName='Fixture1'
        print(simName)
        projName=simName+'.si'
        spProj=siapp.SignalIntegrityAppHeadless()
        spProj.OpenProjectFile(projName)
        (sp,name)=spProj.CalculateSParameters()
        resDict[simName]=sp
        simName='Fixture2'
        print(simName)
        projName=simName+'.si'
        spProj=siapp.SignalIntegrityAppHeadless()
        spProj.OpenProjectFile(projName)
        (sp,name)=spProj.CalculateSParameters()
        resDict[simName]=sp
        simName='Thru'
        print(simName)
        projName=simName+'.si'
        spProj=siapp.SignalIntegrityAppHeadless()
        spProj.OpenProjectFile(projName)
        (sp,name)=spProj.CalculateSParameters()
        resDict[simName]=sp
        simName='Short'
        print(simName)
        projName=simName+'.si'
        spProj=siapp.SignalIntegrityAppHeadless()
        spProj.OpenProjectFile(projName)
        (sp,name)=spProj.CalculateSParameters()
        resDict[simName+'1']=sp.PortReorder([0])
        resDict[simName+'2']=sp.PortReorder([1])
        simName='Open'
        print(simName)
        projName=simName+'.si'
        spProj=siapp.SignalIntegrityAppHeadless()
        spProj.OpenProjectFile(projName)
        (sp,name)=spProj.CalculateSParameters()
        resDict[simName+'1']=sp.PortReorder([0])
        resDict[simName+'2']=sp.PortReorder([1])
        simName='Load'
        print(simName)
        projName=simName+'.si'
        spProj=siapp.SignalIntegrityAppHeadless()
        spProj.OpenProjectFile(projName)
        (sp,name)=spProj.CalculateSParameters()
        resDict[simName+'1']=sp.PortReorder([0])
        resDict[simName+'2']=sp.PortReorder([1])
        print('TDR Simulations')
        tdrsim=siapp.SignalIntegrityAppHeadless()
        tdrsim.OpenProjectFile('TDRSimulation.si')
        simName=projName='Short'
        print(simName)
        self.setDevice(tdrsim,'DUT',projName)
        self.setPulser(tdrsim,'VG1',1.0)
        self.setPulser(tdrsim,'VG2',1.0)
        (sourceNames,outputWaveformLabels,transferMatrices,outputWaveformList)=tdrsim.Simulate()
        resDict.update(dict(zip([simName+label for label in outputWaveformLabels],outputWaveformList)))
        simName=projName='Open'
        print(simName)
        self.setDevice(tdrsim,'DUT',projName)
        self.setPulser(tdrsim,'VG1',1.0)
        self.setPulser(tdrsim,'VG2',1.0)
        (sourceNames,outputWaveformLabels,transferMatrices,outputWaveformList)=tdrsim.Simulate()
        resDict.update(dict(zip([simName+label for label in outputWaveformLabels],outputWaveformList)))
        simName=projName='Load'
        print(simName)
        self.setDevice(tdrsim,'DUT',projName)
        self.setPulser(tdrsim,'VG1',1.0)
        self.setPulser(tdrsim,'VG2',1.0)
        (sourceNames,outputWaveformLabels,transferMatrices,outputWaveformList)=tdrsim.Simulate()
        resDict.update(dict(zip([simName+label for label in outputWaveformLabels],outputWaveformList)))
        projName='Thru'
        simName=projName+'1'
        print(simName)
        self.setDevice(tdrsim,'DUT',projName)
        self.setPulser(tdrsim,'VG1',1.0)
        self.setPulser(tdrsim,'VG2',0.0)
        (sourceNames,outputWaveformLabels,transferMatrices,outputWaveformList)=tdrsim.Simulate()
        resDict.update(dict(zip([simName+label for label in outputWaveformLabels],outputWaveformList)))
        projName='Thru'
        simName=projName+'2'
        print(simName)
        self.setDevice(tdrsim,'DUT',projName)
        self.setPulser(tdrsim,'VG1',0.0)
        self.setPulser(tdrsim,'VG2',1.0)
        (sourceNames,outputWaveformLabels,transferMatrices,outputWaveformList)=tdrsim.Simulate()
        resDict.update(dict(zip([simName+label for label in outputWaveformLabels],outputWaveformList)))
        print('converting TDR')
        fd=si.fd.EvenlySpacedFrequencyList(100e9,1000)
        name='Short'
        (incwf,refwf,incfc,reffc)=self.convertTDR(fd,resDict[name+'V1'])
        resDict[name+'1_inc_wf']=incwf
        resDict[name+'1_ref_wf']=refwf[0]
        resDict[name+'1_inc_fc']=incfc
        resDict[name+'1_ref_fc']=reffc[0]
        (incwf,refwf,incfc,reffc)=self.convertTDR(fd,resDict[name+'V2'])
        resDict[name+'2_inc_wf']=incwf
        resDict[name+'2_ref_wf']=refwf[0]
        resDict[name+'2_inc_fc']=incfc
        resDict[name+'2_ref_fc']=reffc[0]

        # this is the relationship between the time domain waveforms and the freqency content
        sp=si.sp.SParameters(resDict[name+'1_inc_fc'].Frequencies(),[[[v*fd.N]] for v in resDict[name+'1_inc_fc'].Values()])
        sp[0][0][0]=sp[0][0][0]*2
        sp[fd.N][0][0]=sp[fd.N][0][0]*2
        sp.WriteToFile('TestInc.s1p')
        sp=si.sp.SParameters(resDict[name+'1_ref_fc'].Frequencies(),[[[v*fd.N]] for v in resDict[name+'1_ref_fc'].Values()])
        sp[0][0][0]=sp[0][0][0]*2
        sp[fd.N][0][0]=sp[fd.N][0][0]*2
        sp.WriteToFile('TestRef.s1p')

    def buildSimulations(self):
        self.alpha1=1.2
        self.alpha2=0.8
        self.beta1=self.alpha1
        self.beta2=self.alpha2
        self.V1=1.0
        self.V2=1.0
        print('Building Simulations')
        simName=projName='Short'
        print(simName)
        tdrsim=siapp.SignalIntegrityAppHeadless()
        tdrsim.OpenProjectFile('TDRSimulation.si')
        self.setRefProperty(tdrsim,'V1','gain',self.alpha1)
        self.setRefProperty(tdrsim,'V2','gain',self.alpha2)
        self.setRefProperty(tdrsim,'DUT','file',simName+'.si')
        self.setRefProperty(tdrsim, 'VG1', 'a', self.V1)
        self.setRefProperty(tdrsim, 'VG2', 'a', self.V2)   
        tdrsim.SaveProjectToFile('TDRSimulation'+simName+'.si')
        simName=projName='Open'
        print(simName)
        tdrsim=siapp.SignalIntegrityAppHeadless()
        tdrsim.OpenProjectFile('TDRSimulation.si')
        self.setRefProperty(tdrsim,'V1','gain',self.alpha1)
        self.setRefProperty(tdrsim,'V2','gain',self.alpha2)
        self.setRefProperty(tdrsim,'DUT','file',simName+'.si')
        self.setRefProperty(tdrsim, 'VG1', 'a', self.V1)
        self.setRefProperty(tdrsim, 'VG2', 'a', self.V2)   
        tdrsim.SaveProjectToFile('TDRSimulation'+simName+'.si')
        simName=projName='Load'
        print(simName)
        tdrsim=siapp.SignalIntegrityAppHeadless()
        tdrsim.OpenProjectFile('TDRSimulation.si')
        self.setRefProperty(tdrsim,'V1','gain',self.alpha1)
        self.setRefProperty(tdrsim,'V2','gain',self.alpha2)
        self.setRefProperty(tdrsim,'DUT','file',simName+'.si')
        self.setRefProperty(tdrsim, 'VG1', 'a', self.V1)
        self.setRefProperty(tdrsim, 'VG2', 'a', self.V2)   
        tdrsim.SaveProjectToFile('TDRSimulation'+simName+'.si')
        simName='Thru'
        projName=simName+'1'
        print(simName)
        tdrsim=siapp.SignalIntegrityAppHeadless()
        tdrsim.OpenProjectFile('TDRSimulation.si')
        self.setRefProperty(tdrsim,'V1','gain',self.alpha1)
        self.setRefProperty(tdrsim,'V2','gain',self.alpha2)
        self.setRefProperty(tdrsim,'DUT','file',simName+'.si')
        self.setRefProperty(tdrsim, 'VG1', 'a', self.V1)
        self.setRefProperty(tdrsim, 'VG2', 'a', 0.0)   
        tdrsim.SaveProjectToFile('TDRSimulation'+projName+'.si')
        simName='Thru'
        projName=simName+'2'
        print(simName)
        tdrsim=siapp.SignalIntegrityAppHeadless()
        tdrsim.OpenProjectFile('TDRSimulation.si')
        self.setRefProperty(tdrsim,'V1','gain',self.alpha1)
        self.setRefProperty(tdrsim,'V2','gain',self.alpha2)
        self.setRefProperty(tdrsim,'DUT','file',simName+'.si')
        self.setRefProperty(tdrsim, 'VG1', 'a', 0.0)
        self.setRefProperty(tdrsim, 'VG2', 'a', self.V2)   
        tdrsim.SaveProjectToFile('TDRSimulation'+projName+'.si')

    def testErrorTerms(self):
        self.buildSimulations()
        resDict={}
        print('S-Parameters')
        simName='Gamma1'
        print(simName)
        projName=simName+'.si'
        spProj=siapp.SignalIntegrityAppHeadless()
        spProj.OpenProjectFile(projName)
        (sp,name)=spProj.CalculateSParameters()
        resDict[simName]=sp
        simName='Gamma2'
        print(simName)
        projName=simName+'.si'
        spProj=siapp.SignalIntegrityAppHeadless()
        spProj.OpenProjectFile(projName)
        (sp,name)=spProj.CalculateSParameters()
        resDict[simName]=sp
        simName='Fixture1'
        print(simName)
        projName=simName+'.si'
        spProj=siapp.SignalIntegrityAppHeadless()
        spProj.OpenProjectFile(projName)
        (sp,name)=spProj.CalculateSParameters()
        resDict[simName]=sp
        simName='Fixture2'
        print(simName)
        projName=simName+'.si'
        spProj=siapp.SignalIntegrityAppHeadless()
        spProj.OpenProjectFile(projName)
        (sp,name)=spProj.CalculateSParameters()
        resDict[simName]=sp
        simName='Thru'
        print(simName)
        projName=simName+'.si'
        spProj=siapp.SignalIntegrityAppHeadless()
        spProj.OpenProjectFile(projName)
        (sp,name)=spProj.CalculateSParameters()
        resDict[simName]=sp
        simName='Short'
        print(simName)
        projName=simName+'.si'
        spProj=siapp.SignalIntegrityAppHeadless()
        spProj.OpenProjectFile(projName)
        (sp,name)=spProj.CalculateSParameters()
        resDict[simName+'1']=sp.PortReorder([0])
        resDict[simName+'2']=sp.PortReorder([1])
        simName='Open'
        print(simName)
        projName=simName+'.si'
        spProj=siapp.SignalIntegrityAppHeadless()
        spProj.OpenProjectFile(projName)
        (sp,name)=spProj.CalculateSParameters()
        resDict[simName+'1']=sp.PortReorder([0])
        resDict[simName+'2']=sp.PortReorder([1])
        simName='Load'
        print(simName)
        projName=simName+'.si'
        spProj=siapp.SignalIntegrityAppHeadless()
        spProj.OpenProjectFile(projName)
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
        fd=si.fd.EvenlySpacedFrequencyList(100e9,1000)
        name='Short'
        (incwf,refwf,incfc,reffc)=self.convertTDR(fd,resDict[name+'V1'])
        resDict[name+'1_inc_wf']=incwf
        resDict[name+'1_ref_wf']=refwf[0]
        resDict[name+'1_inc_fc']=incfc
        resDict[name+'1_ref_fc']=reffc[0]
        (incwf,refwf,incfc,reffc)=self.convertTDR(fd,resDict[name+'V2'])
        resDict[name+'2_inc_wf']=incwf
        resDict[name+'2_ref_wf']=refwf[0]
        resDict[name+'2_inc_fc']=incfc
        resDict[name+'2_ref_fc']=reffc[0]

        # this is the relationship between the time domain waveforms and the freqency content
        sp=si.sp.SParameters(resDict[name+'1_inc_fc'].Frequencies(),[[[v*fd.N]] for v in resDict[name+'1_inc_fc'].Values()])
        sp[0][0][0]=sp[0][0][0]*2
        sp[fd.N][0][0]=sp[fd.N][0][0]*2
        sp.WriteToFile('TestInc.s1p')
        sp=si.sp.SParameters(resDict[name+'1_ref_fc'].Frequencies(),[[[v*fd.N]] for v in resDict[name+'1_ref_fc'].Values()])
        sp[0][0][0]=sp[0][0][0]*2
        sp[fd.N][0][0]=sp[fd.N][0][0]*2
        sp.WriteToFile('TestRef.s1p')

        # now I want to measure the K*g term
        self.K1g=resDict[name+'1_inc_fc']
        self.K2g=resDict[name+'2_inc_fc']
        
        

if __name__ == "__main__":
        unittest.main()