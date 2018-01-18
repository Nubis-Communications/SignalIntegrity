'''
Created on Oct 11, 2017

@author: Peter.Pupalaikis
'''


def main():
    files = [('B1','baseline'),
             ('C1_1','short'),
             ('C1_2','open'),
             ('C1_3','load'),
             ('1M11','bpterm')]
    prefix='F2'
    suffix='00000'
    ext='.txt'
    dir='./Meas'
    timeOffset=9.99388672e-007
    mult=-4e10
    
    outputLineList=['4002M\n','Debug\n',str(len(files))+'\n']
    
    outputFileName='bpterm'
    
    for (itemName,itemFile) in files:
        outputLine=itemName
        filename=dir+'/'+prefix+itemFile+suffix+ext
        with open(filename) as f:
            fileLines=f.readlines()
        
        waveformLength=len(fileLines)-5
        outputLine=outputLine+' '+str(waveformLength)
        for line in fileLines[5:]:
            tokens=line.split(' ')
            (time,ampl)=(float(tokens[0])-timeOffset,float(tokens[1])*mult)
            outputLine=outputLine+' '+str(time)+' '+str(ampl)
        outputLineList.append(outputLine+'\n')
        
    with open(dir+'/'+outputFileName+'.cal','w') as f:
        f.writelines(outputLineList)

if __name__ == '__main__':
    main()