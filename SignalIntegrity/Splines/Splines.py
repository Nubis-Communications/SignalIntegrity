# Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
# Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
# All Rights Reserved.
# 
# Explicit license in accompanying README.txt file.  If you don't have that file
# or do not agree to the terms in that file, then you are not licensed to use
# this material whatsoever.

class Spline(object):
    def __init__(self,x,y):
        N=len(x)
        r = range(0,N-1)
        h = [x[i+1]-x[i] for i in r]
        b = [(y[i+1]-y[i])/h[i] for i in r]
        u = [0,2.*(h[0]+h[1])]
        v = [0,6.*(b[1]-b[0])]
        for i in range(2,N-1):
            u.append(2.*(h[i]+h[i-1])-h[i-1]*h[i-1]/u[i-1])
            v.append(6.*(b[i]-b[i-1])-h[i-1]*v[i-1]/u[i-1])
        zi = range(1,N-1)
        zi.reverse()
        z = [0 for i in range(N)]
        for i in zi:
            z[i]=(v[i]-h[i]*z[i+1])/u[i]
        r=range(0,N-1)
        A = [y[i] for i in r]
        B = [-h[i]*z[i+1]/6.-h[i]*z[i]/3.+b[i] for i in r]
        C = [z[i]/2. for i in r]
        D = [1./6./h[i]*(z[i+1]-z[i]) for i in r]
        self.m_t = [x[i] for i in r]
        P=[]
        #these are the actual polynomial coefficients for P[0]+P[1]*x+P[2]*x**2+P[3]*x**3
        for i in r:
            Pi=[]
            Pi.append(A[i]+x[i]*(-B[i]+x[i]*(C[i]-x[i]*D[i])))
            Pi.append(B[i]+x[i]*(-2.*C[i]+x[i]*3.*D[i]))
            Pi.append(C[i]-3.*D[i]*x[i])
            Pi.append(D[i])
            P.append(Pi)
        self.m_A=[]
        #these are the polynomial coefficients for A[0]+A[1]*(x-t)+A[2]*(x-t)**2+A[3]*(x-t)**3
        #where t is the lower boundary of the interval
        for i in r:
            Ai=[]
            Ai.append(P[i][0]+x[i]*(P[i][1]+x[i]*(P[i][2]+x[i]*P[i][3])))
            Ai.append(P[i][1]+x[i]*(2.*P[i][2]+x[i]*3.*P[i][3]))
            Ai.append(P[i][2]+x[i]*3.*P[i][3])
            Ai.append(P[i][3])
            self.m_A.append(Ai)
    def Interval(self,x):
        if x<self.m_t[0]:
            return 0
        for i in range(1,len(self.m_t)):
            if x < self.m_t[i]:
                return i-1
        return len(self.m_t)-1
    def Evaluate(self,x):
        i = self.Interval(x)
        xi = (x-self.m_t[i])
        A=self.m_A[i]
        return A[0]+xi*(A[1]+xi*(A[2]+xi*A[3]))
    def EvaluateDerivative(self,x):
        i = self.Interval(x)
        xi = (x-self.m_t[i])
        A=self.m_A[i]
        return A[1]+xi*(A[2]+xi*A[3])
    def EvaluateSecondDerivative(self,x):
        i = self.Interval(x)
        xi = (x-self.m_t[i])
        A=self.m_A[i]
        return A[2]+xi*A[3]   
    def WriteToFile(self,fileName):
        with open(fileName,'w') as f:
            f.write(self.m_t)
            f.write(self.m_A)
        return self
    def ReadFromFile(self,fileName):
        with open(fileName,'r') as f:
            self.m_t=f.read(self.m_t)
            self.m_r=f.read(self.m_A)
        return self





