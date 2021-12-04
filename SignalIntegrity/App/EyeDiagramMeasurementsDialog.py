"""
EyeDiagramMeasurementsDialog.py
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
    from Tkinter import ttk
else:
    import tkinter as tk
    from tkinter import ttk

import math

from SignalIntegrity.App.MenuSystemHelpers import StatusBar
import SignalIntegrity.App.Project
import SignalIntegrity.App.Preferences
from SignalIntegrity.App.ToSI import ToSI

class EyeDiagramMeasurementsDialog(tk.Toplevel):
    labelwidth=25
    entrywidth=10
    def __init__(self, parent, name):
        tk.Toplevel.__init__(self, parent)
        self.parent=parent
        self.withdraw()
        self.name=name
        self.title('Eye Diagram: '+name)
        self.img = tk.PhotoImage(file=SignalIntegrity.App.IconsBaseDir+'AppIcon2.gif')
        self.tk.call('wm', 'iconphoto', self._w, self.img)
        self.protocol("WM_DELETE_WINDOW", self.onClosing)

        self.tabControl=ttk.Notebook(self)

        self.tab1=ttk.Frame(self.tabControl)
        self.tabControl.add(self.tab1,text='Vertical/Horizontal')
        self.tabControl.pack(expand=1,fill=tk.BOTH)
        self.eyeStatus=StatusBar(self.tab1)
        self.eyeStatus.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
        self.ParametersFrame=tk.Frame(self.tab1,relief=tk.RIDGE,borderwidth=5)
        self.ParametersFrame.pack(side=tk.LEFT,fill=tk.X,expand=tk.NO,anchor=tk.NW)

        self.tab2=ttk.Frame(self.tabControl)
        self.tabControl.add(self.tab2,text='Error Rates')
        self.BERFrame=tk.Frame(self.tab2,relief=tk.RIDGE,borderwidth=5)
        self.BERFrame.pack(side=tk.LEFT,fill=tk.X,expand=tk.NO,anchor=tk.NW)

        if SignalIntegrity.App.Preferences['Features.OpticalMeasurements']:
            self.tab3=ttk.Frame(self.tabControl)
            self.tabControl.add(self.tab3,text='Penalties')
            self.PenaltiesFrame=tk.Frame(self.tab3,relief=tk.RIDGE,borderwidth=5)
            self.PenaltiesFrame.pack(side=tk.LEFT,fill=tk.X,expand=tk.NO,anchor=tk.NW)

        self.bind('<FocusIn>',self.onFocus)
        self.resizable(False, False)
        self.deiconify()
        self.lift()

    def onFocus(self,event):
        if event.widget == self:
            if self.parent.winfo_exists():
                self.parent.lift()
                self.lift()

    def onClosing(self):
        self.withdraw()
        self.destroy()

    def destroy(self):
        tk.Toplevel.withdraw(self)
        tk.Toplevel.destroy(self)

    def Line2(self,frame,text):
        line=tk.Label(self.ParametersFrame,text=text,font='fixedsys')
        line.pack(side=tk.TOP,expand=tk.NO,fill=tk.X)

    def SingleLine(self,frame,label,textEntry):
        lineFrame=tk.Frame(frame)
        lineFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
        text=label.ljust(self.labelwidth)
        line=tk.Label(lineFrame,text=text,font='fixedsys',width=self.labelwidth)
        line.pack(side=tk.LEFT,expand=tk.NO,fill=tk.X)
        entryFrame=tk.Frame(lineFrame,relief=tk.RIDGE,borderwidth=5)
        entryFrame.pack(side=tk.LEFT,expand=tk.NO,fill=tk.X)
        entry=tk.Label(entryFrame,width=self.entrywidth,text=textEntry)
        entry.pack(side=tk.LEFT,expand=tk.NO,fill=tk.X)


    def Fields2(self,frame,category,parameter,subparameter,label,unit=None):
        lineFrame=tk.Frame(frame)
        lineFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
        text=label.ljust(self.labelwidth)
        line=tk.Label(lineFrame,text=text,font='fixedsys')
        line.pack(side=tk.LEFT,expand=tk.NO,fill=tk.X)
        for e in range(len(self.meas[category])):
            entryFrame=tk.Frame(lineFrame,relief=tk.RIDGE,borderwidth=5)
            entryFrame.pack(side=tk.LEFT,expand=tk.NO,fill=tk.X)
            entry=tk.Label(entryFrame,width=self.entrywidth,text=ToSI(self.meas[category][e][parameter][subparameter],unit))
            entry.pack(side=tk.LEFT,expand=tk.NO,fill=tk.X)

    def Heading(self,frame,label,elements):
        lineFrame=tk.Frame(frame)
        lineFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
        text=label.center(self.labelwidth)
        line=tk.Label(lineFrame,text=text,font='fixedsys')
        line.pack(side=tk.LEFT,expand=tk.NO,fill=tk.X)
        for e in elements:
            entryFrame=tk.Frame(lineFrame,borderwidth=5)
            entryFrame.pack(side=tk.LEFT,expand=tk.NO,fill=tk.X)
            entry=tk.Label(entryFrame,width=self.entrywidth,text=e)
            entry.pack(side=tk.LEFT,expand=tk.NO,fill=tk.X)

    def AddText(self,frame,text,width):
        entryFrame=tk.Frame(frame,borderwidth=5)
        entryFrame.pack(side=tk.LEFT,expand=tk.NO,fill=tk.X)
        line=tk.Label(entryFrame,text=text,width=width)
        line.pack(side=tk.LEFT,expand=tk.NO,fill=tk.X)

    def AddEntry(self,frame,text,width=10):
            entryFrame=tk.Frame(frame,relief=tk.RIDGE,borderwidth=5)
            entryFrame.pack(side=tk.LEFT,expand=tk.NO,fill=tk.X)
            entry=tk.Label(entryFrame,width=width,text=text)
            entry.pack(side=tk.LEFT,expand=tk.NO,fill=tk.X)

    def UpdateMeasurements(self,meas):
        self.withdraw()
        self.meas=meas
        if self.meas==None:
            return

        self.ParametersFrame.pack_forget()
        self.ParametersFrame=tk.Frame(self.tab1,relief=tk.RIDGE,borderwidth=5)
        self.ParametersFrame.pack(side=tk.LEFT,fill=tk.BOTH,expand=tk.YES,anchor=tk.NW)

        self.BERFrame.pack_forget()
        self.BERFrame=tk.Frame(self.tab2,relief=tk.RIDGE,borderwidth=5)
        self.BERFrame.pack(side=tk.LEFT,fill=tk.BOTH,expand=tk.YES,anchor=tk.NW)

        if SignalIntegrity.App.Preferences['Features.OpticalMeasurements']:
            self.PenaltiesFrame.pack_forget()
            self.PenaltiesFrame=tk.Frame(self.tab3,relief=tk.RIDGE,borderwidth=5)
            self.PenaltiesFrame.pack(side=tk.LEFT,fill=tk.BOTH,expand=tk.YES,anchor=tk.NW)

        self.eyeStatus.set(f"All Measurements Taken at: {10.0**meas['BERForMeasure']}")

        #topline=''.join(['Eye'.ljust(self.labelwidth)]+[str(eye).center(self.entrywidth-1) for eye in range(len(self.meas['Eye']))]+[''.ljust(self.entrywidth-1)])
        self.Heading(self.ParametersFrame,'Eye',[str(e) for e in range(len(self.meas['Eye']))])
        #self.Line2(topline)
        self.Line2(self.ParametersFrame,'Timing')
        self.Fields2(self.ParametersFrame,'Eye','Start','Time','Start','s')
        self.Fields2(self.ParametersFrame,'Eye','End','Time','End','s')
        self.Fields2(self.ParametersFrame,'Eye','Width','Time','Width','s')
        self.Line2(self.ParametersFrame,'')
        self.Line2(self.ParametersFrame,'Vertical')
        self.Fields2(self.ParametersFrame,'Eye','Low','Volt','Low','V')
        self.Fields2(self.ParametersFrame,'Eye','Mid','Volt','Midpoint','V')
        self.Fields2(self.ParametersFrame,'Eye','Best','Volt','Best Decision Level','V')
        self.Fields2(self.ParametersFrame,'Eye','High','Volt','High','V')
        self.Fields2(self.ParametersFrame,'Eye','Height','Volt','Height','V')
        self.Fields2(self.ParametersFrame,'Eye','AV','Volt','AV','V')
        self.Line2(self.ParametersFrame,'')
        #line=''.join(['Thresholds'.ljust(self.labelwidth)]+[str(th).center(self.entrywidth-1) for th in range(len(self.meas['Level']))])
        #self.Line2(line)
        self.Heading(self.ParametersFrame,'Extents',[str(th) for th in range(len(self.meas['Level']))])
        self.Fields2(self.ParametersFrame,'Level','Min','Volt','Min','V')
        self.Fields2(self.ParametersFrame,'Level', 'Max', 'Volt', 'Max','V')
        self.Fields2(self.ParametersFrame,'Level', 'Delta', 'Volt', 'Delta','V')
        self.Fields2(self.ParametersFrame,'Level', 'Mean', 'Volt', 'Mean','V')
        self.Line2(self.ParametersFrame,'')
        if len(meas['Eye'])>1:
            self.SingleLine(self.ParametersFrame,'Eye Linearity',ToSI(self.meas['Linearity']*100.,'%'))
            try:
                self.SingleLine(self.ParametersFrame,'RLM',ToSI(self.meas['RLM']*100.,'%'))
            except:
                pass
            self.Line2(self.ParametersFrame,'')
        self.SingleLine(self.ParametersFrame,'Vertical Resolution',ToSI(self.meas['VerticalResolution'],'V'))
        self.SingleLine(self.ParametersFrame,'Horizontal Resolution',ToSI(self.meas['HorizontalResolution'],'s'))

        if 'Probabilities' in self.meas.keys():
#         self.measDict['Probabilities']={'SymbolCodes':SymbolCode,'GrayCodes':GrayCodes,'Interpretation':SymbolInterpretedAsOther,
#                                         'ErrorRate':{'Symbol':{'PerSymbol':SymbolErrorRatePerSymbol,'Nominal':NominalSymbolErrorRate,'Measured':MeasuredSymbolErrorRate},
#                                                      'Bit':{'Standard':{'PerSymbol':BitErrorRatePerSymbol,'Nominal':NominalBitErrorRate,'Measured':MeasuredBitErrorRate},
#                                                             'Gray':{'PerSymbol':GrayCodeBitErrorRatePerSymbol,'Nominal':GrayCodeNominalBitErrorRate,'Measured':GrayCodeMeasuredBitErrorRate}}}}

            SymbolCode=self.meas['Probabilities']['SymbolCodes']
            GrayCode=self.meas['Probabilities']['GrayCodes']
            numberOfSymbols=len(SymbolCode)
            lineFrame=tk.Frame(self.BERFrame); lineFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
            if numberOfSymbols > 2:
                self.AddText(lineFrame,''.center(self.entrywidth),self.entrywidth)
            self.AddText(lineFrame,''.center(self.entrywidth),self.entrywidth)
            self.AddText(lineFrame,'Interpretation'.center(self.entrywidth*numberOfSymbols),self.entrywidth*numberOfSymbols)
            lineFrame=tk.Frame(self.BERFrame); lineFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
            if numberOfSymbols > 2:
                self.AddText(lineFrame,'',self.entrywidth)
            self.AddText(lineFrame,'',self.entrywidth)
            symbolDigits=math.floor(math.log2(numberOfSymbols)+0.5)
            for s in SymbolCode:
                self.AddText(lineFrame,bin(s)[2:].rjust(symbolDigits,'0'),self.entrywidth)
            lineFrame=tk.Frame(self.BERFrame); lineFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
            if numberOfSymbols > 2:
                self.AddText(lineFrame,'',self.entrywidth)
                self.AddText(lineFrame,'',self.entrywidth)
                symbolDigits=math.floor(math.log2(numberOfSymbols)+0.5)
                for s in GrayCode:
                    self.AddText(lineFrame,bin(s)[2:].rjust(symbolDigits,'0'),self.entrywidth)
            lineFrame=tk.Frame(self.BERFrame); lineFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
            self.AddText(lineFrame,'Symbol',self.entrywidth)
            if numberOfSymbols > 2:
                self.AddText(lineFrame,'Gray Code',self.entrywidth)
            Probability=self.meas['Probabilities']['Interpretation']
            for s in range(len(SymbolCode)):
                lineFrame=tk.Frame(self.BERFrame); lineFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
                self.AddText(lineFrame,bin(SymbolCode[s])[2:].rjust(symbolDigits,'0'),self.entrywidth)
                if numberOfSymbols > 2:
                    self.AddText(lineFrame,bin(GrayCode[s])[2:].rjust(symbolDigits,'0'),self.entrywidth)
                for o in range(len(SymbolCode)):
                    self.AddEntry(lineFrame, '{:.3E}'.format(Probability[s][o],3), self.entrywidth)
            # nominal error rates
            lineFrame=tk.Frame(self.BERFrame); lineFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
            self.AddText(lineFrame,''.center(2*self.entrywidth),2*self.entrywidth)
            lineFrame=tk.Frame(self.BERFrame); lineFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
            if numberOfSymbols > 2:
                self.AddText(lineFrame,''.center(self.entrywidth),self.entrywidth)
            self.AddText(lineFrame,''.center(self.entrywidth),self.entrywidth)
            self.AddText(lineFrame,'Nominal Error Rates'.center(self.entrywidth*numberOfSymbols),self.entrywidth*numberOfSymbols)
            lineFrame=tk.Frame(self.BERFrame); lineFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
            self.AddText(lineFrame,'Symbol',self.entrywidth)
            if numberOfSymbols > 2:
                self.AddText(lineFrame,'Gray Code',self.entrywidth)
            self.AddText(lineFrame,'Probability',self.entrywidth)
            if numberOfSymbols > 2:
                self.AddText(lineFrame,'SER',self.entrywidth)
            self.AddText(lineFrame,'BER',self.entrywidth)
            if numberOfSymbols > 2:
                self.AddText(lineFrame,'Gray BER',self.entrywidth)
            Probability=1./len(SymbolCode)
            SER=self.meas['Probabilities']['ErrorRate']['Symbol']['PerSymbol']
            BER=self.meas['Probabilities']['ErrorRate']['Bit']['Standard']['PerSymbol']
            GrayBER=self.meas['Probabilities']['ErrorRate']['Bit']['Gray']['PerSymbol']
            for s in range(len(SymbolCode)):
                lineFrame=tk.Frame(self.BERFrame); lineFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
                self.AddText(lineFrame,bin(SymbolCode[s])[2:].rjust(symbolDigits,'0'),self.entrywidth)
                if numberOfSymbols > 2:
                    self.AddText(lineFrame,bin(GrayCode[s])[2:].rjust(symbolDigits,'0'),self.entrywidth)
                self.AddEntry(lineFrame, '{:.3E}'.format(Probability,3), self.entrywidth)
                if numberOfSymbols > 2:
                    self.AddEntry(lineFrame, '{:.3E}'.format(SER[s],3), self.entrywidth)
                self.AddEntry(lineFrame, '{:.3E}'.format(BER[s],3), self.entrywidth)
                if numberOfSymbols > 2:
                    self.AddEntry(lineFrame, '{:.3E}'.format(GrayBER[s],3), self.entrywidth)
            lineFrame=tk.Frame(self.BERFrame); lineFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
            if numberOfSymbols > 2:
                self.AddText(lineFrame,'',self.entrywidth)
            self.AddText(lineFrame,'Totals',self.entrywidth)
            self.AddEntry(lineFrame, '{:.3E}'.format(1.,3), self.entrywidth)
            if numberOfSymbols > 2:
                self.AddEntry(lineFrame, '{:.3E}'.format(self.meas['Probabilities']['ErrorRate']['Symbol']['Nominal'],3), self.entrywidth)
            self.AddEntry(lineFrame, '{:.3E}'.format(self.meas['Probabilities']['ErrorRate']['Bit']['Standard']['Nominal'],3), self.entrywidth)
            if numberOfSymbols > 2:
                self.AddEntry(lineFrame, '{:.3E}'.format(self.meas['Probabilities']['ErrorRate']['Bit']['Gray']['Nominal'],3), self.entrywidth)
            # measured error rates
            lineFrame=tk.Frame(self.BERFrame); lineFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
            self.AddText(lineFrame,''.center(2*self.entrywidth),2*self.entrywidth)
            lineFrame=tk.Frame(self.BERFrame); lineFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
            if numberOfSymbols > 2:
                self.AddText(lineFrame,''.center(self.entrywidth),self.entrywidth)
            self.AddText(lineFrame,''.center(self.entrywidth),self.entrywidth)
            self.AddText(lineFrame,'Measured Error Rates'.center(self.entrywidth*numberOfSymbols),self.entrywidth*numberOfSymbols)
            lineFrame=tk.Frame(self.BERFrame); lineFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
            self.AddText(lineFrame,'Symbol',self.entrywidth)
            if numberOfSymbols > 2:
                self.AddText(lineFrame,'Gray Code',self.entrywidth)
            self.AddText(lineFrame,'Probability',self.entrywidth)
            if numberOfSymbols > 2:
                self.AddText(lineFrame,'SER',self.entrywidth)
            self.AddText(lineFrame,'BER',self.entrywidth)
            if numberOfSymbols > 2:
                self.AddText(lineFrame,'Gray BER',self.entrywidth)
            Probability=self.meas['Probabilities']['Symbol']
            SER=self.meas['Probabilities']['ErrorRate']['Symbol']['PerSymbol']
            BER=self.meas['Probabilities']['ErrorRate']['Bit']['Standard']['PerSymbol']
            GrayBER=self.meas['Probabilities']['ErrorRate']['Bit']['Gray']['PerSymbol']
            for s in range(len(SymbolCode)):
                lineFrame=tk.Frame(self.BERFrame); lineFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
                self.AddText(lineFrame,bin(SymbolCode[s])[2:].rjust(symbolDigits,'0'),self.entrywidth)
                if numberOfSymbols > 2:
                    self.AddText(lineFrame,bin(GrayCode[s])[2:].rjust(symbolDigits,'0'),self.entrywidth)
                self.AddEntry(lineFrame, '{:.3E}'.format(Probability[s],3), self.entrywidth)
                if numberOfSymbols > 2:
                    self.AddEntry(lineFrame, '{:.3E}'.format(SER[s],3), self.entrywidth)
                self.AddEntry(lineFrame, '{:.3E}'.format(BER[s],3), self.entrywidth)
                if numberOfSymbols > 2:
                    self.AddEntry(lineFrame, '{:.3E}'.format(GrayBER[s],3), self.entrywidth)
            lineFrame=tk.Frame(self.BERFrame); lineFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
            if numberOfSymbols > 2:
                self.AddText(lineFrame,'',self.entrywidth)
            self.AddText(lineFrame,'Totals',self.entrywidth)
            self.AddEntry(lineFrame, '{:.3E}'.format(sum(Probability),3), self.entrywidth)
            if numberOfSymbols > 2:
                self.AddEntry(lineFrame, '{:.3E}'.format(self.meas['Probabilities']['ErrorRate']['Symbol']['Measured'],3), self.entrywidth)
            self.AddEntry(lineFrame, '{:.3E}'.format(self.meas['Probabilities']['ErrorRate']['Bit']['Standard']['Measured'],3), self.entrywidth)
            if numberOfSymbols > 2:
                self.AddEntry(lineFrame, '{:.3E}'.format(self.meas['Probabilities']['ErrorRate']['Bit']['Gray']['Measured'],3), self.entrywidth)
            self.tabControl.tab(1,state='normal')
        else:
            self.tabControl.tab(1,state='disabled')
#             self.measDict['Penalties']={'PH':PH,'PL':PL,'MA':OMA,'QFactorExpected':QFactorExpected,'QFactorExpecteddB':QFactorExpecteddB,
#                                         'BERMeasured':BERmeas,'BERExpected':BERexpected,
#                                         'QFactor':QFactor,'QFactordB':QFactordB,'TxPenalty':TxPenalty,
#                                         'NoiseSigma':self.NoiseSigma,
#                                         'Levels':{'Total':numLevels,'Inner':numInnerLevels,'Outer':numOuterLevels},
#                                         'Eyes':numEyes,'ErrorCases':numErrorCases,
#                                         'F':{'Numerical':F,'Numerator':FN,'Denominator':FD},
#                                         'D':D}

        if SignalIntegrity.App.Preferences['Features.OpticalMeasurements']:
            if 'Penalties' in self.meas.keys():
                PH=self.meas['Penalties']['PH']
                self.SingleLine(self.PenaltiesFrame, 'High Level', ToSI(PH,round=6))
                PL=self.meas['Penalties']['PL']
                self.SingleLine(self.PenaltiesFrame, 'Low Level', ToSI(PL,round=6))
                OMA=self.meas['Penalties']['MA']
                self.SingleLine(self.PenaltiesFrame, 'Modulation Amplitude', ToSI(OMA,round=6))
                sigma=self.meas['Penalties']['NoiseSigma']
                self.SingleLine(self.PenaltiesFrame, 'Noise Sigma', ToSI(sigma,round=6))
                noisePenaltydB=self.meas['Penalties']['NoisePenalty']
                self.SingleLine(self.PenaltiesFrame, 'Noise Penalty', ToSI(noisePenaltydB,'dB',round=4))
                QFactorExpected=self.meas['Penalties']['QFactorExpected']
                self.SingleLine(self.PenaltiesFrame, 'Expected Q Factor', ToSI(QFactorExpected,round=6))
                BERexpected=self.meas['Penalties']['BERExpected']
                self.SingleLine(self.PenaltiesFrame, 'Expected BER', '{:.3E}'.format(BERexpected))
                lineFrame=tk.Frame(self.PenaltiesFrame); lineFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
                self.AddText(lineFrame,'',self.entrywidth)
                BERmeas=self.meas['Penalties']['BERMeasured']
                self.SingleLine(self.PenaltiesFrame, 'Measured BER', '{:.3E}'.format(BERmeas))
                QFactor=self.meas['Penalties']['QFactor']
                self.SingleLine(self.PenaltiesFrame, 'Measured Q Factor', 'infinite' if math.isinf(QFactor) else ToSI(QFactor,round=6))
                TxPenalty=self.meas['Penalties']['TxPenalty']
                if BERexpected == 0 and BERmeas == 0:
                    self.SingleLine(self.PenaltiesFrame, 'Tx Penalty (dB power)', 'unknown')
                else:
                    self.SingleLine(self.PenaltiesFrame, 'Tx Penalty (dB power)', 'infinite' if math.isinf(TxPenalty) else ToSI(TxPenalty,'dB',round=4))
                self.tabControl.tab(2,state='normal')
            else:
                self.tabControl.tab(2,state='disabled')
        self.deiconify()