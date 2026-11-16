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
                      else float(variable['Value']) for variable in variables}

    def equalize(self,waveform,**parameters):
        from SignalIntegrity.Lib.TimeDomain.Waveform.DependentWaveform import DependentWaveform

        namespace=dict(self.defaults,input_waveform_1=waveform,**parameters)
        return DependentWaveform.EvaluateTransformFunctionSafely(
            self.script,namespace,{'output_waveform_1':None,'equalizer_result':None})

    def testSuppliedWaveformImprovesWithoutReference(self):
        import numpy as np

        waveform=si.td.wf.Waveform().ReadFromFile(os.path.join(self.projectDirectory,'Vo.txt'))
        result=self.equalize(waveform)
        output=result['output_waveform_1']
        metrics=result['equalizer_result']
        self.assertLess(metrics['validation_mse'],.2*metrics['unequalized_mse'])
        self.assertEqual(output.td,waveform.td)
        self.assertEqual(len(output),len(waveform))
        self.assertTrue(np.all(np.isfinite(output)))
        # Check the emitted waveform, not just the internal training objective.
        first=(output.td.H-waveform.td.H)*waveform.td.Fs
        sps=waveform.td.Fs/self.defaults['baud_rate']
        last_symbol=int((len(waveform)-1)/sps)-self.defaults['precursor_taps']-1
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
                result=self.equalize(waveform,levels=levels,baud_rate=baud,GDC=0.,GDC2=0.,
                                     ffe_taps=7,precursor_taps=2,dfe_taps=dfe,amplitude=1.)
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

    def testRepeatedExecutionPreservesTimeDescriptor(self):
        import numpy as np

        waveform=si.td.wf.Waveform().ReadFromFile(os.path.join(self.projectDirectory,'Vo.txt'))
        descriptor=si.td.wf.TimeDescriptor(waveform.td.H,waveform.td.K,waveform.td.Fs)
        for iteration in range(3):
            with self.subTest(iteration=iteration):
                waveform=self.equalize(waveform)['output_waveform_1']
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
        evaluate=DependentWaveform.EvaluateTransformFunctionSafely

        def capture(equations,sendargs,returnargs):
            waveform=sendargs['input_waveform_1']
            inputs.append(si.td.wf.Waveform(waveform))
            result=evaluate(equations,sendargs,returnargs)
            self.assertEqual(result['output_waveform_1'].td,waveform.td)
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
                           {'ffe_taps':2,'precursor_taps':2},{'dfe_taps':-1},
                           {'GDC':float('nan')},{'baud_rate':300.e9}]:
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
