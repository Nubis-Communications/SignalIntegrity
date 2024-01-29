"""
StepWaveform.py
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

from SignalIntegrity.Lib.TimeDomain.Waveform.Waveform import Waveform
from SignalIntegrity.Lib.TimeDomain.Waveform.TimeDescriptor import TimeDescriptor
from SignalIntegrity.Lib.Exception import SignalIntegrityExceptionDependentWaveform
import SignalIntegrity.App.ProjectFile
import math
import numpy as np

class DependentWaveform(Waveform):
    """step waveform"""
    def __init__(self, OutputPortName, TransformFN, VariablesList = []):
        """Constructor  
        constructs a dependent waveform, whose value depends on the measured output probe value through an arbitrary transform function. 
        @param outputPortName output port whose voltage is taken as input into transformation function 
            Expects either string of port names separated by comma, or a list of strings with each port name
        @param transformFN file name of function which transforms ouptutPort's voltage into the new voltage of this waveform.
        @param VaraiblesList list of device variables that can be utilized by transform file
        """ 
        if (isinstance(OutputPortName, str)):
            self.OutputPortName = [s.strip() for s in OutputPortName.split(',')]
        elif (isinstance(OutputPortName, list) and isinstance(OutputPortName[0], str)):
            self.OutputPortName = OutputPortName
        else:
            raise SignalIntegrityExceptionDependentWaveform(
                    'Incorrect argumetn type for OutputPortName: ' + (OutputPortName))
        
        self.TransformFN = TransformFN
        self.VariablesList = VariablesList
        super().__init__(TimeDescriptor(0, 1, 100E9)) #Default is a blank waveform

    def UpdateWaveform(self, OutputWaveformLabels, OutputWaveformList):

        allOutputPorts =  self.OutputPortName #Get all port names

        #Dictionary of input waveforms to send to function
        inputWaveforms = {}

        #Read in all of the input waveforms into inputWaveforms dictionary
        for i in range(len(allOutputPorts)):
            if (allOutputPorts[i] in OutputWaveformLabels):
                inputWaveforms[allOutputPorts[i]] = OutputWaveformList[OutputWaveformLabels.index(allOutputPorts[i])]
            else:
                raise SignalIntegrityExceptionDependentWaveform(
                    'dependent output port not found: ' + (allOutputPorts[i]))
                return
            
        #Set up arguments ot pass to transform function 
        sendargs = inputWaveforms
        
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
                        f"Systtem variable not found: {value}"
                    )
            if variable['Type'] in ['file','string','enum']:
                sendargs[variable['Name']]=str(value)
            elif variable['Type'] == 'float':
                sendargs[variable['Name']]=float(value)
            elif variable['Type'] == 'int':
                sendargs[variable['Name']]=int(value)


        returnargs = {'outputWaveform': Waveform()}

        #Read in transform function
        try:
            file = open(self.TransformFN,"r") 
        except FileNotFoundError:
            raise SignalIntegrityExceptionDependentWaveform('transform file not found: '+(self.TransformFN))
        equations = file.read()
        file.close()
        #Perform transformation
        returnargs = DependentWaveform.EvaluateTransformFunctionSafely(equations, sendargs, returnargs)
            
        super().__init__(x=returnargs['outputWaveform'])

    @staticmethod
    def EvaluateTransformFunctionSafely(equations, sendargs, returnargs):
        #Assumes input waveform called inputWaveform in file, and output waveform stored in variable outputVariable
        for argkey in sendargs.keys():
            #arg=sendargs[argkey]
            exec(argkey+' = sendargs[argkey]')
        try:
            exec(equations)
        except Exception:
            import traceback
            #Handles arbitrary excpetion since any could occur realistically
            raise SignalIntegrityExceptionDependentWaveform('Excpetion occured in trnasform file: ' + traceback.format_exc())
        for argkey in returnargs.keys():
            try:
                exec(str("returnargs[argkey] = eval(argkey)"))
            except NameError:
                raise SignalIntegrityExceptionDependentWaveform('Transform file does not set output variable: ' +argkey)
        return returnargs 