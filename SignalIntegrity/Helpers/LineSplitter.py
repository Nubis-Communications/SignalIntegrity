# Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
# Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
# All Rights Reserved.
# 
# Explicit license in accompanying README.txt file.  If you don't have that file
# or do not agree to the terms in that file, then you are not licensed to use
# this material whatsoever.

def LineSplitter(line):
    sline=line.strip()
    inquote=False
    intoken=False
    acc=''
    tokenList=[]
    for i in range(len(sline)):
        if sline[i]==' ':
            if intoken:
                if not inquote:
                    tokenList.append(acc)
                    acc=''
                else:
                    acc=acc+sline[i]
        elif sline[i]=='\'':
            if inquote:
                inquote=False
                intoken=False
                tokenList.append(acc)
                acc=''
            else:
                intoken=True
                inquote=True
        else:
            if not intoken:
                intoken=True
            acc=acc+sline[i]
    if intoken:
        tokenList.append(acc)
    return tokenList  