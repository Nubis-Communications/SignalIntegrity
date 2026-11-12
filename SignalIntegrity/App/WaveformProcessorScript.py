"""Parse declarative interface metadata embedded in waveform processor scripts."""

import json
import keyword
import copy

from SignalIntegrity.App.ProjectFile import VariableConfiguration


_START_MARKER='# <waveform-processor-interface>'
_END_MARKER='# </waveform-processor-interface>'
_VARIABLE_FIELDS={'name','description','type','default','units','visible','read_only','in_cache'}
_VARIABLE_TYPES={'int','float','string','enum','file'}


def ParseWaveformProcessorInterface(script):
    lines=script.splitlines()
    starts=[index for index,line in enumerate(lines) if line.strip() == _START_MARKER]
    ends=[index for index,line in enumerate(lines) if line.strip() == _END_MARKER]
    if len(starts) != 1 or len(ends) != 1 or starts[0] >= ends[0]:
        raise ValueError('script must contain one well-formed waveform processor interface block')

    metadataLines=[]
    for line in lines[starts[0]+1:ends[0]]:
        stripped=line.strip()
        if not stripped.startswith('#'):
            raise ValueError('each interface metadata line must be a Python comment')
        metadataLines.append(stripped[1:].lstrip())
    try:
        metadata=json.loads('\n'.join(metadataLines))
    except json.JSONDecodeError as error:
        raise ValueError('interface metadata must be valid JSON: '+str(error)) from error

    if not isinstance(metadata,dict) or metadata.get('version') != 1:
        raise ValueError('interface metadata version must be 1')
    if set(metadata) != {'version','ports','variables'}:
        raise ValueError('interface metadata must contain only version, ports, and variables')

    ports=metadata['ports']
    if not isinstance(ports,dict) or set(ports) != {'inputs','outputs'}:
        raise ValueError('ports must contain inputs and outputs')
    inputPorts=ports['inputs']
    outputPorts=ports['outputs']
    if type(inputPorts) is not int or inputPorts < 1:
        raise ValueError('ports.inputs must be a positive integer')
    if type(outputPorts) is not int or outputPorts < 1:
        raise ValueError('ports.outputs must be a positive integer')

    variables=metadata['variables']
    if not isinstance(variables,list):
        raise ValueError('variables must be a list')
    variableConfigurations=[]
    names=set()
    for variable in variables:
        if not isinstance(variable,dict) or not {'name','type','default'}.issubset(variable):
            raise ValueError('each variable requires name, type, and default fields')
        if set(variable)-_VARIABLE_FIELDS:
            raise ValueError('variable contains unknown fields: '+', '.join(sorted(set(variable)-_VARIABLE_FIELDS)))
        name=variable['name']
        variableType=variable['type']
        default=variable['default']
        if not isinstance(name,str) or not name.isidentifier() or keyword.iskeyword(name):
            raise ValueError('variable names must be valid Python identifiers')
        if name in names:
            raise ValueError('variable names must be unique: '+name)
        names.add(name)
        if variableType not in _VARIABLE_TYPES:
            raise ValueError('unsupported variable type for '+name+': '+str(variableType))
        if isinstance(default,bool) or not isinstance(default,(str,int,float)):
            raise ValueError('variable default must be a string, integer, or number: '+name)

        description=variable.get('description','')
        units=variable.get('units','')
        visible=variable.get('visible',True)
        readOnly=variable.get('read_only',False)
        inCache=variable.get('in_cache',True)
        if not isinstance(description,str) or not isinstance(units,str):
            raise ValueError('variable description and units must be strings: '+name)
        if type(visible) is not bool or type(readOnly) is not bool or type(inCache) is not bool:
            raise ValueError('variable visible, read_only, and in_cache fields must be booleans: '+name)

        configuration=VariableConfiguration()
        configuration['Name']=name
        configuration['Description']=description
        configuration['Type']=variableType
        configuration['Value']=str(default)
        configuration['Units']=units
        configuration['Visible']=visible
        configuration['ReadOnly']=readOnly
        configuration['InCache']=inCache
        if not configuration.CheckValidity():
            raise ValueError('invalid variable definition: '+name)
        variableConfigurations.append(configuration)

    return inputPorts,outputPorts,variableConfigurations


def ReconcileProcessorVariables(existingVariables,importedVariables):
    existingByName={variable['Name']:variable for variable in existingVariables}
    importedNames={variable['Name'] for variable in importedVariables}
    reconciled=[]
    for importedVariable in importedVariables:
        variable=copy.deepcopy(importedVariable)
        existingVariable=existingByName.get(variable['Name'])
        if existingVariable is not None and existingVariable['Type'] == variable['Type']:
            variable['Value']=existingVariable['Value']
        reconciled.append(variable)
    removedNames=[variable['Name'] for variable in existingVariables
                  if variable['Name'] not in importedNames]
    return reconciled,removedNames


def CreateWaveformProcessorFromScript(script):
    inputPorts,outputPorts,variables=ParseWaveformProcessorInterface(script)
    from SignalIntegrity.App.Device import DeviceWaveformProcessorVariable

    device=DeviceWaveformProcessorVariable(inputPorts,outputPorts)
    device['script']['Value']=script
    device.variablesList=variables
    return device