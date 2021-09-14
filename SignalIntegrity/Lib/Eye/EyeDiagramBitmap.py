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
from SignalIntegrity.Lib.TimeDomain.Waveform.TimeDescriptor import TimeDescriptor

import math
import numpy as np
import hashlib

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
                    repr(self.EnhancementSteps)
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

        self.rawBitmap=bitmap

        # don't cache the waveform
        del self.prbswf
        del self.aprbswf
        self.CacheResult()

    def Bitmap(self):
        return self.rawBitmap