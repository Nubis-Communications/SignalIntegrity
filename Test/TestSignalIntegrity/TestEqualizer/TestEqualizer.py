"""
TestEqualizer.py
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

import os
import unittest

import SignalIntegrity.Lib as si


class TestBlindEqualizerScript(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import xml.etree.ElementTree as ET
        from SignalIntegrity.App.WaveformProcessorScript import ParseWaveformProcessorInterface

        cls.projectDirectory=os.path.dirname(os.path.abspath(__file__))
        root=ET.parse(os.path.join(cls.projectDirectory,'TestEqualizer.si'))
        device=next(device for device in root.findall('.//Device')
                    if any(prop.findtext('Keyword') == 'ref' and prop.findtext('Value') == 'WFP1'
                           for prop in device.findall('./PartProperties/PartProperty')))
        cls.script=next(prop.findtext('Value') for prop in device.findall('./PartProperties/PartProperty')
                        if prop.findtext('Keyword') == 'script')
        _,_,variables=ParseWaveformProcessorInterface(cls.script)
        cls.defaults={variable['Name']:int(variable['Value']) if variable['Type'] == 'int'
                      else float(variable['Value']) if variable['Type'] == 'float'
                      else variable['Value'] for variable in variables}
        dfeDevice=next(device for device in root.findall('.//Device')
                       if any(prop.findtext('Keyword') == 'ref' and prop.findtext('Value') == 'WFP2'
                              for prop in device.findall('./PartProperties/PartProperty')))
        cls.dfeScript=next(prop.findtext('Value') for prop in dfeDevice.findall('./PartProperties/PartProperty')
                          if prop.findtext('Keyword') == 'script')
        _,_,variables=ParseWaveformProcessorInterface(cls.dfeScript)
        cls.dfeDefaults={variable['Name']:int(variable['Value']) if variable['Type'] == 'int'
                         else float(variable['Value']) if variable['Type'] == 'float'
                         else variable['Value'] for variable in variables}

    def applyDfe(self,waveform,**parameters):
        from SignalIntegrity.Lib.TimeDomain.Waveform.DependentWaveform import DependentWaveform

        namespace=dict(self.dfeDefaults,input_waveform_1=waveform)
        namespace.update(parameters)
        return DependentWaveform.EvaluateTransformFunctionSafely(
            self.dfeScript,namespace,{'output_waveform_1':None})['output_waveform_1']

    def assertAlignedDescriptor(self,output,inputDescriptor,delay):
        self.assertEqual(len(output),inputDescriptor.K)
        self.assertEqual(output.td.Fs,inputDescriptor.Fs)
        self.assertAlmostEqual(output.td.H*output.td.Fs,
                               round(output.td.H*output.td.Fs),places=7)
        self.assertLessEqual(abs((output.td.H-inputDescriptor.H-delay)*inputDescriptor.Fs),
                             .5+1.e-7)

    def disableSchematicTraining(self,schematic):
        for device in schematic.deviceList:
            for variable in device.variablesList:
                if variable['Name'] == 'train_equalizer':
                    variable['Value']='False'

    def testStandaloneDfeCorrectsKnownIsiWithSamplingDelay(self):
        import numpy as np

        rng=np.random.default_rng(42)
        symbols=rng.choice([-1.,1.],400)
        baud=25.e9
        origin=-2.e-9
        for sps,phase,start in [(4.,0.,.25),(4.3,.375,.25),
                                (4.3,.375,52.5),(4.,.75,89.125)]:
            with self.subTest(sps=sps,phase=phase,start=start):
                start=round((start+((-phase)%1))*sps)/sps-((-phase)%1)
                td=si.td.wf.TimeDescriptor(origin+start/baud,1000,baud*sps)
                symbolIndex=np.floor(start+np.arange(td.K)/sps-phase+.5).astype(int)
                desired=symbols[5+symbolIndex]
                normalized=desired+.25*symbols[4+symbolIndex]
                raw=(normalized-.12)*.2+.05*1.2
                waveform=si.td.wf.Waveform(td,raw.tolist())
                output=self.applyDfe(
                    waveform,baud_rate=baud,levels=2,amplitude=2.,
                    dfe_taps_input='.25',ffe_taps_input='[.3, 1, -.1]',
                    num_precursor_taps=1,normalization_offset_input=.05,
                    normalization_scale_input=.2,bias_input=.12,
                    sample_time_input=((-phase)%1)/baud)
                interior=(symbolIndex>=symbolIndex[0]+5)&(symbolIndex<symbolIndex[-1]-4)
                np.testing.assert_allclose(np.asarray(output)[interior],desired[interior],atol=2.e-14)
                self.assertAlignedDescriptor(output,td,((-phase)%1)/baud)
                repeated=self.applyDfe(
                    waveform,baud_rate=baud,levels=2,amplitude=2.,
                    dfe_taps_input='.25',ffe_taps_input='[.3, 1, -.1]',
                    num_precursor_taps=1,normalization_offset_input=.05,
                    normalization_scale_input=.2,bias_input=.12,
                    sample_time_input=(((-phase)%1)+1000)/baud)
                np.testing.assert_allclose(output,repeated,rtol=0.,atol=2.e-14)
                self.assertAlmostEqual((repeated.td.H-output.td.H)*baud,0.,places=10)

    def testStandaloneDfeMatchesCombinedEqualizer(self):
        import numpy as np

        rng=np.random.default_rng(17)
        waveform=si.td.wf.Waveform(
            si.td.wf.TimeDescriptor(-1.e-9,4096,100.e9),
            np.repeat(rng.choice([-.5,.5],1024),4).tolist())
        settings=dict(train_equalizer='False',baud_rate=25.e9,levels=2,amplitude=.4,
                      GDC_input=-3.,GDC2_input=-1.,ffe_taps_input='[.2, 1, -.1]',
                      num_precursor_taps=1,normalization_offset_input=.03,
                      normalization_scale_input=.7,bias_input=.05,
                      sample_time_input=.625/25.e9)
        for trim in [0,209]:
            with self.subTest(trim=trim):
                td=si.td.wf.TimeDescriptor(waveform.td.H+trim/waveform.td.Fs,
                                           len(waveform)-trim,waveform.td.Fs)
                trimmed=si.td.wf.Waveform(td,list(waveform)[trim:])
                preDfe=self.equalize(trimmed,dfe_taps_input='[]',**settings)['output_waveform_1']
                result=self.equalize(trimmed,dfe_taps_input='[.2]',**settings)
                self.assertEqual(result['sample_time_output'],settings['sample_time_input'])
                ffeVoltage=(np.asarray(preDfe)/.2-.05)*.7+.03*1.1
                actual=self.applyDfe(
                    si.td.wf.Waveform(preDfe.td.DelayBy(-settings['sample_time_input']),
                                      ffeVoltage.tolist()),
                    baud_rate=25.e9,levels=2,amplitude=.4,ffe_taps_input='[.2, 1, -.1]',
                    num_precursor_taps=1,dfe_taps_input='[.2]',normalization_offset_input=.03,
                    normalization_scale_input=.7,bias_input=.05,
                    sample_time_input=result['sample_time_output'])
                np.testing.assert_allclose(actual,result['output_waveform_1'],rtol=0.,atol=2.e-15)
                self.assertEqual(actual.td,result['output_waveform_1'].td)

    def testDfeDelayCentersEyeWithoutAutoAlignment(self):
        import numpy as np
        from SignalIntegrity.Lib.Eye.EyeDiagramBitmap import EyeDiagramBitmap

        baud=25.e9
        delay=.31/baud
        rng=np.random.default_rng(42)
        symbols=rng.choice([-1.,1.],700)
        for start in [-37.137,52.3]:
            for feedback in [0.,.25]:
                with self.subTest(start=start,feedback=feedback):
                    td=si.td.wf.TimeDescriptor(start/baud,8192,16*baud)
                    clock=start+np.arange(td.K)/16+delay*baud
                    index=np.floor(clock+.5).astype(int)
                    pulse=symbols[100+index]*np.cos(np.pi*(clock-index))
                    raw=pulse+feedback*symbols[99+index]
                    output=self.applyDfe(
                        si.td.wf.Waveform(td,raw.tolist()),baud_rate=baud,levels=2,
                        amplitude=2.,dfe_taps_input=str([feedback]),sample_time_input=delay)
                    self.assertAlignedDescriptor(output,td,delay)
                    interior=si.td.wf.Waveform(
                        si.td.wf.TimeDescriptor(output.td.H+512/output.td.Fs,
                                               len(output)-1024,output.td.Fs),
                        list(output)[512:-512])
                    eye=EyeDiagramBitmap(
                        YAxisMode='Fixed',YMin=-1.2,YMax=1.2,Rows=128,Cols=128,
                        BaudRate=baud,prbswf=interior,EnhancementMode='Fixed',
                        EnhancementSteps=2,Levels=2)
                    volts=eye.minV+np.arange(128)*(eye.maxV-eye.minV)/128
                    opening=np.abs(volts)@eye.Bitmap()
                    self.assertGreater(opening[64],.95)
                    self.assertLess(opening[0],.08+abs(feedback))
                    self.assertLessEqual(abs(int(np.argmax(opening))-64),3)

    def testStandaloneDfeRejectsInvalidSettingsAndHandlesDisabledFeedback(self):
        import numpy as np
        from SignalIntegrity.Lib.Exception import SignalIntegrityExceptionDependentWaveform

        waveform=si.td.wf.Waveform(si.td.wf.TimeDescriptor(0.,8,100.e9),.3)
        for taps in ['[]','[0]',0.]:
            with self.subTest(taps=taps):
                output=self.applyDfe(waveform,baud_rate=25.e9,levels=2,amplitude=2.,
                                     dfe_taps_input=taps,normalization_offset_input=.1,
                                     normalization_scale_input=.2,bias_input=.05)
                np.testing.assert_allclose(output,[1.05]*8,rtol=0.,atol=3.e-16)
        for parameters in [{'baud_rate':0.},{'levels':1},{'amplitude':0.},
                           {'dfe_taps_input':'[True]'},{'dfe_taps_input':'invalid'},
                           {'dfe_taps_input':[np.inf]},{'ffe_taps_input':'[]'},
                           {'normalization_scale_input':0.},{'bias_input':np.nan},
                           {'sample_time_input':np.inf},
                           {'dfe_taps_input':'[.2]'}]:
            with self.subTest(parameters=parameters):
                settings=dict(baud_rate=25.e9)
                settings.update(parameters)
                with self.assertRaises(SignalIntegrityExceptionDependentWaveform):
                    self.applyDfe(waveform,**settings)

    def testStandaloneDfeSchematicWiringAndNormalizedOutput(self):
        import sys
        import numpy as np
        import SignalIntegrity.App as siapp
        from unittest.mock import patch
        from SignalIntegrity.App.SignalIntegrityAppHeadless import SignalIntegrityAppHeadless
        from SignalIntegrity.Lib.TimeDomain.Waveform.DependentWaveform import DependentWaveform

        cwd=os.getcwd()
        searchPath=sys.path[:]
        self.addCleanup(os.chdir,cwd)
        self.addCleanup(setattr,sys,'path',searchPath)
        records=[]
        origins=[]
        clocks=[]
        evaluate=DependentWaveform.EvaluateTransformFunctionSafely

        def capture(script,args,outputs):
            result=evaluate(script,args,outputs)
            if script == self.script and 'WFP1_in1' in args:
                origins.append(args['input_waveform_1'].td.H)
                clocks.append(result['sample_time_output'])
                self.assertEqual(result['sample_time_output'],args['sample_time_input'])
            if script == self.dfeScript:
                self.assertEqual(args['sample_time_input'],clocks[-1])
                records.append((si.td.wf.Waveform(args['input_waveform_1']),
                                si.td.wf.Waveform(result['output_waveform_1'])))
            return result

        with patch.object(siapp,'Project',getattr(siapp,'Project',None),create=True), \
             patch.object(siapp,'Preferences',getattr(siapp,'Preferences',None),create=True):
            app=SignalIntegrityAppHeadless()
            siapp.Preferences['Cache.CacheResults']=False
            siapp.Preferences['Calculation.Processing.StopOnConvergence']=False
            self.assertTrue(app.OpenProjectFile(
                os.path.join(self.projectDirectory,'TestEqualizer.si')))
            byRef={device['ref'].GetValue():device for device in app.Drawing.schematic.deviceList
                   if device['ref'] is not None}
            for ref in ('Vo2','Vo3'):
                self.assertFalse(byRef[ref].configuration['Alignment.AutoAlign'])
            siapp.Project['CalculationProperties.FrequencyPoints']=212
            self.disableSchematicTraining(app.Drawing.schematic)
            text=app.Drawing.schematic.NetList().Text()
            connections=[set(zip(line.split()[1::2],line.split()[2::2]))
                         for line in text if line.startswith('connect ')]
            self.assertIn({('WFP2','1'),('F2','2')},connections)
            self.assertIn({('O2','1'),('WFP2','2')},connections)
            self.assertIn({('F2','1'),('F1','2')},connections)
            with patch.object(DependentWaveform,'EvaluateTransformFunctionSafely',side_effect=capture):
                result=app.Simulate()
            self.assertIn('output waveforms',result)
            self.assertEqual(len(records),app.Drawing.schematic.DependentSourceCount()+1)
            self.assertEqual(len(origins),len(records))
            original=si.td.wf.Waveform().ReadFromFile('Vo.txt')
            self.assertNotAlmostEqual((origins[-1]-original.td.H)*self.defaults['baud_rate'],0.)
            self.assertEqual(float(siapp.Project['Variables'].VariableByName('sample_time').Value()),
                             clocks[-1])
            settings={variable['Name']:variable.Value() for variable in byRef['WFP2'].variablesList}
            for raw,processed in records:
                expected=self.applyDfe(
                    raw,**{name:int(value) if name in ('levels','num_precursor_taps') else
                           value if name in ('dfe_taps_input','ffe_taps_input') else float(value)
                           for name,value in settings.items()})
                np.testing.assert_array_equal(processed,expected)
            vo2=result['output waveforms'][result['output waveform labels'].index('Vo2')]
            expected=records[-2][1].Adapt(vo2.td)
            np.testing.assert_allclose(vo2,expected,rtol=1.e-11,atol=1.e-12)
            vo3=result['output waveforms'][result['output waveform labels'].index('Vo3')]
            baud=self.defaults['baud_rate']
            start=max(vo2.td.H,vo3.td.H)+128/baud
            end=min(vo2.td.H+(len(vo2)-1)/vo2.td.Fs,
                    vo3.td.H+(len(vo3)-1)/vo3.td.Fs)-128/baud
            rate=min(vo2.td.Fs,vo3.td.Fs)
            td=si.td.wf.TimeDescriptor(start,int((end-start)*rate),rate)
            difference=np.asarray(vo2.Adapt(td))-np.asarray(vo3.Adapt(td))
            amplitude=float(next(variable for variable in byRef['WFP1'].variablesList
                                 if variable['Name'] == 'amplitude').Value())
            self.assertLess(np.sqrt(np.mean(difference**2)),amplitude*2.5e-4)
            self.assertLess(np.max(np.abs(difference)),amplitude*2.5e-3)

    def equalize(self,waveform,**parameters):
        from SignalIntegrity.Lib.TimeDomain.Waveform.DependentWaveform import DependentWaveform

        namespace=dict(self.defaults,input_waveform_1=waveform,train_equalizer='True')
        namespace.update(parameters)
        return DependentWaveform.EvaluateTransformFunctionSafely(
            self.script,namespace,{'output_waveform_1':None,'equalizer_result':None,
                                   'GDC_output':None,'GDC2_output':None,
                                   'ffe_taps_output':None,'dfe_taps_output':None,
                                   'normalization_offset_output':None,
                                   'normalization_scale_output':None,
                                   'bias_output':None,'sample_time_output':None,
                                   'ffe_taps_input':None,'dfe_taps_input':None})

    def testFixedSettingsBypassTrainingAndNormalizeTapLists(self):
        import ast
        import numpy as np
        from unittest.mock import patch
        from SignalIntegrity.Lib.SParameters.Devices.EqualizerCTLE import CTLE

        waveform=si.td.wf.Waveform(si.td.wf.TimeDescriptor(0.,32,100.e9),
                                 np.linspace(-1.,1.,32).tolist())
        with patch('scipy.optimize.minimize',side_effect=AssertionError('training called')), \
             patch('scipy.optimize.lsq_linear',side_effect=AssertionError('training called')):
            for ffe,dfe,delay in [('2','0',.25),(2.,0.,-.75),
                                  ([2.],[0.],3.25),('[2.]','[0.]',.25)]:
                with self.subTest(ffe=ffe,dfe=dfe,delay=delay):
                    result=self.equalize(
                        waveform,train_equalizer='False',baud_rate=25.e9,levels=2,
                        amplitude=2.,ffe_taps_input=ffe,dfe_taps_input=dfe,
                        GDC_input=-7.,GDC2_input=-2.,
                        GDC_choices='unused',GDC2_choices='unused',
                        normalization_offset_input=.1,normalization_scale_input=2.,
                        bias_input=.2,sample_time_input=delay/25.e9)
                    size=1 << (len(waveform)+1024-1).bit_length()
                    frequencies=np.fft.rfftfreq(size,1/waveform.td.Fs)
                    ctle=CTLE([0.],-7.,-2.,10.e9,25.e9/80,10.e9,25.e9)
                    response=ctle._Evaluate(frequencies)
                    response[-1]=response[-1].real
                    filtered=np.fft.irfft(np.fft.rfft(waveform,size)*response,size)[:len(waveform)]
                    np.testing.assert_array_equal(result['output_waveform_1'],
                                                  (filtered-.1)/2.*2.+.2)
                    self.assertAlignedDescriptor(result['output_waveform_1'],waveform.td,.25/25.e9)
                    self.assertEqual(result['GDC_output'],-7.)
                    self.assertEqual(result['GDC2_output'],-2.)
                    self.assertEqual(ast.literal_eval(result['ffe_taps_input']),[2.])
                    self.assertEqual(ast.literal_eval(result['dfe_taps_input']),[0.])
                    self.assertEqual(result['ffe_taps_output'],result['ffe_taps_input'])
                    self.assertEqual(result['dfe_taps_output'],result['dfe_taps_input'])
                    self.assertEqual(result['bias_output'],.2)
                    self.assertAlmostEqual(result['sample_time_output']*25.e9,.25,places=13)
                    self.assertEqual(result['normalization_offset_output'],.1)
                    self.assertEqual(result['normalization_scale_output'],2.)
                    self.assertFalse(result['equalizer_result']['trained'])
                    self.assertEqual(result['equalizer_result']['ctle_candidates'],[])
                    self.assertIsNone(result['equalizer_result']['validation_mse'])

        constant=si.td.wf.Waveform(waveform.td,0.)
        fixed=self.equalize(constant,train_equalizer=False,baud_rate=25.e9)
        self.assertEqual(list(fixed['output_waveform_1']),[0.]*len(constant))

    def testFixedDfeAppliesSuppliedCoefficientsWithoutClipping(self):
        import ast
        import numpy as np

        waveform=si.td.wf.Waveform(si.td.wf.TimeDescriptor(0.,64,100.e9),0.)
        result=self.equalize(waveform,train_equalizer='False',baud_rate=25.e9,
                             levels=2,amplitude=2.,ffe_taps_input='[1]',
                             dfe_taps_input='.4',bias_input=2.,max_dfe_tap=0.)
        # A constant positive decision feeds back 0.4 after the first decision UI.
        np.testing.assert_array_equal(result['output_waveform_1'],[2.]*10+[1.6]*54)
        self.assertEqual(ast.literal_eval(result['dfe_taps_output']),[.4])

    def testInvalidFixedEqualizerInputsRaise(self):
        import numpy as np
        from SignalIntegrity.Lib.Exception import SignalIntegrityExceptionDependentWaveform

        waveform=si.td.wf.Waveform(si.td.wf.TimeDescriptor(0.,64,100.e9),0.)
        for parameters in [
                {'train_equalizer':'not a boolean'}, {'train_equalizer':1},
                {'ffe_taps_input':'not a list'}, {'ffe_taps_input':'[]'},
                {'ffe_taps_input':'[True]'}, {'ffe_taps_input':'[[1]]'},
                {'dfe_taps_input':[np.inf]}, {'ffe_taps_input':[1+2j]},
                {'normalization_scale_input':0.}, {'normalization_offset_input':np.nan},
                {'bias_input':np.inf}, {'sample_time_input':np.inf},
                {'GDC_input':1.}, {'GDC2_input':np.nan},
                {'ffe_taps_input':'[1, 0]', 'num_precursor_taps':2}]:
            with self.subTest(parameters=parameters):
                settings=dict(train_equalizer='False',baud_rate=25.e9)
                settings.update(parameters)
                with self.assertRaises(SignalIntegrityExceptionDependentWaveform):
                    self.equalize(waveform,**settings)

    def testTrainedSettingsReplayExactlyAfterSave(self):
        import ast
        import tempfile
        import numpy as np
        import SignalIntegrity.App as siapp
        from unittest.mock import patch
        from SignalIntegrity.App.Device import DeviceWaveformProcessorVariable
        from SignalIntegrity.App.SignalIntegrityAppHeadless import SignalIntegrityAppHeadless

        rng=np.random.default_rng(117)
        symbols=rng.choice([-.5,.5],1800)
        channel=np.convolve(symbols,[.2,1.,.45,.12])
        waveform=si.td.wf.Waveform(si.td.wf.TimeDescriptor(0.,4*len(channel),100.e9),
                                 np.repeat(channel,4).tolist())
        cwd=os.getcwd()
        self.addCleanup(os.chdir,cwd)
        with patch.object(siapp,'Project',getattr(siapp,'Project',None),create=True), \
             patch.object(siapp,'Preferences',getattr(siapp,'Preferences',None),create=True):
            app=SignalIntegrityAppHeadless()
            self.assertTrue(app.OpenProjectFile(
                os.path.join(self.projectDirectory,'TestEqualizer.si'),writable=True))
            processor=next(device for device in app.Drawing.schematic.deviceList
                           if isinstance(device,DeviceWaveformProcessorVariable))
            parameters=dict(train_equalizer='True',baud_rate='25000000000',levels='2',
                            GDC_choices='[-10]',GDC2_choices='[-3]',num_ffe_taps='5',
                            num_precursor_taps='2',num_dfe_taps='2')
            byName={variable['Name']:variable for variable in processor.variablesList}
            for name,value in parameters.items():
                byName[name]['Value']=value
            labels=[processor['ref'].GetValue()+'_in1']
            trained=processor.Waveforms()[0]
            trained.UpdateWaveform(labels,[waveform],0)
            delay=float(byName['sample_time_output'].Value())
            self.assertGreaterEqual(delay,0.)
            self.assertLess(delay,1/25.e9)
            self.assertAlignedDescriptor(trained,waveform.td,delay)
            self.assertTrue(any(ast.literal_eval(byName['dfe_taps_output'].Value())))
            for stem in ['ffe_taps','dfe_taps','GDC','GDC2','normalization_offset',
                         'normalization_scale','bias','sample_time']:
                byName[stem+'_input']['Value']=byName[stem+'_output'].Value()
            byName['train_equalizer']['Value']='False'
            # Supplied coefficients, not the training counts/limits, govern fixed mode.
            byName['num_ffe_taps']['Value']='1'
            byName['num_dfe_taps']['Value']='0'
            byName['max_dfe_tap']['Value']='0'
            with tempfile.TemporaryDirectory() as directory:
                try:
                    filename=os.path.join(directory,'fixed-equalizer.si')
                    app.SaveProjectToFile(filename)
                    restored=SignalIntegrityAppHeadless()
                    self.assertTrue(restored.OpenProjectFile(filename))
                    processor=next(device for device in restored.Drawing.schematic.deviceList
                                   if isinstance(device,DeviceWaveformProcessorVariable))
                    frozen=processor.Waveforms()[0]
                    with patch('scipy.optimize.minimize',side_effect=AssertionError('training called')), \
                         patch('scipy.optimize.lsq_linear',side_effect=AssertionError('training called')):
                        frozen.UpdateWaveform(labels,[waveform],0)
                    np.testing.assert_array_equal(frozen,trained)
                    self.assertEqual(frozen.td,trained.td)
                finally:
                    os.chdir(cwd)

    def testSchematicAppliesFixedSettingsWithoutTraining(self):
        import ast
        import sys
        import SignalIntegrity.App as siapp
        from unittest.mock import patch
        from SignalIntegrity.App.Device import DeviceWaveformProcessorVariable
        from SignalIntegrity.App.SignalIntegrityAppHeadless import SignalIntegrityAppHeadless

        cwd=os.getcwd()
        searchPath=sys.path[:]
        self.addCleanup(os.chdir,cwd)
        self.addCleanup(setattr,sys,'path',searchPath)
        with patch.object(siapp,'Project',getattr(siapp,'Project',None),create=True), \
             patch.object(siapp,'Preferences',getattr(siapp,'Preferences',None),create=True):
            app=SignalIntegrityAppHeadless()
            siapp.Preferences['Cache.CacheResults']=False
            siapp.Preferences['Calculation.Processing.StopOnConvergence']=False
            self.assertTrue(app.OpenProjectFile(
                os.path.join(self.projectDirectory,'TestEqualizer.si')))
            processor=next(device for device in app.Drawing.schematic.deviceList
                           if isinstance(device,DeviceWaveformProcessorVariable)
                           and device['ref'].GetValue() == 'WFP1')
            byName={variable['Name']:variable for variable in processor.variablesList}
            self.disableSchematicTraining(app.Drawing.schematic)
            with patch('scipy.optimize.minimize',side_effect=AssertionError('training called')), \
                 patch('scipy.optimize.lsq_linear',side_effect=AssertionError('training called')):
                result=app.Simulate()
            self.assertIn('output waveforms',result)
            for stem in ['ffe_taps','dfe_taps']:
                self.assertEqual(byName[stem+'_output'].Value(),
                                 str([float(value) for value in ast.literal_eval(
                                     byName[stem+'_input'].Value())]))
            self.assertEqual(byName['GDC_output'].Value(),str(float(byName['GDC_input'].Value())))
            self.assertEqual(byName['GDC2_output'].Value(),str(float(byName['GDC2_input'].Value())))

    def testSuppliedWaveformImprovesWithoutReference(self):
        import numpy as np

        waveform=si.td.wf.Waveform().ReadFromFile(os.path.join(self.projectDirectory,'Vo.txt'))
        result=self.equalize(waveform)
        output=result['output_waveform_1']
        metrics=result['equalizer_result']
        self.assertEqual(len(metrics['ctle_candidates']),44)
        winner=min(metrics['ctle_candidates'],key=lambda item:item['validation_mse'])
        self.assertEqual((metrics['GDC'],metrics['GDC2']),(winner['GDC'],winner['GDC2']))
        self.assertEqual(metrics['validation_mse'],winner['validation_mse'])
        self.assertLessEqual(max(abs(tap) for tap in metrics['dfe']),.3+1.e-12)
        self.assertLess(metrics['validation_mse'],.2*metrics['unequalized_mse'])
        delay=result['sample_time_output']
        self.assertGreaterEqual(delay,0.)
        self.assertLess(delay,1/self.defaults['baud_rate'])
        self.assertAlignedDescriptor(output,waveform.td,delay)
        self.assertEqual(len(output),len(waveform))
        self.assertTrue(np.all(np.isfinite(output)))
        # Check the emitted waveform, not just the internal training objective.
        first=(output.td.H-waveform.td.H)*waveform.td.Fs
        sps=waveform.td.Fs/self.defaults['baud_rate']
        last_symbol=int((len(waveform)-1)/sps)-self.defaults['num_precursor_taps']-1
        symbols=np.arange(int(.75*len(waveform)/sps),
                          last_symbol-1)+metrics['phase_ui']
        values=np.interp(symbols*sps+delay*waveform.td.Fs-first,np.arange(len(output)),output)
        alphabet=np.linspace(-.5,.5,self.defaults['levels'])
        errors=np.min(np.abs(values[:,None]-alphabet),axis=1)
        self.assertLess(np.mean(errors**2)/(alphabet[1]-alphabet[0])**2,.025)
        self.assertGreater(np.std(errors),1.e-4)

    def testBlindPamRecoveryAndFractionalSamplesPerUI(self):
        import numpy as np

        for levels,sps,dfe in [(2,4.,0),(4,4.,3),(6,4.3,3)]:
            with self.subTest(levels=levels,samplesPerUI=sps,dfe=dfe):
                rng=np.random.default_rng(117)
                symbols=rng.choice(np.linspace(-.5,.5,levels),5000)
                channel=np.convolve(symbols,[.2,1.,.45,.12])
                indices=np.floor(np.arange(int(len(channel)*sps))/sps).astype(int)
                values=channel[indices]+rng.normal(0,.002,len(indices))
                baud=25.e9
                waveform=si.td.wf.Waveform(
                    si.td.wf.TimeDescriptor(-2.e-9,len(values),sps*baud),values.tolist())
                result=self.equalize(waveform,levels=levels,baud_rate=baud,GDC_choices=[0.],GDC2_choices=[0.],
                                     num_ffe_taps=7,num_precursor_taps=2,num_dfe_taps=dfe,amplitude=1.)
                output=result['output_waveform_1']
                phase=result['equalizer_result']['phase_ui']
                first=(output.td.H-waveform.td.H)*waveform.td.Fs
                n=np.arange(3000,4800)
                sampleDelay=result['sample_time_output']
                recovered=np.interp((n+phase)*sps+sampleDelay*waveform.td.Fs-first,np.arange(len(output)),output)
                alphabet=np.linspace(-.5,.5,levels)
                decisions=np.argmin(abs(recovered[:,None]-alphabet),axis=1)
                bestError=1.
                for delay in range(-7,8):
                    for polarity in [-1,1]:
                        target=np.rint((polarity*symbols[n+delay]+.5)*(levels-1)).astype(int)
                        bestError=min(bestError,np.mean(decisions != target))
                self.assertLess(bestError,.01)
                self.assertAlignedDescriptor(output,waveform.td,sampleDelay)
                self.assertEqual(len(output),len(waveform))
                self.assertTrue(np.all(np.isfinite(output)))

    def testCtleSearchMatchesIndependentFitsAndBoundsDfe(self):
        import ast
        import numpy as np

        rng=np.random.default_rng(117)
        symbols=rng.choice([-.5,.5],1800)
        channel=np.convolve(symbols,[1.,.55])
        waveform=si.td.wf.Waveform(
            si.td.wf.TimeDescriptor(0.,4*len(channel),100.e9),
            np.repeat(channel,4).tolist())
        parameters=dict(baud_rate=25.e9,levels=2,num_ffe_taps=1,num_precursor_taps=0,num_dfe_taps=1)
        independent=[]
        for gdc in [0.,-10.]:
            for gdc2 in [0.,-3.]:
                result=self.equalize(waveform,GDC_choices=[gdc],GDC2_choices=[gdc2],**parameters)
                independent.append(result['equalizer_result'])
        result=self.equalize(waveform,GDC_choices='[0, -10]',GDC2_choices='[0, -3]',**parameters)
        metrics=result['equalizer_result']
        winner=min(independent,key=lambda item:item['validation_mse'])
        self.assertEqual((metrics['GDC'],metrics['GDC2']),(winner['GDC'],winner['GDC2']))
        self.assertAlmostEqual(metrics['validation_mse'],winner['validation_mse'],places=12)
        for candidate,fit in zip(metrics['ctle_candidates'],independent):
            self.assertAlmostEqual(candidate['validation_mse'],fit['validation_mse'],places=12)
        self.assertEqual(metrics['gdc_db'],metrics['GDC'])
        self.assertEqual(metrics['gdc2_db'],metrics['GDC2'])
        self.assertEqual(result['GDC_output'],metrics['gdc_db'])
        self.assertEqual(result['GDC2_output'],metrics['gdc2_db'])
        self.assertEqual(ast.literal_eval(result['ffe_taps_output']),metrics['ffe'])
        self.assertEqual([(item['GDC'],item['GDC2']) for item in metrics['ctle_candidates']],
                         [(0.,0.),(0.,-3.),(-10.,0.),(-10.,-3.)])
        fits=[]
        for limit in [0.,.05,.3,1.]:
            fit=self.equalize(waveform,GDC_choices=[0.],GDC2_choices=[0.],
                              max_dfe_tap=limit,**parameters)['equalizer_result']
            self.assertLessEqual(max(abs(tap) for tap in fit['dfe']),limit+1.e-12)
            fits.append(fit)
        self.assertGreater(abs(fits[-1]['dfe'][0]),.3)
        self.assertLess(fits[-2]['validation_mse'],fits[0]['validation_mse'])

    def testRepeatedExecutionPreservesSamplesAndAppliesDelay(self):
        import numpy as np

        waveform=si.td.wf.Waveform().ReadFromFile(os.path.join(self.projectDirectory,'Vo.txt'))
        for iteration in range(3):
            with self.subTest(iteration=iteration):
                previous=waveform.td
                result=self.equalize(waveform,GDC_choices=[-10.],GDC2_choices=[-3.])
                waveform=result['output_waveform_1']
                delay=result['sample_time_output']
                self.assertGreaterEqual(delay,0.)
                self.assertLess(delay,1/self.defaults['baud_rate'])
                self.assertAlignedDescriptor(waveform,previous,delay)
                self.assertEqual(len(waveform),previous.K)
                self.assertTrue(np.all(np.isfinite(waveform)))

    def testSchematicProcessorInputDoesNotShrinkAcrossIterations(self):
        import sys
        import numpy as np
        from unittest.mock import patch
        import SignalIntegrity.App as siapp
        from SignalIntegrity.App.SignalIntegrityAppHeadless import SignalIntegrityAppHeadless
        from SignalIntegrity.Lib.TimeDomain.Waveform.DependentWaveform import DependentWaveform

        cwd=os.getcwd()
        searchPath=sys.path[:]
        self.addCleanup(os.chdir,cwd)
        self.addCleanup(setattr,sys,'path',searchPath)
        inputs=[]
        outputSettings=[]
        evaluate=DependentWaveform.EvaluateTransformFunctionSafely

        def capture(equations,sendargs,returnargs):
            if equations != self.script or 'WFP1_in1' not in sendargs:
                return evaluate(equations,sendargs,returnargs)
            waveform=sendargs['input_waveform_1']
            inputs.append(si.td.wf.Waveform(waveform))
            sendargs=dict(sendargs,GDC_choices='[-10]',GDC2_choices='[-3]',train_equalizer='True')
            result=evaluate(equations,sendargs,returnargs)
            self.assertAlignedDescriptor(result['output_waveform_1'],
                                          waveform.td,result['sample_time_output'])
            outputSettings.append((result['ffe_taps_output'],result['GDC_output'],
                                   result['GDC2_output']))
            return result

        with patch.object(siapp,'Project',getattr(siapp,'Project',None),create=True), \
             patch.object(siapp,'Preferences',getattr(siapp,'Preferences',None),create=True):
            app=SignalIntegrityAppHeadless()
            siapp.Preferences['Cache.CacheResults']=False
            siapp.Preferences['Calculation.Processing.StopOnConvergence']=False
            self.assertTrue(app.OpenProjectFile(
                os.path.join(self.projectDirectory,'TestEqualizer.si')))
            self.disableSchematicTraining(app.Drawing.schematic)
            with patch.object(DependentWaveform,'EvaluateTransformFunctionSafely',
                              side_effect=capture):
                result=app.Simulate()
            self.assertIn('output waveforms',result)
            self.assertEqual(
                tuple(siapp.Project['Variables'].VariableByName(name)['Value']
                      for name in ['ffe_taps','GDC','GDC2']),
                tuple(str(value) for value in outputSettings[-1]))
        self.assertGreaterEqual(len(inputs),2)
        for waveform in inputs[1:]:
            self.assertEqual(waveform.td,inputs[0].td)
            self.assertEqual(len(waveform),len(inputs[0]))
            np.testing.assert_array_equal(waveform,inputs[0])

    def testInvalidEqualizerInputsRaise(self):
        import numpy as np
        from SignalIntegrity.Lib.Exception import SignalIntegrityExceptionDependentWaveform

        waveform=si.td.wf.Waveform(si.td.wf.TimeDescriptor(0.,4096,425.e9),
                                 np.random.default_rng(17).normal(size=4096).tolist())
        for parameters in [{'baud_rate':0.},{'levels':1},{'amplitude':0.},
                           {'num_ffe_taps':2,'num_precursor_taps':2},{'num_dfe_taps':-1},
                           {'GDC_choices':float('nan')},{'GDC_choices':[]},{'GDC_choices':[1.]},{'GDC2_choices':[1.]},
                           {'GDC2_choices':'[0, float("nan")]'},{'GDC2_choices':[float('inf')]},
                           {'GDC_choices':'[True]'},{'GDC_choices':'not a list'},
                           {'max_dfe_tap':-0.1},{'max_dfe_tap':float('nan')},
                           {'baud_rate':300.e9}]:
            with self.subTest(parameters=parameters):
                with self.assertRaises(SignalIntegrityExceptionDependentWaveform):
                    self.equalize(waveform,**parameters)
        for invalid in [si.td.wf.Waveform(waveform.td,0.),
                        si.td.wf.Waveform(si.td.wf.TimeDescriptor(0.,0,425.e9),[]),
                        si.td.wf.Waveform(si.td.wf.TimeDescriptor(0.,128,425.e9),[1.,-1.]*64),
                        si.td.wf.Waveform(waveform.td,[float('nan')]*4096)]:
            with self.assertRaises(SignalIntegrityExceptionDependentWaveform):
                self.equalize(invalid)


if __name__ == "__main__":
    unittest.main()
