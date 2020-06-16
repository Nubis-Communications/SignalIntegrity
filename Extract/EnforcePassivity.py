'''
Created on Jun 16, 2020

@author: petep
'''

import sys
import SignalIntegrity.Lib as si

def main():
    """
    Enforce Passivity Utility:,

    Command line format:
    -file [s-parameter file]
    for example: -file network.s2p
    this is the s-parameter file to use.
    """
    args=sys.argv
    if len(args)<=1:
        print(main.__doc__)
        return
    """
    read the command line keeping the list of tokens following one of the recognized tokens in
    the list below.
    """
    tokens=['-file']
    intokens=False
    tokenlist=[]
    for arg in args[1:]:
        if arg in tokens:
            if intokens:
                tokenlist.append(thistokenlist)
            thistokenlist=[arg]
            intokens=True
        else:
            if intokens:
                thistokenlist.append(arg)
    if intokens:
        tokenlist.append(thistokenlist)

    """
    each list of tokens begins with one of the recognized tokens.  Assign the values to a dictionary
    of arguments.
    """
    argsdict={'file':None}

    for arglist in tokenlist:
        arg=arglist[0]
        if arg=='-file':
            if len(arglist)==2:
                argsdict['file']=arglist[1]

    sp=si.sp.SParameterFile(argsdict['file']).EnforcePassivity().WriteToFile(argsdict['file'])
    print('enforced passivity on: '+argsdict['file'])

if __name__ == '__main__':
    main()
