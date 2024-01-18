"""
Simulator.py
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

from tkinter import messagebox

from SignalIntegrity.App.SParameterViewerWindow import SParametersDialog
from SignalIntegrity.App.ProgressDialog import ProgressDialog
from SignalIntegrity.App.EyeDiagramDialog import EyeDiagramDialog

from SignalIntegrity.App.SimulatorDialog import SimulatorDialog

import SignalIntegrity.App.Project

class Simulator(object):
    def __init__(self,parent):
        self.parent=parent
    def DeleteDialogs(self):
        if hasattr(self,'simulatorDialog'):
            if self.simulatorDialog.winfo_exists():
                self.simulatorDialog.destroy()
        if hasattr(self, 'eyeDiagramDialogs'):
            for key in self.eyeDiagramDialogs.keys():
                if self.eyeDiagramDialogs[key].winfo_exists():
                    self.eyeDiagramDialogs[key].destroy()
    def SimulatorDialog(self):
        if not hasattr(self,'simulatorDialog'):
            self.simulatorDialog=SimulatorDialog(self)
        if self.simulatorDialog == None:
            self.simulatorDialog=SimulatorDialog(self)
        else:
            if not self.simulatorDialog.winfo_exists():
                self.simulatorDialog=SimulatorDialog(self)
        return self.simulatorDialog
    def EyeDiagramDialog(self,name):
        if not hasattr(self,'eyeDiagramDialogs'):
            self.eyeDiagramDialogs={}
        if self.eyeDiagramDialogs == None:
            self.eyeDiagramDialogs={}
        if name not in self.eyeDiagramDialogs.keys():
            self.eyeDiagramDialogs[name]=EyeDiagramDialog(self,name)
        else:
            if not self.eyeDiagramDialogs[name].winfo_exists():
                self.eyeDiagramDialogs[name]=EyeDiagramDialog(self,name)
        return self.eyeDiagramDialogs[name]
    def UpdateWaveforms(self,outputWaveformList,outputWaveformLabels):
        self.SimulatorDialog().UpdateWaveforms(outputWaveformList,outputWaveformLabels).state('normal')
    def UpdateEyeDiagrams(self,eyeDiagramDict):
        import SignalIntegrity.Lib as si
        for eye in eyeDiagramDict:
            progressDialog=ProgressDialog(self.parent,"Eye Diagram Processing",self.EyeDiagramDialog(eye['Name']).SetEyeArgs(eye),self.EyeDiagramDialog(eye['Name']).UpdateWaveforms)
            try:
                progressDialog.GetResult()
            except si.SignalIntegrityException as e:
                messagebox.showerror('Eye Diagram',e.parameter+': '+e.message)
                return
    def _ProcessWaveforms(self,callback=None):
        return self.transferMatriceProcessor.ProcessWaveforms(self.inputWaveformList)

    def Simulate(self,TransferMatricesOnly=False):
        netList=self.parent.Drawing.schematic.NetList()
        netListText=netList.Text()
        import SignalIntegrity.Lib as si
        fd=SignalIntegrity.App.Project['CalculationProperties'].FrequencyList()
        cacheFileName=None
        if SignalIntegrity.App.Preferences['Cache.CacheResults']:
            cacheFileName=self.parent.fileparts.FileNameTitle()
        SignalIntegrity.App.Preferences['Calculation'].ApplyPreferences()
        snp=si.p.SimulatorNumericParser(fd,cacheFileName=cacheFileName,Z0=SignalIntegrity.App.Project['CalculationProperties.ReferenceImpedance'])
        snp.AddLines(netListText)
        # if the schematic can generate transfer parameters, let it run, otherwise, if it can't and there are no other
        # waveforms (i.e. eye waveforms or waveforms), then let it run through and fail.  If it can't generate transfer
        # parameters and there are eye waveforms, just skip over the transfer parameter generation.
        if TransferMatricesOnly or self.parent.TransferParametersDoer.active or len(self.parent.Drawing.schematic.OtherWaveforms()) == 0:
            progressDialog=ProgressDialog(self.parent,"Transfer Parameters",snp,snp.TransferMatrices, granularity=1.0)
            try:
                self.transferMatrices=progressDialog.GetResult()
            except si.SignalIntegrityException as e:
                messagebox.showerror('Simulator',e.parameter+': '+e.message)
                return

            self.outputWaveformLabels=netList.OutputNames()
            self.sourceNames=netList.SourceNames()

            if TransferMatricesOnly:
                buttonLabelList=[[out+' due to '+inp for inp in self.sourceNames] for out in self.outputWaveformLabels]
                maxLength=len(max([item for sublist in buttonLabelList for item in sublist],key=len))
                buttonLabelList=[[item.ljust(maxLength) for item in sublist] for sublist in buttonLabelList]
                sp=self.transferMatrices.SParameters()
                SParametersDialog(self.parent,sp,
                                  self.parent.fileparts.FullFilePathExtension('s'+str(sp.m_P)+'p'),
                                  'Transfer Parameters',buttonLabelList)
                return

            progressDialog=ProgressDialog(self.parent,"Input Waveforms",self.parent.Drawing.schematic,self.parent.Drawing.schematic.InputWaveforms, granularity=1.0)
            try:
                self.inputWaveformList=progressDialog.GetResult()
            except si.SignalIntegrityException as e:
                messagebox.showerror('Simulator',e.parameter+': '+e.message)
                return

            diresp=None
            for r in range(len(self.outputWaveformLabels)):
                for c in range(len(self.inputWaveformList)):
                    if self.outputWaveformLabels[r][:3]=='di/' or self.outputWaveformLabels[r][:2]=='d/':
                        if diresp == None:
                            diresp=si.fd.Differentiator(fd).Response()
                        #print 'differentiate: '+self.outputWaveformLabels[r]
                        for n in range(len(self.transferMatrices)):
                            self.transferMatrices[n][r][c]=self.transferMatrices[n][r][c]*diresp[n]

            if not SignalIntegrity.App.Project['CalculationProperties'].IsEvenlySpaced():
                fd=SignalIntegrity.App.Project['CalculationProperties'].FrequencyList(force_evenly_spaced = True)
                self.transferMatrices=self.transferMatrices.Resample(fd)

            self.transferMatriceProcessor=si.td.f.TransferMatricesProcessor(self.transferMatrices)
            SignalIntegrity.App.Preferences['Calculation'].ApplyPreferences()

            progressDialog = ProgressDialog(self.parent,"Frequency Responses",self.transferMatriceProcessor.TransferMatrices,self.transferMatriceProcessor.PrecalculateFrequencyResponses)
            try:
                result = progressDialog.GetResult()
                if result == None:
                    raise ValueError
            except:
                messagebox.showerror('Simulator','Frequency responses were not calculated')
                return

            def _PrecalculateImpulseReseponses():
                from SignalIntegrity.Lib.TimeDomain.Waveform.Waveform import Waveform
                return self.transferMatriceProcessor.PrecalculateImpulseResponses(
                    [wflm.td.Fs if isinstance(wflm,Waveform) and wflm.td is not None else None for wflm in self.inputWaveformList])

            progressDialog = ProgressDialog(self.parent,"Impulse Responses",self.transferMatriceProcessor.TransferMatrices,_PrecalculateImpulseReseponses)
            try:
                result = progressDialog.GetResult()
                if result == None:
                    raise ValueError
            except:
                messagebox.showerror('Simulator','Impulse responses were not calculated')
                return
        #Outer iterations loop for iterative nonlinear solutions - will repeat the processing of waveforms (convolution of input wavefrom to output) on 
        #each iteration and update values of dependent waveforms.
        #Have to repeat the above if statement at the beginning here since we want to only contain the ProcessWaveforms in the bottom loop - UGLY - see if necessary t 
        
        if(self.parent.Drawing.schematic.HasDependentSource()): #If have dependent source, do iterations
            iterations = SignalIntegrity.App.Project['CalculationProperties']['NumIterations']
            if iterations == None:
                iterations = 1 #Default behavior to avoid backwards compatibility issue with new iterative feature
        else:
            #Otherwise no iterations
            iterations = 1

        DISP_EVERY_ITERATION = SignalIntegrity.App.Preferences['ProjectFiles.PlotAllIterations'] and iterations > 1
        AUTOSHUTOFF_ITERATION = SignalIntegrity.App.Preferences['Calculation.AutoshutoffIterations'] and iterations > 1
        if (DISP_EVERY_ITERATION or AUTOSHUTOFF_ITERATION):
            allOutputWaveformList = []
            allOutputWaveformLabel = []


        for i in range(int(iterations)):
            if TransferMatricesOnly or self.parent.TransferParametersDoer.active or len(self.parent.Drawing.schematic.OtherWaveforms()) == 0:
                progressDialog=ProgressDialog(self.parent,"Waveform Processing",self.transferMatriceProcessor,self._ProcessWaveforms)
                try:
                    outputWaveformList = progressDialog.GetResult()
                except si.SignalIntegrityException as e:
                    messagebox.showerror('Simulator',e.parameter+': '+e.message)
                    return

                for r in range(len(outputWaveformList)):
                    if self.outputWaveformLabels[r][:3]=='di/' or self.outputWaveformLabels[r][:2]=='i/':
                        #print 'integrate: '+self.outputWaveformLabels[r]
                        outputWaveformList[r]=outputWaveformList[r].Integral()
            else:
                outputWaveformList = []
                self.outputWaveformLabels = []

            try:
                otherWaveformsTemp=self.parent.Drawing.schematic.OtherWaveforms()
                otherWaveformLabelsTemp=netList.WaveformNames()
                otherWaveforms=[]
                otherWaveformLabels=[]
                for wi in range(len(otherWaveformsTemp)):
                    if not otherWaveformsTemp[wi] is None:
                        otherWaveforms.append(otherWaveformsTemp[wi])
                        otherWaveformLabels.append(otherWaveformLabelsTemp[wi])
                del otherWaveformsTemp
                del otherWaveformLabelsTemp

                outputWaveformList+=otherWaveforms

                sourceNamesToShow=netList.SourceNamesToShow()
                otherWaveformLabels+=sourceNamesToShow
                outputWaveformList+=[self.inputWaveformList[self.sourceNames.index(snt)] for snt in sourceNamesToShow]
            except si.SignalIntegrityException as e:
                messagebox.showerror('Simulator',e.parameter+': '+e.message)
                return

            for outputWaveformIndex in range(len(outputWaveformList)):
                outputWaveform=outputWaveformList[outputWaveformIndex]
                outputWaveformLabel = (self.outputWaveformLabels+otherWaveformLabels)[outputWaveformIndex]
                for device in self.parent.Drawing.schematic.deviceList:
                    if device['partname'].GetValue() in ['Output',
                                                        'DifferentialVoltageOutput',
                                                        'CurrentOutput',
                                                        'EyeProbe',
                                                        'DifferentialEyeProbe',
                                                        'EyeWaveform',
                                                        'Waveform']:
                        if device['ref'].GetValue() == outputWaveformLabel:
                            # probes may have different kinds of gain specified
                            gainProperty = device['gain']
                            gain=gainProperty.GetValue()
                            offset=device['offset'].GetValue()
                            delay=device['td'].GetValue()
                            if gain != 1.0 or offset != 0.0 or delay != 0.0:
                                outputWaveform = outputWaveform.DelayBy(delay)*gain+offset
                            outputWaveformList[outputWaveformIndex]=outputWaveform
                            break

            #Having calculated intermediate output waveform values, can update all dependent waveforms now. 
            try:
                if (iterations > 1):
                    #First check output waveforms to see if they are all empty - implies impulse respones too long
                    allOutputsEmpty = True
                    for outputWaveform in outputWaveformList:
                        if (len(outputWaveform) > 1):
                            allOutputsEmpty = False
                            break
                    if (allOutputsEmpty):
                        messagebox.showerror('Simulator', 'Output waveforms empty: Decrease impulse response or increase waveform duration')
                        return
                    #Now if that is fine - try to update the waveform list
                    for inputWaveform in self.inputWaveformList:
                        if isinstance(inputWaveform, DependentWaveform):
                            inputWaveform.UpdateWaveform(self.outputWaveformLabels, outputWaveformList)

            except si.SignalIntegrityException as e: 
                messagebox.showerror('Simulator',e.parameter+': '+e.message)
                return


            if (DISP_EVERY_ITERATION or AUTOSHUTOFF_ITERATION):
                #Add all waveforms, both main output and "other" waveforms (manually loaded waveforms + displayed input waveforms)
                #This is for displaying all at end, mostly for debugging purposes
                allOutputWaveformList.append(outputWaveformList)
                allOutputWaveformLabel.append(self.outputWaveformLabels + otherWaveformLabels)

                if (AUTOSHUTOFF_ITERATION and i > 0): #If not on first iterations, compare to previous iteration to see if reached the end
                    converged = True
                    lastOuptutWaveformList = allOutputWaveformList[i-1]
                    for j in range(len(outputWaveformList)):
                        import numpy
                        #Go thorugh each waveform and calculate magnitude of change 
                        diffWvfm = outputWaveformList[j] - lastOuptutWaveformList[j]
                        magnChange = numpy.sqrt(numpy.mean(numpy.square(diffWvfm)))

                        #Calculate "changed" threshold based on average intensity of old waveform plus a user defined scaling factor
                        threshold = numpy.sqrt(numpy.mean(numpy.square(lastOuptutWaveformList[j])))*SignalIntegrity.App.Preferences['Calculation.AutoshutoffThreshold']

                        print(f"Iteration: {i}, Wvfm {j}, Change: {magnChange}, Threshold: {threshold}")


                        #Minimum threshold to avoid issue with close to 0 waveforms - kinda arbitrary
                        MIN_THRESHOLD = 1E-7
                        threshold = numpy.max([MIN_THRESHOLD, threshold])


                        #If change bigger than threshold, did not converge, so exit out
                        if (magnChange > threshold):
                            converged = False
                            break
                    
                    #If converged, can exit out of iteration script
                    if (converged):
                        #Update iteraitons to account for number of iterations actually done now
                        iterations = i + 1
                        break


                
        #Resampling happens outside of iterative solver, to keep dependent waveforms in most native time base and avoid unnecessary conversions

        userSampleRate=SignalIntegrity.App.Project['CalculationProperties.UserSampleRate']
        outputWaveformList = [wf.Adapt(
            si.td.wf.TimeDescriptor(wf.td.H,int(wf.td.K*userSampleRate/wf.td.Fs),userSampleRate))
                for wf in outputWaveformList[:len(self.outputWaveformLabels)]]+outputWaveformList[len(self.outputWaveformLabels):]
        outputWaveformLabels=self.outputWaveformLabels+otherWaveformLabels

        if (DISP_EVERY_ITERATION):
            #Unpacks the saved intermiate interatoin values one iteration at a time
            #Don't do final iteration since that will be "output values"
            for i in range(iterations-1):
                currOutputWaveformList = allOutputWaveformList[i]
                currOutputWaveformLabels = allOutputWaveformLabel[i]

                #Code could be cleaned up here so above lines aren't copy pasted
                currOutputWaveformList = [wf.Adapt(
                    si.td.wf.TimeDescriptor(wf.td.H,int(wf.td.K*userSampleRate/wf.td.Fs),userSampleRate))
                        for wf in currOutputWaveformList[:len(self.outputWaveformLabels)]]+currOutputWaveformList[len(self.outputWaveformLabels):]
                currOutputWaveformLabels = [currLabel + f"_it_{i}" for currLabel in currOutputWaveformLabels]

                #Now assign this to overall outputWaveformList + outputWaveformLabels which will be plotted 
                outputWaveformList += currOutputWaveformList
                outputWaveformLabels += currOutputWaveformLabels

        self.UpdateWaveforms(outputWaveformList, outputWaveformLabels)

        self.SimulatorDialog().title('Sim: '+self.parent.fileparts.FileNameTitle())
        self.SimulatorDialog().ExamineTransferMatricesDoer.Activate(True)
        self.SimulatorDialog().SimulateDoer.Activate(True)

        self.parent.root.update()
        # gather up the eye probes and create a dialog for each one
        eyeDiagramDict=[]
        for outputWaveformIndex in range(len(outputWaveformList)):
            outputWaveform=(outputWaveformList)[outputWaveformIndex]
            outputWaveformLabel = (outputWaveformLabels)[outputWaveformIndex]
            for device in self.parent.Drawing.schematic.deviceList:
                if device['partname'].GetValue() in ['EyeProbe','DifferentialEyeProbe','EyeWaveform']:
                    matched = device['ref'].GetValue() == outputWaveformLabel
                    if (DISP_EVERY_ITERATION and not matched):
                        for i in range(iterations):
                            #Check if match to "saved" waveform from previous iteration
                            #Not cleanest way to do this but not sure of an easy alternative
                            if (device['ref'].GetValue() + f"_it_{i}" == outputWaveformLabel):
                                matched = True
                                break
                    if matched:
                        if device['eyestate'].GetValue() == 'on':
                            eyeDict={'Name':outputWaveformLabel,
                                     'BaudRate':device['br'].GetValue(),
                                     'Waveform':(outputWaveformList)[(outputWaveformLabels).index(outputWaveformLabel)],
                                     'Config':device.configuration}
                            eyeDiagramDict.append(eyeDict)
                        break

                    #If saving intermiedate iterations - check for output match to an intermediate iteraiton and plot


        self.UpdateEyeDiagrams(eyeDiagramDict)

    def VirtualProbe(self,TransferMatricesOnly=False):
        netList=self.parent.Drawing.schematic.NetList()
        netListText=netList.Text()
        import SignalIntegrity.Lib as si
        cacheFileName=None
        if SignalIntegrity.App.Preferences['Cache.CacheResults']:
            cacheFileName=self.parent.fileparts.FileNameTitle()
        SignalIntegrity.App.Preferences['Calculation'].ApplyPreferences()
        snp=si.p.VirtualProbeNumericParser(
            SignalIntegrity.App.Project['CalculationProperties'].FrequencyList(),
            cacheFileName=cacheFileName,
            Z0=SignalIntegrity.App.Project['CalculationProperties.ReferenceImpedance'])
        snp.AddLines(netListText)
        progressDialog=ProgressDialog(self.parent,"Transfer Parameters",snp,snp.TransferMatrices, granularity=1.0)
        try:
            self.transferMatrices=progressDialog.GetResult()
        except si.SignalIntegrityException as e:
            messagebox.showerror('Virtual Probe',e.parameter+': '+e.message)
            return

        self.outputWaveformLabels=netList.OutputNames()
        self.sourceNames=netList.MeasureNames()

        if TransferMatricesOnly:
            buttonLabelList=[[out+' due to '+inp for inp in self.sourceNames] for out in self.outputWaveformLabels]
            maxLength=len(max([item for sublist in buttonLabelList for item in sublist],key=len))
            buttonLabelList=[[item.ljust(maxLength) for item in sublist] for sublist in buttonLabelList]
            sp=self.transferMatrices.SParameters()
            SParametersDialog(self.parent,sp,
                              self.parent.fileparts.FullFilePathExtension('s'+str(sp.m_P)+'p'),
                              'Transfer Parameters',buttonLabelList)
            return

        if not SignalIntegrity.App.Project['CalculationProperties'].IsEvenlySpaced():
            fd=SignalIntegrity.App.Project['CalculationProperties'].FrequencyList(force_evenly_spaced = True)
            self.transferMatrices=self.transferMatrices.Resample(fd)

        self.transferMatriceProcessor=si.td.f.TransferMatricesProcessor(self.transferMatrices)
        SignalIntegrity.App.Preferences['Calculation'].ApplyPreferences()

        try:
            self.inputWaveformList=self.parent.Drawing.schematic.InputWaveforms()
        except si.SignalIntegrityException as e:
            messagebox.showerror('Virtual Probe',e.parameter+': '+e.message)
            return

        progressDialog=ProgressDialog(self.parent,"Waveform Processing",self.transferMatriceProcessor,self._ProcessWaveforms)
        try:
            outputWaveformList = progressDialog.GetResult()
        except si.SignalIntegrityException as e:
            messagebox.showerror('Virtual Probe',e.parameter+': '+e.message)
            return

        try:
            otherWaveformsTemp=self.parent.Drawing.schematic.OtherWaveforms()
            otherWaveformLabelsTemp=netList.WaveformNames()
            otherWaveforms=[]
            otherWaveformLabels=[]
            for wi in range(len(otherWaveformsTemp)):
                if not otherWaveformsTemp[wi] is None:
                    otherWaveforms.append(otherWaveformsTemp[wi])
                    otherWaveformLabels.append(otherWaveformLabelsTemp[wi])
            del otherWaveformsTemp
            del otherWaveformLabelsTemp

            outputWaveformList+=otherWaveforms
            sourceNamesToShow=netList.SourceNamesToShow()
            otherWaveformLabels+=sourceNamesToShow
            outputWaveformList+=[self.inputWaveformList[self.sourceNames.index(snt)] for snt in sourceNamesToShow]
        except si.SignalIntegrityException as e:
            messagebox.showerror('Simulator',e.parameter+': '+e.message)
            return

        for outputWaveformIndex in range(len(outputWaveformList)):
            outputWaveform=outputWaveformList[outputWaveformIndex]
            outputWaveformLabel = (self.outputWaveformLabels+otherWaveformLabels)[outputWaveformIndex]
            for device in self.parent.Drawing.schematic.deviceList:
                if device['partname'].GetValue() in ['Output',
                                                     'DifferentialVoltageOutput',
                                                     'CurrentOutput',
                                                     'EyeProbe',
                                                     'DifferentialEyeProbe',
                                                     'EyeWaveform',
                                                     'Waveform']:
                    if device['ref'].GetValue() == outputWaveformLabel:
                        # probes may have different kinds of gain specified
                        gainProperty = device['gain']
                        gain=gainProperty.GetValue()
                        offset=device['offset'].GetValue()
                        delay=device['td'].GetValue()
                        if gain != 1.0 or offset != 0.0 or delay != 0.0:
                            outputWaveform = outputWaveform.DelayBy(delay)*gain+offset
                        outputWaveformList[outputWaveformIndex]=outputWaveform
                        break
        userSampleRate=SignalIntegrity.App.Project['CalculationProperties.UserSampleRate']
        outputWaveformList = [wf.Adapt(
            si.td.wf.TimeDescriptor(wf.td.H,int(wf.td.K*userSampleRate/wf.td.Fs),userSampleRate))
                for wf in outputWaveformList]
        self.SimulatorDialog().title('Virtual Probe: '+self.parent.fileparts.FileNameTitle())
        self.SimulatorDialog().ExamineTransferMatricesDoer.Activate(True)
        self.SimulatorDialog().SimulateDoer.Activate(True)
        outputWaveformLabels=self.outputWaveformLabels+otherWaveformLabels
        self.UpdateWaveforms(outputWaveformList, outputWaveformLabels)
        self.SimulatorDialog().update_idletasks()
        # gather up the eye probes and create a dialog for each one
        eyeDiagramDict=[]
        for outputWaveformIndex in range(len(outputWaveformList)):
            outputWaveform=outputWaveformList[outputWaveformIndex]
            outputWaveformLabel = outputWaveformLabels[outputWaveformIndex]
            for device in self.parent.Drawing.schematic.deviceList:
                if device['partname'].GetValue() in ['EyeProbe','DifferentialEyeProbe']:
                    if device['ref'].GetValue() == outputWaveformLabel:
                        if device['eyestate'].GetValue() == 'on':
                            eyeDict={'Name':outputWaveformLabel,
                                     'BaudRate':device['br'].GetValue(),
                                     'Waveform':outputWaveformList[self.outputWaveformLabels.index(outputWaveformLabel)],
                                     'Config':device.configuration}
                            eyeDiagramDict.append(eyeDict)
                        break
        self.UpdateEyeDiagrams(eyeDiagramDict)

