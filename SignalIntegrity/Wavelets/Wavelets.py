# Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
# Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
# All Rights Reserved.
# 
# Explicit license in accompanying README.txt file.  If you don't have that file
# or do not agree to the terms in that file, then you are not licensed to use
# this material whatsoever.

import math

class Wavelet(object):
	def __init__(self,h):
		self.h=h
		self.L=len(self.h)
		self.g=[pow(-1.,l)*h[self.L-1-l] for l in range(self.L)]
	def DWT(self,xi):
		x=list(xi)
		N=len(x)
		B=self.intlog2(N)-self.intlog2(self.L)+1
		for i in range(B):
			X=list(x)
			for k in range(N/2):
				X[k]=sum([x[(2*k+l)%N]*self.h[l]
					for l in range(self.L)])
				X[k+N/2]=sum([x[(2*k+l+N-2)%N]*self.g[l]
					for l in range(self.L)])
			x=list(X)
			N=N/2
		return X

	def IDWT(self,XI):
		X=list(XI)
		N=len(X)
		B=self.intlog2(N)-self.intlog2(self.L)+1
		N=self.L
		for i in range(B):
			x=list(X)
			for k in range(N/2):
				x[2*k]=sum([self.h[2*l]*X[(k-l+(N/2))%(N/2)]+
						self.g[2*l]*X[(k+1-l+(N/2))%(N/2)+(N/2)]
							for l in range(self.L/2)])
				x[2*k+1]=sum([self.h[2*l+1]*X[(k-l+(N/2))%(N/2)]+
						self.g[2*l+1]*X[(k+1-l+(N/2))%(N/2)+(N/2)]
							for l in range(self.L/2)])
			X=list(x)
			N=2*N
		return x

	@staticmethod
	def intlog2(x):
		r=math.log(float(x))/math.log(2.)
		return int(round(r))

class WaveletDaubechies4(Wavelet):
	def __init__(self):
		Wavelet.__init__(self,[h*math.sqrt(2.)/2
			for h in [0.6830127,1.1830127,0.3169873,-0.1830127]])

class WaveletHaar(Wavelet):
	def __init__(self):
		Wavelet.__init__(self,[h*math.sqrt(2.)/2
			for h in [1.,1.]])
