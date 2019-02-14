"""
TestClassWriter.py
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
import unittest
import SignalIntegrity.Lib as si
import os

class TestWriteClass(unittest.TestCase,si.test.RoutineWriterTesterHelper):
    def __init__(self, methodName='runTest'):
        si.test.RoutineWriterTesterHelper.__init__(self)
        unittest.TestCase.__init__(self,methodName)
    def setUp(self):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
    def tearDown(self):
        pass
    def testWriteFrequencyResponse_ImpulseResponse(self):
        fileName="../../SignalIntegrity/Lib/FrequencyDomain/FrequencyResponse.py"
        className='FrequencyResponse'
        defName=['ImpulseResponse']
        self.WriteClassCode(fileName,className,defName)
    def testWriteFrequencyResponse_Resample(self):
        fileName="../../SignalIntegrity/Lib/FrequencyDomain/FrequencyResponse.py"
        className='FrequencyResponse'
        defName=['Resample']
        self.WriteClassCode(fileName,className,defName)
    def testWriteFrequencyResponse_ResampleCZT(self):
        fileName="../../SignalIntegrity/Lib/FrequencyDomain/FrequencyResponse.py"
        className='FrequencyResponse'
        defName=['ResampleCZT']
        self.WriteClassCode(fileName,className,defName)
    def testWriteFrequencyResponse_Pad(self):
        fileName="../../SignalIntegrity/Lib/FrequencyDomain/FrequencyResponse.py"
        className='FrequencyResponse'
        defName=['_Pad']
        self.WriteClassCode(fileName,className,defName)
    def testWriteFrequencyResponse_DelayBy(self):
        fileName="../../SignalIntegrity/Lib/FrequencyDomain/FrequencyResponse.py"
        className='FrequencyResponse'
        defName=['_DelayBy','_FractionalDelayTime']
        self.WriteClassCode(fileName,className,defName)
    def testWriteFrequencyResponse_Rat(self):
        fileName="../../SignalIntegrity/Lib/Rat/Rat.py"
        className=''
        defName=['Rat']
        self.WriteClassCode(fileName,className,defName)
    def testWriteFrequencyDomain(self):
        fileName="../../SignalIntegrity/Lib/FrequencyDomain/FrequencyDomain.py"
        className='FrequencyDomain'
        defName=['__init__','FrequencyList',
        'Frequencies','Values','ReadFromFile','WriteToFile']
        self.WriteClassCode(fileName,className,defName)
    def testWriteFrequencyResponse_Basic(self):
        fileName="../../SignalIntegrity/Lib/FrequencyDomain/FrequencyResponse.py"
        className='FrequencyResponse'
        defName=['__init__','Response']
        self.WriteClassCode(fileName,className,defName)
    def testWriteImpulseResponse_FrequencyResponse(self):
        fileName="../../SignalIntegrity/Lib/TimeDomain/Waveform/ImpulseResponse.py"
        className='ImpulseResponse'
        defName=['FrequencyResponse','_AdjustLength']
        self.WriteClassCode(fileName,className,defName)
    def testWriteImpulseResponse_DelayBy(self):
        fileName="../../SignalIntegrity/Lib/TimeDomain/Waveform/ImpulseResponse.py"
        className='ImpulseResponse'
        defName=['DelayBy','_FractionalDelayTime']
        self.WriteClassCode(fileName,className,defName)
    def testWriteImpulseResponse_TrimToThreshold(self):
        fileName="../../SignalIntegrity/Lib/TimeDomain/Waveform/ImpulseResponse.py"
        className='ImpulseResponse'
        defName=['TrimToThreshold']
        self.WriteClassCode(fileName,className,defName)
    def testWriteImpulseResponse_FirFilter(self):
        fileName="../../SignalIntegrity/Lib/TimeDomain/Waveform/ImpulseResponse.py"
        className='ImpulseResponse'
        defName=['FirFilter']
        self.WriteClassCode(fileName,className,defName)
    def testWriteImpulseResponse_Pad(self):
        fileName="../../SignalIntegrity/Lib/TimeDomain/Waveform/ImpulseResponse.py"
        className='ImpulseResponse'
        defName=['_Pad']
        self.WriteClassCode(fileName,className,defName)
    def testWriteImpulseResponse_Resample(self):
        fileName="../../SignalIntegrity/Lib/TimeDomain/Waveform/ImpulseResponse.py"
        className='ImpulseResponse'
        defName=['Resample']
        self.WriteClassCode(fileName,className,defName)
    def testWriteTimeDescriptor_ApplyFilter(self):
        fileName="../../SignalIntegrity/Lib/TimeDomain/Waveform/TimeDescriptor.py"
        className='TimeDescriptor'
        defName=['ApplyFilter','__init__','__len__','__getitem__','Times','__mul__','__truediv__',
                 '__div__','DelayBy','FrequencyList','TimeOfPoint']
        self.WriteClassCode(fileName,className,defName)
    def testWriteFilterDescriptor_mul(self):
        fileName="../../SignalIntegrity/Lib/TimeDomain/Filters/FilterDescriptor.py"
        className='FilterDescriptor'
        defName=['__mul__','__init__','__eq__']
        self.WriteClassCode(fileName,className,defName)
    def testWriteFilterDescriptor_Trimmer(self):
        fileName="../../SignalIntegrity/Lib/TimeDomain/Filters/FilterDescriptor.py"
        className='FilterDescriptor'
        defName=['TrimLeft','TrimRight','TrimTotal']
        self.WriteClassCode(fileName,className,defName,lineDefs=True)
    def testWriteFilterDescriptor_Order(self):
        fileName="../../SignalIntegrity/Lib/TimeDomain/Filters/FilterDescriptor.py"
        className='FilterDescriptor'
        defName=['Before','After']
        self.WriteClassCode(fileName,className,defName,lineDefs=True)
    def testWriteWaveform_Values(self):
        fileName="../../SignalIntegrity/Lib/TimeDomain/Waveform/Waveform.py"
        className='Waveform'
        defName=['Values','__init__','Times','TimeDescriptor',]
        self.WriteClassCode(fileName,className,defName)
    def testWriteWaveform_File(self):
        fileName="../../SignalIntegrity/Lib/TimeDomain/Waveform/Waveform.py"
        className='Waveform'
        defName=['ReadFromFile','WriteToFile']
        self.WriteClassCode(fileName,className,defName)
    def testWriteWaveform_Multiply(self):
        fileName="../../SignalIntegrity/Lib/TimeDomain/Waveform/Waveform.py"
        className='Waveform'
        defName=['__mul__']
        self.WriteClassCode(fileName,className,defName)
    def testWriteWaveform_Adapt(self):
        fileName="../../SignalIntegrity/Lib/TimeDomain/Waveform/Waveform.py"
        className='Waveform'
        defName=['Adapt']
        self.WriteClassCode(fileName,className,defName)
    def testWriteStepWaveform(self):
        fileName="../../SignalIntegrity/Lib/TimeDomain/Waveform/StepWaveform.py"
        className='StepWaveform'
        firstDef='__init__'
        allfuncs=self.EntireListOfClassFunctions(fileName,className)
        allfuncs.remove(firstDef)
        defName=[firstDef]+allfuncs
        self.WriteClassCode(fileName,className,defName)
    def testWritePulseWaveform(self):
        fileName="../../SignalIntegrity/Lib/TimeDomain/Waveform/PulseWaveform.py"
        className='PulseWaveform'
        firstDef='__init__'
        allfuncs=self.EntireListOfClassFunctions(fileName,className)
        allfuncs.remove(firstDef)
        defName=[firstDef]+allfuncs
        self.WriteClassCode(fileName,className,defName)
    def testWriteSineWaveform(self):
        fileName="../../SignalIntegrity/Lib/TimeDomain/Waveform/SineWaveform.py"
        className='SineWaveform'
        firstDef='__init__'
        allfuncs=self.EntireListOfClassFunctions(fileName,className)
        allfuncs.remove(firstDef)
        defName=[firstDef]+allfuncs
        self.WriteClassCode(fileName,className,defName)
    def testWriteFrequencyList_Frequencies(self):
        fileName="../../SignalIntegrity/Lib/FrequencyDomain/FrequencyList.py"
        className='FrequencyList'
        defName=['Frequencies','SetEvenlySpaced','SetList',
        'EvenlySpaced','CheckEvenlySpaced','__truediv__','__div__','__mul__','TimeDescriptor']
        self.WriteClassCode(fileName,className,defName)
    def testWriteEvenlySpacedFrequencyList_Init(self):
        fileName="../../SignalIntegrity/Lib/FrequencyDomain/FrequencyList.py"
        className='EvenlySpacedFrequencyList'
        defName=['__init__']
        self.WriteClassCode(fileName,className,defName)
    def testGenericFrequencyList_Init(self):
        fileName="../../SignalIntegrity/Lib/FrequencyDomain/FrequencyList.py"
        className='GenericFrequencyList'
        defName=['__init__']
        self.WriteClassCode(fileName,className,defName)
    def testSystemSParametersSymbolic_LaTeXSolution(self):
        fileName="../../SignalIntegrity/Lib/SystemDescriptions/SystemSParametersSymbolic.py"
        className='SystemSParametersSymbolic'
        defName=['LaTeXSolution','__init__','_LaTeXSi']
        self.WriteClassCode(fileName,className,defName,lineDefs=True)
    def testWriteVirtualProbe(self):
        fileName="../../SignalIntegrity/Lib/SystemDescriptions/VirtualProbe.py"
        className='VirtualProbe'
        defName=['__init__','pMeasurementList','pStimDef']
        self.WriteClassCode(fileName,className,defName,lineDefs=True)
    def testWriteVirtualProbeNumeric(self):
        fileName="../../SignalIntegrity/Lib/SystemDescriptions/VirtualProbeNumeric.py"
        className='VirtualProbeNumeric'
        defName=['__init__','TransferMatrix']
        self.WriteClassCode(fileName,className,defName,lineDefs=True)
    def testWriteVirtualProbeSymbolic(self):
        fileName="../../SignalIntegrity/Lib/SystemDescriptions/VirtualProbeSymbolic.py"
        className='VirtualProbeSymbolic'
        defName=['__init__','LaTeXTransferMatrix','LaTeXEquations']
        self.WriteClassCode(fileName,className,defName,lineDefs=True)
    def testWriteVirtualProbeParser(self):
        fileName="../../SignalIntegrity/Lib/Parsers/VirtualProbeParser.py"
        className='VirtualProbeParser'
        defName=['__init__','_ProcessVirtualProbeLine','_ProcessLines']
        self.WriteClassCode(fileName,className,defName,lineDefs=True)
    def testWriteVirtualProbeNumericParserc(self):
        fileName="../../SignalIntegrity/Lib/Parsers/VirtualProbeNumericParser.py"
        className='VirtualProbeNumericParser'
        defName=['__init__','TransferMatrices']
        self.WriteClassCode(fileName,className,defName,lineDefs=True)
    def testWritePort(self):
        fileName='../../SignalIntegrity/Lib/SystemDescriptions/Port.py'
        className='Port'
        defName=['__init__','IsConnected','Print']
        self.WriteClassCode(fileName,className,defName,lineDefs=True)
    def testWriteDevice(self):
        fileName='../../SignalIntegrity/Lib/SystemDescriptions/Device.py'
        className='Device'
        defName=self.EntireListOfClassFunctions(fileName,className)
        self.WriteClassCode(fileName,className,defName,lineDefs=True)
    def testWriteSystemDescriptionBasic(self):
        fileName='../../SignalIntegrity/Lib/SystemDescriptions/SystemDescription.py'
        className='SystemDescription'
        firstDef='__init__'
        allfuncs=self.EntireListOfClassFunctions(fileName,className)
        for subroutine in [firstDef,'AddDevice','AddPort','ConnectDevicePort']:
            allfuncs.remove(subroutine)
        defName=[firstDef]+allfuncs
        self.WriteClassCode(fileName,className,defName,lineDefs=True)
    def testWriteSystemDescriptionImportant(self):
        fileName='../../SignalIntegrity/Lib/SystemDescriptions/SystemDescription.py'
        className='SystemDescription'
        defName=['AddDevice','AddPort','ConnectDevicePort']
        self.WriteClassCode(fileName,className,defName,lineDefs=True)
    def testWriteSystemDescriptionSymbolic(self):
        fileName='../../SignalIntegrity/Lib/SystemDescriptions/SystemDescriptionSymbolic.py'
        className='SystemDescriptionSymbolic'
        firstDef='LaTeXSystemEquation'
        allfuncs=self.EntireListOfClassFunctions(fileName,className)
        allfuncs.remove(firstDef)
        defName=[firstDef]+allfuncs
        self.WriteClassCode(fileName,className,defName,lineDefs=True)
    def testWriteSystemSParameters(self):
        fileName='../../SignalIntegrity/Lib/SystemDescriptions/SystemSParameters.py'
        className='SystemSParameters'
        defName=['__init__','PortANames','PortBNames','OtherNames','NodeVector',
        'StimulusVector','WeightsMatrix']
        self.WriteClassCode(fileName,className,defName,lineDefs=True)
    def testWriteSymbolic(self):
        fileName='../../SignalIntegrity/Lib/SystemDescriptions/Symbolic.py'
        className='Symbolic'
        defName=['__init__','Clear','Emit','DocStart','DocEnd','_BeginEq',
        '_EndEq','_AddLine','_AddLines','WriteToFile','_SmallMatrix',
        '_Identity','Get','_AddEq','_LaTeXMatrix']
        self.WriteClassCode(fileName,className,defName)
    def testWriteSystemDescriptionParser(self):
        fileName='../../SignalIntegrity/Lib/Parsers/SystemDescriptionParser.py'
        className='SystemDescriptionParser'
        firstDef='__init__'
        allfuncs=self.EntireListOfClassFunctions(fileName,className)
        allfuncs.remove(firstDef)
        defName=[firstDef]+allfuncs
        self.WriteClassCode(fileName,className,defName)
    def testWriteSystemSParametersNumeric(self):
        fileName="../../SignalIntegrity/Lib/SystemDescriptions/SystemSParametersNumeric.py"
        className='SystemSParametersNumeric'
        firstDef='SParameters'
        allfuncs=self.EntireListOfClassFunctions(fileName,className)
        allfuncs.remove(firstDef)
        defName=[firstDef]+allfuncs
        self.WriteClassCode(fileName,className,defName)
    def testWriteSystemSParametersNumericParser(self):
        fileName="../../SignalIntegrity/Lib/Parsers/SystemSParametersParser.py"
        className='SystemSParametersNumericParser'
        firstDef='SParameters'
        allfuncs=self.EntireListOfClassFunctions(fileName,className)
        allfuncs.remove(firstDef)
        defName=[firstDef]+allfuncs
        self.WriteClassCode(fileName,className,defName)
    def testWriteSubCircuit(self):
        fileName="../../SignalIntegrity/Lib/SubCircuits/SubCircuit.py"
        className='SubCircuit'
        firstDef='__init__'
        allfuncs=self.EntireListOfClassFunctions(fileName,className)
        allfuncs.remove(firstDef)
        defName=[firstDef]+allfuncs
        self.WriteClassCode(fileName,className,defName)
    def testWriteParserArgs(self):
        fileName="../../SignalIntegrity/Lib/Parsers/ParserArgs.py"
        className='ParserArgs'
        firstDef='ProcessVariables'
        allfuncs=self.EntireListOfClassFunctions(fileName,className)
        allfuncs.remove(firstDef)
        defName=[firstDef]+allfuncs
        self.WriteClassCode(fileName,className,defName)
    def testWriteDeembedder(self):
        fileName="../../SignalIntegrity/Lib/SystemDescriptions/Deembedder.py"
        className='Deembedder'
        firstDef='__init__'
        allfuncs=self.EntireListOfClassFunctions(fileName,className)
        allfuncs.remove(firstDef)
        defName=[firstDef]+allfuncs
        self.WriteClassCode(fileName,className,defName)
    def testWriteDeembedderNumeric(self):
        fileName="../../SignalIntegrity/Lib/SystemDescriptions/DeembedderNumeric.py"
        className='DeembedderNumeric'
        firstDef='__init__'
        allfuncs=self.EntireListOfClassFunctions(fileName,className)
        allfuncs.remove(firstDef)
        defName=[firstDef]+allfuncs
        self.WriteClassCode(fileName,className,defName,lineDefs=True)
    def testWriteDeembedderSymbolic(self):
        fileName="../../SignalIntegrity/Lib/SystemDescriptions/DeembedderSymbolic.py"
        className='DeembedderSymbolic'
        firstDef='__init__'
        allfuncs=self.EntireListOfClassFunctions(fileName,className)
        allfuncs.remove(firstDef)
        defName=[firstDef]+allfuncs
        self.WriteClassCode(fileName,className,defName)
    def testWriteDeembedderParser(self):
        fileName="../../SignalIntegrity/Lib/Parsers/DeembedderParser.py"
        className='DeembedderParser'
        firstDef='__init__'
        allfuncs=self.EntireListOfClassFunctions(fileName,className)
        allfuncs.remove(firstDef)
        defName=[firstDef]+allfuncs
        self.WriteClassCode(fileName,className,defName,lineDefs=True)
    def testWriteDeembedderNumericParser(self):
        fileName="../../SignalIntegrity/Lib/Parsers/DeembedderNumericParser.py"
        className='DeembedderNumericParser'
        firstDef='__init__'
        allfuncs=self.EntireListOfClassFunctions(fileName,className)
        allfuncs.remove(firstDef)
        defName=[firstDef]+allfuncs
        self.WriteClassCode(fileName,className,defName,lineDefs=True)
    def testWriteReferenceImpedance(self):
        fileName="../../SignalIntegrity/Lib/Conversions/ReferenceImpedance.py"
        className=''
        defName=['ReferenceImpedance']
        self.WriteClassCode(fileName,className,defName)
    def testWriteReferenceImpedanceTransformer(self):
        fileName="../../SignalIntegrity/Lib/Devices/ReferenceImpedanceTransformer.py"
        className=''
        defName=['ReferenceImpedanceTransformer']
        self.WriteClassCode(fileName,className,defName)
    def testWriteSeriesZ(self):
        fileName="../../SignalIntegrity/Lib/Devices/SeriesZ.py"
        className=''
        defName=['SeriesZ']
        self.WriteClassCode(fileName,className,defName)
    def testWriteShuntZ(self):
        fileName="../../SignalIntegrity/Lib/Devices/ShuntZ.py"
        className=''
        defName=['ShuntZTwoPort']
        self.WriteClassCode(fileName,className,defName)
    def testWriteTee(self):
        fileName="../../SignalIntegrity/Lib/Devices/Tee.py"
        className=''
        defName=['Tee']
        self.WriteClassCode(fileName,className,defName)
    def testWriteZ2S(self):
        fileName="../../SignalIntegrity/Lib/Conversions/Z2S.py"
        className=''
        defName=['Z2S']
        self.WriteClassCode(fileName,className,defName)
    def testWriteS2Z(self):
        fileName="../../SignalIntegrity/Lib/Conversions/S2Z.py"
        className=''
        defName=['S2Z']
        self.WriteClassCode(fileName,className,defName)
    def testWriteY2S(self):
        fileName="../../SignalIntegrity/Lib/Conversions/Y2S.py"
        className=''
        defName=['Y2S']
        self.WriteClassCode(fileName,className,defName)
    def testWriteS2Y(self):
        fileName="../../SignalIntegrity/Lib/Conversions/S2Y.py"
        className=''
        defName=['S2Y']
        self.WriteClassCode(fileName,className,defName)
    def testWriteABCD2S(self):
        fileName="../../SignalIntegrity/Lib/Conversions/ABCD2S.py"
        className=''
        defName=['ABCD2S']
        self.WriteClassCode(fileName,className,defName)
    def testWriteS2ABCD(self):
        fileName="../../SignalIntegrity/Lib/Conversions/S2ABCD.py"
        className=''
        defName=['S2ABCD']
        self.WriteClassCode(fileName,className,defName)
    def testWriteSp2Sw(self):
        fileName="../../SignalIntegrity/Lib/Conversions/Sp2Sw.py"
        className=''
        defName=['Sp2Sw']
        self.WriteClassCode(fileName,className,defName)
    def testWriteSw2Sp(self):
        fileName="../../SignalIntegrity/Lib/Conversions/Sw2Sp.py"
        className=''
        defName=['Sw2Sp']
        self.WriteClassCode(fileName,className,defName)
    def testWriteT2S(self):
        fileName="../../SignalIntegrity/Lib/Conversions/T2S.py"
        className=''
        defName=['T2S']
        self.WriteClassCode(fileName,className,defName)
    def testWriteS2T(self):
        fileName="../../SignalIntegrity/Lib/Conversions/S2T.py"
        className=''
        defName=['S2T']
        self.WriteClassCode(fileName,className,defName)
    def testWriteSParameterFile(self):
        fileName="../../SignalIntegrity/Lib/SParameters/SParameterFile.py"
        className='SParameterFile'
        firstDef='__init__'
        allfuncs=self.EntireListOfClassFunctions(fileName,className)
        allfuncs.remove(firstDef)
        defName=[firstDef]+allfuncs
        self.WriteClassCode(fileName,className,defName)
    def testWriteSParameters(self):
        fileName="../../SignalIntegrity/Lib/SParameters/SParameters.py"
        className='SParameters'
        firstDef='__init__'
        allfuncs=self.EntireListOfClassFunctions(fileName,className)
        allfuncs.remove(firstDef)
        allfuncs.remove('Resample')
        allfuncs.remove('SetReferenceImpedance')
        defName=[firstDef]+allfuncs
        self.WriteClassCode(fileName,className,defName)
    def testWriteSParametersResample(self):
        fileName="../../SignalIntegrity/Lib/SParameters/SParameters.py"
        className='SParameters'
        defName=['Resample']
        self.WriteClassCode(fileName,className,defName)
    def testWriteOpen(self):
        fileName="../../SignalIntegrity/Lib/Devices/Open.py"
        className=''
        defName=['Open']
        self.WriteClassCode(fileName,className,defName)
    def testWriteGround(self):
        fileName="../../SignalIntegrity/Lib/Devices/Ground.py"
        className=''
        defName=['Ground']
        self.WriteClassCode(fileName,className,defName)
    def testWriteTerminationZ(self):
        fileName="../../SignalIntegrity/Lib/Devices/TerminationZ.py"
        className=''
        defName=['TerminationZ']
        self.WriteClassCode(fileName,className,defName)
    def testWriteSimulatorSymbolic(self):
        fileName="../../SignalIntegrity/Lib/SystemDescriptions/SimulatorSymbolic.py"
        className='SimulatorSymbolic'
        firstDef='__init__'
        allfuncs=self.EntireListOfClassFunctions(fileName,className)
        allfuncs.remove(firstDef)
        defName=[firstDef]+allfuncs
        self.WriteClassCode(fileName,className,defName)
    def testWriteSimulatorParser(self):
        fileName="../../SignalIntegrity/Lib/Parsers/SimulatorParser.py"
        className='SimulatorParser'
        firstDef='__init__'
        allfuncs=self.EntireListOfClassFunctions(fileName,className)
        allfuncs.remove(firstDef)
        defName=[firstDef]+allfuncs
        self.WriteClassCode(fileName,className,defName)
    def testWriteSimulatorNumeric(self):
        fileName="../../SignalIntegrity/Lib/SystemDescriptions/SimulatorNumeric.py"
        className='SimulatorNumeric'
        firstDef='__init__'
        allfuncs=self.EntireListOfClassFunctions(fileName,className)
        allfuncs.remove(firstDef)
        defName=[firstDef]+allfuncs
        self.WriteClassCode(fileName,className,defName)
    def testWriteSimulatorNumericParser(self):
        fileName="../../SignalIntegrity/Lib/Parsers/SimulatorNumericParser.py"
        className='SimulatorNumericParser'
        firstDef='__init__'
        allfuncs=self.EntireListOfClassFunctions(fileName,className)
        allfuncs.remove(firstDef)
        defName=[firstDef]+allfuncs
        self.WriteClassCode(fileName,className,defName)
    def testWriteFirFilter(self):
        fileName="../../SignalIntegrity/Lib/TimeDomain/Filters/FirFilter.py"
        className='FirFilter'
        firstDef='__init__'
        allfuncs=self.EntireListOfClassFunctions(fileName,className)
        allfuncs.remove(firstDef)
        defName=[firstDef]+allfuncs
        self.WriteClassCode(fileName,className,defName,lineDefs=True)
    def testWriteSinXFunc(self):
        fileName="../../SignalIntegrity/Lib/TimeDomain/Filters/InterpolatorSinX.py"
        className=''
        defName=['SinX']
        self.WriteClassCode(fileName,className,defName)
    def testWriteFractionalDelayFilterSinX(self):
        fileName="../../SignalIntegrity/Lib/TimeDomain/Filters/InterpolatorSinX.py"
        className='FractionalDelayFilterSinX'
        firstDef='__init__'
        allfuncs=self.EntireListOfClassFunctions(fileName,className)
        allfuncs.remove(firstDef)
        defName=[firstDef]+allfuncs
        self.WriteClassCode(fileName,className,defName)
    def testWriteInterpolatorSinX(self):
        fileName="../../SignalIntegrity/Lib/TimeDomain/Filters/InterpolatorSinX.py"
        className='InterpolatorSinX'
        firstDef='__init__'
        allfuncs=self.EntireListOfClassFunctions(fileName,className)
        allfuncs.remove(firstDef)
        defName=[firstDef]+allfuncs
        self.WriteClassCode(fileName,className,defName)
    def testWriteInterpolatorFractionalDelayFilterSinX(self):
        fileName="../../SignalIntegrity/Lib/TimeDomain/Filters/InterpolatorSinX.py"
        className='InterpolatorFractionalDelayFilterSinX'
        firstDef='__init__'
        allfuncs=self.EntireListOfClassFunctions(fileName,className)
        allfuncs.remove(firstDef)
        defName=[firstDef]+allfuncs
        self.WriteClassCode(fileName,className,defName)
    def testWriteFractionalDelayFilterLinear(self):
        fileName="../../SignalIntegrity/Lib/TimeDomain/Filters/InterpolatorLinear.py"
        className='FractionalDelayFilterLinear'
        firstDef='__init__'
        allfuncs=self.EntireListOfClassFunctions(fileName,className)
        allfuncs.remove(firstDef)
        defName=[firstDef]+allfuncs
        self.WriteClassCode(fileName,className,defName)
    def testWriteInterpolatorLinear(self):
        fileName="../../SignalIntegrity/Lib/TimeDomain/Filters/InterpolatorLinear.py"
        className='InterpolatorLinear'
        firstDef='__init__'
        allfuncs=self.EntireListOfClassFunctions(fileName,className)
        allfuncs.remove(firstDef)
        defName=[firstDef]+allfuncs
        self.WriteClassCode(fileName,className,defName)
    def testWriteInterpolatorFractionalDelayFilterLinear(self):
        fileName="../../SignalIntegrity/Lib/TimeDomain/Filters/InterpolatorLinear.py"
        className='InterpolatorFractionalDelayFilterLinear'
        firstDef='__init__'
        allfuncs=self.EntireListOfClassFunctions(fileName,className)
        allfuncs.remove(firstDef)
        defName=[firstDef]+allfuncs
        self.WriteClassCode(fileName,className,defName)
    def testWriteWaveformTrimmer(self):
        fileName="../../SignalIntegrity/Lib/TimeDomain/Filters/WaveformTrimmer.py"
        className='WaveformTrimmer'
        firstDef='__init__'
        allfuncs=self.EntireListOfClassFunctions(fileName,className)
        allfuncs.remove(firstDef)
        defName=[firstDef]+allfuncs
        self.WriteClassCode(fileName,className,defName,lineDefs=True)
    def testWriteWaveformDecimator(self):
        fileName="../../SignalIntegrity/Lib/TimeDomain/Filters/WaveformDecimator.py"
        className='WaveformDecimator'
        firstDef='__init__'
        allfuncs=self.EntireListOfClassFunctions(fileName,className)
        allfuncs.remove(firstDef)
        defName=[firstDef]+allfuncs
        self.WriteClassCode(fileName,className,defName,lineDefs=True)
    def testWriteMutual(self):
        fileName="../../SignalIntegrity/Lib/Devices/Mutual.py"
        className=''
        defName=['Mutual']
        self.WriteClassCode(fileName,className,defName)
    def testWriteCZT(self):
        fileName="../../SignalIntegrity/Lib/ChirpZTransform/ChirpZTransform.py"
        className=''
        defName=['CZT']
        self.WriteClassCode(fileName,className,defName)
    def testWriteParserDevice(self):
        fileName="../../SignalIntegrity/Lib/Parsers/Devices/DeviceParser.py"
        className='ParserDevice'
        firstDef='__init__'
        allfuncs=self.EntireListOfClassFunctions(fileName,className)
        allfuncs.remove(firstDef)
        defName=[firstDef]+allfuncs
        self.WriteClassCode(fileName,className,defName)
    def testWriteDeviceFactoryInit(self):
        fileName="../../SignalIntegrity/Lib/Parsers/Devices/DeviceParser.py"
        className='DeviceFactory'
        defName=['__init__']
        self.WriteClassCode(fileName,className,defName)
    def testWriteDeviceFactoryInitContd(self):
        fileName="../../SignalIntegrity/Lib/Parsers/Devices/DeviceParser.py"
        className='DeviceFactory'
        defName=['__init__Contd']
        self.WriteClassCode(fileName,className,defName)
    def testWriteDeviceFactoryMakeDevice(self):
        fileName="../../SignalIntegrity/Lib/Parsers/Devices/DeviceParser.py"
        className='DeviceFactory'
        defName=['MakeDevice']
        self.WriteClassCode(fileName,className,defName)
    def testWriteDeviceParser(self):
        fileName="../../SignalIntegrity/Lib/Parsers/Devices/DeviceParser.py"
        className='DeviceParser'
        firstDef='__init__'
        allfuncs=self.EntireListOfClassFunctions(fileName,className)
        allfuncs.remove(firstDef)
        defName=[firstDef]+allfuncs
        self.WriteClassCode(fileName,className,defName)
    def testWriteTransferMatricesProcessing(self):
        fileName="../../SignalIntegrity/Lib/FrequencyDomain/TransferMatrices.py"
        className='TransferMatrices'
        firstDef='__init__'
        allfuncs=self.EntireListOfClassFunctions(fileName,className)
        allfuncs.remove(firstDef)
        allfuncs.remove('SParameters')
        defName=[firstDef]+allfuncs
        self.WriteClassCode(fileName,className,defName,lineDefs=True)
    def testWriteTransferMatricesProcessor(self):
        fileName="../../SignalIntegrity/Lib/TimeDomain/Filters/TransferMatricesProcessor.py"
        className='TransferMatricesProcessor'
        firstDef='__init__'
        allfuncs=self.EntireListOfClassFunctions(fileName,className)
        allfuncs.remove(firstDef)
        defName=[firstDef]+allfuncs
        self.WriteClassCode(fileName,className,defName,lineDefs=True)
    def testWriteMixedModeConverter(self):
        fileName="../../SignalIntegrity/Lib/Devices/MixedModeConverter.py"
        className=''
        defName=['MixedModeConverter']
        self.WriteClassCode(fileName,className,defName)
    def testWriteMixedModeConverterVoltage(self):
        fileName="../../SignalIntegrity/Lib/Devices/MixedModeConverter.py"
        className=''
        defName=['MixedModeConverterVoltage']
        self.WriteClassCode(fileName,className,defName)
    def testWriteFrequencyContent(self):
        fileName="../../SignalIntegrity/Lib/FrequencyDomain/FrequencyContent.py"
        className='FrequencyContent'
        firstDef='__init__'
        allfuncs=self.EntireListOfClassFunctions(fileName,className)
        allfuncs.remove(firstDef)
        defName=[firstDef]+allfuncs
        self.WriteClassCode(fileName,className,defName,lineDefs=True)
    def testWriteErrorTermsCodeCalibration(self):
        fileName="../../SignalIntegrity/Lib/Measurement/Calibration/ErrorTerms.py"
        className='ErrorTerms'
        defName=['ReflectCalibration','ThruCalibration','ExCalibration','TransferThruCalibration']
        self.WriteClassCode(fileName,className,defName,lineDefs=True)
    def testWriteErrorTermsCodeDut(self):
        fileName="../../SignalIntegrity/Lib/Measurement/Calibration/ErrorTerms.py"
        className='ErrorTerms'
        defName=['DutCalculation','DutCalculationAlternate','Fixture']
        self.WriteClassCode(fileName,className,defName,lineDefs=True)
    def testWriteCalibrationKitCode(self):
        fileName="../../SignalIntegrity/Lib/Measurement/CalKit/CalibrationKit.py"
        className='CalibrationKit'
        firstDef='__init__'
        allfuncs=self.EntireListOfClassFunctions(fileName,className)
        allfuncs.remove(firstDef)
        defName=[firstDef]+allfuncs
        self.WriteClassCode(fileName,className,defName,lineDefs=True)
    def testWriteCalibrationConstantsCode(self):
        fileName="../../SignalIntegrity/Lib/Measurement/CalKit/CalibrationKit.py"
        className='CalibrationConstants'
        defName=['__init__']
        self.WriteClassCode(fileName,className,defName)
        defName=['ReadFromFile']
        self.WriteClassCode(fileName,className,defName)
    def testWriteOffsetCode(self):
        fileName="../../SignalIntegrity/Lib/Measurement/CalKit/Standards/Offset.py"
        className='Offset'
        defName=['__init__']
        self.WriteClassCode(fileName,className,defName)
    def testWriteThruStandardCode(self):
        fileName="../../SignalIntegrity/Lib/Measurement/CalKit/Standards/ThruStandard.py"
        className='ThruStandard'
        defName=['__init__']
        self.WriteClassCode(fileName,className,defName)
    def testWriteShortStandardCode(self):
        fileName="../../SignalIntegrity/Lib/Measurement/CalKit/Standards/ShortStandard.py"
        className='ShortStandard'
        defName=['__init__']
        self.WriteClassCode(fileName,className,defName)
    def testWriteOpenStandardCode(self):
        fileName="../../SignalIntegrity/Lib/Measurement/CalKit/Standards/OpenStandard.py"
        className='OpenStandard'
        defName=['__init__']
        self.WriteClassCode(fileName,className,defName)
    def testWriteLoadStandardCode(self):
        fileName="../../SignalIntegrity/Lib/Measurement/CalKit/Standards/LoadStandard.py"
        className='LoadStandard'
        defName=['__init__']
        self.WriteClassCode(fileName,className,defName)
    def testWriteCalibrationCode(self):
        fileName="../../SignalIntegrity/Lib/Measurement/Calibration/Calibration.py"
        className='Calibration'
        firstDef='__init__'
        allfuncs=self.EntireListOfClassFunctions(fileName,className)
        allfuncs.remove(firstDef)
        allfuncs.remove('__getitem__')
        allfuncs.remove('__len__')
        allfuncs.remove('WriteToFile')
        allfuncs.remove('Fixtures')
        allfuncs.remove('InitializeFromFixtures')
        defName=[firstDef]+allfuncs
        self.WriteClassCode(fileName,className,defName,lineDefs=True)
    def testWriteTDRWaveformToSParameterConverterClassCodeExceptConvert(self):
        fileName='../../SignalIntegrity/Lib/Measurement/TDR/TDRWaveformToSParameterConverter.py'
        className='TDRWaveformToSParameterConverter'
        firstDef='__init__'
        allfuncs=self.EntireListOfClassFunctions(fileName,className)
        allfuncs.remove(firstDef)
        allfuncs.remove('Convert')
        allfuncs.remove('_ExtractionWindows')
        defName=[firstDef]+allfuncs
        self.WriteClassCode(fileName,className,defName)
    def testWriteTDRWaveformToSParameterConverterClassCodeConvert(self):
        fileName='../../SignalIntegrity/Lib/Measurement/TDR/TDRWaveformToSParameterConverter.py'
        className='TDRWaveformToSParameterConverter'
        defName=['Convert']
        self.WriteClassCode(fileName,className,defName)

if __name__ == '__main__':
    unittest.main()