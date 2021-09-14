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
from SignalIntegrity.Lib.Exception import SignalIntegrityExceptionEyeDiagram
from SignalIntegrity.Lib.Eye.EyeDiagramBitmap import EyeDiagramBitmap

import SignalIntegrity.App.Project
import SignalIntegrity.App.Preferences

from PIL import Image,ImageTk

import math
import copy

import numpy as np

# class Pixelator(object):
#     def __init__(self,Bins=1,minValue=0,maxValue=1.,wrapNotLimit=False):
#         self.bins=Bins
#         self.minValue=minValue
#         self.maxValue=maxValue
#         self.wrapNotLimit=wrapNotLimit
#         self.span=self.maxValue-self.minValue
#         # m and b convert bin to volts
#         self.m = self.bins/self.span
#         # solve m*0+b=minValue
#         self.b = self.minValue
#     def Value(self,bin):
#         """
#             @note: maximum bin will not produce maximum value.  The maximum bin + 1 produces the maximum
#             value.  This is because the lower bin edge is the actual value.
#         """
#         return bin*self.m+self.b
#     def FloatBin(self,value):
#         bin=(value-self.b)/self.m
#         if self.wrapNotLimit:
#             bin=bin%self.bins
#             if bin<0: bin=bin+self.bins
#         return bin
#     def IntBin(self,value):
#         return int(self.FloatBin(value))
# 
# class VerticalPixelator(Pixelator):
#     def __init__(self,Rows=1,minValue=0,maxValue=1.):
#         super().__init__(Rows,minValue,maxValue,wrapNotLimit=False)
# 
# 
# class HorizontalPixelator(Pixelator):
#     def __init__(self,Rows=1,minValue=0,maxValue=1.):
#         super().__init__(Rows,minValue,maxValue,wrapNotLimit=True)

class Pixelator(object):
    def __init__(self,rows,columns,step=1,mode='Fixed'):
        self.rows=rows
        self.columns=columns
        self.step=step
        self.auto=(mode=='Auto')

    def Hits(self,r,c):
        R=self.rows; C=self.columns
        lowestr=r-0.5
        rl=int(math.floor(lowestr))
        highestr=r+0.5
        rh=int(math.floor(highestr))
        lrh=lowestr-rl
        lrl=1-lrh
        lowestc=c-0.5
        cl=int(math.floor(lowestc))
        highestc=c+0.5
        ch=int(math.floor(highestc))
        lch=lowestc-cl
        lcl=1-lch
        rlValid=(0<=rl<R)
        rhValid=(0<=rh<R)
        if cl<0:
            cl=cl+C
        if ch>=C:
            ch=ch-C
        clValid=(0<=cl<C)
        chValid=(0<=ch<C)
        results=[]
        if rlValid and clValid: results+=[((rl,cl),(lrl,lcl),lrl*lcl/self.step)]
        if rhValid and clValid: results+=[((rh,cl),(lrh,lcl),lrh*lcl/self.step)]
        if rlValid and chValid: results+=[((rl,ch),(lrl,lch),lrl*lch/self.step)]
        if rhValid and chValid: results+=[((rh,ch),(lrh,lch),lrh*lch/self.step)]
#         for result in results:
#             print(f"({result[0][0]},{result[0][1]}) = {result[1][0]}*{result[1][1]}={result[2]}")
        return results

    def Results(self,ri,ci,rf,cf,useFirst=False):
        R=self.rows; C=self.columns
        steps=self.step if not self.auto else max(1,min(int(math.ceil(2*abs(rf-ri))),self.step))
        if ci>cf:
            cf=cf+C
        m=(rf-ri)/(cf-ci)
        # solve y=mx+b for ci to produce ri:  ri=m*ci+b
        b=ri-m*ci
        # so now, r=m*c+b

        cspan=cf-ci
        rspan=rf-ri
        c=[n/steps*cspan+ci for n in range(steps+1)]
        r=[n/steps*rspan+ri for n in range(steps+1)]
        results=[]
        useFirst=True
        for n in range(steps+1):
            if n!=0 or useFirst:
                results.extend(self.Hits(r[n],c[n]))
        return results

