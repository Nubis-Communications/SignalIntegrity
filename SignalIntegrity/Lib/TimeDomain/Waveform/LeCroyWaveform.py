"""
LeCroyWaveform.py
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

from SignalIntegrity.Lib.Exception import SignalIntegrityExceptionWaveformFile

import numpy as np
import sys,os
import math

"""
This file defines the numpy dtype strings for the lecroy waveform template.
Note that the endianness of the basic data types is for file access and
is opposite from what the remote interface yields.
"""

WFM_STRING = "S16"
WFM_BYTE = "i1"
WFM_WORD = "<i2"
WFM_LONG = "<i4"
WFM_FLOAT = "<f4"
WFM_DOUBLE = "<f8"
WFM_ENUM = "<u2"

WFM_DATA_WORD = "<i2"
WFM_DATA_BYTE = "i1"
WFM_TEXT = "S"
WFM_UNIT_DEFINITION = "S48"

WFM_TIME_STAMP = [("seconds",WFM_DOUBLE),("minute",WFM_BYTE),("hour",WFM_BYTE),("day",WFM_BYTE),("month",WFM_BYTE),("year",WFM_WORD),("reserved",WFM_WORD)]

TRIGGER_TIME_ARRAY = [("TRIGGER_TIME",WFM_DOUBLE),("TRIGGER_OFFSET",WFM_DOUBLE)]

WFM_DESC = [
("DESCRIPTOR_NAME", WFM_STRING ),       # the first 8 chars are always WAVEDESC
("TEMPLATE_NAME", WFM_STRING),
("COMM_TYPE", WFM_ENUM ),               # chosen by remote command COMM_FORMAT
("COMM_ORDER", WFM_ENUM ),
("WAVE_DESCRIPTOR", WFM_LONG ),         # length in bytes of block WAVEDESC
("USER_TEXT", WFM_LONG ),               # length in bytes of block USERTEXT
("RES_DESC1", WFM_LONG ),               #
("TRIGTIME_ARRAY", WFM_LONG ),          # length in bytes of TRIGTIME array
("RIS_TIME_ARRAY", WFM_LONG ),          # length in bytes of RIS_TIME array
("RES_ARRAY1", WFM_LONG ),              # an expansion entry is reserved
("WAVE_ARRAY_1", WFM_LONG ),            # length in bytes of 1st simple
("WAVE_ARRAY_2", WFM_LONG ),            # length in bytes of 2nd simple
("RES_ARRAY2", WFM_LONG),
("RES_ARRAY3", WFM_LONG ),              # 2 expansion entries are reserved
("INSTRUMENT_NAME", WFM_STRING),
("INSTRUMENT_NUMBER", WFM_LONG),
("TRACE_LABEL", WFM_STRING ),           # identifies the waveform.
("RESERVED1", WFM_WORD),
("RESERVED2", WFM_WORD ),               # 2 expansion entries
("WAVE_ARRAY_COUNT", WFM_LONG ),        # number of data points in the data
("PNTS_PER_SCREEN", WFM_LONG ),         # nominal number of data points
("FIRST_VALID_PNT", WFM_LONG ),         # count of number of points to skip
("LAST_VALID_PNT", WFM_LONG ),          # index of last good data point
("FIRST_POINT", WFM_LONG ),             # for input and output, indicates
("SPARSING_FACTOR", WFM_LONG ),         # for input and output, indicates
("SEGMENT_INDEX", WFM_LONG ),           # for input and output, indicates the
("SUBARRAY_COUNT", WFM_LONG ),          # for Sequence, acquired segment count,
("SWEEPS_PER_ACQ", WFM_LONG ),          # for Average or Extrema,
("POINTS_PER_PAIR", WFM_WORD ),         # for Peak Detect waveforms (which
("PAIR_OFFSET", WFM_WORD ),             # for Peak Detect waveforms only
("VERTICAL_GAIN", WFM_FLOAT),
("VERTICAL_OFFSET", WFM_FLOAT ),        # to get WFM_FLOATing values from raw data ",
("MAX_VALUE", WFM_FLOAT ),              # maximum allowed value. It corresponds
("MIN_VALUE", WFM_FLOAT ),              # minimum allowed value. It corresponds
("NOMINAL_BITS", WFM_WORD ),            # a measure of the intrinsic precision
("NOM_SUBARRAY_COUNT", WFM_WORD ),      # for Sequence, nominal segment count
("HORIZ_INTERVAL", WFM_FLOAT ),         # sampling interval for time domain
("HORIZ_OFFSET", WFM_DOUBLE ),          # trigger offset for the first sweep of
("PIXEL_OFFSET", WFM_DOUBLE ),          # needed to know how to display the
("VERTUNIT", WFM_UNIT_DEFINITION ),     # units of the vertical axis
("HORUNIT", WFM_UNIT_DEFINITION ),      # units of the horizontal axis
("HORIZ_UNCERTAINTY", WFM_FLOAT ),      # uncertainty from one acquisition to the
("TRIGGER_TIME", WFM_TIME_STAMP ),      # time of the trigger
("ACQ_DURATION", WFM_FLOAT ),           # duration of the acquisition (in sec)
("RECORD_TYPE", WFM_ENUM),
("PROCESSING_DONE", WFM_ENUM),
("RESERVED5", WFM_WORD ),               # expansion entry
("RIS_SWEEPS", WFM_WORD ),              # for RIS, the number of sweeps
("TIMEBASE", WFM_ENUM),
("VERT_COUPLING", WFM_ENUM),
("PROBE_ATT", WFM_FLOAT),
("FIXED_VERT_GAIN", WFM_ENUM),
("BANDWIDTH_LIMIT", WFM_ENUM),
("VERTICAL_VERNIER", WFM_FLOAT),
("ACQ_VERT_OFFSET", WFM_FLOAT),
("WAVE_SOURCE", WFM_ENUM)]


default_descriptor_values = {
    "WAVE_ARRAY_COUNT":             1002,           # exact number of samples in the waveform
    "NOM_SUBARRAY_COUNT":           1,              # the number of segments in the waveform
    "TRACE_LABEL":                  "",
    "PAIR_OFFSET":                  0,
    "RES_DESC1":                    0,
    "FIRST_VALID_PNT":              0,
    "USER_TEXT":                    0,
    "TEMPLATE_NAME":                "LECROY_2_3",
    "HORUNIT":                      "S",
    "POINTS_PER_PAIR":              0,
    "BANDWIDTH_LIMIT":              0,
    "RES_ARRAY2":                   0,
    "RES_ARRAY3":                   0,
    "SPARSING_FACTOR":              1,
    "RES_ARRAY1":                   0,
    "PROBE_ATT":                    1.,
    "VERTUNIT":                     "V",
    "INSTRUMENT_NUMBER":            7,
    "PNTS_PER_SCREEN":              1000,           # set to 2 less than the total number of points?
    "HORIZ_OFFSET":-                0.0001,         # time of the first point at the left (first one or first one on screen?)
    "FIRST_POINT":                  0,
    "HORIZ_INTERVAL":               2.00000003e-10, #1/sample rate
    "WAVE_SOURCE":                  0,
    "VERT_COUPLING":                2,
    "TRIGGER_TIME":                 (22.805368966, 55, 15, 29, 9, 2016, 0),
    "LAST_VALID_PNT":               1000001,        # WAVE_ARRAY_COUNT - 1
    "RECORD_TYPE":                  0,
    "WAVE_ARRAY_1":                 2000004,        # 2 * WAVE_ARRAY_COUNT if the data type is word
    "WAVE_ARRAY_2":                 0,
    "SEGMENT_INDEX":                0,
    "INSTRUMENT_NAME":              "LECROYHDO6104",
    "COMM_ORDER":                   1,
    "COMM_TYPE":                    1,
    "SWEEPS_PER_ACQ":               1,
    "MIN_VALUE":                    -32000.,        # the data is 16 bits so this is the minimum value
    "MAX_VALUE":                    31744.,         # the data is 16 bits so this is the minimum value
    "RIS_SWEEPS":                   1,
    "FIXED_VERT_GAIN":              17,
    "TRIGTIME_ARRAY":               0,
    "ACQ_DURATION":                 0.0,
    "TIMEBASE":                     22,
    "RESERVED1":                    16962,
    "ACQ_VERT_OFFSET":              0.0,            # the vertical offset of the channel
    "RESERVED2":                    15,
    "NOMINAL_BITS":                 12,
    "PROCESSING_DONE":              0,
    "RIS_TIME_ARRAY":               0,
    "SUBARRAY_COUNT":               1,
    "WAVE_DESCRIPTOR":              346,
    "PIXEL_OFFSET":                 -1.00000000e-04,    # not sure
    "VERTICAL_VERNIER":             1.,
    "HORIZ_UNCERTAINTY":            9.99999996e-13,
    "VERTICAL_OFFSET":             -0.,             # vertical offset but different than ACQ_VERT_OFFSET?
    "DESCRIPTOR_NAME":             "WAVEDESC",
    "VERTICAL_GAIN":                6.25000030e-05, # volts per 16 bit code
    "RESERVED5":                    0
}

def to_trc(wf,fname):
    """Save the waveform in lecroy trc format
    @param wf Instance of class Waveform containing the waveform to store.
    @param fname String name of the filename to save to.  Should have a .trc extension
    """
    try:
        filename, file_extension = os.path.splitext(fname)
        extensionCorrect=True
        if file_extension=='' or file_extension is None:
            fname=fname+'.trc'
        else:
            file_extension=file_extension.lower()
            if file_extension != '.trc':
                extensionCorrect=False
        if not extensionCorrect:
            raise SignalIntegrityExceptionWaveformFile('incorrect extension LeCroy trace file name in '+fname+'.  Should be .trc.')
    except:
        raise SignalIntegrityExceptionWaveformFile('incorrect extension in LeCroy trace file name in '+fname+'.  Should be .trc.')

    try:
        # setup the descriptor and populate it with the default values
        desc = np.empty((1,),dtype=WFM_DESC)
        for field in default_descriptor_values:
            desc[field] = default_descriptor_values[field]

        # TODO: add option to store the raw samples directly rather than re-scaling to get maximum resolution (this might be more important for the ADC tester)
        # force the waveform into the right format
        x = np.array(wf.Values())
        vert_scale = (x.max() - x.min())/60000
        vert_offset = x.min() + (x.max() - x.min())/2

        # modify the descriptor where needed
        desc["WAVE_ARRAY_COUNT"]=   len(x),         # exact number of samples in the waveform
        desc["NOM_SUBARRAY_COUNT"]= 1,              # the number of segments in the waveform
        desc["PNTS_PER_SCREEN"]=    len(x),         # set to 2 less than the total number of points?
        desc["HORIZ_OFFSET"]=       wf.td.H,        # time of the first point at the left (first one or first one on screen?)
        desc["HORIZ_INTERVAL"]=     1/wf.td.Fs,     # 1/sample rate
        desc["LAST_VALID_PNT"]=     len(x)-1,       # WAVE_ARRAY_COUNT - 1
        desc["WAVE_ARRAY_1"]=       2*len(x),       # 2 * WAVE_ARRAY_COUNT if the data type is word
        desc["MIN_VALUE"]=          -32000.,        # the data is 16 bits so this is the minimum value
        desc["MAX_VALUE"]=          31744.,         # the data is 16 bits so this is the minimum value
        desc["ACQ_VERT_OFFSET"]=    -vert_offset,   # the vertical offset of the channel
        desc["PIXEL_OFFSET"]=       wf.td.H,        # not sure
        desc["VERTICAL_OFFSET"]=    -vert_offset,   # vertical offset but different than ACQ_VERT_OFFSET?
        desc["VERTICAL_GAIN"] =     vert_scale,     # volts per 16 bit code
        desc["FIXED_VERT_GAIN"] =   15

        # reload these to acquire the quantization effect of storing them in the descriptor
        vert_scale = desc["VERTICAL_GAIN"][0]
        vert_offset = -desc["VERTICAL_OFFSET"][0]
        x_int = ((x - vert_offset)/vert_scale).astype(dtype="<i2")

        # Write the values to file
        total_length = 2*len(x) + 346

        with open(fname, "wb") as f:
            if sys.version_info.major > 2:
                f.write(bytes('#9{:09d}'.format(total_length), encoding='utf-8'))
            else:
                f.write(b'#9{:09d}'.format(total_length))
            f.write(desc)
            # f.write('\00')
            f.write(x_int.tobytes())
            # f.write('\00')
    except:
        raise SignalIntegrityExceptionWaveformFile('LeCroy trace file could not be written: '+fname)

def from_trc(filename):
    """Read a waveform in lecroy trc format
    @param filename String name of the filename to read.  Should have a .trc extension
    @return a waveform in SignalIntegrity format
    """
    try:
        fname, file_extension = os.path.splitext(filename)
        extensionCorrect=True
        if file_extension=='' or file_extension is None:
            filename=filename+'.trc'
        else:
            file_extension=file_extension.lower()
            if file_extension != '.trc':
                extensionCorrect=False
        if not extensionCorrect:
            raise SignalIntegrityExceptionWaveformFile('incorrect extension LeCroy trace file name in '+filename+'.  Should be .trc.')
    except:
        raise SignalIntegrityExceptionWaveformFile('incorrect extension in LeCroy trace file name in '+filename+'.  Should be .trc.')
    try:
        with open(filename, "rb") as f:
            header=f.read(11).decode()
            start=header[0:2]
            if start != '#9':
                raise SignalIntegrityExceptionWaveformFile('Incorrect LeCroy trace file header in: '+filename)
            count=int(header[2:11])
            descData=np.frombuffer(f.read(346),np.dtype(WFM_DESC))
            wfBuffer=np.frombuffer(f.read(count-346),'int16')
            if descData["NOM_SUBARRAY_COUNT"] != 1:
                raise SignalIntegrityExceptionWaveformFile('Cannot read multi-segment waveform in: '+filename)
            vertScale=descData['VERTICAL_GAIN'][0]
            vertOffset=-descData['VERTICAL_OFFSET'][0]
            horizontalOffset=descData['HORIZ_OFFSET'][0]
            sampleRate=1./descData['HORIZ_INTERVAL'][0]
            Exp=10**round(math.log10(sampleRate),6)
            sampleRate=sampleRate/Exp
            sampleRate=round(sampleRate,6)
            sampleRate=sampleRate*Exp
            numPoints=descData['WAVE_ARRAY_COUNT'][0]
            from SignalIntegrity.Lib.TimeDomain.Waveform.Waveform import Waveform
            from SignalIntegrity.Lib.TimeDomain.Waveform.TimeDescriptor import TimeDescriptor
            wf=Waveform(TimeDescriptor(horizontalOffset,numPoints,sampleRate),
                                 [v*vertScale+vertOffset for v in wfBuffer])
            return wf
    except:
        raise SignalIntegrityExceptionWaveformFile('LeCroy trace file could not be read: '+filename)
