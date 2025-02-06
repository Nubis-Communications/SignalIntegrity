"""
results caching
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

import pickle
import hashlib

class ResultsCache(object):
    """base class for results caching
    @note derived class must implement the function HashValue(), which determines the hash
    corresponding to a definition.
    """
    files_to_keep = 1
    logging=False
    def __init__(self,name,filename=None):
        """constructor\n
        When a project with a given filename is processed, various results in that project can be cached.
        @param name string name of thing to cache.  Examples are 'SParameters' and 'TransferMatrices'.
        @param filename string base filename of project being processed.
        """
        self.filename=filename
        self.extra='_cached'+name
        self.extension='.p'
    def _FileName(self,wildcard=False,files_to_keep_override=None):
        files_to_keep = self.files_to_keep
        if not files_to_keep_override is None:
            files_to_keep = files_to_keep_override
        if wildcard:
            filename = self.filename+self.extra+'*'+self.extension
        else:
            if files_to_keep != 1:
                filename = self.filename+self.extra+'_'+str(self.hash)+self.extension
            else:
                filename = self.filename+self.extra+self.extension
        return filename
    def HashValue(self,stuffToHash=''):
        """ Generates the hash for a definition\n
        @param stuffToHash repr of stuff to hash
        @remark derived classes should override this method and call the base class HashValue with their stuff added
        @return integer hash value
        """
        return hashlib.sha256(stuffToHash.encode()).hexdigest()
    def CheckCache(self):
        """Called to see if the cache has results that can be used instead of processing the result.\n
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
            if self.logging: print('no filename')
            return False
        filenames=[self._FileName(files_to_keep_override=1),self._FileName(files_to_keep_override=2)]
        for filename in filenames:
            if not os.path.exists(filename):
                if self.logging: print(filename+' does not exist')
                continue
            if not self.CheckTimes(filename):
                if self.logging: print(filename + ' older')
                continue
            try:
                with open(filename,'rb') as f:
                    hash = pickle.load(f)
                    if hash == self.hash:
                        tmp_dict = pickle.load(f)
                        self.__dict__.update(tmp_dict)
                        if self.logging: print(filename + ' passes cache check')
                        if filename == self._FileName(files_to_keep_override=2) and self.files_to_keep == 1:
                            # this means that the file found is the one for multi-cache, but ideally, it's the one
                            # for single file cache.  Write out the single file cache, so that in the future, it's found
                            # in the single file cache.
                            self.CacheResult()
                        return True
                    else:
                        if self.logging: # pragma: no cover
                            print(filename+' hash incorrect')
                            print(filename+' hash value = '+hash)
                            print('expecting: '+self.hash)
                        continue
            except:
                if self.logging: print(filename+' could not be unpickled')
                continue
        return False
    def CacheResult(self,keeperList=None):
        """Caches a calculated result
        @param keeperList (optional, defaults to None) list of members to keep in the cache
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

        if not keeperList == None:
            keeperList.append('hash')
            members=[attr for attr in members if attr in keeperList]

        try:
            pickleDict = {x:self.__dict__[x] for x in members}
        except KeyError:
            pickleDict = {}
            for x in members:
                try:
                    pickleDict[x] = self.__dict__[x]
                except KeyError:
                    pass

        # keep only a certain number of files
        if self.files_to_keep != 1:
            import glob
            import os
            file_list = glob.glob(self._FileName(wildcard=True))
            file_list.sort(key=os.path.getmtime, reverse=True)  # Sort by modification time, newest first
            number_of_files = len(file_list)
            number_to_delete = max(0, number_of_files - self.files_to_keep + 1)

            if self.logging:
                print(f'while caching, found {number_of_files} cache files, can keep {self.files_to_keep}, deleting {number_to_delete} files.')

            for num in range(number_to_delete):
                os.remove(file_list[num])

        with open(self._FileName(), 'wb') as f:
            if self.logging: print('caching '+self._FileName()+' with hash value:'+pickleDict['hash'])
            pickle.dump(pickleDict['hash'], f, 2)
            pickle.dump(pickleDict, f, 2)

        return self
    def CheckTimes(self,cacheFilename):
        """Base class function to check times of various components.
        If a project does not have any file components or time dependencies, this can be ignored, otherwise
        the derived class must overload this function.
        @return True (must be overloaded to provide anything other)
        """
        return True

class LinesCache(ResultsCache):
    """Caches results calculated based on netlist lines, as used in all of the parser classes.\n
    These parser classes derive from this class and thus inherit the caching capability.
    @see Parsers
    """
    def __init__(self,name,filename=None):
        """constructor\n
        When a project with a given filename is processed, various results in that project can be cached.
        @param name string name of thing to cache.  Examples are 'SParameters' and 'TransferMatrices'.
        @param filename string base filename of project being processed.
        """
        ResultsCache.__init__(self,name,filename)
    def HashValue(self,stuffToHash=''):
        """Generates the hash for a definition\n
        @param stuffToHash repr of stuff to hash
        It is formed by hashing a combination of the netlist lines, the frequencies, and the arguments provided.
        @remark derived classes should override this method and call the base class HashValue with their stuff added
        @return integer hash value
        """
        def ReorderLexicographically(lines):
            # lexicographical reordering of the netlist helps ensure that caching of the
            # netlist line remains predictable
            linesSplit=[line.split(' ') for line in lines]
            linesKeyValue=[]
            for lineList in linesSplit:
                if len(lineList)>0:
                    key=lineList[0]
                    value=' '.join(lineList[1:])
                    if key == 'var':
                        try:
                            beginning_value = value.split(' ')[1]
                            if beginning_value[0] == '/' or beginning_value[1] == '/' or beginning_value[1:3] ==':/' or beginning_value[2:4]==':/': # assume this is a file
                                # convert to relative path
                                import os
                                current_path=os.getcwd()
                                relative_path=os.path.relpath(os.path.abspath(' '.join(value.replace("'","").split(' ')[1:])),current_path)
                                value=value.split(' ')[0]+' '+relative_path
                        except:
                            pass
                    linesKeyValue.append((key,value))
            keyList=sorted(list(set([key for key,_ in linesKeyValue])))
            keyLineList={key:[] for key in keyList}
            for key,value in linesKeyValue:
                if not (key == 'var' and 'nocache' in value):
                    keyLineList[key].append(value)
            reorderedText=[]
            for key in keyLineList.keys():
                linelist=sorted(keyLineList[key])
                for line in linelist: reorderedText.append(key+' '+line)
            return reorderedText
        hashed=repr(ReorderLexicographically(self.m_lines))+repr(self.m_f)+repr(self.m_Z0)+repr(self.m_args)+stuffToHash
        if self.logging:
            with open(self.filename+'_hash.txt','w') as f:
                f.write((repr(ReorderLexicographically(self.m_lines))+repr(self.m_f)+repr(self.m_Z0)+repr(self.m_args)+stuffToHash).replace(' ','\n'))
        return ResultsCache.HashValue(self,hashed)
    def CheckTimes(self,cacheFilename):
        """Checks the times for files associated with a netlist.\n
        In netlist devices listed as either file or system devices (i.e. are s-parameter files on the disk) are
        newer than the cache file, then returns False.
        @return False if the cache cannot be used due to file modifications otherwise True
        @note due the potential nonexistance of the files being checked, if any attempt to check them throws an
        exception, then  False is returned.
        """
        import os
        fileList={}
        from SignalIntegrity.Lib.Helpers.LineSplitter import LineSplitter
        try:
            for line in self.m_lines:
                lineList=LineSplitter(line)
                self.ProcessVariables(lineList)
                lineList=self.ReplaceArgs(lineList)
                if len(lineList) == 0: # pragma: no cover
                    pass
                elif lineList[0] == 'device':
                    # todo:  this is wrong - must parse tokens
                    if len(lineList)>=5:
                        if lineList[3]=='file':
                            fileList[lineList[4]]={key:value
                                                   for key,value in [(lineList[k],lineList[k+1])
                                                                     for k in range(5,len(lineList),2)]
                                                   if key not in ['reorder']}
                        elif lineList[3] == 'networkanalyzer':
                            fileList[lineList[5]]={key:value
                                                   for key,value in [(lineList[k],lineList[k+1])
                                                                     for k in range(8,len(lineList),2)]
                                                   if key not in ['et','pl','cd']}
                            fileList[lineList[7]]=fileList[lineList[5]]
                        elif lineList[3]=='networkanalyzermodel':
                            # I don't think this can ever happen
                            fileList[lineList[5]]={key:value
                                                   for key,value in [(lineList[k],lineList[k+1])
                                                                     for k in range(6,len(lineList),2)]}
                        elif lineList[3] == 'parallel':
                            fileList[lineList[5]]={key:value
                                                   for key,value in [(lineList[k],lineList[k+1])
                                                                     for k in range(6,len(lineList),2)]
                                                   if key not in ['sect']}
                        elif lineList[3] == 'series':
                            fileList[lineList[5]]={key:value
                                                   for key,value in [(lineList[k],lineList[k+1])
                                                                     for k in range(6,len(lineList),2)]
                                                   if key not in ['sect','lp','rp']}
                        elif lineList[3] == 'rlgcfit':
                            fileList[lineList[5]]={key:value
                                                   for key,value in [(lineList[k],lineList[k+1])
                                                                     for k in range(6,len(lineList),2)]
                                                   if key not in ['scale']}
                elif lineList[0] == 'calibration':
                    fileList[lineList[3]]={key:value
                                           for key,value in [(lineList[k],lineList[k+1])
                                                             for k in range(4,len(lineList),2)]
                                           if key not in ['std','pn','opn','ct']}
                    if '.' in lineList[5]:
                        fileList[lineList[5]]=fileList[lineList[3]]
                elif lineList[0] == 'system':
                    fileList[lineList[2]]={key:value
                                           for key,value in [(lineList[k],lineList[k+1])
                                                             for k in range(3,len(lineList),2)]}
        except IndexError:
            return False
        try:
            cacheFileTime = os.path.getmtime(cacheFilename)
        except:
            return False
        modificationTimeDict=[]
        for fileName in fileList.keys():
            try:
                from SignalIntegrity.App.SignalIntegrityAppHeadless import ProjectModificationTime
                modificationTimeDict = ProjectModificationTime(modificationTimeDict,fileName,fileList[fileName])
                if modificationTimeDict == None:
                    return False
            except:
                return False
        if len(modificationTimeDict)==0:
            return True
        if max([file['time'] for file in modificationTimeDict]) > cacheFileTime:
            return False
        return True
