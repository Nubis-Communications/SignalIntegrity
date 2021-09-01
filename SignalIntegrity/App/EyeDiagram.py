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

from SignalIntegrity.App.SParameterViewerWindow import SParametersDialog
from SignalIntegrity.App.MenuSystemHelpers import Doer,StatusBar
from SignalIntegrity.App.ProgressDialog import ProgressDialog
from SignalIntegrity.App.FilePicker import AskSaveAsFilename
from SignalIntegrity.App.ToSI import FromSI,ToSI
from SignalIntegrity.App.EyeDiagramPropertiesDialog import EyeDiagramPropertiesDialog

from SignalIntegrity.Lib.Test.TestHelpers import PlotTikZ
from SignalIntegrity.Lib.TimeDomain.Filters import FractionalDelayFilterSinX
from SignalIntegrity.Lib.TimeDomain.Waveform import TimeDescriptor
from SignalIntegrity.Lib.Splines import Spline
from SignalIntegrity.Lib.TimeDomain.Filters.WaveformTrimmer import WaveformTrimmer

import SignalIntegrity.App.Project
import SignalIntegrity.App.Preferences

import matplotlib
import matplotlib.pyplot

if not 'matplotlib.backends' in sys.modules:
    matplotlib.use('TkAgg')

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk

from matplotlib.figure import Figure

from PIL import Image,ImageTk

import math
import copy

import numpy as np

