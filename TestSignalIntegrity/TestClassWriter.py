import unittest

from TestHelpers import *

class TestWriteClass(unittest.TestCase,RoutineWriterTesterHelper):
    def testWriteFrequencyResponse_ImpulseResponse(self):
        fileName="../SignalIntegrity/FrequencyDomain/FrequencyResponse.py"
        className='FrequencyResponse'
        defName=['ImpulseResponse']
        self.WriteClassCode(fileName,className,defName)
    def testWriteFrequencyResponse_Resample(self):
        fileName="../SignalIntegrity/FrequencyDomain/FrequencyResponse.py"
        className='FrequencyResponse'
        defName=['Resample']
        self.WriteClassCode(fileName,className,defName)
    def testWriteFrequencyResponse_ResampleCZT(self):
        fileName="../SignalIntegrity/FrequencyDomain/FrequencyResponse.py"
        className='FrequencyResponse'
        defName=['ResampleCZT']
        self.WriteClassCode(fileName,className,defName)
    def testWriteFrequencyResponse_Pad(self):
        fileName="../SignalIntegrity/FrequencyDomain/FrequencyResponse.py"
        className='FrequencyResponse'
        defName=['_Pad']
        self.WriteClassCode(fileName,className,defName)
    def testWriteFrequencyResponse_DelayBy(self):
        fileName="../SignalIntegrity/FrequencyDomain/FrequencyResponse.py"
        className='FrequencyResponse'
        defName=['_DelayBy','_FractionalDelayTime']
        self.WriteClassCode(fileName,className,defName)
    def testWriteFrequencyResponse_Rat(self):
        fileName="../SignalIntegrity/FrequencyDomain/FrequencyResponse.py"
        className=''
        defName=['Rat']
        self.WriteClassCode(fileName,className,defName)
    def testWriteFrequencyResponse_Basic(self):
        fileName="../SignalIntegrity/FrequencyDomain/FrequencyResponse.py"
        className='FrequencyResponse'
        defName=['__init__','__getitem__','__len__','FrequencyList',
        'Frequencies','Response','ReadFromFile','WriteToFile']
        self.WriteClassCode(fileName,className,defName)
    def testWriteImpulseResponse_FrequencyResponse(self):
        fileName="../SignalIntegrity/TimeDomain/Waveform/ImpulseResponse.py"
        className='ImpulseResponse'
        defName=['FrequencyResponse','_AdjustLength']
        self.WriteClassCode(fileName,className,defName)
    def testWriteImpulseResponse_DelayBy(self):
        fileName="../SignalIntegrity/TimeDomain/Waveform/ImpulseResponse.py"
        className='ImpulseResponse'
        defName=['DelayBy','_FractionalDelayTime']
        self.WriteClassCode(fileName,className,defName)
    def testWriteImpulseResponse_TrimToThreshold(self):
        fileName="../SignalIntegrity/TimeDomain/Waveform/ImpulseResponse.py"
        className='ImpulseResponse'
        defName=['TrimToThreshold']
        self.WriteClassCode(fileName,className,defName)
    def testWriteImpulseResponse_FirFilter(self):
        fileName="../SignalIntegrity/TimeDomain/Waveform/ImpulseResponse.py"
        className='ImpulseResponse'
        defName=['FirFilter']
        self.WriteClassCode(fileName,className,defName)
    def testWriteImpulseResponse_Pad(self):
        fileName="../SignalIntegrity/TimeDomain/Waveform/ImpulseResponse.py"
        className='ImpulseResponse'
        defName=['_Pad']
        self.WriteClassCode(fileName,className,defName)
    def testWriteImpulseResponse_Resample(self):
        fileName="../SignalIntegrity/TimeDomain/Waveform/ImpulseResponse.py"
        className='ImpulseResponse'
        defName=['Resample']
        self.WriteClassCode(fileName,className,defName)
    def testWriteTimeDescriptor_ApplyFilter(self):
        fileName="../SignalIntegrity/TimeDomain/Waveform/TimeDescriptor.py"
        className='TimeDescriptor'
        defName=['ApplyFilter','__init__','__len__','__getitem__','Times','__mul__','__div__',
                 'DelayBy','FrequencyList','TimeOfPoint']
        self.WriteClassCode(fileName,className,defName)
    def testWriteFilterDescriptor_mul(self):
        fileName="../SignalIntegrity/TimeDomain/Filters/FilterDescriptor.py"
        className='FilterDescriptor'
        defName=['__mul__','__init__']
        self.WriteClassCode(fileName,className,defName)
    def testWriteFilterDescriptor_Trimmer(self):
        fileName="../SignalIntegrity/TimeDomain/Filters/FilterDescriptor.py"
        className='FilterDescriptor'
        defName=['TrimLeft','TrimRight','TrimTotal']
        self.WriteClassCode(fileName,className,defName)
    def testWriteFilterDescriptor_Order(self):
        fileName="../SignalIntegrity/TimeDomain/Filters/FilterDescriptor.py"
        className='FilterDescriptor'
        defName=['Before','After']
        self.WriteClassCode(fileName,className,defName)
    def testWriteWaveform_Values(self):
        fileName="../SignalIntegrity/TimeDomain/Waveform/Waveform.py"
        className='Waveform'
        defName=['Values','__init__','__len__','__getitem__','Times','TimeDescriptor',]
        self.WriteClassCode(fileName,className,defName)
    def testWriteFrequencyList_Frequencies(self):
        fileName="../SignalIntegrity/FrequencyDomain/FrequencyList.py"
        className='FrequencyList'
        defName=['Frequencies','__init__','__len__','__getitem__','SetEvenlySpaced','SetList',
        'EvenlySpaced','CheckEvenlySpaced','__div__','TimeDescriptor']
        self.WriteClassCode(fileName,className,defName)
    def testWriteEvenlySpacedFrequencyList_Init(self):
        fileName="../SignalIntegrity/FrequencyDomain/FrequencyList.py"
        className='EvenlySpacedFrequencyList'
        defName=['__init__']
        self.WriteClassCode(fileName,className,defName)
    def testGenericFrequencyList_Init(self):
        fileName="../SignalIntegrity/FrequencyDomain/FrequencyList.py"
        className='GenericFrequencyList'
        defName=['__init__']
        self.WriteClassCode(fileName,className,defName)
    def testSystemSParametersSymbolic_LaTeXSolution(self):
        fileName="../SignalIntegrity/SystemDescriptions/SystemSParametersSymbolic.py"
        className='SystemSParametersSymbolic'
        defName=['LaTeXSolution','__init__','_LaTeXSi']
        self.WriteClassCode(fileName,className,defName)
    def testSystemSParametersNumeric_SParameters(self):
        fileName="../SignalIntegrity/SystemDescriptions/SystemSParametersNumeric.py"
        className='SystemSParametersNumeric'
        defName=['SParameters','__init__']
        self.WriteClassCode(fileName,className,defName)
    def testWriteVirtualProbe(self):
        fileName="../SignalIntegrity/SystemDescriptions/VirtualProbe.py"
        className='VirtualProbe'
        defName=['__init__','pMeasurementList','pStimDef']
        self.WriteClassCode(fileName,className,defName)
    def testWriteVirtualProbeNumeric(self):
        fileName="../SignalIntegrity/SystemDescriptions/VirtualProbeNumeric.py"
        className='VirtualProbeNumeric'
        defName=['__init__','TransferMatrix']
        self.WriteClassCode(fileName,className,defName)
    def testWriteVirtualProbeSymbolic(self):
        fileName="../SignalIntegrity/SystemDescriptions/VirtualProbeSymbolic.py"
        className='VirtualProbeSymbolic'
        defName=['__init__','LaTeXTransferMatrix','LaTeXEquations']
        self.WriteClassCode(fileName,className,defName)
    def testWriteVirtualProbeParser(self):
        fileName="../SignalIntegrity/Parsers/VirtualProbeParser.py"
        className='VirtualProbeParser'
        defName=['__init__','_ProcessVirtualProbeLine','_ProcessLines']
        self.WriteClassCode(fileName,className,defName)
    def testWriteVirtualProbeNumericParserc(self):
        fileName="../SignalIntegrity/Parsers/VirtualProbeNumericParser.py"
        className='VirtualProbeNumericParser'
        defName=['__init__','TransferMatrices']
        self.WriteClassCode(fileName,className,defName)
    def testWritePort(self):
        fileName='../SignalIntegrity/SystemDescriptions/Port.py'
        className='Port'
        defName=['__init__','IsConnected','Print']
        self.WriteClassCode(fileName,className,defName)
    def testWriteDevice(self):
        fileName='../SignalIntegrity/SystemDescriptions/Device.py'
        className='Device'
        defName=['__init__','get_S','set_S','del_S','__getitem__','__len__',
                'SymbolicMatrix','Print']
        self.WriteClassCode(fileName,className,defName)
    def testWriteSystemDescription(self):
        fileName='../SignalIntegrity/SystemDescriptions/SystemDescription.py'
        className='SystemDescription'
        defName=['__init__','__getitem__','__len__','AddDevice','AssignM','DeviceNames',
            'IndexOfDevice','_InsertNodeName','ConnectDevicePort',
            'AddPort','AssignSParameters','Print']
        self.WriteClassCode(fileName,className,defName)
    def testWriteSystemSParameters(self):
        fileName='../SignalIntegrity/SystemDescriptions/SystemSParameters.py'
        className='SystemSParameters'
        defName=['__init__','PortANames','PortBNames','OtherNames','NodeVector',
        'StimulusVector','WeightsMatrix']
        self.WriteClassCode(fileName,className,defName)
    def testWriteSymbolic(self):
        fileName='../SignalIntegrity/SystemDescriptions/Symbolic.py'
        className='Symbolic'
        defName=['__init__','Clear','Emit','DocStart','DocEnd','_BeginEq',
        '_EndEq','_AddLine','_AddLines','WriteToFile','_SmallMatrix',
        '_Identity','Get','_AddEq','_LaTeXMatrix']
        self.WriteClassCode(fileName,className,defName)
if __name__ == '__main__':
    unittest.main()