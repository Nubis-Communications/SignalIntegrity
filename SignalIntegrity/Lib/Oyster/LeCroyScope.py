"""
LeCroyScope.py
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
from SignalIntegrity.Lib.Exception import SignalIntegrityException
from SignalIntegrity.Lib.TimeDomain.Waveform.Waveform import Waveform
from SignalIntegrity.Lib.TimeDomain.Waveform.TimeDescriptor import TimeDescriptor

class SignalIntegrityExceptionScope(SignalIntegrityException):
    def __init__(self,message=''):
        SignalIntegrityException.__init__(self,'Scope',message)


class LeCroyScope():
    isConnected=False
    serialNumber=None
    instrument=None
    platform=None
    instanceCount=0
    def __init__(self,serialNumber,rootPath=None):
        LeCroyScope.instanceCount=LeCroyScope.instanceCount+1
        if rootPath is None:
            self.m_rootPath=''
        else:
            self.m_rootPath=rootPath
        if LeCroyScope.isConnected:
            if LeCroyScope.serialNumber == serialNumber:
                return
            else:
                del LeCroyScope.instrument
                LeCroyScope.isConnected=False
                LeCroyScope.serialNumber=None
                LeCroyScope.instrument=None
        if serialNumber==None:
            serialNumber='None'
        import platform
        LeCroyScope.platform=platform.system()
        if LeCroyScope.platform == 'Linux':
            import usbtmc
            devs=usbtmc.usbtmc.list_devices()
            for dev in devs:
                try:
                    if dev.serial_number == serialNumber:
                        LeCroyScope.instrument=usbtmc.Instrument(dev)
                        LeCroyScope.instrument.write('CHDR OFF')
                        print LeCroyScope.instrument.ask('*IDN?')
                        #LeCroyScope.instrument.write('*RST')
                        LeCroyScope.instrument.timeout=250000
                        LeCroyScope.isConnected = True
                        LeCroyScope.serialNumber = serialNumber
                        return
                except:
                    pass
        else:
            import visa
            #pyvisa.resources.messagebased.MessageBasedResource
            rm=visa.ResourceManager()
            resourceList=rm.list_resources()
            for resource in resourceList:
                tokenList=resource.split('::')
                if serialNumber in tokenList:
                    LeCroyScope.instrument=rm.open_resource(resource)
                    LeCroyScope.instrument.chunk_size=1024*1024
                    LeCroyScope.instrument.timeout=250000
                    LeCroyScope.instrument.write('CHDR OFF')
                    print LeCroyScope.instrument.query('*IDN?')
                    #LeCroyScope.instrument.write('*RST')
                    LeCroyScope.isConnected = True
                    LeCroyScope.serialNumber = serialNumber
                    return
        if not LeCroyScope.isConnected:
            raise SignalIntegrityExceptionScope('cannot connect to: '+serialNumber)
    def SetPath(self,path):
        self.m_rootPath=path
        return self
    def GetPath(self):
        return self.m_rootPath
    def Indent(self,path):
        self.m_rootPath='.'.join(self.m_rootPath.split('.')+path.split('.'))
    def Outdent(self):
        pathList=self.m_rootPath.split('.')
        if len(pathList)>0:
            self.m_rootPath='.'.join([pathList[i]
                for i in range(len(pathList)-1)])
    def _FormGetPropertyString(self,path):
        return "VBS? 'return="+'.'.join(self.m_rootPath.split('.')+\
            path.split('.'))+"'"
    def _FormGetPropertyStringNoError(self,path):
        return "VBS? 'n=\"\":on error resume next:n="+'.'.join(self.m_rootPath.split('.')+\
            path.split('.'))+":return=n'"
    def _FormWriteString(self,path,string):
        fullPath='.'.join(self.m_rootPath.split('.')+path.split('.'))
        if fullPath[0]=='.':
            fullPath=fullPath[1:]
        if not string is None:
            if string != 'True' and string != 'False':
                string ="\""+string+"\""
        if string is None:
            return "VBS '"+fullPath+"'"
        else:
            return "VBS '"+fullPath+" = "+string+"'"
    def GetPropertyString(self,path):
        stringToWrite=self._FormGetPropertyString(path)
        self.instrument.write(stringToWrite)
        replyString = self.instrument.read()
        return replyString
    def GetPropertyStringPanelRemote(self,path):
        stringToWrite="VBS? 'return="+'.'.join(self.m_rootPath.split('.')+\
            path.split('.'))+".GetAdaptedValueStringAutomation'"
        self.m_scope.WriteString(stringToWrite,True)
        replyString = self.m_scope.ReadString(8000)
        return replyString
    def GetPropertyHex(self,path):
        replyString=self.GetPropertyString(path)
        return int(replyString[replyString.find('&h')+2:],16)
    def GetPropertyInt(self,path):
        return int(self.GetPropertyString(path))
    def GetPropertyStringNoError(self,path):
        stringToWrite=self._FormGetPropertyStringNoError(path)
        self.m_scope.WriteString(stringToWrite,True)
        replyString = self.m_scope.ReadString(8000)
        return replyString
    def GetPropertyIntNoError(self,path):
        stringReturned=self.GetPropertyStringNoError(path)
        if stringReturned=='':
            return 0
        else:
            return int(stringReturned)
    def SetPropertyString(self,path,string):
        return self.WriteString(string,path)
    def SetPropertyHex(self,path,value):
        return self.WriteString('&h'+hex(value).replace('0x','').strip('L'),path)
    def SetPropertyInt(self,path,value):
        return self.WriteString(str(value),path)
    def WriteString(self,string,path=None):
        if path==None:
            return self.instrument.write(string)
        else:
            stringToWrite=self._FormWriteString(path,string)
            return self.instrument.write(stringToWrite)
    def Command(self,string):
        return self.instrument.write(string)
    def Query(self,string,encoding=None):
        if LeCroyScope.platform == 'Linux':
            if encoding is None:
                return self.instrument.ask(string)
            else:
                return self.instrument.ask(string,encoding=encoding)
        else:
            if encoding is None:
                return self.instrument.query(string)
            else:
                self.instrument.write(string)
                return self.instrument.read(string,encoding=encoding)
    def __del__(self):
        LeCroyScope.instanceCount=LeCroyScope.instanceCount-1
        if LeCroyScope.instanceCount == 0:
            LeCroyScope.isConnected=False
            LeCroyScope.serialNumber=None
            LeCroyScope.instrument=None
            LeCroyScope.platform=None
    def ReadWaveform(self,channelStr):
        self.WriteString('COMM_FORMAT OFF, WORD, BIN')
        wfstr=self.Query(channelStr+':waveform? dat1',encoding='latin-1')
        ho=float(str(self.Query(channelStr+':INSP? HORIZ_OFFSET').split(':')[-1]).strip(' "\n'))
        Ts=float(str(self.Query(channelStr+':INSP? HORIZ_INTERVAL').split(':')[-1]).strip(' "\n'))
        Fs=1/Ts
        m=float(str(self.Query(channelStr+':INSP? VERTICAL_GAIN').split(':')[-1]).strip(' "\n'))
        b=float(str(self.Query(channelStr+':INSP? VERTICAL_OFFSET').split(':')[-1]).strip(' "\n'))
        value=[((((ord(wfstr[i+16])+256*ord(wfstr[i+1+16]))-32768)%65536)-32768)*m-b for i in range(0,(len(wfstr)-16)/2*2,2)]
        numPts=len(value)
        import SignalIntegrity.Lib as si
        timeDescriptor = si.td.wf.TimeDescriptor(ho,numPts,Fs)
        #timeDescriptor.Print()
        wf = si.td.wf.Waveform(timeDescriptor,value)
        #wf.adaptionStrategy='Linear'
        return wf
    def ReadWaveformAlternate(self,channelString):
        wf = self.Query(channelString+':inspect? "simple"')
        #m=float(self.Query(channelString+':inspect? VERTICAL_GAIN').split()[-2])
        #b=float(self.Query(channelString+':inspect? VERTICAL_OFFSET').split()[-2])
        wfn=[float(e) for e in str(wf).translate(None,'"\r\n').split()]
        ho=float(self.Query(channelString+':inspect? HORIZ_OFFSET').split()[-2])
        Fs=1./float(self.Query(channelString+':inspect? HORIZ_INTERVAL').split()[-2])
        K=len(wfn)
        return Waveform(TimeDescriptor(ho,K,Fs),wfn)

def main():
    ls=LeCroyScope('10.30.5.12')
    wf=ls.ReadWaveform('F1')
    wf.WriteToFile('CISTest.txt')
    clkwf=ls.ReadWaveform('C1')
    clkwf.WriteToFile('CISTestClk.txt')
    thwf=ls.ReadWaveform('C3')
    thwf.WriteToFile('CISTestTh.txt')
    import matplotlib.pyplot as plt
    plt.clf()
    plt.xlabel('time (us)')
    plt.ylabel('amplitude')
    plt.plot(wf.Times('us'),wf.Values(),label='data')
    plt.legend(loc='upper right')
    plt.show()
    print 'done'
    pass

    
if __name__ == '__main__':
    main()