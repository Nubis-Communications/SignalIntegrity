"""
SpectralDensity.py
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

import math
import csv
import json
import sys
import os
import numpy as np
from numpy import fft

from SignalIntegrity.Lib.FrequencyDomain.FrequencyDomain import FrequencyDomain
from SignalIntegrity.Lib.FrequencyDomain.DFTUtilities import DFTUtilities
from SignalIntegrity.Lib.FrequencyDomain.FrequencyList import FrequencyList

class SpectralDensity(FrequencyDomain):
    """SpectralDensity
    Spectral density view of frequency-domain content.

    Stores per-bin amplitude spectral density values (V/sqrt(Hz)) across an
    instance of class FrequencyList.  This class is the spectral-density
    counterpart of FrequencyResponse and FrequencyContent: it represents the
    noise (or signal) spectral density distribution, and provides conversions
    to other common units (dBm/Hz, per-bin rms, per-bin dBm) as well as
    integrated quantities (total rms, total dBm), random time-domain noise
    realization, resampling onto a different FrequencyList, and a WhiteNoise()
    factory.
    @see FrequencyResponse
    @see FrequencyContent
    @see DFTUtilities
    """
    R=50.0
    P=1e-3
    LogRP10=10.*math.log10(R*P)
    def __init__(self,f=None,density=None,Keven=True):
        """Constructor
        @param f (optional) instance of class FrequencyList
        @param density (optional) list of float spectral density values in V/sqrt(Hz)
        @param Keven (optional) bool whether the corresponding time-record length K
        is even (K=2*N) or odd (K=2*N+1).  Defaults to True.
        """
        FrequencyDomain.__init__(self,f,density)
        self.Keven=Keven
    def Density(self,unit=None):
        """Density
        @param unit string defining the desired units for the spectral density.
        @return list of spectral density values in the unit specified.
        @see Values() for valid units.
        """
        return self.Values(unit)
    def ReadFromFile(self,fileName):
        """reads a spectral density from a file
        @param fileName string file name to read
        @return self
        @remark
        Supported extensions:
        - '.csv' via ReadFromCSV()
        - '.json' via ReadFromJson()
        - '.txt' via FrequencyDomain.ReadFromFile()
        Other extensions fall back to FrequencyDomain.ReadFromFile().
        """
        _,file_extension=os.path.splitext(fileName)
        extension=file_extension.lower()
        if extension == '.csv':
            return self.ReadFromCSV(fileName)
        if extension == '.json':
            return self.ReadFromJson(fileName)
        return FrequencyDomain.ReadFromFile(self,fileName)
    def ReadFromCSV(self,fileName):
        """reads a spectral density from a CSV file
        @param fileName string name of file to read
        @return self
        @remark
        The CSV file is assumed to contain frequency in Hz in the first column
        and spectral density in V/sqrt(Hz) in the second column.  Any
        non-numeric lines before or within the data are skipped until valid
        comma-separated frequency,density pairs are found.
        """
        frequencies=[]
        density=[]
        with open(fileName,'rU' if sys.version_info.major < 3 else 'r') as f:
            for row in csv.reader(f):
                if len(row) < 2:
                    continue
                try:
                    frequency=float(row[0].strip())
                    value=float(row[1].strip())
                except (TypeError,ValueError):
                    continue
                if not math.isfinite(frequency) or not math.isfinite(value):
                    continue
                frequencies.append(frequency)
                density.append(value)
        if len(frequencies) == 0:
            raise ValueError('no spectral density data found in '+str(fileName))
        fd=FrequencyList(frequencies)
        fd.CheckEvenlySpaced()
        SpectralDensity.__init__(self,fd,density,getattr(self,'Keven',True))
        return self
    def ReadFromJson(self,fileName):
        """reads a spectral density from a JSON file
        @param fileName string name of file to read
        @return self
        @remark
        The JSON data must decode to a dictionary that contains a 'noise' (or,
        alternatively, 'wave') key at the root level.  That key holds a
        dictionary with the frequency in Hz and spectral density in V/sqrt(Hz),
        typically as arrays keyed by 'x' and 'y'.  Any other keys present at the
        root level are ignored, so additional metadata in the file is tolerated.
        """
        with open(fileName,'rU' if sys.version_info.major < 3 else 'r') as f:
            text=f.read()

        decoder=json.JSONDecoder()
        index=0
        while index < len(text) and text[index].isspace():
            index=index+1
        data,_=decoder.raw_decode(text,index)

        if not isinstance(data,dict):
            raise ValueError('spectral density json must decode to a dictionary')

        if 'noise' in data:
            section=data['noise']
        elif 'wave' in data:
            section=data['wave']
        else:
            raise ValueError(
                "spectral density json must contain a 'noise' or 'wave' key")

        if not isinstance(section,dict):
            raise ValueError(
                "spectral density json 'noise'/'wave' entry must be a dictionary")

        if 'x' in section and 'y' in section:
            frequencies=section['x']
            density=section['y']
        elif 'frequency' in section and 'density' in section:
            frequencies=section['frequency']
            density=section['density']
        elif 'frequencies' in section and 'densities' in section:
            frequencies=section['frequencies']
            density=section['densities']
        else:
            raise ValueError('spectral density json must contain x/y arrays')

        if len(frequencies) != len(density):
            raise ValueError('frequency and density arrays must be the same length')
        if len(frequencies) == 0:
            raise ValueError('no spectral density data found in '+str(fileName))

        parsed_frequencies=[]
        parsed_density=[]
        for frequency,value in zip(frequencies,density):
            f_hz=float(frequency)
            rho=float(value)
            if not math.isfinite(f_hz) or not math.isfinite(rho):
                raise ValueError('spectral density json contains non-finite values')
            parsed_frequencies.append(f_hz)
            parsed_density.append(rho)

        fd=FrequencyList(parsed_frequencies)
        fd.CheckEvenlySpaced()
        SpectralDensity.__init__(self,fd,parsed_density,getattr(self,'Keven',True))
        return self
    def WriteToCSV(self,fileName):
        """writes a spectral density to a CSV file
        @param fileName string name of file to write
        @return self
        @remark
        The CSV file contains frequency in Hz in the first column and spectral
        density in V/sqrt(Hz) in the second column.
        """
        with open(fileName,'w') as f:
            for frequency,value in zip(self.Frequencies(),self.Values('V/sqrt(Hz)')):
                f.write(str(frequency)+','+str(value)+'\n')
        return self
    def WriteToJson(self,fileName):
        """writes a spectral density to a JSON file
        @param fileName string name of file to write
        @return self
        @remark
        The JSON data contains a 'noise' key at the root whose value is a
        dictionary with frequency in Hz in 'x' and spectral density in
        V/sqrt(Hz) in 'y'.
        """
        with open(fileName,'w') as f:
            json.dump({'noise':{'x':self.Frequencies(),
                                'y':self.Values('V/sqrt(Hz)')}},f,indent=4,
                      default=lambda o: o.tolist() if hasattr(o,'tolist') else o)
        return self
    def WriteToFile(self,fileName):
        """writes a spectral density to a file
        @param fileName string file name to write
        @return self
        @remark
        Supported extensions:
        - '.csv' via WriteToCSV()
        - '.json' via WriteToJson()
        - '.txt' via FrequencyDomain.WriteToFile()
        Other extensions fall back to FrequencyDomain.WriteToFile().
        """
        _,file_extension=os.path.splitext(fileName)
        extension=file_extension.lower()
        if extension == '.csv':
            return self.WriteToCSV(fileName)
        if extension == '.json':
            return self.WriteToJson(fileName)
        return FrequencyDomain.WriteToFile(self,fileName)
    def Values(self,unit=None):
        """spectral density values
        @param unit (optional) string containing the unit for the values desired.
        @return list of float values in the unit specified.
        @remark
        Valid spectral-density units are:
        - 'V/sqrt(Hz)' - amplitude spectral density (default if no unit).
        - 'dBm/Hz' - power spectral density in dBm/Hz (50 ohm, 1 mW).

        If no unit is specified, the magnitudes of the spectral density values
        (V/sqrt(Hz)) are returned.

        If no spectral-density unit matches, the call defers to the
        FrequencyDomain base class for generic complex-value units such as
        'dB', 'mag', 'rad', 'deg', 'real', and 'imag'.
        @see FrequencyDomain
        """
        if unit is None or unit == 'V/sqrt(Hz)':
            return np.abs(self.values).tolist()
        elif unit in ['dBm/Hz','dBmPerHz']:
            r=np.abs(self.values)
            result=np.full(len(r),-3000.)
            mask=r>=1e-15
            result[mask]=20.*np.log10(r[mask])-self.LogRP10
            return result.tolist()
        else:
            return FrequencyDomain.Values(self,unit)
    def TotalRMS(self):
        """Total RMS across the spectrum
        @return float total rms = sqrt(sum(rms[n]^2)).
        """
        deltaf = DFTUtilities.DeltaFrequency((len(self)-1)*2, self.Frequencies()[-1]*2)
        return DFTUtilities.TotalSpectralContentRMS(
            DFTUtilities.rho_to_rms(
                self.Values(),
                deltaf))
    def TotaldBm(self,reference='voltage'):
        """Total power across the spectrum
        @param reference (optional) string either 'voltage' (default) or
        'current' selecting the power law used to convert the integrated rms
        to power.  For a voltage quantity P = rms^2 / R (R divides); for a
        current quantity P = rms^2 * R (R multiplies).
        @return float total power in dBm.
        @note
        The two references differ by exactly 20*log10(R) dB for the same
        numeric rms.
        """
        deltaf = DFTUtilities.DeltaFrequency((len(self)-1)*2, self.Frequencies()[-1]*2)
        rms = DFTUtilities.rho_to_rms(self.Values(), deltaf)
        if reference == 'current':
            # P = rms^2 * R  (current through the reference impedance)
            total_power = np.sum(np.square(np.asarray(rms))) * self.R
            return -3000. if total_power <= 1e-300 else 10.*math.log10(total_power/self.P)
        return DFTUtilities.TotalSpectralContentdBm(
            DFTUtilities.rms_to_dBm(rms))
    def SNRdB(self, other, other_is_signal_or_noise):
        """Calculates SNR in dB from integrated spectral-density powers.
        @param other instance of class SpectralDensity.
        @param other_is_signal_or_noise string either 'signal' or 'noise'.
        When set to 'signal', other is treated as signal and self as noise.
        When set to 'noise', other is treated as noise and self as signal.
        @return float SNR in dB computed as signal_dBm - noise_dBm.
        """
        if not isinstance(other, SpectralDensity):
            raise TypeError('other must be an instance of SpectralDensity')

        if other_is_signal_or_noise not in ['signal', 'noise']:
            raise ValueError("other_is_signal_or_noise must be 'signal' or 'noise'")

        if other_is_signal_or_noise == 'signal':
            signal_dbm = other.TotaldBm()
            noise_dbm = self.TotaldBm()
        else:
            signal_dbm = self.TotaldBm()
            noise_dbm = other.TotaldBm()

        return signal_dbm - noise_dbm
    def SalzSNRdB(self, other, other_is_signal_or_noise, noise_floor=1e-300):
        """Calculates Salz SNR in dB using bin-wise PSD ratios.
        @param other instance of class SpectralDensity.
        @param other_is_signal_or_noise string either 'signal' or 'noise'.
        When set to 'signal', other is treated as signal and self as noise.
        When set to 'noise', other is treated as noise and self as signal.
        @param noise_floor (optional) minimum linear noise PSD required for a
        bin to be included in the average. Defaults to 1e-300 (effectively no filtering).
        @return float Salz SNR in dB.
        @remark
        other is resampled to self's frequency list before the computation.
        The implemented definition is:
        SalzSNR = 10*log10(mean(PSD_signal[n]/PSD_noise[n]))
        where PSD = rho^2 and rho is in V/sqrt(Hz).
        Bins whose noise PSD is below noise_floor are excluded from the mean.
        """
        if not isinstance(other, SpectralDensity):
            raise TypeError('other must be an instance of SpectralDensity')

        if other_is_signal_or_noise not in ['signal', 'noise']:
            raise ValueError("other_is_signal_or_noise must be 'signal' or 'noise'")

        if noise_floor <= 0:
            raise ValueError('noise_floor must be positive')

        other_on_self = other.Resample(self.FrequencyList())

        if other_is_signal_or_noise == 'signal':
            signal_rho = other_on_self.Values('V/sqrt(Hz)')
            noise_rho = self.Values('V/sqrt(Hz)')
        else:
            signal_rho = self.Values('V/sqrt(Hz)')
            noise_rho = other_on_self.Values('V/sqrt(Hz)')

        # Compute PSD ratios, filtering by noise floor and excluding zero noise values
        signal=np.asarray(signal_rho)
        noise=np.asarray(noise_rho)
        n_psd=noise*noise
        mask=(n_psd>=noise_floor)&(n_psd>0)
        psd_ratios=(signal[mask]*signal[mask])/n_psd[mask]

        if len(psd_ratios) == 0:
            # If no bins pass the noise floor filter, try without floor (excluding only zero noise).
            # This handles cases where noise spectral density is extremely small
            # (near machine epsilon) across the entire spectrum.
            mask=n_psd>0
            psd_ratios=(signal[mask]*signal[mask])/n_psd[mask]

        if len(psd_ratios) == 0:
            # If still no valid ratios, all noise is zero or undefined.
            # This represents infinite SNR, represented as very large dB value.
            return 3000.0  # Represent infinite SNR as very large positive dB

        salz_linear = np.sum(psd_ratios) / float(len(psd_ratios))

        return -3000. if salz_linear < 1e-300 else 10.*math.log10(salz_linear)
    def NoiseWaveform(self,td=None):
        """Generates a random time-domain noise realization from the spectral density.
        @param td (optional) instance of class TimeDescriptor describing the time
        descriptor of the waveform to produce.
        @return instance of class Waveform containing a random noise realization
        whose expected spectrum matches self.
        @remark
        Each interior bin is assigned an independent uniformly distributed phase;
        the DC bin (and the Nyquist bin when Keven) are kept real so that the
        inverse DFT yields a real-valued waveform.
        @note
        If td is None, the time descriptor corresponding to self's FrequencyList
        is used.
        """
        # pragma: silent exclude
        from SignalIntegrity.Lib.TimeDomain.Waveform.Waveform import Waveform
        # pragma: include
        fd=self.FrequencyList()
        delta_f=fd.Fe/fd.N
        rho=self.Values('V/sqrt(Hz)')
        rms=DFTUtilities.rho_to_rms(rho,delta_f,self.Keven)
        A=DFTUtilities.rms_to_A(rms,self.Keven)
        X=DFTUtilities.A_to_X(A,self.Keven,random_phase=True)
        F=DFTUtilities.Half_to_Full(X,self.Keven)
        x=fft.ifft(F).real
        wf_td=fd.TimeDescriptor(Keven=self.Keven)
        wf=Waveform(wf_td,x)
        if td is not None:
            wf=wf.Adapt(td)
        return wf
    def Resample(self,fdp):
        """Resamples the spectral density to a different frequency list.
        @param fdp instance of class FrequencyList to resample to.
        @return instance of class SpectralDensity containing self resampled onto
        fdp using linear interpolation of the V/sqrt(Hz) values.
        @remark Resampling is performed on the magnitude in V/sqrt(Hz); points
        beyond self's end frequency are clamped to zero.
        """
        if fdp is None:
            return SpectralDensity(self.FrequencyList(),self.Values(),self.Keven)
        from numpy import interp
        fd=self.FrequencyList()
        old_f=list(fd)
        old_rho=self.Values('V/sqrt(Hz)')
        new_f=list(fdp)
        interpolated=interp(new_f,old_f,old_rho)
        new_rho=np.where(np.asarray(new_f)<=old_f[-1],interpolated,0.0)
        return SpectralDensity(fdp,new_rho,self.Keven)
    @staticmethod
    def WhiteNoise(fd,specification_type,value,noise_bandwidth=None,Keven=True):
        """Constructs a flat (white) noise SpectralDensity.
        @param fd instance of class FrequencyList for the frequency descriptor.
        @param specification_type string one of 'dBm/Hz', 'V/sqrt(Hz)', or 'Vrms'.
        @param value float the noise level expressed in the specification_type:
        - 'dBm/Hz'     : power spectral density in dBm/Hz
        - 'V/sqrt(Hz)' : amplitude spectral density in V/sqrt(Hz)
        - 'Vrms'       : total rms voltage over noise_bandwidth
        @param noise_bandwidth (optional) float bandwidth in Hz over which the
        total rms value is specified.  Required only when
        specification_type == 'Vrms'.
        @param Keven (optional) bool whether the corresponding time-record length
        is even.  Defaults to True.
        @return instance of class SpectralDensity containing a flat spectral
        density evaluated at each frequency in fd.
        """
        if specification_type == 'V/sqrt(Hz)':
            rho=value
        elif specification_type == 'dBm/Hz':
            rho=math.sqrt(SpectralDensity.R*SpectralDensity.P*
                          10.**(value/10.))
        elif specification_type == 'Vrms':
            if noise_bandwidth is None or noise_bandwidth <= 0:
                raise ValueError(
                    'noise_bandwidth must be positive for Vrms specification')
            rho=value/math.sqrt(noise_bandwidth)
        else:
            raise ValueError(
                "specification_type must be 'dBm/Hz', 'V/sqrt(Hz)', or 'Vrms'")
        return SpectralDensity(fd,[rho for _ in range(fd.N+1)],Keven)
    def __eq__(self,other):
        """overloads ==
        @param other another instance of class SpectralDensity (or FrequencyDomain).
        @return bool whether self == other.
        """
        if hasattr(other,'Keven') and self.Keven != other.Keven:
            return False
        return FrequencyDomain.__eq__(self,other)
    def __ne__(self,other):
        """overloads !=
        @param other another instance of class SpectralDensity (or FrequencyDomain).
        @return bool whether self != other.
        """
        return not self == other

    def __mul__(self, other):
        """Multiplies a FrequencyResponse by this SpectralDensity (element-wise magnitude).
        @param other instance of class FrequencyResponse.
        @return instance of class SpectralDensity where each bin is |H(f)| * SD(f).
        """
        if isinstance(other,(float,int)):
            return SpectralDensity(self.FrequencyList(),
                        np.abs(self.values)*other,
                        self.Keven)

        return SpectralDensity(self.FrequencyList(),
            np.abs(np.asarray(other))*np.abs(self.values),
            self.Keven)

    def __rmul__(self, other):
        """Right-multiply: allows FrequencyResponse * SpectralDensity.
        @param other instance of class FrequencyResponse, int, or float
        @return instance of class SpectralDensity where each bin is |H(f)| * SD(f).
        """
        return self.__mul__(other)

    def __add__(self, other):
        """Adds two SpectralDensity instances as root-sum-square.
        @param other instance of class SpectralDensity.
        @return instance of class SpectralDensity where each bin is sqrt(a^2 + b^2).
        @remark This models the combination of uncorrelated noise sources.
        """
        return SpectralDensity(self.FrequencyList(),
            np.sqrt(np.square(np.asarray(self.Values()))+
                    np.square(np.asarray(other.Values()))),
            self.Keven)

    ##
    # @var Keven
    # bool whether the corresponding time-record length K is even (K=2*N) or
    # odd (K=2*N+1); affects Nyquist-bin handling in unit conversions and in
    # NoiseWaveform.
