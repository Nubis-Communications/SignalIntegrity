class ErrorTerms(object):
...
    def UnknownThruCalibration(self,Sm,Sest,firstPort,secondPort):
        [ED1,ER1,ES1]=self[firstPort][firstPort]
        [ED2,ER2,ES2]=self[secondPort][secondPort]
        [EX12,ET12,EL12]=self[firstPort][secondPort]
        [EX21,ET21,EL21]=self[secondPort][firstPort]
        p=cmath.sqrt((Sm[0][1]-EX12)/(Sm[1][0]-EX21))
        [EX12,ET12,EL12]=[EX12,cmath.sqrt(ER1)*cmath.sqrt(ER2)*p,ES1]
        [EX21,ET21,EL21]=[EX21,cmath.sqrt(ER1)*cmath.sqrt(ER2)/p,ES2]
        DutCalc1=ErrorTerms([[[ED1,ER1,ES1],[EX12,ET12,EL12]],
                             [[EX21,ET21,EL21],[ED2,ER2,ES2]]]).DutCalculation(Sm)
        DutCalc2=ErrorTerms([[[ED1,ER1,ES1],[EX12,-ET12,EL12]],
                             [[EX21,-ET21,EL21],[ED2,ER2,ES2]]]).DutCalculation(Sm)
        if norm(matrix(DutCalc1)-matrix(Sest)) < norm(matrix(DutCalc2)-matrix(Sest)):
            return DutCalc1
        else:
            return DutCalc2

...
