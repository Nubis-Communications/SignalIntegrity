'''
Created on Jun 3, 2020

@author: petep
'''

import sys
import copy
import SignalIntegrity.Lib as si
import SignalIntegrity.App as siapp

def main():
    """
    Extract Utility:,
    Extracts s-parameters from a project file.  It allows the s-parameters of any file device to be replaced in the project.
    Ports are placed where specified and all unused ports in the project are terminated with 50 ohm resistors.

    Command line format:
    -project [project file name]
    for example: -project test.si
    this is the project file to use.

    -replace [device name] [s-parameter file]
    for example: -replace D2 sparameterfile.s4p
    this replaces the s-parameters in a device in the project
    Notes:
    . this is optional.
    . the number of device ports must match the number of ports in the s-parameter file.
    . the device in the project file must be a file device, meaning a device specified by an s-parameter file.
    . the path must be specified relative to the location of the project file.

    -frequency [end frequency]
    for example: -frequency 40e9
    this specifies the end frequency for the s-parameters that get generated.
    Notes:
    . if this is not specified, the end frequency in the project file is used.

    -numpoints [num points]
    for example: -numpoints 2000
    this specifies the number of points for the s-parameters that get generated.
    Notes:
    . if this is not specified, the number of frequency points in the project file is used.

    -ports [device,port,device,port,device,port....]
    for example: -ports D1 1 D1 2 D3 2 D3 4
    these are the device/port connections for the system ports in the output that gets generated, in system port order.
    In other words, in the example, system port 1 is D1 1, system port 2 is D1 2, etc.

    -output [output file name]
    for example: -output test
    this is the output file.
    Notes:
    . if no extension is supplied, it will be .sXp where X is the number of ports in the solution.
    . if an extension is supplied, it must match the number of ports in the solution.
    . s-parameters will be in the reference impedance specified.

    -Z0 [Z0]
    for example: -Z0 42.5
    this is the reference impedance.
    Notes:
    . all terminations of unused ports will be in this reference impedance specified.
    . output s-parameters will be converted to this reference impedance.
    """
    args=sys.argv
    if len(args)<=1:
        print(main.__doc__)
        return
    """
    read the command line keeping the list of tokens following one of the recognized tokens in
    the list below.
    """
    tokens=['-project','-replace','-frequency','-numpoints','-ports','-output','-Z0']
    intokens=False
    tokenlist=[]
    for arg in args[1:]:
        if arg in tokens:
            if intokens:
                tokenlist.append(thistokenlist)
            thistokenlist=[arg]
            intokens=True
        else:
            if intokens:
                thistokenlist.append(arg)
    if intokens:
        tokenlist.append(thistokenlist)

    """
    each list of tokens begins with one of the recognized tokens.  Assign the values to a dictionary
    of arguments.
    """
    argsdict={'project':None,'endfrequency':None,'numpoints':None,'ports':None,'output':None,'replace':[],'Z0':50.0}

    for arglist in tokenlist:
        arg=arglist[0]
        if arg=='-project':
            if len(arglist)==2:
                argsdict['project']=arglist[1]
        elif arg=='-frequency':
            if len(arglist)==2:
                argsdict['endfrequency']=float(arglist[1])
        elif arg=='-numpoints':
            if len(arglist)==2:
                argsdict['numpoints']=int(arglist[1])
        elif arg=='-ports':
            if len(arglist)>1:
                if (len(arglist)-1)//2*2!=len(arglist):
                    argsdict['ports']=[(arglist[i],int(arglist[i+1])) for i in range(1,len(arglist),2)]
        elif arg=='-output':
            if len(arglist)==2:
                argsdict['output']=arglist[1]
        elif arg=='-Z0':
            if len(arglist)==2:
                argsdict['Z0']=float(arglist[1])
        elif arg=='-replace':
            if len(arglist)>2:
                argsdict['replace'].append(arglist[1:])
    """
    open the specified project file.  If the user did not specify the end frequency and number of
    points on the command line, then get these from the project file.  Replace all device s-parameters
    with those specified in the -replace options specified on the command line.
    """
    siproj=siapp.SignalIntegrityAppHeadless()
    siproj.OpenProjectFile(argsdict['project'])
    if argsdict['endfrequency']==None:
        argsdict['endfrequency']=siapp.Project['CalculationProperties.EndFrequency']
    if argsdict['numpoints']==None:
        argsdict['numpoints']=siapp.Project['CalculationProperties.FrequencyPoints']
    for devicereplace in argsdict['replace']:
        devices=siproj.Drawing.schematic.deviceList
        for device in devices:
            if device['ref']['Value']==devicereplace[0]:
                device['file']['Value']=devicereplace[1]
        #siproj.Device(devicereplace[0])['file']['Value']=devicereplace[1]

    """
    get the netlist from the project.  For speed, remove all of the device file names in netlistext, so that
    when the netlist is parsed, it does not needlessly read the s-parameters (at this step, the goal is only
    to determine which device ports are not connected.
    """
    netlist=siproj.NetListText()
    netlistext=[line if line.split()[0]!='device' else ' '.join(line.split()[:3]) for line in netlist]
    f=si.fd.EvenlySpacedFrequencyList(argsdict['endfrequency'],argsdict['numpoints'])
    sdp=si.p.SystemDescriptionParser(f).AddLines(netlistext)
    sd=sdp.SystemDescription()

    unconnectedlist=[]
    for d in range(len(sd)):
        dev=sd[d]
        for p in range(len(dev)):
            port=dev[p]
            if not port.IsConnected():
                unconnectedlist.append((dev.Name,p+1))
    """
    now having the list of unconnected device ports, build the ports netlist line from those specified
    on the command line, removing these device,port combinations from the list of unconnected device
    ports.
    """
    portnetlistline='port'
    for p in range(len(argsdict['ports'])):
        (device,port)=argsdict['ports'][p]
        unconnectedlist.remove((device,port))
        portnetlistline+=' '+str(p+1)+' '+device+' '+str(port)
    """
    Finally, for each unconnected device port, add a resistor to the netlist and connect it to each
    remaining unconnected device port.
    """
    for r in range(len(unconnectedlist)):
        (device,port)=unconnectedlist[r]
        # use a $ on the resistor devices to avoid clash with other schematic elements.
        netlist.append('device R$'+str(r+1)+' 1 r '+str(argsdict['Z0']))
        netlist.append('connect '+device+' '+str(port)+' R$'+str(r+1)+' 1')

    netlist.append(portnetlistline)
    """
    Use this netlist to generate the s-parameters of the system
    """
    sdp=si.p.SystemSParametersNumericParser(f).AddLines(netlist)
    sp=sdp.SParameters()
    # although the s-parameters are in Z0=50, the format string will cause the reference impedance
    # to be changed when the s-parameters are written.
    sp.WriteToFile(argsdict['output'],'# MHz S MA R '+str(argsdict['Z0']))

if __name__ == '__main__':
    main()
