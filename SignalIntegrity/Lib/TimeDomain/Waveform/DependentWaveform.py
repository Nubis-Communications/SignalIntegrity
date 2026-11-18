"""
DependentWaveform.py
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

from SignalIntegrity.Lib.TimeDomain.Waveform.Waveform import Waveform
from SignalIntegrity.Lib.TimeDomain.Waveform.TimeDescriptor import TimeDescriptor
from SignalIntegrity.Lib.Exception import SignalIntegrityExceptionDependentWaveform
import SignalIntegrity.App.ProjectFile
import os
import sys

class DependentWaveform(Waveform):
    """A waveform whose value depends on measured output probes and an embedded script."""
    def __init__(self, OutputPortName, VariablesList=None, outputWaveformName='outputWaveform', script=None):
        """Constructs a dependent waveform using embedded script text.
        @param outputPortName output port whose voltage is taken as input into transformation function 
            Expects either string of port names separated by comma, or a list of strings with each port name
        @param VariablesList list of device variables available to the script
        """ 
        if script is None:
            raise SignalIntegrityExceptionDependentWaveform('embedded waveform processor script is required')
        if (isinstance(OutputPortName, str)):
            self.OutputPortName = [s.strip() for s in OutputPortName.split(',')]
        elif (isinstance(OutputPortName, list) and isinstance(OutputPortName[0], str)):
            self.OutputPortName = OutputPortName
        else:
            raise SignalIntegrityExceptionDependentWaveform(
                    'Incorrect argument type for OutputPortName: ' + (OutputPortName))
        
        self.Script = script
        self.VariablesList = [] if VariablesList is None else VariablesList
        self.OutputWaveformName = outputWaveformName
        self.ProcessorOutputs = [self]
        self.ProjectVariables = None

        self.td = None
        list.__init__(self, [0]) #Default is a blank waveform

    @staticmethod
    def UpdateWaveforms(dependentWaveforms, OutputWaveformLabels, OutputWaveformList,
                        iteration=None, noise_spectral_densities=None):
        """Execute each processor once, updating all of its outputs together."""
        updated=set()
        for waveform in dependentWaveforms:
            if id(waveform) in updated:
                continue
            waveform.UpdateWaveform(OutputWaveformLabels,OutputWaveformList,iteration,
                                    noise_spectral_densities=noise_spectral_densities)
            updated.add(id(waveform))
            updated.update(id(output) for output in waveform.ProcessorOutputs)

    def UpdateWaveform(self, OutputWaveformLabels, OutputWaveformList, iteration=None,
                       noise_spectral_densities=None):
        """Update from measured waveforms and their statistical noise spectra.

        @param noise_spectral_densities optional dict of probe name to SpectralDensity.
        Scripts receive independent input_noise_1, input_noise_2, ... objects alongside
        input_waveform_1, input_waveform_2, ... . Simulation supplies spectra on its
        calculation frequency grid. Direct calls and previews without a noise mapping
        receive zero spectra on each input waveform's frequency grid.

        Variables marked ReadOnly (Output Variable in the UI) are passed in and
        written back after successful execution, for subsequent iterations and saves.
        A linked output retains its =reference and writes to that system variable.
        All outputs belonging to this processor are updated by the same execution.
        """
        import copy
        from SignalIntegrity.Lib.FrequencyDomain.SpectralDensity import SpectralDensity

        allOutputPorts =  self.OutputPortName #Get all port names

        #Dictionary of input waveforms to send to function
        inputWaveforms = {}
        inputWaveformAliases = {}

        #Read in all of the input waveforms into inputWaveforms dictionary
        for i in range(len(allOutputPorts)):
            if (allOutputPorts[i] in OutputWaveformLabels):
                inputWaveform = OutputWaveformList[OutputWaveformLabels.index(allOutputPorts[i])]
                inputWaveforms[allOutputPorts[i]] = inputWaveform
                inputWaveformAliases['input_waveform_' + str(i+1)] = inputWaveform
                if noise_spectral_densities is None:
                    frequencies=inputWaveform.td.FrequencyList()
                    noise=SpectralDensity(frequencies,[0.]*len(frequencies),
                                          Keven=inputWaveform.td.K % 2 == 0)
                else:
                    if allOutputPorts[i] not in noise_spectral_densities:
                        raise SignalIntegrityExceptionDependentWaveform(
                            'dependent input noise spectrum not found: '+allOutputPorts[i])
                    noise=noise_spectral_densities[allOutputPorts[i]]
                    if not isinstance(noise,SpectralDensity):
                        raise SignalIntegrityExceptionDependentWaveform(
                            'dependent input noise must be a SpectralDensity: '+allOutputPorts[i])
                    noise=copy.deepcopy(noise)
                inputWaveformAliases['input_noise_' + str(i+1)] = noise
            else:
                raise SignalIntegrityExceptionDependentWaveform(
                    'dependent output port not found: ' + (allOutputPorts[i]))
                return
            
        #Set up arguments to pass to the waveform processor script.
        sendargs = inputWaveforms
        # 0-based index of the iteration that just completed; device variables of the same name override it
        sendargs['iteration'] = iteration
        
        #Transferring variables list to a dictionary
        outputTargets={}
        for i in range(len(self.VariablesList)):
            variable = self.VariablesList[i]
            target=variable
            value = variable['Value']
            if value is None:
                value=''
            if value.startswith("="):
                #Check if a system variable 

                projectVariables=(SignalIntegrity.App.Project['Variables']
                                  if self.ProjectVariables is None else self.ProjectVariables)
                if value[1:] in projectVariables.Names():
                    target=projectVariables.VariableByName(value[1:])
                    value=projectVariables.Dictionary()[value[1:]]
                else:
                    raise SignalIntegrityExceptionDependentWaveform(
                        f"System variable not found: {value}"
                    )
            if variable['ReadOnly']:
                outputTargets[variable['Name']]=target
            try:
                if variable['Type'] in ['file','string','enum']:
                    sendargs[variable['Name']]=str(value)
                elif variable['Type'] == 'float':
                    sendargs[variable['Name']]=float(value)
                elif variable['Type'] == 'int':
                    sendargs[variable['Name']]=int(value)
            except (TypeError,ValueError,OverflowError) as error:
                raise SignalIntegrityExceptionDependentWaveform(
                    'invalid '+variable['Type']+' value for variable '+variable['Name']+
                    ': '+str(error)) from error

        sendargs.update(inputWaveformAliases)

        outputVariables=[variable for variable in self.VariablesList if variable['ReadOnly']]
        returnargs = {output.OutputWaveformName: Waveform() for output in self.ProcessorOutputs}
        returnargs.update({variable['Name']:sendargs[variable['Name']]
                           for variable in outputVariables})

        equations=self.Script
        projectDir=os.getcwd()
        if projectDir not in sys.path:
            sys.path.insert(0, projectDir)
        #Perform transformation
        returnargs = DependentWaveform.EvaluateTransformFunctionSafely(equations, sendargs, returnargs)

        waveforms=[]
        for output in self.ProcessorOutputs:
            waveform=returnargs[output.OutputWaveformName]
            if not isinstance(waveform,Waveform):
                raise SignalIntegrityExceptionDependentWaveform(
                    'waveform processor output must be a Waveform: '+output.OutputWaveformName)
            waveforms.append(Waveform(waveform))

        variableValues=[]
        for variable in outputVariables:
            value=self.OutputVariableValue(variable,returnargs[variable['Name']])
            target=outputTargets[variable['Name']]
            if target is not variable:
                value=self.OutputVariableValue(target,value)
            variableValues.append((target,str(value)))

        # Commit only after every returned waveform and variable has been validated.
        for output,waveform in zip(self.ProcessorOutputs,waveforms):
            Waveform.__init__(output,x=waveform)
        for variable,value in variableValues:
            variable['Value']=value

    @staticmethod
    def OutputVariableValue(variable,value):
        """Validate an output against its interface and destination variable types."""
        try:
            if variable['Type'] == 'float':
                return float(value)
            if variable['Type'] == 'int':
                integer=int(value)
                if not isinstance(value,str) and integer != value:
                    raise ValueError('integer output must not have a fractional part')
                return integer
            return str(value)
        except (TypeError,ValueError,OverflowError) as error:
            raise SignalIntegrityExceptionDependentWaveform(
                'invalid '+variable['Type']+' output variable '+variable['Name']+
                ': '+str(error)) from error

    @staticmethod
    def EvaluateTransformFunctionSafely(equations, sendargs, returnargs):
        namespace = globals().copy()
        namespace.update(sendargs)
        try:
            exec(str(equations), namespace, namespace)
        except Exception:
            import traceback
            #Handles arbitrary exception since any could occur realistically
            raise SignalIntegrityExceptionDependentWaveform('Exception occurred in waveform processor script: ' + traceback.format_exc())
        for argkey in returnargs.keys():
            if argkey not in namespace:
                raise SignalIntegrityExceptionDependentWaveform('waveform processor script does not set output variable: ' +argkey)
            returnargs[argkey] = namespace[argkey]
        return returnargs 
