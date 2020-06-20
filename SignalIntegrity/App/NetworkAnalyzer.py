"""
NetworkAnalyzer.py
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

import sys
import os

if sys.version_info.major < 3:
    import Tkinter as tk
    import tkMessageBox as messagebox
else:
    import tkinter as tk
    from tkinter import messagebox

from SignalIntegrity.App.ProgressDialog import ProgressDialog
from SignalIntegrity.App.SignalIntegrityAppHeadless import SignalIntegrityAppHeadless
from SignalIntegrity.App.Simulator import SimulatorDialog
from SignalIntegrity.App.Files import FileParts
from SignalIntegrity.Lib.Exception import SignalIntegrityException,SignalIntegrityExceptionNetworkAnalyzer

import copy,os

import SignalIntegrity.App.Project

class NetworkAnalyzerSimulator(object):
    def __init__(self,parent):
        self.parent=parent
    def SimulatorDialog(self):
        if not hasattr(self,'simulatorDialog'):
            self.simulatorDialog=SimulatorDialog(self)
        if self.simulatorDialog == None:
            self.simulatorDialog=SimulatorDialog(self)
        else:
            if not self.simulatorDialog.winfo_exists():
                self.simulatorDialog=SimulatorDialog(self)
        return self.simulatorDialog
    def UpdateWaveforms(self,outputWaveformList,outputWaveformLabels):
        self.SimulatorDialog().UpdateWaveforms(outputWaveformList,outputWaveformLabels).state('normal')
    def _ProcessWaveforms(self,callback=None):
        self.outputwflist=[]
        for port in range(len(self.wflist)):
            self.outputwflist.append(self.transferMatriceProcessor.ProcessWaveforms(self.wflist[port],adaptToLargest=True))
    def Simulate(self,SParameters=False):
        """
        simulates with a network analyzer model
        """
        #
        # the first step is to calculate the s-parameters of a DUT connected to the ports
        # of the network analyzer.
        #
        self.parent.Drawing.stateMachine.Nothing()
        netList=self.parent.Drawing.schematic.NetList().Text()
        import SignalIntegrity.Lib as si
        fd=si.fd.EvenlySpacedFrequencyList(
                SignalIntegrity.App.Project['CalculationProperties.EndFrequency'],
                SignalIntegrity.App.Project['CalculationProperties.FrequencyPoints'])
        cacheFileName=None
        if SignalIntegrity.App.Preferences['Cache.CacheResults']:
            cacheFileName=self.parent.fileparts.FileNameTitle()+'_DUTSParameters'
        si.sd.Numeric.trySVD=SignalIntegrity.App.Preferences['Calculation.TrySVD']
        spnp=si.p.DUTSParametersNumericParser(fd,cacheFileName=cacheFileName)
        spnp.AddLines(netList)
        progressDialog = ProgressDialog(self.parent,"Calculating DUT S-parameters",spnp,spnp.SParameters,granularity=1.0)
        try:
            (DUTSp,NetworkAnalyzerProjectFile)=progressDialog.GetResult()
            showDutsp=False
            if showDutsp:
                from SignalIntegrity.App.SParameterViewerWindow import SParametersDialog
                self.spd=self.spd=SParametersDialog(self.parent,DUTSp,filename=self.parent.fileparts.FullFilePathExtension('s'+str(DUTSp.m_P)+'p'))
        except si.SignalIntegrityException as e:
            messagebox.showerror('DUT S-parameter Calculator',e.parameter+': '+e.message)
            return None
        #
        # DUTSp now contains the s-parameters of the DUT.  The DUT has a number of ports dictated by how many ports were actually connected
        # to the network analzyer, and the port connections are in spnp.NetworkAnalyzerPortConnectionList
        #
        # The next step is to get the netlist from the network analyzer model's project
        #
        netListText=None
        if NetworkAnalyzerProjectFile != None:
            level=SignalIntegrityAppHeadless.projectStack.Push()
            try:
                app=SignalIntegrityAppHeadless()
                if app.OpenProjectFile(os.path.realpath(NetworkAnalyzerProjectFile)):
                    app.Drawing.DrawSchematic()
                    netList=app.Drawing.schematic.NetList()
                    netListText=netList.Text()
                else:
                    raise SignalIntegrityExceptionNetworkAnalyzer('file could not be opened: '+NetworkAnalyzerProjectFile)
            except SignalIntegrityException as e:
                messagebox.showerror('Network Analyzer Model: ',e.parameter+': '+e.message)
            finally:
                SignalIntegrityAppHeadless.projectStack.Pull(level)
        else:
            netList=self.parent.Drawing.schematic.NetList()
            netListText=self.parent.NetListText()
        if netListText==None:
            return
        #
        # Now, with the dut s-parameters and the netlist of the network analyzer model, get the transfer matrices for a simulation with the DUT
        # using the network analyzer model.
        #
        cacheFileName=self.parent.fileparts.FileNameTitle()+'_TransferMatrices' if SignalIntegrity.App.Preferences['Cache.CacheResults'] else None
        si.sd.Numeric.trySVD=SignalIntegrity.App.Preferences['Calculation.TrySVD']
        snp=si.p.NetworkAnalyzerSimulationNumericParser(fd,DUTSp,spnp.NetworkAnalyzerPortConnectionList,cacheFileName=cacheFileName)
        snp.AddLines(netListText)
        progressDialog = ProgressDialog(self.parent,"Calculating Transfer Matrices",snp,snp.TransferMatrices,granularity=1.0)
        level=SignalIntegrityAppHeadless.projectStack.Push()
        try:
            os.chdir(FileParts(os.path.abspath(NetworkAnalyzerProjectFile)).AbsoluteFilePath())
            self.transferMatrices=progressDialog.GetResult()
        except si.SignalIntegrityException as e:
            messagebox.showerror('Transfer Matrices Calculation: ',e.parameter+': '+e.message)
            return None
        finally:
            SignalIntegrityAppHeadless.projectStack.Pull(level)
        self.sourceNames=snp.m_sd.SourceVector()
        #
        # to clear up any confusion, if the DUT was not connected to all of the network analyzer ports, a multi-port DUT with
        # opens on the unconnected ports was constructed and connected as the DUT, but it was remembered which network
        # analyzer ports are actually driven.  The driven ports, in order, are the first names in self.sourceNames with
        # snp.simulationNumPorts containing the number of them.
        #
        # In other words, if a single-port reflect calibration is performed on port 2 of the network analyzer, a two-port
        # DUT was installed, with an open on port 1, and the transfer parameters were computed for only the outputs needed
        # (the superfluous probe outputs were removed).  self.sourceNames would contain only the reference designator for
        # the transmitter that is on port 2, followed by any other waveforms supplied to the system (usuaully noise).
        #
        # Now, we loop over all of the transmitters that are driven and create a list of lists, where each element in the list
        # is a list of input waveforms to be used in the simulation under that driven condition.  We do this by first, setting
        # all of the transmitters in the appropriate on/off state, and then gathering all of the waveforms.
        #
        gdoDict={}
        self.wflist=[]
        if NetworkAnalyzerProjectFile != None:
            level=SignalIntegrityAppHeadless.projectStack.Push()
            try:
                app=SignalIntegrityAppHeadless()
                if app.OpenProjectFile(os.path.realpath(NetworkAnalyzerProjectFile)):
                    app.Drawing.DrawSchematic()
                    # get output gain, offset, delay
                    for name in [rdn[2] for rdn in snp.m_sd.pOutputList]:
                        gdoDict[name]={'gain':float(app.Device(name)['gain']['Value']),
                            'offset':float(app.Device(name)['offset']['Value']),'delay':float(app.Device(name)['td']['Value'])}
                    for driven in range(snp.simulationNumPorts):
                        for port in range(snp.simulationNumPorts):
                            app.Device(self.sourceNames[port])['state']['Value']='on' if port==driven else 'off'
                        self.wflist.append([app.Device(self.sourceNames[wfIndex]).Waveform() for wfIndex in range(len(self.sourceNames))])
                else:
                    raise SignalIntegrityExceptionNetworkAnalyzer('file could not be opened: '+NetworkAnalyzerProjectFile)
            except SignalIntegrityException as e:
                messagebox.showerror('Network Analyzer Model: ',e.parameter+': '+e.message)
            finally:
                SignalIntegrityAppHeadless.projectStack.Pull(level)
        else:
            # since we're modifying the current schematic, keep the state for restoring
            stateList=[app.Device(self.sourceNames[port])['state']['Value'] for port in range(snp.simulationNumPorts)]
            for name in [rdn[2] for rdn in snp.m_sd.pOutputList]:
                gdoDict[name]={'gain':float(app.Device()[name]['gain']['Value']),'offset':float(app.Device()[name]['offset']['Value']),
                               'delay':float(app.Device()[name]['td']['Value'])}
            for driven in range(snp.simulationNumPorts):
                for port in range(snp.simulationNumPorts):
                    app.Device(self.sourceNames[port])['state']['Value']='on' if port==driven else 'off'
                self.wflist.append([app.Device(self.sourceNames[wfIndex]).Waveform() for wfIndex in range(len(self.sourceNames))])
            # restore the states
            for port in range(snp.simulationNumPorts):
                app.Device(self.sourceNames[port])['state']['Value']=stateList[port]
        #
        # Now, the list of list of input waveforms are processed, generating a list of list of output waveforms in 
        # self.outputwflist.
        #
        self.transferMatriceProcessor=si.td.f.TransferMatricesProcessor(self.transferMatrices)
        si.td.wf.Waveform.adaptionStrategy='SinX' if SignalIntegrity.App.Preferences['Calculation.UseSinX'] else 'Linear'
        progressDialog=ProgressDialog(self.parent,"Waveform Processing",self.transferMatriceProcessor,self._ProcessWaveforms)
        try:
            outputWaveformList = progressDialog.GetResult()
        except si.SignalIntegrityException as e:
            messagebox.showerror('Simulator',e.parameter+': '+e.message)
            return
        #
        # The list of list of input waveforms have been processed processed, generating a list of list of output waveforms in 
        # self.outputwflist.  The names of the output waveforms are in snp.m_sd.pOutputList.
        #
        self.outputwflist = [[wf.Adapt(si.td.wf.TimeDescriptor(wf.td[wf.td.IndexOfTime(-5e-9)],fd.TimeDescriptor().K,wf.td.Fs)) for wf in driven] for driven in self.outputwflist]

        # The port connection list, which is a list of True or False for each port on the network analyzer, is
        # converted to a list of network port indices corresponding to the driven ports.
        #
        portConnections=[]
        for pci in range(len(snp.PortConnectionList)):
            if snp.PortConnectionList[pci]: portConnections.append(pci)

        # Here, the output waveforms are refined by applying any probe gain, offset, and delay, and the
        # waveform labels are converted to a list of list of waveform labels, with the driven port appended.
        outputWaveformList=[]
        self.outputWaveformLabels=[]
        for r in range(len(self.outputwflist)):
            wflist=self.outputwflist[r]
            for c in range(len(wflist)):
                wf=wflist[c]; wfName=snp.m_sd.pOutputList[c][2]
                gain=gdoDict[wfName]['gain']; offset=gdoDict[wfName]['offset']; delay=gdoDict[wfName]['delay']
                if gain != 1.0 or offset != 0.0 or delay != 0.0:
                    wf = wf.DelayBy(delay)*gain+offset
                outputWaveformList.append(wf)
                self.outputWaveformLabels.append(wfName+str(portConnections[r]+1))

        userSampleRate=SignalIntegrity.App.Project['CalculationProperties.UserSampleRate']
        outputWaveformList = [wf.Adapt(
            si.td.wf.TimeDescriptor(wf.td.H,int(wf.td.K*userSampleRate/wf.td.Fs),userSampleRate))
                for wf in outputWaveformList]

        td=si.td.wf.TimeDescriptor(-5e-9,
           SignalIntegrity.App.Project['CalculationProperties.TimePoints'],
           SignalIntegrity.App.Project['CalculationProperties.BaseSampleRate'])
        frequencyList=td.FrequencyList()

        if snp.simulationType != 'CW':
            # note this matrix is transposed from what is normally expected
            Vmat=[[outputWaveformList[self.outputWaveformLabels.index('V'+str(portConnections[r]+1)+str(portConnections[c]+1))]
                for r in range(len(portConnections))]
                    for c in range(len(portConnections))]

            for vli in range(len(Vmat)):
                tdr=si.m.tdr.TDRWaveformToSParameterConverter(
                    WindowForwardHalfWidthTime=500e-12,
                    WindowReverseHalfWidthTime=500e-12,
                    WindowRaisedCosineDuration=250e-12,
                    Step=(snp.simulationType=='TDRStep'),
                    Length=0,
                    Denoise=(snp.simulationType !='TDRStep'),
                    DenoisePercent=20.,
                    Inverted=False,
                    fd=frequencyList
                 )

                tdr.Convert(Vmat[vli],vli)
                for r in range(len(portConnections)):
                    outputWaveformList.append(tdr.IncidentWaveform if r==vli else si.td.wf.Waveform(td))
                    self.outputWaveformLabels.append('A'+str(portConnections[r]+1)+str(portConnections[vli]+1))
                for r in range(len(portConnections)):
                    outputWaveformList.append(tdr.ReflectWaveforms[r])
                    self.outputWaveformLabels.append('B'+str(portConnections[r]+1)+str(portConnections[vli]+1))

        if not SParameters:
            self.SimulatorDialog().title('Sim: '+self.parent.fileparts.FileNameTitle())
            self.SimulatorDialog().ExamineTransferMatricesDoer.Activate(True)
            self.SimulatorDialog().SimulateDoer.Activate(True)
            self.SimulatorDialog().ViewTimeDomainDoer.Set(snp.simulationType != 'CW')
            self.SimulatorDialog().ViewTimeDomainDoer.Activate(snp.simulationType != 'CW')
            self.SimulatorDialog().ViewSpectralContentDoer.Set(snp.simulationType == 'CW')
            self.SimulatorDialog().ViewSpectralDensityDoer.Set(False)
            self.UpdateWaveforms(outputWaveformList, self.outputWaveformLabels)
        else:
            frequencyContentList=[wf.FrequencyContent(fd) for wf in outputWaveformList]

            Afc=[[frequencyContentList[self.outputWaveformLabels.index('A'+str(portConnections[r]+1)+str(portConnections[c]+1))]
                for c in range(len(portConnections))]
                    for r in range(len(portConnections))]
            Bfc=[[frequencyContentList[self.outputWaveformLabels.index('B'+str(portConnections[r]+1)+str(portConnections[c]+1))]
                for c in range(len(portConnections))]
                    for r in range(len(portConnections))]

            from numpy import matrix

            data=[None for _ in range(len(frequencyList))]
            for n in range(len(frequencyList)):
                B=[[Bfc[r][c][n] for c in range(snp.simulationNumPorts)] for r in range(snp.simulationNumPorts)]
                A=[[Afc[r][c][n] for c in range(snp.simulationNumPorts)] for r in range(snp.simulationNumPorts)]
                data[n]=(matrix(B)*matrix(A).getI()).tolist()
            sp=si.sp.SParameters(frequencyList,data)
            return sp
