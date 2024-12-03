"""
ERL.py
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
from SignalIntegrity.Lib.ToSI import FromSI,ToSI
from SignalIntegrity.App.SignalIntegrityAppHeadless import SignalIntegrityAppHeadless
import numpy as np
import SignalIntegrity.Lib as si
import math
import os

def ERL(filename,args,debug=False,verbose=False):
    """computes effective return loss (ERL) mostly according to IEEE COM
    @param filename absolute path of four-port s-parameter file
    @param args dictionary of arguments for the ERL calculation (defined below).
    @param debug boolean (optional, defaults to False) whether to show debug information.
    @param verbose boolean (optional, defaults to False) whether to show intermediate output messages. 
    The valid arguments are:

        |key           | units |required    |description                                                          |
        |:------------:|:----:|:-----------:|:------------------------------------------------------------------- |
        | port_reorder | --   | no, 1,2,3,4 | port ordering of 1p,1n,2p,2n of the .s4p file (default is 1,2,3,4). |
        | T_r          | s    | yes         | transition time associated with a pulse                             |
        | beta_x       | Hz   | yes         | incremental available signal loss factor                            |
        | rho_x        | --   | yes         | permitted reflection from a transmission line external to the DUT   |
        | N            | UI   | yes         | length of reflection signal                                         |
        | N_bx         | UI   | yes         | equalizer length associated with reflection signal                  |
        | Z0           | ohm  | no 100      | intended differential-mode characteristic impedance                 |
        | T_fx         | s    | no 0        | time-gated propagation delay                                        |
        | f_b          | Baud | yes         | Baud rate                                                           |
        | DER_0        | --   | yes         | target detector error ratio                                         |
    """
    class ERL_Exception(si.SignalIntegrityException):
        def __init__(self,message):
            si.SignalIntegrityException.__init__(self,'ERL',message)
            if debug or verbose:
                print(message)

    path=os.getcwd()

    if debug or verbose:
        print(args)

    required_keywords = ['T_r','beta_x','rho_x','N','N_bx','f_b','DER_0']
    for key in required_keywords:
        if key not in args:
            raise ERL_Exception(f'error: {key} must be specified')

    port_reorder = '1,2,3,4' if 'port_reorder' not in args else args['port_reorder']
    T_r = args['T_r']
    beta_x = args['beta_x']
    rho_x = args['rho_x']
    N = args['N']
    N_bx = args['N_bx']
    Z0 = 100.0 if 'Z0' not in args else args['Z0']
    T_fx = 0 if 'T_fx' not in args else args['T_fx']
    f_b = args['f_b']
    DER_0 = args['DER_0']
    if debug or verbose:
        print(f"filename = {filename}")
        print(f"port_reorder = {port_reorder}")
        print(f"T_r = {ToSI(T_r,'s')}")
        print(f"beta_x = {ToSI(beta_x,'Hz')}")
        print(f"rho_x = {ToSI(rho_x,None)}")
        print(f"N = {ToSI(N,'UI')}")
        print(f"N_bx = {ToSI(N_bx,'UI')}")
        print(f"Z0 = {ToSI(Z0,'ohm')}")
        print(f"T_fx = {ToSI(T_fx,'s')}")
        print(f"f_b = {ToSI(f_b,'Baud')}")
        print(f"DER_0 = {ToSI(DER_0,None)}")
        print(f"verbose = {str(verbose)}")
        print(f"debug = {str(debug)}")

    args = {'file_name':os.path.abspath(filename),
            'port_reordering':port_reorder,
            'Z0':Z0/2.,
            'f_b':f_b,
            'T_r':T_r,
            'N':N
            }

    if debug: # pragma: no cover
        kwPairs=' '.join([key+' '+str(args[key]) for key in args.keys()])
        pwdArgString=''
        result=os.system('SignalIntegrity "'+os.path.abspath(os.path.join(os.path.dirname(__file__),'Projects','ERL_S11_Impulse.si'))+'"'+pwdArgString+' --external '+kwPairs)

    siapp = SignalIntegrityAppHeadless()
    opened = siapp.OpenProjectFile(os.path.abspath(os.path.join(os.path.dirname(__file__),'Projects','ERL_S11_Impulse.si')), args)

    if not opened: # pragma: no cover
        raise ERL_Exception('error: project file ERL_S11_Impulse.si could not be opened')

    result = siapp.Simulate()
    if result is None:
        raise ERL_Exception('error: project file ERL_S11_Impulse.si could not be simulated')

    (_, outputWaveformLabels, _, outputWaveformList) = result
    PTDR_wf = outputWaveformList[outputWaveformLabels.index('PTDR')]

    def G_rr(t):
        if t < T_fx:
            return 0.
        elif t < T_fx + (N_bx + 1)/f_b:
            return rho_x*(1+rho_x)*np.exp(-((t-T_fx)*f_b-(N_bx+1))**2/(N_bx+1)**2)
        else:
            return 1.0

    def G_loss(t):
        if t < T_fx:
            return 0.
        elif t < T_fx + (N_bx + 1)/f_b:
            return np.power(10.,beta_x/f_b*((t-T_fx)*f_b-(N_bx+1))/20.)
        else:
            return 1.0

    if debug: # pragma: no cover
        G_rr_wf = si.td.wf.Waveform(PTDR_wf.td,[G_rr(t) for t in PTDR_wf.Times()])
        G_loss_wf = si.td.wf.Waveform(PTDR_wf.td,[G_loss(t) for t in PTDR_wf.Times()])

    R_eff_wf = si.td.wf.Waveform(PTDR_wf.td,[v*G_rr(t)*G_loss(t) for t,v in zip(PTDR_wf.Times(),PTDR_wf.Values())])

    import matplotlib.pyplot as plt
    if debug: # pragma: no cover
        plt.plot([t*f_b for t in G_rr_wf.Times()],G_rr_wf.Values(),label='G_rr')
        plt.plot([t*f_b for t in G_loss_wf.Times()],G_loss_wf.Values(),label='G_loss')
        plt.axvline(T_fx*f_b,linestyle='--',color='red')
        plt.axvline((T_fx + (N_bx + 1)/f_b)*f_b,linestyle='--',color='red')
        plt.xlabel('time (samples)')
        plt.ylabel('amplitude (V)')
        plt.title('gating functions')
        plt.grid()
        plt.legend()
        plt.show()
        plt.cla()

    Phi = 10 # assume 10x oversampling
    K = int(R_eff_wf.td.K/Phi)*Phi
    phi_max=0
    sigma_max=0
    for phi in range(0,Phi):
        x=[R_eff_wf[k*Phi+phi] for k in range(0,K//Phi)]
        sigma=np.std(x)
        # print(sigma)
        if sigma > sigma_max:
            phi_max = phi
            sigma_max = sigma

    if debug or verbose:
        print(f'maximum sigma of {sigma_max} at phi={phi_max}')

    worst_phase_wf = si.td.wf.Waveform(si.td.wf.TimeDescriptor(R_eff_wf.Times()[0*Phi+phi_max],
                                                               K//Phi,
                                                               R_eff_wf.td.Fs/Phi),
                                        [R_eff_wf[k*Phi+phi_max] for k in range(0,K//Phi)])

    epsilon=1e-5
    def kmin():
        for k in range(0,worst_phase_wf.td.K):
            if abs(worst_phase_wf[k]) > epsilon:
                return k

    def kmax():
        for k in range(0,worst_phase_wf.td.K):
            index = worst_phase_wf.td.K-1-k
            if abs(worst_phase_wf[index]) > epsilon:
                return index

    kmin=kmin()
    kmax=kmax()
    K=kmax-kmin+1
    worst_phase_wf = si.td.wf.Waveform(si.td.wf.TimeDescriptor(worst_phase_wf.Times()[kmin],
                                                               kmax-kmin+1,
                                                               worst_phase_wf.td.Fs),
                                        worst_phase_wf.Values()[kmin:kmax+1])

    if debug or verbose:
        print(f"min: {kmin}, max: {kmax}")

    if debug: # pragma: no cover
        plt.plot([t*f_b for t in R_eff_wf.Times()],R_eff_wf.Values(),label='R_eff')
        plt.plot([t*f_b for t in PTDR_wf.Times()],PTDR_wf.Values(),label='PTDR')
        plt.stem([t*f_b for t in worst_phase_wf.Times()],worst_phase_wf.Values(),label='R_eff_worst_phase')
        plt.xlabel('time (samples)')
        plt.ylabel('amplitude (V)')
        plt.title('pulse TDR')
        plt.grid()
        plt.legend()
        plt.show()
        plt.cla()

    worst_phase_wf.WriteToFile('ERL_Filter.txt')

    args = {'Nbits':4e6,
            'f_b':f_b,
            }

    if debug: # pragma: no cover
        kwPairs=' '.join([key+' '+str(args[key]) for key in args.keys()])
        pwdArgString=''
        result=os.system('SignalIntegrity "'+os.path.abspath('ERL_S11_Error.si')+'"'+pwdArgString+' --external '+kwPairs)

    siapp = SignalIntegrityAppHeadless()
    opened = siapp.OpenProjectFile('ERL_S11_Error.si', args)
    if not opened: # pragma: no cover
        raise ERL_Exception('error: project file ERL_S11_Error.si could not be opened')

    result = siapp.Simulate()
    if result is None: # pragma: no cover
        raise ERL_Exception('error: project file ERL_S11_Error.si could not be simulated')

    (_, outputWaveformLabels, _, outputWaveformList) = result
    error_wf = outputWaveformList[outputWaveformLabels.index('V_error')]

    sigma=np.std(error_wf)

    if debug or verbose:
        print(f"min error: {min(error_wf)}, max error: {max(error_wf)}")

    histo,bin_edges = np.histogram(error_wf.Values(),
                         bins = 1000,
                         range=(-5.*sigma,5.*sigma),
                         )
    histo = histo / error_wf.td.K
    bin_centers=[(bin_edges[b]+bin_edges[b+1])/2. for b in range(bin_edges.shape[0]-1)]

    cdf=list(histo)
    for b in range(1,len(cdf)):
        cdf[b]=cdf[b-1]+histo[b]


    def linearly_interpolate(xi,yi,xf,yf,T):
        if yi < 10**-300/10: # protection when CDF just rose above zero
            return xi
        yi=np.log10(yi)
        yf=np.log10(yf)
        T=np.log10(T)
        m=(yf-yi)/(xf-xi)
        b=yi-m*xi
        x=(T-b)/m
        return x

    for b in range(len(cdf)):
        if cdf[b] > DER_0:
            bin_value = linearly_interpolate(bin_centers[b-1],
                                             cdf[b-1],
                                             bin_centers[b],
                                             cdf[b],
                                             DER_0)
            break

    if debug or verbose:
        print(f"DER intercept at: {ToSI(bin_value,'V')}")

    ERL = -20.*np.log10(-bin_value)

    if debug: # pragma: no cover
        sigma_estimate = [0.5*math.erf(0.5*np.sqrt(2)*bin_centers[b]/sigma)+0.5 for b in range(len(bin_centers))]

        plt.semilogy(bin_centers,cdf,label='cdf')
        plt.semilogy(bin_centers,sigma_estimate,label='cdf estimate')
        plt.xlabel('bin')
        plt.ylabel('probability')
        plt.title('cdf')
        plt.axhline(DER_0,linestyle='--',color='red')
        plt.axvline(bin_value,linestyle='--',color='red')
        plt.grid()
        plt.legend()
        plt.show()
        plt.cla()

    if debug or verbose:
        print(f"ERL: -20*Log_10(-DER intercept = {ToSI(-bin_value,'V')}) = {ToSI(ERL,'dB',round=5)}")
    return ERL

def ERL_Main():
    import argparse
    from argparse import RawTextHelpFormatter
    parser = argparse.ArgumentParser(
                    prog='ERL',
                    description="""Effective Return Loss Calculator

                    Calculates ERL mostly according to the IEEE standard.

                    """,
                    epilog='',
                    formatter_class=RawTextHelpFormatter)
    parser.add_argument('filename',nargs='?',default=None, help='name of .s4p file for the ERL measurement')           # positional argument
    parser.add_argument('-debug','--debug',action='store_true', help='shows debug information and plots as the computation proceeds')
    parser.add_argument('-p','--profile',action='store_true', help='profiles the software')
    parser.add_argument('-v','--verbose',action='store_true', help='prints information as calculation proceeds.\n\
this should not be set if you are relying on stdout for the return value.')
    parser.add_argument('-port_reorder', type=str, help='(optional) port ordering of 1p,1n,2p,2n of the .s4p file (default is 1,2,3,4).',default='1,2,3,4')
    parser.add_argument('-T_r', type=str, help='(required) transition time associated with a pulse,\n\
specified with units of s or UI (like 5ps or 5e-12 or 0.5UI).')
    parser.add_argument('-beta_x', type=str, help='(required) incremental available signal loss factor,\n\
specified with units of Hz (like 2.53GHz or 2.53e9).')
    parser.add_argument('-rho_x', type=str, help='(required) permitted reflection from a transmission line external to the DUT,\n\
must be between 0 and 1, specified unitless (like 0.5).')
    parser.add_argument('-N', type=str, help='(required) length of reflection signal,\n\
specified with units of UI (like 400UI or 400).')
    parser.add_argument('-N_bx', type=str, help='(required) equalizer length associated with reflection signal,\n\
specified with units of UI (like 16UI or 16).')
    parser.add_argument('-T_fx', type=str, default='0', help='(optional) time-gated propagation delay,\n\
specified with units of s (like 1ns or 1e-9),\n\
defaults to 0.')
    parser.add_argument('-f_b', type=str,  help='(required) baud rate\n\
specified with units of Baud (like 106.25GBaud or 106.25e9).')
    parser.add_argument('-Z0', type=str,  help='(optional) intended differential-mode characteristic impedance\n\
specified with units of ohm (like 100ohm or 100),\n\
defaults to 100.',default='100ohm')
    parser.add_argument('-DER_0', type=str,  help='(required) target detector error ratio\n\
specified unitless (like 1e-6).')
    args, unknown = parser.parse_known_args()

    argsDict=dict(zip(unknown[0::2],unknown[1::2]))

    def Error(message):
        if args.verbose or args.debug:
            print(message)
        print('error')
        exit(1)

    import sys
    if len(sys.argv)==1:
        # parser.print_help()
        # parser.exit()
        Error('file name and keyword values must be specified')

    if len(unknown):
        # parser.print_usage()
        # parser.exit()
        Error(f'unknown keyword {unknown[0]} encountered')

    argsDict['port_reorder'] = args.port_reorder

    try:
        argsDict['f_b']=FromSI(args.f_b,'Baud')
        if argsDict['f_b'] == None:
            raise(AttributeError)
    except (AttributeError,TypeError):
        Error('error: f_b must be specified')

    try:
        argsDict['T_r']=FromSI(args.T_r,'s')
        if argsDict['T_r'] == None:
            argsDict['T_r']=FromSI(args.T_r,'UI')/argsDict['f_b']
        if argsDict['T_r'] == None:
            raise(AttributeError)
    except (AttributeError,TypeError):
        Error('error: T_r must be specified')

    try:
        argsDict['beta_x']=FromSI(args.beta_x,'Hz')
        if argsDict['beta_x'] == None:
            raise(AttributeError)
    except (AttributeError,TypeError):
        Error('error: beta_x must be specified')

    try:
        argsDict['rho_x']=FromSI(args.rho_x,'')
        if argsDict['rho_x'] == None:
            raise(AttributeError)
    except (AttributeError,TypeError):
        Error('error: rho_x must be specified')

    try:
        argsDict['N']=FromSI(args.N,'UI')
        if argsDict['N'] == None:
            raise(AttributeError)
    except (AttributeError,TypeError):
        Error('error: N must be specified')

    try:
        argsDict['N_bx']=FromSI(args.N_bx,'UI')
        if argsDict['N_bx'] == None:
            raise(AttributeError)
    except (AttributeError,TypeError):
        Error('error: N_bx must be specified')

    try:
        argsDict['Z0']=FromSI(args.Z0,'ohm')
        if argsDict['Z0'] == None:
            raise(AttributeError)
    except (AttributeError,TypeError):
        Error('error: Z0 must be specified')

    try:
        argsDict['T_fx']=FromSI(args.T_fx,'s')
        if argsDict['T_fx'] == None:
            raise(AttributeError)
    except (AttributeError,TypeError):
        Error('error: T_fx must be specified')

    try:
        argsDict['DER_0']=FromSI(args.DER_0,'')
        if argsDict['DER_0'] == None:
            raise(AttributeError)
    except (AttributeError,TypeError):
        Error('error: DER_0 must be specified')

    runProfiler=args.profile

    if runProfiler: # pragma: no cover
        import cProfile
        globals()['args']=args
        globals()['argsDict']=argsDict
        cProfile.run('ERL(args.filename,args=argsDict,debug=args.debug,verbose=args.verbose)','stats')

        import pstats
        p = pstats.Stats('stats')
        p.strip_dirs().sort_stats('cumulative').print_stats(100)
    else:
        try:
            erl=ERL(args.filename,args=argsDict,debug=args.debug,verbose=args.verbose)
        except:
            erl='error'
        print(erl)
        exit(1 if erl == 'error' else 0)

if __name__ == '__main__': # pragma: no cover
    ERL_Main()
