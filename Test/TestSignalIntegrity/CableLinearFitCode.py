import math
from numpy import array
from numpy.linalg import pinv
import SignalIntegrity.Lib as si
sp=si.sp.SParameterFile('cable.s2p')
s21=sp.FrequencyResponse(2,1)
f=s21.Frequencies('GHz')
mS21=s21.Values('mag')
K=len(f)
X=[[1,x,math.sqrt(x)] for x in f]
a=(pinv(array(X)).dot(array([[y] for y in mS21]))).tolist()
yf=(array(X).dot(array(a))).tolist()
r=(array(yf)-array([[y] for y in mS21])).tolist()
sigma=math.sqrt((array(r).conj().T.dot(array(r)).tolist()[0][0])/K)
print('\\[a_0 = \\text{'+"{:10.4e}".format(a[0][0])+'}\\]')
print('\\[a_1 = \\text{'+"{:10.4e}".format(a[1][0])+'/GHz}\\]')
print('\\[a_2 = \\text{'+"{:10.4e}".format(a[2][0])+'}/\\sqrt{\\text{GHz}}\\]')
print('\\[\\sigma = \\text{'+"{:10.4e}".format(sigma)+'}\\]')
