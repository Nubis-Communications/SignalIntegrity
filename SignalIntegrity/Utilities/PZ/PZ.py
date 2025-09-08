"""
PZ.py
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
from SignalIntegrity.Lib.ToSI import ToSI
import numpy as np
import SignalIntegrity.Lib as si
import math
import os
from SignalIntegrity.Lib.Fit.PoleZero.PoleZeroFitter import PoleZeroLevMar

class PZ_Main(object):
    prog='PZ'
    def PrintProgress(self,iteration):
        iteration_string=str(self.m_fitter.ccm._IterationsTaken)+'  '+str(self.m_fitter.m_mse)
        if self.m_fitter.ccm._IterationsTaken == 2:
            iteration_string+='                             '
        print(iteration_string, end='\r')
    def PlotResult(self,iteration):
        if not self.args['verbose'] and not self.args['debug']:
            return
        self.PrintProgress(iteration)
        if not self.args['debug']:
            return
        import matplotlib.pyplot as plt
        if not self.plotInitialized:
            import platform
            self.windows = platform.system() != 'Linux'
            #self.windows = False
            self.skip_amount = 1
            plt.ion()
            self.fig,self.axs=plt.subplots(2,2)
            if self.windows:
                ax=self.fig.add_subplot(2,2,4,projection='polar')
                ax.set_rscale('log')
                self.axs[1,1]=ax
            self.fig.suptitle('SignalIntegrity Pole/Zero Fitting Dashboard')
            self.fig.canvas.manager.set_window_title('SignalIntegrity PZ Utility')
            import tkinter as tk
            if self.windows:
                import SignalIntegrity.App.Project
                self.img = tk.PhotoImage(file=SignalIntegrity.App.IconsBaseDir+'AppIcon2.gif')
                thismanager = plt.get_current_fig_manager()
                thismanager.window.tk.call('wm', 'iconphoto', thismanager.window._w, self.img)
            plt.subplots_adjust(wspace=0.5, hspace=0.7) # Increase horizontal and vertical spacing
            self.plotInitialized=True
            self.skipper=0
            self.filteredLogLambdaTracker=[]
            self.filteredLogMseTracker=[]
        self.skipper=self.skipper+1
        if self.skipper<self.skip_amount:
            return
        self.skipper=0
        self.skip_amount=min(500.0,self.skip_amount*1.05)

        frequency_unit = ToSI(self.m_fitter.mul,'Hz').split()[-1]

        self.axs[0,0].cla()
        self.axs[0,0].set_title('fit compare')
        self.axs[0,0].set_xlabel(f'frequency ({frequency_unit})')
        self.axs[0,0].set_ylabel('magnitude (dB)')
        self.axs[0,0].plot(self.m_fitter.f,
                     [20.*np.log10(np.abs(v[0])) for v in self.m_fitter.m_y],label='goal')
        self.axs[0,0].plot(self.m_fitter.f,
                     [20.*np.log10(np.abs(v[0])) for v in self.m_fitter.m_Fa],label='fit')
        self.axs[0,0].legend()
        self.axs[0,0].grid(True,'both')

        self.axs[0,1].cla()
        self.axs[0,1].set_title('fit compare')
        self.axs[0,1].set_xlabel('real part')
        self.axs[0,1].set_ylabel('imaginary part')
        self.axs[0,1].plot([v[0].real for v in self.m_fitter.m_y],
                 [v[0].imag for v in self.m_fitter.m_y],label='goal')
        self.axs[0,1].plot([v[0].real for v in self.m_fitter.m_Fa],
                 [v[0].imag for v in self.m_fitter.m_Fa],label='fit')
        self.axs[0,1].legend()
        self.axs[0,1].grid(True,'both')

        self.axs[1,0].cla()
        self.axs[1,0].set_title('lamda and mse')
        #self.axs[1,0].semilogy(self.m_fitter.ccm._FilteredLogDeltaLambdaTracker,label='log Δλ')
        self.axs[1,0].semilogy(self.m_fitter.ccm._FilteredLogDeltaMseTracker,label='log Δmse')
        self.filteredLogLambdaTracker+=[math.pow(10.,v) for v in self.m_fitter.ccm._FilteredLogLambdaTracker[len(self.filteredLogLambdaTracker):]]
        self.filteredLogMseTracker+=[math.pow(10.,v) for v in self.m_fitter.ccm._FilteredLogMseTracker[len(self.filteredLogMseTracker):]]
        self.axs[1,0].semilogy(self.filteredLogLambdaTracker,label='log λ')
        self.axs[1,0].semilogy(self.filteredLogMseTracker,label='log mse')
        self.axs[1,0].set_xlabel('iteration #')
        self.axs[1,0].set_ylabel('log delta')
        self.axs[1,0].grid(True,'both')
        self.axs[1,0].legend()

        results=self.m_fitter.Results()
        num_zero_pairs=self.m_fitter.num_zero_pairs
        num_pole_pairs=self.m_fitter.num_pole_pairs
        zero_mag=[]
        zero_angle=[]
        pole_mag=[]
        pole_angle=[]
        zero_real=[]
        zero_imag=[]
        pole_real=[]
        pole_imag=[]
        for s in range(num_zero_pairs):
            wz=results[s*2+2+0]
            Qz=results[s*2+2+1]
            zeros = np.roots(np.array([1, wz/Qz, wz*wz]))/(2.*np.pi)
            zero_mag.extend([np.abs(z) for z in zeros])
            zero_angle.extend([np.angle(z) for z in zeros])
            zero_real.extend([z.real for z in zeros])
            zero_imag.extend([z.imag for z in zeros])
        for s in range(num_pole_pairs):
            wp=results[(s+num_zero_pairs)*2+2+0]
            Qp=results[(s+num_zero_pairs)*2+2+1]
            poles = np.roots(np.array([1, wp/Qp, wp*wp]))/(2.*np.pi)
            pole_mag.extend([np.abs(p) for p in poles])
            pole_angle.extend([np.angle(p) for p in poles])
            pole_real.extend([p.real for p in poles])
            pole_imag.extend([p.imag for p in poles])

        if self.windows:
            self.axs[1,1].cla()
            self.axs[1,1].set_rscale('log')
            self.axs[1,1].set_title('pole/zero locations')
            self.axs[1,1].plot(zero_angle,zero_mag,marker='o', linestyle='',markersize=10, markerfacecolor='none')
            self.axs[1,1].plot(pole_angle,pole_mag,marker='X', linestyle='',markersize=10)
            self.axs[1,1].grid(True,'both')
        else:
            self.axs[1,1].cla()
            self.axs[1,1].set_title('pole/zero locations')
            log10mz=np.log10(zero_mag)
            log10mp=np.log10(pole_mag)
            max_extents=max(max(log10mz),max(log10mp))
            min_extents=min(min(log10mz),min(log10mp))
            maxmin_extents=max_extents-min_extents
            self.axs[1,1].plot([(np.log10(m)-min_extents)*np.cos(theta) for m,theta in zip(zero_mag,zero_angle)],
                                [(np.log10(m)-min_extents)*np.sin(theta) for m,theta in zip(zero_mag,zero_angle)],
                                marker='o', linestyle='',markersize=10, markerfacecolor='none')
            self.axs[1,1].plot([(np.log10(m)-min_extents)*np.cos(theta) for m,theta in zip(pole_mag,pole_angle)],
                                [(np.log10(m)-min_extents)*np.sin(theta) for m,theta in zip(pole_mag,pole_angle)],
                                marker='X', linestyle='',markersize=10)
            self.axs[1,1].set_xlim(-maxmin_extents,maxmin_extents)
            self.axs[1,1].set_ylim(-maxmin_extents,maxmin_extents)

        self.fig.canvas.draw()
        if iteration == 0:
            print('pausing 5 seconds for you to align the dashboard.', end='\r')
            plt.pause(5)
        plt.pause(0.001)

    def __init__(self):
        import argparse
        from argparse import RawTextHelpFormatter
        parser = argparse.ArgumentParser(
                        prog='PZ',
                        description="""Pole/zero Fitter

                        Fits gain, delay, poles and zeros to response provided.

                        """,
                        epilog='',
                        formatter_class=RawTextHelpFormatter)
        parser.add_argument('filename',nargs='?',default=None, help='name of file for the fit\n\
this could be an:\n\
    s-parameter file (s21 assumed for fit),\n\
    SignalIntegrity frequency response file (not yet supported), or\n\
    a .csv file containing frequency, real part, imaginary part comma separated on each line.')           # positional argument
        parser.add_argument('-ft','--fit_type',type=str,help='(required) type of fit -- either "magnitude" or "complex"')
        parser.add_argument('-debug','--debug',action='store_true', help='shows debug information and plots as the computation proceeds')
        parser.add_argument('-pf','--profile',action='store_true', help='profiles the software')
        parser.add_argument('-v','--verbose',action='store_true', help='prints information as calculation proceeds.\n\
this should not be set if you are relying on stdout for the return value.')
        parser.add_argument('-zp','--zero_pairs',type=int,help='(required) number of zero pairs')
        parser.add_argument('-pp','--pole_pairs',type=int,help='(required) number of pole pairs')
        parser.add_argument('-gf','--guess_file',type=str,help='(optional) file containing initial guess\n\
this file can be an output file (see --output_file), in which case, the raw fit results are\n\
extracted and used as the starting guess.  this file must be a .json file with the .json\n\
extension.  otherwise, it is assumed to be a text file produced in debug mode (see --debug),\n\
which is usually called test_result.txt.')
        parser.add_argument('-of','--output_file',type=str,help='(optional) output file\n\
no matter how this file is specified, it will have the .json extension added to it.')
        parser.add_argument('-fe','--end_frequency',type=float,help='(optional) end frequency to resample to\n\
if this is specified, then the number of frequency points must also be specified\n\
(see --frequency_points).')
        parser.add_argument('-n','--frequency_points',type=int,help='(optional) number of frequency points to resample to\n\
if this is specified, then the end frequency must also be specified (see --end_frequency).\n\
it\'s a good idea to use as few frequency points as needed to improve speed.')
        parser.add_argument('-mind','--min_delay',type=float,default=0,help='(optional) minimum delay - defaults to 0')
        parser.add_argument('-maxd','--max_delay',type=float,help='(optional) maximum delay')
        parser.add_argument('-maxq','--max_q',type=float,default=5,help='(optional) maximum Q - defaults to 5\n\
limiting the maximum Q forces the result to be at least reasonably behaved and improves\n\
the chances of a successful fit.')
        parser.add_argument('-id','--initial_delay',type=float,default=0,help='(optional) initial delay - defaults to 0\n\
it is highly recommended to supply the best guess at the delay for improving the success\n\
of the fit and to limit the delay range (see --max_delay and --min_delay).')
        parser.add_argument('-i','--iterations',type=str,default='medium',help='(optional) iterations (short,medium,long,infinite) - defaults to medium\n\
normally fit convergence should not end with the expiration of iterations.  if medium\n\
iterations is used, iterations expire after about a minute.  long increases this to\n\
several minutes max.')
        parser.add_argument('-pr','--precision',type=str,default='medium',help='(optional) precision for fit (low,medium,high,super)\n\
this is the main way of controlling how convergence is determined and it determines how little\n\
the error is decreasing before giving up.  low will be very quick, but will result in\n\
sub-optimal fits.  medium is usually good enough, while high gives a very good fit.  super is\n\
used for extremely good fits, but takes longer (possibly several minutes).')
        parser.add_argument('-rz','--real_zeros',action='store_true', help='(optional) restrict zeros to be real\n\
often the solution can only have real zeros.')
        parser.add_argument('-lz','--lhp_zeros',action='store_true', help='(optional) restrict zeros to the LHP\n\
left-half plane zeros enforces a minimum phase solution.')
        parser.add_argument('-vt','--voltage_transfer_function',action='store_true',help='(optional, applies only to s-parameters) fit to the voltage transfer function\n\
when s-parameters are used, the default is to fit s21, which is the ratio of output\n\
wave to incident wave. this is not the voltage transfer function, which is s21/(1+s11).')
        parser.add_argument('-xg','--fix_gain',action='store_true',help='(optional) fix the dc gain.\n\
choosing this option fixes the dc point to the first frequency point, otherwise, the dc gain is part of the fit.')
        parser.add_argument('-xdly','--fix_delay',action='store_true',help='(optional) fix the delay value.\n\
choosing this option fixes the delay value to 0, if -id not specified or what is specified by -id, otherwise,\n\
the delay is part of the fit.')
        parser.add_argument('-r','--reference_impedance',type=float,help='(optional, applies only to s-parameters) specify another reference impedance to use')
        parser.add_argument('-maxi','--max_iterations',type=int,help=argparse.SUPPRESS)
        parser.add_argument('-mseu','--mse_unchanging_threshold',type=float,help=argparse.SUPPRESS)
        parser.add_argument('-il','--initial_lambda',type=float,default=1000.,help=argparse.SUPPRESS)
        parser.add_argument('-lm','--lambda_multiplier',type=float,default=2.,help=argparse.SUPPRESS)
        parser.add_argument('-tol','--tolerance',type=float,default=1e-6,help=argparse.SUPPRESS)
        parser.add_argument('-mfm','--max_frequency_multiplier',type=float,default=5,help=argparse.SUPPRESS)
        args, unknown = parser.parse_known_args()

        #self.args=dict(zip(unknown[0::2],unknown[1::2]))

        def Message(message,error=False):
            if args.verbose or args.debug:
                print(message)
            if error:
                print('error')
                exit(1)

        def Error(message):
            Message(message,error=True)

        import sys
        if len(sys.argv)==1:
            # parser.print_help()
            # parser.exit()
            Error('file name and keyword values must be specified')

        if len(unknown):
            # parser.print_usage()
            # parser.exit()
            Error(f'unknown keyword {unknown[0]} encountered')

        self.args=vars(args)

        if self.args['max_iterations'] == None:
            iterations_dict = {'short':10000,
                               'medium':50000,
                               'long':200000,
                               'infinite':1000000000000}
            try:
                self.args['max_iterations']=iterations_dict[self.args['iterations']]
                Message('iterations are: '+self.args['iterations'])
            except KeyError:
                Error('iterations must be short, medium, or long.  you specified: '+self.args['iterations'])
        else:
            Message('max iterations set to: '+str(self.args['max_iterations']))

        if self.args['mse_unchanging_threshold'] == None:
            mse_unchanging_dict = {'low':1e-5,
                               'medium':1e-6,
                               'high':1e-7,
                               'super':1e-8}
            try:
                self.args['mse_unchanging_threshold']=mse_unchanging_dict[self.args['precision']]
                Message('precision is: '+self.args['precision'])
            except KeyError:
                Error('precision must be low, medium, high, or super.  you specified: '+self.args['precision'])
        else:
            Message('mse unchanging threshold set to: '+str(self.args['mse_unchanging_threshold']))

        filename=self.args['filename']

        ext=os.path.splitext(filename)[-1]
        if ext.lower() == '.csv':
            # .csv file
            try:
                with open(filename,'rt') as f:
                    lines = f.readlines()
                f=[]; r=[]
                for line in lines:
                    tokens=line.strip().split(',')
                    f.append(float(tokens[0]))
                    r.append(float(tokens[1])+1j*float(tokens[2]))
                fr=si.fd.FrequencyResponse(f,r)
                Message(os.path.split(filename)[-1] +' read')
                if self.args['reference_impedance'] != None:
                    Message('reference impedance (-r) ignored')
                if self.args['voltage_transfer_function']:
                    Message('voltage transfer function (-vt) ignored')
            except:
                Error('file: '+filename+' could not be opened')
        elif len(ext)>=4:
            if ext[0:2].lower() == '.s' and ext[-1].lower() == 'p' and ext[2:-1].isnumeric():
                # it's an s-parameter file
                try:
                    sp=si.sp.SParameterFile(filename)
                    if self.args['reference_impedance'] != None:
                        Message(f"reference impedance specified as {ToSI(self.args['reference_impedance'],'ohm')}")
                        sp.SetReferenceImpedance(self.args['reference_impedance'])
                    else:
                        Message(f"no reference impedance specified so the reference impedance of {ToSI(sp.m_Z0,'ohm')} in the file will be used")
                    fr=sp.FrequencyResponse(2,1)
                    if self.args['voltage_transfer_function']:
                        Message('fit will be to the voltage transfer function')
                        s11=sp.FrequencyResponse(1,1)
                        for n in range(len(fr)):
                            fr[n]=fr[n]/(1+s11[n])
                    else:
                        Message('fit will be to s21, which is not the voltage transfer function')
                    Message(os.path.split(filename)[-1] +' read')
                except:
                    Error('file: '+filename+' could not be opened')
            else:
                Error('only .csv and s-parameter files supported currently')
        if self.args['end_frequency'] != None or self.args['frequency_points'] != None:
            if self.args['end_frequency'] == None:
                Error('if number of frequency points specified, then end frequency must be specified')
            if self.args['frequency_points'] == None:
                Error('if end frequency is specified, then number of frequency points must be specified')
            fe=self.args['end_frequency']; n = self.args['frequency_points']
            fr=fr.Resample(si.fd.EvenlySpacedFrequencyList(fe,n))
            Message(f"frequency response resampled to end frequency: {ToSI(fe,'Hz')} with: {n} points")

        guess=None
        guess_file = self.args['guess_file']
        if guess_file != None:
            if os.path.splitext(guess_file)[-1].lower() == '.json':
                import json
                try:
                    with open(guess_file,'r') as f:
                        gf=json.load(f)
                        guess=gf['raw']
                        self.args['zero_pairs'] = gf['zero pair']['number of']
                        self.args['pole_pairs'] = gf['pole pair']['number of']

                        Message('guess file: '+filename+' read')
                        Message('zeros are '+str(self.args['zero_pairs'])+' and poles are '+str(self.args['pole_pairs'])+' from guess file')
                except:
                    Error('guess file: '+filename+' could not be opened')
            else:
                try:
                    gf = PoleZeroLevMar.ReadResultsFile(guess_file)
                    Message('guess file: '+os.path.split(filename)[-1]+' read')

                    self.args['zero_pairs'] = gf[0]
                    self.args['pole_pairs'] = gf[1]
                    guess = gf[2:]
                    Message('zeros are '+str(gf[0])+' and poles are '+str(gf[1])+' from guess file')
                except:
                    Error('guess file: '+filename+' could not be opened')

        num_poles = self.args['pole_pairs']
        num_zeros = self.args['zero_pairs']

        if num_zeros == None:
            Error('number of zero pairs must be specified (-zp)')

        if num_poles == None:
            Error('number of pole pairs must be specified (-pp)')

        if guess == None:
            Message('zeros are '+str(num_zeros)+' and poles are '+str(num_poles))

        Message(f"initial delay: {ToSI(self.args['initial_delay'],'s')}")
        Message(f"minimum delay allowed: {ToSI(self.args['min_delay'],'s')}")
        if self.args['max_delay'] == None:
            Message('there is no limit on maximum delay')
        else:
            Message(f"maximum delay allowed: {ToSI(self.args['max_delay'],'s')}")

        if self.args['fix_gain']:
            Message('gain is fixed')
        else:
            Message('gain is a free variable in the fit')

        if not self.args['fix_delay'] and self.args['fit_type'] == 'magnitude':
            self.args['fix_delay'] = True
            Message('delay is always fixed for magnitude fits')
        else:
            if self.args['fix_delay']:
                Message('delay is fixed')
            else:
                Message('delay is a free variable in the fit')

        Message("poles are always restricted to LHP")
        if self.args['lhp_zeros']:
            Message("zeros are restricted to LHP")
        else:
            Message('no restriction on LHP or RHP on zeros')

        if self.args['real_zeros']:
            Message('zeros are restricted to be real')
        else:
            Message('zeros are allowed to be complex')

        Message(f"maximum Q is {self.args['max_q']}")

        fit_type=self.args['fit_type']
        if fit_type == 'magnitude':
            Message('fit type is: magnitude')
        elif fit_type == 'complex':
            Message('fit type is: complex')
        else:
            Error('fit type must be either "magnitude" or "complex"')

        default_initial_lambda = parser.get_default('initial_lambda')
        initial_lambda=self.args['initial_lambda']
        if default_initial_lambda != initial_lambda:
            Message(f'initial λ: {initial_lambda} as opposed to default of: {default_initial_lambda}')

        default_lambda_multiplier = parser.get_default('lambda_multiplier')
        lambda_multiplier=self.args['lambda_multiplier']
        if default_lambda_multiplier != lambda_multiplier:
            Message(f'λ multiplier: {lambda_multiplier} as opposed to default of: {default_lambda_multiplier}')

        default_tolerance = parser.get_default('tolerance')
        tolerance=self.args['tolerance']
        if default_tolerance != tolerance:
            Message(f'tolerance is: {tolerance} as opposed to default of: {default_tolerance}')

        default_max_frequency_multiplier = parser.get_default('max_frequency_multiplier')
        max_frequency_multiplier=self.args['max_frequency_multiplier']
        if default_max_frequency_multiplier != max_frequency_multiplier:
            Message(f'max_frequency_multiplier is: {max_frequency_multiplier} as opposed to default of: {default_max_frequency_multiplier}')

        import time
        from datetime import datetime
        start_time = time.time()
        self.m_fitter=PoleZeroLevMar(fr,num_zeros,num_poles,
                                     guess=guess,
                                     min_delay=self.args['min_delay'],
                                     max_delay=self.args['max_delay'],
                                     max_Q=self.args['max_q'],
                                     initial_delay=self.args['initial_delay'],
                                     max_iterations=self.args['max_iterations'],
                                     mse_unchanging_threshold=self.args['mse_unchanging_threshold'],
                                     LHP_zeros=self.args['lhp_zeros'],
                                     real_zeros=self.args['real_zeros'],
                                     fit_type=self.args['fit_type'],
                                     initial_lambda=self.args['initial_lambda'],
                                     lambda_multiplier=self.args['lambda_multiplier'],
                                     tolerance=self.args['tolerance'],
                                     max_frequency_multiplier=self.args['max_frequency_multiplier'],
                                     fix_delay=self.args['fix_delay'],
                                     fix_gain=self.args['fix_gain'],
                                     callback=self.PlotResult)
        self.plotInitialized=False

        if self.args['profile']:
            import cProfile
            profiler=cProfile.Profile()
            profiler.enable()
            self.m_fitter.Solve()
            profiler.disable()
            import pstats
            p = pstats.Stats(profiler)
            p.strip_dirs().sort_stats('cumulative').print_stats(100)
        else:
            self.m_fitter.Solve()

        Message('convergence: '+str(self.m_fitter.ccm.why))
        Message('iterations: '+str(self.m_fitter.ccm._IterationsTaken)+' mse:'+str(self.m_fitter.ccm._Mse))

        end_time = time.time()
        elapsed_time=end_time-start_time
        if self.args['debug'] or self.args['verbose']:
            self.m_fitter.PrintResults()
        if self.args['debug']:
            self.m_fitter.WriteResultsToFile('test_result.txt').WriteGoalToFile('test_goal.txt')

        if self.args['debug']:
            # make an s-parameter file out of this result
            try:
                from SignalIntegrity.Lib.Fit.PoleZero.QuadraticComplex import TransferFunctionComplexVectorized
                sp=si.sp.SParameterFile(filename)
                if self.args['reference_impedance'] != None:
                    sp.SetReferenceImpedance(self.args['reference_impedance'])
                f=sp.m_f
                new_s21=TransferFunctionComplexVectorized(np.array(f)*2.*np.pi,
                                                      np.array(self.m_fitter.Results()),
                                                      num_zeros,
                                                      num_poles,
                                                      self.args['fix_gain'],
                                                      self.args['fix_delay']
                                                      ).H
                if self.args['voltage_transfer_function']:
                    # convert back to s11
                    s11=sp.FrequencyResponse(1,1)
                    for n in range(len(f)):
                        sp.m_d[n][1][0] = new_s21[n]*(1+s11[n])
                else:
                    for n in range(len(f)):
                        sp.m_d[n][1][0] = new_s21[n]
                sp.WriteToFile('debug')
            except:
                pass
        Message(f'elapsed time: {elapsed_time} s')

        if self.args['output_file']:
            self.args['output_file']=os.path.splitext(self.args['output_file'])[0]+'.json'
            num_zero_pairs=self.m_fitter.num_zero_pairs
            num_pole_pairs=self.m_fitter.num_pole_pairs
            raw_results=self.m_fitter.Results()
            results={}
            results['raw']=raw_results
            results['configuration']=self.args
            results['convergence']={'iterations':self.m_fitter.ccm._IterationsTaken,
                                    'mse':self.m_fitter.ccm._Mse,
                                    'time':elapsed_time,
                                    'completed':datetime.now().strftime("%m/%d/%Y %H:%M:%S"),
                                    'why stopped':self.m_fitter.ccm.why,
                                    'frequency multiplier':self.m_fitter.mul}
            fit_result=self.m_fitter.fF(self.m_fitter.m_a).reshape(-1).tolist()
            results['response']={'frequency':fr.Frequencies(),
                                 'goal':{'magnitude':fr.Values('mag'),'phase':fr.Values('deg')},
                                 'result':{'magnitude':[np.abs(v) for v in fit_result],
                                           'phase':[np.angle(v)*180/np.pi for v in fit_result]}}
            results['gain']={'value':raw_results[0],'dB':20*math.log10(np.abs(raw_results[0]))}
            results['delay']={'value':raw_results[1]}
            results['pole pair']={'number of':num_pole_pairs,'list':[]}
            results['pole']={'number of':num_pole_pairs*2,'list':[]}
            results['zero pair']={'number of':num_zero_pairs,'list':[]}
            results['zero']={'number of':num_zero_pairs*2,'list':[]}
            for s in range(num_zero_pairs):
                wz=raw_results[s*2+2+0]
                Qz=raw_results[s*2+2+1]
                zeta=1/(2.*Qz)
                if zeta < 1./np.sqrt(2):
                    try:
                        wr=np.sqrt(1-2*(zeta*zeta))*wz
                    except (RuntimeWarning,RuntimeError):
                        wr=0
                    if np.isnan(wr):
                        wr=0
                else:
                    wr=0
                peak_dB = 0 if wr==0 else 20*np.log10(abs(wz*wz/((wz*wz-wr*wr)+1j*wr*wz/Qz)))
                zeros = np.roots(np.array([1, wz/Qz, wz*wz]))
                zero_mag = [np.abs(z) for z in zeros]
                zero_angle = [np.angle(z) for z in zeros]
                zero_real = [z.real for z in zeros]
                zero_imag = [z.imag for z in zeros]
                results['zero pair']['list'].append({'w0':wz,
                                                     'Q':Qz,
                                                     'zeta':zeta,
                                                     'f0':wz/(2.*np.pi),
                                                     'wr':wr,
                                                     'fr':wr/(2.*np.pi),
                                                     'peakdB':peak_dB})
                for z in range(2):
                    results['zero']['list'].append({#'complex':zeros[z],
                                       'real':zero_real[z],
                                       'imag':zero_imag[z],
                                       'mag':zero_mag[z],
                                       'angle':{'rad':zero_angle[z],
                                                'deg':zero_angle[z]*180./np.pi}})
            for s in range(num_pole_pairs):
                wp=raw_results[(s+num_zero_pairs)*2+2+0]
                Qp=raw_results[(s+num_zero_pairs)*2+2+1]
                zeta=1/(2.*Qp)
                if zeta < 1./np.sqrt(2):
                    try:
                        wr=np.sqrt(1-2*(zeta*zeta))*wp
                    except (RuntimeWarning,RuntimeError):
                        wr=0
                    if np.isnan(wr):
                        wr=0
                else:
                    wr=0
                peak_dB = 0 if wr==0 else 20*np.log10(abs(wp*wp/((wp*wp-wr*wr)+1j*wr*wp/Qp)))
                poles = np.roots(np.array([1, wp/Qp, wp*wp]))
                pole_mag=[np.abs(p) for p in poles]
                pole_angle=[np.angle(p) for p in poles]
                pole_real=[p.real for p in poles]
                pole_imag=[p.imag for p in poles]
                results['pole pair']['list'].append({'w0':wp,
                                                     'Q':Qp,
                                                     'zeta':zeta,
                                                     'f0':wp/(2.*np.pi),
                                                     'wr':wr,
                                                     'fr':wr/(2.*np.pi),
                                                     'peakdB':peak_dB})
                for p in range(2):
                    results['pole']['list'].append({#'complex':poles[p],
                                       'real':pole_real[p],
                                       'imag':pole_imag[p],
                                       'mag':pole_mag[p],
                                       'angle':{'rad':pole_angle[p],
                                                'deg':pole_angle[p]*180./np.pi}})
            import json
            with open(self.args['output_file'],'w') as f:
                json.dump(results,f,indent=4)
        print('done')
        if self.args['debug']:
            input("Press Enter to continue...")
if __name__ == '__main__': # pragma: no cover
    PZ_Main()