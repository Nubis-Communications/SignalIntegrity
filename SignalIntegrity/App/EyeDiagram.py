"""
EyeDiagram.py
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

import sys

if sys.version_info.major < 3:
    import Tkinter as tk
    import tkMessageBox as messagebox
else:
    import tkinter as tk
    from tkinter import messagebox

from SignalIntegrity.Lib.TimeDomain.Waveform import TimeDescriptor
from SignalIntegrity.Lib.TimeDomain.Filters.WaveformTrimmer import WaveformTrimmer
from SignalIntegrity.Lib.Splines.Splines import Spline
from SignalIntegrity.Lib.Exception import SignalIntegrityExceptionEyeDiagram

import SignalIntegrity.App.Project
import SignalIntegrity.App.Preferences

from PIL import Image,ImageTk

import math
import copy

import numpy as np

class EyeDiagram(object):
    def __init__(self,parent,headless=False):
        self.parent=parent
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
        res =  EyeDiagram.cnorm(x+1/2.,mu,sigma)-EyeDiagram.cnorm(x-1/2.,mu,sigma)
        return res

    @staticmethod
    def dnorm_trial(x,mu,sigma):
        if sigma == 0.:
            return EyeDiagram.dnorm_old(x,mu,sigma)
        res=0.5*EyeDiagram.normpd(x,mu,sigma)+0.25*EyeDiagram.normpd(x-0.5,mu,sigma)+0.25*EyeDiagram.normpd(x+0.5,mu,sigma)
        return res

    def CalculateEyeDiagram(self,callback=None):
        self.img=None
        self.rawBitmap=None

        if not self.headless:
            self.parent.statusbar.set('Creating Eye Diagram')

        baudRate=self.baudrate
        UI=1./baudRate
        R=SignalIntegrity.App.Project['EyeDiagram.Rows']; C=SignalIntegrity.App.Project['EyeDiagram.Columns']
        Fs=baudRate*C
        UpsampleFactor=Fs/self.prbswf.td.Fs

        if not self.headless: self.parent.statusbar.set('Adapting Waveform for Eye Diagram')
        # The waveform is adapted to the new sample rate.  This puts it on the same sample frame as the original waveform, such that there
        # is the assumption that there is a point at exactly time zero, and that is the center of the unit interval.
        # the amount of points to remove is trimmed from the left to make the very first sample at the center of a unit interval.
        self.aprbswf=self.prbswf.Adapt(TimeDescriptor(self.prbswf.td.H,self.prbswf.td.K*UpsampleFactor,Fs))
        self.aprbswf=WaveformTrimmer(C-int(round((self.aprbswf.td.H-math.floor(self.aprbswf.td.H/UI)*UI)*self.aprbswf.td.Fs)),0).TrimWaveform(self.aprbswf)
        if not self.headless: self.parent.statusbar.set('Adaption Complete')

        auto=(SignalIntegrity.App.Project['EyeDiagram.YAxis.Mode']=='Auto')
        noiseSigma=SignalIntegrity.App.Project['EyeDiagram.JitterNoise.Noise']
        applyJitterNoise=(SignalIntegrity.App.Project['EyeDiagram.Mode'] == 'JitterNoise')

        if auto:
            maxV=max(self.aprbswf.Values())
            minV=min(self.aprbswf.Values())
            if applyJitterNoise:
                maxV=maxV+10.*noiseSigma
                minV=minV-10.*noiseSigma
            else:
                maxV=maxV+abs(maxV-minV)*.1
                minV=minV-abs(maxV-minV)*.1
        else:
            maxV = SignalIntegrity.App.Project['EyeDiagram.YAxis.Max']
            minV = SignalIntegrity.App.Project['EyeDiagram.YAxis.Min']

        DeltaV=maxV-minV
        midBin=C//2

        if not self.headless: self.parent.statusbar.set('Building Bitmap')
        bitmap=np.zeros((R,C))
        for k in range(self.aprbswf.td.K):
            r=(self.aprbswf[k]-minV)/DeltaV*R
            c=(k+midBin)%C
            if (not callback is None) and (k//C != (k-1)//C):
                if not callback(k/self.aprbswf.td.K*100.):
                    return
            bitmap[max(0,min(R-1,int(math.ceil(r))))][c]+=r-math.floor(r)
            bitmap[max(0,min(R-1,int(math.floor(r))))][c]+=1.-(r-math.floor(r))

        self.rawBitmap=bitmap

        if applyJitterNoise:
            if not self.headless: self.parent.statusbar.set('Applying Jitter and Noise')
            deltaT=UI/C
            deltaY=(maxV-minV)/R

            jitterSigma=SignalIntegrity.App.Project['EyeDiagram.JitterNoise.JitterS']
            noiseSigma=SignalIntegrity.App.Project['EyeDiagram.JitterNoise.Noise']
            deterministicJitter=SignalIntegrity.App.Project['EyeDiagram.JitterNoise.JitterDeterministicPkS']

            WH=int(math.floor(math.floor(2.*10.*(deterministicJitter+jitterSigma)/deltaT/2.)*2.)+1.)
            WV=int(math.floor(math.floor(2.*10.*noiseSigma/deltaY/2.)*2.)+1.)

            maxPixels = int(SignalIntegrity.App.Project['EyeDiagram.JitterNoise.MaxKernelPixels'])
            if WH*WV > maxPixels:
                if not self.headless: self.parent.statusbar.set('***** warning - limiting window to : '+str(maxPixels)+' *****')
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
            bitmap=convolve(bitmaparray,kernelHarray,mode='wrap')
            bitmap=convolve(bitmap,kernelVarray,mode='constant')
            bitmap=bitmap/np.sum(bitmap)*C
            self.rawBitmap=bitmap

        try:
            self.AutoAlignEyeDiagram()
            bitmap=self.rawBitmap
        except:
            raise SignalIntegrityExceptionEyeDiagram('Eye Diagram Auto-Alignment Failed.')

        if applyJitterNoise:
            if SignalIntegrity.App.Project['EyeDiagram.JitterNoise.LogIntensity.LogIntensity']:
                bitmap=bitmap/np.sum(bitmap)*C
                minBER=max(SignalIntegrity.App.Project['EyeDiagram.JitterNoise.LogIntensity.MinExponent'],-20)
                maxBER=max(minBER,SignalIntegrity.App.Project['EyeDiagram.JitterNoise.LogIntensity.MaxExponent'])
                minValue=pow(10.,minBER-1)
                minSat=0
                maxSat=1.

                m=(maxSat-minSat)/(maxBER-minBER)
                b=minSat-minBER*m
                bitmap=np.array([[math.log10(max(bitmap[r][c],minValue)) for c in range(C)] for r in range(R)])
                bitmap=bitmap*m+b
                bitmap=np.array([[0. if bitmap[r][c] < minSat else (1 if bitmap[r][c] > maxSat else bitmap[r][c]) for c in range(C)] for r in range(R)])
                self.rawBitmap=bitmap
                bitmap=255.0-bitmap*255.0

        maxValue=(max([max(v) for v in bitmap]))

        numUI=int(SignalIntegrity.App.Project['EyeDiagram.UI']+0.5)
        if numUI>1:
            bitmap=[[bitmap[r][c%C] for c in range(C*numUI)] for r in range(R)]

        C=C*numUI

        if not applyJitterNoise or not SignalIntegrity.App.Project['EyeDiagram.JitterNoise.LogIntensity.LogIntensity']:
            saturationCurve=Spline([0.,0.5,1.],[0.,SignalIntegrity.App.Project['EyeDiagram.Saturation']/100.,1.])

            bitmap=[[int(saturationCurve.Evaluate((maxValue - float(bitmap[r][c]))/maxValue)*255.0)
                     for c in range(C)] for r in range(R)]

        InvertImage=SignalIntegrity.App.Project['EyeDiagram.Invert']
        if InvertImage:
            bitmap=[[255-bitmap[r][c] for c in range(C)] for r in range(R)]

        color=True
        if color:
            try:
                color=int(SignalIntegrity.App.Project['EyeDiagram.Color'].strip('#'),16)
                b=color%256; g=(color//256)%256; r=(color//(256*256))%256
            except:
                r=256; g=256; b=256

            ba=np.squeeze(np.asarray(np.array(bitmap)))
            rgbArray = np.zeros((ba.shape[0],ba.shape[1],3), 'uint8')
            rgbArray[..., 0] = ba*r/256
            rgbArray[..., 1] = ba*g/256
            rgbArray[..., 2] = ba*b/256

            self.img = Image.fromarray(rgbArray)
        else:
            self.img=Image.fromarray(np.squeeze(np.asarray(np.array(bitmap))).astype(np.uint8))

        C=int(C*SignalIntegrity.App.Project['EyeDiagram.ScaleX']/100.); R=int(R*SignalIntegrity.App.Project['EyeDiagram.ScaleY']/100.)
        self.img=self.img.resize((C,R))
        self.image=copy.deepcopy(self.img)
        if self.headless:
            return

    def AutoAlignEyeDiagram(self):
        if not SignalIntegrity.App.Project['EyeDiagram.Alignment.AutoAlign']:
            return
        bitmap=self.rawBitmap.copy()
        BERForAlignment=SignalIntegrity.App.Project['EyeDiagram.Alignment.BERForAlignment']
        BitsPerSymbol=SignalIntegrity.App.Project['EyeDiagram.Alignment.BitsPerSymbol']
        numberOfEyes=int(2**BitsPerSymbol-1)
        (R,C)=bitmap.shape
        darkCounts=[]
        darkExtents=[]
        minValueLog=pow(10.,-20)
        minSat=0
        maxSat=1.

        minBER=BERForAlignment; maxBER=BERForAlignment+0.001
        m=(maxSat-minSat)/(maxBER-minBER)
        b=minSat-minBER*m
        bitmapLog=np.array([[math.log10(max(bitmap[r][c],minValueLog)) for c in range(C)] for r in range(R)])
        bitmapLog=bitmapLog*m+b
        bitmapLog=np.array([[0. if bitmapLog[r][c] < minSat else (1 if bitmapLog[r][c] > maxSat else bitmapLog[r][c]) for c in range(C)] for r in range(R)])

        for c in range(C):
            counter=None
            thisCounts=[]
            thisExtents=[]
            for r in range(1,R):
                if bitmapLog[r][c]==0. and bitmapLog[r-1][c]!=0.:
                    counter=r
                elif bitmapLog[r][c]!=0 and bitmapLog[r-1][c]==0:
                    if counter != None:
                        thisCounts.append(r-counter)
                        thisExtents.append((counter,r))
            darkExtents.append(thisExtents)
            darkCounts.append(thisCounts)
        bestOpenings=None
        indexOfBestOpening=None
        for c in range(C):
            dc=darkCounts[c]
            if len(dc)!=numberOfEyes:
                continue
            if bestOpenings is None:
                bestOpenings=np.sort(dc)
            else:
                dc=np.sort(dc)
                if dc[0]>bestOpenings[0]:
                    bestOpenings=dc; indexOfBestOpening=c
                elif (dc[0]==bestOpenings[0]) and (numberOfEyes > 1):
                    if dc[1]> bestOpenings[1]:
                        bestOpenings=dc; indexOfBestOpening=c
                    elif dc[1]==bestOpenings[1]:
                        if dc[2]>bestOpenings[2]:
                            bestOpenings=dc; indexOfBestOpening=c
        # These are the three largest eye openings at the best index in order of appearance
        # remember that the eye is upside down (we're looking from the bottom up
        eyeExtents=sorted(sorted(darkExtents[indexOfBestOpening],key = lambda x: x[1]-x[0])[0:numberOfEyes],key = lambda y:y[0])
        # now, for each eye, walk backwards and forwards at each row slice within these extents
        # to find the extents of each eye opening
        rowOfMaxEyeWidth=None
        startColumnofMaxEyeWidth=None
        endColumnofMaxEyeWidth=None
        maxEyeWidth=0
        for eye in eyeExtents:
            for r in range(eye[0],eye[1]+1):
                c=indexOfBestOpening
                count=1 # count the pixel we're on
                startColumn=c
                endColumn=c
                found=False
                while count != C and not found:
                    c=(c-1)%C
                    if bitmapLog[r][c]!=0:
                        found=True
                    else:
                        count+=1
                        startColumn=c
                found=False
                while count != C and not found:
                    c=(c+1)%C
                    if bitmapLog[r][c]!=0:
                        found=True
                    else:
                        count+=1
                        endColumn=c
                if (count < C) and (count > maxEyeWidth):
                    maxEyeWidth=count
                    rowOfMaxEyeWidth=r
                    startColumnofMaxEyeWidth=startColumn
                    endColumnofMaxEyeWidth=endColumn
        # should check these for None
        if endColumnofMaxEyeWidth<startColumnofMaxEyeWidth:
            endColumnofMaxEyeWidth+=C
        columnAtEyeCenter=((startColumnofMaxEyeWidth+endColumnofMaxEyeWidth)//2)%C
        for r in range(R):
            for c in range(C):
                self.rawBitmap[r][(c+C//2)%C]=bitmap[r][(c+columnAtEyeCenter)%C]
        return
