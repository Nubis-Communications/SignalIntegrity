"""
arctest.py
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
else:
    import tkinter as tk

def onCalculate():
    canvas.delete(tk.ALL)
    startx=int(startxVar.get())
    starty=int(startyVar.get())
    endx=int(endxVar.get())
    endy=int(endyVar.get())
    startAngle=int(startAngleVar.get())
    extentAngle=int(extentVar.get())
    canvas.create_arc(startx,starty,endx,endy,start=startAngle,extent=extentAngle,style='arc')


root = tk.Tk()
frame=tk.Frame(root)
frame.pack()
startxFrame=tk.Frame(frame)
startxFrame.pack()
startxLabel=tk.Label(startxFrame,width=20,text='start x: ',anchor='e')
startxLabel.pack(side=tk.LEFT,expand=tk.NO,fill=tk.X)
startxVar=tk.StringVar(value='0')
startxEntry=tk.Entry(startxFrame,textvariable=startxVar,width=10)
startxEntry.pack(side=tk.LEFT,expand=tk.YES,fill=tk.X)
startyFrame=tk.Frame(frame)
startyFrame.pack()
startyLabel=tk.Label(startyFrame,width=20,text='start y: ',anchor='e')
startyLabel.pack(side=tk.LEFT,expand=tk.NO,fill=tk.X)
startyVar=tk.StringVar(value='0')
startyEntry=tk.Entry(startyFrame,textvariable=startyVar,width=10)
startyEntry.pack(side=tk.LEFT,expand=tk.YES,fill=tk.X)

endxFrame=tk.Frame(frame)
endxFrame.pack()
endxLabel=tk.Label(endxFrame,width=20,text='end x: ',anchor='e')
endxLabel.pack(side=tk.LEFT,expand=tk.NO,fill=tk.X)
endxVar=tk.StringVar(value='200')
endxEntry=tk.Entry(endxFrame,textvariable=endxVar,width=10)
endxEntry.pack(side=tk.LEFT,expand=tk.YES,fill=tk.X)

endyFrame=tk.Frame(frame)
endyFrame.pack()
endyLabel=tk.Label(endyFrame,width=20,text='end y: ',anchor='e')
endyLabel.pack(side=tk.LEFT,expand=tk.NO,fill=tk.X)
endyVar=tk.StringVar(value='200')
endyEntry=tk.Entry(endyFrame,textvariable=endyVar,width=10)
endyEntry.pack(side=tk.LEFT,expand=tk.YES,fill=tk.X)

startAngleFrame=tk.Frame(frame)
startAngleFrame.pack()
startAngleLabel=tk.Label(startAngleFrame,width=20,text='start angle: ',anchor='e')
startAngleLabel.pack(side=tk.LEFT,expand=tk.NO,fill=tk.X)
startAngleVar=tk.StringVar(value='0')
startAngleEntry=tk.Entry(startAngleFrame,textvariable=startAngleVar,width=10)
startAngleEntry.pack(side=tk.LEFT,expand=tk.YES,fill=tk.X)

extentFrame=tk.Frame(frame)
extentFrame.pack()
extentLabel=tk.Label(extentFrame,width=20,text='extent: ',anchor='e')
extentLabel.pack(side=tk.LEFT,expand=tk.NO,fill=tk.X)
extentVar=tk.StringVar(value='90')
extentEntry=tk.Entry(extentFrame,textvariable=extentVar,width=10)
extentEntry.pack(side=tk.LEFT,expand=tk.YES,fill=tk.X)

calculateButton= tk.Button(frame,text='calculate',command=onCalculate).pack(side=tk.TOP,expand=tk.NO,fill=tk.NONE)

canvas=tk.Canvas(frame)
canvas.pack()
root.title("App")
root.mainloop()