class EyeDiagramDialog(tk.Toplevel):

    def __init__(self, parent, name):
        tk.Toplevel.__init__(self, parent.parent)
        self.parent=parent
        self.withdraw()
        self.name=name
        self.title('Eye Diagram: '+name)
        self.img = tk.PhotoImage(file=SignalIntegrity.App.IconsBaseDir+'AppIcon2.gif')
        self.tk.call('wm', 'iconphoto', self._w, self.img)
        self.protocol("WM_DELETE_WINDOW", self.onClosing)

        # the Doers - the holder of the commands, menu elements, toolbar elements, and key bindings
        self.EyeDiagramSaveDoer = Doer(self.onWriteImageToFile).AddHelpElement('Control-Help:Save-Eye-Diagram-Image').AddToolTip('Save images to files')
        self.CalculationPropertiesDoer = Doer(self.onCalculationProperties).AddHelpElement('Control-Help:Calculation-Properties').AddToolTip('Edit calculation properties')
        self.PropertiesDoer=Doer(self.onProperties).AddHelpElement('Control-Help:Eye-Diagram-Properties').AddToolTip('Edit eye diagram properties')
        self.SimulateDoer = Doer(self.onCalculate).AddHelpElement('Control-Help:Recalculate').AddToolTip('Recalculate simulation')
        self.OnlyRecalculateEyeDoer =Doer(self.onRecalculateEyeDiagram).AddHelpElement('Control-Help:Only-Recalculate-Eye-Diagram').AddToolTip('Recalculate eye diagram')
        # ------
        self.HelpDoer = Doer(self.onHelp).AddHelpElement('Control-Help:Eye-Diagram-Open-Help-File').AddToolTip('Open the help system in a browser')
        self.ControlHelpDoer = Doer(self.onControlHelp).AddHelpElement('Control-Help:Eye-Diagram-Control-Help').AddToolTip('Get help on a control')
        # ------
        self.EscapeDoer = Doer(self.onEscape).AddKeyBindElement(self,'<Escape>').DisableHelp()

        # The menu system
        TheMenu=tk.Menu(self)
        self.TheMenu=TheMenu
        self.config(menu=TheMenu)
        FileMenu=tk.Menu(self)
        TheMenu.add_cascade(label='File',menu=FileMenu,underline=0)
        self.EyeDiagramSaveDoer.AddMenuElement(FileMenu,label="Save Image to File",underline=0)
        FileMenu.add_separator()
        # ------
        CalcMenu=tk.Menu(self)
        TheMenu.add_cascade(label='Calculate',menu=CalcMenu,underline=0)
        self.CalculationPropertiesDoer.AddMenuElement(CalcMenu,label='Calculation Properties',underline=0)
        self.PropertiesDoer.AddMenuElement(CalcMenu,label='Eye Diagram Properties',underline=0)
        CalcMenu.add_separator()
        self.SimulateDoer.AddMenuElement(CalcMenu,label='Recalculate',underline=0)
        self.OnlyRecalculateEyeDoer.AddMenuElement(CalcMenu,label='Only Recalculate Eye Diagram',underline=0)
        # ------
        HelpMenu=tk.Menu(self)
        TheMenu.add_cascade(label='Help',menu=HelpMenu,underline=0)
        self.HelpDoer.AddMenuElement(HelpMenu,label='Open Help File',underline=0)
        self.ControlHelpDoer.AddMenuElement(HelpMenu,label='Control Help',underline=0)

        # The Toolbar
        ToolBarFrame = tk.Frame(self)
        ToolBarFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
        iconsdir=SignalIntegrity.App.IconsDir+''
        self.EyeDiagramSaveDoer.AddToolBarElement(ToolBarFrame,iconfile=iconsdir+'document-save-2.gif').Pack(side=tk.LEFT,fill=tk.NONE,expand=tk.NO)
        tk.Frame(self,height=2,bd=2,relief=tk.RAISED).pack(side=tk.LEFT,fill=tk.X,padx=5,pady=5)
        self.CalculationPropertiesDoer.AddToolBarElement(ToolBarFrame,iconfile=iconsdir+'tooloptions.gif').Pack(side=tk.LEFT,fill=tk.NONE,expand=tk.NO)
        self.SimulateDoer.AddToolBarElement(ToolBarFrame,iconfile=iconsdir+'system-run-3.gif').Pack(side=tk.LEFT,fill=tk.NONE,expand=tk.NO)
        self.OnlyRecalculateEyeDoer.AddToolBarElement(ToolBarFrame,iconfile=iconsdir+'eye.gif').Pack(side=tk.LEFT,fill=tk.NONE,expand=tk.NO)
        tk.Frame(ToolBarFrame,height=2,bd=2,relief=tk.RAISED).pack(side=tk.LEFT,fill=tk.X,padx=5,pady=5)
        self.HelpDoer.AddToolBarElement(ToolBarFrame,iconfile=iconsdir+'help-contents-5.gif').Pack(side=tk.LEFT,fill=tk.NONE,expand=tk.NO)
        self.ControlHelpDoer.AddToolBarElement(ToolBarFrame,iconfile=iconsdir+'help-3.gif').Pack(side=tk.LEFT,fill=tk.NONE,expand=tk.NO)

        self.eyeFrame=tk.Frame(self, relief=tk.RIDGE, borderwidth=5) 
        self.eyeCanvas=tk.Canvas(self.eyeFrame,width=0,height=0)
        self.eyeCanvas.pack()
        self.eyeFrame.pack(side=tk.TOP,fill=tk.BOTH,expand=tk.YES)

        # status bar
        self.statusbar=StatusBar(self)
        self.statusbar.pack(side=tk.BOTTOM,fill=tk.X,expand=tk.NO)

        self.eyeDiagram=EyeDiagram(self)

        if SignalIntegrity.App.Project['EyeDiagram']==None:
            import copy
            SignalIntegrity.App.Project.SubDir(copy.deepcopy(SignalIntegrity.App.Preferences['EyeDiagram']))

        self.geometry("%+d%+d" % (self.parent.parent.root.winfo_x()+self.parent.parent.root.winfo_width()/2-self.winfo_width()/2,
            self.parent.parent.root.winfo_y()+self.parent.parent.root.winfo_height()/2-self.winfo_height()/2))

        # Allow resizing of the image
        self.knowDelta=False
        self.deltaWidth=0
        self.deltaHeight=0
        self.bind('<Configure>',self.onResize)

    def onResize(self,event):
        if not self.knowDelta:
            self.adjusting=False
            self.adjustCount=0
            self.deltaWidth=4
            self.deltaHeight=4
            self.knowDelta=True
        else:
            if self.adjusting:
                self.adjustCount+=1
            else:
                self.adjusting=True
                self.adjustCount=0
                self.after(100,self.AdjustImage)

    def AdjustImage(self):
        if self.adjustCount != 0:
            self.adjustCount=0
            self.after(100,self.AdjustImage)
        else:
            if hasattr(self, 'eyeImage'):
                newImageWidth=self.eyeCanvas.winfo_width()-self.deltaWidth
                newImageHeight=self.eyeCanvas.winfo_height()-self.deltaHeight
                if (newImageWidth != self.eyeImage.width()) or (newImageHeight != self.eyeImage.height()):
                    if (newImageHeight > 0) and (newImageWidth > 0):
                        img=self.eyeDiagram.img.resize((newImageWidth,newImageHeight))
                        self.eyeImage=ImageTk.PhotoImage(img)
                        self.eyeCanvas.create_image(newImageWidth/2,newImageHeight/2,image=self.eyeImage)
            self.adjusting=False

    def onClosing(self):
        self.withdraw()
        self.destroy()

    def destroy(self):
        tk.Toplevel.withdraw(self)
        tk.Toplevel.destroy(self)

    def onWriteImageToFile(self):
        if self.parent.parent.fileparts.filename=='':
            filename=self.name
        else:
            filename=self.parent.parent.fileparts.filename+'_'+self.name
        filename=AskSaveAsFilename(parent=self,filetypes=[('Images',('.png','.bmp','.jpg','.gif','.tiff'))],
                        defaultextension='.png',
                        initialdir=self.parent.parent.fileparts.AbsoluteFilePath(),
                        initialfile=filename+'.png')
        if filename is None:
            return
        self.eyeDiagram.img.save(filename)

    def onCalculate(self):
        self.statusbar.set('Calculation Started')
        self.parent.parent.onCalculate()

    def onRecalculateEyeDiagram(self):
        self.statusbar.set('Calculation Started')
        import SignalIntegrity.Lib as si
        progressDialog=ProgressDialog(self.parent.parent,"Eye Diagram Processing",self,self.CalculateEyeDiagram)
        try:
            progressDialog.GetResult()
        except si.SignalIntegrityException as e:
            messagebox.showerror('Eye Diagram',e.parameter+': '+e.message)
            return

    def onCalculationProperties(self):
        self.parent.parent.onCalculationProperties()

    def onHelp(self):
        if Doer.helpKeys is None:
            messagebox.showerror('Help System','Cannot find or open this help element')
            return
        Doer.helpKeys.Open('sec:Eye-Diagram-Dialog')

    def onControlHelp(self):
        Doer.inHelp=True
        self.config(cursor='question_arrow')

    def onEscape(self):
        Doer.inHelp=False
        self.config(cursor='left_ptr')

    def onProperties(self):
        self.eyeDialog=EyeDiagramPropertiesDialog(self,SignalIntegrity.App.Project)
        if not hasattr(self, 'eyeDialog'):
            self.eyeDialog = EyeDiagramPropertiesDialog(self,SignalIntegrity.App.Project)
        if self.eyeDialog == None:
            self.eyeDialog= EyeDiagramPropertiesDialog(self,SignalIntegrity.App.Projectt)
        else:
            if not self.eyeDialog.winfo_exists():
                self.eyeDialog=EyeDiagramPropertiesDialog(self,SignalIntegrity.App.Project)

    def SetEyeArgs(self,eyeArgs):
        self.eyeArgs=eyeArgs
        return self

    def InstallCallback(self,Callback=None):
        self.callback=Callback

    def RemoveCallback(self):
        self.callback=None

    def CalculateEyeDiagram(self):
        self.eyeDiagram.CalculateEyeDiagram(self.callback)

    def UpdateWaveforms(self):
        self.eyeDiagram.prbswf=self.eyeArgs['Waveform']
        self.eyeDiagram.baudrate=self.eyeArgs['BaudRate']
        self.eyeDiagram.CalculateEyeDiagram(self.callback)
        self.deiconify()
        self.lift()
        return self

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

        if not self.headless: self.parent.statusbar.set('Building Bitmap')
        bitmap=np.zeros((R,C))
        for k in range(self.aprbswf.td.K):
            if not callback is None:
                if not callback(k/self.aprbswf.td.K*100.):
                    return
            r=(self.aprbswf[k]-minV)/DeltaV*R
            c=k%C
            bitmap[max(0,min(R-1,int(math.ceil(r))))][c]+=r-math.floor(r)
            bitmap[max(0,min(R-1,int(math.floor(r))))][c]+=1.-(r-math.floor(r))

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
            bitmapJitterNoise=convolve(bitmaparray,kernelHarray,mode='wrap')
            bitmapJitterNoise=convolve(bitmapJitterNoise,kernelVarray,mode='constant')
            bitmap=bitmapJitterNoise
            self.bitmapJitterNoise=bitmapJitterNoise
            total=sum([sum([self.bitmapJitterNoise[r][c] for c in range(C)]) for r in range(R)])
            self.bitmapJitterNoise=[[self.bitmapJitterNoise[r][c]/total*C for c in range(C)] for r in range(R)]

            if SignalIntegrity.App.Project['EyeDiagram.JitterNoise.LogIntensity.LogIntensity']:
                total=sum([sum([bitmap[r][c] for c in range(C)]) for r in range(R)])
                bitmap=[[bitmap[r][c]/total*C for c in range(C)] for r in range(R)]
                minBER=max(SignalIntegrity.App.Project['EyeDiagram.JitterNoise.LogIntensity.MinExponent'],-20)
                maxBER=max(minBER,SignalIntegrity.App.Project['EyeDiagram.JitterNoise.LogIntensity.MaxExponent'])
                minValue=pow(10.,minBER-1)
                minSat=0
                maxSat=1.

                m=(maxSat-minSat)/(maxBER-minBER)
                b=minSat-minBER*m
                bitmap=[[math.log10(max(bitmap[r][c],minValue)) for c in range(C)] for r in range(R)]
                bitmap=[[bitmap[r][c]*m+b for c in range(C)] for r in range(R)]
                bitmap=[[255.0 if bitmap[r][c] < minSat else (0 if bitmap[r][c] > maxSat else 255.0-bitmap[r][c]*255.0) for c in range(C)] for r in range(R)]

        maxValue=(max([max(v) for v in bitmap]))
        midBin=0

        midBin=midBin+C//2

        numUI=int(SignalIntegrity.App.Project['EyeDiagram.UI']+0.5)
        bitmapCentered=[[0 for c in range(C*numUI)] for _ in range(R)]
        self.rawBitmap=np.empty((len(bitmap),len(bitmap[0])))

        for u in range(numUI):
            for r in range(R):
                for c in range(C):
                    bitmapCentered[r][u*C+c]=bitmap[r][(c+midBin)%C]
                    if u==0:
                        self.rawBitmap[r][c]=bitmap[r][(c+midBin)%C]

        bitmap=bitmapCentered
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

        self.parent.eyeCanvas.pack_forget()
        self.parent.eyeCanvas=tk.Canvas(self.parent.eyeFrame,width=C,height=R)
        self.parent.eyeImage=ImageTk.PhotoImage(self.img)
        self.parent.eyeCanvas.create_image(C/2,R/2,image=self.parent.eyeImage)
        self.parent.eyeCanvas.pack(expand=tk.YES,fill=tk.BOTH)
        self.parent.statusbar.set('Calculation complete')
