"""
results caching
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

import pickle
import hashlib

class ResultsCache(object):
    """
    base class for results caching
    @note derived class must implement the function HashValue(), which determines the hash
    corresponding to a definition.
    """
    def __init__(self,name,filename=None):
        """
        constructor\n
        When a project with a given filename is processed, various results in that project can be cached.
        @param name string name of thing to cache.  Examples are 'SParameters' and 'TransferMatrices'.
        @param filename string base filename of project being processed.
        """
        self.filename=filename
        self.extra='_cached'+name+'.p'
    def CheckCache(self):
        """
        Called to see if the cache has results that can be used instead of processing the result.\n
        It calculates a hash value for the definition of the processing and sees if a _pickle_ containing
        a cached result exists and can be loaded.  Then it checks the times of the cache file and the
        various subcomponents.  Finally, if the hash value matches the cache, meaning they were both
        generated from the same definition, it returns True with it's internal dictionary of the cached
        results initialized.  Otherwise, it returns False.
        @return bool whether the cache can be used.
        """
        self.hash=self.HashValue()
        import os
        if self.filename is None:
            return False
        if not os.path.exists(self.filename+self.extra):
            return False
        if not self.CheckTimes(self.filename+self.extra):
            return False
        try:
            with open(self.filename+self.extra,'rb') as f: tmp_dict = pickle.load(f)
        except:
            return False
        try:
            if tmp_dict['hash'] == self.hash:
                self.__dict__.update(tmp_dict)
                return True
            return False
        except:
            return False
    def CacheResult(self):
        """
        Caches a calculated result
        @return self
        @note that the hash value for the result was generated through a previous call to CheckCache().
        In other words, each cached value must be stored with a hash corresponding to the definition that generated
        the result to be cached (to be checked when an attempt is made to load the cache).  This hash is generated
        automatically when the CheckCache call is made.
        @see CheckCache() 
        """
        if self.filename is None:
            return

        members = [attr for attr in dir(self) if not callable(getattr(self, attr)) and not attr.startswith("__")]
        pickleDict = {x:self.__dict__[x] for x in members}
        with open(self.filename+self.extra, 'wb') as f: pickle.dump(pickleDict, f, 2)
        return self
    def FileTime(self,filename):
        """
        Modification time of a file.
        @param filename string name of file on the disk.
        @note the filename must contain a path that can be directly navigated to from the current directory.
        @return the last modification time of the file.
        """
        import os
        modificationTime = os.path.getmtime(filename)
        return modificationTime
    def CheckTimes(self,cacheFilename):
        """
        Base class function to check times of various components.
        If a project does not have any file components or time dependencies, this can be ignored, otherwise
        the derived class must overload this function.
        @return True (must be overloaded to provide anything other)
        """
        return True

class LinesCache(ResultsCache):
    """
    Caches results calculated based on netlist lines, as used in all of the parser classes.\n
    These parser classes derive from this class and thus inherit the caching capability.
    @see Parsers
    """
    def __init__(self,name,filename=None):
        """
        constructor\n
        When a project with a given filename is processed, various results in that project can be cached.
        @param name string name of thing to cache.  Examples are 'SParameters' and 'TransferMatrices'.
        @param filename string base filename of project being processed.
        """
        ResultsCache.__init__(self,name,filename)
    def HashValue(self):
        """
        Generates the hash for a definition\n
        It is formed by hashing a combination of the netlist lines, the frequencies, and the arguments provided.
        @return integer hash value
        """
        return hashlib.sha256((repr(self.m_lines)+repr(self.m_f)+repr(self.m_args)).encode()).hexdigest()
    def CheckTimes(self,cacheFilename):
        """
        Checks the times for files associated with a netlist.\n
        In netlist devices listed as either file or system devices (i.e. are s-parameter files on the disk) are
        newer than the cache file, then returns False.
        @return False if the cache cannot be used due to file modifications otherwise True
        @note due the potential nonexistance of the files being checked, if any attempt to check them throws an
        exception, then  False is returned.
        """
        import os
        fileList=[]
        from SignalIntegrity.Lib.Helpers.LineSplitter import LineSplitter
        for line in self.m_lines:
            lineList=LineSplitter(line)
            if len(lineList) == 0: # pragma: no cover
                pass
            elif lineList[0] == 'device':
                if len(lineList)>=5:
                    if lineList[3]=='file':
                        fileList.append(lineList[4])
            elif lineList[0] == 'system':
                fileList.append(lineList[2])
        try:
            cacheFileTime = os.path.getmtime(cacheFilename)
        except:
            return False
        for fileName in fileList:
            try:
                modificationTime = os.path.getmtime(fileName)
                if modificationTime > cacheFileTime:
                    return False
            except:
                return False
        return True
