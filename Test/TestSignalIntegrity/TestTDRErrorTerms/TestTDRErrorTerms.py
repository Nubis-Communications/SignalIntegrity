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
        self.g1=1.2
        self.g2=0.8
        self.V1=1.0
        self.V2=1.0
        print('Building Simulations')
        simName=projName='Short'
        print(simName)
        tdrsim=siapp.SignalIntegrityAppHeadless()
        tdrsim.OpenProjectFile('TDRSimulation.si')
        self.setRefProperty(tdrsim,'V1','gain',self.g1)
        self.setRefProperty(tdrsim,'V2','gain',self.g2)
        self.setRefProperty(tdrsim,'DUT','file',simName+'.si')
        self.setRefProperty(tdrsim, 'VG1', 'a', self.V1)
        self.setRefProperty(tdrsim, 'VG2', 'a', self.V2)   
        tdrsim.SaveProjectToFile('TDRSimulation'+simName+'.si')
        simName=projName='Open'
        print(simName)
        tdrsim=siapp.SignalIntegrityAppHeadless()
        tdrsim.OpenProjectFile('TDRSimulation.si')
        self.setRefProperty(tdrsim,'V1','gain',self.g1)
        self.setRefProperty(tdrsim,'V2','gain',self.g2)
        self.setRefProperty(tdrsim,'DUT','file',simName+'.si')
        self.setRefProperty(tdrsim, 'VG1', 'a', self.V1)
        self.setRefProperty(tdrsim, 'VG2', 'a', self.V2)   
        tdrsim.SaveProjectToFile('TDRSimulation'+simName+'.si')
        simName=projName='Load'
        print(simName)
        tdrsim=siapp.SignalIntegrityAppHeadless()
        tdrsim.OpenProjectFile('TDRSimulation.si')
        self.setRefProperty(tdrsim,'V1','gain',self.g1)
        self.setRefProperty(tdrsim,'V2','gain',self.g2)
        self.setRefProperty(tdrsim,'DUT','file',simName+'.si')
        self.setRefProperty(tdrsim, 'VG1', 'a', self.V1)
        self.setRefProperty(tdrsim, 'VG2', 'a', self.V2)   
        tdrsim.SaveProjectToFile('TDRSimulation'+simName+'.si')
        simName='Thru'
        projName=simName+'1'
        print(simName)
        tdrsim=siapp.SignalIntegrityAppHeadless()
        tdrsim.OpenProjectFile('TDRSimulation.si')
        self.setRefProperty(tdrsim,'V1','gain',self.g1)
        self.setRefProperty(tdrsim,'V2','gain',self.g2)
        self.setRefProperty(tdrsim,'DUT','file',simName+'.si')
        self.setRefProperty(tdrsim, 'VG1', 'a', self.V1)
        self.setRefProperty(tdrsim, 'VG2', 'a', 0.0)   
        tdrsim.SaveProjectToFile('TDRSimulation'+projName+'.si')
        simName='Thru'
        projName=simName+'2'
        print(simName)
        tdrsim=siapp.SignalIntegrityAppHeadless()
        tdrsim.OpenProjectFile('TDRSimulation.si')
        self.setRefProperty(tdrsim,'V1','gain',self.g1)
        self.setRefProperty(tdrsim,'V2','gain',self.g2)
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
        tdr=si.m.tdr.TDRWaveformToSParameterConverter(Step=False,fd=fd)
        tdr.Convert(resDict[name+'V1'],0)
        resDict[name+'1_inc_wf']=tdr.IncidentWaveform
        resDict[name+'1_ref_wf']=tdr.ReflectWaveforms[0]
        resDict[name+'1_inc_fc']=tdr.IncidentFrequencyContent
        resDict[name+'1_ref_fc']=tdr.ReflectFrequencyContent[0]
        tdr.Convert(resDict[name+'V2'],0)
        (incwf,refwf,incfc,reffc)=self.convertTDR(fd,resDict[name+'V2'])
        resDict[name+'2_inc_wf']=tdr.IncidentWaveform
        resDict[name+'2_ref_wf']=tdr.ReflectWaveforms[0]
        resDict[name+'2_inc_fc']=tdr.IncidentFrequencyContent
        resDict[name+'2_ref_fc']=tdr.ReflectFrequencyContent[0]

        # this is the relationship between the time domain waveforms and the freqency content
        sp=si.sp.SParameters(resDict[name+'1_inc_fc'].Frequencies(),[[[v*fd.N]] for v in resDict[name+'1_inc_fc'].Values()])
        sp[0][0][0]=sp[0][0][0]*2
        sp[fd.N][0][0]=sp[fd.N][0][0]*2
        sp.WriteToFile('TestInc.s1p')
        sp=si.sp.SParameters(resDict[name+'1_ref_fc'].Frequencies(),[[[v*fd.N]] for v in resDict[name+'1_ref_fc'].Values()])
        sp[0][0][0]=sp[0][0][0]*2
        sp[fd.N][0][0]=sp[fd.N][0][0]*2
        sp.WriteToFile('TestRef.s1p')

        cs=si.m.calkit.CalibrationKit(f=fd)

        short1measurement=tdr.RawMeasuredSParameters(resDict['ShortV1'])
        short2measurement=tdr.RawMeasuredSParameters(resDict['ShortV2'])
        open1measurement=tdr.RawMeasuredSParameters(resDict['OpenV1'])
        open2measurement=tdr.RawMeasuredSParameters(resDict['OpenV2'])
        load1measurement=tdr.RawMeasuredSParameters(resDict['LoadV1'])
        load2measurement=tdr.RawMeasuredSParameters(resDict['LoadV2'])
        thrumeasurement=tdr.RawMeasuredSParameters([[resDict['Thru1V1'],resDict['Thru1V2']],[resDict['Thru2V1'],resDict['Thru2V2']]])

        cmTDR=si.m.cal.Calibration(2,fd,[
            si.m.cal.ReflectCalibrationMeasurement(short1measurement.FrequencyResponse(1,1),cs.shortStandard,0,'Short1'),
            si.m.cal.ReflectCalibrationMeasurement(open1measurement.FrequencyResponse(1,1),cs.openStandard,0,'Open1'),
            si.m.cal.ReflectCalibrationMeasurement(load1measurement.FrequencyResponse(1,1),cs.loadStandard,0,'Load1'),
            si.m.cal.ReflectCalibrationMeasurement(short2measurement.FrequencyResponse(1,1),cs.shortStandard,1,'Short2'),
            si.m.cal.ReflectCalibrationMeasurement(open2measurement.FrequencyResponse(1,1),cs.openStandard,1,'Open2'),
            si.m.cal.ReflectCalibrationMeasurement(load2measurement.FrequencyResponse(1,1),cs.loadStandard,1,'Load2'),
            si.m.cal.ThruCalibrationMeasurement(thrumeasurement.FrequencyResponse(1,1),thrumeasurement.FrequencyResponse(2,1),cs.thruStandard,0,1,'Thru1'),
            si.m.cal.ThruCalibrationMeasurement(thrumeasurement.FrequencyResponse(2,2),thrumeasurement.FrequencyResponse(1,2),cs.thruStandard,1,0,'Thru2'),
            ])

        #cmTDR.WriteToFile('calibration.l12t').WriteFixturesToFiles('ErrorTermFixture')

        # calculate the error terms using equations
        F1sp=resDict['Fixture1']
        rho1=si.ip.ImpedanceProfile(F1sp,1,1)[0]
        Gamma1sp=resDict['Gamma1']
        g1=self.g1
        F2sp=resDict['Fixture2']
        rho2=si.ip.ImpedanceProfile(F2sp,1,1)[0]
        Gamma2sp=resDict['Gamma2']
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
        cmEq=si.m.cal.Calibration(2,fd)
        cmEq.ET=ET
        #cmEq.WriteFixturesToFiles('TwoPortCalEquations')

        FixturesActual=cmTDR.Fixtures()
        FixturesEquations=cmEq.Fixtures()

        for p in range(len(FixturesActual)):
            self.assertTrue(self.SParametersAreEqual(FixturesActual[p],FixturesEquations[p]),'Fixture '+str(p+1)+' not equal')

        # confirm equation for raw measured s-parameters at port 1 with short connected
        Fsp=resDict['Fixture1']
        rho=si.ip.ImpedanceProfile(Fsp,1,1)[0]
        Gammasp=resDict['Gamma1']
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
        #short1measurement.WriteToFile('Short1RawMeasured.s1p')
        self.assertTrue(self.SParametersAreEqual(Shatsp,short1measurement),'raw short 1 measurement equation wrong')

        # confirm equation for raw measured s-parameters at port 2 with short connected
        Fsp=resDict['Fixture2']
        rho=si.ip.ImpedanceProfile(Fsp,1,1)[0]
        Gammasp=resDict['Gamma2']
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
        #short2measurement.WriteToFile('Short2RawMeasured.s1p')
        self.assertTrue(self.SParametersAreEqual(Shatsp,short2measurement),'raw short 2 measurement equation wrong')

        # confirm equation for raw measured s-parameters at port 1 with open connected
        Fsp=resDict['Fixture1']
        rho=si.ip.ImpedanceProfile(Fsp,1,1)[0]
        Gammasp=resDict['Gamma1']
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
        #open1measurement.WriteToFile('Open1RawMeasured.s1p')
        self.assertTrue(self.SParametersAreEqual(Shatsp,open1measurement),'raw open 1 measurement equation wrong')

        # confirm equation for raw measured s-parameters at port 2 with open connected
        Fsp=resDict['Fixture2']
        rho=si.ip.ImpedanceProfile(Fsp,1,1)[0]
        Gammasp=resDict['Gamma2']
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
        #open2measurement.WriteToFile('Open2RawMeasured.s1p')
        self.assertTrue(self.SParametersAreEqual(Shatsp,open2measurement),'raw open 2 measurement equation wrong')

        # confirm equation for raw measured s-parameters at port 1 with load connected
        Fsp=resDict['Fixture1']
        rho=si.ip.ImpedanceProfile(Fsp,1,1)[0]
        Gammasp=resDict['Gamma1']
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
        #load1measurement.WriteToFile('Load1RawMeasured.s1p')
        self.assertTrue(self.SParametersAreEqual(Shatsp,load1measurement),'raw load 1 measurement equation wrong')

        # confirm equation for raw measured s-parameters at port 2 with load connected
        Fsp=resDict['Fixture2']
        rho=si.ip.ImpedanceProfile(Fsp,1,1)[0]
        Gammasp=resDict['Gamma2']
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
        #load1measurement.WriteToFile('Load2RawMeasured.s1p')
        self.assertTrue(self.SParametersAreEqual(Shatsp,load2measurement),'raw load 2 measurement equation wrong')

        # confirm equation for measured voltage with short connected
        Fsp=resDict['Fixture1']
        rho=si.ip.ImpedanceProfile(Fsp,1,1)[0]
        Gammasp=resDict['Gamma1']
        S11=-1
        V=self.V1
        g=self.g1
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
            Vhat[n]=((Fp22+dFp)*S11-1-Fp11)/((Fp22-dFp*Gp)*S11-1+Fp11*Gp)*(1-Gp)/2*V*g
        Vhatsp=si.sp.SParameters(Fsp.m_f,[[[vh]] for vh in Vhat])
        Vhatsp.WriteToFile('ShortV1RawEquation.s1p')

        # confirm equation for incident voltage with short connected
        Fsp=resDict['Fixture1']
        rho=si.ip.ImpedanceProfile(Fsp,1,1)[0]
        Gammasp=resDict['Gamma1']
        S11=-1
        V=self.V1
        g=self.g1
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
            vhat[n]=(1+rho)/(1-rho*Gp)*(1-Gp)/2*V*g
        vhatsp=si.sp.SParameters(Fsp.m_f,[[[vh]] for vh in vhat])
        vhatsp.WriteToFile('ShortV1IncEquation.s1p')

        # confirm equation for measured voltage at port 2 with thru connected
        Fpsp=resDict['Fixture1']
        Gammapsp=resDict['Gamma1']
        Vp=self.V1
        go=self.g2
        Fosp=resDict['Fixture2']
        Gammaosp=resDict['Gamma2']
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
            Vhat[n]=(Fo12*Fp21*(1+Go))/((dFp*Fo22-Fp11+(Fo11*Fp11-dFp*dFo)*Go)*Gp+(Fp22*dFo-Fo11)*Go-Fp22*Fo22+1)*(1-Gp)/2*Vp*go
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

        Vhatsp=si.sp.SParameters(Fpsp.m_f,[[[vh]] for vh in Vhat])
        Vhatsp.WriteToFile('ShortV2ThruRawEquation.s1p')


        return


        return


if __name__ == "__main__":
        unittest.main()