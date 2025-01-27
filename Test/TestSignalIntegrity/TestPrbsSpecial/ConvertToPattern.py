"""
ConvertToPattern.py
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

with open('SSPRQ.txt','rt') as f:
    lines=f.readlines()

bits_per_symbol=2
pattern=[]

for line in lines:
    code = round((float(line)*3+3)/2)
    #print(line+' '+str(code))
    bit_list=[]
    for b in range(bits_per_symbol):
        bit=code%2
        bit_list.append(bit)
        code=code//2
    bit_list.reverse()
    pattern.extend(bit_list)

with open('SSPRQ_pattern.txt','wt') as f:
    for p in pattern:
        f.write(str(p)+'\n')

with open('SSPRQ_Python_pattern.txt','wt') as f:
    line=''
    for p in pattern:
        line=line+str(p)+','
        if len(line)>200:
            f.write(line+'\n')
            line=''
    f.write(line+'\n')



with open('PRBS13Q.txt','rt') as f:
    lines=f.readlines()

bits_per_symbol=2
pattern=[]

for line in lines:
    code = round((float(line)*3+3)/2)
    #print(line+' '+str(code))
    bit_list=[]
    for b in range(bits_per_symbol):
        bit=code%2
        bit_list.append(bit)
        code=code//2
    bit_list.reverse()
    pattern.extend(bit_list)

with open('PRBS13Q_pattern.txt','wt') as f:
    for p in pattern:
        f.write(str(p)+'\n')

with open('PRBS13Q_Python_pattern.txt','wt') as f:
    line=''
    for p in pattern:
        line=line+str(p)+','
        if len(line)>200:
            f.write(line+'\n')
            line=''
    f.write(line+'\n')

if __name__ == '__main__':
    pass