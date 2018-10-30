import math
from numpy import matrix
import SignalIntegrity.Lib as si
sp=si.sp.SParameterFile('cable.s2p')
s21=sp.FrequencyResponse(2,1)
f=s21.Frequencies('GHz')
mS21=s21.Values('mag')
K=len(f)
X=[[1,x,math.sqrt(x)] for x in f]
a=(matrix(X).getI()*[[y] for y in mS21]).tolist()
yf=(matrix(X)*matrix(a)).tolist()
r=(matrix(yf)-matrix(y)).tolist()
sigma=math.sqrt(((matrix(r).H*matrix(r)).tolist()[0][0])/K)
print('\[a_0 = '+"{:10.4e}".format(a[0][0])+'\]')
print('\[a_1 = '+"{:10.4e}".format(a[1][0])+'/GHz\]')
print('\[a_2 = '+"{:10.4e}".format(a[2][0])+'/\sqrt{GHz}\]')
print('\[\sigma = '+"{:10.4e}".format(sigma)+'\]')
