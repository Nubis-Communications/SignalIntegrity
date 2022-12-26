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

        self.tab3=ttk.Frame(self.tabControl)
        self.tabControl.add(self.tab3,text='Optical')
        self.OpticalFrame=tk.Frame(self.tab3,relief=tk.RIDGE,borderwidth=5)
        self.OpticalFrame.pack(side=tk.LEFT,fill=tk.X,expand=tk.NO,anchor=tk.NW)

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
        line=tk.Label(frame,text=text,font='fixedsys')
        line.pack(side=tk.TOP,expand=tk.NO,fill=tk.X)

    def SingleLine(self,frame,label,textEntry):
        if not isinstance(textEntry,list): textEntry=[textEntry]
        if all([t==None for t in textEntry]):
            return
        lineFrame=tk.Frame(frame)
        lineFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
        text=label.ljust(self.labelwidth)
        line=tk.Label(lineFrame,text=text,width=self.labelwidth)
        line.pack(side=tk.LEFT,expand=tk.NO,fill=tk.X)
        for entry in textEntry:
            if entry == None:
                entryFrame=tk.Frame(lineFrame)
            else:
                entryFrame=tk.Frame(lineFrame,relief=tk.RIDGE,borderwidth=2)
            entryFrame.pack(side=tk.LEFT,expand=tk.NO,fill=tk.X)
            entry=tk.Label(entryFrame,width=self.entrywidth,text='' if entry == None else entry)
            entry.pack(side=tk.LEFT,expand=tk.NO,fill=tk.X)

    def Fields2(self,frame,category,parameter,subparameter,label,unit=None):
        lineFrame=tk.Frame(frame)
        lineFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
        text=label.ljust(self.labelwidth)
        line=tk.Label(lineFrame,text=text,width=self.labelwidth)
        line.pack(side=tk.LEFT,expand=tk.NO,fill=tk.X)
        for e in range(len(self.meas[category])):
            entryFrame=tk.Frame(lineFrame,relief=tk.RIDGE,borderwidth=2)
            entryFrame.pack(side=tk.LEFT,expand=tk.NO,fill=tk.X)
            entry=tk.Label(entryFrame,width=self.entrywidth,text=ToSI(self.meas[category][e][parameter][subparameter],unit))
            entry.pack(side=tk.LEFT,expand=tk.NO,fill=tk.X)

    def Heading(self,frame,label,elements):
        lineFrame=tk.Frame(frame)
        lineFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
        text=label.center(self.labelwidth-5)
        line=tk.Label(lineFrame,text=text,font='fixedsys')
        line.pack(side=tk.LEFT,expand=tk.NO,fill=tk.X)
        for e in elements:
            entryFrame=tk.Frame(lineFrame,borderwidth=2)
            entryFrame.pack(side=tk.LEFT,expand=tk.NO,fill=tk.X)
            entry=tk.Label(entryFrame,width=self.entrywidth,text=e,anchor='center')
            entry.pack(side=tk.LEFT,expand=tk.NO,fill=tk.X)
            entry.configure(anchor="center")

    def AddText(self,frame,text,width):
        entryFrame=tk.Frame(frame,borderwidth=2)
        entryFrame.pack(side=tk.LEFT,expand=tk.NO,fill=tk.X)
        line=tk.Label(entryFrame,text=text,width=width)
        line.pack(side=tk.LEFT,expand=tk.NO,fill=tk.X)

    def AddEntry(self,frame,text,width=10):
            entryFrame=tk.Frame(frame,relief=tk.RIDGE,borderwidth=2)
            entryFrame.pack(side=tk.LEFT,expand=tk.NO,fill=tk.X)
            entry=tk.Label(entryFrame,width=width,text=text)
            entry.pack(side=tk.LEFT,expand=tk.NO,fill=tk.X)

    def UpdateMeasurements(self,meas):
        self.withdraw()
        self.meas=meas
        if self.meas==None:
            return

        self.tabControl.destroy()
        self.tabControl=ttk.Notebook(self)

        self.tab1=ttk.Frame(self.tabControl)
        self.tabControl.add(self.tab1,text='Vertical/Horizontal')
        self.tabControl.pack(expand=1,fill=tk.BOTH)
        self.eyeStatus=StatusBar(self.tab1)
        self.eyeStatus.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
        self.ParametersFrame=tk.Frame(self.tab1,relief=tk.RIDGE,borderwidth=5)
        self.ParametersFrame.pack(side=tk.LEFT,fill=tk.BOTH,expand=tk.YES,anchor=tk.NW)

        self.tab2=ttk.Frame(self.tabControl)
        self.tabControl.add(self.tab2,text='Error Rates')
        self.BERFrame=tk.Frame(self.tab2,relief=tk.RIDGE,borderwidth=5)
        self.BERFrame.pack(side=tk.LEFT,fill=tk.BOTH,expand=tk.YES,anchor=tk.NW)

        if 'Optical' in self.meas.keys():
            self.tab3=ttk.Frame(self.tabControl)
            self.tabControl.add(self.tab3,text='Optical')
            self.OpticalFrame=tk.Frame(self.tab3,relief=tk.RIDGE,borderwidth=5)
            self.OpticalFrame.pack(side=tk.LEFT,fill=tk.BOTH,expand=tk.YES,anchor=tk.NW)

        self.eyeStatus.set(f"All Measurements Taken at: {10.0**meas['BERForMeasure']}")

        verticalUnit={'V':'V','A':'A','W':'W','FW':'','AW':'A','VW':'V'}[meas['WaveformType']]
        noiseUnit = {'V':'Vrms','A':'Arms','W':'Wrms','':'','AW':'Arms','VW':'Vrms'}[verticalUnit]

        #topline=''.join(['Eye'.ljust(self.labelwidth)]+[str(eye).center(self.entrywidth-1) for eye in range(len(self.meas['Eye']))]+[''.ljust(self.entrywidth-1)])
        self.Heading(self.ParametersFrame,'Eye',[str(e) for e in range(len(self.meas['Eye']))])
        #self.Line2(topline)
        self.Line2(self.ParametersFrame,'Timing')
        self.Fields2(self.ParametersFrame,'Eye','Start','Time','Start','s')
        self.Fields2(self.ParametersFrame,'Eye','End','Time','End','s')
        self.Fields2(self.ParametersFrame,'Eye','Width','Time','Width','s')
        self.Line2(self.ParametersFrame,'')
        self.Line2(self.ParametersFrame,'Vertical')
        self.Fields2(self.ParametersFrame,'Eye','Low','Value','Low',verticalUnit)
        self.Fields2(self.ParametersFrame,'Eye','Mid','Value','Midpoint',verticalUnit)
        self.Fields2(self.ParametersFrame,'Eye','Best','Value','Best Decision Level',verticalUnit)
        self.Fields2(self.ParametersFrame,'Eye','High','Value','High',verticalUnit)
        self.Fields2(self.ParametersFrame,'Eye','Height','Value','Height',verticalUnit)
        self.Fields2(self.ParametersFrame,'Eye','AV','Value','AV',verticalUnit)
        self.Line2(self.ParametersFrame,'')
        #line=''.join(['Thresholds'.ljust(self.labelwidth)]+[str(th).center(self.entrywidth-1) for th in range(len(self.meas['Level']))])
        #self.Line2(line)
        self.Heading(self.ParametersFrame,'Extents',[str(th) for th in range(len(self.meas['Level']))])
        self.Fields2(self.ParametersFrame,'Level','Min','Value','Min',verticalUnit)
        self.Fields2(self.ParametersFrame,'Level', 'Max', 'Value', 'Max',verticalUnit)
        self.Fields2(self.ParametersFrame,'Level', 'Delta', 'Value', 'Delta',verticalUnit)
        self.Fields2(self.ParametersFrame,'Level', 'Mean', 'Value', 'Mean',verticalUnit)
        self.Line2(self.ParametersFrame,'')
        if len(meas['Eye'])>1:
            self.SingleLine(self.ParametersFrame,'Eye Linearity',ToSI(self.meas['Linearity']*100.,'%'))
            try:
                self.SingleLine(self.ParametersFrame,'RLM',ToSI(self.meas['RLM']*100.,'%'))
            except:
                pass
            self.Line2(self.ParametersFrame,'')
        self.SingleLine(self.ParametersFrame,'Signal Power',ToSI(self.meas['RMS'],noiseUnit))
        self.SingleLine(self.ParametersFrame,'Noise',ToSI(self.meas['Noise'],noiseUnit))
        self.SingleLine(self.ParametersFrame, 'Residual Error',ToSI(self.meas['NoiseResidual'],noiseUnit))
        self.SingleLine(self.ParametersFrame,'SDR',ToSI(self.meas['SDR'],'dB'))
        if not self.meas['SNR'] is None:
            self.SingleLine(self.ParametersFrame,'SNR',ToSI(self.meas['SNR'],'dB'))
            self.SingleLine(self.ParametersFrame, 'SNDR',ToSI(self.meas['SNDR'],'dB'))
        self.Line2(self.ParametersFrame,'')
        self.SingleLine(self.ParametersFrame,'Vertical Resolution',ToSI(self.meas['VerticalResolution'],verticalUnit))
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

        if 'Optical' in self.meas.keys():
            def ToSINone(d,sa): return None if d==None else ToSI(d,sa,round=3)
            self.Line2(self.OpticalFrame,f'Optical Power: '+{'W':'W','FW':'Fractional Power','AW':'Current Proportional to Power','VW':'Voltage Proportional to Power'}[self.meas['WaveformType']])
            if 'Pin' in self.meas['Optical'].keys():
                self.SingleLine(self.OpticalFrame,'Input Power (Pin)', [ToSINone(self.meas['Optical']['Pin']['Linear']['Value'],self.meas['Optical']['Pin']['Linear']['Unit']),
                                                                        ToSINone(self.meas['Optical']['Pin']['Log']['Value'],self.meas['Optical']['Pin']['Log']['Unit'])])
            self.SingleLine(self.OpticalFrame, 'High Level (PH)', [ToSINone(self.meas['Optical']['PH']['Linear']['Value'],self.meas['Optical']['PH']['Linear']['Unit']),
                                                                   ToSINone(self.meas['Optical']['PH']['Log']['Value'],self.meas['Optical']['PH']['Log']['Unit'])])
            self.SingleLine(self.OpticalFrame, 'Low Level (PL)', [ToSINone(self.meas['Optical']['PL']['Linear']['Value'],self.meas['Optical']['PL']['Linear']['Unit']),
                                                                  ToSINone(self.meas['Optical']['PL']['Log']['Value'],self.meas['Optical']['PL']['Log']['Unit'])])
            self.SingleLine(self.OpticalFrame, 'Average Power (Pavg)', [ToSINone(self.meas['Optical']['Pavg']['Linear']['Value'],self.meas['Optical']['Pavg']['Linear']['Unit']),
                                                                        ToSINone(self.meas['Optical']['Pavg']['Log']['Value'],self.meas['Optical']['Pavg']['Log']['Unit'])])
            self.SingleLine(self.OpticalFrame, 'Modulation Amplitude (OMA)', [ToSINone(self.meas['Optical']['OMA']['Linear']['Value'],self.meas['Optical']['OMA']['Linear']['Unit']),
                                                                              ToSINone(self.meas['Optical']['OMA']['Log']['Value'],self.meas['Optical']['OMA']['Log']['Unit'])])
            self.SingleLine(self.OpticalFrame, 'Extinction Ratio (ER)', [ToSINone(self.meas['Optical']['ER']['Linear']['Value'],self.meas['Optical']['ER']['Linear']['Unit']),
                                                                         ToSINone(self.meas['Optical']['ER']['Log']['Value'],self.meas['Optical']['ER']['Log']['Unit'])])
            if 'IL' in self.meas['Optical'].keys():
                self.SingleLine(self.OpticalFrame,'Insertion Loss (IL)', [ToSINone(self.meas['Optical']['IL']['Linear']['Value'],self.meas['Optical']['IL']['Linear']['Unit']),
                                                                          ToSINone(self.meas['Optical']['IL']['Log']['Value'],self.meas['Optical']['IL']['Log']['Unit'])])
            if 'Loss' in self.meas['Optical'].keys():
                self.SingleLine(self.OpticalFrame,'Loss (Pin - Pavg)', [ToSINone(self.meas['Optical']['Loss']['Linear']['Value'],self.meas['Optical']['Loss']['Linear']['Unit']),
                                                                        ToSINone(self.meas['Optical']['Loss']['Log']['Value'],self.meas['Optical']['Loss']['Log']['Unit'])])
            if 'TP' in self.meas['Optical'].keys():
                self.SingleLine(self.OpticalFrame,'Transmission Penalty (TP)', [ToSINone(self.meas['Optical']['TP']['Linear']['Value'],self.meas['Optical']['TP']['Linear']['Unit']),
                                                                                ToSINone(self.meas['Optical']['TP']['Log']['Value'],self.meas['Optical']['TP']['Log']['Unit'])])

            if 'Q' in self.meas['Optical'].keys():
                self.Line2(self.OpticalFrame,'Q Measurements')
                self.SingleLine(self.OpticalFrame, 'BER', '{:.3E}'.format(self.meas['Optical']['Q']['BERMeasured']))
                self.SingleLine(self.OpticalFrame,'Q Factor', [ToSINone(self.meas['Optical']['Q']['QFactor'],''),ToSINone(self.meas['Optical']['Q']['QFactordB'],'dB')])

                if 'QFactorExpected' in self.meas['Optical']['Q'].keys():
                    self.SingleLine(self.OpticalFrame, 'BER Expected', '{:.3E}'.format(self.meas['Optical']['Q']['BERExpected']))
                    self.SingleLine(self.OpticalFrame,'Q Factor Expected', [ToSINone(self.meas['Optical']['Q']['QFactorExpected'],''),ToSINone(self.meas['Optical']['Q']['QFactorExpecteddB'],'dB')])
                    self.SingleLine(self.OpticalFrame,'Tx Penalty', ToSINone(self.meas['Optical']['Q']['TxPenalty'],'dB'))
# 
#             self.tabControl.tab(2,state='normal')
#         else:
#             self.tabControl.tab(2,state='disabled')
        self.deiconify()