"""
TestEyeDiagram.py
"""

# Copyright (c) 2018 Teledyne LeCroy, Inc.
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
import unittest
import math
import SignalIntegrity as si
import numpy as np

import sys
if sys.version_info.major < 3:
    import Tkinter as tk
else:
    import tkinter as tk


class Calculator(object):
    def __init__(self,parent,headless=False):
        self.parent=parent
        self.project=parent.project
        self.headless=headless

    @staticmethod
    def normpd(x,mu,sigma):
        return 1./math.sqrt(2.*math.pi*sigma*sigma)*math.exp(-1./2.*((x-mu)/sigma)**2)

    @staticmethod
    def cnorm(x,mu,sigma):
        if sigma==0.:
            if x < mu:
                return 0.
            if x==mu:
                return 0.5
            if x > mu:
                return 1.0
        else:
            res= (1.+math.erf((x-mu)/sigma/math.sqrt(2.)))/2.
            return res

    @staticmethod
    def dnorm(x,mu,sigma):
        res =  Calculator.cnorm(x+1/2.,mu,sigma)-Calculator.cnorm(x-1/2.,mu,sigma)
        return res

    @staticmethod
    def dnorm_trial(x,mu,sigma):
        if sigma == 0.:
            return Calculator.dnorm_old(x,mu,sigma)
        res=0.5*Calculator.normpd(x,mu,sigma)+0.25*Calculator.normpd(x-0.5,mu,sigma)+0.25*Calculator.normpd(x+0.5,mu,sigma)
        return res

    def CalculateEyeDiagram(self):
        print('Creating Eye Diagram')
        prbswf=self.prbswf.DelayBy(self.project['Delay'])
        baudRate=self.project['Serdes.Baudrate']
        UI=1./baudRate
        R=self.project['Eye.Rows']; C=self.project['Eye.Columns']
        Fs=baudRate*C
        prbsTD=self.prbswf.TimeDescriptor()
        UpsampleFactor=Fs/prbsTD.Fs
        samplesRemovedLeft=si.td.f.FractionalDelayFilterSinX.S+1
        timeRemovedLeft=samplesRemovedLeft/prbsTD.Fs
        UIRemovedLeft=timeRemovedLeft/UI
        timeToRemoveLeft=math.ceil(UIRemovedLeft)*UI # this should cause the edge of the unit inverval to start at the first waveform point

        print('Adapting Waveform for Eye Diagram') 
        self.aprbswf=prbswf.Adapt(si.td.wf.TimeDescriptor(prbsTD.H+timeToRemoveLeft,prbsTD.K*UpsampleFactor,Fs))
        print('Adaption Complete')
        aprbsTD=self.aprbswf.TimeDescriptor()

        from PIL import Image,ImageTk

        auto=(self.project['Eye.YAxis.Mode']=='Auto')
        noiseSigma=self.project['Eye.JitterNoise.Noise']
        maxVProject=self.project['Eye.YAxis.Max']
        minVProject=self.project['Eye.YAxis.Min']

        self.project['Measurements.Max']=max(self.aprbswf.Values())
        self.project['Measurements.Min']=min(self.aprbswf.Values())

        maxV=max(self.aprbswf.Values())+10.*noiseSigma if auto else maxVProject
        minV=min(self.aprbswf.Values())-10.*noiseSigma if auto else minVProject
        DeltaV=maxV-minV

        bitmap=np.zeros((R,C))
        for k in range(aprbsTD.K):
            r=(self.aprbswf[k]-minV)/DeltaV*R
            c=k%C
            bitmap[max(0,min(R-1,int(math.ceil(r))))][c]+=r-math.floor(r)
            bitmap[max(0,min(R-1,int(math.floor(r))))][c]+=1.-(r-math.floor(r))

        applyJitterNoise=(self.project['Eye.Mode'] == 'JitterNoise')
        if applyJitterNoise:
            print('Applying Jitter and Noise')
            deltaT=UI/C
            deltaY=(maxV-minV)/R

            jitterSigma=self.project['Eye.JitterNoise.JitterS']
            noiseSigma=self.project['Eye.JitterNoise.Noise']
            deterministicJitter=self.project['Eye.JitterNoise.JitterDeterministicPkS']

            WH=int(math.floor(math.floor(2.*10.*(deterministicJitter+jitterSigma)/deltaT/2.)*2.)+1.)
            WV=int(math.floor(math.floor(2.*10.*noiseSigma/deltaY/2.)*2.)+1.)

            maxPixels = int(self.project['Eye.JitterNoise.MaxWindowPixels'])
            if WH*WV > maxPixels:
                print('***** warning - limiting window to : '+str(maxPixels)+' *****')
                WH=int(math.floor((WH*math.sqrt(float(maxPixels)/float(WH*WV))-1)/2))*2+1
                WV=int(math.floor((WV*math.sqrt(float(maxPixels)/float(WH*WV))-1)/2))*2+1

            # make the Gaussian kernel
            bitmaparray=np.array(bitmap)
            kernelHarray=np.array([[(self.dnorm(wh-(WH-1)//2,-deterministicJitter/deltaT,jitterSigma/deltaT)+self.dnorm(wh-(WH-1)//2,deterministicJitter/deltaT,jitterSigma/deltaT))/2.0 for wh in range(WH)]])
            kernelVarray=np.array([[self.dnorm(wv-(WV-1)//2,0,noiseSigma/deltaY)] for wv in range(WV)])
#                 with open('VArray.txt','wt') as f:
#                     for wv in range(WV):
#                         f.write(str(kernelVarray[wv][0])+'\n')

            from scipy.ndimage.filters import convolve
            bitmapJitterNoise=convolve(bitmaparray,kernelHarray,mode='wrap')
            bitmapJitterNoise=convolve(bitmapJitterNoise,kernelVarray,mode='constant')
            bitmap=bitmapJitterNoise
            self.bitmapJitterNoise=bitmapJitterNoise
            total=sum([sum([self.bitmapJitterNoise[r][c] for c in range(C)]) for r in range(R)])
            self.bitmapJitterNoise=[[self.bitmapJitterNoise[r][c]/total*C for c in range(C)] for r in range(R)]

            if self.project['Eye.JitterNoise.LogIntensity.LogIntensity']:
                total=sum([sum([bitmap[r][c] for c in range(C)]) for r in range(R)])
                bitmap=[[bitmap[r][c]/total*C for c in range(C)] for r in range(R)]
                minBER=max(self.project['Eye.JitterNoise.LogIntensity.MinBERExponent'],-20)
                maxBER=max(minBER,self.project['Eye.JitterNoise.LogIntensity.MaxBERExponent'])
                minValue=pow(10.,minBER-1)
                minSat=self.project['Eye.JitterNoise.LogIntensity.MinBERSaturationPercent']/100.
                maxSat=self.project['Eye.JitterNoise.LogIntensity.MaxBERSaturationPercent']/100.

                m=(maxSat-minSat)/(maxBER-minBER)
                b=minSat-minBER*m
                bitmap=[[math.log10(max(bitmap[r][c],minValue)) for c in range(C)] for r in range(R)]
                bitmap=[[bitmap[r][c]*m+b for c in range(C)] for r in range(R)]
                bitmap=[[255.0 if bitmap[r][c] < minSat else (0 if bitmap[r][c] > maxSat else 255.0-bitmap[r][c]*255.0) for c in range(C)] for r in range(R)]

        maxValue=(max([max(v) for v in bitmap]))
        midBin=0

        midBin=midBin+C//2

        numUI=int(self.project['Eye.UI']+0.5)
        bitmapCentered=[[0 for c in range(C*numUI)] for _ in range(R)]

        for u in range(numUI):
            for r in range(R):
                for c in range(C):
                    bitmapCentered[r][u*C+c]=bitmap[r][(c+midBin)%C]

        bitmap=bitmapCentered
        C=C*numUI

        if not applyJitterNoise or not self.project['Eye.JitterNoise.LogIntensity.LogIntensity']:
            saturationCurve=si.spl.Spline([0.,0.5,1.],[0.,self.project['Eye.Saturation']/100.,1.])

            bitmap=[[int(saturationCurve.Evaluate((maxValue - float(bitmap[r][c]))/maxValue)*255.0)
                     for c in range(C)] for r in range(R)]

        InvertImage=self.project['Eye.Invert']
        if InvertImage:
            bitmap=[[255-bitmap[r][c] for c in range(C)] for r in range(R)]

        self.img=Image.fromarray(np.squeeze(np.asarray(np.array(bitmap))).astype(np.uint8))

        C=int(C*self.project['Eye.ScaleX']/100.); R=int(R*self.project['Eye.ScaleY']/100.)
        self.img=self.img.resize((C,R))

        if self.parent.preferences['Calculation.SaveWaveforms']:
            self.img.save('eye.png')

        if self.headless:
            return

        self.parent.eyeCanvas.pack_forget()
        self.parent.eyeCanvas=tk.Canvas(self.parent.eyeFrame,width=C,height=R)
        self.parent.eyeImage=ImageTk.PhotoImage(self.img)
        self.parent.eyeCanvas.create_image(C/2,R/2,image=self.parent.eyeImage)
        self.parent.eyeCanvas.pack(expand=tk.YES,fill=tk.BOTH)

    def PixelX(self,time):
        return min(time*self.XM+self.XB,self.pixelsX)
    def PixelY(self,volt):
        return min(volt*self.YM+self.YB+4,self.pixelsY)

class TestEyeDiagramTest(unittest.TestCase,tk.Frame):
    project={'Delay':0,
             'Serdes.Baudrate':56e9,
             'Eye.Rows':200,
             'Eye.Columns':200,
             'Serdes.SignalingType':'Pam-4',
             'Eye.YAxis.Mode':'Auto',
             'Eye.JitterNoise.Noise':0,
             'Eye.YAxis.Max':0,
             'Eye.YAxis.Min':0,
             'Measurements.Max':0,
             'Measurements.Min':0,
             'Eye.Mode':'ISIOnly',
             'Eye.UI':2,
             'Eye.JitterNoise.LogIntensity.LogIntensity':False,
             'Eye.Invert':True,
             'Eye.ScaleX':350.0,
             'Eye.ScaleY':300.0,
             'Calculation.SaveWaveforms':True,
             'Eye.Saturation':20.0,
             'Eye.JitterNoise.JitterS':357e-15,
             'Eye.JitterNoise.Noise':2e-3,
             'Eye.JitterNoise.JitterDeterministicPkS':357e-15,
             'Eye.JitterNoise.MaxWindowPixels':100000,
             'Eye.JitterNoise.LogIntensity.MinBERExponent':-6,
             'Eye.JitterNoise.LogIntensity.MaxBERExponent':0,
             'Eye.JitterNoise.LogIntensity.MinBERSaturationPercent':0,
             'Eye.JitterNoise.LogIntensity.MaxBERSaturationPercent':100.
             }

    preferences={'Calculation.SaveWaveforms':True}

    def testEyeDiagram(self):
        self.root = tk.Tk()
        self.root.withdraw()

        tk.Frame.__init__(self, self.root)
        self.pack(fill=tk.BOTH, expand=tk.YES)

        self.eyeFrame=tk.Frame(self, relief=tk.RIDGE, borderwidth=5) 
        self.eyeCanvas=tk.Canvas(self.eyeFrame,width=0,height=0)
        self.eyeCanvas.pack()
        self.eyeFrame.pack(side=tk.TOP,fill=tk.BOTH,expand=tk.YES)

        self.calculator=Calculator(self)
        #self.calculator.prbswf=si.td.wf.Waveform().ReadFromFile('C:\\Users\\pete_\\Documents\\NubisSystemSim\\Projects\\prbswf.trc')
        Fs=280e9
        Dur=100e-9
        td=si.td.wf.TimeDescriptor(-10e-9,Dur*Fs,Fs)
        wf=si.prbs.MultiLevelWaveform(polynomial=13,
                                      baudrate=self.project['Serdes.Baudrate'],
                                      bitsPerSymbol=2,
                                      amplitude=1.0,
                                      risetime=10e-12,
                                      delay=0.,
                                      td=td)
        self.project['Delay']=-1./self.project['Serdes.Baudrate']/2.
        self.calculator.prbswf=wf
        self.calculator.CalculateEyeDiagram()

        self.root.deiconify()
        self.root.mainloop()

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()