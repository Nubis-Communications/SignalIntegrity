'''
 Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
 Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
 All Rights Reserved.

 Explicit license in accompanying README.txt file.  If you don't have that file
 or do not agree to the terms in that file, then you are not licensed to use
 this material whatsoever.
'''
def IdealTransformer(a=1):
    if isinstance(a,str):
        try:
            a=int(a)
        except ValueError:
            try:
                a=float(a)
            except ValueError:
                pass
    if isinstance(a,int) or isinstance(a,float):
        if a==1:
            a='1'
            asq='1'
            denom='2'
        else:
            asq=str(a*a)
            denom=str(a*a+1)
            a=str(a)
    elif isinstance(a,str):
        asq=a+'^2'
        denom=asq+' + 1'
    one=' \\frac{ 1 }{'+denom+'} '
    a2=' \\frac{ '+asq+' }{ '+denom+' } '
    a1=' \\frac{ '+a+' }{ '+denom+' } '
    na=' -\\frac{ '+a+' }{ '+denom+' } '
    return [[one,a2,a1,na],[a2,one,na,a1],[a1,na,a2,one],[na,a1,one,a2]]