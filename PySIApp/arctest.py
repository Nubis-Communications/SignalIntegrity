'''
Created on Oct 26, 2015

@author: peterp
'''
from Tkinter import *

def onCalculate():
    canvas.delete(ALL)
    startx=int(startxVar.get())
    starty=int(startyVar.get())
    endx=int(endxVar.get())
    endy=int(endyVar.get())
    startAngle=int(startAngleVar.get())
    extentAngle=int(extentVar.get())
    canvas.create_arc(startx,starty,endx,endy,start=startAngle,extent=extentAngle,style='arc')


root = Tk()
frame=Frame(root)
frame.pack()
startxFrame=Frame(frame)
startxFrame.pack()
startxLabel=Label(startxFrame,width=20,text='start x: ',anchor='e')
startxLabel.pack(side=LEFT,expand=NO,fill=X)
startxVar=StringVar(value='0')
startxEntry=Entry(startxFrame,textvariable=startxVar,width=10)
startxEntry.pack(side=LEFT,expand=YES,fill=X)
startyFrame=Frame(frame)
startyFrame.pack()
startyLabel=Label(startyFrame,width=20,text='start y: ',anchor='e')
startyLabel.pack(side=LEFT,expand=NO,fill=X)
startyVar=StringVar(value='0')
startyEntry=Entry(startyFrame,textvariable=startyVar,width=10)
startyEntry.pack(side=LEFT,expand=YES,fill=X)

endxFrame=Frame(frame)
endxFrame.pack()
endxLabel=Label(endxFrame,width=20,text='end x: ',anchor='e')
endxLabel.pack(side=LEFT,expand=NO,fill=X)
endxVar=StringVar(value='200')
endxEntry=Entry(endxFrame,textvariable=endxVar,width=10)
endxEntry.pack(side=LEFT,expand=YES,fill=X)

endyFrame=Frame(frame)
endyFrame.pack()
endyLabel=Label(endyFrame,width=20,text='end y: ',anchor='e')
endyLabel.pack(side=LEFT,expand=NO,fill=X)
endyVar=StringVar(value='200')
endyEntry=Entry(endyFrame,textvariable=endyVar,width=10)
endyEntry.pack(side=LEFT,expand=YES,fill=X)

startAngleFrame=Frame(frame)
startAngleFrame.pack()
startAngleLabel=Label(startAngleFrame,width=20,text='start angle: ',anchor='e')
startAngleLabel.pack(side=LEFT,expand=NO,fill=X)
startAngleVar=StringVar(value='0')
startAngleEntry=Entry(startAngleFrame,textvariable=startAngleVar,width=10)
startAngleEntry.pack(side=LEFT,expand=YES,fill=X)

extentFrame=Frame(frame)
extentFrame.pack()
extentLabel=Label(extentFrame,width=20,text='extent: ',anchor='e')
extentLabel.pack(side=LEFT,expand=NO,fill=X)
extentVar=StringVar(value='90')
extentEntry=Entry(extentFrame,textvariable=extentVar,width=10)
extentEntry.pack(side=LEFT,expand=YES,fill=X)

calculateButton= Button(frame,text='calculate',command=onCalculate).pack(side=TOP,expand=NO,fill=NONE)

canvas=Canvas(frame)
canvas.pack()
root.title("PySI App")
root.mainloop()