class EyeDiagram(object):
    def __init__(self,parent,name,headless=False):
        self.parent=parent
        self.headless=headless
        self.name=name

    def Image(self):
        return self.img

    def BitMap(self):
        return self.rawBitmap

    def Measurements(self):
        return self.measDict

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

    def CalculateEyeDiagram(self,cacheFileName,callback=None):
        self.img=None
        self.rawBitmap=None
        self.measDict=None
        self.annotationBitmap=None

        if not self.headless:
            self.parent.statusbar.set('Creating Eye Diagram')

        eyeDiagramBitmap=EyeDiagramBitmap(
            callback=callback,
            cacheFileName=cacheFileName+'_'+self.name if SignalIntegrity.App.Preferences['Cache.CacheResults'] else None,
            YAxisMode=SignalIntegrity.App.Project['EyeDiagram.YAxis.Mode'],
            YMax=SignalIntegrity.App.Project['EyeDiagram.YAxis.Max'],
            YMin=SignalIntegrity.App.Project['EyeDiagram.YAxis.Min'],
            NoiseSigma=SignalIntegrity.App.Project['EyeDiagram.JitterNoise.Noise'] if (SignalIntegrity.App.Project['EyeDiagram.Mode'] == 'JitterNoise') else 0,
            Rows=SignalIntegrity.App.Project['EyeDiagram.Rows'],
            Cols=SignalIntegrity.App.Project['EyeDiagram.Columns'],
            BaudRate=self.baudrate,
            prbswf=self.prbswf,
            EnhancementMode=SignalIntegrity.App.Project['EyeDiagram.EnhancedPrecision.Mode'],
            EnhancementSteps=SignalIntegrity.App.Project['EyeDiagram.EnhancedPrecision.FixedEnhancement'])
        bitmap=eyeDiagramBitmap.Bitmap()
        self.rawBitmap=bitmap
        baudRate=self.baudrate
        UI=1./baudRate
        self.maxV=eyeDiagramBitmap.maxV
        self.minV=eyeDiagramBitmap.minV
        R=SignalIntegrity.App.Project['EyeDiagram.Rows']; C=SignalIntegrity.App.Project['EyeDiagram.Columns']

        applyJitterNoise=(SignalIntegrity.App.Project['EyeDiagram.Mode'] == 'JitterNoise')
        if applyJitterNoise:
            if not self.headless: self.parent.statusbar.set('Applying Jitter and Noise')
            deltaT=UI/C
            deltaY=(self.maxV-self.minV)/R

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

        try:
            self.EyeMeasurements()
        except Exception as e:
            raise SignalIntegrityExceptionEyeDiagram('Eye Diagram Measurements Failed.')

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

        maxValue=bitmap.max()

        numUI=int(SignalIntegrity.App.Project['EyeDiagram.UI']+0.5)
        if numUI>1:
            bitmap=np.array([[bitmap[r][c%C] for c in range(C*numUI)] for r in range(R)])
            if not self.annotationBitmap is None:
                annotationBitmap=np.array([[self.annotationBitmap[r][c%C] for c in range(C*numUI)] for r in range(R)])
        elif not self.annotationBitmap is None:
            annotationBitmap=self.annotationBitmap

        C=C*numUI

        if not SignalIntegrity.App.Project['EyeDiagram.JitterNoise.LogIntensity.LogIntensity']:
            P=math.log10(min(0.99,max(0.001,SignalIntegrity.App.Project['EyeDiagram.Saturation']/100.)))/math.log10(0.5)
            bitmap=(((bitmap.astype(float)*-1.0+maxValue)/maxValue)**P*255.0).astype(int)

        InvertImage=SignalIntegrity.App.Project['EyeDiagram.Invert']
        if InvertImage:
            bitmap=255-bitmap

        color=True
        if color:
            try:
                color=int(SignalIntegrity.App.Project['EyeDiagram.Color'].strip('#'),16)
                b=color%256; g=(color//256)%256; r=(color//(256*256))%256
            except:
                r=256; g=256; b=256

            ba=np.squeeze(np.asarray(np.array(bitmap)))
            rgbArray = np.zeros((ba.shape[0],ba.shape[1],3), 'uint8')
            rgbArray[..., 0] = np.flipud(ba)*r/256
            rgbArray[..., 1] = np.flipud(ba)*g/256
            rgbArray[..., 2] = np.flipud(ba)*b/256

            if not self.annotationBitmap is None:
                try:
                    color=int(SignalIntegrity.App.Project['EyeDiagram.Annotation.Color'].strip('#'),16)
                    b=color%256; g=(color//256)%256; r=(color//(256*256))%256
                except:
                    r=256; g=256; b=256

                for row in range(rgbArray.shape[0]):
                    for col in range(rgbArray.shape[1]):
                        if np.flipud(annotationBitmap)[row][col] != 0:
                            rgbArray[row][col][0]=r
                            rgbArray[row][col][1]=g
                            rgbArray[row][col][2]=b

            self.img = Image.fromarray(rgbArray)
        else:
            self.img=Image.fromarray(np.squeeze(np.asarray(np.array(bitmap))).astype(np.uint8))

        C=int(C*SignalIntegrity.App.Project['EyeDiagram.ScaleX']/100.); R=int(R*SignalIntegrity.App.Project['EyeDiagram.ScaleY']/100.)
        self.img=self.img.resize((C,R))
        self.image=copy.deepcopy(self.img)
        if self.headless:
            return

    def AutoAlignEyeDiagram(self):
        if not SignalIntegrity.App.Project['EyeDiagram.Alignment.AutoAlign'] and not SignalIntegrity.App.Project['EyeDiagram.Measure.Measure']:
            return
        bitmap=self.rawBitmap.copy()
        BERForAlignment=SignalIntegrity.App.Project['EyeDiagram.Alignment.BERForAlignment']
        BitsPerSymbol=SignalIntegrity.App.Project['EyeDiagram.Alignment.BitsPerSymbol']
        numberOfEyes=int(2**BitsPerSymbol-1)
        (R,C)=bitmap.shape
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

        # develop the extents of the eye openings for each eye in a column (vertical slice)
        # The assumption is that there is signal or the exterior in the first row.  Stepping into
        # a dark area from a non-dark area starts an extent and the stepping from a dark area to a
        # non-dark area ends an extent.
        for c in range(C):
            counter=None
            thisExtents=[]
            for r in range(1,R):
                if bitmapLog[r][c]==0. and bitmapLog[r-1][c]!=0.:
                    counter=r
                elif bitmapLog[r][c]!=0 and bitmapLog[r-1][c]==0:
                    if counter != None:
                        thisExtents.append((counter,r))
            darkExtents.append(thisExtents)
        # convert the extents into sizes for comparison
        darkCounts=[[f-e for (e,f) in extents] for extents in darkExtents]

        # now we look for the column index having the best opening
        # this is defined as the largest eye opening.  If there is a tie and there are multiple
        # eyes, then we compare the size of the next eye, and so on.
        bestOpenings=None
        indexOfBestOpening=None
        bestMinimumOpening=None
        indexOfBestMinimumOpening=None
        for c in range(C):
            dc=darkCounts[c]
            if len(dc)<numberOfEyes:
                continue
            thisMinimumOpening=np.flip(np.sort(dc))[numberOfEyes-1]
            if bestMinimumOpening is None:
                bestMinimumOpening=thisMinimumOpening
                indexOfBestMinimumOpening=c
            elif thisMinimumOpening > bestMinimumOpening:
                bestMinimumOpening=thisMinimumOpening
                indexOfBestMinimumOpening=c
            if bestOpenings is None:
                bestOpenings=np.flip(np.sort(dc))
                indexOfBestOpening=c
            else:
                dc=np.flip(np.sort(dc))
                e=0; Continue=True
                while (e < numberOfEyes) and (indexOfBestOpening !=c) and Continue:
                    if dc[e]>bestOpenings[e]:
                        bestOpenings=dc
                        indexOfBestOpening=c
                        Continue=False
                    elif dc[e]==bestOpenings[e]:
                        pass # should continue
                    else:
                        Continue=False
                    e+=1
        alignOnTime=(SignalIntegrity.App.Project['EyeDiagram.Alignment.Mode'] == 'Horizontal')
        if alignOnTime: # 'Horizontal', meaning midpoint in time in an eye
            # These are the three largest eye openings at the best index in order of appearance
            # remember that the eye is upside down (we're looking from the bottom up
            self.eyeExtentsForAlignment=sorted(sorted(darkExtents[indexOfBestOpening],key = lambda x: x[1]-x[0],reverse=True)[0:numberOfEyes],key = lambda y:y[0])
            # now, for each eye, walk backwards and forwards at each row slice within these extents
            # to find the extents of each eye opening
            rowOfMaxEyeWidth=None
            startColumnofMaxEyeWidth=None
            endColumnofMaxEyeWidth=None
            alignOnMiddleEye=(SignalIntegrity.App.Project['EyeDiagram.Alignment.Horizontal'] == 'Middle')
            if alignOnMiddleEye: # 'Middle', meaning horizontal midpoint of middle eye
                eyeExtents=[self.eyeExtentsForAlignment[(2**BitsPerSymbol)//2-1]]
            else: # 'Max', meaning horizontal midpoint of widest eye
                eyeExtents=self.eyeExtentsForAlignment
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
        else: # 'Vertical', meaning at location of a maximum eye opening
            alignMaxMinimum=(SignalIntegrity.App.Project['EyeDiagram.Alignment.Vertical'] == 'MaxMin')
            if alignMaxMinimum: # 'MaxMin', meaning max vertical opening of smallest eye
                columnAtEyeCenter=indexOfBestMinimumOpening
            else: # 'Max', meaning max vertical opening of all eyes
                columnAtEyeCenter=indexOfBestOpening

        if not SignalIntegrity.App.Project['EyeDiagram.Alignment.AutoAlign']:
            return
        for r in range(R):
            for c in range(C):
                self.rawBitmap[r][(c+C//2)%C]=bitmap[r][(c+columnAtEyeCenter)%C]
        return

    def EyeMeasurements(self):
        if not SignalIntegrity.App.Project['EyeDiagram.Measure.Measure']:
            return
        bitmap=self.rawBitmap.copy()
        BERForMeasure=SignalIntegrity.App.Project['EyeDiagram.Measure.BERForMeasure']
        BitsPerSymbol=SignalIntegrity.App.Project['EyeDiagram.Alignment.BitsPerSymbol']
        numberOfEyes=int(2**BitsPerSymbol-1)
        (R,C)=bitmap.shape
        minValueLog=pow(10.,-20)
        minSat=0
        maxSat=1.

#         import matplotlib.pyplot as plt
#         plt.cla()
# 
#         ber=[math.log10(max(bitmap[r][c],minValueLog)) for r in range(R)]
#         plt.plot([r for r in range(R)],ber)
#         plt.xlabel('row')
#         plt.ylabel('ber exponent')
#         plt.show()

        minBER=BERForMeasure; maxBER=BERForMeasure+0.001
        m=(maxSat-minSat)/(maxBER-minBER)
        b=minSat-minBER*m
        bitmapLog=np.array([[math.log10(max(bitmap[r][c],minValueLog)) for c in range(C)] for r in range(R)])
        bitmapLog=bitmapLog*m+b
        bitmapLog=np.array([[0. if bitmapLog[r][c] < minSat else (1 if bitmapLog[r][c] > maxSat else bitmapLog[r][c]) for c in range(C)] for r in range(R)])

        # develop the extents of the eye openings for each eye in a column (vertical slice)
        # The assumption is that there is signal or the exterior in the first row.  Stepping into
        # a dark area from a non-dark area starts an extent and the stepping from a dark area to a
        # non-dark area ends an extent.

        c=C//2
        counter=None
        darkExtents=[]
        for r in range(1,R):
            if bitmapLog[r][c]==0. and bitmapLog[r-1][c]!=0.:
                counter=r
            elif bitmapLog[r][c]!=0 and bitmapLog[r-1][c]==0:
                if counter != None:
                    darkExtents.append((counter,r))
        eyeVerticalExtentsForMeasurement=sorted(sorted(darkExtents,key = lambda x: x[1]-x[0],reverse=True)[0:numberOfEyes],key = lambda y:y[0])
        # now, for each eye, walk backwards and forwards at each row slice within these extents
        # to find the extents of each eye opening
        deltaV=self.maxV-self.minV
        eyeHeights=[(f-e)/R*deltaV for (e,f) in eyeVerticalExtentsForMeasurement]
        eyeMidBins=[int(round((f+e)/2)) for (e,f) in eyeVerticalExtentsForMeasurement]
        eyeMids=[b/R*deltaV+self.minV for b in eyeMidBins]
        # the threshold extents are based off the eye extents, except for the bottom and top
        thresholdExtents=[(None if t==0 else eyeVerticalExtentsForMeasurement[t-1][1]+1,
                                None if t==numberOfEyes else eyeVerticalExtentsForMeasurement[t][0]-1)
                               for t in range(numberOfEyes+1)]
        # fill in the bottom threshold extent
        for r in range(R):
            if bitmapLog[r][c] > 0:
                thresholdExtents[0]=(r,thresholdExtents[0][1])
                break
        # fill in the top threshold extent
        for r in range(R):
            if bitmapLog[R-1-r][c] > 0:
                thresholdExtents[-1]=(thresholdExtents[-1][0],R-1-r)
                break
        eyeAverageLevels=[]
        acc=0
        pacc=0
        L=0
        for r in range(R+1):
            if ((L < len(eyeMidBins)) and (r < eyeMidBins[L])) or ((L >= len(eyeMidBins)) and (r < R)):
                pacc+=self.rawBitmap[r][c]
                acc+=self.rawBitmap[r][c]*(r/R*deltaV+self.minV)
            else:
                eyeAverageLevels.append(acc/pacc)
                acc=0; pacc=0; L+=1
        AV=[eyeAverageLevels[l+1]-eyeAverageLevels[l] for l in range(len(eyeAverageLevels)-1)]
        EyeLinearity=min(AV)/max(AV)
        if BitsPerSymbol == 2:
            (V0,V1,V2,V3)=(eyeAverageLevels[0],eyeAverageLevels[1],eyeAverageLevels[2],eyeAverageLevels[3])
            Vmid=(V0+V3)/2
            ES1=(V1-Vmid)/(V0-Vmid)
            ES2=(V2-Vmid)/(V3-Vmid)
            RLM=min(3.*ES1,3.*ES2,2.-3.*ES1,2.-3.*ES2)
        else:
            RLM=None
        eyeHorizontalExtentsForMeasure=[]
        eyeWidths=[]
        baudRate=self.baudrate
        UI=1./baudRate
        for eye in eyeVerticalExtentsForMeasurement:
            r=(eye[0]+eye[1])//2
            c=C//2
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
            c=C//2
            while count != C and not found:
                c=(c+1)%C
                if bitmapLog[r][c]!=0:
                    found=True
                else:
                    count+=1
                    endColumn=c
            if (count < C):
                eyeHorizontalExtentsForMeasure.append((startColumn,endColumn))
                eyeWidths.append(count/C*UI)
        def precision_round(number, digits=3):
            if number == None: return number
            power = "{:e}".format(number).split('e')[1]
            return round(number, -(int(power) - digits))
        self.measDict={'Eye':{i:{'Start':{'Bin':eyeHorizontalExtentsForMeasure[i][0],
                                          'Time':precision_round((eyeHorizontalExtentsForMeasure[i][0]-C/2)/C*UI)},
                                 'End':{'Bin':eyeHorizontalExtentsForMeasure[i][1],
                                        'Time':precision_round((eyeHorizontalExtentsForMeasure[i][1]-C/2)/C*UI)},
                                 'Width':{'Bin':(eyeHorizontalExtentsForMeasure[i][1]-eyeHorizontalExtentsForMeasure[i][0]+1),
                                          'Time':precision_round(eyeWidths[i])},
                                 'Low':{'Bin':eyeVerticalExtentsForMeasurement[i][0],
                                        'Volt':precision_round(eyeVerticalExtentsForMeasurement[i][0]/R*deltaV+self.minV)},
                                 'High':{'Bin':eyeVerticalExtentsForMeasurement[i][1],
                                         'Volt':precision_round(eyeVerticalExtentsForMeasurement[i][1]/R*deltaV+self.minV)},
                                 'Mid':{'Bin':int((eyeVerticalExtentsForMeasurement[i][0]+eyeVerticalExtentsForMeasurement[i][1])/2),
                                        'Volt':precision_round(eyeMids[i])},
                                 'Height':{'Bin':(eyeVerticalExtentsForMeasurement[i][1]-eyeVerticalExtentsForMeasurement[i][0]+1),
                                           'Volt':precision_round(eyeHeights[i])},
                                 'AV':{'Volt':precision_round(AV[i])}} for i in range(numberOfEyes)},
                        'Level':{i:{'Min':{'Bin':thresholdExtents[i][0],
                                           'Volt':precision_round(thresholdExtents[i][0]/R*deltaV+self.minV)},
                                    'Max':{'Bin':thresholdExtents[i][1],
                                           'Volt':precision_round(thresholdExtents[i][1]/R*deltaV+self.minV)},
                                    'Delta':{'Bin':(thresholdExtents[i][1]-thresholdExtents[i][0]),
                                             'Volt':precision_round((thresholdExtents[i][1]-thresholdExtents[i][0])/R*deltaV)},
                                    'Mean':{'Bin':int((eyeAverageLevels[i]-self.minV)/deltaV*R+0.5),
                                            'Volt':precision_round(eyeAverageLevels[i])}} for i in range(numberOfEyes+1)},
                        'Linearity':precision_round(EyeLinearity*100.)/100.,
                        'RLM':precision_round(RLM),
                        'VerticalResolution':precision_round((self.maxV-self.minV)/R),
                        'HorizontalResolution':precision_round(UI/C)}
        if SignalIntegrity.App.Project['EyeDiagram.Annotation.Annotate']:
            self.annotationBitmap=np.zeros(self.rawBitmap.shape)
            if SignalIntegrity.App.Project['EyeDiagram.Annotation.MeanLevels']:
                # a line through the levels
                for i in range(len(self.measDict['Level'])):
                    r=self.measDict['Level'][i]['Mean']['Bin']
                    for c in range(C):
                        self.annotationBitmap[r][c]=1
                    if SignalIntegrity.App.Project['EyeDiagram.Annotation.LevelExtents']:
                        # dotted lines at the level edges
                        r = self.measDict['Level'][i]['Min']['Bin']
                        for c in range(0,C,2):
                            self.annotationBitmap[r][c]=1
                        r = self.measDict['Level'][i]['Max']['Bin']
                        for c in range(0,C,2):
                            self.annotationBitmap[r][c]=1
            # lines in the eye
            for i in range(len(self.measDict['Eye'])):
                if SignalIntegrity.App.Project['EyeDiagram.Annotation.EyeWidth']:
                    # horizontal line through the middle of the eye
                    r = self.measDict['Eye'][i]['Mid']['Bin']
                    for c in range(self.measDict['Eye'][i]['Start']['Bin'],self.measDict['Eye'][i]['End']['Bin']):
                        self.annotationBitmap[r][c]=1
                if SignalIntegrity.App.Project['EyeDiagram.Annotation.EyeHeight']:
                    # vertical line through the middle of the eye
                    c = C//2
                    for r in range(self.measDict['Eye'][i]['Low']['Bin'],self.measDict['Eye'][i]['High']['Bin']):
                        self.annotationBitmap[r][c]=1
                if SignalIntegrity.App.Project['EyeDiagram.Annotation.Contours.Show']:
                    if SignalIntegrity.App.Project['EyeDiagram.Annotation.Contours.Which'] == 'All':
                        # develop the extents of the eye openings for each eye in a column (vertical slice)
                        # The assumption is that there is signal or the exterior in the first row.  Stepping into
                        # a dark area from a non-dark area starts an extent and the stepping from a dark area to a
                        # non-dark area ends an extent.
                        darkExtents=[]
                        for c in range(C):
                            counter=None
                            thisExtents=[]
                            for r in range(1,R):
                                if bitmapLog[r][c]==0. and bitmapLog[r-1][c]!=0.:
                                    counter=r
                                elif bitmapLog[r][c]!=0 and bitmapLog[r-1][c]==0:
                                    if counter != None:
                                        thisExtents.append((counter,r))
                            darkExtents.append(thisExtents)
                        # convert the extents into sizes for comparison
                        for c in range(len(darkExtents)):
                            extents=darkExtents[c]
                            for extent in extents:
                                self.annotationBitmap[extent[0]][c]=1
                                self.annotationBitmap[extent[1]][c]=1
                    else:
                        # contour line
                        # walk horizontally looking at the max and min vertical extents
                        r = self.measDict['Eye'][i]['Mid']['Bin']
                        lastrh=None
                        lastrl=None
                        for c in range(self.measDict['Eye'][i]['Start']['Bin'],self.measDict['Eye'][i]['End']['Bin']):
                            rh=r
                            while bitmapLog[rh][c]==0:
                                if rh==R-1:
                                    break
                                rh=rh+1
                            rl=r
                            while bitmapLog[rl][c]==0:
                                if rl==0:
                                    break
                                rl=rl-1
                            if lastrh==None:
                                self.annotationBitmap[rh][c]=1
                                self.annotationBitmap[rl][c]=1
                            else:
                                for rline in range(min(lastrh+1,rh),min(max(lastrh+1,rh)+1,R)):
                                    self.annotationBitmap[rline][c]=1
                                for rline in range(min(lastrl+1,rl),min(max(lastrl+1,rl)+1,R)):
                                    self.annotationBitmap[rline][c]=1
                            lastrh=rh
                            lastrl=rl
                        # walk vertically lookin at the max and min horizontal extents
                        c=C//2
                        lastch=None
                        lastcl=None
                        for r in range(self.measDict['Eye'][i]['Low']['Bin'],self.measDict['Eye'][i]['High']['Bin']):
                            ch=c
                            while bitmapLog[r][ch]==0:
                                if ch==C-1:
                                    break
                                ch=ch+1
                            cl=c
                            while bitmapLog[r][cl]==0:
                                if cl==0:
                                    break
                                cl=cl-1
                            if lastch==None:
                                self.annotationBitmap[r][ch]=1
                                self.annotationBitmap[r][cl]=1
                            else:
                                for cline in range(min(lastch+1,ch),min(max(lastch+1,ch)+1,C)):
                                    self.annotationBitmap[r][cline]=1
                                for cline in range(min(lastcl+1,cl),min(max(lastcl+1,cl)+1,C)):
                                    self.annotationBitmap[r][cline]=1
                            lastch=ch
                            lastcl=cl
