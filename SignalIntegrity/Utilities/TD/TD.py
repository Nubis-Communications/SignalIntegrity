"""
TD.py
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
import numpy as np
import SignalIntegrity.Lib as si
import math
import os
from SignalIntegrity.Lib.ToSI import ToSI,FromSI
from SignalIntegrity.App.SignalIntegrityAppHeadless import SignalIntegrityAppHeadless

class TD_Calculator():
    prog='TD'

    @staticmethod
    def ParseKeywordPairs(args_list=[]):
        import argparse
        from argparse import RawTextHelpFormatter
        parser = argparse.ArgumentParser(
                        prog='TD',
                        description="""Thunder IC measurement calculator

                        Calculates a calibrated thunder IC measurement

The single-ended s-parameter file is read in and converted to the differential mode.

Then a calibrated version is calculated according to the lane number (-ln) specified, and
the ic type specified (-ic) either tia or dvr using the end frequency (-fe) and number of points (-n) specified.

Note, the port ordering the input single-ended s-parameter file is ip,in,op,on,
where i means input, o means output, p means positive, and n means negative.
                        """,
                        epilog='',
                        formatter_class=RawTextHelpFormatter)
        parser.add_argument('filename',nargs='?',default=None, help='s-parameter file name')
        parser.add_argument('-ln','--lane_number',type=int,help='(required) lane number')
        parser.add_argument('-of','--output_file',type=str,help='(optional) output file\n\
no matter how this file is specified, it will have .s2p as an extension')
        parser.add_argument('-ic','--ic_type',type=str,help='(required) ic type, either tia or dvr')
        parser.add_argument('-debug','--debug',action='store_true', help='shows debug information and plots as the computation proceeds')
        parser.add_argument('-p','--profile',action='store_true', help='profiles the software')
        parser.add_argument('-v','--verbose',action='store_true', help='prints information as calculation proceeds.\n\
this should not be set if you are relying on stdout for the return value.')
        parser.add_argument('-fe','--end_frequency',type=float,default=65e9,help='(optional) end frequency to resample to.')
        parser.add_argument('-n','--frequency_points',type=int,default=928,help='(optional) number of frequency points to resample to.')
        parser.add_argument('-cli','--command_line',type=bool,default=False,help=argparse.SUPPRESS)
        args, unknown = parser.parse_known_args(args_list)
        return vars(args),unknown

    def Message(self,message,error=False):
        if self.args['verbose'] or self.args['debug']:
            print(message)
        if error:
            raise Exception(message)

    def Error(self,message):
        self.Message(message,error=True)

    def __init__(self,**kwargs):
        self.cwd = os.getcwd()

        self.result=None

        defaults,_ = self.ParseKeywordPairs()

        self.args=kwargs

        # default any argument not supplied in kwargs
        for key in defaults.keys():
            if not key in kwargs:
                kwargs[key]=defaults[key]

        for key in kwargs:
            if not key in defaults:
                self.Error(f'unknown key: {key}')

        self.args=kwargs


        filename=self.args['filename']
        if filename is None:
            self.Error('file name must be supplied')
        else:
            filename = os.path.abspath(filename)
            self.Message(f'absolute file name is {filename}')
    
        if self.args['ic_type'] is None:
            self.Error('ic type must be supplied, either tia or dvr')
        elif self.args['ic_type'] not in ['tia','dvr']:
            self.Error('ic type must be either tia or dvr')
        else:
            self.Message(f'ic type is {self.args["ic_type"]}')

        # if not self.args['port_reorder'] is None:
        #     try:
        #         sp=sp.PortReorder(self.args['port_reorder'])
        #         self.Message('ports reordered')
        #     except:
        #         self.Error('port reordering failed')

        if self.args['debug']: # pragma: no cover
            debug_args=args={'raw_measurement':filename,
                             'lane_number':self.args['lane_number'],
                             'ic_type':self.args['ic_type'],
                             'EndFrequency':self.args['end_frequency'],
                             'FrequencyPoints':self.args['frequency_points'],
                            }
            if ' ' in debug_args['raw_measurement']:
                debug_args['raw_measurement']='"'+args['raw_measurement'].replace('"','')+'"'
            kwPairs=' '.join([key+' '+str(debug_args[key]) for key in debug_args.keys()])
            pwdArgString=''
            result=os.system('SignalIntegrity "'+os.path.abspath(os.path.join(os.path.dirname(__file__),'Projects','CalculationDiff.si'))+'"'+pwdArgString+' --external '+kwPairs)

        siapp = SignalIntegrityAppHeadless()
        opened = siapp.OpenProjectFile(os.path.join(os.path.dirname(__file__),'Projects','CalculationDiff.si'),
                                       args={'raw_measurement':filename,
                                             'lane_number':self.args['lane_number'],
                                             'ic_type':self.args['ic_type'],
                                             'EndFrequency':self.args['end_frequency'],
                                             'FrequencyPoints':self.args['frequency_points'],
                                             })
        if not opened:
            Error('project file could not be opened')

        try:
            result = siapp.CalculateSParameters()
            self.result = result['s-parameters']
            self.Message('calculation successful')
        except:
            self.Error('calculation failed')
        finally:
            os.chdir(self.cwd)

        output_file = self.args['output_file']
        if self.args['output_file'] is not None:
            try:
                output_file = os.path.abspath(output_file)
                self.result.WriteToFile(output_file)
                self.Message(f'calibrated s-parameters written to {output_file}')
            except:
                self.Error('failed to write output file')

def TD_Main():
    import sys
    args_list=sys.argv[1:]
    args,unknown = TD_Calculator.ParseKeywordPairs(args_list)

    def ConvertStringToList(list_string):
        if list_string is None:
            return list_string
        else:
            try:
                return eval('['+list_string+']')
            except:
                return list_string

    args['command_line']=True
    if args['profile']:
        import cProfile
        profiler=cProfile.Profile()
        profiler.enable()
        try:
            td = TD_Calculator(**args)
            td = td.result
        except:
            td = None
        profiler.disable()
        import pstats
        p = pstats.Stats(profiler)
        p.strip_dirs().sort_stats('cumulative').print_stats(100)
    else:
        try:
            td = TD_Calculator(**args)
            td = td.result
        except:
            td = None

    if td is None:
        td = 'error'
    else:
        td = 'success'

    print(td)
    exit(1 if td == 'error' else 0)

if __name__ == '__main__': # pragma: no cover
    TD_Main()