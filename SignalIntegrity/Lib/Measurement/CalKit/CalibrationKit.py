"""
 calibration kits and constants
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

from SignalIntegrity.Lib.Measurement.CalKit.Standards.ShortStandard import ShortStandard
from SignalIntegrity.Lib.Measurement.CalKit.Standards.OpenStandard import OpenStandard
from SignalIntegrity.Lib.Measurement.CalKit.Standards.LoadStandard import LoadStandard
from SignalIntegrity.Lib.Measurement.CalKit.Standards.ThruStandard import ThruStandard
from SignalIntegrity.Lib.SParameters.SParameterFile import SParameterFile

class CalibrationConstants(object):
    """Class for holding, reading and writing calibration constants for a calibration kit

    Calibration Constants File Format

    @verbatim
    % DESCRIPTION [Enter manufacturer and model number of calkit]
    % 
    % C0 (fF) - OPEN
    % C1 (1e-27 F/Hz) - OPEN
    % C2 (1e-36 F/Hz^2) - OPEN
    % C3 (1e-45 F/Hz^3) - OPEN
    % offset delay (pS) - OPEN
    % real(Zo) of offset length - OPEN
    % offset loss (GOhm/s) - OPEN
    % L0 (pH) - SHORT
    % L1 (1e-24 H/Hz) - SHORT
    % L2 (1e-33 H/Hz^2) - SHORT
    % L3 (1e-42 H/Hz^3) - SHORT
    % offset delay (pS) - SHORT
    % real(Zo) of offset length - SHORT
    % offset loss (GOhm/s) - SHORT
    % load resistance (Ohm) - LOAD
    % offset delay (pS) - LOAD
    % real(Zo) of offset length - LOAD
    % offset loss (GOhm/s) - LOAD
    % offset delay (pS) - THRU
    % real(Zo) of offset length - THRU
    % offset loss (GOhm/s) - THRU
    63.170000 
    -1178.000000
    109.600000
    -2.146000
    14.490000
    50.000000
    1.300000
    0.000000
    0.000000
    0.000000
    0.000000
    16.684000
    50.000000
    1.300000
    50.000000
    0.000000
    50.000000
    1.300000
    57.960000
    50.000000
    0.000000
    @endverbatim
    """
    def __init__(self):
        """Constructor
        Initializes the calibration constants such that the calibration kit contains:
        - open standard - a perfect, lossless, lengthless open
        - short standard - a perfect, lossless, lengthless short
        - load standard - a perfect, lossless, lengthless 50 Ohm termination
        - thru standard - a perfect, lossless, lengthless 50 Ohm thru
        """
        self.openC0=0.              # % C0 (fF) - OPEN
        self.openC1=0.              # % C1 (1e-27 F/Hz) - OPEN
        self.openC2=0.              # % C2 (1e-36 F/Hz^2) - OPEN
        self.openC3=0.              # % C3 (1e-45 F/Hz^3) - OPEN
        self.openOffsetDelay=0.     # % offset delay (pS) - OPEN
        self.openOffsetZ0=50.       # % real(Zo) of offset length - OPEN
        self.openOffsetLoss=0.      # % offset loss (GOhm/s) - OPEN
        self.shortL0=0.             # % L0 (pH) - SHORT
        self.shortL1=0.             # % L1 (1e-24 H/Hz) - SHORT
        self.shortL2=0.             # % L2 (1e-33 H/Hz^2) - SHORT
        self.shortL3=0.             # % L3 (1e-42 H/Hz^3) - SHORT
        self.shortOffsetDelay=0.    # % offset delay (pS) - SHORT
        self.shortOffsetZ0=50.      # % real(Zo) of offset length - SHORT
        self.shortOffsetLoss=0.     # % offset loss (GOhm/s) - SHORT
        self.loadZ=50.              # % load resistance (Ohm) - LOAD
        self.loadOffsetDelay=0.     # % offset delay (pS) - LOAD
        self.loadOffsetZ0=50.       # % real(Zo) of offset length - LOAD
        self.loadOffsetLoss=0.      # % offset loss (GOhm/s) - LOAD
        self.thruOffsetDelay=0.     # % offset delay (pS) - THRU
        self.thruOffsetZ0=50.       # % real(Zo) of offset length - THRU
        self.thruOffsetLoss=0.      # % offset loss (GOhm/s) - THRU
    def ReadFromFile(self,filename):
        """The file is read from the disk and the constants stored internally.
        @param filename string name of calibration constant file to read.
        @return self
        """
        with open(filename) as f:
            lines=f.readlines()
        actualLines=[]
        for line in lines:
            if line.strip()[0]!='%':
                actualLines.append(line.strip())
        # % C0 (fF) - OPEN
        self.openC0=float(actualLines[0])*1e-15
        # % C1 (1e-27 F/Hz) - OPEN
        self.openC1=float(actualLines[1])*1e-27
        # % C2 (1e-36 F/Hz^2) - OPEN
        self.openC2=float(actualLines[2])*1e-36
        # % C3 (1e-45 F/Hz^3) - OPEN
        self.openC3=float(actualLines[3])*1e-45
        # % offset delay (pS) - OPEN
        self.openOffsetDelay=float(actualLines[4])*1e-12
        # % real(Zo) of offset length - OPEN
        self.openOffsetZ0=float(actualLines[5])
        # % offset loss (GOhm/s) - OPEN
        self.openOffsetLoss=float(actualLines[6])*1e9
        # % L0 (pH) - SHORT
        self.shortL0=float(actualLines[7])*1e-12
        # % L1 (1e-24 H/Hz) - SHORT
        self.shortL1=float(actualLines[8])*1e-24
        # % L2 (1e-33 H/Hz^2) - SHORT
        self.shortL2=float(actualLines[9])*1e-33
        # % L3 (1e-42 H/Hz^3) - SHORT
        self.shortL3=float(actualLines[10])*1e-42
        # % offset delay (pS) - SHORT
        self.shortOffsetDelay=float(actualLines[11])*1e-12
        # % real(Zo) of offset length - SHORT
        self.shortOffsetZ0=float(actualLines[12])
        # % offset loss (GOhm/s) - SHORT
        self.shortOffsetLoss=float(actualLines[13])*1e9
        # % load resistance (Ohm) - LOAD
        self.loadZ=float(actualLines[14])
        # % offset delay (pS) - LOAD
        self.loadOffsetDelay=float(actualLines[15])*1e-12
        # % real(Zo) of offset length - LOAD
        self.loadOffsetZ0=float(actualLines[16])
        # % offset loss (GOhm/s) - LOAD
        self.loadOffsetLoss=float(actualLines[17])*1e9
        # % offset delay (pS) - THRU
        self.thruOffsetDelay=float(actualLines[18])*1e-12
        # % real(Zo) of offset length - THRU
        self.thruOffsetZ0=float(actualLines[19])
        # % offset loss (GOhm/s) - THRU
        self.thruOffsetLoss=float(actualLines[20])*1e9
        return self
    def WriteToFile(self,filename,calkitname=None):
        """The calibration constants are written to a file.
        @param filename string name of calibration constant file to write
        @param calkitname (optional) string containing header information to be placed after the DESCRIPTION:
        in the header information.
        @return self 
        @see CalibrationConstants
        """
        line=[]
        if not calkitname is None:
            line.append('% DESCRIPTION: '+calkitname+'\n')
        else:
            line.append('% DESCRIPTION [Enter manufacturer and model number of calkit]\n')
        line.append('%\n')
        line.append('% C0 (fF) - OPEN\n')
        line.append('% C1 (1e-27 F/Hz) - OPEN\n')
        line.append('% C2 (1e-36 F/Hz^2) - OPEN\n')
        line.append('% C3 (1e-45 F/Hz^3) - OPEN\n')
        line.append('% offset delay (pS) - OPEN\n')
        line.append('% real(Zo) of offset length - OPEN\n')
        line.append('% offset loss (GOhm/s) - OPEN\n')
        line.append('% L0 (pH) - SHORT\n')
        line.append('% L1 (1e-24 H/Hz) - SHORT\n')
        line.append('% L2 (1e-33 H/Hz^2) - SHORT\n')
        line.append('% L3 (1e-42 H/Hz^3) - SHORT\n')
        line.append('% offset delay (pS) - SHORT\n')
        line.append('% real(Zo) of offset length - SHORT\n')
        line.append('% offset loss (GOhm/s) - SHORT\n')
        line.append('% load resistance (Ohm) - LOAD\n')
        line.append('% offset delay (pS) - LOAD\n')
        line.append('% real(Zo) of offset length - LOAD\n')
        line.append('% offset loss (GOhm/s) - LOAD\n')
        line.append('% offset delay (pS) - THRU\n')
        line.append('% real(Zo) of offset length - THRU\n')
        line.append('% offset loss (GOhm/s) - THRU\n')
        line.append('{:.12g}\n'.format(self.openC0/1e-15))            # % C0 (fF) - OPEN
        line.append('{:.12g}\n'.format(self.openC1/1e-27))            # % C1 (1e-27 F/Hz) - OPEN
        line.append('{:.12g}\n'.format(self.openC2/1e-36))            # % C2 (1e-36 F/Hz^2) - OPEN
        line.append('{:.12g}\n'.format(self.openC3/1e-45))            # % C3 (1e-45 F/Hz^3) - OPEN
        line.append('{:.12g}\n'.format(self.openOffsetDelay/1e-12))   # % offset delay (pS) - OPEN
        line.append('{:.12g}\n'.format(self.openOffsetZ0))            # % real(Zo) of offset length - OPEN
        line.append('{:.12g}\n'.format(self.openOffsetLoss/1e9))      # % offset loss (GOhm/s) - OPEN
        line.append('{:.12g}\n'.format(self.shortL0/1e-12))           # % L0 (pH) - SHORT
        line.append('{:.12g}\n'.format(self.shortL1/1e-24))           # % L1 (1e-24 H/Hz) - SHORT
        line.append('{:.12g}\n'.format(self.shortL2/1e-33))           # % L2 (1e-33 H/Hz^2) - SHORT
        line.append('{:.12g}\n'.format(self.shortL3/1e-42))           # % L3 (1e-42 H/Hz^3) - SHORT
        line.append('{:.12g}\n'.format(self.shortOffsetDelay/1e-12))  # % offset delay (pS) - SHORT
        line.append('{:.12g}\n'.format(self.shortOffsetZ0))           # % real(Zo) of offset length - SHORT
        line.append('{:.12g}\n'.format(self.shortOffsetLoss/1e9))      # % offset loss (GOhm/s) - SHORT
        line.append('{:.12g}\n'.format(self.loadZ))                   # % load resistance (Ohm) - LOAD
        line.append('{:.12g}\n'.format(self.loadOffsetDelay/1e-12))   # % offset delay (pS) - LOAD
        line.append('{:.12g}\n'.format(self.loadOffsetZ0))            # % real(Zo) of offset length - LOAD
        line.append('{:.12g}\n'.format(self.loadOffsetLoss/1e9))      # % offset loss (GOhm/s) - LOAD
        line.append('{:.12g}\n'.format(self.thruOffsetDelay/1e-12))   # % offset delay (pS) - THRU
        line.append('{:.12g}\n'.format(self.thruOffsetZ0))            # % real(Zo) of offset length - THRU
        line.append('{:.12g}\n'.format(self.thruOffsetLoss/1e9))      # % offset loss (GOhm/s) - THRU
        with open(filename,'w') as f:
            f.writelines(line)
        return self
    ## @var openC0
    # float Capacitance polynomial term for f^0 for open standard in F.
    # @note the internal storage is in the correct units and is the value in the calibration contants file
    # *1e-15.
    ## @var openC1
    # float Capacitance polynomial term for f^1 for open standard in F/Hz.
    # @note the internal storage is in the correct units and is the value in the calibration contants file
    # *1e-27.
    ## @var openC2
    # float Capacitance polynomial term for f^2 for open standard in F/Hz^2.
    # @note the internal storage is in the correct units and is the value in the calibration contants file
    # *1e-36.
    ## @var openC3
    # float Capacitance polynomial term for f^3 for open standard in F/Hz^3.
    # @note the internal storage is in the correct units and is the value in the calibration contants file
    # *1e-45.
    ## @var openOffsetDelay
    # float open offset electrical length in s.
    # @note the internal storage is in the correct units and is the value in the calibration contants file
    # *1e-12.
    ## @var openOffsetZ0
    # float real characteristic impedance of offset to open in Ohms.
    ## @var openOffsetLoss
    # float open offset loss in Ohm/s at f0=1 GHz.
    # @note the internal storage is in the correct units and is the value in the calibration contants file
    # /1e9.
    ## @var shortL0
    # float Inductance polynomial term for f^0 for short standard in H.
    # @note the internal storage is in the correct units and is the value in the calibration contants file
    # *1e-12.
    ## @var shortL1
    # float Inductance polynomial term for f^1 for short standard in H/Hz.
    # @note the internal storage is in the correct units and is the value in the calibration contants file
    # *1e-24.
    ## @var shortL2
    # float Inductance polynomial term for f^2 for short standard in H/Hz^2.
    # @note the internal storage is in the correct units and is the value in the calibration contants file
    # *1e-33.
    ## @var shortL3
    # float Inductance polynomial term for f^3 for short standard in H/Hz^3.
    # @note the internal storage is in the correct units and is the value in the calibration contants file
    # *1e-42.
    ## @var shortOffsetDelay
    # float short offset electrical length in s.
    # @note the internal storage is in the correct units and is the value in the calibration contants file
    # *1e-12.
    ## @var shortOffsetZ0
    # float real characteristic impedance of offset to short in Ohms.
    ## @var shortOffsetLoss
    # float short offset loss in Ohm/s at f0=1 GHz.
    # @note the internal storage is in the correct units and is the value in the calibration contants file
    # /1e9.
    ## @var loadZ
    # float load resistance in Ohms.
    ## @var loadOffsetDelay
    # float load offset electrical length in s.
    # @note the internal storage is in the correct units and is the value in the calibration contants file
    # *1e-12.
    ## @var loadOffsetZ0
    # float real characteristic impedance of offset to load in Ohms.
    ## @var loadOffsetLoss
    # float load offset loss in Ohm/s at f0=1 GHz.
    # @note the internal storage is in the correct units and is the value in the calibration contants file
    # /1e9.
    ## @var thruOffsetDelay
    # float thru offset electrical length in s.
    # @note the internal storage is in the correct units and is the value in the calibration contants file
    # *1e-12.
    ## @var thruOffsetZ0
    # float real characteristic impedance of offset to thru in Ohms.
    ## @var thruOffsetLoss
    # float thru offset loss in Ohm/s at f0=1 GHz.
    # @note the internal storage is in the correct units and is the value in the calibration contants file
    # /1e9.

class CalibrationKit(object):
    """Class for holding a calibration kit derived from calibration constants"""
    def __init__(self,filename=None,f=None):
        """Constructor
        @param filename (optional) string filename of calibration constants file to read.
        @param f (optional) list of frequencies to define the calibration standards for.
        The calibration constants are initialized to their default as specified in CalibrationConstants.__init__().

        If a filename is specified, the calibration constants are read from the disk.

        If frequencies are provided, the frequencies are initialized and the calibration standards are initialized
        to have the s-parameters of the standards as defined by the frequencies and calibration constants.

        No calibration standards are generated yet if no frequencies are provided.
        @see IntializeFrequency
        """
        self.Constants=CalibrationConstants()
        self.m_f=None
        if not filename is None:
            self.ReadFromFile(filename)
        if not f is None:
            self.InitializeFrequency(f)
    def InitializeFrequency(self,f):
        """Initializes frequencies
        @param f list of frequencies
        Calibration standards are initialized to have the s-parameters of the standards as defined by the
        frequencies and calibration constants.

        Once intialized, the s-parameters of the calibration standards can be accessed and used.
        @see openStandard
        @see shortStandard
        @see loadStandard
        @see thruStandard
        """
        self.m_f=f
        self.openStandard=OpenStandard(self.m_f,self.Constants.openOffsetDelay,
            self.Constants.openOffsetZ0,self.Constants.openOffsetLoss,
            self.Constants.openC0,self.Constants.openC1,self.Constants.openC2,
            self.Constants.openC3)
        self.shortStandard=ShortStandard(self.m_f,self.Constants.shortOffsetDelay,
            self.Constants.shortOffsetZ0,self.Constants.shortOffsetLoss,
            self.Constants.shortL0,self.Constants.shortL1,self.Constants.shortL2,
            self.Constants.shortL3)
        self.loadStandard=LoadStandard(self.m_f,self.Constants.loadOffsetDelay,
            self.Constants.loadOffsetZ0,self.Constants.loadOffsetLoss,
            self.Constants.loadZ)
        self.thruStandard=ThruStandard(self.m_f,self.Constants.thruOffsetDelay,
            self.Constants.thruOffsetZ0,self.Constants.thruOffsetLoss)
        return self
    def ReadFromFile(self,filename):
        """Reads the calibration constants from a file
        @param filename string name of file to read calibration constants from
        @return self
        @see CalibrationConstants.ReadFromFile()
        @see CalibrationConstants for file format
        """
        self.Constants=CalibrationConstants().ReadFromFile(filename)
        return self
    def WriteToFile(self,filename,calkitname=None):
        """Write calibration constants to a file
        @param filename string name of calibration constant file to write
        @param calkitname (optional) string containing header information to be placed after the DESCRIPTION:
        in the header information.
        @return self
        @see CalibrationConstants.WriteToFile()
        """
        self.Constants.WriteToFile(filename, calkitname)
        return self
    def WriteStandardsToFiles(self,filenamePrefix=''):
        """Writes the standards to s-parameter files.
        @param filenamePrefix string name of prefix for standards file names
        @return self
        Each standard is prefixed with the filenamePrefix provided concatenated with:
        - 'Short.s1p' - for the short standard.
        - 'Open.s1p' - for the open standard.
        - 'Load.s1p' - for the load standard.
        - 'Thru.s2p' - for the thru standard
        @attention the member variables for the standards must exist.
        @see shortStandard
        @see openStandard
        @see loadStandard
        @see thruStandard
        """
        self.shortStandard.WriteToFile(filenamePrefix+'Short')
        self.openStandard.WriteToFile(filenamePrefix+'Open')
        self.loadStandard.WriteToFile(filenamePrefix+'Load')
        self.thruStandard.WriteToFile(filenamePrefix+'Thru')
        return self
    def ReadStandardsFromFiles(self,filenamePrefix):
        """Reads the standards from s-parameter files.
        @param filenamePrefix string name of prefix for standards file names
        @return self
        Each standard is prefixed with the filenamePrefix provided concatenated with:
        - 'Short.s1p' - for the short standard.
        - 'Open.s1p' - for the open standard.
        - 'Load.s1p' - for the load standard.
        - 'Thru.s2p' - for the thru standard
        @attention This decouples the standards from the calibration constants and is not preferred.
        @see shortStandard
        @see openStandard
        @see loadStandard
        @see thruStandard 
        """
        self.shortStandard=SParameterFile(filenamePrefix+'Short.s1p')
        self.openStandard=SParameterFile(filenamePrefix+'Open.s1p')
        self.loadStandard=SParameterFile(filenamePrefix+'Load.s1p')
        self.thruStandard=SParameterFile(filenamePrefix+'Thru.s2p')
        return self
    ## @var openStandard
    # instance of class SParameters containing s-parameters of an open standard corresponding to frequencies
    # provided and calibration constants.
    # @attention this only defined if the class was initialized with a frequency list or a call was made to
    # InitializeFrequency()
    #
    ## @var shortStandard
    # instance of class SParameters containing s-parameters of a short standard corresponding to frequencies
    # provided and calibration constants.
    # @attention this only defined if the class was initialized with a frequency list or a call was made to
    # InitializeFrequency()
    #
    ## @var loadStandard
    # instance of class SParameters containing s-parameters of a load standard corresponding to frequencies
    # provided and calibration constants.
    # @attention this only defined if the class was initialized with a frequency list or a call was made to
    # InitializeFrequency()
    #
    ## @var thruStandard
    # instance of class SParameters containing s-parameters of a thru standard corresponding to frequencies
    # provided and calibration constants.
    # @attention this only defined if the class was initialized with a frequency list or a call was made to
    # InitializeFrequency()
    #
    ## @var Constants
    # instance of class CalibrationConstants containing the calibration constants.
    #
    ## @var m_f
    #
    # list of frequencies
    #
