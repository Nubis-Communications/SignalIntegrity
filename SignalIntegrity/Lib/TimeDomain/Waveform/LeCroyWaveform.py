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

from SignalIntegrity.Lib.TimeDomain.Waveform.TimeDescriptor import TimeDescriptor
from SignalIntegrity.Lib.TimeDomain.Waveform.AdaptedWaveforms import AdaptedWaveforms
from SignalIntegrity.Lib.Exception import SignalIntegrityExceptionWaveformFile

from struct import unpack
import numpy as np
import struct
import array

def read_timetrace(filename):
	'''
	Read binary waveform file (.trc) from LeCroy waverunner
	Based on Matlab file LCREAD.m
	Input:
		filename : filename, string
	Output:

	'''
	## Seek offset in the header block
	fid = open(filename, "r")
	data = fid.read(50)
	WAVEDESC = str.find(data,'WAVEDESC')
	##---------------------------------------------------------------------------------------
	## Define the addresses of the various informations in the file
	## These addresses are valid for the template LECROY_2_2 and are subject to change in
	## future revisions of the LeCroy firmware
	##---------------------------------------------------------------------------------------
	TESTED_TEMPLATE = 'LECROY_2_3';

	#Addresses (WAVEDESC + address as stated in the LECROY template)
	aCOMM_TYPE			= WAVEDESC+ 32;
	aCOMM_ORDER			= WAVEDESC+ 34;
	aWAVE_DESCRIPTOR	= WAVEDESC+ 36;	# length of the descriptor block
	aUSER_TEXT			= WAVEDESC+ 40;	# length of the usertext block
	aTRIGTIME_ARRAY     = WAVEDESC+ 48; # length of the TRIGTIME array
	aWAVE_ARRAY_1		= WAVEDESC+ 60;	# length (in Byte) of the sample array

	aVERTICAL_GAIN		= WAVEDESC+ 156;
	aVERTICAL_OFFSET	= WAVEDESC+ 160;

	aHORIZ_INTERVAL	    = WAVEDESC+ 176;
	aHORIZ_OFFSET		= WAVEDESC+ 180;

	#---------------------------------------------------------------------------------------
	## determine the number storage format HIFIRST / LOFIRST 	(big endian / little endian)
	#---------------------------------------------------------------------------------------

	fid.seek(aCOMM_ORDER)
	COMM_ORDER = ord(fid.read(1))

	if COMM_ORDER == 0:
	 	## big-endian
		fmt = '>'
	else:
		## little-endian
		fmt = '<'

	COMM_TYPE			= ReadWord(fid, fmt, aCOMM_TYPE)
	WAVE_DESCRIPTOR 	= ReadLong(fid, fmt, aWAVE_DESCRIPTOR)
	USER_TEXT			= ReadLong(fid, fmt, aUSER_TEXT)
	TRIGTIME_array      = ReadLong(fid, fmt, aTRIGTIME_ARRAY)
	WAVE_ARRAY_1		= ReadLong(fid, fmt, aWAVE_ARRAY_1)
	VERTICAL_GAIN		= ReadFloat	(fid, fmt, aVERTICAL_GAIN)
	VERTICAL_OFFSET		= ReadFloat	(fid, fmt, aVERTICAL_OFFSET)
	HORIZ_INTERVAL		= ReadFloat(fid, fmt, aHORIZ_INTERVAL);
	HORIZ_OFFSET		= ReadDouble(fid, fmt, aHORIZ_OFFSET);

	fid.close()
	fid = open(filename, "rb")

	y = ReadData(fid, fmt, WAVEDESC + WAVE_DESCRIPTOR + USER_TEXT + TRIGTIME_array, WAVE_ARRAY_1)
	y = VERTICAL_GAIN * y - VERTICAL_OFFSET
	x = np.arange(1,len(y)+1)*HORIZ_INTERVAL + HORIZ_OFFSET

	fid.close()
	return x,y

def ReadByte(fid,fmt,Addr):
	fid.seek(Addr)
	s = fid.readline(1)
	s = unpack(fmt + 'b', s)
	if(type(s) == tuple):
		return s[0]
	else:
		return s

def ReadWord(fid,fmt,Addr):
	fid.seek(Addr)
	s = fid.readline(2)
	s = unpack(fmt + 'h', s)
	if(type(s) == tuple):
		return s[0]
	else:
		return s

def ReadLong(fid,fmt,Addr):
	fid.seek(Addr)
	s = fid.readline(4)
	s = unpack(fmt + 'l', s)
	if(type(s) == tuple):
		return s[0]
	else:
		return s

def ReadFloat(fid,fmt,Addr):
	fid.seek(Addr)
	s = fid.readline(4)
	s = unpack(fmt + 'f', s)
	if(type(s) == tuple):
		return s[0]
	else:
		return s

def ReadDouble(fid,fmt,Addr):
	fid.seek(Addr)
	s = fid.readline(8)
	s = unpack(fmt + 'd', s)
	if(type(s) == tuple):
		return s[0]
	else:
		return s

def ReadData(fid, fmt, Addr, datalen):
    import time
    start = time.time()
    fid.seek(Addr)
    #m1 = time.time()
    fmt = fmt + str(datalen) + "b"
    nbytes = struct.calcsize(fmt)
    data = fid.read(nbytes)
    #m2 = time.time()
    result = np.frombuffer(data, 'b', nbytes)
#    result = struct.unpack(fmt, data[0:nbytes])
    #m3 = time.time()
    #print 'M1: %s, M2: %s, M3: %s' % (m1-start,m2-start,m3-start)
    return result
