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
                    if device.findtext('ClassName') == 'DeviceWaveformProcessorVariable')
        cls.script=next(prop.findtext('Value') for prop in device.findall('./PartProperties/PartProperty')
                        if prop.findtext('Keyword') == 'script')
        _,_,variables=ParseWaveformProcessorInterface(cls.script)
        cls.defaults={variable['Name']:int(variable['Value']) if variable['Type'] == 'int'
                      else float(variable['Value']) if variable['Type'] == 'float'
                      else variable['Value'] for variable in variables}

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
                                   'bias_output':None,'phase_ui_output':None,
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
            for ffe,dfe in [('2','0'),(2.,0.),([2.],[0.]),('[2.]','[0.]')]:
                with self.subTest(ffe=ffe,dfe=dfe):
                    result=self.equalize(
                        waveform,train_equalizer='False',baud_rate=25.e9,levels=2,
                        amplitude=2.,ffe_taps_input=ffe,dfe_taps_input=dfe,
                        GDC_input=-7.,GDC2_input=-2.,
                        GDC_choices='unused',GDC2_choices='unused',
                        normalization_offset_input=.1,normalization_scale_input=2.,
                        bias_input=.2,phase_ui_input=.25)
                    size=1 << (len(waveform)+1024-1).bit_length()
                    frequencies=np.fft.rfftfreq(size,1/waveform.td.Fs)
                    ctle=CTLE([0.],-7.,-2.,10.e9,25.e9/80,10.e9,25.e9)
                    response=ctle._Evaluate(frequencies)
                    response[-1]=response[-1].real
                    filtered=np.fft.irfft(np.fft.rfft(waveform,size)*response,size)[:len(waveform)]
                    np.testing.assert_array_equal(result['output_waveform_1'],
                                                  (filtered-.1)/2.*2.+.2)
                    self.assertEqual(result['output_waveform_1'].td,waveform.td)
                    self.assertEqual(result['GDC_output'],-7.)
                    self.assertEqual(result['GDC2_output'],-2.)
                    self.assertEqual(ast.literal_eval(result['ffe_taps_input']),[2.])
                    self.assertEqual(ast.literal_eval(result['dfe_taps_input']),[0.])
                    self.assertEqual(result['ffe_taps_output'],result['ffe_taps_input'])
                    self.assertEqual(result['dfe_taps_output'],result['dfe_taps_input'])
                    self.assertEqual(result['bias_output'],.2)
                    self.assertEqual(result['phase_ui_output'],.25)
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
                {'bias_input':np.inf}, {'phase_ui_input':1.},
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
            self.assertTrue(any(ast.literal_eval(byName['dfe_taps_output'].Value())))
            for stem in ['ffe_taps','dfe_taps','GDC','GDC2','normalization_offset',
                         'normalization_scale','bias','phase_ui']:
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

    def testSavedSchematicDefaultsToFixedSettings(self):
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
            with patch('scipy.optimize.minimize',side_effect=AssertionError('training called')), \
                 patch('scipy.optimize.lsq_linear',side_effect=AssertionError('training called')):
                result=app.Simulate()
            self.assertIn('output waveforms',result)
            processor=next(device for device in app.Drawing.schematic.deviceList
                           if isinstance(device,DeviceWaveformProcessorVariable))
            byName={variable['Name']:variable for variable in processor.variablesList}
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
        self.assertEqual(output.td,waveform.td)
        self.assertEqual(len(output),len(waveform))
        self.assertTrue(np.all(np.isfinite(output)))
        # Check the emitted waveform, not just the internal training objective.
        first=(output.td.H-waveform.td.H)*waveform.td.Fs
        sps=waveform.td.Fs/self.defaults['baud_rate']
        last_symbol=int((len(waveform)-1)/sps)-self.defaults['num_precursor_taps']-1
        symbols=np.arange(int(.75*len(waveform)/sps),
                          last_symbol-1)+metrics['phase_ui']
        values=np.interp(symbols*sps-first,np.arange(len(output)),output)
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
                recovered=np.interp((n+phase)*sps-first,np.arange(len(output)),output)
                alphabet=np.linspace(-.5,.5,levels)
                decisions=np.argmin(abs(recovered[:,None]-alphabet),axis=1)
                bestError=1.
                for delay in range(-7,8):
                    for polarity in [-1,1]:
                        target=np.rint((polarity*symbols[n+delay]+.5)*(levels-1)).astype(int)
                        bestError=min(bestError,np.mean(decisions != target))
                self.assertLess(bestError,.01)
                self.assertEqual(output.td,waveform.td)
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

    def testRepeatedExecutionPreservesTimeDescriptor(self):
        import numpy as np

        waveform=si.td.wf.Waveform().ReadFromFile(os.path.join(self.projectDirectory,'Vo.txt'))
        descriptor=si.td.wf.TimeDescriptor(waveform.td.H,waveform.td.K,waveform.td.Fs)
        for iteration in range(3):
            with self.subTest(iteration=iteration):
                waveform=self.equalize(waveform,GDC_choices=[-10.],GDC2_choices=[-3.])['output_waveform_1']
                self.assertEqual(waveform.td,descriptor)
                self.assertEqual(len(waveform),descriptor.K)
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
            waveform=sendargs['input_waveform_1']
            inputs.append(si.td.wf.Waveform(waveform))
            sendargs=dict(sendargs,GDC_choices='[-10]',GDC2_choices='[-3]',train_equalizer='True')
            result=evaluate(equations,sendargs,returnargs)
            self.assertEqual(result['output_waveform_1'].td,waveform.td)
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
