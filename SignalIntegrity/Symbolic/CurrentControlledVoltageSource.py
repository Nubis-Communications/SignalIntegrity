# Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
# Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
# All Rights Reserved.
# 
# Explicit license in accompanying README.txt file.  If you don't have that file
# or do not agree to the terms in that file, then you are not licensed to use
# this material whatsoever.

def CurrentControlledVoltageSource(G):
    """symbolic current controlled voltage source
    @param G string transresistance
    @return list of list of string s-parameter matrix
    containing LaTeX or ASCII strings for each element.
    @note strings can be any valid LaTeX
    @note this is the symbolic version of
    SignalIntegrity.Devices.CurrentControlledVoltageSource.CurrentControlledVoltageSource
    """
    return  [['0','1','0','0'],
             ['1','0','0','0'],
             ['-\\frac{'+G+' }{2\\cdot Z0}','\\frac{'+G+' }{2\\cdot Z0}','0','1'],
             ['\\frac{'+G+' }{2\\cdot Z0}','-\\frac{'+G+' }{2\\cdot Z0}','1','0']]
