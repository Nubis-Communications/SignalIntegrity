"""
Result.py
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

from SignalIntegrity.Lib.Exception import SignalIntegrityException

class Result(dict):
    """result dictionary for signal integrity results
    """
    def __init__(self,result_type,result_dict={}):
        """initializes the result dictionary
        @param dict results dictionary
        """
        if result_type not in ['simulation',
                        'virtual probe',
                        's-parameters',
                        'de-embed',
                        'network analyzer',
                        'error terms']:
            raise SignalIntegrityException('result type incorrect')
        if result_dict is None:
            dict.__init__(self,{})
        else:
            result_dict['type']=result_type
            dict.__init__(self,result_dict)
    def _all_defined(self,keys):
        return all([item in self for item in keys])
    def _return_them(self,keys):
        return tuple([self[key] for key in keys])
    def Legacy(self):
        """puts the results in a tuple in the legacy form
        @deprecated: This will be removed at some point in the future
        """
        import warnings
        warnings.warn('this function is deprecated - use dictionary result instead')
        if self == {}:
            return None
        result_type = self['type']
        if result_type in ['simulation','virtual probe']:
            keyword_list = ['source names','output waveform labels',
                            'transfer matrices','output waveforms',
                            'eye diagram labels','eye diagrams']
            if self._all_defined(keyword_list):
                return self._return_them(keyword_list)
            keyword_list.remove('eye diagram labels')
            keyword_list.remove('eye diagrams')
            if self._all_defined(keyword_list):
                return self._return_them(keyword_list)
            keyword_list.remove('output waveforms')
            if self._all_defined(keyword_list):
                return self._return_them(keyword_list)
        elif result_type == 's-parameters':
            keyword_list = ['s-parameters','file names']
            if self._all_defined(keyword_list):
                return self._return_them(keyword_list)
        elif result_type == 'de-embed':
            keyword_list = ['unknown names','s-parameters']
            if self._all_defined(keyword_list):
                return self._return_them(keyword_list)
        elif result_type == 'network analyzer':
            keyword_list=['source names',
                          'output waveform labels',
                          'transfer matrices',
                          'output waveforms']
            if 's-parameters' in self:
                return self['s-parameters']
            elif self._all_defined(keyword_list):
                return self._return_them(keyword_list)
        elif result_type == 'error terms':
            keyword_list=['error terms','file names']
            if self._all_defined(keyword_list):
                return self._return_them(keyword_list)
        return None
    def OutputWaveform(self,name):
        """returns an output waveform
        @param name string name of output waveform to return
        @return instance of class Waveform
        """
        return self['output waveforms'][self['output waveform labels'].index(name)]
    def FrequencyResponse(self,from_name,to_name):
        """returns a frequency response
        @param from_name string name of source of frequency response
        @param to_name string name of output of frequency response
        @return instance of class FrequencyResponse
        """
        return self['transfer matrices'].FrequencyResponse(
            self['output waveform labels'].index(to_name)+1,
            self['source names'.index(from_name)+1])