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

        self.td = None
        list.__init__(self, [0]) #Default is a blank waveform

    def UpdateWaveform(self, OutputWaveformLabels, OutputWaveformList, iteration=None):

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
            else:
                raise SignalIntegrityExceptionDependentWaveform(
                    'dependent output port not found: ' + (allOutputPorts[i]))
                return
            
        #Set up arguments to pass to the waveform processor script.
        sendargs = inputWaveforms
        # 0-based index of the iteration that just completed; device variables of the same name override it
        sendargs['iteration'] = iteration
        
        #Transferring variables list to a dictionary
        for i in range(len(self.VariablesList)):
            variable = self.VariablesList[i]
            value = variable['Value']
            if value[0] == "=":
                #Check if a system variable 

                projectVariables=SignalIntegrity.App.Project['Variables'].Dictionary()
                if (value[1:] in projectVariables):
                    value = projectVariables[value[1:]]
                else:
                    raise SignalIntegrityExceptionDependentWaveform(
                        f"System variable not found: {value}"
                    )
            if variable['Type'] in ['file','string','enum']:
                sendargs[variable['Name']]=str(value)
            elif variable['Type'] == 'float':
                sendargs[variable['Name']]=float(value)
            elif variable['Type'] == 'int':
                sendargs[variable['Name']]=int(value)

        sendargs.update(inputWaveformAliases)

        returnargs = {self.OutputWaveformName: Waveform()}

        equations=self.Script
        projectDir=os.getcwd()
        if projectDir not in sys.path:
            sys.path.insert(0, projectDir)
        #Perform transformation
        returnargs = DependentWaveform.EvaluateTransformFunctionSafely(equations, sendargs, returnargs)
            
        super().__init__(x=returnargs[self.OutputWaveformName])

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
