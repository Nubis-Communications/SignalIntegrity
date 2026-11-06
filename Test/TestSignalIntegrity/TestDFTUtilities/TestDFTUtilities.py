"""
TestDFTUtilites.py
"""
# Copyright (c) 2018-2020 Teledyne LeCroy, Inc.
# Copyright (c) 2021-2025 Nubis Communications, Inc.
# Copyright (c) 2026 Ciena, Inc.
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
from SignalIntegrity.App import SignalIntegrityAppHeadless
from SignalIntegrity.App import TpX
from SignalIntegrity.App import TikZ
import SignalIntegrity.Lib as si
from numpy import fft
import numpy as np
import math
import os

class TestDFTUtilitiesTest(unittest.TestCase,si.test.SParameterCompareHelper,si.test.SignalIntegrityAppTestHelper):
    relearn=True
    debug=False
    checkPictures=True
    def __init__(self, methodName='runTest'):
        si.test.SignalIntegrityAppTestHelper.__init__(self,os.path.dirname(os.path.realpath(__file__)))
        si.test.SParameterCompareHelper.__init__(self)
        unittest.TestCase.__init__(self,methodName)
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.cwd=os.getcwd()
        os.chdir(self.path)
        from SignalIntegrity.App.SignalIntegrityAppHeadless import SignalIntegrityAppHeadless
        import SignalIntegrity.App.Project
        pysi=SignalIntegrityAppHeadless()
        self.UseSinX=SignalIntegrity.App.Preferences['Calculation.UseSinX']
        SignalIntegrity.App.Preferences['Calculation.UseSinX']=True
        self.Caching=SignalIntegrity.App.Preferences['Cache.CacheResults']
        SignalIntegrity.App.Preferences['Cache.CacheResults']=False
        self.TextLimit=SignalIntegrity.App.Preferences['Appearance.LimitText']
        SignalIntegrity.App.Preferences['Appearance.LimitText']=60
        self.RoundDisplayedValues=SignalIntegrity.App.Preferences['Appearance.RoundDisplayedValues']
        SignalIntegrity.App.Preferences['Appearance.RoundDisplayedValues']=4
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
        SignalIntegrity.App.Preferences['Cache.CacheResults']=self.Caching
        SignalIntegrity.App.Preferences['Appearance.LimitText']=self.TextLimit
        SignalIntegrity.App.Preferences['Appearance.RoundDisplayedValues']=self.RoundDisplayedValues
        SignalIntegrity.App.Preferences.SaveToFile()
        pysi=SignalIntegrityAppHeadless()
        SignalIntegrity.App.Preferences['Calculation'].ApplyPreferences()
    def testSpectralDensityToRMSAndBackKeven(self):
        rho0 = si.ToSI.FromSI('5 mV','V')/si.ToSI.FromSI('100 GHz','Hz')**0.5 # spectral density for noise in 100 GHZ bandwidth with 5 mV RMS noise
        N = 50
        Fe = 100e9
        f = [n/N*Fe for n in range(N+1)]
        rho = [rho0 for n in range(N+1)]
        delta_f = Fe/N
        rms = si.fd.DFTUtilities.rho_to_rms(rho, delta_f, Keven = True)
        rho2 = si.fd.DFTUtilities.rms_to_rho(rms, delta_f, Keven = True)
        for r, r2 in zip(rho, rho2):
            self.assertAlmostEqual(r, r2, places=20)
    def testSpectralDensityAddsUpToRightRMSNoiseInFDKeven(self):
        rho0 = si.ToSI.FromSI('5 mV','V')/si.ToSI.FromSI('100 GHz','Hz')**0.5 # spectral density for noise in 100 GHZ bandwidth with 5 mV RMS noise
        N = 50
        Fe = 100e9
        f = [n/N*Fe for n in range(N+1)]
        rho = [rho0 for n in range(N+1)]
        delta_f = Fe/N
        rms = si.fd.DFTUtilities.rho_to_rms(rho, delta_f, Keven = True)
        rms0 = si.fd.DFTUtilities.TotalSpectralContentRMS(rms)
        self.assertEqual(si.ToSI.ToSI(rms0,'V'),'5.0 mV') # should amount to 5 mV RMS noise when integrated over spectrum
    def testSpectralDensityAddsUpToRightdBmNoiseInFDKeven(self):
        rho0 = si.ToSI.FromSI('5 mV','V')/si.ToSI.FromSI('100 GHz','Hz')**0.5 # spectral density for noise in 100 GHZ bandwidth with 5 mV RMS noise
        N = 50
        Fe = 100e9
        f = [n/N*Fe for n in range(N+1)]
        rho = [rho0 for n in range(N+1)]
        delta_f = Fe/N
        rms = si.fd.DFTUtilities.rho_to_rms(rho, delta_f, Keven = True)
        dBm = si.fd.DFTUtilities.rms_to_dBm(rms)
        dBm0 = si.fd.DFTUtilities.TotalSpectralContentdBm(dBm)
        dBm_calc = 10*np.log10(si.ToSI.FromSI('5 mV','V')**2/si.ToSI.FromSI('50 ohm','ohm')/si.ToSI.FromSI('1 mW','W')) # power in watts of 5 mV RMS noise across 50 ohms, converted to mW
        self.assertEqual(si.ToSI.ToSI(dBm0,'dBm'),si.ToSI.ToSI(dBm_calc,'dBm')) # should amount to 5 mV RMS noise when integrated over spectrum
    def testSpectralDensityAddsUpToRightRMSNoiseInTDKeven(self):
        rho0 = si.ToSI.FromSI('5 mV','V')/si.ToSI.FromSI('100 GHz','Hz')**0.5 # spectral density for noise in 100 GHZ bandwidth with 5 mV RMS noise
        N = 50
        Fe = 100e9
        f = [n/N*Fe for n in range(N+1)]
        rho = [rho0 for n in range(N+1)]
        delta_f = Fe/N
        rms = si.fd.DFTUtilities.rho_to_rms(rho, delta_f, Keven = True)
        A = si.fd.DFTUtilities.rms_to_A(rms, Keven = True)
        XH = si.fd.DFTUtilities.A_to_X(A, Keven = True, random_phase = True)
        X = si.fd.DFTUtilities.Half_to_Full(XH, Keven = True)
        x = fft.ifft(X).real
        K=si.fd.DFTUtilities.K(N, Keven = True)
        rms0 = si.fd.DFTUtilities.TotalSpectralContentRMS(rms)
        self.assertEqual(si.ToSI.ToSI(rms0,'V'),'5.0 mV') # should amount to 5 mV RMS noise in time domain
    def testSpectralDensitytoTDAndBackAgainKeven(self):
        rho0 = si.ToSI.FromSI('5 mV','V')/si.ToSI.FromSI('100 GHz','Hz')**0.5 # spectral density for noise in 100 GHZ bandwidth with 5 mV RMS noise
        N = 50
        K=si.fd.DFTUtilities.K(N, Keven = True)
        Keven = si.fd.DFTUtilities.Keven(K)
        self.assertTrue(Keven, 'K is even')
        N2 = si.fd.DFTUtilities.N(K)
        self.assertEqual(N, N2, 'N and K consistent')
        Fe = 100e9
        f = [n/N*Fe for n in range(N+1)]
        rho = [rho0 for n in range(N+1)]
        delta_f = Fe/N
        rms = si.fd.DFTUtilities.rho_to_rms(rho, delta_f, Keven = True)
        A = si.fd.DFTUtilities.rms_to_A(rms, Keven = True)
        XH = si.fd.DFTUtilities.A_to_X(A, Keven = True, random_phase = True)
        X = si.fd.DFTUtilities.Half_to_Full(XH, Keven = True)
        x = fft.ifft(X).real
        K=si.fd.DFTUtilities.K(N, Keven = True)
        # rms0 = (sum([v**2 for v in x])/K)**0.5
        # self.assertEqual(si.ToSI.ToSI(rms0,'V'),'5.0 mV') # should amount to 5 mV RMS noise in time domain
        X2 = fft.fft(x)
        X2H = si.fd.DFTUtilities.Full_to_Half(X2)
        A2 = si.fd.DFTUtilities.X_to_A(X2H, Keven = True)
        rms2 = si.fd.DFTUtilities.A_to_rms(A2, Keven = True)
        rho2 = si.fd.DFTUtilities.rms_to_rho(rms2, delta_f, Keven = True)
        self.assertEqual(len(rho), len(rho2))
        for r, r2 in zip(rho, rho2):
            self.assertAlmostEqual(r, r2, places=20)
    def testSpectralDensityToRMSAndBackKodd(self):
        rho0 = si.ToSI.FromSI('5 mV','V')/si.ToSI.FromSI('100 GHz','Hz')**0.5 # spectral density for noise in 100 GHZ bandwidth with 5 mV RMS noise
        N = 50
        Fe = 100e9
        f = [n/N*Fe for n in range(N+1)]
        rho = [rho0 for n in range(N+1)]
        delta_f = Fe/N
        rms = si.fd.DFTUtilities.rho_to_rms(rho, delta_f, Keven = False)
        rho2 = si.fd.DFTUtilities.rms_to_rho(rms, delta_f, Keven = False)
        for r, r2 in zip(rho, rho2):
            self.assertAlmostEqual(r, r2, places=20)
    def testSpectralDensityAddsUpToRightRMSNoiseInFDKodd(self):
        rho0 = si.ToSI.FromSI('5 mV','V')/si.ToSI.FromSI('100 GHz','Hz')**0.5 # spectral density for noise in 100 GHZ bandwidth with 5 mV RMS noise
        N = 50
        Fe = 100e9
        f = [n/N*Fe for n in range(N+1)]
        rho = [rho0 for n in range(N+1)]
        delta_f = Fe/N
        rms = si.fd.DFTUtilities.rho_to_rms(rho, delta_f, Keven = False)
        rms0 = si.fd.DFTUtilities.TotalSpectralContentRMS(rms)
        self.assertEqual(si.ToSI.ToSI(rms0,'V'),'5.0 mV') # should amount to 5 mV RMS noise when integrated over spectru
    def testSpectralDensityAddsUpToRightdBmNoiseInFDKodd(self):
        rho0 = si.ToSI.FromSI('5 mV','V')/si.ToSI.FromSI('100 GHz','Hz')**0.5 # spectral density for noise in 100 GHZ bandwidth with 5 mV RMS noise
        N = 50
        Fe = 100e9
        f = [n/N*Fe for n in range(N+1)]
        rho = [rho0 for n in range(N+1)]
        delta_f = Fe/N
        rms = si.fd.DFTUtilities.rho_to_rms(rho, delta_f, Keven = False)
        dBm = si.fd.DFTUtilities.rms_to_dBm(rms)
        dBm0 = si.fd.DFTUtilities.TotalSpectralContentdBm(dBm)
        dBm_calc = 10*np.log10(si.ToSI.FromSI('5 mV','V')**2/si.ToSI.FromSI('50 ohm','ohm')/si.ToSI.FromSI('1 mW','W')) # power in watts of 5 mV RMS noise across 50 ohms, converted to mW
        self.assertEqual(si.ToSI.ToSI(dBm0,'dBm'),si.ToSI.ToSI(dBm_calc,'dBm')) # should amount to 5 mV RMS noise when integrated over spectrum
    def testSpectralDensityAddsUpToRightRMSNoiseInTDKodd(self):
        rho0 = si.ToSI.FromSI('5 mV','V')/si.ToSI.FromSI('100 GHz','Hz')**0.5 # spectral density for noise in 100 GHZ bandwidth with 5 mV RMS noise
        N = 50
        Fe = 100e9
        f = [n/N*Fe for n in range(N+1)]
        rho = [rho0 for n in range(N+1)]
        delta_f = Fe/N
        rms = si.fd.DFTUtilities.rho_to_rms(rho, delta_f, Keven = False)
        A = si.fd.DFTUtilities.rms_to_A(rms, Keven = False)
        XH = si.fd.DFTUtilities.A_to_X(A, Keven = False, random_phase = True)
        X = si.fd.DFTUtilities.Half_to_Full(XH, Keven = False)
        x = fft.ifft(X).real
        K=si.fd.DFTUtilities.K(N, Keven = False)
        rms0 = si.fd.DFTUtilities.TotalSpectralContentRMS(rms)
        self.assertEqual(si.ToSI.ToSI(rms0,'V'),'5.0 mV') # should amount to 5 mV RMS noise in time domain
    def testSpectralDensitytoTDAndBackAgainKodd(self):
        rho0 = si.ToSI.FromSI('5 mV','V')/si.ToSI.FromSI('100 GHz','Hz')**0.5 # spectral density for noise in 100 GHZ bandwidth with 5 mV RMS noise
        N = 50
        K=si.fd.DFTUtilities.K(N, Keven = False)
        Keven = si.fd.DFTUtilities.Keven(K)
        self.assertFalse(Keven, 'K is odd')
        N2 = si.fd.DFTUtilities.N(K)
        self.assertEqual(N, N2, 'N and K consistent')
        Fe_nominal = 100e9
        Fs = 2*Fe_nominal
        Fe = si.fd.DFTUtilities.EndFrequency(K, Fs)
        Fs2 = si.fd.DFTUtilities.SampleRate(K, Fe)
        self.assertEqual(Fs, Fs2, 'sample rate correct')
        f = [si.fd.DFTUtilities.Frequency(n,K,Fs) for n in range(N+1)]
        rho = [rho0 for n in range(N+1)]
        delta_f = si.fd.DFTUtilities.DeltaFrequency(K, Fs)
        rms = si.fd.DFTUtilities.rho_to_rms(rho, delta_f, Keven = False)
        A = si.fd.DFTUtilities.rms_to_A(rms, Keven = False)
        XH = si.fd.DFTUtilities.A_to_X(A, Keven = False, random_phase = True)
        X = si.fd.DFTUtilities.Half_to_Full(XH, Keven = False)
        x = fft.ifft(X).real
        
        # rms0 = (sum([v**2 for v in x])/K)**0.5
        # self.assertEqual(si.ToSI.ToSI(rms0,'V'),'5.0 mV') # should amount to 5 mV RMS noise in time domain
        X2 = fft.fft(x).tolist()
        X2H = si.fd.DFTUtilities.Full_to_Half(X2)
        A2 = si.fd.DFTUtilities.X_to_A(X2H, Keven = False)
        rms2 = si.fd.DFTUtilities.A_to_rms(A2, Keven = False)
        rho2 = si.fd.DFTUtilities.rms_to_rho(rms2, delta_f, Keven = False)
        self.assertEqual(len(rho), len(rho2))
        for r, r2 in zip(rho, rho2):
            self.assertAlmostEqual(r, r2, places=20)
    def testSineWaveContent0Keven(self):
        N = 3
        K = si.fd.DFTUtilities.K(N, Keven = True)
        Fe = 100e9
        Fs = si.fd.DFTUtilities.SampleRate(K, Fe)
        f = [si.fd.DFTUtilities.Frequency(n,K,Fs) for n in range(N+1)]
        n0 = 0
        x = [np.cos(2*np.pi*k*f[n0]/Fs) for k in range(K)]
        X = fft.fft(x).tolist()
        XH = si.fd.DFTUtilities.Full_to_Half(X)
        A = si.fd.DFTUtilities.X_to_A(XH, Keven = True)
        rms = si.fd.DFTUtilities.A_to_rms(A, Keven = True)
        self.assertEqual(si.ToSI.ToSI(rms[n0],'V',round=3),'1.0 V')
    def testSineWaveContent1Keven(self):
        N = 3
        K = si.fd.DFTUtilities.K(N, Keven = True)
        Fe = 100e9
        Fs = si.fd.DFTUtilities.SampleRate(K, Fe)
        f = [si.fd.DFTUtilities.Frequency(n,K,Fs) for n in range(N+1)]
        n0 = 1
        x = [np.cos(2*np.pi*k*f[n0]/Fs) for k in range(K)]
        X = fft.fft(x).tolist()
        XH = si.fd.DFTUtilities.Full_to_Half(X)
        A = si.fd.DFTUtilities.X_to_A(XH, Keven = True)
        rms = si.fd.DFTUtilities.A_to_rms(A, Keven = True)
        self.assertEqual(si.ToSI.ToSI(rms[n0],'V',round=3),'707.0 mV')
    def testSineWaveContent2Keven(self):
        N = 3
        K = si.fd.DFTUtilities.K(N, Keven = True)
        Fe = 100e9
        Fs = si.fd.DFTUtilities.SampleRate(K, Fe)
        f = [si.fd.DFTUtilities.Frequency(n,K,Fs) for n in range(N+1)]
        n0 = 2
        x = [np.cos(2*np.pi*k*f[n0]/Fs) for k in range(K)]
        X = fft.fft(x).tolist()
        XH = si.fd.DFTUtilities.Full_to_Half(X)
        A = si.fd.DFTUtilities.X_to_A(XH, Keven = True)
        rms = si.fd.DFTUtilities.A_to_rms(A, Keven = True)
        self.assertEqual(si.ToSI.ToSI(rms[n0],'V',round=3),'707.0 mV')
    def testSineWaveContent3Keven(self):
        N = 3
        K = si.fd.DFTUtilities.K(N, Keven = True)
        Fe = 100e9
        Fs = si.fd.DFTUtilities.SampleRate(K, Fe)
        f = [si.fd.DFTUtilities.Frequency(n,K,Fs) for n in range(N+1)]
        n0 = 3
        x = [np.cos(2*np.pi*k*f[n0]/Fs) for k in range(K)]
        X = fft.fft(x).tolist()
        XH = si.fd.DFTUtilities.Full_to_Half(X)
        A = si.fd.DFTUtilities.X_to_A(XH, Keven = True)
        rms = si.fd.DFTUtilities.A_to_rms(A, Keven = True)
        self.assertEqual(si.ToSI.ToSI(rms[n0],'V',round=3),'1.0 V')
    def testSineWaveContent0Kodd(self):
        N = 3
        K = si.fd.DFTUtilities.K(N, Keven = False)
        Fe = 100e9
        Fs = si.fd.DFTUtilities.SampleRate(K, Fe)
        f = [si.fd.DFTUtilities.Frequency(n,K,Fs) for n in range(N+1)]
        n0 = 0
        x = [np.cos(2*np.pi*k*f[n0]/Fs) for k in range(K)]
        X = fft.fft(x).tolist()
        XH = si.fd.DFTUtilities.Full_to_Half(X)
        A = si.fd.DFTUtilities.X_to_A(XH, Keven = False)
        rms = si.fd.DFTUtilities.A_to_rms(A, Keven = False)
        self.assertEqual(si.ToSI.ToSI(rms[n0],'V',round=3),'1.0 V')
    def testSineWaveContent1Kodd(self):
        N = 3
        K = si.fd.DFTUtilities.K(N, Keven = False)
        Fe = 100e9
        Fs = si.fd.DFTUtilities.SampleRate(K, Fe)
        f = [si.fd.DFTUtilities.Frequency(n,K,Fs) for n in range(N+1)]
        n0 = 1
        x = [np.cos(2*np.pi*k*f[n0]/Fs) for k in range(K)]
        X = fft.fft(x).tolist()
        XH = si.fd.DFTUtilities.Full_to_Half(X)
        A = si.fd.DFTUtilities.X_to_A(XH, Keven = False)
        rms = si.fd.DFTUtilities.A_to_rms(A, Keven = False)
        self.assertEqual(si.ToSI.ToSI(rms[n0],'V',round=3),'707.0 mV')
    def testSineWaveContent2Kodd(self):
        N = 3
        K = si.fd.DFTUtilities.K(N, Keven = False)
        Fe = 100e9
        Fs = si.fd.DFTUtilities.SampleRate(K, Fe)
        f = [si.fd.DFTUtilities.Frequency(n,K,Fs) for n in range(N+1)]
        n0 = 2
        x = [np.cos(2*np.pi*k*f[n0]/Fs) for k in range(K)]
        X = fft.fft(x).tolist()
        XH = si.fd.DFTUtilities.Full_to_Half(X)
        A = si.fd.DFTUtilities.X_to_A(XH, Keven = False)
        rms = si.fd.DFTUtilities.A_to_rms(A, Keven = False)
        self.assertEqual(si.ToSI.ToSI(rms[n0],'V',round=3),'707.0 mV')
    def testSineWaveContent3Kodd(self):
        N = 3
        K = si.fd.DFTUtilities.K(N, Keven = False)
        Fe = 100e9
        Fs = si.fd.DFTUtilities.SampleRate(K, Fe)
        f = [si.fd.DFTUtilities.Frequency(n,K,Fs) for n in range(N+1)]
        n0 = 3
        x = [np.cos(2*np.pi*k*f[n0]/Fs) for k in range(K)]
        X = fft.fft(x).tolist()
        XH = si.fd.DFTUtilities.Full_to_Half(X)
        A = si.fd.DFTUtilities.X_to_A(XH, Keven = False)
        rms = si.fd.DFTUtilities.A_to_rms(A, Keven = False)
        self.assertEqual(si.ToSI.ToSI(rms[n0],'V',round=3),'707.0 mV')


    # -- ConvertSpectralDensity ------------------------------------------------

    def testConvertSpectralDensityIdentityDBmHz(self):
        """Same-unit conversion returns the input unchanged."""
        self.assertEqual(
            si.fd.DFTUtilities.ConvertSpectralDensity(-100.0, 'dBm/Hz', 'dBm/Hz'),
            -100.0)

    def testConvertSpectralDensityIdentityVPerSqrtHz(self):
        """Same-unit conversion returns the input unchanged."""
        self.assertEqual(
            si.fd.DFTUtilities.ConvertSpectralDensity(1e-9, 'V/sqrt(Hz)', 'V/sqrt(Hz)'),
            1e-9)

    def testConvertSpectralDensityIdentityVrmsNoBwRequired(self):
        """Vrms -> Vrms short-circuits before the bw check, so bw is not needed."""
        self.assertEqual(
            si.fd.DFTUtilities.ConvertSpectralDensity(5e-3, 'Vrms', 'Vrms'),
            5e-3)

    def testConvertSpectralDensityVPerSqrtHzToDBmHz(self):
        """1 V/sqrt(Hz) into 50 ohm / 1 mW is 10*log10(20) dBm/Hz."""
        expected = 10. * math.log10(1.0 / 50.0 / 1e-3)
        self.assertAlmostEqual(
            si.fd.DFTUtilities.ConvertSpectralDensity(1.0, 'V/sqrt(Hz)', 'dBm/Hz'),
            expected, places=12)

    def testConvertSpectralDensityDBmHzToVPerSqrtHz(self):
        """0 dBm/Hz in 50 ohm corresponds to sqrt(50 mW) V/sqrt(Hz)."""
        expected = math.sqrt(50. * 1e-3)
        self.assertAlmostEqual(
            si.fd.DFTUtilities.ConvertSpectralDensity(0.0, 'dBm/Hz', 'V/sqrt(Hz)'),
            expected, places=12)

    def testConvertSpectralDensityVPerSqrtHzToVrms(self):
        """5 mV / sqrt(100 GHz) integrated over 100 GHz is 5 mV rms."""
        bw = 100e9
        asd = 5e-3 / math.sqrt(bw)
        self.assertAlmostEqual(
            si.fd.DFTUtilities.ConvertSpectralDensity(asd, 'V/sqrt(Hz)', 'Vrms', bw=bw),
            5e-3, places=12)

    def testConvertSpectralDensityVrmsToVPerSqrtHz(self):
        """5 mV rms over 100 GHz gives 5 mV / sqrt(100 GHz) V/sqrt(Hz)."""
        bw = 100e9
        expected = 5e-3 / math.sqrt(bw)
        self.assertAlmostEqual(
            si.fd.DFTUtilities.ConvertSpectralDensity(5e-3, 'Vrms', 'V/sqrt(Hz)', bw=bw),
            expected, places=20)

    def testConvertSpectralDensityVrmsToDBmHz(self):
        """Vrms -> dBm/Hz matches the analytical ASD^2 / (R * Pref) per Hz."""
        bw = 100e9
        rms = 5e-3
        expected = 10. * math.log10(rms * rms / 50. / 1e-3 / bw)
        self.assertAlmostEqual(
            si.fd.DFTUtilities.ConvertSpectralDensity(rms, 'Vrms', 'dBm/Hz', bw=bw),
            expected, places=10)

    def testConvertSpectralDensityDBmHzToVrms(self):
        """dBm/Hz -> Vrms inverts Vrms -> dBm/Hz at the same bandwidth."""
        bw = 100e9
        rms = 5e-3
        dbm = si.fd.DFTUtilities.ConvertSpectralDensity(rms, 'Vrms', 'dBm/Hz', bw=bw)
        self.assertAlmostEqual(
            si.fd.DFTUtilities.ConvertSpectralDensity(dbm, 'dBm/Hz', 'Vrms', bw=bw),
            rms, places=12)

    def testConvertSpectralDensityRoundtripVPerSqrtHzDBmHz(self):
        """V/sqrt(Hz) -> dBm/Hz -> V/sqrt(Hz) returns the original value."""
        asd = 1e-9
        dbm = si.fd.DFTUtilities.ConvertSpectralDensity(asd, 'V/sqrt(Hz)', 'dBm/Hz')
        asd2 = si.fd.DFTUtilities.ConvertSpectralDensity(dbm, 'dBm/Hz', 'V/sqrt(Hz)')
        self.assertAlmostEqual(asd, asd2, places=20)

    def testConvertSpectralDensityRoundtripVrmsVPerSqrtHz(self):
        """Vrms -> V/sqrt(Hz) -> Vrms returns the original value."""
        bw = 100e9
        rms = 5e-3
        asd = si.fd.DFTUtilities.ConvertSpectralDensity(rms, 'Vrms', 'V/sqrt(Hz)', bw=bw)
        rms2 = si.fd.DFTUtilities.ConvertSpectralDensity(asd, 'V/sqrt(Hz)', 'Vrms', bw=bw)
        self.assertAlmostEqual(rms, rms2, places=15)

    def testConvertSpectralDensityRoundtripVrmsDBmHz(self):
        """Vrms -> dBm/Hz -> Vrms returns the original value."""
        bw = 100e9
        rms = 5e-3
        dbm = si.fd.DFTUtilities.ConvertSpectralDensity(rms, 'Vrms', 'dBm/Hz', bw=bw)
        rms2 = si.fd.DFTUtilities.ConvertSpectralDensity(dbm, 'dBm/Hz', 'Vrms', bw=bw)
        self.assertAlmostEqual(rms, rms2, places=12)

    def testConvertSpectralDensityKnownDBmHzAtFiveMilliVoltOver100GHz(self):
        """5 mV rms over 100 GHz in 50 ohm gives a known dBm/Hz value."""
        bw = 100e9
        rms = 5e-3
        expected = 10. * math.log10(rms * rms / 50. / 1e-3 / bw)  # ~ -143.01 dBm/Hz
        self.assertAlmostEqual(
            si.fd.DFTUtilities.ConvertSpectralDensity(rms, 'Vrms', 'dBm/Hz', bw=bw),
            expected, places=10)

    def testConvertSpectralDensityZeroAsdToDBmHzClampsTo3000(self):
        """Zero amplitude spectral density clamps the log to -3000 dBm/Hz."""
        self.assertEqual(
            si.fd.DFTUtilities.ConvertSpectralDensity(0.0, 'V/sqrt(Hz)', 'dBm/Hz'),
            -3000.0)

    def testConvertSpectralDensityZeroVrmsToDBmHzClampsTo3000(self):
        """Zero Vrms (which yields zero ASD) also clamps to -3000 dBm/Hz."""
        self.assertEqual(
            si.fd.DFTUtilities.ConvertSpectralDensity(0.0, 'Vrms', 'dBm/Hz', bw=100e9),
            -3000.0)

    def testConvertSpectralDensityUnknownFromUnitsRaises(self):
        """An unknown source unit raises ValueError."""
        with self.assertRaises(ValueError):
            si.fd.DFTUtilities.ConvertSpectralDensity(1.0, 'XYZ', 'dBm/Hz')

    def testConvertSpectralDensityUnknownToUnitsRaises(self):
        """An unknown target unit raises ValueError."""
        with self.assertRaises(ValueError):
            si.fd.DFTUtilities.ConvertSpectralDensity(1.0, 'dBm/Hz', 'XYZ')

    def testConvertSpectralDensityVrmsFromWithoutBwRaises(self):
        """Converting from Vrms without bw raises ValueError."""
        with self.assertRaises(ValueError):
            si.fd.DFTUtilities.ConvertSpectralDensity(5e-3, 'Vrms', 'V/sqrt(Hz)')

    def testConvertSpectralDensityVrmsToWithoutBwRaises(self):
        """Converting to Vrms without bw raises ValueError."""
        with self.assertRaises(ValueError):
            si.fd.DFTUtilities.ConvertSpectralDensity(1e-9, 'V/sqrt(Hz)', 'Vrms')


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()