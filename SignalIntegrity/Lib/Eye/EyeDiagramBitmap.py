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
        C=self.columns
        steps=self.step if not self.auto else max(1,min(int(math.ceil(2*abs(rf-ri))),self.step))
        if ci>cf: cf=cf+C
        cspan=cf-ci
        rspan=rf-ri
        c=[n/steps*cspan+ci for n in range(steps+1)]
        r=[n/steps*rspan+ri for n in range(steps+1)]
        results=[]
        for n in range(steps+1):
            if n!=0 or useFirst:
                results.extend(self.Hits(r[n],c[n]))
        return results

class EyeDiagramBitmap(CallBacker,ResultsCache):
    """Generates the eye diagram bitmap and many associated measurements from it
        @note After construction, there are limitations on the order of further downstream processing.  The
        recommended order is:
        1.  Constructor
        2.  ApplyJitterNoise
        3.  AutoAlign
        4.  Measure
        5.  Bathtub
        6.  Annotations
        7.  CreateImage
        """
    def HashValue(self,stuffToHash=''):
        """Generates the hash for a definition.  
        It is formed by hashing the bitmap definition with whatever else is hashed.
        @param stuffToHash repr of stuff to hash
        @remark derived classes should override this method and call the base class HashValue with their stuff added
        @return integer hash value
        """
        stuffToHash=stuffToHash+repr(self.YAxisMode)+repr(self.YMax)+repr(self.YMin)+\
                    repr(self.RowsSpecified)+repr(self.Cols)+repr(Waveform.adaptionStrategy)+\
                    repr(self.BaudRate)+repr(self.prbswf)+repr(self.EnhancementMode)+\
                    repr(self.EnhancementSteps)+repr(self.BitsPerSymbol)
        return hashlib.sha256(stuffToHash.encode()).hexdigest()

    def __init__(self,callback=None,
                 cacheFileName=None,
                 YAxisMode='Auto',
                 YMax=None, # ignored if YAxisMode is Auto
                 YMin=None, # ignored if YAxisMode is Auto
                 Rows=None,
                 Cols=None,
                 BaudRate=None,
                 prbswf=None,
                 EnhancementMode='Auto', # can be Auto, Fixed, or None
                 EnhancementSteps=10, # ignored unless EnhancementMode is Fixed
                 BitsPerSymbol=1, # 1 for NRZ, 2 for PAM-4  (3 for PAM-8!?)
                 ):
        """Constructor
        Attempts to generate an eye diagram bitmap from the definition provided.  The bitmap generated here is
        not aligned -- it assumes that the unit interval starts at zero time. (see AutoAlign for alignment).
        This class allows for caching of the bitmap if the cacheFileName is provided.
        @param cacheFileName string file name (defaults to None) containing the base cached file name.
        Usually, this file name is the name of the project file joined to the name of the waveform with an
        underscore.
        @param YAxisMode String, 'Auto' or 'Fixed' (defaults to 'Auto') defining the method of computing the
        y axis extents for the eye diagram.  'Auto' means to generate this axis depending on the extents of
        the input waveform.  'Fixed' means that these extents are defined in the
        YMax and YMin arguments.  'Auto' places the y axis such that it is 10% beyond the min and max extents of
        the waveform.
        @param YMax float, defaults to None, defining the upper extent of the y-axis in the bitmap when YAxisMode
        is provided as 'Fixed'.  If YAxisMode is auto, this parameter is ignored.
        @param YMin float, defaults to None, defining the lower extent of the y-axis in the bitmap when YAxisMode
        is provided as 'Fixed'.  If YAxisMode is auto, this parameter is ignored.
        @param Rows int, defaults to None, defining the number of rows in the eye diagram bitmap.
        @param Cols int, defaults to None, defining the number of columns in the eye diagram bitmap.
        @param Baudrate float, defaults to None, Baud or symbol rate for the waveform.
        @param prbswf instance of class Waveform, defaults to None, containing the serial data waveform used
        to generate the bitmap.
        @param EnhancementMode string, defaults to 'Auto', containing the enhancement mode -- can be 'Auto',
        'Fixed', or 'None'.  The eye diagram is generated from a waveform that is upsampled to a
        rate such that every point falls in a column of the bitmap.  When 'None' is specified, for each point,
        the row is calculated (usually a probability straddling two rows) and the probability is counted.
        Sometimes, the waveform transitions multiple rows in between columns and this can lead to bitmaps with
        vertical holes.  This is not only visually undesirable but can play havoc with the measurements.  When
        'Fixed' is specified, for every point, the steps provided in EnhancementSteps is used.  This is slow and
        not really advised.  'Auto' strikes a balance and calculates how many rows have been traversed and
        calculates a step amount to fill in about two steps per row.  'Auto' therefore dynamically adjusts the
        step size and is the recommended mode.
        @param EnhancementSteps int, defaults to 10, fixed number of steps to be used in 'Fixed' EnhancementMode.
        @param BitsPerSymbol int, defaults to 1, number of bits per symbol.  One bit per symbol is NRZ, or PAM-2.
        Two bits per symbol is PAM-4, etc.  

        At the end of construction, the bitmap can be accessed through a call to Bitmap.  
        The construction initializes several member variables that contain computed or partially computed results
        as a result of further processing.  These are:
        *  self.BitmapLog - the logarithmic bitmap which is calculated in the call to Measure.
        *  self.measDict - the dictionary containing the measurement and bathtub curve calculation results
        produced in calls to Measure and Bathtub.
        *  self.annotationBitmap - the bitmap that is overlaid containing annotations on the eye created in the
        call to Annotations..
        *  self.img - the actual bitmap picture created in the call to CreateImage.  

        @note After construction, there are limitations on the order of further downstream processing.  The
        recommended order is:
        1.  Constructor
        2.  ApplyJitterNoise
        3.  AutoAlign
        4.  Measure
        5.  Bathtub
        6.  Annotations
        7.  CreateImage
        """
        self.YAxisMode=YAxisMode
        self.YMax=YMax
        self.YMin=YMin
        self.RowsSpecified=Rows
        self.Cols=Cols
        self.BaudRate=BaudRate
        self.prbswf=prbswf # saved only for generating hash value
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
        aprbswf=prbswf.Adapt(TimeDescriptor(prbswf.td.H,prbswf.td.K*UpsampleFactor,Fs))
        aprbswf=WaveformTrimmer(C-int(round((aprbswf.td.H-math.floor(aprbswf.td.H/UI)*UI)*aprbswf.td.Fs)),0).TrimWaveform(aprbswf)

        if YAxisMode=='Auto':
            maxV=max(aprbswf.Values())
            minV=min(aprbswf.Values())
            self.maxV=maxV+abs(maxV-minV)*.1
            self.minV=minV-abs(maxV-minV)*.1
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
        ri=(aprbswf[0]-self.minV)/DeltaV*R
        ci=(0+midBin)%C
        for k in range(1,aprbswf.td.K):
            rf=(aprbswf[k]-self.minV)/DeltaV*R
            cf=(k+midBin)%C
            if (not callback is None) and (k//C != (k-1)//C):
                if not callback(k/aprbswf.td.K*100.):
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
        self.CacheResult()

    def Bitmap(self):
        """Returns the raw bitmap
        """
        return self.rawBitmap

    def ApplyJitterNoise(self,
                         NoiseSigma=0.,
                         JitterSigma=0.,
                         DeterministicJitter=0.,
                         MaxPixelsKernel=100000):
        """Applies jitter and/or noise to the eye diagram bitmap
        @param NoiseSigma float, defaults to 0, amount of rms vertical noise to apply.
        @param JitterSigma float, defaults to 0, amount of rms horizontal jitter to apply.
        @param DeterministicJitter float, defaults to 0, amount of deterministic jitter to apply
        horizontally.
        @param MaxPixelsKernel int, defaults to 100000, maximum number of pixels in kernel  

        Noise and jitter are applied by constructing a kernel and then convolving this kernel with
        the eye diagram bitmap.  The kernel itself is a convolution of a vertical histogram, containing
        the Gaussian distributed vertical noise and a horizontal histogram, containing the jitter.
        The jitter histogram is also, itself, a convolution of a dual-Dirac, whose pk-pk separation is
        twice the amount of deterministic jitter specified, with a Guassian distribution representing
        the jitter specified.  
        The kernel generated covers 10 standard deviations in both vertical and horizontal direction.
        As a protection against absurd numbers for jitter and noise, a check is made that the number of
        points in the kernel does not exceed a gigantic number.  If the kernel exceeds this amount, it
        is truncated.  
        When this function concludes, the side effect is that the rawBitmap member variable is updated
        with a new bitmap representing the noise and jitter addition effect.
        @remark The shape of the bitmap is adjusted by padding rows based on the amount of vertical noise
        added.
        """
        UI=1./self.BaudRate
        deltaT=UI/self.Cols
        deltaY=(self.maxV-self.minV)/self.RowsSpecified

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

        # trim away the edges of the vertical part of the kernel that is containing zeros to save time
        for vertStart in range(kernelVarray.shape[0]):
            if kernelVarray[vertStart][0]!=0:
                break
        for vertEnd in range(kernelVarray.shape[0]):
            if kernelVarray[kernelVarray.shape[0]-1-vertEnd][0]!=0:
                vertEnd=kernelVarray.shape[0]-1-vertEnd
                break
        kernelVarray=kernelVarray[vertStart:vertEnd,:]

        # trim away the edges of the horizontal part of the kernel that is containing zeros to save time
        for horStart in range(kernelHarray.shape[1]):
            if kernelHarray[0][horStart]!=0:
                break
        for horEnd in range(kernelHarray.shape[1]):
            if kernelHarray[0][kernelHarray.shape[1]-1-horEnd]!=0:
                horEnd=kernelHarray.shape[1]-1-horEnd
                break
        kernelHarray=kernelHarray[:,horStart:horEnd]

        # pad the bitmap array to encompass the vertical size of the kernel
        rowsToPad=min(kernelVarray.shape[0],self.RowsSpecified)
        if rowsToPad > 0:
            padding=np.zeros((rowsToPad,self.Cols))
            bitmaparray=np.vstack((padding,bitmaparray,padding))
            #self.RowsSpecified+=rowsToPad*2
            self.minV-=rowsToPad*deltaY
            self.maxV+=rowsToPad*deltaY

        from scipy.ndimage.filters import convolve
        bitmap=convolve(bitmaparray,kernelHarray,mode='wrap')
        bitmap=convolve(bitmap,kernelVarray,mode='constant')
        bitmap=bitmap/np.sum(bitmap)*self.Cols
        self.rawBitmap=bitmap

    def AutoAlign(self,
                  BERForAlignment=-3, # Exponent of probability contour to align on
                  AlignmentMode='Horizontal', # can be 'Horizontal' or 'Vertical'
                  HorizontalAlignment='Middle', # 'Middle' or 'Max' (vertical eye) - alignment will be the horizontal midpoint of one of these two eye possibilities
                  VerticalAlignment='MaxMin', # 'MaxMin' (maximum minimum opening) or 'Max' (maximum opening)
                  ):
        """Automatically align the eye diagram
        @param BERForAlignment float, defaults to -3, exponent of the probability contour to align on.
        @param AlignmentMode string, either 'Horizontal' or 'Vertical', defaults to 'Horizontal', defining the alignment mode.
        @param HorizontalAlignment string, either 'Middle' or 'Max' , defaults to 'Middle', defining the horizontal alignment mode.
        @param VerticalAlignment string, either 'MaxMin' or 'Max', defaults to MaxMin, defining the vertical alignment mode.  

        Alignment is made by considering contours that define the probability specified by the BERForAlignment.  While not technically
        a BER, it is the probability contour inside of which, all hits are lower probability.  All measurements of vertical height and
        horizontal width are taken on these contours produced.   
        Alignment modes are a combination of the three alignment mode specifications:
        | AlignmentMode | HorizontalAlignment | VerticalAlignment | Definition                                                                                  |
        |:-------------:|:-------------------:|:-----------------:|:--------------------------------------------------------------------------------------------|
        | Horizontal    | Middle              | N/A               | The center of the eye is found by first computing the widest horizontal opening of the middle eye, then computing the horizontal midpoint.|
        | Horizontal    | Max                 | N/A               | The center of the eye is found by first computing the widest horizontal opening of the widest eye, then computing the horizontal midpoint.|
        | Vertical      | N/A                 | MaxMin            | The center of the eye is found by finding the horizontal location where the vertical opening is maximized for the narrowest eye.          |
        | Vertical      | N/A                 | Max               | The center of the eye is found by finding the horizontal location where the vertical opening is maximized for any eye.                    |
        The side effect of this function is for the rawBitmap member variable to be replaced with a new bitmap containing the aligned eye diagram.
        """
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

        for r in range(R):
            for c in range(C):
                self.rawBitmap[r][(c+C//2)%C]=bitmap[r][(c+columnAtEyeCenter)%C]
        return

    def Measure(self,
                BERForMeasure=-6, # Exponent of probability contour to measure
                DecisionMode='Mid', # Mid means middle of eye vertically, Best means least likely location
                ):
        """Computes measurements on the eye diagram
        @param BERForMeasure float, defaults to -6, exponent of probability contour in eye to make measurements on.
        @param DecisionMode string, 'Mid' or 'Best', defaults to 'Mid' to determine where the decision point is.
        If 'Mid', the decision point is the vertical middle of the eye.  If 'Best' is specified, it is the least likey
        point in the middle of the eye.  If the probability goes to zero in the middle, it is the midpoint of the middle
        zero locations.  

        Measurements are made by first determining a probablity contour in the eye such that everything inside the contour
        is lower probability than the contour edge, which is above the probability of the BERForMeasure.  The vertical extents
        of the contour (the eye height) is the length of the vertical line in the exact center of the eye diagram.  The horizontal
        extents of the contour (the eye width) are the lengths of the horizontal line at the decision point, specified by the
        DecisionMode.  

        Upon completion, the member variable measDict contains a dictionary with the following elements:
        * R - Rows in the bitmap.
        * C - Columns in the bitmap.
        * MinV - Voltage defined by row 0.
        * MaxV - Voltage defined by the maximum row.
        * MinT - Time defined by the column 0.
        * MaxT - Time defined by the last column.
        * BERForMeasure - BER, or probability, for contour for all of the eye measurements.
        * Eye - An array of parameters, one for each eye containing:
            - Start - a dictionary containing Bin and Time defining the pixel column of the horizontal start of the eye.
            - End - a dictionary containing Bin and Time defining the pixel column of the horizontal end of the eye.
            - Width - a dictionary containing the Bin and Time width of the eye.
            - High - a dictionary containing the Bin and Volt defining the pixel row of the vertical top of the eye.
            - Low - a dictionary containing the Bin and Volt defining the pixel row of the vertical bottom of the eye.
            - Mid - a dictionary containing the Bin and Volt defining the pixel row of the vertical middle of the eye.
            - Best - a dictionary containing the Bin and Volt defining the pixel row of the best decision point for the eye.
            - Height - a dictionary containing the Bin and Volt defining the vertical height of the eye.
            - AV - a dictionary containing Volt defining the volts between the level extents at each edge of the eye.
        * Level - An array of parameters, one for each level of the eye (the number of eyes plus one) containing:
            - Min - a dictionary containing the Bin and Volt of the minimum edge of the level extent.
            - Max - a dictionary containing the Bin and Volt of the maximum edge of the level extent.
            - Delta  - a dictionary containing the Bin and Volt vertical distance between the edeges of the level extent.
            - Mean - a dictionary containing the Bin and Volt of the mean vertical location of the level extent.
        * Linearity - The eye linearity calculated as the Min(AV)/Max(AV).  This is 100% for NRZ waveforms.
        * RLM - Relative Level Mismatch - only defined for PAM-4.
        * VerticalResolution - the resolution, in V, for each row of the eye.
        * HorizontalResolution - the resolution in seconds, for each column of the eye.
        """
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
        self.measDict={'R':R,'C':C,'MinV':self.minV,'MaxV':self.maxV,'MinT':-C//2*UI,'MaxT':(C-1)//2*UI,'BERForMeasure':BERForMeasure,
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
        """Generates bathtub curves on the eye diagram and calculates the error probabilities and rates
        @param DecadesFromJoin float, defaults to 0.25, number of decades above the point where the PDFs join together to begin fitting
        the histogram tails.  A bit further up, like 0.5-1 decade is ideal, but will cause algorithm failure for very low BER systems.
        Too low, and the tail estimate will contain portions of the adjacent PDF.
        @param MinPointsForFit integer, defaults to 6, minimum number of points to use to fit the tail of the PDF.  
        After processing, the measDict member variable has an additional dictionary added called 'Bathtub' and 'Probabilities'.  Inside
        the 'Bathtub' dictionary are the following items:
        Vertical - a dictionary containing:
        * Data - contains two vectors called:
            - x - an x axis containing one element per row containing the voltage.
            - y - a y axis containing one element per row containing the probability.
        * Level - a dictionary array (each element in the dictionary is 0, 1, 2, etc.) containing, per level:
            - LeftEst - a dictionary containing information on the left estimate (the PDF tail below the level in the histogram shown as a vertical slice:
                - Start - a dictionary containing Bin which is the starting row for the estimate of the PDF.
                - End - a dictionary containing Bin which is the ending row for the estimate of the PDF.
                - Est - a dictionary of the estimatated polynomial:
                    - Coef - list of the three coefficients a0, a1, a2 for the polynomial a0+a1*x+a2*x^2 where x is the natural log of the probability.
                    - Valid - if the estimate is valid.
                    - Wf - a dictionary of the estimated PDF tail where:
                        - x - is the x axis containing the voltage.
                        - y - is the y axis containing the probability.
            - RightEst - a dictionary containing information on the right estimate (the PDF tail above the level in the histogram shown as a vertical slice:
                - Start - a dictionary containing Bin which is the starting row for the estimate of the PDF.
                - End - a dictionary containing Bin which is the ending row for the estimate of the PDF.
                - Est - a dictionary of the estimatated polynomial:
                    - Coef - list of the three coefficients a0, a1, a2 for the polynomial a0+a1*x+a2*x^2 where x is the natural log of the probability.
                    - Valid - if the estimate is valid.
                    - Wf - a dictionary of the estimated PDF tail where:
                        - x - is the x axis containing the voltage.
                        - y - is the y axis containing the probability.
            - Hist - the entire, partially estimated, PDF for this level vertically across the entire vertical slice.  There is one probablity element
            per row in the eye diagram.
            - CDFFromLeft - The integrated PDF from the bottom to the top, forming the probability that a value could be below a given row.
            - CDFFromRight - The integrated PDF from the top to the bottom, forming the probability that a value could be above a given row.
        * Horizontal - a dictionary array, one element per eye, where each element in the dictionary is 0, 1, 2, etc.), containing, per eye:
            - Data - an instance of class Waveform, spanning the entire UI horizontally, containing the probability at the decision point for each column.
            This is used to plot the jitter bathtub curves.
        Inside the 'Probabilities' dictionary are the following items:
        * SymbolCodes - a list of the codes for the symbol.  This is just 0, 1, 2, etc. depending on the bits per symbol.
        * GrayCodes - a list of gray coded symbols corresponding to the symbol codes.
        * Interpretation - A list of lists representing a Symbols x Symbols matrix, where Interpretation[x][y] represents the probability that a
        symbol transmitted as symbol x is interpreted as symbol y.
        * Symbol - the measured probability that a symbol was transmitted.
        * ErrorRate - The error rates containing:
            - Symbol - the symbol error rates as:
                - PerSymbol - A list per symbol containing the probability of a symbol being erroneously decoded.
                - Nominal - The total, nominal symbol error rate, assuming that each symbol was transmitted with equal probability.
                - Measured - The total, measured symbol error rate, considering the measured probability that a given symbol was transmitted.
            - Bit - The bit error rates containing:
                - Standard - The un-gray coded bit errors:
                    - PerSymbol - a list per symbol containing the probability of one or more bit errors in the symbol.
                    - Nominal - The total, nominal bit error rate, assuming that each bit was transmitted with equal probability.
                    - Measured - the total, measured bit error rate, considering the measured probability that a given bit was transmitted.
                - Gray - The gray coded bit errors:
                    - PerSymbol - a list per symbol containing the probability of one or more bit errors in the symbol.
                    - Nominal - The total, nominal bit error rate, assuming that each bit was transmitted with equal probability.  Nominally, this should
                    be the nominal BER divided by the number of bits per symbol.
                    - Measured - the total, measured bit error rate, considering the measured probability that a given bit was transmitted.
        @remark The Measure member function be called prior to this call.
        """
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
                        with np.errstate(divide='ignore'):
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
            #print(ex)
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
                        with np.errstate(divide='ignore'):
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
            #print(ex)
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
                            with np.errstate(divide='ignore'):
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
                #print(ex)
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
                            with np.errstate(divide='ignore'):
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
                #print(ex)
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
                #print(ex)
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
        """Generates an annotation bitmap that goes along with the raw bitmap containing annotation marks.  
        This creates an annotationBitmap member variable of the same dimensions as the rawBitmap member variable.  Each pixel in
        the bitmap contains a 1 whereever there should be an overlaid, lit pixel for the annotation.
        @param MeanLevels bool, defaults to True, whether to place a horizontal line at the mean levels.
        @param LevelExtents bool, defaults to True, whether to place horizontal dotted lines about the mean levels to demarcate the extents.
        @param EyeWidth bool, defaults to True, whether to place a horizontal line where the eye width is measured.
        @param EyeHeight bool, defaults to True, whether to place a vertical line where the eye height is measured.
        @param Contours bool, defaults to True, whether to annotate the eye contour with the probability specified in the Measurement.
        @param WhichContours string, 'Eye' or 'All', defaults to 'Eye', where to annotate the contour.  'Eye' annotates only the contour around
        the eye.  'All' annotates any region whose inside has the probability specified.
        @remark The Measure member function be called prior to this call.
        """
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
        """Creates the image (picture) from the raw bitmap and the annotation bit map.  
        @param LogIntensity bool, defaults to False, whether to generate the eye diagram with a logarithmic intensity.  This allows better
        insight into the BER contours.
        @param MinExponentLogIntensity float, defaults to -6.  If LogIntensity is specified, this is the exponent on the probablity, below which
        pixels are shown a totally colored (or totally black if inverted).
        @param MaxExponentLogIntensity float, defaults to 0.  If LogIntensity is specified, this is the exponent on the probablity, above which
        pixels are shown a totally black (or totally colored if inverted).
        @param NumUI int, defaults to 1, number of unit intervals to show in the eye diagram.
        @param Saturation float, defaults to 20 (%) used to generate a saturation curve for the eye, otherwise the correct contrast is not shown.
        Best values are 20 % or lower.
        @param InvertImage bool, defaults to True.  Non-inverted images are shades of black on the color specified.  Inverted images are shades of
        the color specified on black.
        @param Color string, defaults to #ffffff, hexadecimal code where each of the three bytes represents the 0-255 value of R, G, and B, for the
        eye diagram.  '#ffffff' is white.  '#000000' is black.
        @param AnnotationColor string, defaults to #000000, hexadecimal code where each of the three bytes represents the 0-255 value of R, G, and B,
        for the annotations.
        @param ScaleX float, defaults to 100, scaling of the x axis of the image after construction.
        @param ScaleY float, defaults to 100, scaling of the y axis of the image after construction. 
        Scaling allows for lower resolution images, requiring less processing, to create larger, beautiful eye diagrams.  
        Upon completion, the image is held in the image member variable.
        """
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

        C=int(C*ScaleX/100.); R=int(self.RowsSpecified*ScaleY/100.)
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
