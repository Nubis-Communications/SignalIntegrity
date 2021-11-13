"""
EyeDiagramBitmap.py
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

from SignalIntegrity.Lib.CallBacker import CallBacker
from SignalIntegrity.Lib.ResultsCache import ResultsCache
from SignalIntegrity.Lib.TimeDomain.Filters.WaveformTrimmer import WaveformTrimmer
from SignalIntegrity.Lib.TimeDomain.Waveform import TimeDescriptor,Waveform
from SignalIntegrity.Lib.Rat.Rat import Rat

import math
import copy
import numpy as np
import hashlib
import scipy.special

from PIL import Image

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

class EyeDiagramBitmap(CallBacker,ResultsCache):

    def HashValue(self,stuffToHash=''):
        stuffToHash=stuffToHash+repr(self.YAxisMode)+repr(self.YMax)+repr(self.YMin)+\
                    repr(self.NoiseSigma)+repr(self.Rows)+repr(self.Cols)+\
                    repr(self.BaudRate)+repr(self.prbswf)+repr(self.EnhancementMode)+\
                    repr(self.EnhancementSteps)+repr(self.BitsPerSymbol)
        return hashlib.sha256(stuffToHash.encode()).hexdigest()

    def __init__(self,callback=None,
                 cacheFileName=None,
                 YAxisMode='Auto',
                 YMax=None, # ignored if YAxisMode is Auto
                 YMin=None, # ignored if YAxisMode is Auto
                 NoiseSigma=0, # if Auto, can be used to set the axis, otherwise 10% added to each side
                 Rows=None,
                 Cols=None,
                 BaudRate=None,
                 prbswf=None,
                 EnhancementMode='Auto', # can be Auto, Fixed, or None
                 EnhancementSteps=10, # ignored unless EnhancementMode is Fixed
                 BitsPerSymbol=1, # 1 for NRZ, 2 for PAM-4  (3 for PAM-8!?)
                 *args,
                 **kwargs):
        self.YAxisMode=YAxisMode
        self.YMax=YMax
        self.YMin=YMin
        self.NoiseSigma=NoiseSigma
        self.Rows=Rows
        self.Cols=Cols
        self.BaudRate=BaudRate
        self.prbswf=prbswf
        self.EnhancementMode=EnhancementMode
        self.EnhancementSteps=EnhancementSteps
        self.BitsPerSymbol=BitsPerSymbol

        self.BitmapLog=None
        self.measDict=None
        self.annotationBitmap=None
        self.img=None

        CallBacker.__init__(self,callback)
        ResultsCache.__init__(self,'EyeDiagramBitMap',cacheFileName)
        self.rawBitmap=None

        if self.CheckCache():
            self.CallBack(100.0)
            return

        baudRate=BaudRate
        UI=1./baudRate
        R=Rows; C=Cols
        Fs=baudRate*C
        UpsampleFactor=Fs/prbswf.td.Fs

        # The waveform is adapted to the new sample rate.  This puts it on the same sample frame as the original waveform, such that there
        # is the assumption that there is a point at exactly time zero, and that is the center of the unit interval.
        # the amount of points to remove is trimmed from the left to make the very first sample at the center of a unit interval.
        self.aprbswf=prbswf.Adapt(TimeDescriptor(prbswf.td.H,prbswf.td.K*UpsampleFactor,Fs))
        self.aprbswf=WaveformTrimmer(C-int(round((self.aprbswf.td.H-math.floor(self.aprbswf.td.H/UI)*UI)*self.aprbswf.td.Fs)),0).TrimWaveform(self.aprbswf)

        auto=YAxisMode
        noiseSigma=NoiseSigma

        if auto:
            self.maxV=max(self.aprbswf.Values())
            self.minV=min(self.aprbswf.Values())
            if noiseSigma != 0:
                self.maxV=self.maxV+10.*noiseSigma
                self.minV=self.minV-10.*noiseSigma
            else:
                self.maxV=self.maxV+abs(self.maxV-self.minV)*.1
                self.minV=self.minV-abs(self.maxV-self.minV)*.1
        else:
            self.maxV = YMax
            self.minV = YMin

        DeltaV=self.maxV-self.minV
        midBin=C//2

        enhancementMode=EnhancementMode
        if enhancementMode=='Fixed':
            steps=EnhancementSteps
        elif enhancementMode=='Auto':
            steps=R
        else:
            steps=1
        pixelator = Pixelator(R,C,steps,mode=enhancementMode)

        bitmap=np.zeros((R,C))
        ri=(self.aprbswf[0]-self.minV)/DeltaV*R
        ci=(0+midBin)%C
        for k in range(1,self.aprbswf.td.K):
            rf=(self.aprbswf[k]-self.minV)/DeltaV*R
            cf=(k+midBin)%C
            if (not callback is None) and (k//C != (k-1)//C):
                if not callback(k/self.aprbswf.td.K*100.):
                    return
            results=pixelator.Results(ri, ci, rf, cf, k==0)
            for result in results:
                r,c,prob=result[0][0],result[0][1],result[2]
                bitmap[r][c]+=prob
            ri=rf; ci=cf

        self.rawBitmap=bitmap/np.sum(bitmap)*C

        for c in range(C):
            self.rawBitmap[:,c]=self.rawBitmap[:,c]/sum(self.rawBitmap[:,c])

        # don't cache the waveform
        del self.prbswf
        del self.aprbswf
        self.CacheResult()

    def Bitmap(self):
        return self.rawBitmap


    def ApplyJitterNoise(self,
                         NoiseSigma=0.,
                         JitterSigma=0.,
                         DeterministicJitter=0.,
                         MaxPixelsKernel=100000):
        UI=1./self.BaudRate
        deltaT=UI/self.Cols
        deltaY=(self.maxV-self.minV)/self.Rows

        WH=int(math.floor(math.floor(2.*10.*(DeterministicJitter+JitterSigma)/deltaT/2.)*2.)+1.)
        WV=int(math.floor(math.floor(2.*10.*NoiseSigma/deltaY/2.)*2.)+1.)

        if WH*WV > MaxPixelsKernel:
            WH=int(math.floor((WH*math.sqrt(float(MaxPixelsKernel)/float(WH*WV))-1)/2))*2+1
            WV=int(math.floor((WV*math.sqrt(float(MaxPixelsKernel)/float(WH*WV))-1)/2))*2+1

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

        def dnorm(x,mu,sigma):
            res =  cnorm(x+1/2.,mu,sigma)-cnorm(x-1/2.,mu,sigma)
            return res

        # make the Gaussian kernel
        bitmaparray=np.array(self.rawBitmap)
        kernelHarray=np.array([[(dnorm(wh-(WH-1)//2,-DeterministicJitter/deltaT,JitterSigma/deltaT)+dnorm(wh-(WH-1)//2,DeterministicJitter/deltaT,JitterSigma/deltaT))/2.0 for wh in range(WH)]])
        kernelVarray=np.array([[dnorm(wv-(WV-1)//2,0,NoiseSigma/deltaY)] for wv in range(WV)])

        from scipy.ndimage.filters import convolve
        bitmap=convolve(bitmaparray,kernelHarray,mode='wrap')
        bitmap=convolve(bitmap,kernelVarray,mode='constant')
        bitmap=bitmap/np.sum(bitmap)*self.Cols
        self.rawBitmap=bitmap

    def AutoAlign(self,
                  BERForAlignment=-6, # Exponent of probability contour to align on
                  AlignmentMode='Horizontal', # can be 'Horizontal' or 'Vertical'
                  HorizontalAlignment='Middle', # 'Middle' or 'Max' (vertical eye) - alignment will be the horizontal midpoint of one of these two eye possibilities
                  VerticalAlignment='MaxMin', # 'MaxMin' (maximum minimum opening) or 'Max' (maximum opening) 
                  GenerateExtentsOnly=False # if this is True, calculations are made only to obtain the extents, to be used in the measurements
                  ):
        bitmap=self.rawBitmap.copy()
        numberOfEyes=int(2**self.BitsPerSymbol-1)
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
        alignOnTime=(AlignmentMode == 'Horizontal')
        if alignOnTime: # 'Horizontal', meaning midpoint in time in an eye
            # These are the three largest eye openings at the best index in order of appearance
            # remember that the eye is upside down (we're looking from the bottom up
            self.eyeExtentsForAlignment=sorted(sorted(darkExtents[indexOfBestOpening],key = lambda x: x[1]-x[0],reverse=True)[0:numberOfEyes],key = lambda y:y[0])
            # now, for each eye, walk backwards and forwards at each row slice within these extents
            # to find the extents of each eye opening
            rowOfMaxEyeWidth=None
            startColumnofMaxEyeWidth=None
            endColumnofMaxEyeWidth=None
            alignOnMiddleEye=(HorizontalAlignment == 'Middle')
            if alignOnMiddleEye: # 'Middle', meaning horizontal midpoint of middle eye
                eyeExtents=[self.eyeExtentsForAlignment[(2**self.BitsPerSymbol)//2-1]]
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
                    c=(indexOfBestOpening+1)%C
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
            alignMaxMinimum=(VerticalAlignment == 'MaxMin')
            if alignMaxMinimum: # 'MaxMin', meaning max vertical opening of smallest eye
                columnAtEyeCenter=indexOfBestMinimumOpening
            else: # 'Max', meaning max vertical opening of all eyes
                columnAtEyeCenter=indexOfBestOpening

        if GenerateExtentsOnly:
            return
        for r in range(R):
            for c in range(C):
                self.rawBitmap[r][(c+C//2)%C]=bitmap[r][(c+columnAtEyeCenter)%C]
        return

    def Measure(self,
                BERForMeasure=-6, # Exponent of probability contour to measure
                DecisionMode='Mid', # Mid means middle of eye vertically, Best means least likely location
                ):
        bitmap=self.rawBitmap.copy()
        numberOfEyes=int(2**self.BitsPerSymbol-1)
        (R,C)=bitmap.shape
        minValueLog=pow(10.,-20)
        minBER=BERForMeasure; maxBER=BERForMeasure+0.001
        m=1./(maxBER-minBER)
        b=0-minBER*m
        bitmapLog=np.array([[math.log10(max(bitmap[r][c],minValueLog)) for c in range(C)] for r in range(R)])
        bitmapLog=bitmapLog*m+b
        bitmapLog=np.array([[0. if bitmapLog[r][c] < 0 else (1 if bitmapLog[r][c] > 1 else bitmapLog[r][c]) for c in range(C)] for r in range(R)])

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
        # find the best decision points based on probability
        eyeDecisionPoints=[]
        for extent in eyeVerticalExtentsForMeasurement:
            minIndex=None
            minValue=None
            count=0
            for r in range(extent[0],extent[1]+1):
                value=self.rawBitmap[r][c]
                if (minValue == None) or (value<minValue):
                    minValue=value
                    minIndex=r
                    count=1
                elif value==0:
                    count+=1
            eyeDecisionPoints.append(int(minIndex+count//2))
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
        if self.BitsPerSymbol == 2:
            (V0,V1,V2,V3)=(eyeAverageLevels[0],eyeAverageLevels[1],eyeAverageLevels[2],eyeAverageLevels[3])
            Vmid=(V0+V3)/2
            ES1=(V1-Vmid)/(V0-Vmid)
            ES2=(V2-Vmid)/(V3-Vmid)
            RLM=min(3.*ES1,3.*ES2,2.-3.*ES1,2.-3.*ES2)
        else:
            RLM=None
        eyeHorizontalExtentsForMeasure=[]
        eyeWidths=[]
        UI=1./self.BaudRate
        for i in range(len(eyeVerticalExtentsForMeasurement)):
            decision=eyeDecisionPoints[i]
            eye=eyeVerticalExtentsForMeasurement[i]
            r=(eye[0]+eye[1])//2 if DecisionMode == 'Mid' else decision
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
        self.measDict={'R':R,'C':C,'MinV':self.minV,'MaxV':self.maxV,'MinT':-C//2*UI,'MaxT':(C-1)//2*UI,
                       'Eye':{i:{'Start':{'Bin':eyeHorizontalExtentsForMeasure[i][0],
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
                                 'Best':{'Bin':eyeDecisionPoints[i],
                                        'Volt':precision_round(eyeDecisionPoints[i]/R*deltaV+self.minV)},
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
        for i in range(numberOfEyes):
            self.measDict['Eye'][i]['Decision']=self.measDict['Eye'][i]['Mid'] if DecisionMode=='Mid' else self.measDict['Eye'][i]['Best']
        self.BitmapLog = bitmapLog

    def Bathtub(self,
                DecadesFromJoin=0.25,
                MinPointsForFit=6
                ):
        numberOfEyes=int(2**self.BitsPerSymbol-1)
        UI=1./self.BaudRate
        (R,C)=self.rawBitmap.shape
        # build bathtub curve waveforms
        # one long vertical waveform for a bathtub curve
        c=C//2
        # a horizontal bathtub curve waveform for each eye
        x=[self.minV+r/R*(self.maxV-self.minV) for r in range(R)]
        y=[self.rawBitmap[r][c] for r in range(R)]
        self.measDict['Bathtub']={'Vertical':{'Data':{'x':x,'y':y}},
                                  'Horizontal':{}}

        XF=[[1.,v,v**2] for v in x]

        lowerLimit=1e-30
        self.measDict['Bathtub']['Vertical']['Level']={e:{'LeftEst':None,'RightEst':None} for e in range(numberOfEyes+1)}
        # estimate the gaussians for the edges
        try:
            r=0
            maxFit=1e-40
            minFit=0.
            gathering=False
            X=[]; Y=[]; rStart=None; rEnd=None; CF=None
            while r < R:
                if not gathering:
                    if y[r] > minFit:
                        gathering=True
                        rStart=r
                if gathering:
                    if y[r] <= maxFit or len(X) < MinPointsForFit:
                        X.append(XF[r])
                        Y.append([np.log(y[r])])
                        rEnd=r
                    else:
                        break
                r=r+1
            if r != R:
                X=np.array(X); Y=np.array(Y)
                CF = np.linalg.inv(np.transpose(X).dot(X)).dot(np.transpose(X)).dot(Y)
                self.measDict['Bathtub']['Vertical']['Level'][0]['LeftEst']={'Start':{'Bin':rStart},'End':{'Bin':rEnd},
                            'Est':{'Coef':CF.tolist(),'Valid':CF[2][0]<0,
                                   'Wf':{'x':[x[v] for v in range(rStart,rEnd+1)],'y':[np.exp(v[0]) for v in X.dot(CF)]}}}
            else:
                raise
        except Exception as ex:
            print(ex)
            self.measDict['Bathtub']['Vertical']['Level'][0]['LeftEst']=\
                    {'Start':{'Bin':rStart},'End':{'Bin':rEnd},'Est':{'Coef':None,'Valid':False,'Wf':None}}

        try:
            r=R-1
            maxFit=1e-40
            minFit=0.
            gathering=False
            X=[]; Y=[]; rStart=None; rEnd=None; CF=None
            while r > 0:
                if not gathering:
                    if y[r] > minFit:
                        gathering=True
                        rStart=r
                if gathering:
                    if y[r] <= maxFit or len(X) < MinPointsForFit:
                        X.append(XF[r])
                        Y.append([np.log(y[r])])
                        rEnd=r
                    else:
                        break
                r=r-1
            if r > 0:
                X=np.array(X); Y=np.array(Y)
                CF = np.linalg.inv(np.transpose(X).dot(X)).dot(np.transpose(X)).dot(Y)
                self.measDict['Bathtub']['Vertical']['Level'][numberOfEyes]['RightEst']={'Start':{'Bin':rStart},'End':{'Bin':rEnd},
                            'Est':{'Coef':CF.tolist(),'Valid':CF[2][0]<0,
                                   'Wf':{'x':[x[v] for v in range(rEnd,rStart+1)],'y':[np.exp(v[0]) for v in reversed(X.dot(CF).tolist())]}}}
            else:
                raise
        except Exception as ex:
            print(ex)
            self.measDict['Bathtub']['Vertical']['Level'][numberOfEyes]['RightEst']=\
                {'Start':{'Bin':rStart},'End':{'Bin':rEnd},'Est':{'Coef':None,'Valid':False,'Wf':None}}

        for e in range(len(self.measDict['Eye'])):
            maxFit=1e-40
            minFit=1e-6
            minProbability=y[self.measDict['Eye'][e]['Decision']['Bin']]
            if y[self.measDict['Eye'][e]['Decision']['Bin']]==0: # there's a hole in the middle
                minFit=0.
            else:
                minFit=pow(10.,np.log10(minProbability)+DecadesFromJoin)
            try:
                r=self.measDict['Eye'][e]['Decision']['Bin']
                gathering=False
                X=[]; Y=[]; rStart=None; rEnd=None; CF=None
                while r > 0:
                    if not gathering:
                        if y[r] > minFit:
                            gathering=True
                            rStart=r
                    if gathering:
                        if y[r] <= maxFit or len(X) < MinPointsForFit:
                            X.append(XF[r])
                            Y.append([np.log(y[r])])
                            rEnd=r
                        else:
                            break
                    r=r-1
                if r != 0:
                    X=np.array(X); Y=np.array(Y)
                    CF = np.linalg.inv(np.transpose(X).dot(X)).dot(np.transpose(X)).dot(Y)
                    self.measDict['Bathtub']['Vertical']['Level'][e]['RightEst']={'Start':{'Bin':rStart},
                                'Est':{'Coef':CF.tolist(),'Valid':CF[2][0]<0,
                                       'Wf':{'x':[x[v] for v in range(rEnd,rStart+1)],'y':[np.exp(v[0]) for v in reversed(X.dot(CF).tolist())]}}}
                else:
                    raise
            except Exception as ex:
                print(ex)
                self.measDict['Bathtub']['Vertical']['Level'][e]['RightEst']=\
                    {'Start':{'Bin':rStart},'End':{'Bin':rEnd},'Est':{'Coef':None,'Valid':False,'Wf':None}}

            try:
                r=self.measDict['Eye'][e]['Decision']['Bin']
                gathering=False
                X=[]; Y=[]; rStart=None; rEnd=None; CF=None
                while r < R:
                    if not gathering:
                        if y[r] > minFit:
                            gathering=True
                            rStart=r
                    if gathering:
                        if y[r] <= maxFit  or len(X) < MinPointsForFit:
                            X.append(XF[r])
                            Y.append([np.log(y[r])])
                            rEnd=r
                        else:
                            break
                    r=r+1
                if r != R:
                    X=np.array(X)
                    Y=np.array(Y)
                    CF = np.linalg.inv(np.transpose(X).dot(X)).dot(np.transpose(X)).dot(Y)
                    self.measDict['Bathtub']['Vertical']['Level'][e+1]['LeftEst']={'Start':{'Bin':rStart},'End':{'Bin':rEnd},
                                'Est':{'Coef':CF.tolist(),'Valid':CF[2][0]<0,
                                       'Wf':{'x':[x[v] for v in range(rStart,rEnd+1)],'y':[np.exp(v[0]) for v in X.dot(CF)]}}}
                else:
                    raise
            except Exception as ex:
                print(ex)
                self.measDict['Bathtub']['Vertical']['Level'][e+1]['LeftEst']=\
                    {'Start':{'Bin':rStart},'End':{'Bin':rEnd},'Est':{'Coef':None,'Valid':False,'Wf':None}}

        # now, gather all of the curve fits and actual data into probability histograms that span the entire
        # eye
        td=TimeDescriptor(self.minV,R,R/(self.maxV-self.minV))
        for t in range(numberOfEyes+1):
            try:
                # calculate the entire left estimate
                if self.measDict['Bathtub']['Vertical']['Level'][t]['LeftEst']['Est']['Valid']:
                    yleft=[np.exp(v[0]) for v in np.array(XF).dot(np.array(self.measDict['Bathtub']['Vertical']['Level'][t]['LeftEst']['Est']['Coef']))]
                else:
                    yleft=[0. for _ in range(R)]
                yleftStart=self.measDict['Bathtub']['Vertical']['Level'][t]['LeftEst']['Start']['Bin']
                if self.measDict['Bathtub']['Vertical']['Level'][t]['RightEst']['Est']['Valid']:
                    yright=[np.exp(v[0]) for v in np.array(XF).dot(np.array(self.measDict['Bathtub']['Vertical']['Level'][t]['RightEst']['Est']['Coef']))]
                else:
                    yright=[0. for _ in range(R)]
                yrightStart=self.measDict['Bathtub']['Vertical']['Level'][t]['RightEst']['Start']['Bin']
                yCombo=[yleft[r] if r < yleftStart else yright[r] if r > yrightStart else y[r] for r in range(R)]
                self.measDict['Bathtub']['Vertical']['Level'][t]['Hist']=yCombo
                # compute the CDF from the left and the right
                self.measDict['Bathtub']['Vertical']['Level'][t]['CDFFromLeft']=Waveform(td,yCombo).Integral(addPoint=False,scale=False).Values()
                self.measDict['Bathtub']['Vertical']['Level'][t]['CDFFromRight']=[v for v in reversed(Waveform(td,[v for v in reversed(yCombo)]).Integral(addPoint=False,scale=False).Values())]
            except Exception as ex:
                print(ex)
                pass

        # SymbolProbability[s] is the probabability that a symbol sent was sent as symbol s
        SymbolProbability=[sum(self.measDict['Bathtub']['Vertical']['Level'][s]['Hist']) for s in range(numberOfEyes+1)]
        DecisionLevel=[self.measDict['Eye'][e]['Decision']['Bin'] for e in range(numberOfEyes)]
        LessThanCDF=[self.measDict['Bathtub']['Vertical']['Level'][t]['CDFFromLeft'] for t in range(numberOfEyes+1)]
        GreaterThanCDF=[self.measDict['Bathtub']['Vertical']['Level'][t]['CDFFromRight'] for t in range(numberOfEyes+1)]
        # SymbolLessThanDecisionLevel[s][t] is the probability that a symbol transmitted as s is lower than decision threshold t
        SymbolLessThanDecisionLevel=[[(LessThanCDF[b][DecisionLevel[t]] if t < numberOfEyes else LessThanCDF[b][-1])/SymbolProbability[b] for t in range(numberOfEyes+1)] for b in range(numberOfEyes+1)]
        # SymbolGreaterThanDecisionLevel[s][t] is the probability that a symbol transmitted as s is higher than decision threshold t
        SymbolGreaterThanDecisionLevel=[[(GreaterThanCDF[b][DecisionLevel[t-1]] if t > 0 else GreaterThanCDF[b][0])/SymbolProbability[b] for t in range(numberOfEyes+1)] for b in range(numberOfEyes+1)]
        # SymbolInterpretedAsOther[r][c] is the probability that a symbol transmitted as r was interpreted as symbol c
        SymbolInterpretedAsOther=[[SymbolLessThanDecisionLevel[r][c]*SymbolGreaterThanDecisionLevel[r][c] for c in range(numberOfEyes+1)] for r in range(numberOfEyes+1)]
        # SymbolErrorRatePerSymbol[s] is the probability that a symbol transmitted as s was interpreted incorrectly
        SymbolErrorRatePerSymbol=[sum([SymbolInterpretedAsOther[r][c] if r!=c else 0. for c in range(numberOfEyes+1)]) for r in range(numberOfEyes+1)]
        NominalSymbolErrorRate=sum([SymbolErrorRatePerSymbol[s]*1./(numberOfEyes+1) for s in range(numberOfEyes+1)])
        MeasuredSymbolErrorRate=sum([SymbolErrorRatePerSymbol[s]*SymbolProbability[s] for s in range(numberOfEyes+1)])

        #normal coding
        SymbolCode=[s for s in range(numberOfEyes+1)]
        BitChanges=[[sum([int(v) for v in bin(SymbolCode[r]^SymbolCode[c])[2:]]) for c in range(numberOfEyes+1)] for r in range(numberOfEyes+1)]
        BitErrorRatePerSymbol=[sum([SymbolInterpretedAsOther[r][c]*BitChanges[r][c]/self.BitsPerSymbol if r!=c else 0. for c in range(numberOfEyes+1)]) for r in range(numberOfEyes+1)]
        NominalBitErrorRate=sum([BitErrorRatePerSymbol[s]*1./(numberOfEyes+1) for s in range(numberOfEyes+1)])
        MeasuredBitErrorRate=sum([BitErrorRatePerSymbol[s]*SymbolProbability[s] for s in range(numberOfEyes+1)])

        # this is the formula for gray coding -- each code change changes by only one bit
        GrayCodes=[0 if b==0 else b^(b>>1) for b in range(numberOfEyes+1)]
        GrayCodeBitChanges=[[sum([int(v) for v in bin(GrayCodes[r]^GrayCodes[c])[2:]]) for c in range(numberOfEyes+1)] for r in range(numberOfEyes+1)]
        GrayCodeBitErrorRatePerSymbol=[sum([SymbolInterpretedAsOther[r][c]*GrayCodeBitChanges[r][c]/self.BitsPerSymbol if r!=c else 0. for c in range(numberOfEyes+1)]) for r in range(numberOfEyes+1)]
        GrayCodeNominalBitErrorRate=sum([GrayCodeBitErrorRatePerSymbol[s]*1./(numberOfEyes+1) for s in range(numberOfEyes+1)])
        GrayCodeMeasuredBitErrorRate=sum([GrayCodeBitErrorRatePerSymbol[s]*SymbolProbability[s] for s in range(numberOfEyes+1)])

        self.measDict['Probabilities']={'SymbolCodes':SymbolCode,'GrayCodes':GrayCodes,'Interpretation':SymbolInterpretedAsOther,'Symbol':SymbolProbability,
                                        'ErrorRate':{'Symbol':{'PerSymbol':SymbolErrorRatePerSymbol,'Nominal':NominalSymbolErrorRate,'Measured':MeasuredSymbolErrorRate},
                                                     'Bit':{'Standard':{'PerSymbol':BitErrorRatePerSymbol,'Nominal':NominalBitErrorRate,'Measured':MeasuredBitErrorRate},
                                                            'Gray':{'PerSymbol':GrayCodeBitErrorRatePerSymbol,'Nominal':GrayCodeNominalBitErrorRate,'Measured':GrayCodeMeasuredBitErrorRate}}}}
        # horizontal
        td=TimeDescriptor(-0.5*UI,C,C/UI)
        for e in range(numberOfEyes):
            r=self.measDict['Eye'][e]['Decision']['Bin']
            self.measDict['Bathtub']['Horizontal'][e]={'Data':Waveform(td,[self.rawBitmap[r][c] for c in range(C)])}

    def Annotations(self,
                    MeanLevels=True,
                    LevelExtents=True,
                    EyeWidth=True,
                    EyeHeight=True,
                    Contours=True,
                    WhichContours='Eye' # 'Eye' or 'All'
                    ):
        # annotations
        (R,C)=self.rawBitmap.shape
        self.annotationBitmap=np.zeros(self.rawBitmap.shape)
        if MeanLevels:
            # a line through the levels
            for i in range(len(self.measDict['Level'])):
                r=self.measDict['Level'][i]['Mean']['Bin']
                for c in range(C):
                    self.annotationBitmap[r][c]=1
                if LevelExtents:
                    # dotted lines at the level edges
                    r = self.measDict['Level'][i]['Min']['Bin']
                    for c in range(0,C,2):
                        self.annotationBitmap[r][c]=1
                    r = self.measDict['Level'][i]['Max']['Bin']
                    for c in range(0,C,2):
                        self.annotationBitmap[r][c]=1
        # lines in the eye
        for i in range(len(self.measDict['Eye'])):
            if EyeWidth:
                # horizontal line through the middle of the eye
                r = self.measDict['Eye'][i]['Decision']['Bin']
                for c in range(self.measDict['Eye'][i]['Start']['Bin'],self.measDict['Eye'][i]['End']['Bin']):
                    self.annotationBitmap[r][c]=1
            if EyeHeight:
                # vertical line through the middle of the eye
                c = C//2
                for r in range(self.measDict['Eye'][i]['Low']['Bin'],self.measDict['Eye'][i]['High']['Bin']):
                    self.annotationBitmap[r][c]=1
            if Contours:
                if WhichContours == 'All':
                    # develop the extents of the eye openings for each eye in a column (vertical slice)
                    # The assumption is that there is signal or the exterior in the first row.  Stepping into
                    # a dark area from a non-dark area starts an extent and the stepping from a dark area to a
                    # non-dark area ends an extent.
                    darkExtents=[]
                    for c in range(C):
                        counter=None
                        thisExtents=[]
                        for r in range(1,R):
                            if self.BitmapLog[r][c]==0. and self.BitmapLog[r-1][c]!=0.:
                                counter=r
                            elif self.BitmapLog[r][c]!=0 and self.BitmapLog[r-1][c]==0:
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
                    r = self.measDict['Eye'][i]['Decision']['Bin']
                    lastrh=None
                    lastrl=None
                    for c in range(self.measDict['Eye'][i]['Start']['Bin'],self.measDict['Eye'][i]['End']['Bin']):
                        rh=r
                        while self.BitmapLog[rh][c]==0:
                            if rh==R-1:
                                break
                            rh=rh+1
                        rl=r
                        while self.BitmapLog[rl][c]==0:
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
                    # walk vertically looking at the max and min horizontal extents
                    c=C//2
                    lastch=None
                    lastcl=None
                    for r in range(self.measDict['Eye'][i]['Low']['Bin'],self.measDict['Eye'][i]['High']['Bin']):
                        ch=c
                        while self.BitmapLog[r][ch]==0:
                            if ch==C-1:
                                break
                            ch=ch+1
                        cl=c
                        while self.BitmapLog[r][cl]==0:
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

    def CreateImage(self,
                    LogIntensity=False,
                    MinExponentLogIntensity=-6.,
                    MaxExponentLogIntensity=0,
                    NumUI=1,
                    Saturation=20.,
                    InvertImage=True,
                    Color='#ffffff',
                    AnnotationColor='#000000',
                    ScaleX=100.,
                    ScaleY=100.,
                    ):
        bitmap=self.Bitmap().copy()
        (R,C)=bitmap.shape
        if LogIntensity:
            bitmap=bitmap/np.sum(bitmap)*C
            minBER=max(MinExponentLogIntensity,-20)
            maxBER=max(minBER,MaxExponentLogIntensity)
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

        numUI=int(NumUI+0.5)
        if numUI>1:
            bitmap=np.array([[bitmap[r][c%C] for c in range(C*numUI)] for r in range(R)])
            if not self.annotationBitmap is None:
                annotationBitmap=np.array([[self.annotationBitmap[r][c%C] for c in range(C*numUI)] for r in range(R)])
        elif not self.annotationBitmap is None:
            annotationBitmap=self.annotationBitmap

        C=C*numUI

        if not LogIntensity:
            P=math.log10(min(0.99,max(0.001,Saturation/100.)))/math.log10(0.5)
            bitmap=(((bitmap.astype(float)*-1.0+maxValue)/maxValue)**P*255.0).astype(int)

        if InvertImage:
            bitmap=255-bitmap

        color=True
        if color:
            try:
                color=int(Color.strip('#'),16)
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
                    color=int(AnnotationColor.strip('#'),16)
                    b=color%256; g=(color//256)%256; r=(color//(256*256))%256
                except:
                    r=256; g=256; b=256

                abm=np.flipud(annotationBitmap)
                for row in range(rgbArray.shape[0]):
                    for col in range(rgbArray.shape[1]):
                        if abm[row][col] != 0:
                            rgbArray[row][col][0]=r
                            rgbArray[row][col][1]=g
                            rgbArray[row][col][2]=b

            self.img = Image.fromarray(rgbArray)
        else:
            self.img=Image.fromarray(np.squeeze(np.asarray(np.array(bitmap))).astype(np.uint8))

        C=int(C*ScaleX/100.); R=int(R*ScaleY/100.)
        self.img=self.img.resize((C,R))
        self.image=copy.deepcopy(self.img)

    def Penalties(self,
                  NoisePenaltydB=0
                  ):
        if self.NoiseSigma == 0:
            if 'Penalties' in self.measDict.keys():
                del self.measDict['Penalties']
        else:
            numLevels=2**self.BitsPerSymbol
            numEyes=numLevels-1
            numInnerLevels=numLevels-2
            numOuterLevels=numLevels-numInnerLevels
            numErrorCases=numOuterLevels+2*numInnerLevels
            # expected BER is 1/BPS * 1/levels * cases * 1/2 * erfc( outer oma / eyes / sqrt(2) / 2 / sigma of noise )
            # for NRZ this is 1/1 * 1/2 * 2 * 1/2 *erfc( OMA/1/sqrt(2)/2/sigma) = 1/2 * erfc( OMA/sqrt(2)/2/sigma)
            # for PAM-4 this is 1/2 * 1/4 * 6 * 1/2 * erfc( OMA/3/sqrt(2)/2/sigma) = 3/8 * erfc( OMA/6/sqrt(2)/sigma )
            # for PAM-8 this is 1/3 * 1/8 * 14 *1/2 * erfc( OMA/7/sqrt(2)/2/sigma ) =  7/24 * erfc( OMA/14/sqrt(2)/sigma )
            # we simplify this to F * erfc( 1./sqrt(2) * OMA/2/D/sigma )
            # where OMA/2/D/sigma is effectively the SNR
            F= 1./self.BitsPerSymbol * 1./numLevels * numErrorCases * 1./2
            (FN,FD)=Rat(F)
            D = numEyes

            PH=self.measDict['Level'][len(self.measDict['Level'])-1]['Mean']['Volt']
            PL=self.measDict['Level'][0]['Mean']['Volt']
            OMA=PH-PL
            BERmeas=self.measDict['Probabilities']['ErrorRate']['Bit']['Gray']['Measured']

            NoisePenalty=10**(NoisePenaltydB/10.)

            QFactorExpected=OMA/2/D/self.NoiseSigma*NoisePenalty
            BERexpected=F*scipy.special.erfc(1./math.sqrt(2.)*QFactorExpected)
            QFactorExpecteddB=10.*math.log10(QFactorExpected)
            QFactor=scipy.special.erfcinv(BERmeas/F)*math.sqrt(2)
            QFactordB=10.*math.log10(QFactor)
            TxPenalty=QFactorExpecteddB-QFactordB
            self.measDict['Penalties']={'PH':PH,'PL':PL,'MA':OMA,'QFactorExpected':QFactorExpected,'QFactorExpecteddB':QFactorExpecteddB,
                                        'BERMeasured':BERmeas,'BERExpected':BERexpected,
                                        'QFactor':QFactor,'QFactordB':QFactordB,'TxPenalty':TxPenalty,
                                        'NoiseSigma':self.NoiseSigma,'NoisePenalty':NoisePenaltydB,
                                        'Levels':{'Total':numLevels,'Inner':numInnerLevels,'Outer':numOuterLevels},
                                        'Eyes':numEyes,'ErrorCases':numErrorCases,
                                        'F':{'Numerical':F,'Numerator':FN,'Denominator':FD},
                                        'D':D}
