"""
 s-parameter file
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

from numpy import empty
from numpy import array
import cmath
import math
import os
import sys
import inspect
import numpy as np

from SignalIntegrity.Lib.SParameters.SParameters import SParameters
from SignalIntegrity.Lib.Conversions import ReferenceImpedance
from SignalIntegrity.Lib.FrequencyDomain.FrequencyList import GenericFrequencyList
from SignalIntegrity.Lib.Exception import SignalIntegrityExceptionSParameterFile

class SParameterFile(SParameters):
    """class for s-parameters read from a file"""
    sort_frequencies=True
    @staticmethod
    def _CallbackAcceptsName(callback):
        """Whether the callback accepts a 'name' keyword argument.
        File-reading progress is only reported through callbacks that manage a
        progress dialog title stack (which accept a 'name' argument).  The generic
        Lib-level single-argument progress callback is left untouched.
        @param callback function ptr callback function (or None).
        @return bool True if callback is not None and accepts a 'name' argument.
        """
        if callback is None:
            return False
        try:
            params=inspect.signature(callback).parameters
        except (TypeError,ValueError):
            return False
        if 'name' in params:
            return True
        return any(p.kind==inspect.Parameter.VAR_KEYWORD for p in params.values())
    def __init__(self,name,Z0=None,callback=None,**kwargs):
        """Constructor
        @param name string file name of s-parameter file to read.
        @param Z0 (optional) real or complex reference impedance desired (defaults to 50 ohms).
        @param callback function ptr (optional, defaults to None) callback function.
        @param **kwargs dict (optional, defaults to {}) dictionary of arguments for the file

        Reads the s-parameter file and produces an instance of its base class SParameters.  

        If the reference impedance of the Touchstone 1.0 file read is not the reference
        impedance specified, then the reference impedance of the s-parameters are converted
        to the reference impedance specified.

        The callback function is used to pass down into s-parameter files that are actually
        SignalIntegrity projects so that progress can be tracked and the UI thread can be kept
        updated.  The callback function should have a signature like Callback(self,number,name=None),
        where the number is the progress in percent and the name is the name of the file being processed.

        If the name is the name of an s-parameter file and one of the kwarg keywords is 'text', then
        the item associated with the keyword is assumed be a text stream containing s-parameter data to
        directly fill in.  In this case, the file name is used only to determine the number of ports.

        if a kwarg keyword is 'reorder', then it is followed by a string of comma separted integer
        one-based values representing the ports to take the data from in the list.  For example, a
        two-port with the argument 'reorder 1,2' will return the s-parameters unchanged, but
        'reorder 2,1' will swap the ports. You can also use 'reorder 1' to extract the port 1 return
        loss and convert it into a one-port s-parameter.
        """
        self.m_sToken='S'
        self.m_Z0=Z0
        # pragma: silent exclude
        order=kwargs.pop('reorder',None)
        if order not in [None,'None','']:
            order=[int(p) for p in order.split(',')]
        else:
            order=None
        ext=str.lower(name).split('.')[-1]
        if ext == 'si':
            from SignalIntegrity.App.SignalIntegrityAppHeadless import ProjectSParameters
            sp=ProjectSParameters(name,callback,**kwargs)
            if not sp is None:
                if order != None:
                    sp=sp.PortReorder(order)
                SParameters.__init__(self,sp.m_f,sp.m_d,sp.m_Z0)
                self.SetReferenceImpedance(Z0)
                return
            else:
                raise SignalIntegrityExceptionSParameterFile('s-parameters could not be produced by '+name)
        else:
            try:
            # pragma: include outdent outdent
                self.m_P=int(str.lower(name).split('.')[-1].split('s')[1].split('p')[0])
            # pragma: silent exclude indent indent
            except:
                raise SignalIntegrityExceptionSParameterFile('incorrect extension in s-parameter file name in '+name)
        # pragma: include
        freqMul = 1e6
        complexType = 'MA'
        Z0=50.
        sp=True
        self.m_f=[]
        numeric_chunks=[]
        # pragma: silent exclude
        self.header=[]
        self.picture=None
        in_picture=False
        lastReportedProgress=-1
        baseName=os.path.basename(name)
        # only report file-reading progress through the callback if the callback
        # supports the 'name' argument used to manage the progress dialog's title
        # stack (e.g. an App ProgressDialog callback).  The generic Lib-level
        # callback contract only takes a single progress argument and is used to
        # count progress in the frequency loops, so reporting file-read progress
        # through it would corrupt that counting and its abort semantics.
        progressCallback=callback if self._CallbackAcceptsName(callback) else None
        if not progressCallback is None:
            # push the file name onto the progress dialog's title stack and
            # report 0 progress before the (potentially slow) file read so the
            # progress dialog appears immediately
            if progressCallback(0.,name='+'+baseName) is False:
                raise SignalIntegrityExceptionSParameterFile(
                    'reading '+name+' aborted')
        if 'text' in kwargs:
            spfile=kwargs['text']
        else:
            try:
                from SignalIntegrity.Lib.Encryption import Encryption
                spfile=Encryption().ReadEncryptedLines(name)
            except IOError:
                if not progressCallback is None:
                    # pop the file name back off the progress dialog's title stack
                    progressCallback(100.,name='-')
                raise SignalIntegrityExceptionSParameterFile(name+' not found')
        readHeader=True
        totalLines=len(spfile) if hasattr(spfile,'__len__') else None
        # pragma: include
        for lineIndex,line in enumerate(spfile):
            # pragma: silent exclude
            if not progressCallback is None and not totalLines is None:
                progress=int((lineIndex+1)*100//totalLines)
                if progress != lastReportedProgress:
                    lastReportedProgress=progress
                    if progressCallback(progress) is False:
                        raise SignalIntegrityExceptionSParameterFile(
                            'reading '+name+' aborted')
            if readHeader:
                stripped = line.lstrip()
                first = stripped[:1]
                if first in ['!','#'] or first == '':
                    if first == '!':
                        if line == '! picture start\n':
                            self.picture=[]
                            in_picture=True
                            continue
                        elif line == '! picture end\n':
                            in_picture=False
                            continue
                        if in_picture:
                            self.picture.append(line[1:-1]+'\n')
                        else:
                            self.header.append(line[1:-1]+'\n')
                else:
                    readHeader = False
            # pragma: include
            line_no_comment = line.split('!')[0]
            stripped = line_no_comment.lstrip()
            if len(stripped)>0:
                if stripped[:1] == '#':
                    lineList = stripped.lower().split()
                    if 'hz' in lineList: freqMul = 1.0
                    if 'khz' in lineList: freqMul = 1e3
                    if 'mhz' in lineList: freqMul = 1e6
                    if 'ghz' in lineList: freqMul = 1e9
                    if 'ma' in lineList: complexType = 'MA'
                    if 'ri' in lineList: complexType = 'RI'
                    if 'db' in lineList: complexType = 'DB'
                    if 'r' in lineList:
                        Z0=float(lineList[lineList.index('r')+1])
                    if not self.m_sToken.lower() in lineList:
                        sp=False
                else:
                    nums = np.fromstring(line_no_comment, sep=' ')
                    if nums.size:
                        numeric_chunks.append(nums)
        # pragma: silent exclude
        if not progressCallback is None:
            # pop the file name back off the progress dialog's title stack
            progressCallback(100.,name='-')
        # pragma: include
        if not sp: return
        if self.m_Z0==None: self.m_Z0=Z0
        numbers = np.concatenate(numeric_chunks)\
            if len(numeric_chunks)>0 else np.array([],dtype=float)
        # pragma: silent exclude
        if np.any(np.isnan(numbers)):
            raise SignalIntegrityExceptionSParameterFile(name+' has invalid values')
        # pragma: include
        P=self.m_P
        values_per_freq = 1 + P*P*2
        # pragma: silent exclude
        if numbers.size % values_per_freq != 0:
            raise SignalIntegrityExceptionSParameterFile(name+' has invalid values')
        # pragma: include
        values = numbers.reshape((-1, values_per_freq))
        f = values[:, 0] * freqMul
        raw_pairs = values[:, 1:].reshape((-1, P, P, 2))

        if complexType == 'RI':
            m_d_np = raw_pairs[..., 0] + 1j * raw_pairs[..., 1]
        else:
            angles = np.exp(1j * np.deg2rad(raw_pairs[..., 1]))
            if complexType == 'MA':
                m_d_np = raw_pairs[..., 0] * angles
            elif complexType == 'DB':
                m_d_np = np.power(10.0, raw_pairs[..., 0] / 20.0) * angles
            # pragma: silent exclude
            else:
                raise SignalIntegrityExceptionSParameterFile(
                    name+' has invalid values')
            # pragma: include

        if P == 2:
            m_d_np = m_d_np.transpose((0, 2, 1))

        self.m_d=m_d_np.tolist()
        if Z0 != self.m_Z0:
            for fi in range(len(self.m_d)):
                self.m_d[fi]=ReferenceImpedance(self.m_d[fi],self.m_Z0,Z0)
        self.m_f=GenericFrequencyList(f.tolist())
        # pragma: silent exclude
        if order != None:
            sp=self.PortReorder(order)
            SParameters.__init__(self,sp.m_f,sp.m_d,sp.m_Z0)
        if self.sort_frequencies:
            if not all (np.diff(f) > 0): # frequency list is not in order!
                newf,index = np.unique(f,return_index=True)
                newd=[self.m_d[i] for i in index]
                self.m_f=newf.tolist()
                self.m_d=newd
        # pragma: include
# pragma: silent exclude
if __name__ == "__main__": # pragma: no cover
    runProfiler=True

    if runProfiler:
        import cProfile
        cProfile.run('SParameterFile(\'C:/Users/ppupalai/Downloads/CpX_connector.s256p\')','stats')

        import pstats
        p = pstats.Stats('stats')
        p.strip_dirs().sort_stats('cumulative').print_stats(30)
    else:
        SParameterFile(r"C:\Users\ppupalai\Downloads\CpX_connector.s256p")