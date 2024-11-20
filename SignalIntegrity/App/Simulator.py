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
            SignalIntegrity.App.Preferences['Cache'].ApplyPreferences()
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
                from SignalIntegrity.Lib.TimeDomain.Waveform.DCWaveform import DCWaveform
                return self.transferMatriceProcessor.PrecalculateImpulseResponses(
                    [wflm.td.Fs if (isinstance(wflm,Waveform) and not isinstance(wflm,DCWaveform)) else None for wflm in self.inputWaveformList])

            progressDialog = ProgressDialog(self.parent,"Impulse Responses",self.transferMatriceProcessor.TransferMatrices,_PrecalculateImpulseReseponses)
            try:
                result = progressDialog.GetResult()
                if result == None:
                    raise ValueError
            except:
                messagebox.showerror('Simulator','Impulse responses were not calculated')
                return

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

        noise_list = [owf.noise if hasattr(owf,'noise') else None for owf in outputWaveformList]
        noiseWaveformList = []
        noiseWaveformLabels = []
        noise_rms_list=[]
        noise_rms_label_list=[]
        for wf,noise,label in zip(outputWaveformList,noise_list,self.outputWaveformLabels+otherWaveformLabels):
            from SignalIntegrity.Lib.FrequencyDomain.FrequencyContent import FrequencyContent
            from SignalIntegrity.Lib.ToSI import ToSI
            import numpy as np
            if not noise is None:
                wffc=wf
                if not isinstance(wffc,si.td.wf.DCWaveform):
                    if wffc.td.K//2*2 != wffc.td.K:
                        import copy
                        wffc=copy.deepcopy(wf)
                        td=wffc.td
                        td.K=td.K-1
                        wffc=wffc.Adapt(td)
                fc=FrequencyContent(wffc)
                fd=fc.FrequencyList()
                phase_list=np.exp(1j*np.random.uniform(0.,2*np.pi,size=len(fd)))
                noise_content=noise.Resample(fd)
                # import matplotlib.pyplot as plt
                # plt.cla()
                # plt.plot(noise.Frequencies('GHz'),noise.Values('dB'),label=label+' before')
                # plt.plot(noise_content.Frequencies('GHz'),noise_content.Values('dB'),label=label+' after')
                # plt.legend()
                # plt.show()
                root_delta_f=np.sqrt(fd.Fe/fd.N)
                sqrt2=np.sqrt(2) # sqrt to take it from rms to amplitude for the dft
                for n in range(len(noise_content)):
                    fc[n]=noise_content[n]*root_delta_f*(1./sqrt2 if n in [0,fd.N] else sqrt2)*(1. if n in [0,fd.N] else phase_list[n])
                noise_wf=fc.Waveform()
                rms=np.sqrt(np.mean(np.square(noise_wf)))
                noise_rms_list.append(rms)
                noise_rms_label_list.append(label)
                print('rms value of '+label+'_noise: '+ToSI(rms,'V'))
                noiseWaveformList.append(noise_wf)
                noiseWaveformLabels.append(label+'_noise')
        otherWaveformLabels+=noiseWaveformLabels
        outputWaveformList+=noiseWaveformList

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
                        if device['ac_coupled'].GetValue() == 'true':
                            import numpy as np
                            outputWaveform = outputWaveform - np.mean(outputWaveform)
                        if gain != 1.0 or offset != 0.0 or delay != 0.0:
                            outputWaveform = outputWaveform.DelayBy(delay)*gain+offset
                            if outputWaveformLabel+'_noise' in (self.outputWaveformLabels+otherWaveformLabels):
                                # apply the gain to the noise, as well
                                noise_rms_list[noise_rms_label_list.index(outputWaveformLabel)]*=gain
                                outputWaveformList[(self.outputWaveformLabels+otherWaveformLabels).index(outputWaveformLabel+'_noise')]*=gain
                        outputWaveformList[outputWaveformIndex]=outputWaveform
                        break

        userSampleRate=SignalIntegrity.App.Project['CalculationProperties.UserSampleRate']
        outputWaveformList = [wf.Adapt(
            si.td.wf.TimeDescriptor(wf.td.H,int(wf.td.K*userSampleRate/wf.td.Fs),userSampleRate))
                for wf in outputWaveformList[:len(self.outputWaveformLabels)]]+outputWaveformList[len(self.outputWaveformLabels):]
        outputWaveformList = [wf.TrueWaveform() for wf in outputWaveformList]
        for n in range(len(noise_list)):
            if not noise_list[n] is None:
                outputWaveformList[n].noise = noise_list[n]
        self.SimulatorDialog().title('Sim: '+self.parent.fileparts.FileNameTitle())
        self.SimulatorDialog().ExamineTransferMatricesDoer.Activate(True)
        self.SimulatorDialog().SimulateDoer.Activate(True)
        outputWaveformLabels=self.outputWaveformLabels+otherWaveformLabels
        self.UpdateWaveforms(outputWaveformList, outputWaveformLabels)
        self.parent.root.update()
        # gather up the eye probes and create a dialog for each one
        eyeDiagramDict=[]
        for outputWaveformIndex in range(len(outputWaveformList)):
            outputWaveform=(outputWaveformList)[outputWaveformIndex]
            outputWaveformLabel = (outputWaveformLabels)[outputWaveformIndex]
            for device in self.parent.Drawing.schematic.deviceList:
                if device['partname'].GetValue() in ['EyeProbe','DifferentialEyeProbe','EyeWaveform']:
                    if device['ref'].GetValue() == outputWaveformLabel:
                        if device['eyestate'].GetValue() == 'on':
                            external_noise = 0.0
                            if outputWaveformLabel in noise_rms_label_list:
                                external_noise=noise_rms_list[noise_rms_label_list.index(outputWaveformLabel)]
                            eyeDict={'Name':outputWaveformLabel,
                                     'BaudRate':device['br'].GetValue(),
                                     'Waveform':(outputWaveformList)[(outputWaveformLabels).index(outputWaveformLabel)],
                                     'Config':device.configuration,
                                     'ExternalNoise':external_noise}
                            eyeDiagramDict.append(eyeDict)
                        break
        self.UpdateEyeDiagrams(eyeDiagramDict)

    def VirtualProbe(self,TransferMatricesOnly=False):
        netList=self.parent.Drawing.schematic.NetList()
        netListText=netList.Text()
        import SignalIntegrity.Lib as si
        cacheFileName=None
        if SignalIntegrity.App.Preferences['Cache.CacheResults']:
            cacheFileName=self.parent.fileparts.FileNameTitle()
            SignalIntegrity.App.Preferences['Cache'].ApplyPreferences()
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
                        if device['ac_coupled'].GetValue() == 'true':
                            import numpy as np
                            outputWaveform = outputWaveform - np.mean(outputWaveform)
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

