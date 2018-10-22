"""
ConvertWaveformsToCalFile.py
"""

# Copyright (c) 2018 Teledyne LeCroy, Inc.
# All rights reserved worldwide.
#
# This file is part of PySI.
#
# PySI is free software: You can redistribute it and/or modify it under the terms of the
# GNU General Public License as published by the Free Software Foundation, either version
# 3 of the License, or any later version.
#
# This program is distrbuted in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this program.
# If not, see <https://www.gnu.org/licenses/>


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