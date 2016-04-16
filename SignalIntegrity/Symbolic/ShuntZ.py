'''
 Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
 Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
 All Rights Reserved.

 Explicit license in accompanying README.txt file.  If you don't have that file
 or do not agree to the terms in that file, then you are not licensed to use
 this material whatsoever.
'''
def ShuntZ(P,Z):
    if P==1:
        return ShuntZOnePort(Z)
    elif P==2:
        return ShuntZTwoPort(Z)
    elif P==3:
        return ShuntZThreePort(Z)
    elif P==4:
        return ShuntZFourPort(Z)

def ShuntZFourPort(Z):
    D='2\\cdot \\left('+Z+'+Z0\\right)'
    return [['\\frac{-Z0}{'+D+'}','\\frac{Z0}{'+D+'}','\\frac{2\\cdot '+Z+'+Z0}{'+D+'}','\\frac{Z0}{'+D+'}'],
            ['\\frac{Z0}{'+D+'}','\\frac{-Z0}{'+D+'}','\\frac{Z0}{'+D+'}','\\frac{2\\cdot '+Z+'+Z0}{'+D+'}'],
            ['\\frac{2\\cdot '+Z+'+Z0}{'+D+'}','\\frac{Z0}{'+D+'}','\\frac{-Z0}{'+D+'}','\\frac{Z0}{'+D+'}'],
            ['\\frac{Z0}{'+D+'}','\\frac{2\\cdot '+Z+'+Z0}{'+D+'}','\\frac{Z0}{'+D+'}','\\frac{-Z0}{'+D+'}']]

def ShuntZThreePort(Z):
    D='2\\cdot '+Z+'+3\\cdot Z0'
    return [['\\frac{-Z0}{'+D+'}','\\frac{2\\cdot '+Z+'+2\\cdot Z0}{'+D+'}','\\frac{2\\cdot Z0}{'+D+'}'],
            ['\\frac{2\\cdot '+Z+'+2\\cdot Z0}{'+D+'}','\\frac{-Z0}{'+D+'}','\\frac{2\\cdot Z0}{'+D+'}'],
            ['\\frac{2\\cdot Z0}{'+D+'}','\\frac{2\\cdot Z0}{'+D+'}','\\frac{2\\cdot '+Z+'-Z0}{'+D+'}']]

def ShuntZTwoPort(Z):
    D='2\\cdot '+Z+' +Z0'
    return [['\\frac{-Z0}{'+D+'}','\\frac{2\\cdot '+Z+'}{'+D+'}'],
            ['\\frac{2\\cdot '+Z+'}{'+D+'}','\\frac{-Z0}{'+D+'}']]

def ShuntZOnePort(Z):
    return [['\\frac{ '+Z+' -Z0}{ '+Z+' +Z0}']]


