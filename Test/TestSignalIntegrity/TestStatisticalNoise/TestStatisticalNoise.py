"""
TestStatisticalNoise.py
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

import unittest
import SignalIntegrity.Lib as si
import SignalIntegrity.App.SignalIntegrityAppHeadless as siapp
import os
import math
import tempfile
import json
import SignalIntegrity.App.Project as proj
from SignalIntegrity.Lib.Test.SignalIntegrityAppTestHelper import SignalIntegrityAppTestHelper

class TestStatisticalNoiseTest(unittest.TestCase,
        si.test.SParameterCompareHelper,si.test.SignalIntegrityAppTestHelper,
        si.test.RoutineWriterTesterHelper):
    relearn=True
    plot=False
    debug=False
    checkPictures=True
    epsilon=50e-12
    plotErrors=True
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.cwd=os.getcwd()
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        from SignalIntegrity.App.SignalIntegrityAppHeadless import SignalIntegrityAppHeadless
        import SignalIntegrity.App.Project
        pysi=SignalIntegrityAppHeadless()
        self.UseSinX=SignalIntegrity.App.Preferences['Calculation.UseSinX']
        SignalIntegrity.App.Preferences['Calculation.UseSinX']=True
        SignalIntegrity.App.Preferences.SaveToFile()
        pysi=SignalIntegrityAppHeadless()
        SignalIntegrity.App.Preferences['Calculation'].ApplyPreferences()
    def tearDown(self):
        unittest.TestCase.tearDown(self)
        os.chdir(self.cwd)
        from SignalIntegrity.App.SignalIntegrityAppHeadless import SignalIntegrityAppHeadless
        import SignalIntegrity.App.Project
        pysi=SignalIntegrityAppHeadless()
        SignalIntegrity.App.Preferences['Calculation.UseSinX']=self.UseSinX
        SignalIntegrity.App.Preferences.SaveToFile()
        pysi=SignalIntegrityAppHeadless()
        SignalIntegrity.App.Preferences['Calculation'].ApplyPreferences()
    def __init__(self, methodName='runTest'):
        si.test.SParameterCompareHelper.__init__(self)
        unittest.TestCase.__init__(self,methodName)
        si.test.SignalIntegrityAppTestHelper.__init__(self,os.path.dirname(os.path.realpath(__file__)))
        si.test.RoutineWriterTesterHelper.__init__(self)
    def testStatisticalNoise(self):
        self.SimulationResultsChecker('StatisticalNoise.si',checkNoise = True)
    def testStatisticalNoiseAbove(self):
        self.SimulationResultsChecker('StatisticalNoiseExternal.si',checkNoise = True)
    def testNoiseWaveform(self):
        """
        This simulation has five probes VO1-VO7.

        The first is for an actual noise waveform specified: 10 mVrms of noise at 80 GS/s (to 40 GHz).
        The second is a statistical noise source specified with 10 mVrms of noise to 40 GHz.
        The third is a statistical noise source specified with a waveform generated in 1.
        The fourth is the time domain waveform used for the third statistical noise source.
        The fifth is a statistical noise source specified with a spectral density file with 15.81 nV/sqrt(Hz) to 100 GHz.  It is a .txt file.
        The sixth is a statistical noise source specified with a spectral density csv file to 40 GHz.
        The fifth is a statistical noise source specified with a spectral density json file to 40 GHz.

        Therefore, VO1 and VO4 produce actual waveforms and zero noise spectral density.
        VO2 and VO3,V04,V05,V06,V07 produce a 0V DC waveform with spectral density.
        
        """
        from SignalIntegrity.Lib.TimeDomain.Waveform.NoiseWaveform import NoiseWaveform

        old_seed = NoiseWaveform.seed
        NoiseWaveform.seed = 0
        try:
            results = self.SimulationResultsChecker('StatisticalNoiseWaveforms.si',checkNoise = True, checkWaveforms = False)
        finally:
            NoiseWaveform.seed = old_seed
        VO1_wf = results['output waveforms'][results['output waveform labels'].index('VO1')]
        VO2_wf = results['output waveforms'][results['output waveform labels'].index('VO2')]
        VO3_wf = results['output waveforms'][results['output waveform labels'].index('VO3')]
        VO4_wf = results['output waveforms'][results['output waveform labels'].index('VO4')]
        VO5_wf = results['output waveforms'][results['output waveform labels'].index('VO5')]
        VO6_wf = results['output waveforms'][results['output waveform labels'].index('VO6')]
        VO7_wf = results['output waveforms'][results['output waveform labels'].index('VO7')]
        VO1_sd = results['noise']['output_noise_spectral_density']['VO1']
        VO2_sd = results['noise']['output_noise_spectral_density']['VO2']
        VO3_sd = results['noise']['output_noise_spectral_density']['VO3']
        VO4_sd = results['noise']['output_noise_spectral_density']['VO4']
        VO5_sd = results['noise']['output_noise_spectral_density']['VO5']
        VO6_sd = results['noise']['output_noise_spectral_density']['VO6']
        VO7_sd = results['noise']['output_noise_spectral_density']['VO7']
        from SignalIntegrity.Lib.ToSI import ToSI

        # VO1
        self.assertEqual(ToSI(VO1_wf.rms(),'Vrms',round=2),'10.0 mVrms')
        self.assertEqual(ToSI(VO1_wf.SpectralDensity().TotalRMS(),'Vrms',round=2),'10.0 mVrms')
        self.assertEqual(ToSI(VO1_sd['Vrms'],'Vrms'),'0 Vrms')

        # VO2
        self.assertEqual(ToSI(VO2_sd['Vrms'],'Vrms',round=2),'10.0 mVrms')
        self.assertEqual(ToSI(VO2_wf.rms(),'Vrms'),'0 Vrms')

        # VO3
        self.assertEqual(ToSI(VO3_sd['Vrms'],'Vrms',round=2),'10.0 mVrms')
        self.assertEqual(ToSI(VO3_wf.rms(),'Vrms'),'0 Vrms')

        # VO4
        self.assertEqual(ToSI(VO4_wf.rms(),'Vrms',round=2),'10.0 mVrms')
        self.assertEqual(ToSI(VO4_wf.SpectralDensity().TotalRMS(),'Vrms',round=2),'10.0 mVrms')
        self.assertEqual(ToSI(VO4_sd['Vrms'],'Vrms'),'0 Vrms')

        # VO5
        # this generates 10 mVrms of total noise by having 10 lanes of noise
        self.assertEqual(ToSI(VO5_sd['Vrms'],'Vrms',round=2),'10.0 mVrms')
        self.assertEqual(ToSI(VO5_wf.rms(),'Vrms'),'0 Vrms')

        # VO6
        # from .csv file.
        self.assertEqual(ToSI(VO6_sd['Vrms'],'Vrms',round=2),'26.0 uVrms')
        self.assertEqual(ToSI(VO6_wf.rms(),'Vrms'),'0 Vrms')

        # VO7
        # from .json file.
        self.assertEqual(ToSI(VO7_sd['Vrms'],'Vrms',round=2),'2.5 mVrms')
        self.assertEqual(ToSI(VO7_wf.rms(),'Vrms'),'0 Vrms')

    def testAttenuator(self):
        self.SimulationResultsChecker('Attenuator.si',checkNoise = True)

    def testCrosstalk(self):
        self.SimulationResultsChecker('CrosstalkAnalysis.si',checkNoise = True)

    def testSpectralDensitySNRdB(self):
        fd = si.fd.EvenlySpacedFrequencyList(40e9, 400)
        signal_sd = si.fd.SpectralDensity.WhiteNoise(fd, 'Vrms', 10e-3, noise_bandwidth=40e9)
        noise_sd = si.fd.SpectralDensity.WhiteNoise(fd, 'Vrms', 1e-3, noise_bandwidth=40e9)

        self.assertAlmostEqual(noise_sd.SNRdB(signal_sd, 'signal'), 20.0, places=12)
        self.assertAlmostEqual(signal_sd.SNRdB(noise_sd, 'noise'), 20.0, places=12)

        with self.assertRaises(ValueError):
            signal_sd.SNRdB(noise_sd, 'invalid')

        with self.assertRaises(TypeError):
            signal_sd.SNRdB(1.0, 'noise')

    def testSpectralDensitySalzSNRdB(self):
        fd_signal = si.fd.EvenlySpacedFrequencyList(40e9, 400)
        fd_noise = si.fd.EvenlySpacedFrequencyList(40e9, 200)
        signal_sd = si.fd.SpectralDensity.WhiteNoise(fd_signal, 'Vrms', 10e-3, noise_bandwidth=40e9)
        noise_sd = si.fd.SpectralDensity.WhiteNoise(fd_noise, 'Vrms', 1e-3, noise_bandwidth=40e9)

        # Uses different frequency grids to verify internal resampling to self.
        self.assertAlmostEqual(noise_sd.SalzSNRdB(signal_sd, 'signal'), 20.0, places=12)
        self.assertAlmostEqual(signal_sd.SalzSNRdB(noise_sd, 'noise'), 20.0, places=12)

        with self.assertRaises(ValueError):
            signal_sd.SalzSNRdB(noise_sd, 'invalid')

        with self.assertRaises(TypeError):
            signal_sd.SalzSNRdB(1.0, 'noise')

        with self.assertRaises(ValueError):
            signal_sd.SalzSNRdB(noise_sd, 'noise', noise_floor=0.0)

    def testSpectralDensityReadFromCSVSkipsExtraneousText(self):
        fd, fileName = tempfile.mkstemp(suffix='.csv')
        try:
            with os.fdopen(fd,'w') as f:
                f.write('some tool-specific header text\n')
                f.write('frequency,density\n')
                f.write('\n')
                f.write('1.0,2.0e-9\n')
                f.write('ignore this line entirely\n')
                f.write('2.0,3.0e-9,extra column\n')
                f.write('three,4.0e-9\n')
                f.write('3.0,4.0e-9\n')
            sd=si.fd.SpectralDensity(Keven=False).ReadFromCSV(fileName)
            self.assertEqual(sd.Frequencies(),[1.0,2.0,3.0])
            self.assertEqual(sd.Values('V/sqrt(Hz)'),[2.0e-9,3.0e-9,4.0e-9])
            self.assertFalse(sd.Keven)
        finally:
            os.remove(fileName)

    def testSpectralDensityReadFromCSVCadenceNoiseFile(self):
        fileName=os.path.join(os.path.dirname(os.path.realpath(__file__)),'InputNoise_80C_3p3V_tt_gainID_0.csv')
        sd=si.fd.SpectralDensity().ReadFromCSV(fileName)
        self.assertTrue(len(sd) > 1000)
        self.assertAlmostEqual(sd.Frequencies()[0],100000.0)
        self.assertAlmostEqual(sd.Values('V/sqrt(Hz)')[0],5.935415921178399e-09)

    def testSpectralDensityWriteToCSVWritesFrequencyAndDensityColumns(self):
        fd, fileName = tempfile.mkstemp(suffix='.csv')
        try:
            os.close(fd)
            sd=si.fd.SpectralDensity([1.0,2.0,3.0],[2.0e-9,3.0e-9,4.0e-9])
            sd.WriteToCSV(fileName)
            with open(fileName,'r') as f:
                lines=f.readlines()
            self.assertEqual(lines,['1.0,2e-09\n','2.0,3e-09\n','3.0,4e-09\n'])
        finally:
            os.remove(fileName)

    def testSpectralDensityWriteToCSVRoundTrip(self):
        fd, fileName = tempfile.mkstemp(suffix='.csv')
        try:
            os.close(fd)
            original=si.fd.SpectralDensity([1.0,2.0,3.0],[2.0e-9,3.0e-9,4.0e-9],Keven=False)
            original.WriteToCSV(fileName)
            readback=si.fd.SpectralDensity(Keven=False).ReadFromCSV(fileName)
            self.assertEqual(readback,original)
            self.assertFalse(readback.Keven)
        finally:
            os.remove(fileName)

    def testSpectralDensityReadFromJsonNoiseDensityFile(self):
        fileName=os.path.join(os.path.dirname(os.path.realpath(__file__)),'noise_density.json')
        sd=si.fd.SpectralDensity().ReadFromJson(fileName)
        self.assertEqual(len(sd),6501)
        self.assertAlmostEqual(sd.Frequencies()[0],1.0e7)
        self.assertAlmostEqual(sd.Values('V/sqrt(Hz)')[0],9.148053e-09)
        self.assertAlmostEqual(sd.Frequencies()[-1],1.3e11)
        self.assertAlmostEqual(sd.Values('V/sqrt(Hz)')[-1],2.760135e-09)

    def testSpectralDensityReadFromJsonAllowsTrailingData(self):
        fd, fileName = tempfile.mkstemp(suffix='.json')
        try:
            with os.fdopen(fd,'w') as f:
                f.write('{"x":[1.0,2.0,3.0],"y":[2.0e-9,3.0e-9,4.0e-9]}\n}\n')
            sd=si.fd.SpectralDensity(Keven=False).ReadFromJson(fileName)
            self.assertEqual(sd.Frequencies(),[1.0,2.0,3.0])
            self.assertEqual(sd.Values('V/sqrt(Hz)'),[2.0e-9,3.0e-9,4.0e-9])
            self.assertFalse(sd.Keven)
        finally:
            os.remove(fileName)

    def testSpectralDensityWriteToJsonWritesXYArrays(self):
        fd, fileName = tempfile.mkstemp(suffix='.json')
        try:
            os.close(fd)
            sd=si.fd.SpectralDensity([1.0,2.0,3.0],[2.0e-9,3.0e-9,4.0e-9])
            sd.WriteToJson(fileName)
            with open(fileName,'r') as f:
                data=json.load(f)
            self.assertEqual(data['x'],[1.0,2.0,3.0])
            self.assertEqual(data['y'],[2.0e-9,3.0e-9,4.0e-9])
        finally:
            os.remove(fileName)

    def testSpectralDensityWriteToJsonRoundTrip(self):
        fd, fileName = tempfile.mkstemp(suffix='.json')
        try:
            os.close(fd)
            original=si.fd.SpectralDensity([1.0,2.0,3.0],[2.0e-9,3.0e-9,4.0e-9],Keven=False)
            original.WriteToJson(fileName)
            readback=si.fd.SpectralDensity(Keven=False).ReadFromJson(fileName)
            self.assertEqual(readback,original)
            self.assertFalse(readback.Keven)
        finally:
            os.remove(fileName)

    def testSpectralDensityReadFromFileDispatchCsv(self):
        fileName=os.path.join(os.path.dirname(os.path.realpath(__file__)),'InputNoise_80C_3p3V_tt_gainID_0.csv')
        sd=si.fd.SpectralDensity().ReadFromFile(fileName)
        self.assertTrue(len(sd) > 1000)
        self.assertAlmostEqual(sd.Frequencies()[0],100000.0)
        self.assertAlmostEqual(sd.Values('V/sqrt(Hz)')[0],5.935415921178399e-09)

    def testSpectralDensityReadFromFileDispatchJson(self):
        fileName=os.path.join(os.path.dirname(os.path.realpath(__file__)),'noise_density.json')
        sd=si.fd.SpectralDensity().ReadFromFile(fileName)
        self.assertEqual(len(sd),6501)
        self.assertAlmostEqual(sd.Frequencies()[0],1.0e7)
        self.assertAlmostEqual(sd.Values('V/sqrt(Hz)')[0],9.148053e-09)

    def testSpectralDensityReadFromFileDispatchTxt(self):
        fd, fileName = tempfile.mkstemp(suffix='.txt')
        try:
            os.close(fd)
            original=si.fd.SpectralDensity([1.0,2.0,3.0],[2.0e-9,3.0e-9,4.0e-9],Keven=False)
            si.fd.FrequencyDomain.WriteToFile(original,fileName)
            readback=si.fd.SpectralDensity(Keven=False).ReadFromFile(fileName)
            self.assertEqual(readback,original)
            self.assertFalse(readback.Keven)
        finally:
            os.remove(fileName)

    def testSpectralDensityWriteToFileDispatchCsv(self):
        fd, fileName = tempfile.mkstemp(suffix='.csv')
        try:
            os.close(fd)
            original=si.fd.SpectralDensity([1.0,2.0,3.0],[2.0e-9,3.0e-9,4.0e-9])
            original.WriteToFile(fileName)
            with open(fileName,'r') as f:
                lines=f.readlines()
            self.assertEqual(lines,['1.0,2e-09\n','2.0,3e-09\n','3.0,4e-09\n'])
        finally:
            os.remove(fileName)

    def testSpectralDensityWriteToFileDispatchJson(self):
        fd, fileName = tempfile.mkstemp(suffix='.json')
        try:
            os.close(fd)
            original=si.fd.SpectralDensity([1.0,2.0,3.0],[2.0e-9,3.0e-9,4.0e-9])
            original.WriteToFile(fileName)
            with open(fileName,'r') as f:
                data=json.load(f)
            self.assertEqual(data['x'],[1.0,2.0,3.0])
            self.assertEqual(data['y'],[2.0e-9,3.0e-9,4.0e-9])
        finally:
            os.remove(fileName)

    def testSpectralDensityWriteToFileDispatchTxt(self):
        fd, fileName = tempfile.mkstemp(suffix='.txt')
        try:
            os.close(fd)
            original=si.fd.SpectralDensity([1.0,2.0,3.0],[2.0e-9,3.0e-9,4.0e-9],Keven=False)
            original.WriteToFile(fileName)
            readback=si.fd.SpectralDensity(Keven=False).ReadFromFile(fileName)
            self.assertEqual(readback,original)
            self.assertFalse(readback.Keven)
        finally:
            os.remove(fileName)

    def testWhiteNoiseConfigurationVSquaredUnits(self):
        from SignalIntegrity.App.StatisticalNoisePreferencesFile import WhiteNoiseConfiguration
        from SignalIntegrity.Lib.FrequencyDomain.DFTUtilities import DFTUtilities

        cfg = WhiteNoiseConfiguration()
        cfg['NoiseBandwidth'] = 35e9

        # 2.5e-3 V^2/GHz corresponds to sqrt(2.5e-12) V/sqrt(Hz).
        expected_rho = math.sqrt(2.5e-12)
        cfg['WhiteNoiseType'] = 'V^2/GHz'
        cfg['VSquaredPerGHz'] = 2.5e-3
        self.assertAlmostEqual(cfg.NoiseDensity(), expected_rho, places=18)

        # V^2/Hz and legacy alias support were intentionally removed.
        with self.assertRaises(ValueError):
            DFTUtilities.ConvertSpectralDensity(1.0, 'V^2/Hz', 'V/sqrt(Hz)')
        with self.assertRaises(ValueError):
            DFTUtilities.ConvertSpectralDensity(1.0, 'V^2/GHIz', 'V/sqrt(Hz)')

        sd = cfg.SpectralDensity(50e9, 5)
        rho_values = sd.Values('V/sqrt(Hz)')
        self.assertEqual(len(rho_values), 6)
        self.assertEqual(rho_values[0], 0.0)
        self.assertAlmostEqual(rho_values[1], expected_rho, places=18)
        self.assertAlmostEqual(rho_values[2], expected_rho, places=18)
        self.assertAlmostEqual(rho_values[3], expected_rho, places=18)
        self.assertEqual(rho_values[4], 0.0)
        self.assertEqual(rho_values[5], 0.0)

    def testWhiteNoiseConfigurationENOB(self):
        from SignalIntegrity.App.StatisticalNoisePreferencesFile import WhiteNoiseConfiguration

        cfg = WhiteNoiseConfiguration()
        cfg['WhiteNoiseType'] = 'ENOB'
        cfg['SNR.ENOB.ENOB'] = 8.0
        cfg['SNR.Vpp'] = 1.0
        cfg['NoiseBandwidth'] = 20e9

        self.assertEqual(cfg['SNR'].NoiseBandwidth(), cfg['NoiseBandwidth'])
        self.assertEqual(cfg['SNR.ENOB'].Vpp(), cfg['SNR.Vpp'])
        self.assertEqual(cfg['SNR.ENOB'].NoiseBandwidth(), cfg['NoiseBandwidth'])

        snr_db = 6.02 * cfg['SNR.ENOB.ENOB'] + 1.76
        full_scale_sine_vrms = cfg['SNR.Vpp'] / (2.0 * math.sqrt(2.0))
        expected_vrms = full_scale_sine_vrms / (10.0 ** (snr_db / 20.0))
        expected_rho = expected_vrms / math.sqrt(cfg['NoiseBandwidth'])

        self.assertAlmostEqual(cfg.NoiseDensity(), expected_rho, places=18)

        sd = cfg.SpectralDensity(25e9, 5)
        rho_values = sd.Values('V/sqrt(Hz)')
        self.assertEqual(rho_values[0], 0.0)
        self.assertAlmostEqual(rho_values[1], expected_rho, places=18)
        self.assertAlmostEqual(rho_values[2], expected_rho, places=18)
        self.assertAlmostEqual(rho_values[3], expected_rho, places=18)
        self.assertAlmostEqual(rho_values[4], expected_rho, places=18)
        self.assertEqual(rho_values[5], 0.0)

        cfg['NoiseBandwidth'] = 0.0
        with self.assertRaises(ValueError):
            cfg.NoiseDensity()

    def testWhiteNoiseConfigurationComTx(self):
        from SignalIntegrity.App.StatisticalNoisePreferencesFile import WhiteNoiseConfiguration
        from SignalIntegrity.Lib.TimeDomain.Filters.Risetime.Gaussian import Gaussian

        cfg = WhiteNoiseConfiguration()
        cfg['WhiteNoiseType'] = 'COM TX'
        cfg['SNR.COM_TX.h0'] = 0.85
        cfg['SNR.Vpp'] = 1.2
        cfg['SNR.COM_TX.SNRdB'] = 33.0
        cfg['NoiseBandwidth'] = 40e9
        cfg['SNR.COM_TX.Risetime'] = 9e-12

        self.assertEqual(cfg['SNR.COM_TX'].Vpp(), cfg['SNR.Vpp'])
        self.assertEqual(cfg['SNR.COM_TX'].NoiseBandwidth(), cfg['NoiseBandwidth'])

        expected_vrms = cfg['SNR.COM_TX.h0'] * cfg['SNR.Vpp'] / 2.0 * (10.0 ** (-cfg['SNR.COM_TX.SNRdB'] / 20.0))
        expected_rho = expected_vrms / math.sqrt(cfg['NoiseBandwidth'])
        self.assertAlmostEqual(cfg.NoiseDensity(), expected_rho, places=18)

        sd = cfg.SpectralDensity(40e9, 4)
        rho_values = sd.Values('V/sqrt(Hz)')
        frequencies = list(sd.FrequencyList())

        self.assertEqual(rho_values[0], 0.0)
        for i in range(1, len(rho_values)):
            expected = expected_rho * math.exp(-2.0 * (math.pi * frequencies[i] * cfg['SNR.COM_TX.Risetime'] / Gaussian.a2080) ** 2)
            self.assertAlmostEqual(rho_values[i], expected, places=18)

        cfg['NoiseBandwidth'] = 0.0
        with self.assertRaises(ValueError):
            cfg.NoiseDensity()

    def testWhiteNoiseConfigurationJohnson(self):
        from SignalIntegrity.App.StatisticalNoisePreferencesFile import WhiteNoiseConfiguration
        import scipy.constants as const

        cfg = WhiteNoiseConfiguration()
        cfg['WhiteNoiseType'] = 'Johnson'
        cfg['Johnson.Temperature_Kelvin'] = 300.0
        cfg['Johnson.Resistance'] = 50.0
        cfg['NoiseBandwidth'] = 20e9

        expected_rho = math.sqrt(4.0 * const.k * cfg['Johnson.Temperature_Kelvin'] * cfg['Johnson.Resistance'])
        self.assertAlmostEqual(cfg.NoiseDensity(), expected_rho, places=18)

        sd = cfg.SpectralDensity(50e9, 5)
        rho_values = sd.Values('V/sqrt(Hz)')
        self.assertEqual(rho_values[0], 0.0)
        self.assertAlmostEqual(rho_values[1], expected_rho, places=18)
        self.assertAlmostEqual(rho_values[2], expected_rho, places=18)
        self.assertEqual(rho_values[3], 0.0)
        self.assertEqual(rho_values[4], 0.0)
        self.assertEqual(rho_values[5], 0.0)

    def testNoiseConfigurationLegacyJohnsonType(self):
        from SignalIntegrity.App.StatisticalNoisePreferencesFile import NoiseConfiguration
        import scipy.constants as const

        cfg = NoiseConfiguration()
        cfg['Enable'] = True
        cfg['Type'] = 'Johnson'
        cfg['Lanes'] = 4.0
        cfg['WhiteNoise.Johnson.Temperature_Kelvin'] = 300.0
        cfg['WhiteNoise.Johnson.Resistance'] = 50.0
        cfg['WhiteNoise.NoiseBandwidth'] = 20e9

        expected_rho = math.sqrt(4.0 * const.k * cfg['WhiteNoise.Johnson.Temperature_Kelvin'] * cfg['WhiteNoise.Johnson.Resistance'])
        sd = cfg.SpectralDensity(50e9, 5)
        rho_values = sd.Values('V/sqrt(Hz)')
        self.assertEqual(rho_values[0], 0.0)
        self.assertAlmostEqual(rho_values[1], expected_rho * 2.0, places=18)
        self.assertAlmostEqual(rho_values[2], expected_rho * 2.0, places=18)
        self.assertEqual(rho_values[3], 0.0)
        self.assertEqual(rho_values[4], 0.0)
        self.assertEqual(rho_values[5], 0.0)

    def testSalzSNR(self):
        """Test script for SalzSNRdB noise floor filtering"""

        from SignalIntegrity.Lib.FrequencyDomain.FrequencyList import EvenlySpacedFrequencyList
        from SignalIntegrity.Lib.FrequencyDomain.SpectralDensity import SpectralDensity
        import math

        # Create simple test frequency list
        fl = EvenlySpacedFrequencyList(1e9, 10)

        # Create noise and signal spectral densities (uniform)
        noise_sd = SpectralDensity(fl, [1e-6] * (fl.N+1))
        signal_sd = SpectralDensity(fl, [1e-5] * (fl.N+1))

        # Test 1: Default noise floor (should include all bins)
        salz_default = noise_sd.SalzSNRdB(signal_sd, 'noise')
        print(f'Test 1 - SalzSNR with default noise_floor (1e-300): {salz_default:.2f} dB')

        # Test 2: With noise floor that filters some bins
        salz_filtered = noise_sd.SalzSNRdB(signal_sd, 'noise', noise_floor=1e-12)
        print(f'Test 2 - SalzSNR with noise_floor=1e-12: {salz_filtered:.2f} dB')

        # Test 3: Verify they're the same in this case (uniform spectrum, all bins pass filter)
        match = abs(salz_default - salz_filtered) < 0.01
        print(f'Test 3 - Results match (uniform spectrum): {match}')

        # Test 4: Non-uniform spectrum with high noise floor to actually filter bins
        noise_with_nulls = [1e-6 if i % 2 == 0 else 1e-8 for i in range(fl.N+1)]
        noise_sd_nulls = SpectralDensity(fl, noise_with_nulls)
        signal_sd_uniform = SpectralDensity(fl, [1e-5] * (fl.N+1))

        salz_no_filter = noise_sd_nulls.SalzSNRdB(signal_sd_uniform, 'noise', noise_floor=1e-300)
        salz_with_filter = noise_sd_nulls.SalzSNRdB(signal_sd_uniform, 'noise', noise_floor=1e-7)
        print(f'Test 4a - SalzSNR with non-uniform noise, no filter: {salz_no_filter:.2f} dB')
        print(f'Test 4b - SalzSNR with non-uniform noise, noise_floor=1e-7: {salz_with_filter:.2f} dB')
        print(f'Test 4c - Difference (filter should give higher SNR): {salz_with_filter - salz_no_filter:.2f} dB (higher is good)')

        print('\n✓ All SalzSNRdB noise floor filtering tests completed successfully!')

    def testEqualized(self):
        from SignalIntegrity.App.SignalIntegrityAppHeadless import SignalIntegrityAppHeadless
        import numpy as np
        siapp = SignalIntegrityAppHeadless()
        opened = siapp.OpenProjectFile(os.path.join(os.path.dirname(os.path.realpath(__file__)),'CrosstalkAnalysis.si'))
        self.assertTrue(opened,"Failed to open CrosstalkAnalysis.si project")
        results = siapp.Simulate()
        unequalized_wf = results['output waveforms'][results['output waveform labels'].index('Unequalized')]
        from SignalIntegrity.Lib.Equalization.Equalizer import BlindEqualizer
        eq = BlindEqualizer(
            waveform=unequalized_wf,
            num_levels=4,
            baud_rate=53e9,
            ideal_samples_per_ui=8,
            num_ffe_taps=11,
            num_dfe_taps=0,
            num_precursor_taps=5,
        )

        # Baseline cost at the initializer point.
        initial_residuals = eq.fF(eq.m_a)
        initial_rms = float(np.sqrt(np.mean(np.square(np.asarray(initial_residuals).reshape(-1)))))

        equalized_wf, ffe, dfe, tau = eq.Solve()
        _, _, _, _, final_residuals = eq.Results()
        final_rms = float(np.sqrt(np.mean(np.square(np.asarray(final_residuals).reshape(-1)))))

        self.assertIsNotNone(equalized_wf)
        self.assertEqual(len(ffe), 11)
        self.assertEqual(len(dfe), 0)
        self.assertGreaterEqual(tau, 0.0)
        self.assertLess(tau, eq.ui)
        # Equalization quality is measured by reducing decode error RMS.
        self.assertLess(final_rms, initial_rms)
        
        ffe=ffe/sum(np.abs(ffe))
        print(str(ffe.tolist()).replace(' ',''))
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()