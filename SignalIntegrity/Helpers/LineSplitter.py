

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